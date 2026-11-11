#!/usr/bin/env python3
"""Short commands for one run, the experiment matrix, analysis, and NetAnim.

Nothing in this file pins a results filename. Animation files are discovered
under results/, and the NetAnim program is discovered under tools/ or PATH.
Allowed protocols, node counts, and speeds come from experiment_lib.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from experiment_lib import (
    NODE_COUNTS,
    PROTOCOLS,
    RESULTS,
    ROOT,
    RUNS,
    SPEEDS,
    load_scenario,
    run_dir,
    run_one,
    speed_token,
)

NAME_RE = re.compile(
    r"(?P<protocol>aodv|dsdv)_nodes(?P<nodes>\d+)_speed(?P<speed>\d+(?:\.\d+)?)_run(?P<run>\d+)\.xml$",
    re.IGNORECASE,
)


def die(message: str) -> None:
    print(f"manet: {message}", file=sys.stderr)
    raise SystemExit(1)


def find_netanim() -> Path:
    override = os.environ.get("NETANIM", "").strip()
    if override:
        path = Path(override)
        if path.is_file() and os.access(path, os.X_OK):
            return path
        die(f"NETANIM={override} is not an executable file")
    found = []
    tools = ROOT / "tools"
    if tools.is_dir():
        for path in tools.rglob("NetAnim"):
            if path.is_file() and os.access(path, os.X_OK):
                found.append(path)
    on_path = shutil.which("NetAnim")
    if on_path:
        found.append(Path(on_path))
    if not found:
        die("NetAnim was not found. Build it under tools/ or set NETANIM to the executable.")
    found.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return found[0]


def parse_animation_name(name: str) -> dict | None:
    match = NAME_RE.search(name)
    if not match:
        return None
    return {
        "protocol": match.group("protocol").upper(),
        "num_nodes": int(match.group("nodes")),
        "node_speed_mps": float(match.group("speed")),
        "run": int(match.group("run")),
    }


def meta_from_manifest(path: Path) -> dict | None:
    if not path.is_file():
        return None
    import json

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    try:
        return {
            "protocol": str(data["protocol"]).upper(),
            "num_nodes": int(data["num_nodes"]),
            "node_speed_mps": float(data["node_speed_mps"]),
            "run": int(data["run"]),
        }
    except (KeyError, TypeError, ValueError):
        return None


def discover_animations() -> list[dict]:
    """Collect animation XML files. Prefer the copy under results/animations/."""
    records = []
    seen = set()

    def add(path: Path, meta: dict | None, source: str) -> None:
        if not path.is_file() or path.stat().st_size == 0:
            return
        info = meta or parse_animation_name(path.name) or {}
        key = (
            info.get("protocol"),
            info.get("num_nodes"),
            info.get("node_speed_mps"),
            info.get("run"),
            str(path.resolve()),
        )
        if key in seen:
            return
        seen.add(key)
        records.append({"path": path, "source": source, **info})

    animations = RESULTS / "animations"
    if animations.is_dir():
        for path in sorted(animations.glob("*.xml")):
            add(path, parse_animation_name(path.name), "animations")
    for bucket in ("raw", "pilot", "smoke"):
        root = RESULTS / bucket
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("animation.xml")):
            add(path, meta_from_manifest(path.parent / "manifest.json"), bucket)
    return records


def filter_animations(records: list[dict], args: argparse.Namespace) -> list[dict]:
    selected = records
    if args.protocol:
        token = args.protocol.upper()
        selected = [item for item in selected if item.get("protocol") == token]
    if args.nodes is not None:
        selected = [item for item in selected if item.get("num_nodes") == args.nodes]
    if args.speed is not None:
        selected = [item for item in selected if item.get("node_speed_mps") == float(args.speed)]
    if args.run is not None:
        selected = [item for item in selected if item.get("run") == args.run]
    if getattr(args, "xml", None):
        wanted = Path(args.xml).resolve()
        selected = [item for item in selected if item["path"].resolve() == wanted]
    # One row per scenario, preferring the standalone animations/ copy.
    best: dict[tuple, dict] = {}
    for item in selected:
        key = (item.get("protocol"), item.get("num_nodes"), item.get("node_speed_mps"), item.get("run"))
        current = best.get(key)
        if current is None or (item.get("source") == "animations" and current.get("source") != "animations"):
            best[key] = item
    return list(best.values())


def describe(item: dict) -> str:
    protocol = item.get("protocol") or "?"
    nodes = item.get("num_nodes")
    speed = item.get("node_speed_mps")
    run = item.get("run")
    bits = [protocol]
    if nodes is not None:
        bits.append(f"nodes={nodes}")
    if speed is not None:
        bits.append(f"speed={speed_token(float(speed))}")
    if run is not None:
        bits.append(f"run={run}")
    return " ".join(bits)


def print_animations(records: list[dict]) -> None:
    if not records:
        print("No animation XML files found under results/.")
        return
    for item in records:
        print(f"{describe(item)}  {item['path']}")


def command_anim(args: argparse.Namespace) -> int:
    if args.xml:
        path = Path(args.xml)
        if not path.is_file():
            die(f"animation file not found: {path}")
        records = [{"path": path, "source": "given", **(parse_animation_name(path.name) or {})}]
    else:
        records = filter_animations(discover_animations(), args)
    if args.list:
        print_animations(records)
        return 0 if records else 1
    if not records:
        print("No animation XML matched that selection.", file=sys.stderr)
        print_animations(discover_animations())
        return 1
    if len(records) > 1 and not args.all:
        print_animations(records)
        print("\nMore than one file matches. Narrow it, for example: ./manet anim aodv --speed 20 --run 1")
        print("Or open every match with: ./manet anim --all")
        return 0
    binary = find_netanim()
    if args.dry_run:
        for item in records:
            print(f"{binary} {item['path']}")
        return 0
    if len(records) == 1:
        item = records[0]
        print(f"Opening {describe(item)}")
        os.execv(str(binary), [str(binary), str(item["path"])])
    for item in records:
        print(f"Opening {describe(item)}")
        subprocess.Popen([str(binary), str(item["path"])], start_new_session=True)
    return 0


def check_case(protocol: str, nodes: int, speed: float, run: int) -> dict:
    protocol = protocol.upper()
    if protocol not in PROTOCOLS:
        die(f"protocol must be one of: {', '.join(PROTOCOLS)}")
    if nodes not in NODE_COUNTS:
        die(f"nodes must be one of: {', '.join(str(value) for value in NODE_COUNTS)}")
    speeds = [float(value) for value in SPEEDS]
    if float(speed) not in speeds:
        die(f"speed must be one of: {', '.join(speed_token(value) for value in SPEEDS)}")
    if run not in RUNS:
        die(f"run must be one of: {', '.join(str(value) for value in RUNS)}")
    return {
        "protocol": protocol,
        "num_nodes": nodes,
        "node_speed_mps": float(speed),
        "run": run,
    }


def command_run(args: argparse.Namespace) -> int:
    case = check_case(args.protocol, args.nodes, args.speed, args.run)
    case["enable_animation"] = args.animate
    scenario = load_scenario()
    bucket = RESULTS / args.where
    output = run_dir(bucket, case["protocol"], case["num_nodes"], case["node_speed_mps"], case["run"])
    ledger = RESULTS / "experiment_status.csv" if args.where == "raw" else bucket / "experiment_status.csv"
    print(f"Running {describe({'protocol': case['protocol'], 'num_nodes': case['num_nodes'], 'node_speed_mps': case['node_speed_mps'], 'run': case['run']})}")
    print(f"Output: {output}")
    return run_one(case, output, scenario, ledger, overwrite=args.force)


def delegate(script: str, extra: list[str]) -> int:
    path = Path(__file__).resolve().parent / script
    return subprocess.call([sys.executable, str(path), *extra])


def command_analyze(_args: argparse.Namespace) -> int:
    for script in ("process_results.py", "validate_results.py", "plot_results.py", "generate_report.py"):
        code = delegate(script, [])
        if code != 0:
            return code
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="manet",
        description="Short commands for the MANET AAT. Paths and animation files are discovered, not fixed in the command.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    anim = sub.add_parser("anim", help="Open a discovered NetAnim XML file")
    anim.add_argument("protocol", nargs="?", help=f"Protocol to match ({', '.join(PROTOCOLS)})")
    anim.add_argument("--nodes", type=int, help="Node count")
    anim.add_argument("--speed", type=float, help="Nominal speed in m/s")
    anim.add_argument("--run", type=int, help="Run number")
    anim.add_argument("--xml", help="Open this XML file instead of searching")
    anim.add_argument("--all", action="store_true", help="Open every file that matches")
    anim.add_argument("--list", action="store_true", help="List matches and do not launch")
    anim.add_argument("--dry-run", action="store_true", help="Print the NetAnim command only")
    anim.set_defaults(func=command_anim)

    run = sub.add_parser("run", help="Run one simulation. Area and power come from config/scenario.json")
    run.add_argument("protocol", help=f"One of: {', '.join(PROTOCOLS)}")
    run.add_argument("nodes", type=int)
    run.add_argument("speed", type=float)
    run.add_argument("run", type=int)
    run.add_argument("--animate", action="store_true", help="Write NetAnim XML for this run")
    run.add_argument("--force", action="store_true", help="Overwrite an existing summary.csv")
    run.add_argument("--where", default="raw", choices=["raw", "pilot", "smoke"], help="Results bucket")
    run.set_defaults(func=command_run)

    for name, script, help_text in (
        ("build", None, "Build the manet-aat simulation"),
        ("smoke", "run_smoke_tests.py", "CLI checks plus the two smoke runs"),
        ("pilot", "run_experiments.py", "Calibration runs, kept out of the final aggregate"),
        ("matrix", "run_experiments.py", "Run every planned matrix case"),
        ("analyze", None, "Rebuild tables, validation, plots, and the report from raw results"),
    ):
        item = sub.add_parser(name, help=help_text)
        if name in ("pilot", "matrix"):
            item.add_argument("--force", action="store_true")
        item.set_defaults(func=name, script=script)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "build":
        from experiment_lib import NS3, NS3_DIR

        return subprocess.call([str(NS3), "build", "manet-aat", "-j", "8"], cwd=NS3_DIR)
    if args.command == "smoke":
        return delegate("run_smoke_tests.py", [])
    if args.command == "pilot":
        extra = ["--pilot"]
        if args.force:
            extra.append("--force")
        return delegate("run_experiments.py", extra)
    if args.command == "matrix":
        extra = ["--force"] if args.force else []
        return delegate("run_experiments.py", extra)
    if args.command == "analyze":
        return command_analyze(args)
    return args.func(args)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
