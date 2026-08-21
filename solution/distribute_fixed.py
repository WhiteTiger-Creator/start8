#!/usr/bin/env python3
"""Structured-finance payment waterfall distribution engine (governance dialect).

Cascades a period's settled collections through the deal's priority waterfall and
emits the trustee distribution artifacts. Every step, trigger, cap and rounding
direction here is the deal governance board's own dialect, reconstructed from
/app/incident/waterfall_governance_log.md, the operational data under /app/data and
/app/docs/report_spec.json (output contract only).

Standard library only. All money is carried in integer minor units; no value in any
emitted artifact is a floating-point number.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

# Fixed absolute operational-input paths. --input selects the settled collections
# only; the tranche terms and the waterfall policy never become relative to it.
DEFAULT_INPUT = "/app/data/settled_collections.json"
DEFAULT_OUTPUT_DIR = "/app/output"
TRANCHE_TERMS_PATH = "/app/data/tranche_terms.json"
WATERFALL_POLICY_PATH = "/app/data/waterfall_policy.json"

SCHEMA_VERSION = "waterfall-dist-v1"

# --- Governance constants (final decisions; see log entries in comments) ---
BPS = 10000                     # #WF-4106: basis-point denominator
ACCRUAL_DENOM = 3600000         # #WF-4106: 30/360 accrual denominator (10000 * 360)
COUPON_MIN_BPS = 1              # #WF-4102: tranche register validity band
COUPON_MAX_BPS = 3000           # #WF-4102
SUBORDINATE_CLASS = "subordinate"   # #WF-4102: every other class is senior
INTEREST_ELIGIBLE_CATEGORIES = ("recovery", "scheduled_interest")   # #WF-4110
PAYEE_CAP = 2                   # #WF-4146: at most 2 register rows per payee

STEP_KIND_ORDER = (
    "fee",
    "residual",
    "senior_interest",
    "senior_principal",
    "sub_interest",
    "sub_principal",
    "turbo_principal",
)
REGISTERED_KINDS = (
    "fee",
    "senior_interest",
    "senior_principal",
    "sub_interest",
    "sub_principal",
    "turbo_principal",
)   # #WF-4140: the residual step is never registered

# Baseline waterfall policy (#WF-4150). Any field the policy file omits keeps these
# values; the policy file may override per default and per tranche.
POLICY_BASELINE = {
    "concentration_cap_bps": 900,
    "ic_trigger_bps": 30340,
    "oc_trigger_bps": 12000,
    "divert_cap_minor": 22680000000,
    "residual_cap_minor": 11340000000,
    "deferred_sub_cap_minor": 6804000000,
    "register_min_minor": 189000000,
    "register_shortfall_min_minor": 7560,
    "sub_penalty_bps": 200,
}


def _ceil_div(numer: int, denom: int) -> int:
    """Integer ceil for non-negative numer; ceil(x/n) == -(-x // n)."""
    return -(-numer // denom)


def canon_text(value: object) -> str:
    text = str(value).strip().lower()
    return text if text else "unknown"


def collapse_ws(value: object) -> str:
    return " ".join(str(value).split())


def coerce_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    text = str(value).strip()
    try:
        return int(text)
    except ValueError:
        try:
            return int(float(text))
        except ValueError:
            return 0


# --------------------------------------------------------------------------
# Inputs (#WF-4101 settled collections, #WF-4102 tranche register)
# --------------------------------------------------------------------------
def load_settlement(path: str) -> tuple[str, str, int, list[dict]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    raw_items = data.get("items", [])
    items = []
    for row in raw_items:
        amount = coerce_int(row.get("amount_minor", 0))
        if amount <= 0:
            continue
        items.append(
            {
                "item_id": collapse_ws(row.get("item_id", "")),
                "category": canon_text(row.get("category", "")),
                "obligor": canon_text(row.get("obligor", "")),
                "amount_minor": amount,
            }
        )
    items.sort(key=lambda row: (row["category"], row["item_id"]))
    period = collapse_ws(data.get("period", ""))
    currency = str(data.get("settlement_currency", "")).strip().upper()
    return period, currency, len(raw_items), items


def load_tranches(terms: dict) -> list[dict]:
    kept: dict[str, dict] = {}
    for row in terms.get("tranches", []):
        tranche_id = str(row.get("tranche_id", "")).strip().upper()
        coupon_bps = coerce_int(row.get("coupon_bps", 0))
        balance = coerce_int(row.get("balance_minor", 0))
        interest_cf = coerce_int(row.get("interest_carryforward_minor", 0))
        principal_cf = coerce_int(row.get("principal_carryforward_minor", 0))
        if not tranche_id or not COUPON_MIN_BPS <= coupon_bps <= COUPON_MAX_BPS:
            continue
        if balance <= 0 and interest_cf <= 0 and principal_cf <= 0:
            continue
        record = {
            "tranche_id": tranche_id,
            "tranche_class": canon_text(row.get("class", "")),
            "seniority": coerce_int(row.get("seniority", 0)),
            "balance_minor": balance,
            "coupon_bps": coupon_bps,
            "scheduled_principal_minor": coerce_int(row.get("scheduled_principal_minor", 0)),
            "interest_carryforward_minor": interest_cf,
            "principal_carryforward_minor": principal_cf,
        }
        previous = kept.get(tranche_id)
        if previous is None or record["balance_minor"] > previous["balance_minor"]:
            kept[tranche_id] = record
    return sorted(kept.values(), key=lambda t: (t["seniority"], t["tranche_id"]))


def load_fees(terms: dict, pool_balance: int) -> list[dict]:
    fees = []
    for row in terms.get("fees", []):
        fee_id = canon_text(row.get("fee_id", ""))
        basis_bps = coerce_int(row.get("basis_bps", 0))
        servicing_fee_base = pool_balance * basis_bps
        # #WF-4106: the basis leg of a fee accrual rounds UP.
        due = coerce_int(row.get("flat_minor", 0)) + _ceil_div(servicing_fee_base, BPS)
        fees.append({"fee_id": fee_id, "due_minor": due})
    fees.sort(key=lambda row: row["fee_id"])
    return fees


# --------------------------------------------------------------------------
# Policy resolution (#WF-4150, #WF-4152)
# --------------------------------------------------------------------------
def resolve_policy(payee_id: str, policy_data: dict) -> dict:
    resolved = dict(POLICY_BASELINE)
    for field, value in policy_data.get("default", {}).items():
        if field in resolved:
            resolved[field] = coerce_int(value)
    override = policy_data.get("tranche_overrides", {}).get(payee_id)
    if isinstance(override, dict):
        for field, value in override.items():
            if field in resolved:
                resolved[field] = coerce_int(value)
    return resolved


# --------------------------------------------------------------------------
# Accrual and carryforward (#WF-4106, #WF-4120)
# --------------------------------------------------------------------------
def accrue_interest(tranche: dict, period_days: int) -> int:
    base = tranche["balance_minor"] * tranche["coupon_bps"] * period_days
    if tranche["tranche_class"] == SUBORDINATE_CLASS:
        sub_accrual_base = base
        return _ceil_div(sub_accrual_base, ACCRUAL_DENOM)
    senior_accrual_base = base
    return senior_accrual_base // ACCRUAL_DENOM


def carryforward_out(kind: str, shortfall: int, coupon_bps: int, penalty_bps: int) -> int:
    """#WF-4120: unpaid interest compounds, unpaid principal and fees do not."""
    if shortfall <= 0:
        return 0
    if kind == "senior_interest":
        senior_carry_interest = shortfall * coupon_bps
        return shortfall + _ceil_div(senior_carry_interest, BPS)
    if kind == "sub_interest":
        sub_carry_interest = shortfall * (coupon_bps + penalty_bps)
        return shortfall + sub_carry_interest // BPS
    return shortfall


# --------------------------------------------------------------------------
# The cascade (#WF-4104 order, #WF-4110..#WF-4118 triggers)
# --------------------------------------------------------------------------
class Cascade:
    """Sequential priority cascade: each step takes what it is owed or what is left."""

    def __init__(self, funds: int) -> None:
        self.funds = funds
        self.steps: list[dict] = []

    def execute(
        self,
        kind: str,
        payee_id: str,
        due: int,
        cap: int | None = None,
        opening_balance: int = 0,
        closing_balance: int = 0,
        carryforward: int = 0,
        trigger_flag: str = "none",
    ) -> dict:
        funds_before = self.funds
        allowed = due if cap is None else min(due, cap)
        paid = max(min(allowed, funds_before), 0)
        self.funds = funds_before - paid
        step = {
            "step_index": len(self.steps),
            "step_id": f"{kind}:{payee_id}",
            "step_kind": kind,
            "payee_id": payee_id,
            "due_minor": due,
            "paid_minor": paid,
            "shortfall_minor": max(due - paid, 0),
            "funds_before_minor": funds_before,
            "funds_after_minor": self.funds,
            "opening_balance_minor": opening_balance,
            "closing_balance_minor": closing_balance,
            "carryforward_out_minor": carryforward,
            "trigger_flag": trigger_flag,
        }
        self.steps.append(step)
        return step


LEDGER_FIELDS = (
    "step_index",
    "step_id",
    "step_kind",
    "due_minor",
    "paid_minor",
    "shortfall_minor",
    "funds_before_minor",
    "funds_after_minor",
    "opening_balance_minor",
    "closing_balance_minor",
    "carryforward_out_minor",
    "trigger_flag",
)
REGISTER_FIELDS = ("payee_id", *LEDGER_FIELDS)
TRANCHE_KINDS = (
    "senior_interest",
    "senior_principal",
    "sub_interest",
    "sub_principal",
    "turbo_principal",
)


def run(input_path: str, output_dir: str) -> None:
    period, currency, raw_item_count, items = load_settlement(input_path)
    terms = json.loads(Path(TRANCHE_TERMS_PATH).read_text(encoding="utf-8"))
    policy_data = json.loads(Path(WATERFALL_POLICY_PATH).read_text(encoding="utf-8"))

    deal = resolve_policy("__default__", policy_data)
    period_days = coerce_int(terms.get("period_days", 0))
    pool_balance = coerce_int(terms.get("collateral", {}).get("pool_balance_minor", 0))
    residual_payee = canon_text(terms.get("residual_payee", ""))

    category_subtotals: dict[str, int] = {}
    for item in items:
        category_subtotals[item["category"]] = (
            category_subtotals.get(item["category"], 0) + item["amount_minor"]
        )
    # --- obligor concentration cap (#WF-7172) ---
    # Each obligor's total is accumulated in a single pass and looked up;
    # re-summing an obligor's lines for every item is the item count times the
    # lines per obligor and cannot meet the runtime budget.
    pool_total = sum(item["amount_minor"] for item in items)
    obligor_totals: dict[str, int] = {}
    for item in items:
        obligor_totals[item["obligor"]] = (
            obligor_totals.get(item["obligor"], 0) + item["amount_minor"]
        )
    cap_bps = deal["concentration_cap_bps"]
    allowance = cap_bps * pool_total // BPS if pool_total else 0
    # #WF-7172: an obligor whose share EXCEEDS the cap contributes only up to its
    # allowance. A share sitting exactly on the cap is not over it, so it
    # contributes in full even where flooring leaves its total above the
    # allowance.
    excluded_concentration = 0
    for total in obligor_totals.values():
        share_bps = total * BPS // pool_total if pool_total else 0
        if share_bps > cap_bps:
            excluded_concentration += max(total - allowance, 0)
    max_obligor_bps = max(
        (total * BPS // pool_total for total in obligor_totals.values()), default=0
    )
    available = pool_total - excluded_concentration

    tranches = load_tranches(terms)
    for tranche in tranches:
        tranche["interest_due_minor"] = (
            accrue_interest(tranche, period_days) + tranche["interest_carryforward_minor"]
        )
        tranche["principal_due_minor"] = min(
            tranche["scheduled_principal_minor"] + tranche["principal_carryforward_minor"],
            tranche["balance_minor"],
        )
    senior = [t for t in tranches if t["tranche_class"] != SUBORDINATE_CLASS]
    subordinate = [t for t in tranches if t["tranche_class"] == SUBORDINATE_CLASS]
    senior_interest_due = sum(t["interest_due_minor"] for t in senior)

    # --- interest coverage trigger (#WF-4110) --------------------------------
    eligible = sum(category_subtotals.get(name, 0) for name in INTEREST_ELIGIBLE_CATEGORIES)
    ic_bps = (eligible * BPS) // senior_interest_due if senior_interest_due > 0 else 0
    ic_breached = senior_interest_due > 0 and ic_bps < deal["ic_trigger_bps"]

    balances = {t["tranche_id"]: t["balance_minor"] for t in tranches}
    penalties = {
        t["tranche_id"]: resolve_policy(t["tranche_id"], policy_data)["sub_penalty_bps"]
        for t in tranches
    }
    cascade = Cascade(available)

    # --- step 1: deal fees, fee_id ascending ---------------------------------
    for fee in load_fees(terms, pool_balance):
        step = cascade.execute("fee", fee["fee_id"], fee["due_minor"])
        step["carryforward_out_minor"] = carryforward_out(
            "fee", step["shortfall_minor"], 0, 0
        )

    # --- step 2: senior interest, seniority ascending ------------------------
    for tranche in senior:
        step = cascade.execute(
            "senior_interest",
            tranche["tranche_id"],
            tranche["interest_due_minor"],
            opening_balance=balances[tranche["tranche_id"]],
            closing_balance=balances[tranche["tranche_id"]],
        )
        step["carryforward_out_minor"] = carryforward_out(
            "senior_interest", step["shortfall_minor"], tranche["coupon_bps"], 0
        )

    # --- step 3: subordinate interest, only while the coverage test holds ----
    if not ic_breached:
        for tranche in subordinate:
            step = cascade.execute(
                "sub_interest",
                tranche["tranche_id"],
                tranche["interest_due_minor"],
                opening_balance=balances[tranche["tranche_id"]],
                closing_balance=balances[tranche["tranche_id"]],
            )
            step["carryforward_out_minor"] = carryforward_out(
                "sub_interest",
                step["shortfall_minor"],
                tranche["coupon_bps"],
                penalties[tranche["tranche_id"]],
            )

    # --- step 4: senior principal, sequential by seniority -------------------
    principal_paid_total = 0
    for tranche in senior:
        opening = balances[tranche["tranche_id"]]
        step = cascade.execute(
            "senior_principal",
            tranche["tranche_id"],
            tranche["principal_due_minor"],
            opening_balance=opening,
            closing_balance=opening,
        )
        balances[tranche["tranche_id"]] = opening - step["paid_minor"]
        step["closing_balance_minor"] = balances[tranche["tranche_id"]]
        step["carryforward_out_minor"] = carryforward_out(
            "senior_principal", step["shortfall_minor"], tranche["coupon_bps"], 0
        )
        principal_paid_total += step["paid_minor"]

    # --- step 5: diverted turbo redemption when the coverage test failed -----
    if ic_breached:
        budget = min(cascade.funds, deal["divert_cap_minor"])
        for tranche in senior:
            allocation = min(budget, balances[tranche["tranche_id"]])
            if allocation <= 0:
                continue
            opening = balances[tranche["tranche_id"]]
            step = cascade.execute(
                "turbo_principal",
                tranche["tranche_id"],
                allocation,
                opening_balance=opening,
                closing_balance=opening,
                trigger_flag="ic_diverted",
            )
            balances[tranche["tranche_id"]] = opening - step["paid_minor"]
            step["closing_balance_minor"] = balances[tranche["tranche_id"]]
            budget -= step["paid_minor"]
            principal_paid_total += step["paid_minor"]

    # --- overcollateralisation trigger, measured after the principal steps ---
    senior_balance_after = sum(balances[t["tranche_id"]] for t in senior)
    pool_balance_after = pool_balance - principal_paid_total
    oc_bps = (
        (pool_balance_after * BPS) // senior_balance_after if senior_balance_after > 0 else 0
    )
    oc_breached = senior_balance_after > 0 and oc_bps < deal["oc_trigger_bps"]

    # --- step 6: subordinate principal, withheld while the test is breached --
    for tranche in subordinate:
        opening = balances[tranche["tranche_id"]]
        step = cascade.execute(
            "sub_principal",
            tranche["tranche_id"],
            tranche["principal_due_minor"],
            cap=0 if oc_breached else None,
            opening_balance=opening,
            closing_balance=opening,
            trigger_flag="oc_skipped" if oc_breached else "none",
        )
        balances[tranche["tranche_id"]] = opening - step["paid_minor"]
        step["closing_balance_minor"] = balances[tranche["tranche_id"]]
        step["carryforward_out_minor"] = carryforward_out(
            "sub_principal", step["shortfall_minor"], tranche["coupon_bps"], 0
        )

    # --- step 7: deferred subordinate interest, capped -----------------------
    if ic_breached:
        for tranche in subordinate:
            step = cascade.execute(
                "sub_interest",
                tranche["tranche_id"],
                tranche["interest_due_minor"],
                cap=deal["deferred_sub_cap_minor"],
                opening_balance=balances[tranche["tranche_id"]],
                closing_balance=balances[tranche["tranche_id"]],
                trigger_flag="ic_deferred",
            )
            step["carryforward_out_minor"] = carryforward_out(
                "sub_interest",
                step["shortfall_minor"],
                tranche["coupon_bps"],
                penalties[tranche["tranche_id"]],
            )

    # --- step 8: residual to the equity holder, capped -----------------------
    residual_cap = 0 if oc_breached else deal["residual_cap_minor"]
    cascade.execute(
        "residual",
        residual_payee,
        min(cascade.funds, residual_cap),
        trigger_flag="oc_capped" if oc_breached else "none",
    )
    unapplied = cascade.funds

    steps = cascade.steps

    # --- payment register: admission, ordering, then the per-payee cap -------
    admitted = []
    for step in steps:
        if step["step_kind"] not in REGISTERED_KINDS:
            continue
        policy = resolve_policy(step["payee_id"], policy_data)
        if (
            step["paid_minor"] >= policy["register_min_minor"]
            or step["shortfall_minor"] >= policy["register_shortfall_min_minor"]
        ):
            admitted.append(step)
    admitted.sort(
        key=lambda s: (
            -s["shortfall_minor"],
            -s["paid_minor"],
            -s["due_minor"],
            s["step_kind"],
            s["payee_id"],
            s["step_index"],
        )
    )
    seen: dict[str, int] = {}
    register: list[dict] = []
    for step in admitted:
        count = seen.get(step["payee_id"], 0)
        if count < PAYEE_CAP:
            register.append(step)
            seen[step["payee_id"]] = count + 1

    # --- summary aggregates (#WF-4148) ---------------------------------------
    def paid_of(kind: str) -> int:
        return sum(s["paid_minor"] for s in steps if s["step_kind"] == kind)

    step_kind_counts = {kind: 0 for kind in STEP_KIND_ORDER}
    for step in steps:
        step_kind_counts[step["step_kind"]] += 1

    summary = {
        "schema_version": SCHEMA_VERSION,
        "period": period,
        "settlement_currency": currency,
        "raw_item_count": raw_item_count,
        "settled_item_count": len(items),
        "excluded_concentration_minor": excluded_concentration,
        "max_obligor_concentration_bps": max_obligor_bps,
        "category_subtotals": {name: category_subtotals[name] for name in sorted(category_subtotals)},
        "available_funds_minor": available,
        "senior_interest_due_minor": senior_interest_due,
        "ic_bps": ic_bps,
        "ic_breached": ic_breached,
        "oc_bps": oc_bps,
        "oc_breached": oc_breached,
        "fee_paid_minor": paid_of("fee"),
        "senior_interest_paid_minor": paid_of("senior_interest"),
        "senior_principal_paid_minor": paid_of("senior_principal"),
        "turbo_principal_paid_minor": paid_of("turbo_principal"),
        "sub_interest_paid_minor": paid_of("sub_interest"),
        "sub_principal_paid_minor": paid_of("sub_principal"),
        "residual_paid_minor": paid_of("residual"),
        "unapplied_funds_minor": unapplied,
        "total_paid_minor": sum(s["paid_minor"] for s in steps),
        "total_shortfall_minor": sum(s["shortfall_minor"] for s in steps),
        "total_carryforward_out_minor": sum(s["carryforward_out_minor"] for s in steps),
        "executed_step_count": len(steps),
        "registered_step_count": len(register),
        "step_kind_counts": step_kind_counts,
        "max_paid_minor": max((s["paid_minor"] for s in register), default=0),
        "max_shortfall_minor": max((s["shortfall_minor"] for s in register), default=0),
        "max_carryforward_out_minor": max((s["carryforward_out_minor"] for s in steps), default=0),
    }

    # --- tranche ledger: object keyed by tranche, steps in execution order ---
    ledger: dict[str, list[dict]] = {t["tranche_id"]: [] for t in tranches}
    for step in steps:
        if step["step_kind"] in TRANCHE_KINDS and step["payee_id"] in ledger:
            ledger[step["payee_id"]].append(step)
    out_ledger = {
        tranche_id: [
            {field: step[field] for field in LEDGER_FIELDS}
            for step in sorted(ledger[tranche_id], key=lambda s: s["step_index"])
        ]
        for tranche_id in sorted(ledger)
    }
    out_register = [{field: step[field] for field in REGISTER_FIELDS} for step in register]

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "distribution_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    (out / "tranche_ledger.json").write_text(
        json.dumps(out_ledger, indent=2) + "\n", encoding="utf-8"
    )
    with (out / "payment_register.jsonl").open("w", encoding="utf-8") as handle:
        for row in out_register:
            handle.write(json.dumps(row, separators=(",", ":")) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Structured-finance payment waterfall engine")
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    run(args.input, args.output_dir)


if __name__ == "__main__":
    main()
