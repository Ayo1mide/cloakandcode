$ErrorActionPreference = "Stop"
Push-Location (Split-Path $MyInvocation.MyCommand.Path -Parent)
Set-Location ..
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8080 --log-level info
Pop-Location
