# FortuneOne local dev (SQLite + ports 8000 / 6100)
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Starting FortuneOne..." -ForegroundColor Cyan

$env:DATABASE_URL = "sqlite+aiosqlite:///./data/fortuneone.db"
New-Item -ItemType Directory -Force -Path "$Root\backend\data" | Out-Null

Start-Process powershell -ArgumentList @(
  "-NoExit", "-Command",
  "cd '$Root\backend'; `$env:DATABASE_URL='sqlite+aiosqlite:///./data/fortuneone.db'; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
)

Start-Process powershell -ArgumentList @(
  "-NoExit", "-Command",
  "cd '$Root\frontend'; `$env:NEXT_PUBLIC_API_URL='http://127.0.0.1:8000'; npm run dev"
)

Write-Host "API  http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "App  http://localhost:6100" -ForegroundColor Green
