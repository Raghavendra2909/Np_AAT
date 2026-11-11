#!/usr/bin/env python3
"""Run the frozen 36-simulation matrix. Exit non-zero if any run is not PASS."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from experiment_lib import RESULTS, load_scenario, matrix, run_dir, run_one, utc_now


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing per-run summary.csv",
    )
    parser.add_argument(
        "--pilot",
        action="store_true",
        help="Run four calibration cases into results/pilot instead of the 36-run matrix",
    )
    args = parser.parse_args()
    scenario = load_scenario()
    if args.pilot:
        cases = [
            {"protocol": "AODV", "num_nodes": 10, "node_speed_mps": 20.0, "run": 1},
            {"protocol": "DSDV", "num_nodes": 10, "node_speed_mps": 20.0, "run": 1},
            {"protocol": "AODV", "num_nodes": 20, "node_speed_mps": 20.0, "run": 1},
            {"protocol": "DSDV", "num_nodes": 20, "node_speed_mps": 20.0, "run": 1},
        ]
        root = RESULTS / "pilot"
        ledger = root / "experiment_status.csv"
    else:
        cases = matrix()
        root = RESULTS / "raw"
        ledger = RESULTS / "experiment_status.csv"

    print(f"{utc_now()} starting {len(cases)} runs under {root}")
    failures = []
    for index, case in enumerate(cases, start=1):
        output = run_dir(root, case["protocol"], case["num_nodes"], case["node_speed_mps"], case["run"])
        print(
            f"[{index}/{len(cases)}] {case['protocol']} nodes={case['num_nodes']} "
            f"speed={case['node_speed_mps']} run={case['run']}"
        )
        code = run_one(case, output, scenario, ledger, overwrite=args.force)
        if code != 0:
            print(f"  attempt failed, retrying once: {output}")
            code = run_one(case, output, scenario, ledger, overwrite=True)
        if code != 0:
            failures.append(str(output))
            print(f"  FAIL {output}", file=sys.stderr)
        else:
            print(f"  PASS {output}")
    print(f"{utc_now()} finished. failures={len(failures)} ledger={ledger}")
    if failures:
        print("Failed runs:", file=sys.stderr)
        for item in failures:
            print(f"  {item}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
