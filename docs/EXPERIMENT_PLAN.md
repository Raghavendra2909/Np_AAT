# Full Experiment Plan (36 Runs, No Omissions)

## 1. Independent variables

- Protocol: AODV, DSDV.
- Number of nodes: 10, 20.
- Nominal speed: 5, 10, 20 m/s.
- Repetition/run number: 1, 2, 3.

Total: `2 × 2 × 3 × 3 = 36 runs`.

## 2. Fixed controls

Hold the following constant except where directly specified by an independent variable:

- NS-3 version (3.45), C++ source/build and tool versions;
- area/position bounds for both node counts;
- Wi-Fi standard, channel, MAC, PHY, propagation model, data/control mode and Tx power;
- mobility model, pause time and speed within each speed condition;
- three source/destination flow pairs and UDP ports;
- packet payload and offered data rate;
- traffic start/stop time and simulator stop time;
- master seed and matching run number for AODV/DSDV paired cases;
- metric equations and scripts.

Node count deliberately changes from 10 to 20 while the area remains fixed, so node density changes. Do not vary node count and area together.

## 3. Complete matrix

The runner must build its expected matrix programmatically and confirm all keys exist exactly once:

| Protocol | Nodes | Speed (m/s) | Run IDs |
|---|---:|---:|---|
| AODV, DSDV | 10 | 5 | 1, 2, 3 each |
| AODV, DSDV | 10 | 10 | 1, 2, 3 each |
| AODV, DSDV | 10 | 20 | 1, 2, 3 each |
| AODV, DSDV | 20 | 5 | 1, 2, 3 each |
| AODV, DSDV | 20 | 10 | 1, 2, 3 each |
| AODV, DSDV | 20 | 20 | 1, 2, 3 each |

Run ordering should interleave matched conditions to make comparisons and recovery easy, e.g. AODV then DSDV for nodes=10/speed=5/run=1, followed by the matching pair for run=2, etc. Ordering is not an experimental variable.

## 4. RNG pairing and mobility verification

- Global fixed seed: 12345.
- NS-3 run number: 1, 2, 3.
- Every AODV/DSDV pair must receive the same `(nodes, speed, seed, run)` values.
- Explicitly assign streams to position and mobility random variables using the API verified in the 3.45 tree. Ensure the routing stack does not shift the mobility random streams.
- Save `mobility.csv` for each run.
- Compare paired traces at each timestamp and node ID. Write the result into `results/paired_mobility_validation.csv`. A paired case is valid only if positions agree within a small documented floating-point tolerance.
- If exact paired traces cannot be achieved after correct stream assignment, do not claim exact pairing. Explain the limitation in the report and make the best controlled alternative explicit.

## 5. Calibration/pilot phase (not a substitute for the matrix)

Run a few pilot cases to determine whether the selected area/radio configuration yields useful connectivity and mobility effects. This is a calibration stage. Record it separately under `results/pilot/`; do not mix pilots into final aggregates.

Pilot rules:

1. Do not calibrate to favor AODV or DSDV.
2. If traffic is received by neither protocol, investigate the topology/radio setup before proceeding.
3. If all nodes remain effectively connected regardless of mobility, evaluate the trajectory/connectivity evidence and adjust the fixed arena/radio settings only if justified.
4. Once frozen, document the final fixed settings and use them across all 36 runs.
5. Re-run any already completed condition if a global parameter changes.

## 6. Run output contract

For each run create a unique directory such as:

`results/raw/protocol_aodv/nodes_10/speed_5/run_1/`

It should contain at least:

- `run.log` (stdout + stderr or clearly separated equivalents);
- `summary.csv` (exactly one data row plus header for that run);
- `manifest.json` (config, seed/run, versions, code hash if available, command, timestamps, status);
- `flowmon.xml`;
- `mobility.csv`;
- `animation.xml` only for designated demo runs (or a manifest flag explaining why not).

Do not overwrite an existing completed run without explicit `--force`/overwrite choice. The orchestrator must return a nonzero exit code when any expected run fails.

## 7. Outputs after all runs

- `results/experiment_status.csv`: every expected run with command, start/end, exit code and status.
- `results/paired_mobility_validation.csv`.
- `results/processed/all_runs.csv`: 36 valid rows, no duplicate run keys.
- `results/processed/aggregate_mean_std.csv`: grouped by protocol × nodes × speed, with `n`, mean and sample standard deviation for each metric.
- `results/plots/pdr_vs_speed.png` and `.svg`.
- `results/plots/delay_vs_speed.png` and `.svg`.
- `results/plots/throughput_vs_speed.png` and `.svg`.
- `results/plots/packet_loss_vs_speed.png` and `.svg`.
- a machine-readable validation summary.

## 8. Statistics and presentation

- Use mean and sample standard deviation across the three runs per protocol × node count × speed.
- Include variability, such as error bars, in plots where readable.
- Plot AODV and DSDV as distinct series and distinguish node-count cases clearly.
- Keep units in labels: PDR (%), average delay (ms), throughput (kb/s), packet loss (packets or %; use packet count as primary and optionally percentage).
- Do not present results as statistically significant solely because means differ. Three runs provide a small-repeat study; state this limitation.
- Do not omit awkward/poor results. If a run has zero transmitted app packets, a failed flow filter, or no connectivity, flag the invalid condition and fix the scenario or report the true limitation rather than silently removing the row.
