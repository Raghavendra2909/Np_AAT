# Performance Evaluation of AODV and DSDV Routing Protocols in Mobile Ad Hoc Networks Using NS-3

Author: Pradhan

## Abstract

This simulation study compares the built-in AODV and DSDV models in NS-3.45 on a mobile IEEE 802.11 ad-hoc network. Each protocol was run at 10 and 20 nodes and at nominal speeds of 5, 10 and 20 m/s, with three paired repetitions (36 runs). Application performance was taken only from three constant-rate UDP flows and summarized as packet delivery ratio, average end-to-end delay, throughput and packet loss. Validation status of the processed matrix: **PASS**. In 6 of the 6 node-count and speed cells, the AODV mean PDR was higher than the DSDV mean PDR. The highest mean PDR in the table is AODV with 20 nodes at 5 m/s (88.26%). The lowest is DSDV with 10 nodes at 20 m/s (28.22%). Mean delay does not follow the same ordering: at 10 nodes and 5 m/s, DSDV's mean delay (40.35 ms) is lower than AODV's (57.01 ms) even though its PDR is also lower. Several delay sample standard deviations are large relative to the gap between the two means, so three runs do not support a stable delay ranking.

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
| Area | 500 m × 500 m |
| Wi-Fi | 802.11b, constant rate `DsssRate11Mbps`, ad-hoc MAC |
| Propagation | Friis, constant-speed delay |
| Transmit power | 7.5 dBm |
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

Validation status: **PASS**.

Values are the arithmetic mean of the three runs and the sample standard deviation (divisor n−1).

| Protocol | Nodes | Speed (m/s) | n | PDR (%) | Delay (ms) | Throughput (kb/s) | Loss (packets) |
|---|---:|---:|---:|---:|---:|---:|---:|
| AODV | 10 | 5 | 3 | 74.48 ± 4.77 | 57.01 ± 47.56 | 150.75 ± 9.66 | 657.67 ± 122.96 |
| DSDV | 10 | 5 | 3 | 49.75 ± 11.97 | 40.35 ± 9.78 | 100.70 ± 24.24 | 1295.00 ± 308.59 |
| AODV | 10 | 10 | 3 | 67.83 ± 22.42 | 128.67 ± 27.87 | 137.30 ± 45.38 | 829.00 ± 577.79 |
| DSDV | 10 | 10 | 3 | 46.14 ± 15.71 | 68.00 ± 3.13 | 93.39 ± 31.80 | 1388.00 ± 404.83 |
| AODV | 10 | 20 | 3 | 65.53 ± 10.97 | 109.30 ± 74.97 | 132.64 ± 22.20 | 888.33 ± 282.59 |
| DSDV | 10 | 20 | 3 | 28.22 ± 13.58 | 120.61 ± 23.45 | 57.13 ± 27.49 | 1849.67 ± 350.04 |
| AODV | 20 | 5 | 3 | 88.26 ± 9.54 | 71.39 ± 93.63 | 178.64 ± 19.31 | 302.67 ± 245.87 |
| DSDV | 20 | 5 | 3 | 65.96 ± 10.50 | 58.22 ± 17.81 | 133.50 ± 21.25 | 877.33 ± 270.52 |
| AODV | 20 | 10 | 3 | 69.80 ± 7.57 | 35.25 ± 29.73 | 141.28 ± 15.33 | 778.33 ± 195.12 |
| DSDV | 20 | 10 | 3 | 44.68 ± 8.75 | 54.73 ± 18.84 | 90.43 ± 17.71 | 1425.67 ± 225.53 |
| AODV | 20 | 20 | 3 | 55.98 ± 13.61 | 64.21 ± 85.00 | 113.31 ± 27.54 | 1134.33 ± 350.66 |
| DSDV | 20 | 20 | 3 | 41.09 ± 11.87 | 19.20 ± 22.27 | 83.18 ± 24.02 | 1518.00 ± 305.79 |

In 6 of the 6 node-count and speed cells, the AODV mean PDR was higher than the DSDV mean PDR. The highest mean PDR in the table is AODV with 20 nodes at 5 m/s (88.26%). The lowest is DSDV with 10 nodes at 20 m/s (28.22%). Mean delay does not follow the same ordering: at 10 nodes and 5 m/s, DSDV's mean delay (40.35 ms) is lower than AODV's (57.01 ms) even though its PDR is also lower. Several delay sample standard deviations are large relative to the gap between the two means, so three runs do not support a stable delay ranking.

With 10 nodes at 5 m/s, mean PDR was 74.48% for AODV (sample std 4.77) and 49.75% for DSDV (sample std 11.97). Mean delay was 57.01 ms (AODV) and 40.35 ms (DSDV). Mean throughput was 150.75 kb/s (AODV) and 100.70 kb/s (DSDV). Mean packet loss was 657.67 packets (AODV) and 1295.00 packets (DSDV).

With 10 nodes at 10 m/s, mean PDR was 67.83% for AODV (sample std 22.42) and 46.14% for DSDV (sample std 15.71). Mean delay was 128.67 ms (AODV) and 68.00 ms (DSDV). Mean throughput was 137.30 kb/s (AODV) and 93.39 kb/s (DSDV). Mean packet loss was 829.00 packets (AODV) and 1388.00 packets (DSDV).

