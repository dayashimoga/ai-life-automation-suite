$ErrorActionPreference = "Continue"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " AI Life Automation Suite - Test Runner" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

$apps = @(
    "unified-dashboard-app",
    "memory-journal-app",
    "doomscroll-breaker-app",
    "visual-intelligence-app",
    "micro-habit-engine"
)
$failed = $false

foreach ($app in $apps) {
    Write-Host "`n`u{27A4} Running Tests for $app ..." -ForegroundColor Yellow

    $appDir = "apps/$app"

    Push-Location $appDir
    try {
        Write-Host "  -> Creating temporary venv..." -ForegroundColor DarkGray
        python -m venv .venv_tmp
        
        Write-Host "  -> Installing dependencies..." -ForegroundColor DarkGray
        & .venv_tmp\Scripts\python.exe -m pip install --quiet --upgrade pip
        & .venv_tmp\Scripts\python.exe -m pip install --quiet ruff black pytest pytest-cov
        if (Test-Path "requirements.txt") {
            & .venv_tmp\Scripts\python.exe -m pip install --quiet -r requirements.txt
        }
        
        Write-Host "  -> Running linting (Ruff & Black)..." -ForegroundColor DarkGray
        $lintResult1 = & .venv_tmp\Scripts\python.exe -m ruff check . 2>&1
        $exitCode1 = $LASTEXITCODE
        if ($exitCode1 -ne 0) { Write-Host $lintResult1; throw "Linting failed!" }

        $lintResult2 = & .venv_tmp\Scripts\python.exe -m black --check . 2>&1
        $exitCode2 = $LASTEXITCODE
        if ($exitCode2 -ne 0) { Write-Host $lintResult2; throw "Formatting failed!" }
        
        Write-Host "  -> Running tests with coverage..." -ForegroundColor DarkGray
        $result = & .venv_tmp\Scripts\python.exe -m pytest tests/ -v --tb=short --cov=. --cov-report=term-missing 2>&1
        $exitCode = $LASTEXITCODE
        Write-Host $result

        if ($exitCode -ne 0) {
            Write-Host "X $app tests FAILED!" -ForegroundColor Red
            $failed = $true
        } else {
            Write-Host "OK $app tests PASSED!" -ForegroundColor Green
        }
    } finally {
        Write-Host "  -> Cleaning up temporary venv..." -ForegroundColor DarkGray
        if (Test-Path ".venv_tmp") {
            Remove-Item -Recurse -Force -ErrorAction SilentlyContinue .venv_tmp
        }
        Pop-Location
    }
}

Write-Host "`n=========================================" -ForegroundColor Cyan
if ($failed) {
    Write-Host "WARNING: SOME TESTS FAILED." -ForegroundColor Red
    exit 1
} else {
    Write-Host "ALL TESTS PASSED!" -ForegroundColor Green
    exit 0
}
