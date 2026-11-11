# End to End Project Documentation

## Performance Evaluation of AODV and DSDV Routing Protocols in Mobile Ad Hoc Networks Using NS-3

## 1. Project at a glance

This project is a controlled simulation study of two Mobile Ad Hoc Network (MANET) routing protocols: Ad hoc On-Demand Distance Vector (AODV) and Destination-Sequenced Distance Vector (DSDV). It uses NS-3.45 to measure how each protocol behaves when the number of mobile nodes and their movement speed change.

The study completed and validated **36 simulations**: 2 routing protocols × 2 node counts × 3 speeds × 3 repetitions. Under this exact simulated environment, AODV achieved higher mean packet delivery ratio (PDR) and throughput and lower application packet loss in every one of the six node-count/speed comparisons. Delay did not show a stable protocol ranking because it is measured only for packets that arrive and varied substantially between repetitions.

This conclusion applies only to the tested NS-3 configuration. It is not a claim that AODV is universally better than DSDV.

## 2. Why this problem matters

A MANET is a temporary wireless network formed by mobile devices without a fixed router, access point, or central controller. Each node can forward packets for other nodes. As nodes move, a path that existed moments earlier can disappear, so the network needs a routing protocol that can find or maintain a usable multi-hop route.

The project addresses this question:

> How do AODV and DSDV differ in packet delivery ratio, end-to-end delay, throughput, and packet loss when node count and movement speed vary in the same mobile wireless NS-3 scenario?

The independent variables are routing protocol, number of nodes, and node speed. The measured outputs are PDR, average end-to-end delay, throughput, and packet loss.

## 3. Routing concepts

### AODV

AODV is a **reactive** routing protocol. A node starts route discovery when it needs a route to send traffic. It uses route-request and route-reply messages to find routes and sequence numbers to prefer fresh route information. This can reduce unnecessary route-maintenance work when traffic is sparse, but route discovery can add delay when a path is first needed or after it breaks.

### DSDV

DSDV is a **proactive** routing protocol. Nodes maintain routing tables and periodically exchange updates, so a route may already be present when application traffic begins. Sequence numbers help avoid routing loops and identify newer information. Periodic tables can become outdated between updates when topology changes rapidly, while maintaining them also creates control activity even when no user data is being sent.

The project does not directly count routing-control overhead. It compares only the delivery performance of the three configured UDP application flows.

## 4. What was implemented

The implementation is not a modification of NS-3's stock MANET example. The project adds a new scratch simulation program and a reproducible Python workflow around the NS-3.45 distribution.

| Component | Location | Responsibility |
|---|---|---|
| Simulation model | `ns-3.45/scratch/manet-aat.cc` | Creates the wireless MANET, installs one routing protocol, generates traffic, collects FlowMonitor data, and writes per-run evidence. |
| Frozen configuration | `config/scenario.json` | Stores shared controls: 500 m × 500 m area, 7.5 dBm transmit power, zero pause, and master seed 12345. |
| Experiment library | `scripts/experiment_lib.py` | Defines the valid matrix and reusable run/output helpers. |
| Matrix runner | `scripts/run_experiments.py` | Executes the four pilot cases or all 36 final cases and records a status ledger. |
| Result processor | `scripts/process_results.py` | Builds run-level and aggregate CSV files and tests paired mobility equality. |
| Validator | `scripts/validate_results.py` | Checks file contracts, FlowMonitor consistency, formulas, matrix completeness, animations, and duplicates. |
| Plotter | `scripts/plot_results.py` | Produces PDR, delay, throughput, and loss graphs with sample-standard-deviation error bars. |
| Report generator | `scripts/generate_report.py` | Rebuilds the existing technical report from processed evidence. |
| Convenience command | `manet` and `scripts/manet.py` | Provides short commands for build, run, matrix, analysis, and NetAnim. |

## 5. Simulation architecture

```text
Random Waypoint mobile nodes
        ↓
IEEE 802.11b ad-hoc Wi-Fi with Friis propagation
        ↓
IPv4 stack with exactly one protocol: AODV or DSDV
        ↓
Three constant-rate UDP source/sink pairs
        ↓
FlowMonitor, mobility trace, optional NetAnim XML
        ↓
Per-run CSV/XML/JSON evidence
        ↓
Aggregation, validation, plots, and report
```

For every run, the program creates `N` nodes, installs one 802.11b ad-hoc interface on each node, assigns IPv4 addresses on `10.1.1.0/24`, installs either AODV or DSDV, and starts three UDP flows. FlowMonitor observes IP-level flow statistics. The program selects only the expected UDP flows on destination ports 9000, 9001, and 9002 before calculating metrics.

## 6. Experimental design

### 6.1 Fixed controls

