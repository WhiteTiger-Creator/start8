"""Verifier tests for the structured-finance payment waterfall task."""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

WORKFLOW_PATH = Path("/app/workflow/distribute.py")
ORIGINAL_WORKFLOW_PATH = Path("/app/workflow/.distribute.original")
DEFAULT_INPUT = Path("/app/data/settled_collections.json")
COLLECTIONS_PATH = Path("/app/data/collections.json")
CONTROL_TOTALS_PATH = Path("/app/data/control_totals.json")
TERMS_PATH = Path("/app/data/tranche_terms.json")
POLICY_PATH = Path("/app/data/waterfall_policy.json")
SPEC_PATH = Path("/app/docs/report_spec.json")
LOG_PATH = Path("/app/incident/waterfall_governance_log.md")
EXPECTED_FIXTURE = Path("/tests/fixtures/expected_report.json")
ALT_INPUT = Path("/tests/fixtures/alt_settled_collections.json")

FIXTURE = json.loads(EXPECTED_FIXTURE.read_text())
SPEC = json.loads(SPEC_PATH.read_text())

LEDGER_KEYS = set(SPEC["tranche_ledger_json"]["required_fields"])
REGISTER_KEYS = set(SPEC["payment_register"]["required_fields"])
SUMMARY_KEYS = set(SPEC["distribution_summary_json"]["required_fields"])
STEP_KINDS = SPEC["field_types"]["step_kind"]["enum"]
TRIGGER_FLAGS = set(SPEC["field_types"]["trigger_flag"]["enum"])
STEP_KIND_ORDER = SPEC["distribution_summary_json"]["step_kind_counts_key_order"]

SETTLED_ITEM_FIELDS = set(SPEC["settled_collections_source"]["items"]["item_required_fields"])
TRANCHE_KINDS = (
    "senior_interest",
    "senior_principal",
    "sub_interest",
    "sub_principal",
    "turbo_principal",
)

POLICY_FIELDS = (
    "deferred_sub_cap_minor", "divert_cap_minor", "ic_trigger_bps", "oc_trigger_bps",
    "register_min_minor", "register_shortfall_min_minor", "residual_cap_minor",
    "sub_penalty_bps",
)
BASELINE = {
    "ic_trigger_bps": 11000,
    "oc_trigger_bps": 12000,
    "divert_cap_minor": 3000000,
    "residual_cap_minor": 1500000,
    "deferred_sub_cap_minor": 900000,
    "register_min_minor": 25000,
    "register_shortfall_min_minor": 1,
    "sub_penalty_bps": 200,
}
BPS = 10000


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _resolve(payee: str, data: dict) -> dict:
    resolved = dict(BASELINE)
    resolved.update({k: int(v) for k, v in data.get("default", {}).items() if k in BASELINE})
    override = data.get("tranche_overrides", {}).get(payee)
    if isinstance(override, dict):
        resolved.update({k: int(v) for k, v in override.items() if k in BASELINE})
    return resolved


# --- verifier execution isolation -------------------------------------------------
# The submitted /app/workflow/distribute.py is untrusted once the separate verifier runs it.
# We execute it under an unprivileged UID (65534 / nobody) via setpriv, so it cannot write the
# reward path, read the held-out fixtures under /tests, or interfere with the verifier. Inputs are
# staged into a candidate-writable work area; the operational files under /app keep their fixed paths.
_CWORK = Path("/candidate-work")
_run_ctr = itertools.count()
_SETPRIV = ["setpriv", "--reuid=65534", "--regid=65534", "--clear-groups", "--no-new-privs"]

# The submitted program gets a minimal explicit environment rather than inheriting the verifier's
# (PATH/PYTHONPATH/CI variables and any other grader context).
_CANDIDATE_ENV = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": "/candidate-work", "LANG": "C.UTF-8"}
_CANDIDATE_TIMEOUT = 300


def _candidate_dir() -> Path:
    directory = _CWORK / f"run-{next(_run_ctr)}"
    directory.mkdir(parents=True, exist_ok=True)
    os.chmod(directory, 0o777)
    return directory


