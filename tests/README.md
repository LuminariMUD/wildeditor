# Repository Tests

This directory contains repository-level integration, deployment, API, and
diagnostic tests. Run them from the repository root so their documented
commands and environment setup remain consistent.

Examples:

```bash
python3 tests/test_mcp_endpoints.py
./tests/test-mcp-networking-fix.sh
```

```powershell
.\tests\test-terrain-bridge-api.ps1
```

Many of these tests require a running backend or MCP server, API credentials,
Docker, Ollama, or access to production infrastructure. Package-specific unit
tests remain alongside their packages under `apps/*/tests/` and
`packages/*/tests/`.
