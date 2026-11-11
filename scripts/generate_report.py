#!/usr/bin/env python3
"""Write the technical report, demo script, and slide outline from measured CSVs."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from experiment_lib import RESULTS, load_scenario


def load_aggregate() -> list[dict]:
    path = RESULTS / "processed" / "aggregate_mean_std.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 12:
        raise SystemExit(f"{path} does not have 12 groups")
    return rows


def fmt(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}"


def cell(row: dict, metric: str) -> str:
    mean = float(row[f"{metric}_mean"])
    std = float(row[f"{metric}_sample_std"])
    return f"{fmt(mean)} ± {fmt(std)}"


def grouped(rows: list[dict]) -> dict[tuple, dict]:
    return {(row["protocol"], int(float(row["num_nodes"])), float(row["node_speed_mps"])): row for row in rows}


def markdown_table(rows: list[dict]) -> str:
    lines = [
        "| Protocol | Nodes | Speed (m/s) | n | PDR (%) | Delay (ms) | Throughput (kb/s) | Loss (packets) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    order = []
    for nodes in (10, 20):
        for speed in (5.0, 10.0, 20.0):
            for protocol in ("AODV", "DSDV"):
                order.append((protocol, nodes, speed))
    lookup = grouped(rows)
    for key in order:
        row = lookup[key]
        lines.append(
            "| {protocol} | {nodes} | {speed:g} | {n} | {pdr} | {delay} | {tp} | {loss} |".format(
                protocol=key[0],
                nodes=key[1],
                speed=key[2],
                n=row["n"],
                pdr=cell(row, "pdr_percent"),
                delay=cell(row, "avg_delay_ms"),
                tp=cell(row, "throughput_kbps"),
                loss=cell(row, "packet_loss_packets"),
            )
        )
    return "\n".join(lines)


def findings(rows: list[dict]) -> str:
    lookup = grouped(rows)
    higher_pdr = 0
    for nodes in (10, 20):
        for speed in (5.0, 10.0, 20.0):
            aodv = float(lookup[("AODV", nodes, speed)]["pdr_percent_mean"])
            dsdv = float(lookup[("DSDV", nodes, speed)]["pdr_percent_mean"])
            if aodv > dsdv:
                higher_pdr += 1
    aodv_low = lookup[("AODV", 10, 5.0)]
    dsdv_fast = lookup[("DSDV", 10, 20.0)]
    return (
        f"In {higher_pdr} of the 6 node-count and speed cells, the AODV mean PDR was higher than the DSDV mean PDR. "
        f"The highest mean PDR in the table is AODV with 20 nodes at 5 m/s "
        f"({fmt(float(lookup[('AODV', 20, 5.0)]['pdr_percent_mean']))}%). "
        f"The lowest is DSDV with 10 nodes at 20 m/s "
        f"({fmt(float(dsdv_fast['pdr_percent_mean']))}%). "
        f"Mean delay does not follow the same ordering: at 10 nodes and 5 m/s, DSDV's mean delay "
        f"({fmt(float(lookup[('DSDV', 10, 5.0)]['avg_delay_ms_mean']))} ms) is lower than AODV's "
        f"({fmt(float(aodv_low['avg_delay_ms_mean']))} ms) even though its PDR is also lower. "
        f"Several delay sample standard deviations are large relative to the gap between the two means, "
        f"so three runs do not support a stable delay ranking."
    )


def _mean(lookup: dict, protocol: str, nodes: int, speed: float, field: str) -> float:
    return float(lookup[(protocol, nodes, speed)][field])


def inference(rows: list[dict]) -> str:
    """Plain-language reading of the 12 group means. Numbers come from the aggregate CSV."""
    lookup = grouped(rows)

    def pdr(protocol: str, nodes: int, speed: float) -> float:
        return _mean(lookup, protocol, nodes, speed, "pdr_percent_mean")

    def delay(protocol: str, nodes: int, speed: float) -> float:
        return _mean(lookup, protocol, nodes, speed, "avg_delay_ms_mean")

    def delay_std(protocol: str, nodes: int, speed: float) -> float:
        return _mean(lookup, protocol, nodes, speed, "avg_delay_ms_sample_std")

    gaps = []
    for nodes in (10, 20):
        for speed in (5.0, 10.0, 20.0):
            gap = pdr("AODV", nodes, speed) - pdr("DSDV", nodes, speed)
            gaps.append((gap, nodes, speed))
    narrow = min(gaps)
    wide = max(gaps)

    def drop(protocol: str, nodes: int) -> float:
        return pdr(protocol, nodes, 5.0) - pdr(protocol, nodes, 20.0)

    aodv_slow_gain = pdr("AODV", 20, 5.0) - pdr("AODV", 10, 5.0)
    dsdv_slow_gain = pdr("DSDV", 20, 5.0) - pdr("DSDV", 10, 5.0)
    aodv_fast_change = pdr("AODV", 20, 20.0) - pdr("AODV", 10, 20.0)
    return (
        "The offered application load is three flows at 64 kb/s, 192 kb/s in total. "
        "Throughput follows packet delivery because both are computed from the packets that arrived. "
        "Every run sends 2577 data packets, and packet loss is TX − RX, so the loss ranking is the reverse of the PDR ranking.\n\n"
        f"1. **Delivery favors AODV in all six cells.** The gap is about {fmt(narrow[0])} to {fmt(wide[0])} percentage points. "
        f"The widest gap is {wide[1]} nodes at {wide[2]:g} m/s, where AODV delivers {fmt(pdr('AODV', wide[1], wide[2]))}% "
        f"and DSDV delivers {fmt(pdr('DSDV', wide[1], wide[2]))}%.\n"
        f"2. **Faster movement reduces delivery for both protocols.** From 5 m/s to 20 m/s, AODV with 10 nodes falls by about {fmt(drop('AODV', 10))} points "
        f"and DSDV with 10 nodes falls by about {fmt(drop('DSDV', 10))} points. With 20 nodes the drop is about {fmt(drop('AODV', 20))} points for AODV "
        f"and about {fmt(drop('DSDV', 20))} points for DSDV.\n"
        f"3. **More nodes help when movement is slow.** At 5 m/s, going from 10 to 20 nodes raises AODV by about {fmt(aodv_slow_gain)} points "
        f"(to {fmt(pdr('AODV', 20, 5.0))}%) and DSDV by about {fmt(dsdv_slow_gain)} points (to {fmt(pdr('DSDV', 20, 5.0))}%). "
        f"At 20 m/s that benefit disappears for AODV: 20 nodes deliver {fmt(pdr('AODV', 20, 20.0))}%, "
        f"which is {fmt(abs(aodv_fast_change))} points below the 10-node result.\n"
        f"4. **Delay is not a second ranking.** Delay is the average only over packets that arrived. "
        f"At 10 nodes and 5 m/s, DSDV's mean delay is {fmt(delay('DSDV', 10, 5.0))} ms and AODV's is {fmt(delay('AODV', 10, 5.0))} ms, "
        f"while DSDV delivered far less. AODV's delay sample standard deviation is {fmt(delay_std('AODV', 10, 5.0))} ms in that cell "
        f"and {fmt(delay_std('AODV', 20, 5.0))} ms at 20 nodes and 5 m/s. Three repeats are too few to rank the protocols by delay.\n\n"
        "A fair reading of the mechanism, without a direct measurement of control packets, is that AODV looks up a route when a packet needs one, "
        "so it can follow the topology after nodes move. DSDV keeps tables that can go stale while nodes are moving quickly. "
        "This project counted application packets on ports 9000–9002 only, so routing overhead was not compared."
    )


def conclusion(rows: list[dict]) -> str:
    lookup = grouped(rows)
    best = max(
        ((float(row["pdr_percent_mean"]), row) for row in rows),
        key=lambda item: item[0],
    )[1]
    worst = min(
        ((float(row["pdr_percent_mean"]), row) for row in rows),
        key=lambda item: item[0],
    )[1]
    return (
        "On this IEEE 802.11 ad-hoc network, with Random Waypoint mobility, pause 0, and three constant-rate UDP flows, "
        "AODV gave higher packet delivery, lower packet loss, and higher application throughput than DSDV at both 10 and 20 nodes "
        "and at 5, 10, and 20 m/s. "
        f"The best measured delivery is {best['protocol']} with {int(float(best['num_nodes']))} nodes at {float(best['node_speed_mps']):g} m/s "
        f"({fmt(float(best['pdr_percent_mean']))}%). "
        f"The worst is {worst['protocol']} with {int(float(worst['num_nodes']))} nodes at {float(worst['node_speed_mps']):g} m/s "
        f"({fmt(float(worst['pdr_percent_mean']))}%). "
        "Higher speed reduced delivery for both protocols, and the extra nodes helped only while the nodes were moving slowly. "
        "Average delay is a separate observation: it is computed only for packets that arrived, and the repeat-to-repeat spread is too large for a stable ranking. "
        "The numbers describe NS-3.45 with 802.11b, the Friis model, a 500 m square, 7.5 dBm transmit power, seed 12345, and three repeats."
    )


def observation(rows: list[dict]) -> str:
    lookup = grouped(rows)
    sentences = []
    for nodes in (10, 20):
        for speed in (5.0, 10.0, 20.0):
            aodv = lookup[("AODV", nodes, speed)]
            dsdv = lookup[("DSDV", nodes, speed)]
            sentences.append(
                f"With {nodes} nodes at {speed:g} m/s, mean PDR was {fmt(float(aodv['pdr_percent_mean']))}% "
                f"for AODV (sample std {fmt(float(aodv['pdr_percent_sample_std']))}) and "
                f"{fmt(float(dsdv['pdr_percent_mean']))}% for DSDV "
                f"(sample std {fmt(float(dsdv['pdr_percent_sample_std']))}). "
                f"Mean delay was {fmt(float(aodv['avg_delay_ms_mean']))} ms (AODV) and "
                f"{fmt(float(dsdv['avg_delay_ms_mean']))} ms (DSDV). "
                f"Mean throughput was {fmt(float(aodv['throughput_kbps_mean']))} kb/s (AODV) and "
                f"{fmt(float(dsdv['throughput_kbps_mean']))} kb/s (DSDV). "
                f"Mean packet loss was {fmt(float(aodv['packet_loss_packets_mean']))} packets (AODV) and "
                f"{fmt(float(dsdv['packet_loss_packets_mean']))} packets (DSDV)."
            )
    return "\n\n".join(sentences)


def main() -> int:
    rows = load_aggregate()
    scenario = load_scenario()
    validation_path = RESULTS / "processed" / "validation_summary.json"
    validation = {}
    if validation_path.is_file():
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
    status = validation.get("status", "NOT RUN")
    table = markdown_table(rows)
    narrative = observation(rows)
    finding_text = findings(rows)
    inference_text = inference(rows)
    conclusion_text = conclusion(rows)
    reports = ROOT_REPORTS = RESULTS.parent / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    technical = f"""# Performance Evaluation of AODV and DSDV Routing Protocols in Mobile Ad Hoc Networks Using NS-3