def _run_agent(argv, cwd: Path):
    """Run the submitted program under the unprivileged candidate UID with a scrubbed environment."""
    return subprocess.run(
        _SETPRIV + argv, check=True, capture_output=True, text=True, cwd=str(cwd),
        env=dict(_CANDIDATE_ENV), timeout=_CANDIDATE_TIMEOUT,
    )


def _run_pipeline(tmp_path: Path, script_path: Path = WORKFLOW_PATH, input_path: Path = DEFAULT_INPUT):
    work = _candidate_dir()
    out_dir = work / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(out_dir, 0o777)
    staged_input = work / "settled_input.json"
    shutil.copy(str(input_path), str(staged_input))
    os.chmod(staged_input, 0o644)
    result = _run_agent(
        [sys.executable, str(script_path), "--input", str(staged_input), "--output-dir", str(out_dir)],
        cwd=work,
    )
    assert result.returncode == 0
    summary = _load_json(out_dir / "distribution_summary.json")
    ledger = _load_json(out_dir / "tranche_ledger.json")
    register = _load_jsonl(out_dir / "payment_register.jsonl")
    return out_dir, summary, ledger, register


@pytest.fixture(scope="session")
def primary_outputs(tmp_path_factory):
    return _run_pipeline(tmp_path_factory.mktemp("primary"))


# --------------------------------------------------------------------------
# Step 1: the raw collections must be reconciled in place
# --------------------------------------------------------------------------
def _major_to_minor(value: object) -> int:
    text = str(value).strip()
    whole, _, frac = text.partition(".")
    return int(whole or "0") * 100 + int(((frac + "00")[:2]) or "0")


def _active_tranches() -> dict[str, dict]:
    """The tranche register after the shipped terms are normalised and de-duplicated."""
    kept: dict[str, dict] = {}
    for row in _load_json(TERMS_PATH)["tranches"]:
        tranche_id = str(row["tranche_id"]).strip().upper()
        balance = int(row["balance_minor"])
        if not 1 <= int(row["coupon_bps"]) <= 3000:
            continue
        if balance <= 0 and not int(row["interest_carryforward_minor"]) and not int(
            row["principal_carryforward_minor"]
        ):
            continue
        previous = kept.get(tranche_id)
        if previous is None or balance > int(previous["balance_minor"]):
            kept[tranche_id] = row
    return kept


def _mishandled_settlement(normalise: bool, reversal_mode: str, drop_categories: bool) -> dict:
    """Rebuild the settled set the way a responder who missed part of #WF-4170 would."""
    control = _load_json(CONTROL_TOTALS_PATH)
    currency = control["settlement_currency"]
    rates = control["fx_rates_bps"]
    categories = control["category_totals_minor"]

    def amount_of(row: dict) -> int:
        if not normalise:
            return int(float(str(row["reported_amount"]).strip()))
        value = (
            _major_to_minor(row["reported_amount"])
            if row["unit"] == "major"
            else int(row["reported_amount"])
        )
        if row["currency"] != currency:
            value = value * int(rates[row["currency"]]) // BPS
        return value

    items: dict[str, dict] = {}
    order: list[str] = []
    reversals: list[tuple[str, int]] = []
    for row in _load_json(COLLECTIONS_PATH):
        value = amount_of(row)
        if row["entry_type"] == "reversal":
            if reversal_mode == "net":
                reversals.append((row["reverses"], value))
                continue
            if reversal_mode == "drop":
                continue
            # reversal_mode == "include": the line is summed as if it were a collection
        items[row["item_id"]] = {
            "item_id": row["item_id"],
            "category": row["category"],
            "obligor": row["obligor"],
            "amount_minor": value,
        }
        order.append(row["item_id"])
    for target, value in reversals:
        if target in items:
            items[target]["amount_minor"] = max(items[target]["amount_minor"] - value, 0)

    settled = [
        items[key]
        for key in order
        if (not drop_categories or items[key]["category"] in categories)
        and items[key]["amount_minor"] > 0
    ]
    settled.sort(key=lambda row: (row["category"], row["item_id"]))
    totals: dict[str, int] = {}
    for row in settled:
        totals[row["category"]] = totals.get(row["category"], 0) + row["amount_minor"]
    return {
        "period": control["period"],
        "settlement_currency": currency,
        "category_totals_minor": {name: totals[name] for name in sorted(totals)},
        "items": settled,
    }


