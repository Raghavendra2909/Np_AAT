# AAT Report Content

## Performance Evaluation of AODV and DSDV Routing Protocols in Mobile Ad Hoc Networks Using NS-3

This is report-ready content aligned with the supplied AAT report structure. Replace bracketed placeholders on the cover page. Insert the four validated figures from `../results/plots/` where marked. The report guideline asks for 20–25 pages, 1.5 or double spacing on A4, left margin 1.25 inches, right margin 1 inch, and top/bottom margins 0.75 inches. It also asks for at least 12 literature sources; the reference section below provides 15 sources, but the five user-supplied 2025–2026 entries still need their final DOI/URL checked before submission.

---

## Cover Page

**Alternate Assessment Report on Network Programming**

**Performance Evaluation of AODV and DSDV Routing Protocols in Mobile Ad Hoc Networks Using NS-3**

Submitted by:

- Pradhan Sagar K — 1BM23CS237
- Raghavendra Ashok Kumbar — 1BM23CS258
- Rohan B Shekar — 1BM23CS272
- Saketh Bharadwaj K H — 1BM23CS287

Department of Computer Science and Engineering  
B.M.S. College of Engineering  
Course: Network Programming — 23CS7PCNWP  
Faculty in charge: Prof. Surabhi S, Assistant Professor, Department of CSE  
Date of submission: [DD Month YYYY]

---

# Chapter 1 Abstract

Mobile Ad Hoc Networks (MANETs) allow wireless devices to communicate without fixed infrastructure, but node movement changes the available routes during communication. This project evaluates the performance of Ad hoc On-Demand Distance Vector (AODV) and Destination-Sequenced Distance Vector (DSDV) routing protocols using NS-3.45. AODV is reactive and finds routes when required, whereas DSDV is proactive and maintains routing tables through periodic updates. The simulation used IEEE 802.11b ad-hoc Wi-Fi, Random Waypoint mobility, a 500 m × 500 m field, and three constant-rate UDP flows. The study varied the protocol, node count (10 and 20), and node speed (5, 10, and 20 m/s), with three repetitions for each condition, producing 36 validated runs. Packet delivery ratio, average end-to-end delay, throughput, and packet loss were calculated from the three application flows. AODV achieved a higher mean packet delivery ratio and throughput, and lower application packet loss, in all six matched node-count/speed conditions. The highest mean PDR was 88.26% for AODV with 20 nodes at 5 m/s, while the lowest was 28.22% for DSDV with 10 nodes at 20 m/s. Delay did not give a stable ranking because it measures only successfully delivered packets and showed substantial variation across repetitions. The result is specific to the tested NS-3 configuration and does not establish a universal ranking of the protocols.

# Chapter 2 Objectives

The objectives of this work are:

1. To understand the routing challenge in infrastructure-free mobile ad hoc networks.
2. To implement a reproducible NS-3.45 simulation for AODV and DSDV under the same wireless, mobility, and traffic conditions.
3. To evaluate the effect of node count and node speed on routing performance.
4. To measure packet delivery ratio, average end-to-end delay, throughput, and packet loss from selected UDP application flows.
5. To verify comparison fairness by matching mobility traces for each AODV/DSDV pair.
6. To interpret results within the limits of a controlled simulation study.

# Chapter 3 Introduction

## 3.1 Mobile Ad Hoc Networks

A Mobile Ad Hoc Network is a set of wireless mobile devices that form a network without a fixed access point, wired backbone, or central controller. A node can act both as a host that sends or receives data and as a router that forwards data for other nodes. MANETs are useful when fixed infrastructure is unavailable or impractical, such as disaster recovery, military communication, temporary events, and remote field operations.

The main technical challenge is dynamic topology. Radio links appear and disappear as nodes move, so a path between a source and destination can fail while packets are in transit. Routing must react to path changes while using limited wireless bandwidth. A protocol can either maintain routes continuously or find them only when data needs to be sent. This study compares one protocol from each approach.

## 3.2 AODV and DSDV

AODV is a reactive protocol. When a source has no valid route, it starts route discovery by broadcasting a route request. A route reply establishes a path back to the source. Sequence numbers are used to identify fresh route information and prevent loops. Because AODV discovers routes on demand, it can respond after a link changes, but a route-discovery process can delay initial packets.

