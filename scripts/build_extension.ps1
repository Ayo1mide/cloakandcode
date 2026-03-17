$ErrorActionPreference = "Stop"
Push-Location (Split-Path $MyInvocation.MyCommand.Path -Parent)
Set-Location ..
Compress-Archive -Path extension\\* -DestinationPath dist\\cloakandcode-extension.zip -Force
Pop-Location
