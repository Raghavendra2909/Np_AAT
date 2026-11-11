#!/usr/bin/env python3
"""Build manet-aat and run the Gate 3 AODV/DSDV smoke cases plus CLI checks."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from experiment_lib import NS3, NS3_DIR, RESULTS, load_scenario, run_one

SMOKE = [
    {"protocol": "AODV", "num_nodes": 10, "node_speed_mps": 10.0, "run": 1, "seed": 12345},
    {"protocol": "DSDV", "num_nodes": 10, "node_speed_mps": 10.0, "run": 1, "seed": 12345},
]


def expect_failure(args: str, needle: str) -> None:
    completed = subprocess.run(
        [str(NS3), "run", "--no-build", args],
        cwd=NS3_DIR,
        capture_output=True,
        text=True,
        check=False,
    )
    combined = (completed.stdout or "") + (completed.stderr or "")
    if completed.returncode == 0 or needle not in combined:
        print(combined, file=sys.stderr)
        raise SystemExit(f"CLI check failed for: {args}")
    print(f"CLI reject OK: {needle}")


def main() -> int:
    print("Building manet-aat...")
    build = subprocess.run([str(NS3), "build", "manet-aat", "-j", "8"], cwd=NS3_DIR, check=False)
    if build.returncode != 0:
        return build.returncode

    expect_failure(
        "manet-aat --protocol=OLSR --numNodes=10 --nodeSpeed=10 --run=1 --outputDir=/tmp/manet-aat-unused",
        "AODV or DSDV",
    )
    expect_failure(
        "manet-aat --protocol=AODV --numNodes=7 --nodeSpeed=10 --run=1 --outputDir=/tmp/manet-aat-unused",
        "numNodes",
    )
    expect_failure(
        "manet-aat --protocol=AODV --numNodes=10 --nodeSpeed=15 --run=1 --outputDir=/tmp/manet-aat-unused",
        "nodeSpeed",
    )
    expect_failure(
        "manet-aat --protocol=AODV --numNodes=10 --nodeSpeed=10 --run=9 --outputDir=/tmp/manet-aat-unused",
        "run must",
    )
    expect_failure(
        "manet-aat --protocol=AODV --numNodes=10 --nodeSpeed=10 --run=1 --outputDir=",
        "outputDir",
    )
    expect_failure(
        "manet-aat --protocol=AODV --numNodes=10 --nodeSpeed=10 --run=1 --outputDir=/tmp/manet-aat-unused --notARealFlag=1",
        "Invalid command-line argument",
    )
    blocker = RESULTS / "smoke" / "not_a_directory"
    blocker.parent.mkdir(parents=True, exist_ok=True)
    blocker.write_text("this file blocks directory creation\n", encoding="utf-8")
    expect_failure(
        f"manet-aat --protocol=AODV --numNodes=10 --nodeSpeed=10 --run=1 --outputDir={blocker}/child",
        "cannot create output directory",
    )

    scenario = load_scenario()
    ledger = RESULTS / "smoke" / "experiment_status.csv"
    failures = 0
    for case in SMOKE:
        output = (
            RESULTS
            / "smoke"
            / f"protocol_{case['protocol'].lower()}"
            / "nodes_10"
            / "speed_10"
            / "run_1"
        )
        print(f"Smoke {case['protocol']} -> {output}")
        failures += run_one(case, output, scenario, ledger, overwrite=True)
    if failures:
        print(f"Smoke failures: {failures}", file=sys.stderr)
        return 1
    print("Smoke tests passed.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
