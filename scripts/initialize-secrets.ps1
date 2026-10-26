$ErrorActionPreference = 'Stop'
$platformRoot = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $platformRoot '.env'
if (Test-Path -LiteralPath $envFile) { throw 'Existing .env; refusing to replace credentials' }
New-Item -ItemType Directory -Path "$platformRoot/secrets", "$platformRoot/backups" -Force | Out-Null
function New-LocalSecret { [Convert]::ToHexString([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(24)) }
$secretMap = [ordered]@{
    GITLAB_ROOT_PASSWORD = New-LocalSecret
    PENPOT_SECRET_KEY = [Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(64))
    PENPOT_DB_PASSWORD = New-LocalSecret
    MYSQL_ROOT_PASSWORD = New-LocalSecret
    MYSQL_PASSWORD = New-LocalSecret
}
($secretMap.GetEnumerator() | ForEach-Object { '{0}={1}' -f $_.Key, $_.Value }) | Set-Content -LiteralPath $envFile -Encoding utf8
@{
    gitlab = @{url='http://localhost:8088'; username='root'; password=$secretMap.GITLAB_ROOT_PASSWORD}
    penpot = @{url='http://localhost:9001'; email='developer@local.test'; password=(New-LocalSecret)}
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath "$platformRoot/secrets/accounts.json" -Encoding utf8
$identityName = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
icacls $envFile /inheritance:r /grant:r "${identityName}:(F)" 'SYSTEM:(F)' | Out-Null
foreach ($directory in 'secrets', 'backups') {
    icacls "$platformRoot/$directory" /inheritance:r /grant:r "${identityName}:(OI)(CI)F" 'SYSTEM:(OI)(CI)F' | Out-Null
}
Write-Output 'Local credentials generated; values are in restricted files only.'
