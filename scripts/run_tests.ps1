# Run Tests with Coverage (PowerShell)
# This script runs the complete test suite and generates coverage reports

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  AI Grading System - Test Runner with Coverage" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

param(
    [switch]$CoverageOnly,
    [switch]$Fast,
    [switch]$Verbose
)

# Check if pytest is installed
try {
    pytest --version | Out-Null
} catch {
    Write-Host "❌ pytest not found. Installing..." -ForegroundColor Red
    pip install pytest pytest-cov
}

# Clean previous coverage data
Write-Host "🧹 Cleaning previous coverage data..." -ForegroundColor Blue
Remove-Item -Path ".coverage*" -ErrorAction SilentlyContinue
Remove-Item -Path "htmlcov" -Recurse -ErrorAction SilentlyContinue
Remove-Item -Path "coverage.xml" -ErrorAction SilentlyContinue
Remove-Item -Path "coverage.json" -ErrorAction SilentlyContinue
Write-Host ""

# Run tests
if ($CoverageOnly) {
    Write-Host "📊 Generating coverage report only (no tests)..." -ForegroundColor Blue
    coverage report
    coverage html
} else {
    Write-Host "🧪 Running tests with coverage..." -ForegroundColor Blue
    Write-Host ""

    if ($Fast) {
        # Fast mode - skip slow tests
        pytest -v --cov=. --cov-report=html --cov-report=term-missing -m "not slow and not load"
    } elseif ($Verbose) {
        # Verbose mode
        pytest -vv --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml --cov-report=json
    } else {
        # Normal mode
        pytest --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml --cov-report=json
    }

    $TestExitCode = $LASTEXITCODE
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "✅ Test execution complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Display coverage summary
Write-Host "📊 Coverage Summary:" -ForegroundColor Blue
coverage report --skip-empty

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "📁 Coverage Reports Generated:" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  HTML Report:    htmlcov\index.html" -ForegroundColor Yellow
Write-Host "  XML Report:     coverage.xml" -ForegroundColor Yellow
Write-Host "  JSON Report:    coverage.json" -ForegroundColor Yellow
Write-Host "  Terminal:       See above" -ForegroundColor Yellow
Write-Host ""

# Check coverage threshold
$CoverageOutput = coverage report | Select-String "TOTAL"
if ($CoverageOutput) {
    $CoveragePercent = ($CoverageOutput -split '\s+')[3] -replace '%', ''
    $Threshold = 85

    Write-Host "Coverage: $CoveragePercent% (Target: $Threshold%)" -ForegroundColor Blue

    if ([double]$CoveragePercent -ge $Threshold) {
        Write-Host "✅ Coverage target met!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Coverage below target" -ForegroundColor Yellow
    }
}

Write-Host ""

# Open HTML report (optional)
$OpenReport = Read-Host "Open HTML coverage report in browser? (y/n)"
if ($OpenReport -eq 'y' -or $OpenReport -eq 'Y') {
    Start-Process "htmlcov\index.html"
}

# Exit with test exit code
exit $TestExitCode