def _unnormalised() -> dict:
    return _mishandled_settlement(normalise=False, reversal_mode="net", drop_categories=True)


def _reversals_ignored() -> dict:
    return _mishandled_settlement(normalise=True, reversal_mode="drop", drop_categories=True)


def _naive_sum() -> dict:
    return _mishandled_settlement(normalise=False, reversal_mode="include", drop_categories=False)


def test_collection_sources_are_intact():
    assert _load_json(COLLECTIONS_PATH) == FIXTURE["collections"]
    assert _load_json(CONTROL_TOTALS_PATH) == FIXTURE["control_totals"]


def test_settled_collections_reconciled():
    """/app/data/settled_collections.json ships unreconciled; it must hold the settled set."""
    reconciled = _load_json(DEFAULT_INPUT)
    assert isinstance(reconciled, dict)
    assert reconciled == FIXTURE["reconciled"]


def test_reconciled_totals_tie_to_the_control_totals():
    reconciled = _load_json(DEFAULT_INPUT)
    control = _load_json(CONTROL_TOTALS_PATH)["category_totals_minor"]
    totals: dict[str, int] = {}
    for item in reconciled["items"]:
        totals[item["category"]] = totals.get(item["category"], 0) + item["amount_minor"]
    assert totals == {name: int(value) for name, value in control.items()}
    assert reconciled["category_totals_minor"] == totals
    assert list(reconciled["category_totals_minor"]) == sorted(reconciled["category_totals_minor"])


def test_reconciled_items_carry_only_settlement_fields():
    reconciled = _load_json(DEFAULT_INPUT)
    for item in reconciled["items"]:
        assert set(item) == SETTLED_ITEM_FIELDS
        assert isinstance(item["amount_minor"], int) and item["amount_minor"] > 0
    keys = [(item["category"], item["item_id"]) for item in reconciled["items"]]
    assert keys == sorted(keys)


def test_shipped_and_mishandled_settlements_differ_from_the_reconciled_one():
    """The reconciliation is real work: none of the shortcuts land on the settled set."""
    expected = FIXTURE["reconciled"]
    assert FIXTURE["shipped_settled"] != expected
    assert _unnormalised() != expected
    assert _reversals_ignored() != expected
    assert _naive_sum() == FIXTURE["shipped_settled"]


def test_distribution_depends_on_the_reconciled_collections(tmp_path: Path):
    """Even a correctly repaired engine emits wrong artifacts on a wrongly reconciled set."""
    for label, settled in (
        ("shipped", FIXTURE["shipped_settled"]),
        ("unnormalised", _unnormalised()),
        ("reversals_ignored", _reversals_ignored()),
        ("naive_sum", _naive_sum()),
    ):
        bad_input = tmp_path / f"{label}.json"
        _write_json(bad_input, settled)
        _, summary, ledger, register = _run_pipeline(tmp_path / label, input_path=bad_input)
        assert summary != FIXTURE["primary"]["summary"], label
        assert (ledger, register) != (
            FIXTURE["primary"]["ledger"],
            FIXTURE["primary"]["register_rows"],
        ), label


