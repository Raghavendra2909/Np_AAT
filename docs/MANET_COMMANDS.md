# Short commands (`./manet`)

Run every command below from the project root:

```bash
cd ~/Downloads/projects/network-lab
./manet <command> [arguments]
```

`./manet` is a small launcher. It calls `scripts/manet.py`. Help for the whole tool, or for one command:

```bash
./manet --help
./manet anim --help
./manet run --help
```

The launcher does not store a results filename or a NetAnim path inside the command you type. It looks up files on disk. Protocol names, node counts, speeds, and run numbers are checked against the lists in `scripts/experiment_lib.py`:

| Argument | Allowed values |
|---|---|
| protocol | `AODV`, `DSDV` (capital letters are optional) |
| nodes | `10`, `20` |
| speed | `5`, `10`, `20` (meters per second) |
| run | `1`, `2`, `3` |

Area, pause time, transmit power, and the RNG seed are read from `config/scenario.json` whenever a simulation starts. Change that file to change those settings for later runs. Do not change it after the 36-run matrix unless you rerun the affected cases.

## `./manet build`

Compiles the simulation program `ns-3.45/scratch/manet-aat.cc`.

```bash
./manet build
```

Run this once after cloning or after you edit the C++ file. Later `run`, `smoke`, `pilot`, and `matrix` commands expect that build to exist.

## `./manet run`

Runs **one** simulation.

```bash
./manet run <protocol> <nodes> <speed> <run> [--animate] [--force] [--where raw|pilot|smoke]
```

Example: AODV, 10 nodes, 20 m/s, run 1, and also write a NetAnim file:

```bash
./manet run AODV 10 20 1 --animate
```

What it does:

1. Checks that the four numbers are in the allowed lists.
2. Reads area, pause, power, and seed from `config/scenario.json`.
3. Runs NS-3 and writes a folder of results.

Default folder (`--where raw`):

```text
results/raw/protocol_aodv/nodes_10/speed_20/run_1/
```

That folder gets `run.log`, `summary.csv`, `manifest.json`, `flowmon.xml`, `mobility.csv`, and `flows.csv`. With `--animate`, it also writes `animation.xml` and copies it to `results/animations/`.

| Option | Meaning |
|---|---|
| `--animate` | Turn on NetAnim XML for this run only. Leave it off for ordinary metric runs. |
| `--force` | Replace a `summary.csv` that is already in the output folder. Without this flag, a finished folder is left as it is and the command stops with an error. |
| `--where raw` | Final experiment data. This is the default. The ledger is `results/experiment_status.csv`. |
| `--where pilot` | Calibration data under `results/pilot/`. Not included in the final graphs. |
| `--where smoke` | A trial run under `results/smoke/`. Not included in the final graphs. |

The command prints `PASS` or `FAIL` through its exit code. Exit code `0` means the run passed.

## `./manet smoke`

Checks the program before a long experiment.

```bash
./manet smoke
```

It rebuilds `manet-aat`, then checks that bad inputs are rejected (unknown protocol, bad node count, bad speed, bad run, missing output directory, unknown flag). It then runs two real cases: AODV and DSDV, 10 nodes, 10 m/s, run 1. Output stays in `results/smoke/` and is not mixed into the 36-run tables.

## `./manet pilot`

Runs a short calibration set, not the full matrix.

```bash
./manet pilot
./manet pilot --force
```

The cases are built from the same protocol, node-count, and speed lists: both protocols, both node counts, the highest speed, run 1. Today that is four runs at 20 m/s. Results go to `results/pilot/` and are kept out of the final aggregate. `--force` overwrites a pilot folder that already has a summary.

Use the pilot to see whether nodes can deliver traffic. The frozen 500 m × 500 m, 7.5 dBm setup was kept because these runs delivered packets and were not stuck at 0% or 100% delivery.

## `./manet matrix`

Runs the full experiment: 2 protocols × 2 node counts × 3 speeds × 3 runs = 36 simulations.

```bash
./manet matrix
./manet matrix --force
```

Order is AODV then DSDV for each node count, speed, and run. Each case is written under `results/raw/`. The status of every case is updated in `results/experiment_status.csv`. If one case fails, it is tried once more. The command exits with a non-zero status if any case is still not `PASS`.

Without `--force`, a folder that already contains `summary.csv` is not overwritten. With `--force`, those folders are run again.

The two demo cases (10 nodes, 20 m/s, run 1, both protocols) also write NetAnim XML. The other 34 runs do not, so the batch stays smaller.

## `./manet analyze`

Rebuilds the tables, checks, plots, and report from raw files. It does **not** rerun NS-3.

```bash
./manet analyze
```

Steps, in order:

1. `scripts/process_results.py` writes `results/processed/all_runs.csv`, `results/processed/aggregate_mean_std.csv`, and `results/paired_mobility_validation.csv`.
2. `scripts/validate_results.py` checks the 36 rows, FlowMonitor XML, formulas, and animation files. It writes `results/processed/validation_summary.json`.
3. `scripts/plot_results.py` writes the four PNG and SVG graphs in `results/plots/`.
4. `scripts/generate_report.py` rewrites `reports/technical_report.md`, `reports/demo_script.md`, and `reports/presentation_outline.md` from the CSV numbers.

If any step fails, later steps are skipped. Run this after `./manet matrix` when you want fresh plots and a report.

## `./manet anim`

Opens a NetAnim window for an animation XML file that is already on disk. Run it in the VirtualBox desktop so a window can appear. `NetAnim` by itself is not a system command.

```bash
./manet anim --list
./manet anim aodv
./manet anim dsdv
./manet anim aodv --nodes 10 --speed 20 --run 1
./manet anim --all
./manet anim --xml results/animations/aodv_nodes10_speed20_run1.xml
./manet anim aodv --dry-run
```

How a file is chosen:

1. Look in `results/animations/*.xml`.
2. Also look for `animation.xml` under `results/raw/`, `results/pilot/`, and `results/smoke/`.
3. Read the protocol, node count, speed, and run from the file name or from the run's `manifest.json`.
4. If the same case exists in more than one place, prefer the copy in `results/animations/`.
5. Keep only the files that match the protocol and any `--nodes`, `--speed`, or `--run` you passed.

| Situation | What happens |
|---|---|
| No file matches | The command prints the files it did find and exits with status 1. |
| One file matches | That file opens immediately. NetAnim 3.109 normally ignores a path and shows “please select an XML file”; the local build was changed so `./manet anim` loads the file for you. |
| Several files match | They are listed, and nothing opens, until you narrow the command or pass `--all`. |
| `--list` | Print matches and do not open a window. |
| `--dry-run` | Print the NetAnim program and XML path, and do not open a window. |
| `--all` | Open every match. |
| `--xml PATH` | Open that file even if the name does not match the usual pattern. |

The NetAnim program is chosen in this order:

1. The executable in the `NETANIM` environment variable, if you set one.
2. The newest executable named `NetAnim` under `tools/`.
3. A `NetAnim` program on your `PATH`, if one exists.

Example, if you built NetAnim somewhere else:

```bash
NETANIM=/opt/netanim/NetAnim ./manet anim aodv
```

The current demo files are the 10-node, 20 m/s, run 1 traces for AODV and DSDV. `./manet anim aodv` and `./manet anim dsdv` open those when they are the only match for each protocol.

## Suggested order

```bash
./manet build
./manet smoke
./manet pilot
./manet matrix
./manet analyze
./manet anim aodv
./manet anim dsdv
```

`smoke` and `pilot` are checks. `matrix` is the scored experiment. `analyze` turns the raw folders into the report. `anim` only displays XML that a previous run already wrote.
