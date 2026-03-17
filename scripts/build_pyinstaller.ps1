$ErrorActionPreference = "Stop"
Push-Location (Split-Path $MyInvocation.MyCommand.Path -Parent)
Set-Location ..

pyinstaller `
  --name "cloakandcode-proxy" `
  --onefile `
  --add-data "backend;backend" `
  --hidden-import "spacy" `
  --hidden-import "presidio_analyzer" `
  --hidden-import "presidio_anonymizer" `
  backend/main.py

Pop-Location