| Parameter | Value |
|---|---|
| Simulator | NS-3.45, optimized build |
| Network type | IPv4 MANET |
| Radio | IEEE 802.11b ad-hoc mode |
| PHY data/control rate | `DsssRate11Mbps` constant rate |
| Propagation | Friis propagation loss and constant-speed propagation delay |
| Area | 500 m × 500 m |
| Transmit power | 7.5 dBm |
| Mobility model | Random Waypoint |
| Pause time | 0 s |
| Traffic | Three constant-bit-rate UDP flows |
| Payload | 512 bytes per packet |
| Rate per flow | 64 kb/s; total offered load 192 kb/s |
| Application interval | 5 s to 60 s |
| Simulation stop | 65 s, providing 5 s cleanup after traffic stops |
| Measurement duration | 55 s |
| RNG master seed | 12345 |

### 6.2 Variables and matrix

| Variable | Values |
|---|---|
| Routing protocol | AODV, DSDV |
| Number of nodes | 10, 20 |
| Node speed | 5, 10, 20 m/s |
| Repetitions | Run numbers 1, 2, 3 |

Therefore the experiment count is `2 × 2 × 3 × 3 = 36` runs.

### 6.3 Application flows

For each node count `N`, the three sources are nodes 0, 1, and 2. Their destinations are nodes `N−1`, `N−2`, and `N−3`.

| Flow | Source | Destination | UDP destination port |
|---|---:|---:|---:|
| F1 | 0 | N−1 | 9000 |
| F2 | 1 | N−2 | 9001 |
| F3 | 2 | N−3 | 9002 |

Using the same flow pattern for every configuration makes the protocol comparison focused on the routing choice rather than on a different workload.

## 7. Measurement model

The project sums counters across the three selected application flows first, then calculates a metric. This avoids giving disproportionate influence to a small individual flow.

| Metric | Formula | Meaning |
|---|---|---|
| Packet delivery ratio | `100 × RX / TX` | Percentage of application packets that reached a receiver. |
| Average end-to-end delay | `1000 × delaySum / RX` ms | Mean delivery delay of packets that arrived. |
| Throughput | `8 × RX_BYTES / (55 × 1000)` kb/s | Received IP-layer rate over the fixed 55-second application interval. |
| Packet loss | `TX − RX` | Packets sent by the application but not received. |

`TX`, `RX`, `RX_BYTES`, and `delaySum` come from FlowMonitor after filtering for the three UDP application flows. FlowMonitor byte counts are IP-layer bytes, not pure 512-byte payload bytes and not 802.11-frame bytes.

The separate `flowmonitor_lost_packets_diagnostic` field is retained for diagnostics but is not the reported loss metric. FlowMonitor can label packets as lost when it has not seen them for its timeout, including packets still queued beneath IP at simulation end. The project avoids confusing that diagnostic with `TX − RX` and allows a five-second cleanup interval.

## 8. Fairness and reproducibility safeguards

The comparison uses the same node count, speed, seed, run number, radio settings, traffic pattern, and area for each AODV/DSDV pair. Only the routing protocol changes.

The simulation explicitly assigns random-number streams before routing is installed: position allocation uses stream 100, mobility stream 200, Wi-Fi devices stream 1000, channel stream 2000, and AODV stream 3000. NS-3.45's DSDV helper does not expose an equivalent `AssignStreams` method. To verify that the protocol choice nevertheless did not alter movement, the project writes positions for every node once per second to `mobility.csv` and compares matched AODV/DSDV traces with a tolerance of `1e-6 m`.

The final evidence shows **18 of 18 paired mobility comparisons passed**, with matched movement traces. The final validator also found 36 expected raw summaries, 12 aggregate groups with three runs each, both required animation XML files, valid metric ranges, and zero problems.

## 9. Output and evidence trail

Each final run is stored at a deterministic path similar to:

```text
results/raw/protocol_aodv/nodes_10/speed_5/run_1/
```

| File | Evidence it contains |
|---|---|
| `run.log` | Configuration banner, simulator output, metrics, warnings, and execution details. |
| `summary.csv` | One machine-readable row containing input values and final metrics. |
| `manifest.json` | Protocol, seed/run, command, traffic, radio configuration, timestamps, files, and RNG streams. |
| `flows.csv` | All FlowMonitor flows and a flag identifying the three selected application flows. |
| `flowmon.xml` | Raw FlowMonitor statistics. |
| `mobility.csv` | Node coordinates sampled once per second. |
| `animation.xml` | NetAnim data for designated demonstration cases only. |

Important final files are:

- `results/experiment_status.csv` — ledger for all 36 simulations; all entries are `PASS`.
- `results/paired_mobility_validation.csv` — 18 paired-trace checks; all entries are `PASS`.
- `results/processed/all_runs.csv` — validated data for all individual runs.
- `results/processed/aggregate_mean_std.csv` — mean and sample standard deviation for the 12 protocol/node/speed groups.
- `results/processed/validation_summary.json` — reports `checked_runs: 36`, `problem_count: 0`, `status: PASS`.
- `results/plots/` — the four final plots in PNG and SVG formats.

## 10. Result summary

Values below are mean ± sample standard deviation across three runs.

