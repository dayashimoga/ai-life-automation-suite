$ErrorActionPreference = "Stop"

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
        if (Test-Path "requirements.txt") {
            & .venv_tmp\Scripts\python.exe -m pip install --quiet -r requirements.txt
        }
        
        Write-Host "  -> Running tests..." -ForegroundColor DarkGray
        $result = & .venv_tmp\Scripts\python.exe -m pytest tests/ -v --tb=short 2>&1
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
