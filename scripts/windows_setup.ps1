# TradingBook Windows Setup - PowerShell Script
# ============================================================================
# For users who prefer PowerShell over batch files
# Run: .\scripts\windows_setup.ps1
# ============================================================================

param(
    [switch]$CleanInstall,
    [switch]$BuildInstaller,
    [switch]$BuildPortable,
    [switch]$SkipLaunch
)

$ErrorActionPreference = "Stop"

# Colors and formatting
function Write-Banner {
    Write-Host ""
    Write-Host "  ============================================================" -ForegroundColor Cyan
    Write-Host "   TradingBook - Windows Setup Script (PowerShell)" -ForegroundColor Cyan
    Write-Host "   Privacy-Focused Desktop Trading Journal" -ForegroundColor Cyan
    Write-Host "  ============================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Step, [string]$Message)
    Write-Host "[$Step] $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor White
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

# Main script
Write-Banner

# Check if we're in the right directory
if (-not (Test-Path "package.json")) {
    Write-Error-Custom "package.json not found!"
    Write-Error-Custom "Please run this script from the TradingBook root directory."
    Write-Host ""
    Write-Host "Example:" -ForegroundColor Gray
    Write-Host '  cd "C:\path\to\TradingBook"' -ForegroundColor Gray
    Write-Host '  .\scripts\windows_setup.ps1' -ForegroundColor Gray
    exit 1
}

# ============================================================================
# Step 1: Check for Node.js
# ============================================================================
Write-Step "1/5" "Checking for Node.js..."

$nodeVersion = $null
try {
    $nodeVersion = node --version
    Write-Success "Node.js found: $nodeVersion"
} catch {
    Write-Error-Custom "Node.js is not installed or not in PATH!"
    Write-Host ""
    Write-Host "Please install Node.js from: https://nodejs.org/" -ForegroundColor White
    Write-Host "Recommended version: 18.x or 20.x LTS" -ForegroundColor White
    exit 1
}

$npmVersion = $null
try {
    $npmVersion = npm --version
    Write-Success "npm found: v$npmVersion"
} catch {
    Write-Error-Custom "npm is not installed or not in PATH!"
    exit 1
}

Write-Host ""

# ============================================================================
# Step 2: Check for Visual C++ Build Tools
# ============================================================================
Write-Step "2/5" "Checking build environment..."

$hasCompiler = $false
try {
    $cl = Get-Command cl -ErrorAction SilentlyContinue
    if ($cl) {
        $hasCompiler = $true
        Write-Success "Visual C++ compiler found"
    }
} catch {}

if (-not $hasCompiler) {
    Write-Warning-Custom "Visual C++ compiler not found in PATH."
    Write-Info "better-sqlite3 requires native compilation."
    Write-Host ""
    Write-Host "If installation fails, install Visual Studio Build Tools:" -ForegroundColor White
    Write-Host "https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Cyan
    Write-Host 'Select: "Desktop development with C++"' -ForegroundColor White
    Write-Host ""
}

# ============================================================================
# Step 3: Clean previous installations
# ============================================================================
Write-Step "3/5" "Preparing installation..."

if (Test-Path "node_modules") {
    Write-Info "Found existing node_modules folder"
    
    if ($CleanInstall) {
        Write-Info "Removing node_modules (clean install requested)..."
        Remove-Item -Recurse -Force "node_modules" -ErrorAction SilentlyContinue
        Write-Success "Cleaned node_modules"
    } else {
        $response = Read-Host "Clean install? (y/N)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            Write-Info "Removing node_modules..."
            Remove-Item -Recurse -Force "node_modules" -ErrorAction SilentlyContinue
            Write-Success "Cleaned node_modules"
        }
    }
}

Write-Host ""

# ============================================================================
# Step 4: Install dependencies
# ============================================================================
Write-Step "4/5" "Installing dependencies..."
Write-Info "This may take a few minutes..."
Write-Host ""