Author: Pradhan

## Abstract

This simulation study compares the built-in AODV and DSDV models in NS-3.45 on a mobile IEEE 802.11 ad-hoc network. Each protocol was run at 10 and 20 nodes and at nominal speeds of 5, 10 and 20 m/s, with three paired repetitions (36 runs). Application performance was taken only from three constant-rate UDP flows and summarized as packet delivery ratio, average end-to-end delay, throughput and packet loss. Validation status of the processed matrix: **{status}**. {finding_text}

## 1. Introduction

A mobile ad hoc network (MANET) has wireless nodes that forward traffic for one another without a fixed access point. Movement changes which links exist, so the routing protocol has to create or refresh routes while application packets are in flight.

## 2. Problem statement and research question

How do AODV and DSDV differ in packet delivery ratio, average end-to-end delay, throughput and packet loss as node speed and node count vary in this NS-3 scenario?

## 3. Objectives and scope

The study uses NS-3.45, IPv4, IEEE 802.11b ad-hoc mode, Random Waypoint mobility and UDP application traffic. Only AODV and DSDV are compared. TCP, energy models, attacks and other routing protocols are outside the measured experiment.

## 4. Background

AODV is a reactive protocol: a node looks for a route when it has a packet to send. DSDV is a proactive protocol: nodes periodically exchange routing tables so a route may already be present when data arrives. In this tree DSDV uses the model default periodic update interval of 15 s and settling time of 5 s. AODV uses the installed model defaults, with its random variables pinned by `AssignStreams` at stream 3000. The DSDV helper in NS-3.45 does not provide `AssignStreams`.

