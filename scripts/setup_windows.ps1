param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

Write-Host "[1/4] Creating virtual environment..."
& $Python -m venv .venv

Write-Host "[2/4] Activating virtual environment..."
. .\.venv\Scripts\Activate.ps1

Write-Host "[3/4] Upgrading pip..."
python -m pip install --upgrade pip

Write-Host "[4/4] Installing project with dev dependencies..."
pip install -e .[dev]

Write-Host "Setup complete. Run: pytest"