DSDV is a proactive distance-vector protocol. Each node maintains a table containing next-hop information for destinations and periodically distributes updates. Routes can therefore be available immediately when traffic starts. DSDV also uses destination sequence numbers to avoid loop formation and stale-route preference. In a fast-changing topology, however, a table may temporarily not reflect the newest connectivity between update events.

## 3.3 Problem context

The relative performance of AODV and DSDV depends on scenario choices such as density, mobility, traffic, propagation, and the metric selected. A result from one simulator setup cannot be directly generalized to all MANET deployments. This project therefore defines a clear and reproducible environment and compares only the two protocols under matched conditions.

# Chapter 4 Literature Review

MANET routing literature distinguishes proactive and reactive routing as different responses to dynamic topology. Perkins and Bhagwat introduced DSDV as a destination-sequenced distance-vector scheme that uses sequence numbers to avoid routing loops [6]. Perkins, Belding-Royer, and Das specified AODV as an on-demand protocol that discovers a route through route-request and route-reply processing [7].

Broch et al. showed early that comparative conclusions can change when mobility, traffic, and measurement assumptions change [8]. Das, Perkins, and Royer also compared on-demand routing approaches and reinforced the importance of using clearly defined scenarios and metrics [9]. These foundational works establish that a protocol comparison must control the environment rather than label one protocol universally superior.

Recent comparative studies continue to measure PDR, delay, throughput, packet loss, and routing overhead under varying density and mobility. Abdala [1] reviews AODV and DSDV in MANETs. Raji [2] compares routing protocols in MANETs. Sharma et al. [3] report an NS-3 comparison in a 5G-oriented MANET context. Suleiman, Zimbele, and Yahaya [4] compare AODV and DSDV under Random Waypoint mobility and report a trade-off between delivery-related measures and delay. Selim et al. [5] examine MANET routing under dynamic conditions.

Additional studies show that the outcome remains conditional. Kumar, Srivastava, and Gupta [10] compare AODV and DSDV delay behavior. A 2016 Procedia Computer Science study compares both protocols on PDR, throughput, delay, and routing overhead and reports better delivery-related performance for AODV in its scenario [11]. An IEEE study focused on density and routing overhead reports metric-specific differences rather than a single universal winner [12]. These findings motivate a controlled evaluation that reports both favorable and inconclusive outcomes.

The NS-3.45 model library and FlowMonitor documentation [13], [14] guide the simulator-specific implementation. The local NS-3 MANET comparison example [15] provides a release-compatible reference design for ad-hoc Wi-Fi, mobility, and routing helpers.

# Chapter 5 Research Gap

The literature contains many AODV/DSDV comparisons, but direct comparison is difficult when studies use different simulator versions, node densities, movement models, traffic patterns, radio assumptions, and metric definitions. Several reports present average values without demonstrating that the two protocols experienced identical node movement. Some works also mix application traffic with control traffic or interpret FlowMonitor loss counters without considering end-of-simulation queues.

This project narrows the gap to a reproducible NS-3.45 comparison that: (1) changes only the routing protocol within each matched pair, (2) records raw run artifacts, (3) filters metrics to three explicitly defined UDP application flows, (4) validates that paired AODV/DSDV mobility traces are identical, and (5) reports mean and sample standard deviation rather than only a single run.

# Chapter 6 Problem Statement

The problem is to determine how reactive AODV and proactive DSDV affect application-level packet delivery ratio, average end-to-end delay, throughput, and packet loss in the same NS-3.45 MANET scenario when node count and movement speed vary. The implementation must make the protocol comparison fair, retain reproducible evidence, and avoid conclusions beyond the tested environment.

**Research question:** How do AODV and DSDV differ in PDR, end-to-end delay, throughput, and packet loss for 10 and 20 mobile nodes moving at 5, 10, and 20 m/s under the same IEEE 802.11b ad-hoc NS-3 scenario?

# Chapter 7 Methodology and Implementation

## 7.1 Architecture

```text
N mobile nodes → 802.11b ad-hoc Wi-Fi → IPv4 with AODV or DSDV
       → three UDP OnOff sources and PacketSink receivers
       → FlowMonitor and mobility logger
       → CSV/XML/JSON artifacts → processing, validation, plots
```