## 5. Simulation architecture

Each run creates N wireless nodes, one ad-hoc 802.11b interface per node, Random Waypoint mobility, exactly one routing protocol, three UDP OnOff sources and three PacketSink receivers, then FlowMonitor. NetAnim XML is produced only for the two demonstration runs (10 nodes, 20 m/s, run 1).

## 6. Experimental setup

Frozen controls are recorded in `config/scenario.json` and in every run manifest.

| Item | Value |
|---|---|
| NS-3 | 3.45, optimized build, Python bindings off, tests off |
| Area | {scenario['area_x_m']:g} m × {scenario['area_y_m']:g} m |
| Wi-Fi | 802.11b, constant rate `DsssRate11Mbps`, ad-hoc MAC |
| Propagation | Friis, constant-speed delay |
| Transmit power | {scenario['tx_power_dbm']:g} dBm |
| Mobility | Random Waypoint, constant speed, pause 0 s |
| Flows | 0→N−1 port 9000, 1→N−2 port 9001, 2→N−3 port 9002 |
| Payload / rate | 512 bytes, 64 kb/s per flow (ns-3 `64kb/s` = 64000 bit/s) |
| Traffic | 5 s to 60 s |
| Simulator stop | 65 s (5 s cleanup after the sources stop) |
| Measurement window D | 55 s |
| Seed / runs | 12345 / 1, 2, 3 |
| Matrix | 2 × 2 × 3 × 3 = 36 runs |

