"""Shared paths, the 36-run matrix, and CSV helpers for the MANET AAT."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NS3_DIR = ROOT / "ns-3.45"
NS3 = NS3_DIR / "ns3"
RESULTS = ROOT / "results"
SOURCE = NS3_DIR / "scratch" / "manet-aat.cc"

PROTOCOLS = ("AODV", "DSDV")
NODE_COUNTS = (10, 20)
SPEEDS = (5.0, 10.0, 20.0)
RUNS = (1, 2, 3)
SEED = 12345

# Representative NetAnim cases required by the visualization plan.
ANIMATION_CASES = {("AODV", 10, 20.0, 1), ("DSDV", 10, 20.0, 1)}

SCENARIO_PATH = ROOT / "config" / "scenario.json"
DEFAULT_SCENARIO = {
    "area_x_m": 500.0,
    "area_y_m": 500.0,
    "tx_power_dbm": 7.5,
    "node_pause_s": 0.0,
    "seed": SEED,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_scenario() -> dict:
    if not SCENARIO_PATH.is_file():
        raise FileNotFoundError(
            f"Missing {SCENARIO_PATH}. Create it before running experiments."
        )
    with SCENARIO_PATH.open(encoding="utf-8") as handle:
        data = json.load(handle)
    for key in ("area_x_m", "area_y_m", "tx_power_dbm", "node_pause_s", "seed"):
        if key not in data:
            raise ValueError(f"{SCENARIO_PATH} is missing '{key}'")
    return data


def source_sha256() -> str:
    digest = hashlib.sha256()
    digest.update(SOURCE.read_bytes())
    return digest.hexdigest()


def speed_token(speed: float) -> str:
    return str(int(speed)) if float(speed).is_integer() else str(speed)


def protocol_token(protocol: str) -> str:
    return protocol.strip().lower()


def run_dir(root: Path, protocol: str, nodes: int, speed: float, run: int) -> Path:
    return (
        root
        / f"protocol_{protocol_token(protocol)}"
        / f"nodes_{nodes}"
        / f"speed_{speed_token(speed)}"
        / f"run_{run}"
    )


def experiment_id(protocol: str, nodes: int, speed: float, seed: int, run: int) -> str:
    return f"{protocol}_n{nodes}_s{speed_token(speed)}_seed{seed}_r{run}"


def matrix() -> list[dict]:
    """AODV then DSDV for each (nodes, speed, run), as the experiment plan requests."""
    rows = []
    for nodes in NODE_COUNTS:
        for speed in SPEEDS:
            for run in RUNS:
                for protocol in PROTOCOLS:
                    rows.append(
                        {
                            "protocol": protocol,
                            "num_nodes": nodes,
                            "node_speed_mps": float(speed),
                            "run": run,
                            "seed": SEED,
                        }
                    )
    if len(rows) != 36:
        raise RuntimeError(f"matrix size is {len(rows)}, expected 36")
    keys = [(r["protocol"], r["num_nodes"], r["node_speed_mps"], r["run"]) for r in rows]
    if len(set(keys)) != 36:
        raise RuntimeError("matrix contains duplicate keys")
    return rows


def simulation_command(case: dict, output_dir: Path, scenario: dict, overwrite: bool) -> list[str]:
    if "enable_animation" in case:
        animate = bool(case["enable_animation"])
    else:
        animate = (
            case["protocol"],
            case["num_nodes"],
            float(case["node_speed_mps"]),
            case["run"],
        ) in ANIMATION_CASES
    args = (
        f"manet-aat --protocol={case['protocol']} --numNodes={case['num_nodes']} "
        f"--nodeSpeed={speed_token(case['node_speed_mps'])} --nodePause={scenario['node_pause_s']} "
        f"--seed={scenario['seed']} --run={case['run']} "
        f"--outputDir={output_dir} --enableAnimation={1 if animate else 0} "
        f"--overwrite={1 if overwrite else 0} "
        f"--areaX={scenario['area_x_m']} --areaY={scenario['area_y_m']} "
        f"--txPowerDbm={scenario['tx_power_dbm']}"
    )
    return [str(NS3), "run", "--no-build", args]


def read_summary(path: Path) -> dict:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1:
        raise ValueError(f"{path} must contain exactly one data row, found {len(rows)}")
    return rows[0]


def write_status_row(ledger: Path, row: dict) -> None:
    ledger.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "experiment_id",
        "protocol",
        "num_nodes",
        "node_speed_mps",
        "seed",
        "run",
        "command",
        "cwd",
        "start_time",
        "end_time",
        "exit_code",
        "status",
        "output_dir",
        "notes",
    ]
    existing = []
    if ledger.is_file():
        with ledger.open(newline="", encoding="utf-8") as handle:
            existing = list(csv.DictReader(handle))
    replaced = False
    for index, old in enumerate(existing):
        if old.get("experiment_id") == row["experiment_id"] and old.get("output_dir") == row["output_dir"]:
            existing[index] = {key: row.get(key, "") for key in fieldnames}
            replaced = True
            break
    if not replaced:
        existing.append({key: row.get(key, "") for key in fieldnames})
    with ledger.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing)


def merge_manifest(path: Path, extra: dict) -> None:
    data = {}
    if path.is_file():
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    data.update(extra)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def run_one(case: dict, output_dir: Path, scenario: dict, ledger: Path, overwrite: bool) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = simulation_command(case, output_dir, scenario, overwrite)
    started = utc_now()
    log_path = output_dir / "run.log"
    with log_path.open("w", encoding="utf-8") as log:
        log.write(f"# start_utc {started}\n")
        log.write(f"# cwd {NS3_DIR}\n")
        log.write("# command " + " ".join(command) + "\n\n")
        log.flush()
        completed = subprocess.run(
            command,
            cwd=NS3_DIR,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
        )
        ended = utc_now()
        log.write(f"\n# end_utc {ended}\n")
        log.write(f"# exit_code {completed.returncode}\n")
    summary_path = output_dir / "summary.csv"
    manifest_path = output_dir / "manifest.json"
    animation_xml = output_dir / "animation.xml"
    if animation_xml.is_file() and animation_xml.stat().st_size > 0:
        animations = RESULTS / "animations"
        animations.mkdir(parents=True, exist_ok=True)
        copied = (
            animations
            / f"{protocol_token(case['protocol'])}_nodes{case['num_nodes']}_speed{speed_token(case['node_speed_mps'])}_run{case['run']}.xml"
        )
        shutil.copyfile(animation_xml, copied)
    notes = ""
    status = "FAIL"
    if completed.returncode == 0 and summary_path.is_file():
        summary = read_summary(summary_path)
        status = "PASS" if summary.get("status") == "PASS" else "FAIL"
        if status != "PASS":
            notes = f"summary status={summary.get('status')} warnings={summary.get('warnings', '')}"
    elif completed.returncode != 0:
        notes = f"process exit {completed.returncode}"
        if summary_path.is_file():
            summary = read_summary(summary_path)
            notes += f"; summary status={summary.get('status')}"
    else:
        notes = "missing summary.csv"
    required = ["summary.csv", "manifest.json", "flowmon.xml", "mobility.csv", "flows.csv"]
    missing = [name for name in required if not (output_dir / name).is_file()]
    if missing:
        status = "FAIL"
        notes = (notes + "; " if notes else "") + "missing " + ",".join(missing)
    if manifest_path.is_file() or True:
        try:
            merge_manifest(
                manifest_path,
                {
                    "exit_code": completed.returncode,
                    "wall_start_utc": started,
                    "wall_end_utc": ended,
                    "cwd": str(NS3_DIR),
                    "full_command": command,
                    "os": platform.platform(),
                    "python": platform.python_version(),
                    "source_sha256": source_sha256(),
                    "runner_status": status,
                },
            )
        except (OSError, json.JSONDecodeError) as exc:
            notes = (notes + "; " if notes else "") + f"manifest update failed: {exc}"
            status = "FAIL"
    write_status_row(
        ledger,
        {
            "experiment_id": experiment_id(
                case["protocol"], case["num_nodes"], case["node_speed_mps"], int(scenario["seed"]), case["run"]
            ),
            "protocol": case["protocol"],
            "num_nodes": case["num_nodes"],
            "node_speed_mps": speed_token(case["node_speed_mps"]),
            "seed": scenario["seed"],
            "run": case["run"],
            "command": " ".join(command),
            "cwd": str(NS3_DIR),
            "start_time": started,
            "end_time": ended,
            "exit_code": completed.returncode,
            "status": status,
            "output_dir": str(output_dir),
            "notes": notes,
        },
    )
    return 0 if status == "PASS" else 1


def sample_std(values: list[float]) -> float:
    n = len(values)
    if n < 2:
        return float("nan")
    mean = sum(values) / n
    variance = sum((value - mean) ** 2 for value in values) / (n - 1)
    return math.sqrt(variance)


def as_float(row: dict, key: str) -> float:
    text = (row.get(key) or "").strip()
    if text == "":
        raise ValueError(f"missing numeric field {key}")
    return float(text)


def as_int(row: dict, key: str) -> int:
    return int(float(as_float(row, key)))