def test_subordinate_tranches_go_unpaid_on_unreconciled_collections(tmp_path: Path):
    """A mis-scaled line and an unnetted reversal change how far down the waterfall cash reaches."""
    reconciled = FIXTURE["primary"]["summary"]
    assert reconciled["sub_interest_paid_minor"] > 0
    assert reconciled["sub_principal_paid_minor"] > 0
    for label, settled in (
        ("unnormalised", _unnormalised()),
        ("naive_sum", _naive_sum()),
    ):
        bad_input = tmp_path / f"flip-{label}.json"
        _write_json(bad_input, settled)
        _, summary, _, _ = _run_pipeline(tmp_path / f"flip-{label}", input_path=bad_input)
        assert summary["sub_interest_paid_minor"] == 0, label
        assert summary["sub_principal_paid_minor"] == 0, label
    # Ignoring the reversals lifts the eligible collections over the coverage trigger, which
    # changes where in the cascade the subordinate interest steps run at all.
    ignored_input = tmp_path / "flip-reversals.json"
    _write_json(ignored_input, _reversals_ignored())
    _, ignored_summary, _, _ = _run_pipeline(tmp_path / "flip-reversals", input_path=ignored_input)
    assert reconciled["ic_breached"] is True
    assert ignored_summary["ic_breached"] is False
    assert ignored_summary["sub_interest_paid_minor"] != reconciled["sub_interest_paid_minor"]


# --------------------------------------------------------------------------
# Step 2: the engine output contract
# --------------------------------------------------------------------------
def test_cli_exists():
    assert WORKFLOW_PATH.exists()


def test_output_dir_contains_exactly_three_files(primary_outputs):
    out_dir, _, _, _ = primary_outputs
    names = sorted(p.name for p in out_dir.iterdir() if p.is_file())
    assert names == ["distribution_summary.json", "payment_register.jsonl", "tranche_ledger.json"]


def test_primary_summary_matches_fixture(primary_outputs):
    _, summary, _, _ = primary_outputs
    assert summary == FIXTURE["primary"]["summary"]


def test_primary_ledger_matches_fixture(primary_outputs):
    _, _, ledger, _ = primary_outputs
    assert ledger == FIXTURE["primary"]["ledger"]


def test_primary_register_matches_fixture(primary_outputs):
    _, _, _, register = primary_outputs
    assert register == FIXTURE["primary"]["register_rows"]


def test_summary_schema(primary_outputs):
    _, summary, _, _ = primary_outputs
    assert set(summary) == SUMMARY_KEYS
    assert summary["schema_version"] == "waterfall-dist-v1"
    assert list(summary["step_kind_counts"]) == STEP_KIND_ORDER
    assert isinstance(summary["ic_breached"], bool)
    assert isinstance(summary["oc_breached"], bool)


def test_ledger_schema_and_sorting(primary_outputs):
    _, _, ledger, _ = primary_outputs
    assert list(ledger) == sorted(ledger)
    terms_ids = {
        str(t["tranche_id"]).strip().upper()
        for t in _load_json(TERMS_PATH)["tranches"]
    }
    for tranche_id, rows in ledger.items():
        assert tranche_id in terms_ids
        indexes = [row["step_index"] for row in rows]
        assert indexes == sorted(indexes)
        for row in rows:
            assert set(row) == LEDGER_KEYS
            assert row["step_kind"] in TRANCHE_KINDS
            assert row["trigger_flag"] in TRIGGER_FLAGS
            assert row["step_id"] == f"{row['step_kind']}:{tranche_id}"
            assert row["funds_after_minor"] == row["funds_before_minor"] - row["paid_minor"]
            assert row["shortfall_minor"] == max(row["due_minor"] - row["paid_minor"], 0)


def test_register_required_fields(primary_outputs):
    _, _, _, register = primary_outputs
    for row in register:
        assert set(row) == REGISTER_KEYS
        assert row["step_kind"] in STEP_KINDS
        assert row["step_kind"] != "residual"
        assert row["trigger_flag"] in TRIGGER_FLAGS
        assert row["step_id"] == f"{row['step_kind']}:{row['payee_id']}"


def test_register_sorted(primary_outputs):
    _, _, _, register = primary_outputs
    assert register == sorted(
        register,
        key=lambda row: (
            -row["shortfall_minor"],
            -row["paid_minor"],
            -row["due_minor"],
            row["step_kind"],
            row["payee_id"],
            row["step_index"],
        ),
    )


