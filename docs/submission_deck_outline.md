# FinMatrix — Final Presentation Deck Outline

**Suggested duration:** 7–9 minutes, subject to the official event limit.

## Slide 1 — Title and team (30 sec)
FinMatrix: SME Financial Decision-Support Copilot. Add the confirmed team name and member details.

## Slide 2 — Problem and target users (45 sec)
Explain the practical challenge of reviewing cash-flow records, exploring scenarios, and locating relevant financing-policy information. Avoid unsupported market-size statistics.

## Slide 3 — Proposed solution (45 sec)
Present the current prototype: data upload, deterministic summaries, scenario analysis, configured forecasting, local policy retrieval, guardrail checks, and report export.

## Slide 4 — Architecture (60 sec)
Show Streamlit UI -> data validation/normalization -> financial tools and configured model/retrieval modules -> guardrails/permission helpers -> report output. Clearly mark prototype components and trust boundaries.

## Slide 5 — Live demo (90?120 sec)
Use `docs/demo_script.md`. Show actual outputs from the running application; do not use mock metrics as if they were measured.

## Slide 6 — Evaluation evidence (60 sec)
Report the local automated test results and distinguish them from model validation. If presenting forecasting metrics, identify the dataset, target, chronological split, baseline, metric, and synthetic/historical-data limitation.

## Slide 7 — Security and responsible use (45 sec)
Explain fixed-pattern guardrails, selected permission tests, human-approval design, known limitations, and the need for an app-wide authorization review.

## Slide 8 — Differentiation and current gap (45 sec)
Describe the implemented workflow and the research/evaluation gap honestly. Do not claim novelty or superiority over commercial products without a documented comparison.

## Slide 9 — Roadmap and closing (30 sec)
Priorities: labelled retrieval benchmark, consented real-world SME evaluation, security-path audit, and deployment hardening.

## Before submission
- Verify official track requirements and permitted format.
- Add only confirmed team details.
- Replace all placeholders with real screenshots/results.
- Check that every quantitative claim matches a saved evaluation artifact.
- Keep the final deck within the official duration and slide/file constraints.
