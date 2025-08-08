# Car Lister Deployment Script
# Deploys Blazor PWA frontend to Firebase Hosting

param(
    [string]$Environment = "production"
)

Write-Host "🚀 Car Lister Deployment Script" -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Yellow

# Function to check if command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Check prerequisites
Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Blue

if (-not (Test-Command "dotnet")) {
    Write-Host "❌ .NET SDK not found. Please install .NET 8.0 SDK" -ForegroundColor Red
    exit 1
}

if (-not (Test-Command "firebase")) {
    Write-Host "❌ Firebase CLI not found. Please install Firebase CLI" -ForegroundColor Red
    exit 1
}

Write-Host "✅ All prerequisites found" -ForegroundColor Green

# Build frontend
Write-Host "`n🏗️ Building Blazor PWA..." -ForegroundColor Blue

# Clean and publish
dotnet clean
dotnet publish --configuration Release

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Frontend build failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Frontend build successful" -ForegroundColor Green



# Deploy to Firebase
Write-Host "`n🔥 Deploying to Firebase..." -ForegroundColor Blue

firebase deploy --only hosting

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Firebase deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Deployment completed successfully!" -ForegroundColor Green

# Get deployment info
Write-Host "`n📊 Deployment Information:" -ForegroundColor Blue
Write-Host "Frontend: https://car-lister-be093.web.app" -ForegroundColor Cyan

Write-Host "`n🎉 Your Car Lister PWA is now live!" -ForegroundColor Green 