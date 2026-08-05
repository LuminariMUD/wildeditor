# Documentation archive

This directory preserves documentation that is useful as project history but no longer describes the supported runtime.

## Archive policy

Archive a document when its primary purpose is one of the following:

- a completed or abandoned implementation plan;
- a dated status, roadmap, audit, or completion report;
- a one-time migration, incident, networking fix, or deployment checklist;
- a guide superseded by a canonical maintained document;
- a copied design/reference snapshot that is not verified against current source.

Do not use archived commands, endpoints, credentials, hostnames, dependency versions, deployment layouts, or security claims without re-validating them against source, service Dockerfiles, migrations, manifests, and `.github/workflows/`.

## Contents

[`2024-2025/`](2024-2025/) retains the previous documentation tree and service-specific notes from that period. It includes:

- Express-to-FastAPI and frontend API migration material;
- MCP and chat-agent implementation plans, status reports, and design drafts;
- superseded setup, authentication, deployment, CI/CD, and secrets guides;
- one-off networking, Ollama, backend redeployment, and workflow fixes;
- earlier project specifications, roadmaps, changelogs, and copied wilderness context;
- replaced backend, frontend, agent, and MCP guides.

The archive is intentionally not maintained for link correctness. Links inside it may point to old paths or removed external resources. Current documentation starts at [`docs/README.md`](../README.md).

## Security

Archived examples must still use placeholders. If an archived file contains a credential-like value, private key, access token, or sensitive infrastructure detail, redact it and rotate the underlying credential if there is any chance it was real. Git history should be handled with a separate, deliberate incident process when rotation alone is insufficient.
