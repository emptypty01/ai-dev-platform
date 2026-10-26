param([switch]$IncludeGitLab)
$ErrorActionPreference = 'Stop'
$platformRoot = Split-Path -Parent $PSScriptRoot
$backupDir = Join-Path $platformRoot ('backups/' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $backupDir | Out-Null
function Invoke-DockerChecked([string[]]$Arguments) {
    & docker @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Docker backup step failed: $($Arguments[0..1] -join ' ')" }
}
# 暂停 Penpot 写入，保证数据库与附件来自同一时间窗口。
Push-Location $platformRoot
try {
    Invoke-DockerChecked -Arguments @('compose', 'stop', 'penpot-frontend', 'penpot-backend', 'penpot-exporter', 'penpot-admin-console', 'penpot-mcp')
    try {
        Invoke-DockerChecked -Arguments @('exec', 'ai-dev-penpot-postgres', 'pg_dump', '-U', 'penpot', '-Fc', '-f', '/tmp/penpot.dump', 'penpot')
        Invoke-DockerChecked -Arguments @('cp', 'ai-dev-penpot-postgres:/tmp/penpot.dump', "$backupDir/penpot.dump")
        Invoke-DockerChecked -Arguments @('run', '--rm', '-v', 'ai-dev-platform_penpot_assets:/data:ro', '-v', "${backupDir}:/backup", 'python:3.12-slim', 'tar', '-czf', '/backup/penpot-assets.tar.gz', '-C', '/data', '.')
    } finally {
        Invoke-DockerChecked -Arguments @('compose', 'start', 'penpot-backend', 'penpot-admin-console', 'penpot-mcp', 'penpot-exporter', 'penpot-frontend')
    }
    # 密码由容器既有环境在容器内展开，不写入主机命令或日志。
    Invoke-DockerChecked -Arguments @('exec', 'ai-dev-demo-mysql', 'sh', '-c', 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysqldump -uroot --single-transaction --routines --triggers ai_workflow > /tmp/ai-workflow.sql')
    Invoke-DockerChecked -Arguments @('cp', 'ai-dev-demo-mysql:/tmp/ai-workflow.sql', "$backupDir/ai-workflow.sql")
    if ($IncludeGitLab) {
        Invoke-DockerChecked -Arguments @('exec', 'ai-dev-gitlab', 'gitlab-backup', 'create', 'STRATEGY=copy')
        Invoke-DockerChecked -Arguments @('exec', 'ai-dev-gitlab', 'sh', '-c', 'tar -czf /tmp/gitlab-backups.tar.gz -C /var/opt/gitlab/backups .')
        Invoke-DockerChecked -Arguments @('cp', 'ai-dev-gitlab:/tmp/gitlab-backups.tar.gz', "$backupDir/gitlab-backups.tar.gz")
        Invoke-DockerChecked -Arguments @('exec', 'ai-dev-gitlab', 'sh', '-c', 'tar -czf /tmp/gitlab-config.tar.gz -C /etc/gitlab .')
        Invoke-DockerChecked -Arguments @('cp', 'ai-dev-gitlab:/tmp/gitlab-config.tar.gz', "$backupDir/gitlab-config.tar.gz")
    }
    Copy-Item -LiteralPath "$platformRoot/compose.yaml", "$platformRoot/.env" -Destination $backupDir
    Copy-Item -LiteralPath "$platformRoot/secrets" -Destination "$backupDir/secrets" -Recurse
    Invoke-DockerChecked -Arguments @('run', '--rm', '-v', 'ai-dev-platform_runner_config:/data:ro', '-v', "${backupDir}:/backup", 'python:3.12-slim', 'tar', '-czf', '/backup/runner-config.tar.gz', '-C', '/data', '.')
    $identityName = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    icacls $backupDir /inheritance:r /grant:r "${identityName}:(OI)(CI)F" 'SYSTEM:(OI)(CI)F' | Out-Null
    Get-ChildItem -LiteralPath $backupDir -File | Get-FileHash -Algorithm SHA256 | Select-Object Hash,@{n='File';e={Split-Path -Leaf $_.Path}} | ConvertTo-Json | Set-Content -LiteralPath "$backupDir/checksums.json" -Encoding utf8
    Write-Output "Backup created: $backupDir (GitLab included: $IncludeGitLab)"
} finally { Pop-Location }