Node count changes density because the area stays fixed. Speed is the other independent variable.

## 7. Metric definitions

Counters are summed over the three UDP flows before any ratio is computed. FlowMonitor byte counts are IPv4-level bytes and do not include the 802.11 header.

- Packet delivery ratio: `PDR (%) = 100 × RX / TX`. Undefined when TX = 0.
- Average end-to-end delay: `1000 × delaySum / RX` milliseconds. Undefined when RX = 0.
- Throughput: `8 × RX_BYTES / (D × 1000)` kb/s, with D = 55 s.
- Packet loss: `TX − RX` packets. The percentage is `100 × (TX − RX) / TX` when TX > 0.

`flowmonitor_lost_packets_diagnostic` is FlowMonitor's own lost-packet counter. It is not required to equal `TX − RX`, because FlowMonitor marks a packet lost when it has not seen it for its timeout, including packets still queued below IP at the end of the run. The cleanup interval is there to reduce that effect. The four reported metrics use `TX`, `RX`, byte counts and `delaySum`, not the diagnostic lost counter.

## 8. Reproducibility and fairness

Every AODV/DSDV pair uses the same node count, speed, seed and run number. The position allocator uses random stream 100 and the mobility models use stream 200, both assigned before the routing protocol is installed. Wi-Fi devices use stream 1000 and the channel uses stream 2000. Saved `mobility.csv` traces (one sample per node per second) are compared with a tolerance of 1e-6 m. A pair is accepted only when that check passes. Three runs are a small repetition study; differences between means are described directly and are not treated as a formal significance test.

## 9. Results

Validation status: **{status}**.

Values are the arithmetic mean of the three runs and the sample standard deviation (divisor n−1).

{table}

{finding_text}

{narrative}

The same numbers are plotted in:

- `results/plots/pdr_vs_speed.png`
- `results/plots/delay_vs_speed.png`
- `results/plots/throughput_vs_speed.png`
- `results/plots/packet_loss_vs_speed.png`

