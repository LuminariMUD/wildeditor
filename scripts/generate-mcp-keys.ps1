#!/usr/bin/env pwsh
param(
    [string]$Repository = $env:GITHUB_REPOSITORY
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "gh is required"
}

function New-ServerSecret {
    $bytes = New-Object byte[] 32
    [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    return ([BitConverter]::ToString($bytes)).Replace("-", "").ToLowerInvariant()
}

function Set-GitHubSecret {
    param([string]$Name, [string]$Value)

    $arguments = @("secret", "set", $Name)
    if ($Repository) {
        $arguments += @("--repo", $Repository)
    }
    $Value | & gh @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to set $Name"
    }
}

& gh auth status *> $null
if ($LASTEXITCODE -ne 0) {
    throw "gh is not authenticated"
}

Set-GitHubSecret "WILDEDITOR_MCP_KEY" (New-ServerSecret)
Set-GitHubSecret "WILDEDITOR_BACKEND_SERVICE_KEY" (New-ServerSecret)
Set-GitHubSecret "WILDEDITOR_REDIS_PASSWORD" (New-ServerSecret)

Write-Host "Installed separated MCP, backend-service, and Redis secrets without displaying them."
