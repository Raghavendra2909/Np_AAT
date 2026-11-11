#!/usr/bin/env python3
"""Validate raw FlowMonitor output, the 36-run ledger, aggregates, and animation files."""

from __future__ import annotations

import csv
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from experiment_lib import RESULTS, as_float, as_int, matrix, run_dir

APP_PORTS = (9000, 9001, 9002)
REQUIRED_FILES = ("run.log", "summary.csv", "manifest.json", "flowmon.xml", "mobility.csv", "flows.csv")


def parse_time_seconds(text: str) -> float:
    value = text.strip()
    if value.endswith("ns"):
        value = value[:-2]
    return float(value) / 1e9


def expected_addresses(num_nodes: int) -> list[tuple[str, str, int]]:
    """Node i is assigned 10.1.1.(i+1). Flows are 0->N-1, 1->N-2, 2->N-3."""
    flows = []
    destinations = (num_nodes - 1, num_nodes - 2, num_nodes - 3)
    for index, port in enumerate(APP_PORTS):
        src = f"10.1.1.{index + 1}"
        dst = f"10.1.1.{destinations[index] + 1}"
        flows.append((src, dst, port))
    return flows


def metrics_from_flowmon(path: Path, num_nodes: int) -> dict:
    root = ET.parse(path).getroot()
    stats_parent = root.find("FlowStats")
    class_parent = root.find("Ipv4FlowClassifier")
    if stats_parent is None or class_parent is None:
        raise ValueError(f"{path} is missing FlowStats or Ipv4FlowClassifier")
    stats = {item.get("flowId"): item for item in stats_parent.findall("Flow")}
    selected_ports = []
    totals = {
        "tx_packets": 0,
        "rx_packets": 0,
        "tx_bytes": 0,
        "rx_bytes": 0,
        "delay_sum_s": 0.0,
        "lost_packets": 0,
        "selected": 0,
    }
    expected = expected_addresses(num_nodes)
    for item in class_parent.findall("Flow"):
        flow_id = item.get("flowId")
        stat = stats.get(flow_id)
        if stat is None:
            continue
        identity = (
            item.get("sourceAddress"),
            item.get("destinationAddress"),
            int(item.get("protocol", "0")),
            int(item.get("destinationPort", "0")),
        )
        match = None
        for src, dst, port in expected:
            if identity == (src, dst, 17, port):
                match = port
        if match is None:
            continue
        selected_ports.append(match)
        totals["selected"] += 1
        totals["tx_packets"] += int(stat.get("txPackets", "0"))
        totals["rx_packets"] += int(stat.get("rxPackets", "0"))
        totals["tx_bytes"] += int(stat.get("txBytes", "0"))
        totals["rx_bytes"] += int(stat.get("rxBytes", "0"))
        totals["delay_sum_s"] += parse_time_seconds(stat.get("delaySum", "0ns"))
        totals["lost_packets"] += int(stat.get("lostPackets", "0"))
    totals["ports"] = tuple(sorted(selected_ports))
    return totals