def test_payment_register_jsonl_compact(primary_outputs):
    out_dir, _, _, _ = primary_outputs
    for line in (out_dir / "payment_register.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        assert ": " not in line
        assert json.dumps(json.loads(line), separators=(",", ":")) == line


def test_no_float_values_emitted(primary_outputs):
    out_dir, _, _, _ = primary_outputs

    def walk(node):
        assert not isinstance(node, float), f"floating-point value emitted: {node!r}"
        if isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(_load_json(out_dir / "distribution_summary.json"))
    walk(_load_json(out_dir / "tranche_ledger.json"))
    for row in _load_jsonl(out_dir / "payment_register.jsonl"):
        walk(row)


def test_summary_math_consistency(primary_outputs):
    _, summary, ledger, register = primary_outputs
    rows = [row for rows in ledger.values() for row in rows]
    for kind in TRANCHE_KINDS:
        assert summary[f"{kind}_paid_minor"] == sum(
            row["paid_minor"] for row in rows if row["step_kind"] == kind
        )
    fee_count = len(_load_json(TERMS_PATH)["fees"])
    assert summary["executed_step_count"] == len(rows) + fee_count + 1
    assert summary["step_kind_counts"]["fee"] == fee_count
    assert summary["step_kind_counts"]["residual"] == 1
    for kind in TRANCHE_KINDS:
        assert summary["step_kind_counts"][kind] == sum(
            1 for row in rows if row["step_kind"] == kind
        )
    assert summary["total_paid_minor"] == (
        summary["fee_paid_minor"]
        + summary["residual_paid_minor"]
        + sum(summary[f"{kind}_paid_minor"] for kind in TRANCHE_KINDS)
    )
    assert summary["registered_step_count"] == len(register)
    assert summary["max_paid_minor"] == max((r["paid_minor"] for r in register), default=0)
    assert summary["max_shortfall_minor"] == max((r["shortfall_minor"] for r in register), default=0)
    assert summary["max_carryforward_out_minor"] >= max(
        (r["carryforward_out_minor"] for r in rows), default=0
    )


def test_cash_conservation(primary_outputs):
    _, summary, _, _ = primary_outputs
    settled = _load_json(DEFAULT_INPUT)
    assert summary["available_funds_minor"] == sum(
        item["amount_minor"] for item in settled["items"] if item["amount_minor"] > 0
    )
    assert summary["total_paid_minor"] + summary["unapplied_funds_minor"] == summary[
        "available_funds_minor"
    ]
    assert summary["category_subtotals"] == settled["category_totals_minor"]


def test_step_kind_counts_enumerate_all_seven(primary_outputs):
    _, summary, _, _ = primary_outputs
    assert set(summary["step_kind_counts"]) == set(STEP_KINDS)
    assert sum(summary["step_kind_counts"].values()) == summary["executed_step_count"]


# --------------------------------------------------------------------------
# Register admission and the post-ordering capacity cap
# --------------------------------------------------------------------------
def test_register_admission_follows_resolved_policy(primary_outputs):
    _, _, ledger, register = primary_outputs
    policy_data = _load_json(POLICY_PATH)
    registered = {(row["payee_id"], row["step_index"]) for row in register}
    excluded_by_floor = 0
    for payee, rows in ledger.items():
        resolved = _resolve(payee, policy_data)
        for row in rows:
            admissible = (
                row["paid_minor"] >= resolved["register_min_minor"]
                or row["shortfall_minor"] >= resolved["register_shortfall_min_minor"]
            )
            if not admissible:
                assert (payee, row["step_index"]) not in registered
                excluded_by_floor += 1
    for row in register:
        resolved = _resolve(row["payee_id"], policy_data)
        assert (
            row["paid_minor"] >= resolved["register_min_minor"]
            or row["shortfall_minor"] >= resolved["register_shortfall_min_minor"]
        )
    assert excluded_by_floor, "the shipped policy must exclude at least one tranche step by floor"


def test_payee_capacity_cap_applied_after_ordering(primary_outputs):
    _, _, ledger, register = primary_outputs
    policy_data = _load_json(POLICY_PATH)
    per_payee: dict[str, int] = {}
    for row in register:
        per_payee[row["payee_id"]] = per_payee.get(row["payee_id"], 0) + 1
    assert per_payee
    assert max(per_payee.values()) <= 2, f"payee exceeded cap: {per_payee}"
    crowded = []
    for payee, rows in ledger.items():
        resolved = _resolve(payee, policy_data)
        admissible = sum(
            1
            for row in rows
            if row["paid_minor"] >= resolved["register_min_minor"]
            or row["shortfall_minor"] >= resolved["register_shortfall_min_minor"]
        )
        if admissible > 2:
            crowded.append(payee)
    assert crowded, "fixture must contain a payee with more admissible steps than the cap allows"
    for payee in crowded:
        assert per_payee.get(payee, 0) == 2


# --------------------------------------------------------------------------
# Policy resolution
# --------------------------------------------------------------------------
def test_sparse_override_inherits_remaining_fields():
    data = _load_json(POLICY_PATH)
    overrides = data.get("tranche_overrides", {})
    sparse = [payee for payee, values in overrides.items() if len(values) == 1]
    assert sparse, "the shipped policy must exercise a single-field override"
    default_resolved = _resolve("__absent__", data)
    for payee in sparse:
        resolved = _resolve(payee, data)
        named = next(iter(overrides[payee]))
        assert resolved[named] == int(overrides[payee][named])
        for field in POLICY_FIELDS:
            if field != named:
                assert resolved[field] == default_resolved[field]


def test_policy_default_may_omit_fields_and_falls_back_to_baseline():
    data = _load_json(POLICY_PATH)
    omitted = [field for field in POLICY_FIELDS if field not in data.get("default", {})]
    assert omitted, "the shipped policy must omit at least one field to exercise fallback"
    resolved = _resolve("__absent__", data)
    for field in omitted:
        assert resolved[field] == BASELINE[field]


def test_deferred_cap_baseline_binds(primary_outputs):
    """The omitted deferred cap falls back to its baseline and actually limits a payment."""
    _, summary, ledger, _ = primary_outputs
    data = _load_json(POLICY_PATH)
    assert "deferred_sub_cap_minor" not in data.get("default", {})
    assert summary["ic_breached"] is True
    deferred = [
        row
        for rows in ledger.values()
        for row in rows
        if row["step_kind"] == "sub_interest" and row["trigger_flag"] == "ic_deferred"
    ]
    assert deferred, "a breached coverage test must defer the subordinate interest steps"
    capped = [row for row in deferred if row["paid_minor"] == BASELINE["deferred_sub_cap_minor"]]
    assert capped, "the baseline deferred cap must bind on at least one subordinate step"
    for row in capped:
        assert row["paid_minor"] < row["due_minor"]
        assert row["paid_minor"] < row["funds_before_minor"]


# --------------------------------------------------------------------------
# Original / broken snapshot
# --------------------------------------------------------------------------
def test_original_snapshot_preserved():
    assert ORIGINAL_WORKFLOW_PATH.exists()
    digest = hashlib.sha256(ORIGINAL_WORKFLOW_PATH.read_bytes()).hexdigest()
    assert digest == FIXTURE["broken_snapshot_sha256"]


def test_broken_snapshot_is_wrong(tmp_path: Path):
    _, summary, ledger, register = _run_pipeline(tmp_path, script_path=ORIGINAL_WORKFLOW_PATH)
    assert summary != FIXTURE["primary"]["summary"]
    assert ledger != FIXTURE["primary"]["ledger"]
    assert register != FIXTURE["primary"]["register_rows"]


# --------------------------------------------------------------------------
# Generalization / idempotency / command line
# --------------------------------------------------------------------------
def test_pipeline_rerun_idempotent(tmp_path: Path):
    _, sa, la, ra = _run_pipeline(tmp_path / "a")
    _, sb, lb, rb = _run_pipeline(tmp_path / "b")
    assert (sa, la, ra) == (sb, lb, rb)


def test_engine_supports_alternate_period(tmp_path: Path):
    _, summary, ledger, register = _run_pipeline(tmp_path, input_path=ALT_INPUT)
    assert summary == FIXTURE["alternate"]["summary"]
    assert ledger == FIXTURE["alternate"]["ledger"]
    assert register == FIXTURE["alternate"]["register_rows"]


def test_cli_defaults_work_and_match_explicit_run(tmp_path: Path):
    _, explicit_summary, _, _ = _run_pipeline(tmp_path)
    # The no-argument run writes to the default /app/output; clear any root-owned artifacts from
    # solve.sh and make the dir candidate-writable so the unprivileged program can populate it.
    default_out = Path("/app/output")
    shutil.rmtree(default_out, ignore_errors=True)
    default_out.mkdir(parents=True, exist_ok=True)
    os.chmod(default_out, 0o777)
    _run_agent([sys.executable, str(WORKFLOW_PATH)], cwd=_candidate_dir())
    assert _load_json(default_out / "distribution_summary.json") == explicit_summary


def test_submitted_program_runs_unprivileged_and_cannot_write_reward(tmp_path: Path):
    """The isolation itself works: code run the way the verifier runs the agent is unprivileged
    (uid 65534) and cannot write the reward path."""
    os.makedirs("/logs/verifier", exist_ok=True)
    reward = Path("/logs/verifier/reward.txt")
    if not reward.exists():
        reward.write_text("0")
    os.chmod("/logs/verifier", 0o755)
    os.chmod(reward, 0o644)
    probe = _candidate_dir() / "probe.py"
    probe.write_text(
        "import os\n"
        "print(os.getuid())\n"
        "open('/logs/verifier/reward.txt', 'w').write('1')\n",
        encoding="utf-8",
    )
    os.chmod(probe, 0o644)
    result = subprocess.run(
        _SETPRIV + [sys.executable, str(probe)],
        capture_output=True, text=True, cwd=str(_CWORK), check=False,
    )
    assert result.stdout.strip().splitlines()[0] == "65534", "submitted program must run as uid 65534"
    assert result.returncode != 0 and "Permission denied" in result.stderr, (
        "unprivileged submitted program must not be able to write the reward path"
    )


# --------------------------------------------------------------------------
# Source-path influence
# --------------------------------------------------------------------------
def test_tranche_terms_source_affects_output(tmp_path: Path):
    original = TERMS_PATH.read_text(encoding="utf-8")
    try:
        _, summary_a, ledger_a, queue_a = _run_pipeline(tmp_path / "a")
        data = json.loads(original)
        data["collateral"]["pool_balance_minor"] = 0
        _write_json(TERMS_PATH, data)
        _, summary_b, ledger_b, queue_b = _run_pipeline(tmp_path / "b")
        assert summary_a["fee_paid_minor"] > summary_b["fee_paid_minor"]
        assert summary_b["oc_bps"] < summary_a["oc_bps"]
        assert summary_b["oc_breached"] is True
        assert summary_a != summary_b
        assert ledger_a != ledger_b
        assert queue_a != queue_b
    finally:
        TERMS_PATH.write_text(original, encoding="utf-8")


def test_policy_source_affects_output(tmp_path: Path):
    original = POLICY_PATH.read_text(encoding="utf-8")
    try:
        data = json.loads(original)
        data["default"]["ic_trigger_bps"] = 1
        _write_json(POLICY_PATH, data)
        _, summary, _, _ = _run_pipeline(tmp_path / "shifted")
        assert summary["ic_breached"] is False
        assert summary["turbo_principal_paid_minor"] == 0
        assert summary != FIXTURE["primary"]["summary"]
    finally:
        POLICY_PATH.write_text(original, encoding="utf-8")


# --------------------------------------------------------------------------
# Governance-dialect deviations
# --------------------------------------------------------------------------
def test_coverage_test_is_measured_after_the_senior_principal_step(primary_outputs):
    """The overcollateralisation reading is post-payment; the pre-payment reading breaches."""
    _, summary, _, _ = primary_outputs
    trigger = _resolve("__absent__", _load_json(POLICY_PATH))["oc_trigger_bps"]
    senior_opening = sum(
        int(row["balance_minor"])
        for row in _active_tranches().values()
        if str(row["class"]).strip().lower() != "subordinate"
    )
    pool = int(_load_json(TERMS_PATH)["collateral"]["pool_balance_minor"])
    oc_before = pool * BPS // senior_opening
    assert oc_before < trigger, "fixture must make the pre-payment reading breach"
    assert summary["oc_bps"] > oc_before
    assert summary["oc_bps"] >= trigger
    assert summary["oc_breached"] is False


def test_senior_principal_is_sequential_not_pro_rata(tmp_path: Path):
    """A short period pays the most senior tranche first; a pro-rata split would pay both."""
    control = _load_json(CONTROL_TOTALS_PATH)
    settled = {
        "period": "probe",
        "settlement_currency": control["settlement_currency"],
        "category_totals_minor": {"scheduled_principal": 50000000},
        "items": [
            {
                "item_id": "probe-01",
                "category": "scheduled_principal",
                "obligor": "north-fund",
                "amount_minor": 50000000,
            }
        ],
    }
    probe_input = tmp_path / "sequential.json"
    _write_json(probe_input, settled)
    _, _, ledger, _ = _run_pipeline(tmp_path / "run", input_path=probe_input)
    principal = {
        payee: next(row for row in rows if row["step_kind"] == "senior_principal")
        for payee, rows in ledger.items()
        if any(row["step_kind"] == "senior_principal" for row in rows)
    }
    ranked = sorted(principal.items(), key=lambda kv: kv[1]["step_index"])
    top_payee, top_row = ranked[0]
    assert top_row["paid_minor"] > 0
    assert top_row["shortfall_minor"] > 0, "the probe must leave the first tranche short"
    total_due = sum(row["due_minor"] for row in principal.values())
    for payee, row in ranked[1:]:
        assert row["paid_minor"] == 0, f"{payee} was paid before {top_payee} was made whole"
        pro_rata = top_row["paid_minor"] * row["due_minor"] // total_due
        assert pro_rata > 0, "a pro-rata split would have paid this tranche"


def test_interest_carryforward_compounds_in_opposite_directions(tmp_path: Path):
    """Senior interest shortfalls compound rounded up, subordinate ones rounded down."""
    _, _, ledger, _ = _run_pipeline(tmp_path, input_path=ALT_INPUT)
    terms = _active_tranches()
    policy_data = _load_json(POLICY_PATH)
    checked = {"senior_interest": 0, "sub_interest": 0}
    for payee, rows in ledger.items():
        coupon = int(terms[payee]["coupon_bps"])
        penalty = _resolve(payee, policy_data)["sub_penalty_bps"]
        for row in rows:
            shortfall = row["shortfall_minor"]
            if row["step_kind"] == "senior_interest" and shortfall > 0:
                assert row["carryforward_out_minor"] == shortfall + -(-shortfall * coupon // BPS)
                checked["senior_interest"] += 1
            elif row["step_kind"] == "sub_interest" and shortfall > 0:
                assert row["carryforward_out_minor"] == shortfall + shortfall * (coupon + penalty) // BPS
                checked["sub_interest"] += 1
            elif row["step_kind"] in ("senior_principal", "sub_principal", "turbo_principal"):
                assert row["carryforward_out_minor"] == shortfall
    assert checked["senior_interest"] and checked["sub_interest"]
    # At least one senior leg must round up strictly, proving the direction is not shared.
    strict = [
        row
        for payee, rows in ledger.items()
        for row in rows
        if row["step_kind"] == "senior_interest"
        and row["shortfall_minor"] > 0
        and (row["shortfall_minor"] * int(terms[payee]["coupon_bps"])) % BPS
    ]
    assert strict, "fixture must exercise a senior carryforward that rounds up"


# --------------------------------------------------------------------------
# Sources stay operational
# --------------------------------------------------------------------------
def test_governance_log_present():
    assert LOG_PATH.exists() and LOG_PATH.stat().st_size > 0


def test_engine_does_not_reference_test_artifacts():
    code = WORKFLOW_PATH.read_text(encoding="utf-8")
    for token in ("/tests", "expected_report.json", "alt_settled_collections.json"):
        assert token not in code
