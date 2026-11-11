# Presentation outline

1. **Title.** Performance Evaluation of AODV and DSDV Routing Protocols in Mobile Ad Hoc Networks Using NS-3.
2. **Problem.** Movement changes multi-hop connectivity, so routing strategy affects delivery, delay, throughput and loss.
3. **Protocols.** AODV discovers routes on demand. DSDV advertises routes in advance.
4. **Architecture.** Ad-hoc 802.11b nodes, Random Waypoint, one routing protocol per run, three UDP flows, FlowMonitor, optional NetAnim.
5. **Experiment.** Area 500 m × 500 m, transmit power 7.5 dBm, speeds 5/10/20 m/s, 10 and 20 nodes, seed 12345, runs 1–3, 36 runs.
6. **Metrics.** PDR = 100×RX/TX. Delay = 1000×delaySum/RX ms. Throughput = 8×RX_BYTES/(55×1000) kb/s. Loss = TX−RX packets.
7. **Animation.** `results/animations/aodv_nodes10_speed20_run1.xml` and `results/animations/dsdv_nodes10_speed20_run1.xml`.
8. **PDR and delay.** Use `results/plots/pdr_vs_speed.png` and `results/plots/delay_vs_speed.png` with the means below.
9. **Throughput and loss.** Use `results/plots/throughput_vs_speed.png` and `results/plots/packet_loss_vs_speed.png`.
10. **Inference.** Delivery favors AODV in every cell; faster movement lowers delivery; extra nodes help only at low speed; delay is not a second ranking. Read the bullets below.
11. **Conclusion.** AODV delivered more application traffic than DSDV in this scenario. Quote the best and worst cells, then the simulation limits.

## Inference for slide 10

The offered application load is three flows at 64 kb/s, 192 kb/s in total. Throughput follows packet delivery because both are computed from the packets that arrived. Every run sends 2577 data packets, and packet loss is TX − RX, so the loss ranking is the reverse of the PDR ranking.

1. **Delivery favors AODV in all six cells.** The gap is about 14.89 to 37.30 percentage points. The widest gap is 10 nodes at 20 m/s, where AODV delivers 65.53% and DSDV delivers 28.22%.
2. **Faster movement reduces delivery for both protocols.** From 5 m/s to 20 m/s, AODV with 10 nodes falls by about 8.95 points and DSDV with 10 nodes falls by about 21.52 points. With 20 nodes the drop is about 32.27 points for AODV and about 24.86 points for DSDV.
3. **More nodes help when movement is slow.** At 5 m/s, going from 10 to 20 nodes raises AODV by about 13.78 points (to 88.26%) and DSDV by about 16.21 points (to 65.96%). At 20 m/s that benefit disappears for AODV: 20 nodes deliver 55.98%, which is 9.55 points below the 10-node result.
4. **Delay is not a second ranking.** Delay is the average only over packets that arrived. At 10 nodes and 5 m/s, DSDV's mean delay is 40.35 ms and AODV's is 57.01 ms, while DSDV delivered far less. AODV's delay sample standard deviation is 47.56 ms in that cell and 93.63 ms at 20 nodes and 5 m/s. Three repeats are too few to rank the protocols by delay.

A fair reading of the mechanism, without a direct measurement of control packets, is that AODV looks up a route when a packet needs one, so it can follow the topology after nodes move. DSDV keeps tables that can go stale while nodes are moving quickly. This project counted application packets on ports 9000–9002 only, so routing overhead was not compared.

## Conclusion for slide 11

On this IEEE 802.11 ad-hoc network, with Random Waypoint mobility, pause 0, and three constant-rate UDP flows, AODV gave higher packet delivery, lower packet loss, and higher application throughput than DSDV at both 10 and 20 nodes and at 5, 10, and 20 m/s. The best measured delivery is AODV with 20 nodes at 5 m/s (88.26%). The worst is DSDV with 10 nodes at 20 m/s (28.22%). Higher speed reduced delivery for both protocols, and the extra nodes helped only while the nodes were moving slowly. Average delay is a separate observation: it is computed only for packets that arrived, and the repeat-to-repeat spread is too large for a stable ranking. The numbers describe NS-3.45 with 802.11b, the Friis model, a 500 m square, 7.5 dBm transmit power, seed 12345, and three repeats.

## Numbers for slides 8 and 9

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

Validation status when this file was generated: **PASS**.
