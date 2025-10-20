# Starts the Bitácoras de Vuelos app with Python 3.12 venv
param()

$ErrorActionPreference = 'Stop'

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "Creating Python 3.12 virtual environment..."
    py -3.12 -m venv .venv
}

Write-Host "Activating venv and launching app..."
& powershell -ExecutionPolicy Bypass -NoProfile -Command ". .\\.venv\\Scripts\\Activate.ps1; if (-not (Get-Command pip -ErrorAction SilentlyContinue)) { Write-Error 'pip not found' }; pip install -r requirements.txt; python .\\main.py"
