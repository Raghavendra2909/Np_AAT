#!/usr/bin/env python3
"""Build all_runs.csv, aggregate mean/sample-std tables, and paired mobility checks."""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

from experiment_lib import RESULTS, as_float, as_int, matrix, run_dir, sample_std

SUMMARY_COLUMNS = [
    "experiment_id",
    "protocol",
    "ns3_version",
    "num_nodes",
    "area_x_m",
    "area_y_m",
    "node_speed_mps",
    "node_pause_s",
    "seed",
    "run",
    "wifi_standard",
    "phy_mode",
    "propagation_model",
    "tx_power_dbm",
    "flow_count",
    "packet_size_bytes",
    "flow_rate_kbps",
    "app_start_s",
    "app_stop_s",
    "measurement_duration_s",
    "sim_stop_s",
    "tx_packets",
    "rx_packets",
    "tx_bytes",
    "rx_bytes",
    "packet_loss_packets",
    "packet_loss_percent",
    "pdr_percent",
    "delay_sum_s",
    "avg_delay_ms",
    "throughput_kbps",
    "flowmonitor_lost_packets_diagnostic",
    "animation_enabled",
    "status",
    "selected_flow_count",
    "jitter_sum_s",
    "warnings",
]


def load_raw_rows() -> list[dict]:
    rows = []
    missing = []
    for case in matrix():
        folder = run_dir(
            RESULTS / "raw", case["protocol"], case["num_nodes"], case["node_speed_mps"], case["run"]
        )
        summary = folder / "summary.csv"
        if not summary.is_file():
            missing.append(str(summary))
            continue
        with summary.open(newline="", encoding="utf-8") as handle:
            found = list(csv.DictReader(handle))
        if len(found) != 1:
            raise SystemExit(f"{summary} does not have exactly one data row")
        row = found[0]
        row["source_summary"] = str(summary)
        rows.append(row)
    if missing:
        raise SystemExit("Missing summaries:\n" + "\n".join(missing))
    return rows


def write_all_runs(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(
        rows,
        key=lambda row: (
            int(float(row["num_nodes"])),
            float(row["node_speed_mps"]),
            int(float(row["run"])),
            row["protocol"],
        ),
    )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_COLUMNS + ["source_summary"], extrasaction="ignore")
        writer.writeheader()
        writer.writerows(ordered)


def write_aggregate(rows: list[dict], path: Path) -> None:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        if row.get("status") != "PASS":
            raise SystemExit(f"Refusing to aggregate non-PASS row {row.get('experiment_id')}")
        key = (row["protocol"], int(float(row["num_nodes"])), float(row["node_speed_mps"]))
        groups[key].append(row)
    metrics = [
        "pdr_percent",
        "avg_delay_ms",
        "throughput_kbps",
        "packet_loss_packets",
        "packet_loss_percent",
    ]
    fieldnames = [
        "protocol",
        "num_nodes",
        "node_speed_mps",
        "n",
        "tx_packets_sum",
        "rx_packets_sum",
        "tx_bytes_sum",
        "rx_bytes_sum",
    ]
    for metric in metrics:
        fieldnames.append(f"{metric}_mean")
        fieldnames.append(f"{metric}_sample_std")
    out_rows = []
    for protocol in ("AODV", "DSDV"):
        for nodes in (10, 20):
            for speed in (5.0, 10.0, 20.0):
                members = groups.get((protocol, nodes, speed), [])
                if len(members) != 3:
                    raise SystemExit(f"Group {protocol} n={nodes} v={speed} has n={len(members)}")
                record = {
                    "protocol": protocol,
                    "num_nodes": nodes,
                    "node_speed_mps": speed,
                    "n": 3,
                    "tx_packets_sum": sum(as_int(row, "tx_packets") for row in members),
                    "rx_packets_sum": sum(as_int(row, "rx_packets") for row in members),
                    "tx_bytes_sum": sum(as_int(row, "tx_bytes") for row in members),
                    "rx_bytes_sum": sum(as_int(row, "rx_bytes") for row in members),
                }
                for metric in metrics:
                    values = [as_float(row, metric) for row in members]
                    record[f"{metric}_mean"] = sum(values) / len(values)
                    record[f"{metric}_sample_std"] = sample_std(values)
                out_rows.append(record)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in out_rows:
            writer.writerow(record)


def compare_mobility(tolerance: float = 1e-6) -> list[dict]:
    results = []
    seen = []
    for case in matrix():
        if case["protocol"] != "AODV":
            continue
        key = (case["num_nodes"], case["node_speed_mps"], case["run"])
        if key in seen:
            continue
        seen.append(key)
        aodv = run_dir(RESULTS / "raw", "AODV", *key) / "mobility.csv"
        dsdv = run_dir(RESULTS / "raw", "DSDV", *key) / "mobility.csv"
        record = {
            "num_nodes": key[0],
            "node_speed_mps": key[1],
            "run": key[2],
            "tolerance_m": tolerance,
            "compared_rows": 0,
            "max_abs_diff_m": "",
            "status": "FAIL",
            "notes": "",
        }
        if not aodv.is_file() or not dsdv.is_file():
            record["notes"] = "missing mobility.csv"
            results.append(record)
            continue
        with aodv.open(newline="", encoding="utf-8") as handle:
            a_rows = list(csv.DictReader(handle))
        with dsdv.open(newline="", encoding="utf-8") as handle:
            d_rows = list(csv.DictReader(handle))
        if len(a_rows) != len(d_rows):
            record["notes"] = f"row count {len(a_rows)} vs {len(d_rows)}"
            results.append(record)
            continue
        max_diff = 0.0
        for a_row, d_row in zip(a_rows, d_rows):
            if a_row["node_id"] != d_row["node_id"] or a_row["time_s"] != d_row["time_s"]:
                record["notes"] = "node/time key mismatch"
                max_diff = float("inf")
                break
            for axis in ("x_m", "y_m", "z_m"):
                max_diff = max(max_diff, abs(float(a_row[axis]) - float(d_row[axis])))
        record["compared_rows"] = len(a_rows)
        record["max_abs_diff_m"] = max_diff
        if max_diff <= tolerance:
            record["status"] = "PASS"
        else:
            record["notes"] = record["notes"] or "positions differ beyond tolerance"
        results.append(record)
    path = RESULTS / "paired_mobility_validation.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "num_nodes",
                "node_speed_mps",
                "run",
                "tolerance_m",
                "compared_rows",
                "max_abs_diff_m",
                "status",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(results)
    return results


def main() -> int:
    rows = load_raw_rows()
    processed = RESULTS / "processed"
    write_all_runs(rows, processed / "all_runs.csv")
    write_aggregate(rows, processed / "aggregate_mean_std.csv")
    mobility = compare_mobility()
    bad = [row for row in mobility if row["status"] != "PASS"]
    print(f"Wrote {processed / 'all_runs.csv'} ({len(rows)} rows)")
    print(f"Wrote {processed / 'aggregate_mean_std.csv'} (12 groups)")
    print(f"Paired mobility PASS={len(mobility) - len(bad)} FAIL={len(bad)}")
    if bad:
        return 1
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
