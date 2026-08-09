#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Step 1: reconcile the period's collections (#WF-4170) ------------------
# /app/data/settled_collections.json ships as the servicer's unreconciled draft.
# Normalise every reported line to settlement minor units, net the reversals,
# drop the categories the control totals do not name, and write the reconciled
# set back to that path; nothing the engine distributes is correct until then.

python3 "${SCRIPT_DIR}/reconcile_collections.py"

# --- Step 2: restore the engine and produce the distribution artifacts ------

cp "${SCRIPT_DIR}/distribute_fixed.py" /app/workflow/distribute.py
python3 /app/workflow/distribute.py --output-dir /app/output
