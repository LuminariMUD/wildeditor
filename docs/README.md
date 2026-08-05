# Wildeditor documentation

This directory contains the maintained documentation for the current repository. Start with the root [README](../README.md) for a project overview.

## Guides

| Document | Use it for |
| --- | --- |
| [Architecture](architecture.md) | Service ownership, data flow, boundaries, and current limitations |
| [Development](development.md) | Toolchains, installation, local startup, and development workflow |
| [Configuration](configuration.md) | Environment variables, credentials, CORS, and authentication behavior |
| [API](api.md) | REST route groups, MCP endpoints, chat endpoints, and contract rules |
| [Domain model](domain-model.md) | Coordinates, region/path types, spatial persistence, descriptions, and hints |
| [Deployment](deployment.md) | Supported CI/CD paths, images, required secrets, and release verification |
| [Testing](testing.md) | Meaningful local suites, CI gates, and external probes |
| [Operations](operations.md) | Health checks, logs, backups, recovery, and troubleshooting |
| [User guide](user-guide.md) | Editor tools, staging changes, saving, and AI-assisted workflows |

## Decisions and plans

- [`adr/`](adr/README.md) records accepted architectural decisions. ADRs remain in place because their history explains the current design.
- [`ongoing-projects/`](ongoing-projects/) contains active, proposed work. A plan is not a claim that its target architecture has been implemented.
- [`archive/`](archive/README.md) contains superseded plans, historical status reports, completed migrations, one-off fixes, and replaced guides.

## Sources of truth

When documentation and implementation disagree, use this order and fix the documentation in the same change:

1. Application source, schemas, and models
2. Package manifests and lockfiles
3. New database migrations beside the owning datastore
4. Service Dockerfiles
5. `.github/workflows/`
6. Maintained documents in this directory

Root deployment files, root `tests/`, and archived material may describe experiments or older runtime arrangements. Do not treat them as authoritative without verifying the current code.

## Documentation conventions

- Keep one canonical guide per topic and link to it instead of duplicating instructions.
- Use repository-relative links and commands that run from the documented directory.
- Name the source file or workflow behind operational claims.
- Distinguish current behavior, known limitations, and proposed work.
- Never include real credentials, private host details, or copied production output.
- Move replaced historical material to the archive instead of leaving competing active guides.
