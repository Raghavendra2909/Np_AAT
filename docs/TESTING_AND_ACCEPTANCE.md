# Test Plan and Definition of Done

## 1. Environment checks

- [ ] Local source tree verifies as NS-3.45.
- [ ] Version-appropriate configure/build command succeeds.
- [ ] Required protocol, Wi-Fi, mobility, FlowMonitor and NetAnim module support is present or any missing part is documented.
- [ ] Original `examples/routing/manet-routing-compare.cc` and local APIs have been inspected.
- [ ] No upstream/core file was modified.

## 2. C++ argument/config tests

- [ ] `--protocol=AODV` accepted.
- [ ] `--protocol=DSDV` accepted.
- [ ] Unknown protocol rejected with helpful error.
- [ ] Invalid node count/speed/run rejected clearly.
- [ ] Missing/unwritable output directory handled clearly.
- [ ] `--enableAnimation=0` runs without animation; `=1` creates the expected XML.

## 3. Smoke tests

Run one AODV and one DSDV case using 10 nodes, 10 m/s, master seed 12345, run 1. Verify:

- [ ] process exits successfully;
- [ ] expected number of nodes and three app-flow definitions are logged;
- [ ] at least one app flow has TX packets and the run's results are interpreted honestly;
- [ ] FlowMonitor XML is present and parseable;
- [ ] summary CSV has exactly one valid row;
- [ ] all required metrics are finite where defined and satisfy ranges;
- [ ] app flow ports are correctly filtered;
- [ ] traffic stops before simulation stop by the documented cleanup interval;
- [ ] full run log and manifest exist.

## 4. Paired reproducibility tests

- [ ] For each `(nodes, speed, run)` AODV/DSDV pair, exact common configuration is recorded.
- [ ] Explicit mobility/random streams are assigned according to verified 3.45 APIs.
- [ ] `mobility.csv` traces are compared by time and node ID.
- [ ] Paired movement equality result is saved.
- [ ] A test deliberately catches a changed parameter/duplicate output key.

## 5. Full campaign validation

- [ ] 36 unique expected run keys exist.
- [ ] All expected runs are `PASS` before final aggregate is labeled complete.
- [ ] Every run has logs, manifest, FlowMonitor XML, summary and mobility trace.
- [ ] Failed cases have retained logs and diagnostics and are not silently removed.
- [ ] No duplicate keys or missing rows.
- [ ] `all_runs.csv` has 36 validated rows.
- [ ] `aggregate_mean_std.csv` has 12 groups (2 protocols × 2 node counts × 3 speeds), each with n=3.
- [ ] PDR in [0,100], non-negative delay/throughput/loss, valid measurement duration and TX >= RX.
- [ ] Failed or invalid metrics are never silently converted into zero or omitted.

## 6. Plot/report validation

- [ ] Four plot pairs (PNG + SVG): PDR, delay, throughput, packet loss vs speed.
- [ ] AODV and DSDV are distinguished.
- [ ] Node-count groups are distinguishable.
- [ ] Titles, axes, units and legend are present.
- [ ] Plot values can be traced to aggregate CSV.
- [ ] Report conclusion references actual run results and does not claim universal real-world superiority.
- [ ] Limitations and simulation configuration are explicit.

## 7. NetAnim validation

- [ ] AODV XML exists and matches its manifest.
- [ ] DSDV XML exists and matches its manifest.
- [ ] The pair's mobility traces match.
- [ ] XML files are non-empty and target viewer/version is documented.
- [ ] GUI launch is tested if viewer is available; otherwise provide exact opening instructions and truthful blocked status.

## 8. Reproducibility/report package

- [ ] `MANET_AAT_README.md` explains environment, one-run commands, full-campaign command, processing command, plotting command, NetAnim opening, and report paths.
- [ ] `docs/IMPLEMENTATION_STATUS.md` contains evidence and current status for all gates.
- [ ] Technical report and five-minute demo notes exist.
- [ ] Every output path exists and no fabricated data/placeholders are presented as results.

## 9. Final status language

- `COMPLETE`: every required section passes.
- `INCOMPLETE`: code/artifacts exist but required stage(s) remain.
- `BLOCKED`: a concrete environment/tool dependency prevents one or more stages; identify precise command/error and recovery path.

Do not use `COMPLETE` if even one required experiment is missing or final results have not been validated.
