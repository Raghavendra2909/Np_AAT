# Demo walkthrough

Use this when you present to the professor and a general audience. Stay with the files already generated. Do not rerun the 36 simulations during the demo.

All commands are from the project folder:

```bash
cd ~/Downloads/projects/network-lab
```

## What you are showing

Wireless nodes move around with no access point. They have to forward packets for each other. We compared two routing methods in the NS-3 simulator:

- **AODV** looks for a route only when a node has something to send.
- **DSDV** keeps a route table up to date all the time.

We did not build those algorithms ourselves. NS-3 already has them. We changed the speed (5, 10, 20 m/s) and the crowd (10 or 20 nodes in the same 500 m × 500 m field) and asked four plain questions:

1. What share of sent packets arrived?
2. How long did an arriving packet take?
3. How much data arrived per second?
4. How many packets were lost?

Each setting was repeated 3 times. The graphs show the average of those 3, and a bar showing how much the repeats disagreed.

## Order of the demo (about 5 minutes)

### 1. Say the problem (30 seconds)

“These nodes move and have no fixed router. A packet may need several hops. We compare a reactive protocol, AODV, with a proactive protocol, DSDV.”

You do not need a command for this slide. The title is the project title.

### 2. Show that the experiment is real (45 seconds)

Open the ledger so the audience sees 36 finished runs, not a made-up table:

```bash
less results/experiment_status.csv
```

Say: “There are 36 rows, one for every combination of protocol, node count, speed, and repeat. The status column is PASS.”

Press `q` to leave `less`.

### 3. Show one raw result folder (45 seconds)

```bash
ls results/raw/protocol_aodv/nodes_10/speed_20/run_1/
column -s, -t results/raw/protocol_aodv/nodes_10/speed_20/run_1/summary.csv | less -S
```

Say what the important columns mean. You do not need to read every column.

| Column | Say this |
|---|---|
| `protocol`, `num_nodes`, `node_speed_mps`, `run` | Which case this file is. |
| `tx_packets` | How many application packets the three senders transmitted. |
| `rx_packets` | How many of those the receivers got. |
| `pdr_percent` | `100 × received / sent`. Higher means more packets arrived. |
| `avg_delay_ms` | Average travel time of packets that arrived, in milliseconds. Lower means faster. |
| `throughput_kbps` | How much data arrived, in kilobits per second, over the 55 second sending window. |
| `packet_loss_packets` | Sent minus received. Lower means fewer losses. |
| `flowmonitor_lost_packets_diagnostic` | A second loss counter inside the simulator. It can differ slightly from sent-minus-received. The graphs use sent-minus-received. |

The three conversations are only the UDP ports 9000, 9001, and 9002. Routing control packets are listed in `flows.csv` with `selected` equal to 0, and they are not in the percentages.

### 4. Play the animation (about 90 seconds)

On the desktop, not in a text-only SSH session:

```bash
./manet anim aodv --nodes 10 --speed 20 --run 1
```

The window should open that file by itself. Press the **play** triangle.

What to point at:

- **Green S1** sends to **green D1**.
- **Blue S2** sends to **blue D2**.
- **Orange S3** sends to **orange D3**.
- **Gray “relay” nodes** can forward packets. They are not the application senders or receivers.
- Nodes are moving. That movement is why routes break.

Close it, then:

```bash
./manet anim dsdv --nodes 10 --speed 20 --run 1
```

Say: “Same 10 nodes, same 20 m/s, same random run. Only the routing protocol changed. We checked the saved positions: the AODV and DSDV paths match.”

Do not say every flashing packet is application data. The picture also shows routing messages. The numbers in the CSV are the application packets only.

If the window still says to choose a file, the local NetAnim build is out of date. From the project root:

```bash
make -C tools/netanim-netanim-3.109 -j 8
```

Then run `./manet anim` again.

### 5. Explain the four pictures (90 seconds)

Open these files. They are the audience versions of the graphs:

- `results/plots/pdr_vs_speed.png`
- `results/plots/delay_vs_speed.png`
- `results/plots/throughput_vs_speed.png`
- `results/plots/packet_loss_vs_speed.png`

How to read any of them:

- The horizontal axis is speed: walking-fast at 5 m/s, then 10, then 20.
- Blue is AODV. Orange is DSDV.
- A solid line is 10 nodes. A dashed line is 20 nodes in the same field, so the network is more crowded.
- A dot is the average of 3 repeats. The vertical bar is how much those 3 repeats differed. A long bar means “this number jumped around.”

What the measured averages say. Read one or two cells. Do not say one protocol wins everywhere.

**Packets that arrived** (`results/processed/aggregate_mean_std.csv`, column `pdr_percent_mean`):

| Setting | AODV | DSDV |
|---|---:|---:|
| 10 nodes, 5 m/s | 74.5% | 49.7% |
| 10 nodes, 20 m/s | 65.5% | 28.2% |
| 20 nodes, 5 m/s | 88.3% | 66.0% |
| 20 nodes, 20 m/s | 56.0% | 41.1% |

In all 6 settings, AODV delivered a higher share of packets than DSDV. The best cell is AODV with 20 nodes at 5 m/s (88.3%). The worst is DSDV with 10 nodes at 20 m/s (28.2%). Faster movement made delivery worse, especially for DSDV with only 10 nodes.

**Travel time** (`avg_delay_ms_mean`): this does not follow the same story. At 10 nodes and 5 m/s, DSDV’s average delay is about 40 ms and AODV’s is about 57 ms, even though DSDV delivered fewer packets. Several delay bars are very tall, so three repeats are not enough to rank the protocols on delay.

**Data received** follows delivery, because every flow was offered the same rate. When more packets arrive, throughput is higher.

**Lost packets** is the other side of delivery. DSDV with 10 nodes at 20 m/s lost about 1850 packets on average. AODV with 20 nodes at 5 m/s lost about 303.

### 6. Close (30 seconds)

“This is a simulator, not a campus network. The radio model is simple, and we only repeated each setting 3 times. Under these settings AODV delivered more application packets. That does not mean AODV is better for every wireless network.”

## If someone asks where a number came from

1. The graph is drawn from `results/processed/aggregate_mean_std.csv`.
2. That file averages the three rows in `results/processed/all_runs.csv`.
3. Each row in `all_runs.csv` is copied from one `summary.csv` under `results/raw/`.
4. `summary.csv` is computed from `flowmon.xml`, keeping only the three UDP data flows.

You can show that chain without opening the C++ file.
