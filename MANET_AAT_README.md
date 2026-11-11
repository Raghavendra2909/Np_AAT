# MANET AAT — AODV and DSDV in NS-3.45

Performance evaluation of the built-in AODV and DSDV models on a mobile IEEE 802.11 ad-hoc network. The measured matrix is 36 runs (2 protocols × 2 node counts × 3 speeds × 3 runs). This file records the commands that produced the files currently in `results/`.

## Environment

- OS: Ubuntu 26.04.1, bash, g++ 15.2.0, CMake 4.2.3, Python 3.14.4, Matplotlib 3.10.7
- Simulator: `ns-3.45/` (`VERSION` file contains `3.45`)
- Build: optimized, examples on, tests off, Python bindings off
- Wrapper: `./ns3` (CMake). Do not use `./waf`.
- Local compatibility edit: `ns-3.45/ns3` replaces positional `store_true` arguments with `set_defaults`, because Python 3.14 rejects that argparse pattern. No NS-3 module source and no official example were modified.

## One-time build

```bash
cd ns-3.45
./ns3 configure -d optimized --enable-examples --disable-tests --disable-python-bindings
./ns3 build manet-aat -j 8
```

## One simulation

From `ns-3.45`:

```bash
./ns3 run --no-build "manet-aat --protocol=AODV --numNodes=10 --nodeSpeed=10 --nodePause=0 --seed=12345 --run=1 --outputDir=/absolute/path/to/out --enableAnimation=0 --overwrite=1 --areaX=500 --areaY=500 --txPowerDbm=7.5"
```

`protocol` is `AODV` or `DSDV`. `numNodes` is 10 or 20. `nodeSpeed` is 5, 10 or 20. `run` is 1, 2 or 3.

## Smoke tests

From the project root:

```bash
python3 scripts/run_smoke_tests.py
```

This rebuilds `manet-aat`, rejects bad CLI values, and runs AODV and DSDV at 10 nodes, 10 m/s, seed 12345, run 1. Output: `results/smoke/`.

## Pilot

```bash
python3 scripts/run_experiments.py --pilot --force
```

Four calibration runs (both protocols, 10 and 20 nodes, 20 m/s, run 1) go to `results/pilot/` and are not part of the final aggregate. The frozen radio and area are in `config/scenario.json`: 500 m × 500 m, Friis, 7.5 dBm, 802.11b, `DsssRate11Mbps`.

## Full 36-run matrix

```bash
python3 scripts/run_experiments.py
```

Add `--force` to replace an existing `summary.csv`. The runner returns a non-zero status if any run is not `PASS`. Ledger: `results/experiment_status.csv`.

Each run directory under `results/raw/protocol_<name>/nodes_<n>/speed_<v>/run_<k>/` contains `run.log`, `summary.csv`, `manifest.json`, `flowmon.xml`, `mobility.csv` and `flows.csv`. The two demo runs also contain `animation.xml`.

## Reprocess without resimulating

```bash
python3 scripts/process_results.py
python3 scripts/validate_results.py
python3 scripts/plot_results.py
python3 scripts/generate_report.py
python3 scripts/test_validation.py
```

`process_results.py` rewrites `results/processed/all_runs.csv`, `results/processed/aggregate_mean_std.csv` and `results/paired_mobility_validation.csv` from the raw summaries and mobility traces.

## Demo

How to present the CSV files, the animation, and the four graphs is in [docs/DEMO_WALKTHROUGH.md](docs/DEMO_WALKTHROUGH.md).

## Short commands

`./manet` is the short launcher. What each command does, the arguments, and examples are in [docs/MANET_COMMANDS.md](docs/MANET_COMMANDS.md).

```bash
./manet build
./manet run AODV 10 20 1 --animate
./manet smoke
./manet pilot
./manet matrix
./manet analyze
./manet anim aodv
./manet anim dsdv
```

## NetAnim binary

NS-3.45 does not ship the animator. A local NetAnim 3.109 build used by `./manet anim` is under `tools/`. The XML header says `anim ver="netanim-3.109"`.

## Report

- `reports/technical_report.md`
- `reports/demo_script.md`
- `reports/presentation_outline.md`
- Plots: `results/plots/*_vs_speed.png` and `.svg`

## Current measured status

- Ledger: 36 / 36 `PASS`
- Validation: `results/processed/validation_summary.json` status `PASS`
- Paired mobility: 18 / 18 `PASS`
- Stock `manet-routing-compare`: AODV exit 0 and DSDV exit 0. Per-second CSVs are in `results/stock-example/aodv/` and `results/stock-example/dsdv/` and both reach simulation second 199.

In all 6 node-count/speed cells, AODV's mean PDR was higher than DSDV's. The highest mean PDR was AODV, 20 nodes, 5 m/s (88.26%). The lowest was DSDV, 10 nodes, 20 m/s (28.22%). Mean delay did not follow that same order. See the report table for every mean and sample standard deviation. These figures are simulation results for this configuration, not a general ranking of the protocols.



use
```bash
env \
  -u GTK_EXE_PREFIX \
  -u GTK_PATH \
  -u GTK_MODULES \
  -u GTK_IM_MODULE_FILE \
  -u GIO_MODULE_DIR \
  QT_QPA_PLATFORM=xcb \
  ./tools/netanim-netanim-3.109/NetAnim
```