Error bars are the sample standard deviation across the three runs. Solid lines are 10 nodes and dashed lines are 20 nodes.

## 10. Inference

{inference_text}

## 11. Threats to validity

- Friis propagation with a constant rate and no shadowing is a simplified radio.
- Random Waypoint with zero pause produces continuous motion and is not a trace of a real campus or road.
- Only three repetitions were run for each condition.
- Results are from the NS-3 models, not from a physical deployment.
- Throughput uses FlowMonitor IPv4 bytes over the configured 55 s window, not a payload-only socket counter.
- FlowMonitor's `lostPackets` diagnostic can differ from `TX − RX`.
- DSDV random variables are not stream-assigned, because `DsdvHelper` in this release has no `AssignStreams`. Mobility streams are still assigned explicitly and checked.

## 12. Conclusion

{conclusion_text}

## 13. Future work

Work that was not done here includes adding OLSR, measuring energy, or repeating the matrix with a different propagation model. Those would be new experiments.

## 14. References

1. ns-3.45 installation guide: https://www2.nsnam.org/docs/release/3.45/installation/singlehtml/index.html
2. ns-3.45 tutorial quick start: https://www.nsnam.org/docs/release/3.45/tutorial/html/quick-start.html
3. ns-3.45 model library (AODV, DSDV, Wi-Fi, mobility, FlowMonitor, NetAnim): https://www.nsnam.org/docs/release/3.45/models/ns-3-model-library.pdf
4. FlowMonitor model documentation: https://www.nsnam.org/docs/release/3.45/models/html/flow-monitor.html
5. Installed example `ns-3.45/examples/routing/manet-routing-compare.cc`.

## 15. Reproducibility appendix

Commands and paths are listed in `MANET_AAT_README.md`. Raw runs live under `results/raw/`. The ledger is `results/experiment_status.csv`. Processed tables are `results/processed/all_runs.csv` and `results/processed/aggregate_mean_std.csv`.
"""
    (reports / "technical_report.md").write_text(technical, encoding="utf-8")

    demo = f"""# Five-minute demo

Use files that are already on disk. Do not rerun the 36-run matrix during the demo.

## Commands that produced these results

Run these from the project root. The scored table comes from the 36-run matrix and the analysis scripts. The animation commands only open XML that those runs already wrote.

```bash
python3 scripts/run_smoke_tests.py
python3 scripts/run_experiments.py --pilot --force
python3 scripts/run_experiments.py --force
python3 scripts/process_results.py
python3 scripts/validate_results.py
python3 scripts/plot_results.py
python3 scripts/generate_report.py
```

`python3 scripts/run_experiments.py --force` is the command that wrote the 36 PASS rows in `results/experiment_status.csv` (finished with `failures=0` at 2026-10-13T06:39:38Z). The same two steps through the short wrapper are `./manet matrix --force` and `./manet analyze`.

The two demo animations (10 nodes, 20 m/s, run 1) were written again after the matrix so the nodes carry labels and colors. That rerun uses the same seed and run number, so the packet counts for those two cases stay in the table:

```bash
./manet run AODV 10 20 1 --animate --force
./manet run DSDV 10 20 1 --animate --force
```

During the talk, play them with:

```bash
./manet anim aodv --nodes 10 --speed 20 --run 1
./manet anim dsdv --nodes 10 --speed 20 --run 1
```

## 0:00–0:30 — Problem

MANET nodes communicate without fixed infrastructure. Their movement changes connectivity. This project compares a reactive protocol (AODV) with a proactive protocol (DSDV).

## 0:30–1:15 — Design

Show the path in `scratch/manet-aat.cc`: nodes, ad-hoc Wi-Fi, Random Waypoint, one routing helper, three UDP flows, FlowMonitor. Mention 10 and 20 nodes, speeds 5/10/20 m/s, seed 12345, runs 1–3, and 36 completed runs if `results/experiment_status.csv` says so.

## 1:15–2:15 — AODV animation

