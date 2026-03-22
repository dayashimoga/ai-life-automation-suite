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
        if (Test-Path ".venv_tmp\Scripts\python.exe") {
            $result = & ".venv_tmp\Scripts\python.exe" -m pytest tests/ -v --tb=short 2>&1
        } else {
            $result = & python -m pytest tests/ -v --tb=short 2>&1
        }
        $exitCode = $LASTEXITCODE
        Write-Host $result

        if ($exitCode -ne 0) {
            Write-Host "X $app tests FAILED!" -ForegroundColor Red
            $failed = $true
        } else {
            Write-Host "OK $app tests PASSED!" -ForegroundColor Green
        }
    } finally {
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
