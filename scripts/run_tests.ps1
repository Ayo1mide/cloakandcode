$ErrorActionPreference = "Stop"
Push-Location (Split-Path $MyInvocation.MyCommand.Path -Parent)
Set-Location ..
python -m pytest backend/tests
Pop-Location