def check_rows(rows: list[dict], folders: list[Path]) -> list[str]:
    problems = []
    if len(rows) != 36:
        problems.append(f"expected 36 rows, found {len(rows)}")
    keys = []
    for row, folder in zip(rows, folders):
        ident = row.get("experiment_id", folder.name)
        keys.append(
            (
                row.get("protocol"),
                str(int(float(row["num_nodes"]))),
                str(float(row["node_speed_mps"])),
                str(int(float(row["seed"]))),
                str(int(float(row["run"]))),
            )
        )
        if row.get("protocol") not in ("AODV", "DSDV"):
            problems.append(f"{ident}: bad protocol")
        if int(float(row["num_nodes"])) not in (10, 20):
            problems.append(f"{ident}: bad node count")
        if float(row["node_speed_mps"]) not in (5.0, 10.0, 20.0):
            problems.append(f"{ident}: bad speed")
        if int(float(row["run"])) not in (1, 2, 3):
            problems.append(f"{ident}: bad run")
        if row.get("status") != "PASS":
            problems.append(f"{ident}: status {row.get('status')}")
        tx = as_int(row, "tx_packets")
        rx = as_int(row, "rx_packets")
        if tx <= 0:
            problems.append(f"{ident}: TX is not positive")
        if rx < 0 or tx < rx:
            problems.append(f"{ident}: packet loss is negative or TX < RX")
        pdr = as_float(row, "pdr_percent")
        if not 0.0 <= pdr <= 100.0:
            problems.append(f"{ident}: PDR out of range {pdr}")
        if as_float(row, "avg_delay_ms") < 0:
            problems.append(f"{ident}: negative delay")
        if as_float(row, "throughput_kbps") < 0:
            problems.append(f"{ident}: negative throughput")
        if abs(as_float(row, "measurement_duration_s") - 55.0) > 1e-9:
            problems.append(f"{ident}: measurement window is not 55 s")
        if int(float(row["selected_flow_count"])) != 3:
            problems.append(f"{ident}: selected_flow_count is not 3")
        for name in REQUIRED_FILES:
            if not (folder / name).is_file():
                problems.append(f"{ident}: missing {name}")
        flows_path = folder / "flows.csv"
        if flows_path.is_file():
            with flows_path.open(newline="", encoding="utf-8") as handle:
                flow_rows = list(csv.DictReader(handle))
            selected = [item for item in flow_rows if item.get("selected") == "1"]
            ports = sorted(int(item["destination_port"]) for item in selected)
            if ports != list(APP_PORTS):
                problems.append(f"{ident}: selected ports {ports}")
            other = [
                item
                for item in flow_rows
                if item.get("selected") != "1" and int(item["destination_port"]) in APP_PORTS
            ]
            if other:
                problems.append(f"{ident}: unselected flow uses an application port")
        flowmon = folder / "flowmon.xml"
        if flowmon.is_file() and flowmon.stat().st_size > 0:
            try:
                recomputed = metrics_from_flowmon(flowmon, int(float(row["num_nodes"])))
            except (ET.ParseError, ValueError) as exc:
                problems.append(f"{ident}: flowmon xml {exc}")
            else:
                if recomputed["ports"] != APP_PORTS:
                    problems.append(f"{ident}: xml ports {recomputed['ports']}")
                for field in ("tx_packets", "rx_packets", "tx_bytes", "rx_bytes", "lost_packets"):
                    if recomputed[field] != as_int(row, field if field != "lost_packets" else "flowmonitor_lost_packets_diagnostic"):
                        problems.append(
                            f"{ident}: {field} summary {row.get(field if field != 'lost_packets' else 'flowmonitor_lost_packets_diagnostic')} "
                            f"!= xml {recomputed[field]}"
                        )
                # NS-3 writes Time values in flowmon.xml with limited
                # significant digits, so the text form is coarser than the
                # in-memory delaySum stored in summary.csv.
                xml_delay = recomputed["delay_sum_s"]
                delay_tol = max(1e-3, abs(xml_delay) * 1e-4)
                if abs(xml_delay - as_float(row, "delay_sum_s")) > delay_tol:
                    problems.append(f"{ident}: delay_sum mismatch")
                expected_pdr = 100.0 * as_int(row, "rx_packets") / as_int(row, "tx_packets")
                expected_delay = 1000.0 * as_float(row, "delay_sum_s") / as_int(row, "rx_packets")
                expected_tp = 8.0 * as_int(row, "rx_bytes") / (55.0 * 1000.0)
                expected_loss = as_int(row, "tx_packets") - as_int(row, "rx_packets")
                if abs(expected_pdr - as_float(row, "pdr_percent")) > 1e-6:
                    problems.append(f"{ident}: PDR formula mismatch")
                if abs(expected_delay - as_float(row, "avg_delay_ms")) > 1e-4:
                    problems.append(f"{ident}: delay formula mismatch")
                if abs(expected_tp - as_float(row, "throughput_kbps")) > 1e-4:
                    problems.append(f"{ident}: throughput formula mismatch")
                if expected_loss != as_int(row, "packet_loss_packets"):
                    problems.append(f"{ident}: packet loss formula mismatch")
    if len(keys) != len(set(keys)):
        problems.append("duplicate run keys")
    expected_keys = {
        (case["protocol"], str(case["num_nodes"]), str(float(case["node_speed_mps"])), "12345", str(case["run"]))
        for case in matrix()
    }
    if set(keys) != expected_keys:
        problems.append("run keys do not match the 36-run matrix")
    return problems


