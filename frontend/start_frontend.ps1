# Start Next.js Frontend
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Starting PRIVESCAN AI Frontend SaaS     " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# If not already in the frontend directory, navigate into it
if (-not (Test-Path "package.json")) {
    if (Test-Path "frontend\package.json") {
        Set-Location "frontend"
    }
}

npm run start
