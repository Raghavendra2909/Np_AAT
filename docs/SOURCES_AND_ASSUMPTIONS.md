# Sources and Verified/To-Verify Assumptions

## Official sources to use first

1. **NS-3.45 Installation Guide** — build system, prerequisites and version-specific commands: https://www2.nsnam.org/docs/release/3.45/installation/singlehtml/index.html
2. **NS-3.45 Quick Start/Tutorial** — build and running examples: https://www.nsnam.org/docs/release/3.45/tutorial/html/quick-start.html
3. **NS-3.45 Model Library PDF** — AODV, DSDV, FlowMonitor, mobility, Wi-Fi and NetAnim module documentation: https://www.nsnam.org/docs/release/3.45/models/ns-3-model-library.pdf
4. **NS-3 MANET comparison example source** — `manet-routing-compare.cc`: https://www.nsnam.org/doxygen/dc/d7a/manet-routing-compare_8cc_source.html
5. **FlowMonitor documentation** — statistics and the warning about packets still queued below IP at simulation end: https://www.nsnam.org/docs/release/3.45/models/html/flow-monitor.html
6. **Cursor Rules documentation** — root `AGENTS.md` supported; `.cursor/rules` project rules use `.mdc`: https://cursor.com/docs/rules

## Useful facts confirmed from official references

- NS-3.45 uses the CMake-based `./ns3` wrapper. The Waf system belongs to older NS-3 versions; do not use Waf commands for this release.
- The official MANET comparison example supports AODV, DSDV (as well as other protocols outside our frozen scope), Random Waypoint mobility, ad-hoc Wi-Fi, configurable node count/speed, CSV reception output, and optional FlowMonitor-related code. Use the **local NS-3.45 version** as API truth; current Doxygen pages may track a newer release.
- FlowMonitor records IP-level flow metrics and exports XML. The byte accounting includes IP-level bytes, excluding layer-2 headers.
- FlowMonitor's `lostPackets` is a diagnostic based on packets it has not tracked/seen within its timeout and may differ from `txPackets - rxPackets`. Packets still queued below IP at simulator end may be marked lost; stop apps before simulation end and leave cleanup time.
- Cursor supports a project-root `AGENTS.md`; `.cursor/rules` project-specific rules use `.mdc`, not plain `.md`.

## Project parameter assumptions to pilot-test

Initial candidate values are documented in `PROJECT_SPEC.md` and `SIMULATION_DESIGN.md`. They are not research findings. The implementer must validate topology connectivity, multi-hop behavior and mobility effects using pilot runs, then freeze the chosen setup before the 36-run campaign. Do not alter the configuration after some final runs are completed without rerunning all affected conditions.

## User-provided/course material

The user's supplied `NS3_Basics.pdf` covers the generic NS-3 script structure, helpers for nodes/Wi-Fi/mobility, tracing, NetAnim and FlowMonitor. The supplied `NS3 Project Ideas.pdf` lists MANET-related topics. Those files support course alignment but do not supersede the release-specific official 3.45 documentation about build commands or APIs.
