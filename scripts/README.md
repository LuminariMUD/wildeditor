# Scripts Directory

This directory contains utility scripts for the Wildeditor project.

## Running Scripts

Run repository scripts from the project root so relative paths and generated
output stay in the expected location:

```bash
./scripts/diagnose_production_ai.sh
```

```powershell
.\scripts\validate-secrets.ps1
```

## Script Groups

- `setup-server.sh`, `debug-path.sh`, `diagnose_production_ai.sh`, and
  `fix_ollama_network.sh` support server setup and diagnostics.
- `setup_github_secrets.sh`, `generate-mcp-keys.ps1`, `validate-secrets.ps1`,
  and `setup-copilot-mcp.ps1` support credentials and MCP tooling.
- `setup_openai_from_luminari.sh` configures the production MCP environment.
- `database-setup*.sql`, `setup-supabase-schema.sql`,
  `fix_region_hints_table.sql`, and `path_data_queries.sql` contain database
  setup, repair, and diagnostic queries.
- `github-secrets-setup.txt` and `ssh-port-forward-mcp.txt` contain operational
  command references.

## Server Setup

### `setup-server.sh`

Automated server setup script for preparing a Ubuntu/Debian server for Docker deployment.

**Usage:**
```bash
# Copy to your server and run
scp scripts/setup-server.sh user@your-server:/tmp/
ssh user@your-server
chmod +x /tmp/setup-server.sh
/tmp/setup-server.sh
```

**What it does:**
- Installs Docker if not present
- Adds the current user to the docker group
- Creates required application directories
- Sets up basic firewall rules
- Tests the Docker installation

**Requirements:**
- Ubuntu/Debian server
- User with sudo access
- Internet connection

See `docs/backend/SERVER_SETUP.md` for detailed server setup instructions.

## Contributing

When adding new scripts:
1. Make them executable: `chmod +x script-name.sh`
2. Add proper error handling with `set -e`
3. Include usage documentation in this README
4. Test on a clean environment before committing
