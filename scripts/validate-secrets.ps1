#!/usr/bin/env powershell
<#
.SYNOPSIS
    Validates GitHub secrets for Wildeditor deployment

.DESCRIPTION
    This script helps validate that your GitHub secrets are properly configured
    before deploying. It checks the format and connectivity of your secrets.
#>

param(
    [string]$DatabaseUrl = $env:MYSQL_DATABASE_URL,
    [string]$ApiKey = $env:WILDEDITOR_API_KEY,
    [string]$ProductionHost = $env:PRODUCTION_HOST,
    [string]$ProductionUser = $env:PRODUCTION_USER
)

Write-Host "🔍 GitHub Secrets Validation Script" -ForegroundColor Green
Write-Host "=" -repeat 50 -ForegroundColor Green
Write-Host ""

$errors = @()
$warnings = @()

# Test Database URL
Write-Host "📊 Testing Database URL..." -ForegroundColor Yellow
if (-not $DatabaseUrl) {
    $errors += "MYSQL_DATABASE_URL environment variable not set"
} elseif ($DatabaseUrl -notmatch "^mysql\+pymysql://") {
    $errors += "Database URL should start with 'mysql+pymysql://'"
} elseif ($DatabaseUrl -match "your_|YOUR_|example\.com") {
    $warnings += "Database URL appears to contain placeholder values"
} else {
    Write-Host "✅ Database URL format looks correct" -ForegroundColor Green
    
    # Parse the URL to check components
    if ($DatabaseUrl -match "mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)") {
        $dbUser = $matches[1]
        $dbHost = $matches[3] 
        $dbPort = $matches[4]
        $dbName = $matches[5]
        
        Write-Host "   Host: $dbHost" -ForegroundColor Gray
        Write-Host "   Port: $dbPort" -ForegroundColor Gray
        Write-Host "   User: $dbUser" -ForegroundColor Gray
        Write-Host "   Database: $dbName" -ForegroundColor Gray
    }
}

# Test API Key
Write-Host ""
Write-Host "🔐 Testing API Key..." -ForegroundColor Yellow
if (-not $ApiKey) {
    $errors += "WILDEDITOR_API_KEY environment variable not set"
    Write-Host "   Generate a new key with:" -ForegroundColor Cyan
    Write-Host "   [System.Convert]::ToBase64String((1..32 | ForEach-Object {Get-Random -Maximum 256}))" -ForegroundColor Cyan
} elseif ($ApiKey.Length -lt 16) {
    $warnings += "API key seems short (less than 16 characters)"
} elseif ($ApiKey -match "your_|YOUR_|example|change") {
    $errors += "API key appears to contain placeholder text"
} else {
    Write-Host "✅ API key format looks correct (${ApiKey.Length} characters)" -ForegroundColor Green
    Write-Host "   Preview: $($ApiKey.Substring(0, [Math]::Min(8, $ApiKey.Length)))..." -ForegroundColor Gray
}

# Test Production Host
Write-Host ""
Write-Host "🌐 Testing Production Host..." -ForegroundColor Yellow
if (-not $ProductionHost) {
    $errors += "PRODUCTION_HOST environment variable not set"
} elseif ($ProductionHost -match "your_|YOUR_|example\.com") {
    $errors += "Production host appears to contain placeholder values"
} else {
    Write-Host "✅ Production host configured: $ProductionHost" -ForegroundColor Green
    
    # Test connectivity
    Write-Host "   Testing connectivity..." -ForegroundColor Gray
    try {
        $result = Test-NetConnection -ComputerName $ProductionHost -Port 22 -InformationLevel Quiet -WarningAction SilentlyContinue
        if ($result) {
            Write-Host "   ✅ SSH port (22) is reachable" -ForegroundColor Green
        } else {
            $warnings += "SSH port (22) is not reachable from this machine"
        }
    } catch {
        $warnings += "Could not test SSH connectivity (requires Test-NetConnection)"
    }
}

# Test Production User
Write-Host ""
Write-Host "👤 Testing Production User..." -ForegroundColor Yellow
if (-not $ProductionUser) {
    $errors += "PRODUCTION_USER environment variable not set"
} elseif ($ProductionUser -match "your_|YOUR_|example") {
    $errors += "Production user appears to contain placeholder values"
} else {
    Write-Host "✅ Production user configured: $ProductionUser" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "📋 Validation Summary" -ForegroundColor Green
Write-Host "=" -repeat 20 -ForegroundColor Green

if ($errors.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "🎉 All secrets look good!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Add these secrets to GitHub repository (Settings → Secrets and variables → Actions)" -ForegroundColor White
    Write-Host "2. Push to main branch to trigger deployment" -ForegroundColor White
    Write-Host "3. Check GitHub Actions for deployment status" -ForegroundColor White
} else {
    if ($errors.Count -gt 0) {
        Write-Host ""
        Write-Host "❌ Errors found:" -ForegroundColor Red
        foreach ($error in $errors) {
            Write-Host "   • $error" -ForegroundColor Red
        }
    }
    
    if ($warnings.Count -gt 0) {
        Write-Host ""
        Write-Host "⚠️  Warnings:" -ForegroundColor Yellow
        foreach ($warning in $warnings) {
            Write-Host "   • $warning" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "Please fix the errors before deploying." -ForegroundColor Red
}

Write-Host ""
Write-Host "💡 Pro tip: Set these as environment variables to test:" -ForegroundColor Cyan
Write-Host '$env:MYSQL_DATABASE_URL = "mysql+pymysql://user:pass@host:3306/db"' -ForegroundColor Gray
Write-Host '$env:WILDEDITOR_API_KEY = "your-generated-api-key"' -ForegroundColor Gray
Write-Host '$env:PRODUCTION_HOST = "your.server.com"' -ForegroundColor Gray
Write-Host '$env:PRODUCTION_USER = "your-ssh-user"' -ForegroundColor Gray
Write-Host ""
Write-Host "Then run this script again to validate!" -ForegroundColor Cyan
