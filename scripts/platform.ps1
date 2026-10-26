param([ValidateSet('up', 'stop', 'status', 'logs')][string]$Action = 'status')
$ErrorActionPreference = 'Stop'
$platformRoot = Split-Path -Parent $PSScriptRoot
Push-Location $platformRoot
try {
    switch ($Action) {
        'up' { docker compose up -d --pull never }
        'stop' { docker compose stop }
        'status' { docker compose ps }
        'logs' { docker compose logs --tail 80 }
    }
    if ($LASTEXITCODE -ne 0) { throw "Platform command failed: $Action" }
} finally { Pop-Location }
