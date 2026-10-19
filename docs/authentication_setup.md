# FinMatrix Copilot — Authentication and Configuration Setup

**Team Name:** FinMatrixDUO  
**Project Name:** FinMatrix Copilot  
**Competition:** Shenzhen FinTechathon 2026 — International Track  
**Theme:** AI as a Financial Participant

## 1. Purpose

This guide explains how to configure and run FinMatrix Copilot in a local development environment, including the handling of environment variables, optional AI-provider credentials, and Streamlit secrets.

Authentication and application configuration are separate concerns. Configuring an API key allows the application to communicate with an external service; it does not automatically authenticate application users or provide role-based access control.

The exact commands and configuration options should be checked against the current project files before use.

## 2. Prerequisites

Before starting, make sure the development environment has:

- Python installed at a version supported by the project.
- Git installed if cloning the repository.
- Access to the FinMatrix Copilot source code.
- The project's required Python packages.
- Any external-service credentials required for the features you intend to use.

## 3. Local Setup

Open PowerShell in the project directory.

```powershell
cd C:\FinMatrix_Copilot
```

Activate the existing virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

If the virtual environment does not exist, create it:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies from the project's dependency file. For example, if the repository uses `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

Start the Streamlit application using the entry-point file configured in the project. If `app.py` is the current entry point:

```powershell
streamlit run app.py
```

If the project uses a different entry point or dependency-management method, follow the repository's current configuration instead.

## 4. Environment Variables and API Keys

Some AI-assisted features may require an API key from an external provider.

Store credentials in environment variables or an appropriate secrets manager instead of writing real credentials directly into source code.

For a temporary PowerShell session, an environment variable can be set as follows:

```powershell
$env:OPENAI_API_KEY = "YOUR_API_KEY"
```

Replace the placeholder with your own credential when configuring your local environment. Do not include a real key in documentation, screenshots, source files, or public commits.

The variable name above is an example. Confirm the exact variable name expected by the current implementation before using it.

To remove the variable from the current PowerShell session:

```powershell
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
```

If an external provider is not configured or is unavailable, the application should communicate the failure clearly rather than implying that a live AI request succeeded.

## 5. Streamlit Secrets

Streamlit supports application secrets through a `secrets.toml` file. When the project uses this mechanism, a local configuration file can be placed at:

```text
.streamlit/secrets.toml
```

An example configuration might look like this:

```toml
# Example only — use only the settings required by the application.
OPENAI_API_KEY = "YOUR_API_KEY"
```

This example is not a guarantee that the current application reads its credentials from Streamlit secrets. Check the implementation before selecting a configuration method.

For sharing the repository, use a template containing placeholders rather than real credentials. Keep actual secrets out of version control and verify that local secret files are excluded by `.gitignore`.

## 6. Authentication and Access Control

Application authentication determines who can access the system. Authorization determines what an authenticated user is permitted to do.

Neither should be assumed to exist simply because the application runs in Streamlit or uses an API key.

Before deploying FinMatrix Copilot for external users, verify:

- Whether access to the application is restricted.
- Whether protected operations check authorization.
- Whether session data is isolated between users.
- Whether sensitive records and downloads are protected.
- Whether session expiration and sign-out are handled appropriately.
- Whether the hosting platform provides any additional access restrictions.

If these controls are not implemented and tested, treat the application as a development prototype rather than a secure multi-user financial service.

## 7. Deployment Considerations

Before deploying the application:

1. Configure credentials through the hosting platform's supported secrets mechanism.
2. Never commit `.env`, real `secrets.toml` files, passwords, or API tokens.
3. Verify the application's expected environment-variable names.
4. Confirm that external AI services are enabled and configured intentionally.
5. Review the data sent to external providers.
6. Restrict access if the application processes confidential financial records.
7. Test error handling when credentials are missing or a provider is unavailable.
8. Review logs and exported reports for accidental disclosure of sensitive information.

A successful deployment does not, by itself, establish that the application has production-grade authentication or security.

## 8. Troubleshooting

**The application cannot find an API key**.

- Check the credential variable name expected by the code.
- Confirm that the variable is available in the same environment that starts Streamlit.
- Restart the application after changing configuration where necessary.
- Never print the complete key to debug the issue.

**The external AI provider returns an error**.

- Check provider availability, account limits, and credential configuration.
- Review the application's error message without exposing secrets.
- Confirm whether the affected feature requires an external service.

**The application starts but authentication is unavailable**.

- Confirm whether authentication has actually been implemented.
- Check whether access restrictions are configured by the hosting platform.
- Do not treat a hidden page or UI control as an access-control mechanism.

**The application works locally but not after deployment.**

- Compare dependency versions and configuration.
- Verify that required secrets are configured in the hosting environment.
- Review the deployment logs while avoiding disclosure of sensitive information.

## 9. Related Documentation

- `docs/architecture.md` — system components and data flow.
- `docs/security_self_assessment.md` — security considerations and verification requirements.
- `docs/known_risks.md` — known risks and limitations.
- `docs/llm_integration.md` — AI-provider integration considerations.

## 10. Final Note

This guide describes a configuration approach, not a claim that every option is already implemented. Before publishing it as definitive setup documentation, Team FinMatrixDUO should verify the actual entry point, dependency file, credential names, and supported authentication mechanisms in the repository.

**Team:** FinMatrixDUO  
**Project:** FinMatrix Copilot
