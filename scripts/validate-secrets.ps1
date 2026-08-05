#!/usr/bin/env pwsh
param(
    [string]$DatabaseUrl = $env:MYSQL_DATABASE_URL,
    [string]$BackendServiceKey = $env:WILDEDITOR_BACKEND_SERVICE_KEY,
    [string]$McpKey = $env:WILDEDITOR_MCP_KEY,
    [string]$RedisPassword = $env:WILDEDITOR_REDIS_PASSWORD,
    [string]$ProductionHost = $env:PRODUCTION_HOST,
    [string]$ProductionUser = $env:PRODUCTION_USER
)

$ErrorActionPreference = "Stop"
$errors = @()

if (-not $DatabaseUrl) {
    $errors += "MYSQL_DATABASE_URL is not set"
} elseif ($DatabaseUrl -notmatch "^mysql\+pymysql://") {
    $errors += "MYSQL_DATABASE_URL must start with mysql+pymysql://"
}

foreach ($secret in @(
    @{ Name = "WILDEDITOR_BACKEND_SERVICE_KEY"; Value = $BackendServiceKey },
    @{ Name = "WILDEDITOR_MCP_KEY"; Value = $McpKey },
    @{ Name = "WILDEDITOR_REDIS_PASSWORD"; Value = $RedisPassword }
)) {
    if (-not $secret.Value) {
        $errors += "$($secret.Name) is not set"
    } elseif ($secret.Value.Length -lt 32) {
        $errors += "$($secret.Name) must contain at least 32 characters"
    } elseif ($secret.Value -match "your_|replace|example|change") {
        $errors += "$($secret.Name) contains placeholder text"
    }
}

if (-not $ProductionHost) {
    $errors += "PRODUCTION_HOST is not set"
}
if (-not $ProductionUser) {
    $errors += "PRODUCTION_USER is not set"
}

if ($errors.Count -gt 0) {
    foreach ($validationError in $errors) {
        Write-Error $validationError
    }
    exit 1
}

Write-Host "Required deployment values are present and structurally valid."
Write-Host "No credential values or previews were displayed."
