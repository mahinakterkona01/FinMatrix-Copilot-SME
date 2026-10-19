# FinMatrix — Demo Script and Verification Checklist

**Target duration:** 4–5 minutes. Use synthetic/demo data only.

## 1. Introduction (20 seconds)

Introduce FinMatrix as a Streamlit-based financial decision-support prototype for SMEs. Explain that it aims to make cash-flow information and scenarios easier to inspect.

## 2. Upload and inspect data (45 seconds)

- Open the application.
- Upload a prepared CSV with clearly labelled synthetic/demo records.
- Show detected columns, date coverage, and basic cash-flow summaries.
- Point out that outputs depend on the uploaded data quality.

## 3. Dashboard and scenario analysis (60 seconds)

- Show inflow, outflow, net cash flow, and trend charts.
- Change a scenario assumption if the simulator supports it.
- Explain that scenario outputs are hypothetical, not guaranteed predictions.

## 4. Forecasting (45 seconds)

- Choose a forecast horizon and click Generate forecast.
- If valid predictions are returned, show the plot and output table.
- If the model is unavailable or rejects the data, show the honest warning instead; do not fabricate a successful result.

## 5. Policy retrieval and safety (60 seconds)

- Search a question supported by a document in the configured local corpus.
- Inspect the returned source and snippet before describing it.
- Demonstrate a benign query and selected guardrail test cases.
- State that retrieval quality and regex guardrails have known limitations.

## 6. Export and close (30 seconds)

- Open the report exporter and download a report.
- Summarize the prototype's current scope and the need for independent real-world validation.

## Pre-recording checklist

- [ ] Use synthetic or authorized demo data only.
- [ ] Remove credentials, personal data, and private customer records.
- [ ] Confirm the app starts and each demonstrated page opens.
- [ ] Confirm forecast output or capture the honest unavailable state.
- [ ] Verify every policy source shown in the recording.
- [ ] Ensure no unverified metric or external-validation claim appears.
- [ ] Check the recording duration against the competition's current rules.
