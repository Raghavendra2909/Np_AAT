# NetAnim Visualization and AAT Demo

## 1. Required visualization outputs

Generate at least two representative animation XMLs from actual simulations:

- AODV: 10 nodes, 20 m/s, run 1;
- DSDV: 10 nodes, 20 m/s, run 1;

Both must share the same seed/run and verified mobility trajectory. Store under `results/animations/` and record the exact matching parameters. The full 36-run metric campaign does not need an animation XML per run; all 36 runs still require metrics, logs, raw XML and mobility traces.

## 2. NetAnim implementation

- Verify the installed NS-3.45 `netanim-module.h` and `AnimationInterface` API in the local source tree.
- Add an `enableAnimation` CLI switch. When enabled, construct the animation interface with a unique XML output path and ensure it is finalized/closed according to the local API.
- Use supported animation updates to label nodes if straightforward; avoid spending time on cosmetic customizations.
- Verify XML is non-empty, valid enough for the target viewer and corresponds to the manifest's protocol/seed/run.
- Do not assume the separate NetAnim GUI is installed just because the NS-3 module builds. Locate/check the viewer and record its version.

Official NS-3.45 reference: https://www.nsnam.org/docs/release/3.45/models/ns-3-model-library.pdf

## 3. Evidence for demonstration

Prepare these artifacts before the demo:

1. AODV animation XML and screenshot if the viewer is available.
2. DSDV animation XML and screenshot if the viewer is available.
3. The four plots derived from the final aggregated CSV.
4. AODV-vs-DSDV summary table.
5. One printed/terminal excerpt showing protocol, node count, speed, seed/run and computed metrics.
6. A fallback screen recording or pre-opened animation file if live GUI startup is unreliable. Do not fake or alter the simulation output.

If the viewer cannot launch, still produce valid XML and exact opening instructions; mark actual GUI viewing as blocked rather than claiming success.

## 4. Five-minute demo sequence

### 0:00–0:30 — Problem

“MANET nodes communicate without fixed infrastructure. Their movement changes connectivity. We compare a reactive protocol (AODV) with a proactive protocol (DSDV).”

### 0:30–1:15 — Design

Show the architecture: nodes → ad-hoc Wi-Fi → mobility → selected protocol → UDP traffic → FlowMonitor.

### 1:15–2:15 — AODV animation

Open the recorded AODV NetAnim file, show movement and packets, and identify source/destination flows. Do not claim every visible packet is an application packet unless the display proves it.

### 2:15–3:15 — DSDV animation

Open the matching DSDV file and explain that it uses the same intended setup/mobility trace, with only the selected routing protocol changed.

### 3:15–4:30 — Real performance results

Show PDR, delay, throughput and packet-loss graphs. Explain one observed result from measured values only, including scenario and units. Do not assert that either protocol is universally better.

### 4:30–5:00 — Conclusion/limitations

State the tested parameter ranges, the number of completed runs, the fact that this is simulation rather than physical deployment, and one limitation/future direction.

## 5. Viva-ready one-liners

- **MANET:** wireless nodes form a network without fixed infrastructure; nodes can forward traffic for one another.
- **AODV:** reactive/on-demand route discovery.
- **DSDV:** proactive/table-driven route maintenance.
- **Random Waypoint:** nodes move toward randomly selected waypoints at a specified speed, with configured pauses.
- **FlowMonitor:** records per-flow IP-layer metrics in NS-3; it is not a packet-level real-world sniffer.
- **PDR:** fraction of sent application-flow packets received.
- **Delay:** measured end-to-end packet delay averaged over received packets.
- **Throughput:** received IP-level bytes converted to bits and divided by the configured measurement window.
- **Limitation:** results depend on modeled radio/mobility/traffic parameters and are not direct predictions of every real wireless deployment.
