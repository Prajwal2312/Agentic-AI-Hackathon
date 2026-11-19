# Start FastAPI Backend
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Starting PRIVESCAN AI Backend API       " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# If inside the backend directory, navigate up to the project root
if ((Split-Path -Leaf (Get-Location)) -eq "backend") {
    Set-Location ..
}

python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