The implementation is in `ns-3.45/scratch/manet-aat.cc`. It creates the nodes, installs Wi-Fi devices, assigns Random Waypoint mobility, installs exactly one routing helper, sets IPv4 addresses, creates three UDP flows, runs the simulator, and saves the evidence files. Python scripts automate the matrix, aggregation, validation, plotting, and report regeneration.

## 7.2 Experimental setup

| Item | Value |
|---|---|
| NS-3 version | 3.45, optimized build |
| Area | 500 m × 500 m |
| Wi-Fi | IEEE 802.11b, ad-hoc MAC, `DsssRate11Mbps` |
| Channel | Friis propagation loss; constant-speed propagation delay |
| Transmit power | 7.5 dBm |
| Mobility | Random Waypoint, constant speed, zero pause |
| Protocols | AODV and DSDV, one protocol per run |
| Nodes | 10 and 20 |
| Speeds | 5, 10, and 20 m/s |
| UDP flows | 0→N−1 port 9000; 1→N−2 port 9001; 2→N−3 port 9002 |
| Payload and rate | 512 bytes; 64 kb/s per flow |
| Traffic interval | 5 s to 60 s |
| Simulator stop | 65 s |
| Repetitions | Three runs per protocol/node/speed condition |
| Total simulations | 36 |

## 7.3 Proposed algorithm

1. Load frozen controls from `config/scenario.json`.
2. For each protocol, node count, speed, and run number, set the master seed and run index.
3. Create nodes and configure 802.11b ad-hoc Wi-Fi with the Friis channel.
4. Create Random Waypoint mobility with the selected constant speed and zero pause.
5. Install either AODV or DSDV, but never both in the same run.
6. Install three UDP source/sink pairs with the same payload, rate, ports, and start/stop times.
7. Sample node positions every second; install FlowMonitor; optionally enable NetAnim for demonstration runs.
8. Run until 65 seconds, then serialize FlowMonitor XML.
9. Select only the expected UDP flows using source address, destination address, protocol number 17, and destination port.
10. Compute metrics, save the run CSV/manifest/trace files, and mark the run valid only when the selected-flow and counter checks pass.
11. Aggregate the three repetitions per condition, validate all output contracts and formula calculations, then generate plots.

## 7.4 Mathematical model

Let `TX` be total transmitted packets, `RX` be total received packets, `RX_BYTES` be received IP-layer bytes, `delaySum` be the total delay of received packets, and `D = 55 s` be the fixed traffic measurement duration.

`PDR (%) = 100 × RX / TX`

`Average end-to-end delay (ms) = 1000 × delaySum / RX`

`Throughput (kb/s) = 8 × RX_BYTES / (D × 1000)`

`Packet loss (packets) = TX − RX`

The reported value for each condition is the arithmetic mean of its three runs. The plotted uncertainty is the sample standard deviation, calculated with divisor `n − 1`.

## 7.5 Fairness and validation

Every AODV/DSDV pair uses the same node count, speed, seed, run number, radio configuration, traffic flows, and area. The program assigns reproducible random-number streams to position allocation, mobility, Wi-Fi devices, channel, and AODV. DSDV does not expose `AssignStreams` in NS-3.45, so the study verifies the important common input directly: saved AODV and DSDV mobility traces are compared once per second by node ID and coordinate.

The validation result is `PASS`: 36 runs were checked, no issues were found, all 18 paired mobility traces matched, 12 aggregate groups were created, and both required NetAnim XML files were present. The validation script recomputes metrics from FlowMonitor XML and confirms the expected ports 9000, 9001, and 9002.

# Chapter 8 Performance Evaluation

The performance evaluation compares the two protocols across the four metrics. PDR measures successful packet delivery. Throughput measures received IP-layer data rate. Packet loss counts packets transmitted by the application but not received. Average end-to-end delay measures only the packets that arrived successfully.

The main strength of the evaluation is that it uses three repetitions and reports mean ± sample standard deviation. The error bars show that repeat-to-repeat variation, especially for delay, is material. Therefore differences are described as measured patterns, not as formal statistical significance.

**Insert Figure 8.1 here:** `../results/plots/pdr_vs_speed.png`  
**Insert Figure 8.2 here:** `../results/plots/delay_vs_speed.png`  
**Insert Figure 8.3 here:** `../results/plots/throughput_vs_speed.png`  
**Insert Figure 8.4 here:** `../results/plots/packet_loss_vs_speed.png`