| Protocol | Nodes | Speed (m/s) | PDR (%) | Delay (ms) | Throughput (kb/s) | Loss (packets) |
|---|---:|---:|---:|---:|---:|---:|
| AODV | 10 | 5 | 74.48 ± 4.77 | 57.01 ± 47.56 | 150.75 ± 9.66 | 657.67 ± 122.96 |
| DSDV | 10 | 5 | 49.75 ± 11.97 | 40.35 ± 9.78 | 100.70 ± 24.24 | 1295.00 ± 308.59 |
| AODV | 10 | 10 | 67.83 ± 22.42 | 128.67 ± 27.87 | 137.30 ± 45.38 | 829.00 ± 577.79 |
| DSDV | 10 | 10 | 46.14 ± 15.71 | 68.00 ± 3.13 | 93.39 ± 31.80 | 1388.00 ± 404.83 |
| AODV | 10 | 20 | 65.53 ± 10.97 | 109.30 ± 74.97 | 132.64 ± 22.20 | 888.33 ± 282.59 |
| DSDV | 10 | 20 | 28.22 ± 13.58 | 120.61 ± 23.45 | 57.13 ± 27.49 | 1849.67 ± 350.04 |
| AODV | 20 | 5 | 88.26 ± 9.54 | 71.39 ± 93.63 | 178.64 ± 19.31 | 302.67 ± 245.87 |
| DSDV | 20 | 5 | 65.96 ± 10.50 | 58.22 ± 17.81 | 133.50 ± 21.25 | 877.33 ± 270.52 |
| AODV | 20 | 10 | 69.80 ± 7.57 | 35.25 ± 29.73 | 141.28 ± 15.33 | 778.33 ± 195.12 |
| DSDV | 20 | 10 | 44.68 ± 8.75 | 54.73 ± 18.84 | 90.43 ± 17.71 | 1425.67 ± 225.53 |
| AODV | 20 | 20 | 55.98 ± 13.61 | 64.21 ± 85.00 | 113.31 ± 27.54 | 1134.33 ± 350.66 |
| DSDV | 20 | 20 | 41.09 ± 11.87 | 19.20 ± 22.27 | 83.18 ± 24.02 | 1518.00 ± 305.79 |

### Interpretation

1. AODV has higher mean PDR in all six matched cells. The largest PDR difference occurs at 10 nodes and 20 m/s: AODV delivers 65.53% while DSDV delivers 28.22%.
2. AODV has higher throughput and lower application packet loss in the same six cells. These values must move together because throughput is calculated from received bytes and loss is `TX − RX`.
3. Higher speed generally reduces delivery for both protocols. For example, at 10 nodes, AODV falls from 74.48% PDR at 5 m/s to 65.53% at 20 m/s; DSDV falls from 49.75% to 28.22%.
4. More nodes help at the low-speed 5 m/s condition because extra nodes can improve connectivity. The benefit is not consistent at high mobility. AODV at 20 nodes and 20 m/s records 55.98% PDR, below its 65.53% at 10 nodes and 20 m/s.
5. Mean delay should not be used to declare a general winner. DSDV has lower mean delay in some cases despite delivering fewer packets, and the delay standard deviations are large. Delay includes only successful deliveries, so it does not describe packets that were lost.

## 11. How to run or regenerate the work

The original campaign ran on Ubuntu. The repository now contains a Windows workspace copy, so the supplied commands are best treated as the project’s reproducible Linux commands unless an NS-3.45 Linux environment is available.

```bash
# from the project root
python3 scripts/run_smoke_tests.py
python3 scripts/run_experiments.py
python3 scripts/process_results.py
python3 scripts/validate_results.py
python3 scripts/plot_results.py
python3 scripts/generate_report.py
```

The `manet` launcher provides equivalent shorter commands:

```bash
./manet build
./manet run AODV 10 20 1 --animate
./manet matrix
./manet analyze
./manet anim aodv --speed 20 --run 1
```

Never overwrite raw evidence unintentionally. The runner requires `--force` before replacing an existing run summary.

## 12. Limitations and future work

This is a small, controlled simulation study. It uses a Friis radio model, fixed 802.11b rate, Random Waypoint movement with zero pause, three repetitions per condition, and a fixed offered load. It does not measure energy consumption, routing-control overhead, security behavior, TCP traffic, or real physical deployment performance. Three repetitions show variability but are too few for formal statistical significance claims.

Useful future work includes more repetitions, alternate propagation/fading models, other mobility models, an energy model, direct routing-overhead accounting, additional protocols such as OLSR, and wider traffic/load ranges. Each would be a new experiment and must not be presented as part of the completed result set.

## 13. Source basis

The simulation design follows NS-3.45 documentation and the local `examples/routing/manet-routing-compare.cc` example. The project presentation and report use the validated aggregate CSV rather than manually typed measurements. The AAT-ready chapter content and complete reference list are in `reports/AAT_REPORT_CONTENT.md`.