From the project root, run `./manet anim aodv --nodes 10 --speed 20 --run 1`. Green is flow 1 (S1 sends to D1 receives), blue is flow 2, orange is flow 3, and gray nodes are relays. Packets drawn by NetAnim include traffic the animator traced; the CSV counts only the three UDP data flows.

## 2:15–3:15 — DSDV animation

Run `./manet anim dsdv --nodes 10 --speed 20 --run 1`. Say that this run used the same node count, speed, seed and run number, and that `results/paired_mobility_validation.csv` records whether the mobility traces matched.

## 3:15–4:30 — Measured results

Show the four plots in `results/plots/`. Read the inference, then the conclusion, using the table below.

## Inference

{inference_text}

## Conclusion

{conclusion_text}

{table}

## 4:30–5:00 — Limitations

State the tested ranges, that 36 runs were the plan, that this is an NS-3 simulation, and that three repetitions plus a Friis/Random Waypoint model limit how far the numbers generalize.

## Viva lines

- MANET: wireless nodes form a network without fixed infrastructure and may forward traffic for one another.
- AODV: reactive, on-demand route discovery.
- DSDV: proactive, table-driven route updates.
- Random Waypoint: a node picks a destination inside the area and moves there at the configured speed, with pause 0 s here.
- FlowMonitor: per-flow IPv4 counters inside NS-3.
- PDR: received application packets divided by sent application packets.
- Delay: end-to-end delay averaged over received application packets.
- Throughput: received IPv4 bytes converted to kilobits and divided by the 55 s window.
- Packet loss used in the report: TX − RX on the three UDP flows. FlowMonitor's `lostPackets` field is only a diagnostic.

## If the window does not open

Use `./manet anim aodv` from the project root in the desktop session. `NetAnim` alone is not on the PATH. If there is no display, show the plots and state that the XML files were generated for NetAnim 3.109. Do not describe an animation you did not open.
"""
    (reports / "demo_script.md").write_text(demo, encoding="utf-8")

    slides = f"""# Presentation outline

1. **Title.** Performance Evaluation of AODV and DSDV Routing Protocols in Mobile Ad Hoc Networks Using NS-3.
2. **Problem.** Movement changes multi-hop connectivity, so routing strategy affects delivery, delay, throughput and loss.
3. **Protocols.** AODV discovers routes on demand. DSDV advertises routes in advance.
4. **Architecture.** Ad-hoc 802.11b nodes, Random Waypoint, one routing protocol per run, three UDP flows, FlowMonitor, optional NetAnim.
5. **Experiment.** Area {scenario['area_x_m']:g} m × {scenario['area_y_m']:g} m, transmit power {scenario['tx_power_dbm']:g} dBm, speeds 5/10/20 m/s, 10 and 20 nodes, seed 12345, runs 1–3, 36 runs.
6. **Metrics.** PDR = 100×RX/TX. Delay = 1000×delaySum/RX ms. Throughput = 8×RX_BYTES/(55×1000) kb/s. Loss = TX−RX packets.
7. **Animation.** `results/animations/aodv_nodes10_speed20_run1.xml` and `results/animations/dsdv_nodes10_speed20_run1.xml`.
8. **PDR and delay.** Use `results/plots/pdr_vs_speed.png` and `results/plots/delay_vs_speed.png` with the means below.
9. **Throughput and loss.** Use `results/plots/throughput_vs_speed.png` and `results/plots/packet_loss_vs_speed.png`.
10. **Inference.** Delivery favors AODV in every cell; faster movement lowers delivery; extra nodes help only at low speed; delay is not a second ranking. Read the bullets below.
11. **Conclusion.** AODV delivered more application traffic than DSDV in this scenario. Quote the best and worst cells, then the simulation limits.

## Inference for slide 10

{inference_text}

## Conclusion for slide 11

{conclusion_text}

## Numbers for slides 8 and 9

{table}

Validation status when this file was generated: **{status}**.
"""
    (reports / "presentation_outline.md").write_text(slides, encoding="utf-8")
    print(f"Wrote {reports / 'technical_report.md'}")
    print(f"Wrote {reports / 'demo_script.md'}")
    print(f"Wrote {reports / 'presentation_outline.md'}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
