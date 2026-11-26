$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "=== AlpTrack: Initial Setup ==="

# Проверяем python
python --version
if ($LASTEXITCODE -ne 0) {
    throw "Python is not available"
}

$PythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"

if ($PythonVersion -ne "3.14") {
    throw "Python 3.14 is required. Found: $PythonVersion"
}

# Создаем виртуальное окружение, если его нет
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create virtual environment"
    }
}

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
& $Python -c "import sys; assert sys.version_info[:2] == (3, 14), 'Python 3.14 is required'"

if ($LASTEXITCODE -ne 0) {
    throw "Virtual environment must use Python 3.14"
}


# Устанавливаем зависимости приложения и разработки
Write-Host "Installing dependencies..."
& $Python -m pip install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install dependencies"
}

# Проверяем наличие локальной конфигурации
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "Created .env и .env.example"
        Write-Warning "Configure database and secrets in .env"
    }
    else {
        Write-Warning ".env.example was not found"
    }
}

Write-Host "=== Setup completed successfully ==="