def check_aggregate(path: Path) -> list[str]:
    problems = []
    if not path.is_file():
        return ["missing aggregate_mean_std.csv"]
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 12:
        problems.append(f"aggregate groups {len(rows)} != 12")
    for row in rows:
        if int(row["n"]) != 3:
            problems.append(f"aggregate n != 3 for {row}")
    return problems


def check_mobility(path: Path) -> list[str]:
    if not path.is_file():
        return ["missing paired_mobility_validation.csv"]
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    problems = []
    if len(rows) != 18:
        problems.append(f"mobility pairs {len(rows)} != 18")
    for row in rows:
        if row.get("status") != "PASS":
            problems.append(f"mobility mismatch nodes={row.get('num_nodes')} speed={row.get('node_speed_mps')} run={row.get('run')}")
    return problems


def check_animations() -> list[str]:
    problems = []
    names = (
        "aodv_nodes10_speed20_run1.xml",
        "dsdv_nodes10_speed20_run1.xml",
    )
    for name in names:
        path = RESULTS / "animations" / name
        if not path.is_file() or path.stat().st_size == 0:
            problems.append(f"missing or empty {path}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "<anim" not in text and "<Animation" not in text:
            problems.append(f"{path} does not look like NetAnim XML")
    return problems


def duplicate_key_demo() -> list[str]:
    """Synthetic check: a changed/duplicate key must be reported."""
    rows = [
        {"protocol": "AODV", "num_nodes": "10", "node_speed_mps": "5.0", "seed": "12345", "run": "1", "experiment_id": "a"},
        {"protocol": "AODV", "num_nodes": "10", "node_speed_mps": "5.0", "seed": "12345", "run": "1", "experiment_id": "b"},
    ]
    keys = [
        (row["protocol"], row["num_nodes"], row["node_speed_mps"], row["seed"], row["run"])
        for row in rows
    ]
    problems = []
    if len(keys) != len(set(keys)):
        problems.append("duplicate run keys")
    return problems


def main() -> int:
    rows = []
    folders = []
    problems = []
    for case in matrix():
        folder = run_dir(RESULTS / "raw", case["protocol"], case["num_nodes"], case["node_speed_mps"], case["run"])
        summary = folder / "summary.csv"
        folders.append(folder)
        if not summary.is_file():
            problems.append(f"missing {summary}")
            continue
        with summary.open(newline="", encoding="utf-8") as handle:
            found = list(csv.DictReader(handle))
        if len(found) != 1:
            problems.append(f"{summary} row count {len(found)}")
            continue
        rows.append(found[0])
    if len(rows) == len(folders) == 36:
        problems.extend(check_rows(rows, folders))
    problems.extend(check_aggregate(RESULTS / "processed" / "aggregate_mean_std.csv"))
    problems.extend(check_mobility(RESULTS / "paired_mobility_validation.csv"))
    problems.extend(check_animations())
    caught = duplicate_key_demo()
    if caught != ["duplicate run keys"]:
        problems.append("duplicate-key self-test did not fire")
    summary = {
        "checked_runs": len(rows),
        "problem_count": len(problems),
        "problems": problems,
        "duplicate_key_self_test": caught,
        "status": "PASS" if not problems else "FAIL",
    }
    out = RESULTS / "processed" / "validation_summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Validation {summary['status']} ({len(problems)} problems) -> {out}")
    for item in problems:
        print(f"  - {item}")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