# Chapter 9 Output and Results

## 9.1 Aggregated results

All entries are mean ± sample standard deviation across three runs.

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

## 9.2 Observations

**Packet delivery ratio.** AODV has higher mean PDR in all six matched cells. The strongest AODV delivery result is 88.26% with 20 nodes at 5 m/s. The weakest result is DSDV at 10 nodes and 20 m/s, with 28.22% PDR. The largest gap appears at 10 nodes and 20 m/s, where AODV records 65.53% and DSDV records 28.22%.

**Throughput and loss.** AODV also has higher received throughput and lower packet loss in all six cells. This is internally consistent because throughput uses received bytes and loss is calculated from transmitted minus received packets. The best AODV throughput is 178.64 kb/s for 20 nodes at 5 m/s; the lowest DSDV throughput is 57.13 kb/s for 10 nodes at 20 m/s.

**Effect of mobility.** Increased speed generally reduces delivery. With 10 nodes, AODV PDR drops from 74.48% at 5 m/s to 65.53% at 20 m/s, while DSDV drops from 49.75% to 28.22%. At 20 nodes, AODV falls from 88.26% to 55.98%, and DSDV falls from 65.96% to 41.09%.

**Effect of node count.** At 5 m/s, increasing nodes from 10 to 20 improves PDR for both protocols, likely because extra nodes improve the availability of intermediate paths in the fixed area. At 20 m/s the pattern is not universal: AODV falls from 65.53% at 10 nodes to 55.98% at 20 nodes, showing that more nodes can also increase contention and route changes.

**Delay.** Delay should be interpreted carefully. At 10 nodes and 5 m/s, DSDV has lower mean delay (40.35 ms) than AODV (57.01 ms), although DSDV delivered fewer packets. In several conditions the standard deviation is large, for example AODV at 20 nodes and 5 m/s has 71.39 ± 93.63 ms. A delay average includes only successful packets, so it cannot by itself describe overall reliability. The three repeats do not support a stable general delay ranking.

## 9.3 Output artifacts

The project produces raw FlowMonitor XML, per-run summaries, manifests, mobility traces, status logs, aggregate CSVs, plots, and AODV/DSDV NetAnim XML files. This evidence enables a reviewer to trace the reported aggregate numbers back to individual simulator outputs.

# Chapter 10 Conclusion

This project implemented a reproducible NS-3.45 MANET simulation to compare reactive AODV with proactive DSDV. Across 36 valid runs using IEEE 802.11b ad-hoc Wi-Fi, Random Waypoint movement, three UDP flows, node counts of 10 and 20, and speeds of 5, 10, and 20 m/s, AODV achieved higher mean PDR and throughput and lower application packet loss in all six matched conditions. The best measured delivery result was AODV with 20 nodes at 5 m/s, with a mean PDR of 88.26%. The lowest was DSDV with 10 nodes at 20 m/s, with 28.22%.

The study also shows why a single metric should not decide protocol selection. Delay did not rank the protocols consistently and varied greatly between runs. It measures only delivered packets, while PDR and loss express reliability more directly. The work contributes a fair comparison by using matched conditions, explicit traffic-flow filtering, saved raw artifacts, and paired mobility validation.

The conclusions are limited to this simulation configuration. The model uses Friis propagation, a fixed 802.11b rate, Random Waypoint mobility with zero pause, a fixed traffic load, and three repetitions. Future work can test additional repetitions, alternate propagation and mobility models, routing-control overhead, energy use, TCP traffic, and other protocols such as OLSR.

# Chapter 11 References

The first five entries are the sources supplied for this assessment. Verify their final URL/DOI and bibliographic details before printing because the supplied citations contain placeholders.

