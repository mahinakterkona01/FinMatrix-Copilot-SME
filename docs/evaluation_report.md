# FinMatrix Copilot â€” Evaluation Report

**Team Name:** FinMatrixDUO
**Project:** FinMatrix Copilot
**Competition:** Shenzhen FinTechathon 2026 â€” International Track
**Theme:** AI as a Financial Participant

## 1. Purpose

We are developing FinMatrix Copilot to help small and medium-sized businesses understand financial information, explore possible scenarios, and access AI-assisted financial guidance.

This report describes the evaluation approach used in the project, the main areas we consider important, and the limitations that affect how results should be interpreted.

Our goal is to evaluate not only whether the application runs, but also whether its calculations, data handling, retrieval workflows, and AI-assisted features behave as expected.

## 2. Evaluation Scope

The project includes several areas that require separate evaluation.

| Evaluation Area | What We Examine |

|---|---|
| Financial calculations | Whether supported calculations produce expected results for known inputs. |
| Data normalization | How the application handles missing fields, inconsistent formats, and invalid values. |
| Forecasting | Whether the configured forecasting workflow produces valid predictions and is evaluated using an appropriate time-based methodology. |
| Scenario analysis | Whether changing assumptions produces the expected changes in calculated outcomes. |
| Document retrieval | Whether retrieved passages are relevant to the user's query and provide useful source context. |
| AI-assisted responses | Whether responses stay within the available evidence and avoid unsupported financial claims. |
| Safety checks | Whether selected suspicious inputs and unauthorized action attempts are handled as expected by implemented checks. |
| Reporting | Whether generated reports reflect the results available in the application. |
| Error handling | Whether unavailable models, invalid inputs, and provider failures produce appropriate failure states. |

The scope of each evaluation depends on the functionality implemented and the test cases available.

## 3. Testing Approach

We use automated regression tests and targeted evaluation workflows to check the application's behavior during development.

Our testing approach focuses on the following principles:

- Use known inputs and expected outputs to check deterministic financial calculations.
- Include edge cases such as missing values, invalid formats, and unexpected inputs.
- Check error handling rather than assuming every model or external service will always be available.
- Evaluate forecasting with chronological splits where appropriate to reduce the risk of future-data leakage.
- Inspect retrieval results for relevance instead of assuming every returned passage supports the answer.
- Treat AI-generated explanations as outputs to evaluate, not as ground truth.
- Re-run relevant regression tests after changes to reduce the risk of breaking existing functionality.

Automated tests cover the cases explicitly included in the test suite. Additional testing is necessary before relying on the application in a real business environment.

## 4. Financial Calculation Evaluation

Financial calculations are an important part of FinMatrix Copilot because incorrect numerical results can lead to misleading conclusions.

Our evaluation approach checks supported calculations against expected results for controlled inputs. Where applicable, we also consider boundary conditions, invalid inputs, missing information, and changes to scenario assumptions.

For financial results to be meaningful, the application must handle input fields and units consistently. Even a mathematically correct calculation can produce a misleading result if the original records are incomplete or incorrectly labelled.

A completed evaluation should record the test case, expected result, actual result, and pass or fail status.

## 5. Forecasting Evaluation

Forecasting is evaluated separately from historical financial summaries and scenario calculations.

Where a forecasting model is available, evaluation should use a time-aware methodology that respects the order of observations. Training on information that would not have been available at prediction time can produce misleading performance estimates.

Relevant evaluation measures depend on the prediction target and dataset. Possible measures include MAE and RMSE for numerical forecasts, alongside a comparison against a suitable baseline.

Forecasting metrics should only be reported when the underlying evaluation has actually been executed and its results have been reviewed.

A prediction should not be presented as a guaranteed future outcome. If the model is unavailable, the required inputs are missing, or the output fails validation, the application should communicate that limitation.

## 6. Document Retrieval and AI Evaluation

The retrieval and AI-assisted workflows require evaluation beyond checking whether a response is produced.

Our evaluation approach considers:

- Whether retrieved passages are relevant to the user's question.
- Whether the available source material supports the resulting explanation.
- Whether the system handles irrelevant or insufficient evidence appropriately.
- Whether the response distinguishes available facts from assumptions.
- Whether unsupported financial or policy claims are avoided.
- Whether provider failures are communicated without pretending a successful response was generated.

A retrieval result is not automatically correct or authoritative. Document quality, indexing, retrieval settings, and query wording can all affect the results.

Similarly, a fluent AI response is not proof of factual accuracy. Important financial or policy conclusions require verification against suitable source material.

## 7. Safety and Error Handling

FinMatrix Copilot includes selected safety-related checks, but these should not be interpreted as complete protection against every malicious input or unsafe action.

Relevant evaluation scenarios include invalid input formats, suspicious input patterns, unavailable external services, missing configuration, and attempts to trigger actions outside the supported workflow.

The purpose of these checks is to identify failures and improve handling of known cases. They do not establish that every prompt injection, authorization failure, or security vulnerability has been prevented.

Security-related claims should be supported by the actual test cases and implementation.

## 8. Reporting Results

Evaluation results should be recorded in a reproducible format. For each executed test or experiment, the report should identify:

- The functionality being evaluated.
- The dataset or test inputs used.
- The expected behavior or evaluation metric.
- The observed result.
- The execution date or relevant code version.
- Any known limitations affecting interpretation.

We do not treat an unexecuted test, an intended feature, or a planned experiment as completed evaluation evidence.

Performance figures should be included only when they can be traced to actual execution results and the relevant methodology is documented.

## 9. Limitations

The evaluation has several important limitations.

First, tests cover only the inputs and behaviors represented in the test suite. They cannot establish correctness for every possible financial record or user interaction.

Second, synthetic or demonstration data may not represent the conditions encountered by real businesses.

Third, forecasting and AI performance can vary with the dataset, configuration, model, and evaluation method.

Fourth, document retrieval may return incomplete or irrelevant passages, and language-model responses may contain errors.

Finally, automated regression testing does not replace independent financial validation, privacy review, security assessment, or testing in the intended deployment environment.

## 10. Further Evaluation

Future work may include:

- Evaluation using independently sourced financial datasets.
- Broader testing of financial calculations against independently verified examples.
- Comparisons between forecasting models and appropriate baselines.
- More systematic measurement of retrieval relevance and answer grounding.
- Additional tests for malformed files, edge cases, and security-related failures.
- Usability evaluation with intended SME users.
- Documentation of reproducible evaluation results and known failure cases.

These activities are planned areas for improvement and should not be interpreted as completed experiments unless supporting results are available.

## 11. Conclusion

Evaluation is an ongoing part of developing FinMatrix Copilot. We aim to make the application's financial calculations easier to verify, its limitations clearer to users, and its AI-assisted workflows more useful and reliable.

The current evaluation approach provides a basis for checking implemented functionality, identifying weaknesses, and guiding further development. The application remains a decision-support prototype, and its outputs should be reviewed before being used for consequential financial decisions.

---

**Team:** FinMatrixDUO
**Project:** FinMatrix Copilot
**Document:** Evaluation Report