try {
    $npmInstall = Start-Process -FilePath "npm" -ArgumentList "install" -NoNewWindow -Wait -PassThru
    
    if ($npmInstall.ExitCode -ne 0) {
        throw "npm install failed with exit code $($npmInstall.ExitCode)"
    }
    
    Write-Host ""
    Write-Success "Dependencies installed successfully!"
} catch {
    Write-Host ""
    Write-Error-Custom "npm install failed!"
    Write-Host ""
    Write-Host "Troubleshooting steps:" -ForegroundColor Yellow
    Write-Host "1. Ensure you have Visual Studio Build Tools installed" -ForegroundColor White
    Write-Host "2. Run: npm install --global windows-build-tools" -ForegroundColor White
    Write-Host "3. Try: npm rebuild better-sqlite3" -ForegroundColor White
    Write-Host "4. Check internet connection" -ForegroundColor White
    Write-Host ""
    Write-Host "TradingBook will use JSON fallback if SQLite fails." -ForegroundColor Gray
    exit 1
}

Write-Host ""

# ============================================================================
# Step 5: Build and Launch
# ============================================================================
Write-Step "5/5" "Setup complete!"
Write-Host ""

if ($BuildInstaller) {
    Write-Info "Building Windows Installer..."
    npm run build-windows-installer
    Write-Host ""
    Write-Success "Installer created in dist\ folder!"
    Start-Process "explorer.exe" -ArgumentList "dist"
}
elseif ($BuildPortable) {
    Write-Info "Building Windows Portable..."
    npm run build-windows-portable
    Write-Host ""
    Write-Success "Portable executable created in dist\ folder!"
    Start-Process "explorer.exe" -ArgumentList "dist"
}
elseif (-not $SkipLaunch) {
    Write-Host "  ============================================================" -ForegroundColor Cyan
    Write-Host "   What would you like to do?" -ForegroundColor Cyan
    Write-Host "  ============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   1. Start TradingBook (Development Mode)"
    Write-Host "   2. Build Windows Installer (.exe)"
    Write-Host "   3. Build Windows Portable (.exe)"
    Write-Host "   4. Build Both (Installer + Portable)"
    Write-Host "   5. Exit (run later with 'npm run electron-dev')"
    Write-Host ""
    
    $choice = Read-Host "Enter choice (1-5)"
    
    switch ($choice) {
        "1" {
            Write-Host ""
            Write-Info "Starting TradingBook in development mode..."
            Write-Info "The app will open shortly. Press Ctrl+C to stop."
            Write-Host ""
            npm run electron-dev
        }
        "2" {
            Write-Host ""
            Write-Info "Building Windows Installer..."
            npm run build-windows-installer
            Write-Success "Installer created in dist\ folder!"
            Start-Process "explorer.exe" -ArgumentList "dist"
        }
        "3" {
            Write-Host ""
            Write-Info "Building Windows Portable..."
            npm run build-windows-portable
            Write-Success "Portable executable created in dist\ folder!"
            Start-Process "explorer.exe" -ArgumentList "dist"
        }
        "4" {
            Write-Host ""
            Write-Info "Building both Installer and Portable..."
            npm run build-windows-both
            Write-Success "Both builds created in dist\ folder!"
            Start-Process "explorer.exe" -ArgumentList "dist"
        }
        default {
            Write-Host ""
            Write-Info "Setup complete! To start TradingBook later, run:"
            Write-Host ""
            Write-Host "  npm run electron-dev" -ForegroundColor White
            Write-Host ""
        }
    }
}

Write-Host ""
Write-Host "  ============================================================" -ForegroundColor Cyan
Write-Host "   Data stored at: $env:APPDATA\tradingbook\" -ForegroundColor White
Write-Host "   Documentation: scripts\WINDOWS_SETUP_INSTRUCTIONS.md" -ForegroundColor White
Write-Host "  ============================================================" -ForegroundColor Cyan
Write-Host ""

if (-not $SkipLaunch -and -not $BuildInstaller -and -not $BuildPortable) {
    Read-Host "Press Enter to exit"
}
