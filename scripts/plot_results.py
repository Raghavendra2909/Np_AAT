#!/usr/bin/env python3
"""Plot the four required metrics against node speed from the aggregate CSV."""

from __future__ import annotations

import csv
import os
import sys
from collections import defaultdict
from pathlib import Path

from experiment_lib import RESULTS

os.environ.setdefault("MPLCONFIGDIR", str(RESULTS / ".mplconfig"))
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SERIES = (
    ("AODV", 10, "#0072B2", "o", "-", "AODV, 10 nodes"),
    ("DSDV", 10, "#E69F00", "s", "-", "DSDV, 10 nodes"),
    ("AODV", 20, "#56B4E9", "o", "--", "AODV, 20 nodes (more crowded)"),
    ("DSDV", 20, "#D55E00", "s", "--", "DSDV, 20 nodes (more crowded)"),
)

PLOTS = (
    (
        "pdr_percent",
        "How many sent packets arrived?",
        "Higher is better.",
        "Packets that arrived (%)",
        "pdr_vs_speed",
    ),
    (
        "avg_delay_ms",
        "How long did a packet take to arrive?",
        "Lower is better. This is only for packets that arrived.",
        "Travel time (milliseconds)",
        "delay_vs_speed",
    ),
    (
        "throughput_kbps",
        "How much data actually arrived?",
        "Higher is better. This counts only data that reached the receiver.",
        "Data received (kilobits per second)",
        "throughput_vs_speed",
    ),
    (
        "packet_loss_packets",
        "How many packets were lost?",
        "Lower is better. Lost means sent by the app but not received.",
        "Lost packets",
        "packet_loss_vs_speed",
    ),
)


def load_groups(path: Path) -> dict[tuple[str, int], list[dict]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 12:
        raise SystemExit(f"{path} has {len(rows)} rows; expected 12")
    groups = defaultdict(list)
    for row in rows:
        groups[(row["protocol"], int(float(row["num_nodes"])))].append(row)
    for members in groups.values():
        members.sort(key=lambda item: float(item["node_speed_mps"]))
    return groups


def main() -> int:
    source = RESULTS / "processed" / "aggregate_mean_std.csv"
    groups = load_groups(source)
    out_dir = RESULTS / "plots"
    out_dir.mkdir(parents=True, exist_ok=True)
    for metric, title, hint, ylabel, stem in PLOTS:
        figure, axis = plt.subplots(figsize=(9.2, 6.2))
        for protocol, nodes, color, marker, style, label in SERIES:
            members = groups[(protocol, nodes)]
            speeds = [float(row["node_speed_mps"]) for row in members]
            means = [float(row[f"{metric}_mean"]) for row in members]
            errors = [float(row[f"{metric}_sample_std"]) for row in members]
            axis.errorbar(
                speeds,
                means,
                yerr=errors,
                label=label,
                color=color,
                marker=marker,
                linestyle=style,
                capsize=5,
                linewidth=2.2,
                markersize=8,
            )
        axis.set_title(f"{title}\n{hint}", fontsize=15, pad=12)
        axis.set_xlabel("How fast the nodes are moving (meters per second)", fontsize=12)
        axis.set_ylabel(ylabel, fontsize=12)
        axis.set_xticks([5, 10, 20])
        axis.tick_params(labelsize=11)
        axis.grid(True, linestyle=":", alpha=0.7)
        axis.legend(frameon=True, fontsize=11, title="Each line is one protocol and crowd size")
        figure.text(
            0.5,
            0.01,
            "Each dot is the average of 3 repeats. The bar shows how much those repeats differed.",
            ha="center",
            fontsize=10,
            color="#333333",
        )
        figure.tight_layout(rect=(0, 0.05, 1, 1))
        png = out_dir / f"{stem}.png"
        svg = out_dir / f"{stem}.svg"
        figure.savefig(png, dpi=160)
        figure.savefig(svg)
        plt.close(figure)
        print(f"Wrote {png} and {svg}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
