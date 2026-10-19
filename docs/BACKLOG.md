# Product backlog

MetricPact already ships governed metric selection, SQL disclosure, ambiguity handling,
scan limits, reconciliation evidence, and join-grain rejection. Ideas below are deliberately
marked as planned, not complete.

| Priority | Feature | User problem and behavior | Dependencies | Success test | Risks / trade-offs | Status |
|---|---|---|---|---|---|---|
| P0 | Fiscal-calendar semantics | Calendar queries can misstate fiscal performance. Add governed calendars and require one when wording is ambiguous. | Calendar registry | Fiscal benchmark has zero boundary errors. | More clarification prompts. | Planned |
| P0 | Metric-definition compare | Teams use conflicting definitions. Show both formulas, owners, and side-by-side results before selection. | Versioned metric catalog | 100% of known collisions surface before execution. | Can slow simple queries. | Planned |
| P1 | Row-level policy preview | Analysts cannot see why totals differ. Explain applied access filters without exposing restricted values. | Identity/policy adapter | No forbidden row is returned in adversarial tests. | Explanations can leak policy shape. | Planned |
| P1 | Semantic drift alarms | Schema changes silently invalidate metrics. Diff lineage and quarantine affected metrics. | Warehouse metadata | Breaking fixture blocks certification. | False positives during migrations. | Planned |
| P2 | Certified saved questions | Repeated decisions need stable artifacts. Pin question, plan, semantic version and evidence hash. | Durable store | Replays are byte-for-byte reproducible. | Stale answers may look current. | Planned |
| P2 | Benchmark contamination guard | Curated prompts can overstate accuracy. Version hidden paraphrases and report subgroup results. | Evaluation registry | Holdout score remains within 5 points. | More maintenance and slower releases. | Planned |
| P3 | Anomaly explanation | Users need drivers, not only totals. Rank governed segment contributions with uncertainty. | Statistical module | Synthetic planted driver ranks first. | Correlation may be mistaken for causation. | Planned |
