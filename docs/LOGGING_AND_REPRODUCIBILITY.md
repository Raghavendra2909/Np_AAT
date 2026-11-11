# Logging, Output Layout and Reproducibility

## 1. Required directory structure

Adapt paths to the actual workspace without moving the NS-3 tree unnecessarily. Preserve the following logical structure:

```text
AGENTS.md
MANET_AAT_README.md
scratch/
  manet-aat.cc
scripts/
  run_smoke_tests.py       # or equivalent shell runner
  run_experiments.py
  process_results.py
  validate_results.py
  plot_results.py
  generate_report.py       # if appropriate
results/
  pilot/
  raw/
    protocol_aodv/nodes_10/speed_5/run_1/...
    protocol_dsdv/nodes_10/speed_5/run_1/...
  processed/
    all_runs.csv
    aggregate_mean_std.csv
  plots/
  animations/
  logs/
  experiment_status.csv
  paired_mobility_validation.csv
docs/
  ...
  IMPLEMENTATION_STATUS.md
reports/
  technical_report.md
  demo_script.md
```

Place NS-3 source under its expected directories; do not make a second copy of the entire simulator inside results or reports.

## 2. Per-run files

Each run directory should contain:

- `run.log` (configuration banner, metrics summary, warnings/errors; captured stdout and stderr; timestamps/exit code may be in manifest);
- `summary.csv` (header + one data row);
- `manifest.json` (all parameters, command, seed/run, version, timestamp, source revision/hash if available, output paths, status);
- `flowmon.xml` (raw FlowMonitor output);
- `mobility.csv` (time/node/x/y/z positions at a fixed sample interval);
- animation XML only for selected demo cases, with flag in the manifest.

Keep paths deterministic by parameter. If a run folder already contains a completed run, stop with an informative message or require an explicit overwrite option; do not silently overwrite evidence.

## 3. Logs

- Capture the full command line and working directory.
- Capture standard output and standard error.
- Record start/end time and exit code.
- Include NS-3 release, platform and relevant tool versions where discoverable.
- Log warnings that can affect validity.
- The experiment runner must continue the campaign after an individual failure only if it records that failure and continues safely; it must return an overall nonzero status if any expected run remains failed/blocked.
- Keep pilot runs separate from final runs.

## 4. Manifest fields

At minimum include:

- project title and code version/hash;
- NS-3 version (verified from local source);
- operating system/shell/compiler/build mode where available;
- exact command and normalized config values;
- protocol, node count, area, nominal speed, pause, Wi-Fi/PHY/propagation settings;
- traffic flow definitions, ports, payload size, offered rate, app start/stop, simulator stop;
- seed and run number;
- animation enabled/disabled;
- timestamp, output files, exit code and status;
- validation result and any warnings.

## 5. Experiment identity

Unique run key: `(protocol, num_nodes, speed_mps, seed, run)`.

Do not treat protocols as identical when they differ only by capitalization. Normalize protocol names to uppercase in summary data and lowercase path tokens if convenient.

## 6. Automation contract

The runner must:

1. create the expected 36-run matrix;
2. save the exact command before execution;
3. execute each run from the NS-3 root using the verified NS-3.45 runner syntax;
4. send logs to the run folder;
5. determine success from exit code *and* required output/metric validation;
6. update the status ledger after each run;
7. keep going to gather diagnostic information but not hide failures;
8. validate duplicate/missing run keys at the end;
9. refuse to produce a final “complete” status when the matrix is incomplete.

## 7. Source and data hygiene

- Add no large generated binary/raw output to source files.
- Add a `.gitignore` for NS-3 build artifacts where appropriate, but do not modify an existing `.gitignore` destructively.
- Keep raw output; processed output must be regenerable from raw outputs.
- Explain the single command that reprocesses existing results without re-running simulations.
- Do not copy generated results into source code or hardcode metrics in plotting scripts.
