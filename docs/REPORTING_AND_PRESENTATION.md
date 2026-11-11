# Technical Report, AAT Documentation and Presentation

## 1. Required final artifacts

Create:

- `reports/technical_report.md` (self-contained report; optionally export to PDF only if the toolchain is already available and useful);
- `reports/demo_script.md` (five-minute presentation/demo script);
- a slide outline in `reports/presentation_outline.md`;
- final plot/data files under `results/plots/` and `results/processed/`.

Do not make a PDF a blocker if Markdown report and slide outline are complete. Do not claim a PDF exists until actually generated.

## 2. Technical report outline

1. Title, team/member placeholders only where actual names are not supplied.
2. Abstract: objective, methodology, evaluated parameter ranges, actual completed runs, strongest measured findings. Write after experiments.
3. Introduction: MANET concept and routing challenge.
4. Problem statement and research question.
5. Objectives and scope.
6. Background: AODV (reactive) and DSDV (proactive), explained accurately.
7. Simulation architecture: NS-3.45, 802.11 ad-hoc, Random Waypoint, UDP, FlowMonitor, NetAnim.
8. Experimental setup: all physical/traffic parameters, seed/run approach, 36-run matrix.
9. Metric definitions and exact equations/units.
10. Reproducibility/fairness method: matched runs, stream assignment, mobility trace validation.
11. Results: full aggregate table and four plots; include actual numbers only.
12. Discussion: explain observed patterns, exceptions, variation across three runs, possible model-level causes without overclaiming.
13. Threats to validity/limitations: simplified propagation and mobility, three repetitions, simulated vs real network, FlowMonitor IP-layer semantics, sensitivity to parameters.
14. Conclusion: answer research question based solely on results.
15. Future work (clearly outside current scope, e.g. OLSR or energy analysis—not implemented claims).
16. References: official NS-3.45 documentation and any additional sources actually used.
17. Reproducibility appendix: exact build/run/analysis commands and file map.

## 3. Presentation outline (8–10 slides)

1. Title and team.
2. Problem and why MANET routing matters.
3. AODV vs DSDV conceptual distinction.
4. Proposed simulation architecture.
5. Topology/mobility and experimental variables.
6. Metrics and formulas.
7. NetAnim AODV/DSDV demo screenshots or live XML viewer.
8. Results: PDR + delay.
9. Results: throughput + packet loss; interpretation.
10. Conclusion, limitations and future work.

## 4. Evidence discipline

- Use figures directly generated from CSV/plot scripts; never manually alter the plotted data.
- Every graph specifies units, protocol, node-count distinction, and mobility speeds.
- State the exact number of completed valid runs. If less than 36, call the analysis partial.
- Do not conclude “AODV is better” or “DSDV is better” generally. Say which protocol did what under a particular tested condition and metric.
- Include unexpected or inconclusive results. Explain uncertainty, not hide it.
- Explain the difference between sent-minus-received packet loss and FlowMonitor's `lostPackets` diagnostic field.
- Keep report language clear enough for a networking course viva; do not use unexplained jargon.
