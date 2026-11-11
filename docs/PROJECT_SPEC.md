# Project Specification (Frozen)

## 1. Title

**Performance Evaluation of AODV and DSDV Routing Protocols in Mobile Ad Hoc Networks Using NS-3**

## 2. Problem statement

A Mobile Ad Hoc Network (MANET) contains wireless nodes that communicate without relying on fixed infrastructure. As nodes move, connectivity and viable multi-hop routes can change. This project compares two established routing strategies under controlled mobility and node-density conditions using discrete-event simulation.

## 3. Research question

How do AODV and DSDV differ in packet delivery ratio, average end-to-end delay, throughput, and packet loss as node mobility and node count vary in an NS-3 MANET?

## 4. Objectives

1. Build a mobile IEEE 802.11 ad-hoc wireless network in NS-3.45.
2. Use built-in AODV and DSDV routing implementations; do not implement routing algorithms from scratch.
3. Generate repeatable UDP application traffic.
4. Compare both protocols under the same scenario settings and matched mobility/random runs.
5. collect application-flow performance using FlowMonitor and transparent calculations.
6. Execute the full experiment matrix and preserve logs, raw data and run manifests.
7. Aggregate repetitions, visualize results and discuss limitations based on measured evidence.
8. Provide a NetAnim demonstration and a reproducible technical report.

## 5. Frozen scope

### Included

- NS-3.45; C++ simulation.
- IPv4 MANET.
- IEEE 802.11 ad-hoc Wi-Fi; no AP/infrastructure mode.
- Random Waypoint mobility.
- AODV and DSDV only.
- UDP application data flows.
- FlowMonitor statistics and XML export.
- Four mandatory metrics: packet delivery ratio (PDR), average end-to-end delay, throughput, packet loss.
- Experiment automation and 36 completed condition/repetition runs.
- Run logs, failure ledger, mobility traces, CSV/JSON metadata.
- Python processing/validation and four clear graphs.
- NetAnim XML for representative AODV and DSDV cases; GUI viewing instructions.
- Report, demo script and implementation/status notes.

### Excluded from core scope

- New/custom routing protocols or changing AODV/DSDV internals.
- OLSR, DSR or other protocols as scored comparisons.
- TCP, energy models, security attacks, ML, reinforcement learning, blockchain, real devices, mobile apps, web dashboards.
- Unsupported claims about real-world network performance.

## 6. Required experiment dimensions

- Routing protocol: `AODV`, `DSDV`.
- Node count: `10`, `20`.
- Requested nominal node speed: `5`, `10`, `20 m/s`.
- Paired run numbers: `1`, `2`, `3` with a fixed master seed and explicit independent stream assignment where supported.
- Total planned simulation runs: `2 × 2 × 3 × 3 = 36`.
- Keep the same physical area, Wi-Fi configuration, traffic flow definitions, packet size/rate, application window and simulation end time across node-count comparisons. Node count is the intended density variable.
- For every `(nodes, speed, run)` triple, AODV and DSDV must use matching random seed/run and, as verified by saved traces, matching node mobility trajectories.

## 7. Starting simulation parameters

These are implementation defaults to pilot-test and then freeze in a config/manifest. They must not be quietly changed between protocols.

| Parameter | Initial value |
|---|---:|
| Node counts | 10, 20 |
| Speeds | 5, 10, 20 m/s |
| Mobility | Random Waypoint; no pause (0 s) |
| Initial arena | 500 m × 500 m; validate connectivity and topology change during pilot |
| Wireless mode | IEEE 802.11 ad-hoc |
| Radio starting point | Adapt the official NS-3.45 MANET comparison example's 802.11b/Friis/constant-rate approach; inspect exact API and record chosen settings |
| App data flows | 3 unidirectional UDP flows for node counts >= 10 |
| Flow pairs | `0 -> N-1`, `1 -> N-2`, `2 -> N-3` |
| Destination ports | 9000, 9001, 9002 (one per flow) |
| Payload | 512 bytes per application packet |
| Data rate | 64 kb/s per flow, fixed On-time and zero Off-time, or an equivalent verified constant-rate UDP setup |
| Traffic start | 5 s |
| Traffic stop | 60 s |
| Simulation stop | 65 s, leaving a 5-second cleanup interval |
| Metric measurement duration | 55 s (traffic stop minus traffic start) |
| Master RNG seed | 12345; `run` numbers 1, 2, 3 |

The agent must run pilot simulations to check that the scenario creates real multi-hop/mobility behavior and produces application-flow receptions. It may adjust only the arena/radio settings if the pilot shows the starting combination is completely disconnected or effectively static/fully connected. Any adjustment must be documented and held constant across all comparisons. Do not tune settings to make a preferred protocol win.

## 8. Success criteria

- A single C++ simulation supports the two protocols and documented CLI parameters.
- AODV and DSDV smoke cases both build and run.
- Every planned condition has a visible ledger entry and complete raw output, or a clearly documented actual blocker/status.
- Every valid row's metrics trace back to application-flow packet counters/XML and uses documented formulas.
- The full 36-run matrix is completed before aggregate results are labeled final.
- The four required plots, animation XML, report and demo notes exist.
- No fabricated metrics; all claims are supported by output files.
