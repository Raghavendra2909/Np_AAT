# Simulation Architecture and Implementation Contract

## 1. End-to-end flow

```text
NodeContainer
  -> ad-hoc Wi-Fi devices/channel/PHY
  -> Random Waypoint mobility + position allocator
  -> IPv4 Internet stack with exactly one selected routing helper (AODV or DSDV)
  -> IPv4 address assignment
  -> UDP sinks + constant-rate UDP application sources
  -> FlowMonitor (all nodes)
  -> simulation end after traffic stops and cleanup interval
  -> per-run XML, CSV, mobility trace, run metadata and logs
  -> Python validation/aggregation/plots/report
```

NetAnim is a parallel observation path. The simulation should have a command-line animation flag. Animation can be disabled during most batch runs to limit overhead, but must be enabled for the two representative demo runs.

## 2. Topology

- `N` = 10 or 20 nodes.
- No access point, infrastructure BSS, wired backbone or central router.
- All nodes participate as potential forwarding nodes.
- Assign an IPv4 address to the ad-hoc Wi-Fi interface on each node.
- Use a fixed physical area for both node-count values so node count actually changes density.
- Start with a 500 m × 500 m area, then use a pilot to check connectivity/topology dynamics. If adjustment is necessary, document it and apply exactly the same area/radio configuration to every protocol/scenario.

## 3. Wi-Fi and radio model

Use the official NS-3.45 `manet-routing-compare.cc` as the initial reference. It configures 802.11b ad-hoc Wi-Fi, a constant-rate station manager and a Friis propagation-loss model. Inspect the 3.45 implementation and APIs rather than copying blindly.

Set the Wi-Fi standard, PHY/channel, MAC mode, control/data rate and transmission power explicitly rather than relying on undocumented defaults. A starting point is 802.11b / `DsssRate11Mbps` / Friis / 7.5 dBm as in the official example; pilot-test for the selected 10/20-node area and log the final choices. Keep them identical across compared protocol runs.

Do not use a fixed `RangePropagationLossModel` as the default unless the official setup or a documented pilot justifies it. Prefer a propagation model with clearly stated parameters and document its limitations. Do not tune radio values to make one protocol look better.

## 4. Mobility

- Model: `RandomWaypointMobilityModel`.
- Nominal speed: fixed per scenario at 5, 10 or 20 m/s (use a verified NS-3 `ConstantRandomVariable` configuration or an equivalent explicit setup).
- Pause: 0 seconds.
- Use a position allocator bounded by the selected fixed area.
- Set global master seed to 12345 and run number to 1, 2 or 3.
- Assign explicit random streams to position/mobility using APIs supported by the installed 3.45 version. Check whether the position allocator and `MobilityHelper` expose `AssignStreams` and use the applicable method(s).
- Save a time-sampled mobility trace (at least one sample/node/second, including node ID, time, x, y, z) for every run. Compare traces of corresponding AODV and DSDV runs at equal node count/speed/run.

A seed alone is not evidence of paired movement. The implementation must check the traces.

## 5. Routing

The `--protocol` option accepts `AODV` or `DSDV` only (case normalization can be supported). Validate unknown names with a helpful error. Install exactly one selected routing protocol for each run. Use built-in `AodvHelper` or `DsdvHelper` from the installed release.

Do not combine routing helpers in the same routing stack unless the official example specifically requires and documents a routing-list design; it does not for this two-protocol comparison. Do not add OLSR or DSR to the scored project.

## 6. Application traffic

Use three simultaneous unidirectional UDP data flows for both N=10 and N=20:

| Flow | Source node | Destination node | Sink UDP port |
|---|---:|---:|---:|
| F1 | 0 | N-1 | 9000 |
| F2 | 1 | N-2 | 9001 |
| F3 | 2 | N-3 | 9002 |

For each flow, use 512-byte payloads and 64 kb/s application data rate, continuously on (or a verified equivalent). Keep all flow settings the same across protocol runs. Use sinks that receive continuously; start at 5 s, stop at 60 s, simulation ends at 65 s. This gives a 55-second configured traffic window and a 5-second cleanup period.

Verify the chosen NS-3 application helper attributes in local 3.45 headers/examples. If using `OnOffApplication`, configure the on/off random variables to represent continuous transmission and use UDP. Ensure sink port assignments are unique and traffic is not bidirectional unless the design is explicitly revised in docs.

## 7. FlowMonitor and metrics filtering

Install FlowMonitor once for the simulation and serialize its XML. Use the local IPv4 flow classifier to identify the three configured UDP data flows by protocol and destination port, with source/destination addresses checked as appropriate. Do not include routing-control traffic or unrelated flows in application metrics.

For the required four metrics, aggregate app-flow counters with sums across all three flows. Keep the data-flow filter explicit in code and report.

## 8. End-of-run ordering

- Applications start at 5 s.
- Applications stop at 60 s.
- `Simulator::Stop` at 65 s.
- Run simulation, call FlowMonitor check/serialization methods where appropriate for 3.45, and destroy simulator objects cleanly.
- Five seconds is the starting cleanup interval. If FlowMonitor diagnostics indicate queued/untracked packet artifacts, explain and validate a suitable interval. Never silently redefine packet loss to hide a discrepancy.

FlowMonitor can consider packets still queued below IP at simulation end to be lost. Official documentation recommends stopping applications before the simulation end and leaving time for queued packets to drain: https://www.nsnam.org/docs/release/3.45/models/html/flow-monitor.html

## 9. C++ structure

Keep one file unless the implementation has a compelling reason to split:

- argument/config parsing + validation;
- topology/Wi-Fi setup;
- mobility/stream assignment;
- routing helper selection;
- address assignment;
- applications;
- optional `AnimationInterface` setup;
- mobility trace scheduling;
- FlowMonitor setup;
- simulation execution;
- app-flow filtering and metrics calculation;
- output and clean shutdown.

Make parameter names and console output readable. Print a configuration banner before the run and a concise actual metric summary after it. Handle output-directory creation and file-open errors.

## 10. Required CLI settings

At minimum expose and validate:

- `protocol` = AODV or DSDV;
- `numNodes` = 10 or 20 for full experiments (a smaller smoke test can be added separately if destinations remain valid);
- `nodeSpeed` = 5, 10 or 20 m/s;
- `nodePause` = 0;
- `seed` = 12345;
- `run` = 1, 2 or 3;
- `outputDir`;
- `enableAnimation` = 0 or 1.

It is acceptable to expose other fixed physical/traffic settings, but record them in the manifest and do not vary them in the frozen matrix.
