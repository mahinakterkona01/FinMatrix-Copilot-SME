# FinMatrix Copilot — Competition Requirements Matrix

**Team Name:** FinMatrixDUO\
**Project Name:** FinMatrix Copilot\
**Competition:** Shenzhen FinTechathon 2026 — International Track\
**Theme:** AI as a Financial Participant

## 1. Purpose

This document maps the competition-related requirements to the scope and development status of FinMatrix Copilot.

We created this matrix to keep track of the project's main deliverables, identify areas that still need attention, and make sure our submission is supported by the actual implementation and available evidence.

A feature is not considered complete simply because it is described in the documentation. Its status should reflect the current code, test results, and submission materials.

## 2. Functional Requirements

| Requirement | FinMatrix Copilot Approach | Status |

|---|---|---|
| Address a real financial problem | Help SMEs examine financial records, explore scenarios, and understand financial information. | Implemented scope; validate against the current application |
| Financial data processing | Normalize and validate supported financial inputs before analysis. | Verify against current code |
| Financial calculations | Use Python-based financial tools for supported calculations. | Implemented scope; verify with regression tests |
| Cash-flow analysis | Provide relevant analysis where supported by the current application and input data. | Verify current workflow |
| Scenario analysis | Allow users to examine the effects of supported changes in assumptions. | Verify current workflow |
| Forecasting | Use the configured forecasting implementation when valid predictions are available. | Configuration-dependent |
| Document retrieval | Search the configured document collection for potentially relevant information. | Configuration-dependent |
| AI-assisted interaction | Use supported Copilot logic and an optional language-model integration. | Provider- and configuration-dependent |
| Report generation | Generate downloadable reports from supported results. | Verify current workflow |
| Safe error handling | Communicate invalid inputs, unavailable models, and other supported failure states. | Verify through tests |

## 3. Technical and Security Requirements

| Requirement | Planned or Existing Approach | Status |

|---|---|---|
| Clear system architecture | Document the main modules and data flow in `docs/architecture.md`. | Documentation prepared; verify against code |
| Reproducible setup | Maintain dependency and configuration instructions. | Verify setup on a clean environment |
| Automated testing | Use Pytest for implemented functionality and regression checks. | Tests exist; record the final test result |
| Evaluation methodology | Document calculation, forecasting, retrieval, and AI evaluation approaches. | Evaluation documentation prepared; verify evidence |
| Authentication | Review application-level and hosting-platform access controls. | Must be verified against the deployed application |
| Authorization | Enforce permissions for protected operations where required. | Must be verified |
| Secret management | Keep credentials out of source control and use suitable environment or hosting secrets. | Verify repository and deployment configuration |
| File handling | Validate uploaded files and relevant input limits. | Verify implementation and tests |
| Known risks | Document current limitations and risks in `docs/known_risks.md`. | Documentation prepared; review against implementation |
| Security self-assessment | Record implemented safeguards, limitations, and outstanding concerns. | Documentation prepared; verify evidence |

## 4. Competition Submission Deliverables

The following items should be checked against the official rules for the selected competition track and the latest submission instructions.

| Deliverable | FinMatrix Copilot Material | Status |

|---|---|---|
| Project source code | GitHub repository | Verify repository completeness and access |
| Architecture and core design | `docs/architecture.md` and relevant source modules | Review before submission |
| Security design and risk disclosure | `docs/security_self_assessment.md` and `docs/known_risks.md` | Review before submission |
| Setup instructions | `README.md` and relevant setup documentation | Verify using a clean environment |
| Evaluation evidence | `docs/evaluation_report.md`, test output, and reproducible experiment results | Final evidence required |
| Presentation deck | Competition submission slides | Prepare and review |
| Demo video, if required or useful | Recorded walkthrough of the working application | Optional unless official rules say otherwise |
| Demonstration instructions | `docs/demo_script.md` or equivalent demo notes | Prepare and verify |
| Sandbox logs or other required evidence | Actual logs and artifacts from the required workflow | Confirm the official requirement and provide real evidence |
| Public deployment, if required | Working deployed application and access instructions | Verify availability and access restrictions |

## 5. Implementation Status Definitions

Use the following labels consistently across the project:

- **Implemented:** The functionality exists in the current code and has been checked against its intended behavior.
- **Partial:** Some functionality exists, but important requirements, safeguards, or validation remain incomplete.
- **Configuration-dependent:** The feature requires a configured model, provider, dataset, document collection, or other external dependency.
- **Pending:** The functionality or deliverable has not yet been completed.
- **Needs verification:** The documentation or code indicates a possible implementation, but sufficient evidence has not yet been reviewed.

These labels should be updated as the project changes. A successful unit test alone does not establish that an entire feature is production-ready.

## 6. Remaining Verification

Before final submission, we need to ensure that:

1. Every requirement is matched to the corresponding implemented feature or submission artifact.
2. Configuration-dependent features work in the intended demonstration environment.
3. Automated test results are recorded from the final code version.
4. Evaluation claims are supported by reproducible results.
5. Authentication, authorization, privacy, and secret management are accurately described.
6. Required competition artifacts are present and accessible.
7. The demo demonstrates actual application behavior rather than planned or unavailable features.
8. No credentials, sensitive business records, or unintended local files are included in the public repository.

## 7. Final Review Principle

FinMatrix Copilot is being developed as an AI-assisted financial decision-support prototype. We will describe its capabilities according to the current implementation and support important claims with code, tests, or other verifiable evidence.

This matrix is intended to help our team identify gaps before submission. It is not, by itself, proof that every competition requirement has been satisfied.

---

**Team:** FinMatrixDUO\
**Project:** FinMatrix Copilot\
**Document:** Competition Requirements Matrix
