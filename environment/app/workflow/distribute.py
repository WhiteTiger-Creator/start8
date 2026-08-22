#!/usr/bin/env python3
"""Structured-finance payment waterfall engine (INCIDENT SNAPSHOT — DO NOT SHIP).

This is the distribution engine as it stood when the period's trustee review failed.
It still evaluates stages against proposals the deal governance board later reversed,
so nothing it produces can be relied on. Restore it to the board's final decisions,
recorded in /app/incident/waterfall_governance_log.md.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_INPUT = "/app/data/settled_collections.json"
DEFAULT_OUTPUT_DIR = "/app/output"
TRANCHE_TERMS_PATH = "/app/data/tranche_terms.json"
WATERFALL_POLICY_PATH = "/app/data/waterfall_policy.json"

SCHEMA_VERSION = "waterfall-dist-v1"

BPS = 10000
ACCRUAL_DENOM = 3650000         # basis points times the days in a 365-day year
COUPON_MIN_BPS = 1
COUPON_MAX_BPS = 3000
SUBORDINATE_CLASS = "subordinate"
PAYEE_CAP = 2

STEP_KIND_ORDER = (
    "fee",
    "residual",
    "senior_interest",
    "senior_principal",
    "sub_interest",
    "sub_principal",
    "turbo_principal",
)

POLICY_BASELINE = {
    "ic_trigger_bps": 11000,
    "oc_trigger_bps": 12000,
    "divert_cap_minor": 3000000,
    "residual_cap_minor": 1500000,
    "deferred_sub_cap_minor": 900000,
    "register_min_minor": 25000,
    "register_shortfall_min_minor": 1,
    "sub_penalty_bps": 200,
}


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
        # the flat component plus the basis component on the pool balance
        due = coerce_int(row.get("flat_minor", 0)) + (
            pool_balance * coerce_int(row.get("basis_bps", 0)) // BPS
        )
        fees.append({"fee_id": canon_text(row.get("fee_id", "")), "due_minor": due})
    fees.sort(key=lambda row: row["fee_id"])
    return fees


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


def accrue_interest(tranche: dict, period_days: int) -> int:
    # coupon times balance times days, over the accrual denominator
    return tranche["balance_minor"] * tranche["coupon_bps"] * period_days // ACCRUAL_DENOM


class Cascade:
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
            # whatever the step left unpaid
            "carryforward_out_minor": max(due - paid, 0),
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
    available = sum(item["amount_minor"] for item in items)

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

    # the coverage test, taken against the note balances
    note_balance = sum(t["balance_minor"] for t in tranches)
    ic_bps = (available * BPS) // note_balance if note_balance > 0 else 0
    ic_breached = note_balance > 0 and ic_bps < deal["ic_trigger_bps"]

    balances = {t["tranche_id"]: t["balance_minor"] for t in tranches}
    cascade = Cascade(available)

    for fee in load_fees(terms, pool_balance):
        cascade.execute("fee", fee["fee_id"], fee["due_minor"])

    for tranche in senior:
        cascade.execute(
            "senior_interest",
            tranche["tranche_id"],
            tranche["interest_due_minor"],
            opening_balance=balances[tranche["tranche_id"]],
            closing_balance=balances[tranche["tranche_id"]],
        )

    # subordinate interest is reached only where the coverage test allows it
    if not ic_breached:
        for tranche in subordinate:
            cascade.execute(
                "sub_interest",
                tranche["tranche_id"],
                tranche["interest_due_minor"],
                opening_balance=balances[tranche["tranche_id"]],
                closing_balance=balances[tranche["tranche_id"]],
            )

    # the overcollateralisation test, taken against the senior balances as they
    # stand at this point in the cascade
    senior_balance_before = sum(balances[t["tranche_id"]] for t in senior)
    oc_bps = (pool_balance * BPS) // senior_balance_before if senior_balance_before > 0 else 0
    oc_breached = senior_balance_before > 0 and oc_bps < deal["oc_trigger_bps"]

    # the senior principal budget is shared out across the class
    scheduled_total = sum(t["principal_due_minor"] for t in senior)
    principal_budget = min(cascade.funds, scheduled_total)
    for tranche in senior:
        opening = balances[tranche["tranche_id"]]
        share = (
            principal_budget * tranche["principal_due_minor"] // scheduled_total
            if scheduled_total > 0
            else 0
        )
        step = cascade.execute(
            "senior_principal",
            tranche["tranche_id"],
            tranche["principal_due_minor"],
            cap=share,
            opening_balance=opening,
            closing_balance=opening,
        )
        balances[tranche["tranche_id"]] = opening - step["paid_minor"]
        step["closing_balance_minor"] = balances[tranche["tranche_id"]]

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

    # the residual payee takes what is left
    cascade.execute("residual", residual_payee, cascade.funds)
    unapplied = cascade.funds

    steps = cascade.steps

    # the register is built from the executed steps
    seen: dict[str, int] = {}
    register: list[dict] = []
    for step in steps:
        count = seen.get(step["payee_id"], 0)
        if count < PAYEE_CAP:
            register.append(step)
            seen[step["payee_id"]] = count + 1

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
        # maxima across the steps
        "max_paid_minor": max((s["paid_minor"] for s in steps), default=0),
        "max_shortfall_minor": max((s["shortfall_minor"] for s in steps), default=0),
        "max_carryforward_out_minor": max((s["carryforward_out_minor"] for s in steps), default=0),
    }

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
