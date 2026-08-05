# Security policy

Wildeditor is pre-release software. No released version line currently carries a formal security-support guarantee; security fixes are made on the active development branch as maintainers are able.

## Report a vulnerability privately

Do not open a public issue or discussion for a suspected vulnerability, exposed credential, or exploit.

Use the repository's private vulnerability-reporting flow at [GitHub Security Advisories](https://github.com/LuminariMUD/wildeditor/security/advisories/new) when it is available. If GitHub does not offer that form, contact a repository maintainer privately through the LuminariMUD organization and ask for a secure reporting channel. Do not include exploit details in a public message.

Include, where possible:

- the affected commit, service, route, and configuration;
- reproduction steps using non-production data;
- expected and observed behavior;
- practical impact and required attacker access;
- a minimal proof of concept with secrets removed;
- whether you believe a credential or production system is already exposed.

Maintainers will assess the report and coordinate remediation and disclosure according to severity and availability. This project does not promise a fixed response or remediation time and does not currently operate a bug-bounty program.

## Research boundaries

- Use accounts, data, and infrastructure you own or have explicit permission to test.
- Stop if testing could expose another person's data, degrade availability, or mutate production state.
- Do not use social engineering, denial of service, persistence, or destructive techniques.
- Retain only the minimum evidence needed to describe the issue and transmit it privately.

## Current security posture

Deployment owners must review [configuration](docs/configuration.md) and [architecture](docs/architecture.md) before exposing the system to a network. In particular:

- frontend authentication and backend authorization are not yet aligned end to end;
- a Vite `VITE_*` value is compiled into the browser bundle and cannot be treated as a secret;
- chat routes do not currently enforce user authentication or session ownership;
- MCP operations use a shared `X-API-Key`, and backend mutations use Bearer API-key checks;
- the backend MCP proxy and several legacy root probes contain credential-like literal defaults that must be treated as exposed and removed before reuse;
- the backend validation-error handler currently logs rejected request bodies;
- development authentication bypasses must never be enabled in public environments;
- CORS, TLS termination, rate limiting, secret storage, database least privilege, monitoring, and backups are deployment responsibilities unless the active configuration proves otherwise.

The proposed authentication remediation is tracked in [the self-hosted authentication migration plan](docs/ongoing-projects/self-hosted-postgres-auth-migration-plan.md). A proposal is not an implemented control.

## Handling secrets

- Keep real values in an approved secret manager or deployment platform, not Git, Markdown, command histories, URLs, screenshots, fixtures, or logs.
- Use distinct, randomly generated credentials per environment and trust boundary.
- Rotate any credential that may have appeared in repository history, archived documentation, logs, or a browser bundle; deleting or redacting the current file does not remove Git history or deployed artifacts.
- Treat frontend environment variables as public configuration.
- Review root diagnostic scripts before use because some target external services and accept privileged credentials.

For non-security defects, use the repository's public issue tracker.
