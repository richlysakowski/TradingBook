@echo off
REM ============================================================================
REM TradingBook - Windows Installation & Startup Script
REM ============================================================================
REM This script installs dependencies and launches TradingBook
REM Run this script from the TradingBook root directory
REM ============================================================================

setlocal enabledelayedexpansion

REM Set console title and colors
title TradingBook Setup
color 0A

REM Banner
echo.
echo  ============================================================
echo   TradingBook - Windows Setup Script
echo   Privacy-Focused Desktop Trading Journal
echo  ============================================================
echo.

REM Check if we're in the right directory
if not exist "package.json" (
    echo [ERROR] package.json not found!
    echo [ERROR] Please run this script from the TradingBook root directory.
    echo.
    echo Example:
    echo   cd "C:\path\to\TradingBook"
    echo   scripts\windows_setup.bat
    echo.
    pause
    exit /b 1
)

REM ============================================================================
REM Step 1: Check for Node.js
REM ============================================================================
echo [1/5] Checking for Node.js...
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo.
    echo Please install Node.js from: https://nodejs.org/
    echo Recommended version: 18.x or 20.x LTS
    echo.
    echo After installing, restart this script.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] Node.js found: %NODE_VERSION%

REM Check npm
where npm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] npm is not installed or not in PATH!
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
echo [OK] npm found: v%NPM_VERSION%
echo.

REM ============================================================================
REM Step 2: Check for Visual C++ Build Tools (for native modules)
REM ============================================================================
echo [2/5] Checking build environment...

REM Check if node-gyp can compile
where cl >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Visual C++ compiler not found in PATH.
    echo [INFO] better-sqlite3 requires native compilation.
    echo.
    echo If installation fails, install Visual Studio Build Tools:
    echo https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo Select: "Desktop development with C++"
    echo.
) else (
    echo [OK] Visual C++ compiler found
)
echo.

REM ============================================================================
REM Step 3: Clean previous installations (optional)
REM ============================================================================
echo [3/5] Preparing installation...

if exist "node_modules" (
    echo [INFO] Found existing node_modules folder
    set /p CLEAN_INSTALL="Clean install? (y/N): "
    if /i "!CLEAN_INSTALL!"=="y" (
        echo [INFO] Removing node_modules...
        rmdir /s /q node_modules 2>nul
        echo [OK] Cleaned node_modules
    )
)
echo.

REM ============================================================================
REM Step 4: Install dependencies
REM ============================================================================
echo [4/5] Installing dependencies...
echo [INFO] This may take a few minutes...
echo [INFO] Using --legacy-peer-deps to resolve version conflicts...
echo.

call npm install --legacy-peer-deps

if %ERRORLEVEL% neq 0 (
    echo.
    echo [WARNING] First install attempt failed, trying with --force...
    echo.
    call npm install --legacy-peer-deps --force
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] npm install failed!
    echo.
    echo Troubleshooting steps:
    echo 1. Try manually: npm install --legacy-peer-deps --force
    echo 2. Ensure you have Visual Studio Build Tools installed
    echo 3. Run: npm install --global windows-build-tools
    echo 4. Try: npm rebuild better-sqlite3
    echo 5. Check internet connection
    echo.
    echo TradingBook will use JSON fallback if SQLite fails.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Dependencies installed successfully!
echo.

REM ============================================================================
REM Step 5: Build and Launch options
REM ============================================================================
echo [5/5] Setup complete!
echo.
echo  ============================================================
echo   What would you like to do?
echo  ============================================================
echo.
echo   1. Start TradingBook (Development Mode)
echo   2. Build Windows Installer (.exe)
echo   3. Build Windows Portable (.exe)
echo   4. Build Both (Installer + Portable)
echo   5. Exit (run later with 'npm run electron-dev')
echo.
set /p CHOICE="Enter choice (1-5): "

if "%CHOICE%"=="1" goto START_DEV
if "%CHOICE%"=="2" goto BUILD_INSTALLER
if "%CHOICE%"=="3" goto BUILD_PORTABLE
if "%CHOICE%"=="4" goto BUILD_BOTH
if "%CHOICE%"=="5" goto EXIT_SCRIPT
goto EXIT_SCRIPT

:START_DEV
echo.
echo [INFO] Starting TradingBook in development mode...
echo [INFO] The app will open shortly. Press Ctrl+C to stop.
echo.
call npm run electron-dev
goto END

:BUILD_INSTALLER
echo.
echo [INFO] Building Windows Installer...
echo [INFO] This may take several minutes...
echo.
call npm run build-windows-installer
if %ERRORLEVEL% equ 0 (
    echo.
    echo [OK] Installer created in dist\ folder!
    echo [INFO] Look for: TradingBook-Setup-x.x.x.exe
    start dist
)
goto END

:BUILD_PORTABLE
echo.
echo [INFO] Building Windows Portable...
echo [INFO] This may take several minutes...
echo.
call npm run build-windows-portable
if %ERRORLEVEL% equ 0 (
    echo.
    echo [OK] Portable executable created in dist\ folder!
    echo [INFO] Look for: TradingBook-x.x.x-portable.exe
    start dist
)
goto END

:BUILD_BOTH
echo.
echo [INFO] Building both Installer and Portable...
echo [INFO] This may take several minutes...
echo.
call npm run build-windows-both
if %ERRORLEVEL% equ 0 (
    echo.
    echo [OK] Both builds created in dist\ folder!
    start dist
)
goto END

:EXIT_SCRIPT
echo.
echo [INFO] Setup complete! To start TradingBook later, run:
echo.
echo   cd "%CD%"
echo   npm run electron-dev
echo.
goto END

:END
echo.
echo  ============================================================
echo   Data stored at: %APPDATA%\tradingbook\
echo   Documentation: scripts\WINDOWS_SETUP_INSTRUCTIONS.md
echo  ============================================================
echo.
pause
