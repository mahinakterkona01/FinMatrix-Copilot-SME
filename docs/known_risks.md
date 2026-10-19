# FinMatrix Copilot — Known Risks and Limitations

**Team Name:** FinMatrixDUO  
**Project Name:** FinMatrix Copilot  
**Competition:** Shenzhen FinTechathon 2026 — International Track  
**Theme:** AI as a Financial Participant

## 1. Purpose

FinMatrix Copilot is a financial decision-support prototype designed to help small and medium-sized businesses understand their financial data, explore cash-flow scenarios, and access AI-assisted insights.

Financial decisions can have real consequences. This document records the main risks and limitations identified during development, along with the steps needed to reduce them.

The application is intended to support human decision-making, not replace financial professionals or guarantee business outcomes.

## 2. Known Risks

| Risk | Possible Impact | Mitigation |
|---|---|---|
| Incorrect or incomplete input data | Calculations and recommendations may be misleading. | Validate inputs, identify missing values, and communicate assumptions. |
| Forecasting uncertainty | Predicted cash flow may differ from actual business performance. | Present forecasts as estimates and evaluate them against historical or future observations when available. |
| AI-generated inaccuracies | Users may receive incorrect or unsupported explanations. | Use validated calculations for numerical results and encourage users to verify important conclusions. |
| Retrieval errors | Retrieved documents may be irrelevant or may not support the generated answer. | Review retrieved context and distinguish source-based information from general explanations. |
| Prompt injection | Malicious input or document content may influence AI responses. | Apply input safeguards and enforce application-level controls independently of model instructions. |
| External AI service failure | AI-assisted features may become unavailable because of connectivity, provider, or configuration problems. | Handle failures clearly and provide alternative workflows where supported. |
| API cost and rate limits | AI requests may fail or become unavailable when usage limits are reached. | Monitor usage, handle provider errors, and avoid unnecessary requests. |
| Sensitive financial information | Business data may be exposed through storage, logs, exports, or external services. | Minimize data collection, protect credentials, and verify storage and provider configurations. |
| Unauthorized access | Financial records or protected operations may be accessed by unintended users. | Verify authentication, authorization, and session isolation before public deployment. |
| Limited real-world validation | Results on sample or historical data may not generalize to other businesses. | Evaluate the system on additional representative datasets and real-world cases where permission is available. |
| Dependency or deployment problems | Package conflicts or hosting configuration may interrupt the application. | Maintain dependency records, test deployment settings, and check the final release. |

## 3. Financial Decision Limitations

FinMatrix Copilot does not guarantee that a business will maintain sufficient cash, collect outstanding payments, or avoid financial losses.

Forecasting and scenario analysis depend on the quality of the input data, the assumptions used, and the methods implemented. Unexpected expenses, delayed payments, market changes, and other external factors may affect actual results.

Users should review the underlying figures and assumptions before making significant financial decisions.

## 4. AI and Data Limitations

AI-generated explanations may be incomplete or inaccurate. Retrieved information may not cover every relevant condition, and a model may misunderstand the context of a financial question.

The system should not be assumed to have verified a claim merely because it produces a confident answer. Important outputs should be checked against the underlying financial records or reliable sources.

Sensitive business information should not be submitted to an external AI provider unless the relevant configuration, permissions, and data-handling requirements have been reviewed.

## 5. Security and Privacy Limitations

The security of the application depends on its current implementation and deployment environment.

A local demonstration or passing automated tests does not establish that the system is secure for public or multi-user production use. Authentication, authorization, file handling, session isolation, credential management, and logging must be verified before processing sensitive business records.

For further details, see `docs/security_self_assessment.md`.

## 6. Current Validation Limitations

The strength of the project's claims should match the evidence available.

- Automated tests can verify defined scenarios but cannot cover every possible failure.
- Historical evaluation does not guarantee future forecasting accuracy.
- Results from a limited dataset may not generalize to all SMEs.
- A successful demonstration does not establish production readiness.
- AI responses require separate evaluation from deterministic financial calculations.

Any performance metrics reported in the final submission should include the evaluation method, dataset scope, and relevant limitations.

## 7. Planned Improvements

The following improvements are priorities for future development:

1. Expand evaluation using additional representative financial datasets.
2. Track forecasting performance against actual outcomes when suitable data becomes available.
3. Improve validation and handling of incomplete or inconsistent records.
4. Strengthen testing for prompt injection and untrusted document content.
5. Verify access controls and data isolation for multi-user deployment.
6. Improve observability without exposing sensitive information.
7. Document the limitations of each financial calculation and AI-assisted feature.

These items represent improvement goals and should not be interpreted as completed features unless verified in the implementation.

## 8. Conclusion

FinMatrix Copilot aims to make financial information easier to explore and understand while keeping its limitations visible.

By documenting known risks, validating outputs, and maintaining human oversight, Team FinMatrixDUO intends to develop the prototype responsibly and improve its reliability through further testing and evaluation.
