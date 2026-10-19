# FinMatrix Copilot — Security Self-Assessment

**Team Name:** FinMatrixDUO  
**Project Name:** FinMatrix Copilot  
**Competition:** Shenzhen FinTechathon 2026 — International Track  
**Theme:** AI as a Financial Participant

## 1. Introduction

FinMatrix Copilot is a Streamlit-based financial decision-support prototype developed to help small and medium-sized businesses explore financial data, perform supported calculations, and access AI-assisted information.

Since financial applications may handle sensitive business information, security and responsible data handling are important parts of the project.

This document summarizes the security considerations we have identified, the safeguards included in the application where implemented, and the areas that require further verification or development.

The assessment reflects the prototype's intended design and known limitations. It is not a certification or a claim that the application has passed an independent security audit.

## 2. Security Scope

Our review focuses on the following areas:

- Uploaded financial data and input validation.
- Handling of API keys and other credentials.
- AI-assisted workflows and untrusted input.
- Document retrieval and generated responses.
- Access control and session handling.
- Error handling and information exposure.
- Testing and deployment configuration.

The level of protection available in each area depends on the current implementation and the environment in which the application runs.

## 3. Identified Risks and Safeguards

| Area | Risk | Safeguard or Required Action |

|---|---|---|
| File uploads | Malformed, unexpectedly large, or incorrectly structured files may cause failures or misleading results. | Validate supported formats, file sizes, required fields, and data types. Verify the implemented limits. |
| Financial inputs | Missing, inconsistent, or incorrectly labelled values may produce incorrect calculations. | Normalize inputs, validate assumptions, and communicate errors or missing information. |
| API credentials | Exposed keys may allow unauthorized use of an external service. | Keep secrets outside committed source code and use environment variables or an appropriate secrets manager. |
| Language-model responses | Generated answers may contain inaccurate or unsupported financial claims. | Use deterministic financial tools where appropriate and require users to review important results. |
| Prompt injection | Untrusted input or retrieved text may attempt to influence AI behavior. | Treat external content as untrusted and enforce application controls independently of model instructions. |
| Document retrieval | Retrieved passages may be irrelevant, incomplete, or misleading. | Inspect source context where available and avoid treating retrieval as proof of correctness. |
| Access control | Unauthorized users may access financial data or protected operations. | Verify authentication, authorization, and access restrictions before public deployment. |
| Session isolation | Data associated with one user may be exposed to another if state is not properly isolated. | Review session behavior and ensure that user-specific data is not unintentionally shared. |
| Error handling | Detailed errors may reveal sensitive information or internal configuration. | Use appropriate user-facing errors and avoid exposing credentials or sensitive records in logs. |
| Report export | Downloaded reports may contain sensitive financial information. | Review report contents and protect access to generated files where applicable. |
| Dependencies | Outdated or vulnerable packages may introduce security weaknesses. | Review dependencies and update them through a controlled process. |
| Deployment | Misconfigured hosting may expose the application or its data. | Review network exposure, authentication, secrets, logging, and hosting configuration. |

The safeguards listed above should be checked against the current code before being described as fully implemented.

## 4. Authentication and Authorization

Authentication identifies a user, while authorization determines which data or operations that user can access.

A public application URL does not automatically provide authentication. Similarly, hiding a control in the interface does not guarantee that the underlying action is protected.

Before using FinMatrix Copilot with multiple users or sensitive business records, the deployment should be reviewed to confirm:

- Whether access is restricted to the intended users.
- Whether protected operations enforce authorization.
- Whether user sessions and financial records remain isolated.
- Whether sign-out and session expiration are handled appropriately.
- Whether administrative or sensitive actions require suitable permissions.

Until these controls have been implemented and verified, the prototype should not be represented as providing production-grade authentication or role-based access control.

See `docs/authentication_setup.md` for the related setup and deployment considerations.

## 5. AI and Retrieval Safety

FinMatrix Copilot may use document retrieval and an optional language-model integration to support financial questions.

These features introduce risks that differ from those associated with ordinary deterministic calculations.

Retrieved documents may contain inaccurate or irrelevant information. A language model may also misunderstand a question, generate unsupported statements, or fail to recognize a malicious instruction.

Our security approach therefore emphasizes the following principles:

- Treat uploaded documents and retrieved passages as untrusted input.
- Do not allow retrieved text to override application-level security controls.
- Keep protected actions separate from unrestricted natural-language instructions.
- Validate inputs and enforce permissions independently of generated responses.
- Avoid presenting generated explanations as verified financial or legal advice.
- Communicate unavailable providers and failed requests accurately.

Pattern-based guardrails can help identify selected suspicious inputs, but they cannot guarantee protection against all prompt-injection attempts or other attacks.

## 6. Data Privacy and Secret Management

Financial records may contain commercially sensitive information. Their use should be limited to what is necessary for the intended workflow.

Before deployment, we need to verify:

- Which financial records are uploaded and processed.
- Whether data is stored temporarily or persistently.
- How temporary files and generated reports are handled.
- Whether any data is sent to an external AI provider.
- What information is included in application logs.
- How credentials are stored and accessed.
- Whether users can access or download data belonging to other users.

Real API keys, passwords, tokens, and private business records must not be committed to the public repository.

Example configuration files should contain placeholders only. Production credentials should be managed through the hosting environment or an appropriate secrets-management mechanism.

When an external model provider is enabled, its data-handling terms and the application's configuration should be reviewed before submitting sensitive financial information.

## 7. Testing and Verification

Security-related checks should be supported by reproducible tests wherever possible.

Relevant test scenarios include:

- Invalid or malformed financial inputs.
- Unexpected file formats and file sizes.
- Missing or incorrect configuration.
- Unavailable external model providers.
- Suspicious inputs handled by implemented guardrails.
- Unauthorized attempts to access protected operations.
- Potential cross-user access to session data.
- Sensitive information appearing in errors, logs, or exported reports.

Automated tests can demonstrate how the application behaves for specific scenarios. They do not establish that every vulnerability has been identified or prevented.

An independent security review would be necessary before making stronger claims about production readiness.

## 8. Current Limitations

The current project is a prototype, and its safeguards should be assessed against the actual code and deployment configuration.

In particular:

- Pattern-based input checks are not comprehensive attack prevention.
- AI-generated answers may be inaccurate.
- Retrieval results may not provide sufficient evidence for a conclusion.
- Authentication and authorization must be verified rather than assumed.
- Automated tests cover defined cases, not every possible attack or failure.
- A successful local demonstration does not establish production-grade security.

These limitations are important when deciding whether the application is suitable for real financial records or public deployment.

## 9. Actions Before Public Deployment

Before making the application available to external users, we should:

1. Verify authentication and authorization requirements.
2. Review file-upload validation and resource limits.
3. Check that secrets and sensitive files are excluded from version control.
4. Inspect logging, error handling, and report exports for unintended data exposure.
5. Verify session isolation and temporary-file handling.
6. Review external AI-provider configuration and data privacy implications.
7. Run the relevant regression and security tests against the final code.
8. Review dependency security and hosting configuration.
9. Document unresolved risks and decide whether additional restrictions are necessary.

## 10. Conclusion

Security is an ongoing consideration in the development of FinMatrix Copilot. Our aim is to make the application's behavior easier to inspect, handle financial data responsibly, and communicate the limits of AI-assisted outputs.

This self-assessment records the risks and verification work relevant to the current prototype. It should be updated as safeguards are implemented, tested, and reviewed.

---

**Team:** FinMatrixDUO  
**Project:** FinMatrix Copilot  
**Document:** Security Self-Assessment
