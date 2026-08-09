#!/usr/bin/env python3
"""Reconcile the raw servicer collections file into the period's settled collections.

Implements the deal governance board's final reconciliation decision (#WF-4170 in
/app/incident/waterfall_governance_log.md), which supersedes the #WF-4044 draft and
revises the #WF-4009 interim: every reported line is normalised to settlement minor
units (whole-currency lines scaled by one hundred, foreign lines multiplied by the
quoted rate and floored), reversals net against the original line they name, an item
whose category the control totals do not name is not settled this period, and the
result is written to /app/data/settled_collections.json where the distribution engine
expects it. The per-category totals of the reconciled set tie exactly to
/app/data/control_totals.json; if they do not, the cascade is wrong from its first step.
"""

from __future__ import annotations

import json
from pathlib import Path

COLLECTIONS_PATH = Path("/app/data/collections.json")
CONTROL_TOTALS_PATH = Path("/app/data/control_totals.json")
SETTLED_PATH = Path("/app/data/settled_collections.json")

MINOR_PER_MAJOR = 100
BPS = 10000


def canon_text(value: object) -> str:
    text = str(value).strip().lower()
    return text if text else "unknown"


def collapse_ws(value: object) -> str:
    return " ".join(str(value).split())


def major_to_minor(value: object) -> int:
    """A whole-currency amount scaled to minor units by exact integer arithmetic."""
    text = str(value).strip()
    sign = -1 if text.startswith("-") else 1
    text = text.lstrip("+-")
    whole, _, frac = text.partition(".")
    frac = (frac + "00")[:2]
    return sign * (int(whole or "0") * MINOR_PER_MAJOR + int(frac or "0"))


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


def normalise_amount(row: dict, settlement_currency: str, fx_rates: dict) -> int:
    """#WF-4170: scale to settlement minor units, then convert, flooring the rate leg."""
    unit = canon_text(row.get("unit", ""))
    amount = major_to_minor(row.get("reported_amount", 0)) if unit == "major" else coerce_int(
        row.get("reported_amount", 0)
    )
    currency = str(row.get("currency", "")).strip().upper()
    if currency and currency != settlement_currency:
        rate_bps = coerce_int(fx_rates.get(currency, 0))
        fx_converted = amount * rate_bps
        amount = fx_converted // BPS
    return amount


def reconcile(collections: list[dict], control: dict) -> dict:
    settlement_currency = str(control.get("settlement_currency", "")).strip().upper()
    fx_rates = control.get("fx_rates_bps", {})
    control_categories = control.get("category_totals_minor", {})

    items: dict[str, dict] = {}
    order: list[str] = []
    reversals: list[dict] = []
    for row in collections:
        item_id = collapse_ws(row.get("item_id", ""))
        amount = normalise_amount(row, settlement_currency, fx_rates)
        if canon_text(row.get("entry_type", "")) == "reversal":
            reversals.append({"reverses": collapse_ws(row.get("reverses", "")), "amount": amount})
            continue
        items[item_id] = {
            "item_id": item_id,
            "category": canon_text(row.get("category", "")),
            "obligor": canon_text(row.get("obligor", "")),
            "amount_minor": amount,
        }
        order.append(item_id)

    # A reversal nets against the original line it names, floored at zero; a reversal
    # naming a line this file does not carry contributes nothing of its own.
    for reversal in reversals:
        target = items.get(reversal["reverses"])
        if target is None:
            continue
        target["amount_minor"] = max(target["amount_minor"] - reversal["amount"], 0)

    settled = [
        items[item_id]
        for item_id in order
        if items[item_id]["category"] in control_categories and items[item_id]["amount_minor"] > 0
    ]
    settled.sort(key=lambda row: (row["category"], row["item_id"]))

    totals: dict[str, int] = {}
    for row in settled:
        totals[row["category"]] = totals.get(row["category"], 0) + row["amount_minor"]

    return {
        "period": collapse_ws(control.get("period", "")),
        "settlement_currency": settlement_currency,
        "category_totals_minor": {name: totals[name] for name in sorted(totals)},
        "items": settled,
    }


def main() -> None:
    collections = json.loads(COLLECTIONS_PATH.read_text(encoding="utf-8"))
    control = json.loads(CONTROL_TOTALS_PATH.read_text(encoding="utf-8"))
    settled = reconcile(collections, control)

    expected = control.get("category_totals_minor", {})
    produced = settled["category_totals_minor"]
    if produced != {name: coerce_int(value) for name, value in sorted(expected.items())}:
        raise SystemExit(f"reconciled totals do not tie to the control totals: {produced}")

    SETTLED_PATH.write_text(json.dumps(settled, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
