# Metrics, Formulae and Data Validation

## 1. Filter data traffic first

Metrics must apply only to the three configured UDP application flows (destination ports 9000, 9001, 9002, along with expected protocol and addresses where appropriate). Routing protocol control packets must not be counted as app data. Keep the selected flow IDs and five-tuples in debug output or a separate `flows.csv` to make the filter auditable.

FlowMonitor reports IPv4-layer flow statistics. Its byte counts include IP-level bytes and do not include layer-2 headers; state this when explaining throughput.

## 2. Required metrics

Aggregate counters across the three selected application flows before calculating aggregate metrics.

Let:

- `TX = sum(flow.txPackets)` over selected app flows.
- `RX = sum(flow.rxPackets)` over selected app flows.
- `TX_BYTES = sum(flow.txBytes)` over selected app flows.
- `RX_BYTES = sum(flow.rxBytes)` over selected app flows.
- `DELAY_SUM = sum(flow.delaySum seconds)` over selected app flows.
- `D = applicationStopSeconds - applicationStartSeconds` (configured traffic window, initially 55 s).

### Packet Delivery Ratio (PDR)

`PDR (%) = 100 × RX / TX`

If `TX == 0`, PDR is undefined; output blank/null plus a validation error, never zero by default. A valid run should transmit app packets.

### Average end-to-end delay

`Average delay (ms) = 1000 × DELAY_SUM / RX`

If `RX == 0`, average delay is undefined. Mark the run invalid/incomplete for the final comparative dataset; do not make a fabricated value.

### Throughput

`Throughput (kb/s) = 8 × RX_BYTES / (D × 1000)`

Use the same configured traffic duration D for all scenarios. State that `RX_BYTES` follows FlowMonitor's IPv4-level byte accounting. If a separate sink-payload throughput is also implemented, label it as a separate additional measure; do not mix its bytes/window with the FlowMonitor metric.

### Packet loss

`Packet loss (packets) = TX - RX`

Check `TX >= RX` for the selected application flow group. If not, investigate flow classification or duplicate aggregation; do not silently clamp the value. Optional packet loss percentage: `100 × (TX - RX) / TX`, when TX > 0.

## 3. FlowMonitor diagnostic counter

Also log `sum(flow.lostPackets)` as `flowmonitor_lost_packets_diagnostic`, but do not assume it must equal `TX - RX`. FlowMonitor's lost counter is based on packets it has not tracked/seen for its configured timeout; it can differ from a derived sent-minus-received count. Explain the distinction in the report. Never use unrelated protocol-control flow counters in the four application metrics.

## 4. Jitter/overhead

Jitter may be preserved as a diagnostic column if available, but it is not required for the frozen evaluation. Do not add routing-overhead metrics unless the installed NS-3 model exposes a defensible, verified way to measure them without modifying routing implementations; the four required metrics take priority.

## 5. Per-run summary schema

At minimum:

- `experiment_id`
- `protocol`
- `ns3_version`
- `num_nodes`
- `area_x_m`, `area_y_m`
- `node_speed_mps`, `node_pause_s`
- `seed`, `run`
- `wifi_standard`, `phy_mode`, `propagation_model`, `tx_power_dbm`
- `flow_count`, `packet_size_bytes`, `flow_rate_kbps`
- `app_start_s`, `app_stop_s`, `measurement_duration_s`, `sim_stop_s`
- `tx_packets`, `rx_packets`, `tx_bytes`, `rx_bytes`
- `packet_loss_packets`, `packet_loss_percent`, `pdr_percent`
- `delay_sum_s`, `avg_delay_ms`, `throughput_kbps`
- `flowmonitor_lost_packets_diagnostic`
- `animation_enabled`, `status`

You may add columns, but do not silently drop these core fields. Use a stable CSV writer, not manually concatenated strings without CSV escaping.

## 6. Aggregate calculation

For each `protocol × num_nodes × speed`, summarize the three repetitions:

- `n` (expected 3);
- arithmetic mean of the per-run PDR percentages;
- mean of per-run average delay values;
- mean of per-run throughput values;
- mean of per-run packet-loss counts/percentages;
- sample standard deviation (n−1 denominator) for each metric.

Because each run uses the same planned number of flows and traffic window, mean per-run metrics are useful for describing replicate variability. Also provide aggregate packet counters. Do not average flow-level PDRs without weighting by their transmitted packet counts.

## 7. Validation checks

For each valid run:

- protocol is AODV or DSDV;
- node count is 10 or 20;
- speed is 5, 10 or 20 m/s;
- run ID is 1, 2 or 3;
- TX > 0 and RX is available;
- `0 <= PDR <= 100`;
- delay and throughput are finite and non-negative when defined;
- packet loss is non-negative;
- measurement duration matches configured app window;
- FlowMonitor XML and summary are present and parseable;
- app-flow filter selects only the expected app ports;
- one row per unique run key;
- the final matrix has exactly 36 valid run rows before final aggregation;
- paired mobility validation has an entry per `(nodes, speed, run)` pair.

If a run produces no received packets, preserve the raw data and mark it invalid/failed for final aggregate; diagnose connectivity/application setup instead of assigning a fabricated delay. A scenario with genuine zero reception can be a scientifically meaningful outcome only when it is a valid simulation—not a broken app or flow classifier—and the metric is represented as undefined where appropriate with the limitation discussed.
