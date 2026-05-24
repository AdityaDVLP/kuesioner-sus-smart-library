# Deploy ke Railway (jalankan di PowerShell interaktif setelah login)
# 1. railway login
# 2. gh auth login
# 3. .\deploy-railway.ps1

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "==> Cek Railway login..." -ForegroundColor Cyan
railway whoami | Out-Null

Write-Host "==> Cek GitHub login..." -ForegroundColor Cyan
$gh = (Get-Command gh -ErrorAction SilentlyContinue).Source
if (-not $gh) { $gh = "${env:ProgramFiles}\GitHub CLI\gh.exe" }
& $gh auth status | Out-Null

$repoName = "kuesioner-sus-smart-library"
Write-Host "==> Buat/push repo GitHub: $repoName" -ForegroundColor Cyan
$remote = git remote get-url origin 2>$null
if (-not $remote) {
    & $gh repo create $repoName --public --source=. --remote=origin --push
} else {
    git push -u origin master
}

Write-Host "==> Inisialisasi Railway project..." -ForegroundColor Cyan
if (-not (Test-Path ".railway")) {
    railway init --name $repoName
}

Write-Host "==> Set environment variables..." -ForegroundColor Cyan
$secret = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object { [char]$_ })
railway variables set "SECRET_KEY=$secret"
railway variables set "DATA_DIR=/data"

Write-Host "==> Deploy..." -ForegroundColor Cyan
railway up --detach

Write-Host "==> URL deployment:" -ForegroundColor Green
railway domain
railway status
