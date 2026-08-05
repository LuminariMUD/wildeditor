#!/usr/bin/env pwsh

Write-Error @"
Direct public Copilot-to-MCP setup has been retired. Production MCP is bound to
server loopback and is reachable only through the authenticated Wildeditor chat
service. Do not install MCP or backend service keys in a desktop user profile.
"@
exit 1
