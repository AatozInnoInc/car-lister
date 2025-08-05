# Car Lister Deployment Script
# Deploys both Blazor PWA frontend and Python API backend to Firebase

param(
    [string]$Environment = "production",
    [switch]$FrontendOnly,
    [switch]$BackendOnly
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

if (-not (Test-Command "python")) {
    Write-Host "❌ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

Write-Host "✅ All prerequisites found" -ForegroundColor Green

# Build and deploy frontend
if (-not $BackendOnly) {
    Write-Host "`n🏗️ Building Blazor PWA..." -ForegroundColor Blue
    
    # Clean and build
    dotnet clean
    dotnet build --configuration Release
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Frontend build failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Frontend build successful" -ForegroundColor Green
}

# Deploy backend
if (-not $FrontendOnly) {
    Write-Host "`n🐍 Setting up Python backend..." -ForegroundColor Blue
    
    # Check if backend directory exists
    if (-not (Test-Path "backend")) {
        Write-Host "❌ Backend directory not found" -ForegroundColor Red
        exit 1
    }
    
    # Install Python dependencies
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    Set-Location backend
    python -m pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
        exit 1
    }
    
    Set-Location ..
    Write-Host "✅ Python dependencies installed" -ForegroundColor Green
}

# Deploy to Firebase
Write-Host "`n🔥 Deploying to Firebase..." -ForegroundColor Blue

if ($FrontendOnly) {
    firebase deploy --only hosting
} elseif ($BackendOnly) {
    firebase deploy --only functions
} else {
    firebase deploy
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Firebase deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Deployment completed successfully!" -ForegroundColor Green

# Get deployment info
Write-Host "`n📊 Deployment Information:" -ForegroundColor Blue
Write-Host "Frontend: https://car-lister-be093.web.app" -ForegroundColor Cyan
Write-Host "API: https://us-central1-car-lister-be093.cloudfunctions.net/api" -ForegroundColor Cyan

Write-Host "`n🎉 Your Car Lister PWA is now live!" -ForegroundColor Green 