With 10 nodes at 20 m/s, mean PDR was 65.53% for AODV (sample std 10.97) and 28.22% for DSDV (sample std 13.58). Mean delay was 109.30 ms (AODV) and 120.61 ms (DSDV). Mean throughput was 132.64 kb/s (AODV) and 57.13 kb/s (DSDV). Mean packet loss was 888.33 packets (AODV) and 1849.67 packets (DSDV).

With 20 nodes at 5 m/s, mean PDR was 88.26% for AODV (sample std 9.54) and 65.96% for DSDV (sample std 10.50). Mean delay was 71.39 ms (AODV) and 58.22 ms (DSDV). Mean throughput was 178.64 kb/s (AODV) and 133.50 kb/s (DSDV). Mean packet loss was 302.67 packets (AODV) and 877.33 packets (DSDV).

With 20 nodes at 10 m/s, mean PDR was 69.80% for AODV (sample std 7.57) and 44.68% for DSDV (sample std 8.75). Mean delay was 35.25 ms (AODV) and 54.73 ms (DSDV). Mean throughput was 141.28 kb/s (AODV) and 90.43 kb/s (DSDV). Mean packet loss was 778.33 packets (AODV) and 1425.67 packets (DSDV).

With 20 nodes at 20 m/s, mean PDR was 55.98% for AODV (sample std 13.61) and 41.09% for DSDV (sample std 11.87). Mean delay was 64.21 ms (AODV) and 19.20 ms (DSDV). Mean throughput was 113.31 kb/s (AODV) and 83.18 kb/s (DSDV). Mean packet loss was 1134.33 packets (AODV) and 1518.00 packets (DSDV).

The same numbers are plotted in:

- `results/plots/pdr_vs_speed.png`
- `results/plots/delay_vs_speed.png`
- `results/plots/throughput_vs_speed.png`
- `results/plots/packet_loss_vs_speed.png`

Error bars are the sample standard deviation across the three runs. Solid lines are 10 nodes and dashed lines are 20 nodes.

## 10. Inference

The offered application load is three flows at 64 kb/s, 192 kb/s in total. Throughput follows packet delivery because both are computed from the packets that arrived. Every run sends 2577 data packets, and packet loss is TX − RX, so the loss ranking is the reverse of the PDR ranking.

1. **Delivery favors AODV in all six cells.** The gap is about 14.89 to 37.30 percentage points. The widest gap is 10 nodes at 20 m/s, where AODV delivers 65.53% and DSDV delivers 28.22%.
2. **Faster movement reduces delivery for both protocols.** From 5 m/s to 20 m/s, AODV with 10 nodes falls by about 8.95 points and DSDV with 10 nodes falls by about 21.52 points. With 20 nodes the drop is about 32.27 points for AODV and about 24.86 points for DSDV.
3. **More nodes help when movement is slow.** At 5 m/s, going from 10 to 20 nodes raises AODV by about 13.78 points (to 88.26%) and DSDV by about 16.21 points (to 65.96%). At 20 m/s that benefit disappears for AODV: 20 nodes deliver 55.98%, which is 9.55 points below the 10-node result.
4. **Delay is not a second ranking.** Delay is the average only over packets that arrived. At 10 nodes and 5 m/s, DSDV's mean delay is 40.35 ms and AODV's is 57.01 ms, while DSDV delivered far less. AODV's delay sample standard deviation is 47.56 ms in that cell and 93.63 ms at 20 nodes and 5 m/s. Three repeats are too few to rank the protocols by delay.

A fair reading of the mechanism, without a direct measurement of control packets, is that AODV looks up a route when a packet needs one, so it can follow the topology after nodes move. DSDV keeps tables that can go stale while nodes are moving quickly. This project counted application packets on ports 9000–9002 only, so routing overhead was not compared.

## 11. Threats to validity

- Friis propagation with a constant rate and no shadowing is a simplified radio.
- Random Waypoint with zero pause produces continuous motion and is not a trace of a real campus or road.
- Only three repetitions were run for each condition.
- Results are from the NS-3 models, not from a physical deployment.
- Throughput uses FlowMonitor IPv4 bytes over the configured 55 s window, not a payload-only socket counter.
- FlowMonitor's `lostPackets` diagnostic can differ from `TX − RX`.
- DSDV random variables are not stream-assigned, because `DsdvHelper` in this release has no `AssignStreams`. Mobility streams are still assigned explicitly and checked.

## 12. Conclusion

On this IEEE 802.11 ad-hoc network, with Random Waypoint mobility, pause 0, and three constant-rate UDP flows, AODV gave higher packet delivery, lower packet loss, and higher application throughput than DSDV at both 10 and 20 nodes and at 5, 10, and 20 m/s. The best measured delivery is AODV with 20 nodes at 5 m/s (88.26%). The worst is DSDV with 10 nodes at 20 m/s (28.22%). Higher speed reduced delivery for both protocols, and the extra nodes helped only while the nodes were moving slowly. Average delay is a separate observation: it is computed only for packets that arrived, and the repeat-to-repeat spread is too large for a stable ranking. The numbers describe NS-3.45 with 802.11b, the Friis model, a 500 m square, 7.5 dBm transmit power, seed 12345, and three repeats.

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
