#!/usr/bin/env python3
"""Small checks that do not require the 36-run matrix."""

from __future__ import annotations

import sys
from pathlib import Path

from experiment_lib import matrix
from validate_results import duplicate_key_demo


def main() -> int:
    rows = matrix()
    if len(rows) != 36:
        print(f"matrix length {len(rows)}", file=sys.stderr)
        return 1
    keys = [(row["protocol"], row["num_nodes"], row["node_speed_mps"], row["run"]) for row in rows]
    if len(set(keys)) != 36:
        print("matrix keys are not unique", file=sys.stderr)
        return 1
    if rows[0]["protocol"] != "AODV" or rows[1]["protocol"] != "DSDV":
        print("matrix is not interleaved AODV then DSDV", file=sys.stderr)
        return 1
    caught = duplicate_key_demo()
    if "duplicate run keys" not in caught:
        print("duplicate key detector did not fire", file=sys.stderr)
        return 1
    changed = dict(rows[0])
    changed["node_speed_mps"] = 15.0
    if changed["node_speed_mps"] == rows[0]["node_speed_mps"]:
        print("changed-parameter fixture did not change", file=sys.stderr)
        return 1
    print("test_validation.py PASS")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