1. T. M. Abdala, “Analysis of AODV and DSDV Routing Protocols in Mobile Ad-Hoc Networks: A Review Paper,” *Journal of Insights in Basic and Applied Sciences*, vol. 2, no. 2, pp. 233–237, 2026. [Supplied citation; final link required.]
2. Raji N, “Comparative Study of Routing Protocols in Mobile Ad Hoc Networks,” *Peer-Reviewed Journal of Computer Science*, vol. 1, no. 3, pp. 8–12, 2026. [Supplied citation; final link required.]
3. A. Sharma, S. Negi, S. Singh, A. Sharma, and M. Irfanul Hasan, “Comparison of AODV and DSDV Routing Protocols in MANETs,” *Proceedings of the International Conference on Communication and Smart Devices*, 2025, doi: 10.1109/ICCoSD66074.2025.11348458.
4. B. A. Suleiman, G. A. Zimbele, and U. Yahaya, “Performance Analysis of AODV and DSDV Routing Protocol in MANET,” *Journal of Basics and Applied Sciences Research*, 2025. [Supplied citation; final DOI required.]
5. I. M. Selim, N. S. Abdelrehem, W. M. Alayed, H. M. Elbadawy, and R. A. Sadek, “MANET Routing Protocols’ Performance Assessment Under Dynamic Network Conditions,” *Applied Sciences*, vol. 15, no. 6, Art. 2891, 2025. [Supplied citation; final DOI required.]
6. C. E. Perkins and P. Bhagwat, “Highly Dynamic Destination-Sequenced Distance-Vector Routing (DSDV) for Mobile Computers,” *Proceedings of ACM SIGCOMM*, pp. 234–244, 1994.
7. C. Perkins, E. Belding-Royer, and S. Das, “Ad hoc On-Demand Distance Vector (AODV) Routing,” RFC 3561, IETF, 2003, doi: 10.17487/RFC3561.
8. J. Broch et al., “A Performance Comparison of Multi-Hop Wireless Ad Hoc Network Routing Protocols,” *Proceedings of ACM MobiCom*, pp. 85–97, 1998.
9. S. R. Das, C. E. Perkins, and E. M. Royer, “Performance Comparison of Two On-Demand Routing Protocols for Ad Hoc Networks,” *IEEE Personal Communications*, vol. 7, no. 1, pp. 16–28, 2000.
10. D. Kumar, A. Srivastava, and S. C. Gupta, “Performance Comparison of DSDV and AODV Routing Protocols in MANETS,” *International Journal of Electronics Communication and Computer Technology*, vol. 2, no. 3, pp. 120–124, 2012.
11. A. A. Chavan, D. S. Kurule, and P. U. Dere, “Performance Analysis of AODV and DSDV Routing Protocol in MANET and Modifications in AODV against Black Hole Attack,” *Procedia Computer Science*, vol. 79, pp. 835–844, 2016, doi: 10.1016/j.procs.2016.03.108.
12. R. Singh and N. Singh, “Performance Assessment of DSDV and AODV Routing Protocols in Mobile Adhoc Networks with Focus on Node Density and Routing Overhead,” *2020 International Conference on Emerging Smart Computing and Informatics*, pp. 298–303, 2020, doi: 10.1109/ESCI48226.2020.9167627.
13. ns-3 Consortium, *ns-3.45 Model Library*, 2024. Available: https://www.nsnam.org/docs/release/3.45/models/ns-3-model-library.pdf
14. ns-3 Consortium, “FlowMonitor,” *ns-3 Model Library Documentation*, 2024. Available: https://www.nsnam.org/docs/release/3.45/models/html/flow-monitor.html
15. ns-3 Consortium, “manet-routing-compare.cc,” NS-3.45 local example and API reference. Available: https://www.nsnam.org/doxygen/dc/d7a/manet-routing-compare_8cc_source.html

## Appendix A Reproducibility commands

```bash
cd ns-3.45
./ns3 configure -d optimized --enable-examples --disable-tests --disable-python-bindings
./ns3 build manet-aat -j 8

cd ..
python3 scripts/run_smoke_tests.py
python3 scripts/run_experiments.py
python3 scripts/process_results.py
python3 scripts/validate_results.py
python3 scripts/plot_results.py
python3 scripts/generate_report.py
```

## Appendix B Evidence locations

- Raw runs: `../results/raw/`
- Status ledger: `../results/experiment_status.csv`
- All individual run rows: `../results/processed/all_runs.csv`
- Mean and sample-standard-deviation table: `../results/processed/aggregate_mean_std.csv`
- Validation result: `../results/processed/validation_summary.json`
- Paired mobility validation: `../results/paired_mobility_validation.csv`
- Final figures: `../results/plots/`
- AODV and DSDV animations: `../results/animations/`
