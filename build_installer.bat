@echo off
REM ============================================================================
REM TradingBook - Build Windows Installer Script (Optimized)
REM ============================================================================
REM Builds the NSIS Windows Installer with smart caching.
REM
REM Usage:
REM   build_installer.bat           Smart build (uses cache, ~3-4 min)
REM   build_installer.bat --force   Clean rebuild (no cache, ~8-12 min)
REM
REM Output: dist\TradingBook Setup X.X.X.exe
REM ============================================================================

setlocal enabledelayedexpansion

REM Check for --force flag
set FORCE_BUILD=0
if "%~1"=="--force" set FORCE_BUILD=1
if "%~1"=="-f" set FORCE_BUILD=1

REM Record start time
for /f "tokens=1-4 delims=:. " %%a in ("%TIME%") do (
    set /a START_H=%%a
    set /a START_M=%%b
    set /a START_S=%%c
)
set /a START_TOTAL=START_H*3600 + START_M*60 + START_S

echo.
echo ============================================================================
echo  TradingBook - Windows Installer Builder
echo ============================================================================
if !FORCE_BUILD!==1 (
    echo  Mode: FORCE REBUILD - all steps will run
    echo  Estimated time: 8-12 minutes
) else (
    echo  Mode: SMART BUILD - skipping cached steps
    echo  Estimated time: 3-4 minutes
)
echo  Started: %DATE% %TIME%
echo ============================================================================
echo.

REM Check if we're in the right directory
if not exist "package.json" (
    echo [ERROR] package.json not found!
    echo [ERROR] Please run this script from the TradingBook root directory.
    exit /b 1
)

REM ============================================================================
REM Step 1: Check Prerequisites (~5 seconds)
REM ============================================================================
echo [Step 1/5] Checking prerequisites...

where node >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo   [ERROR] Node.js is not installed!
    echo   Please install Node.js from: https://nodejs.org/
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo   Node.js: !NODE_VERSION!

for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
echo   npm: v!NPM_VERSION!
echo   [OK] Prerequisites verified
echo.

REM ============================================================================
REM Step 2: Install dependencies (SKIP if node_modules exists)
REM ============================================================================
echo [Step 2/5] Checking dependencies...

if !FORCE_BUILD!==1 (
    if exist "node_modules" (
        echo   [FORCE] Removing node_modules for clean install...
        rmdir /s /q node_modules 2>nul
    )
)

if not exist "node_modules" (
    echo   [INSTALL] Installing dependencies...
    echo   [INFO] This takes 2-5 minutes on first run...
    call npm install --legacy-peer-deps
    if !ERRORLEVEL! neq 0 (
        echo   [ERROR] Failed to install dependencies!
        exit /b 1
    )
    echo   [OK] Dependencies installed
) else (
    echo   [SKIP] node_modules exists - using cached dependencies
)
echo.

REM ============================================================================
REM Step 3: Build React bundle (SKIP if build/ exists and not --force)
REM ============================================================================
echo [Step 3/5] React production bundle...

set NEED_REACT_BUILD=1

if !FORCE_BUILD!==1 (
    if exist "build" (
        echo   [FORCE] Removing build folder for clean rebuild...
        rmdir /s /q build 2>nul
    )
) else (
    if exist "build\index.html" (
        echo   [SKIP] build/index.html exists - using cached React bundle
        echo   [TIP] Use --force to rebuild React bundle
        set NEED_REACT_BUILD=0
    )
)

if !NEED_REACT_BUILD!==1 (
    echo   [BUILD] Building React bundle...
    echo   [INFO] This takes 1-2 minutes...
    call npm run build
    if !ERRORLEVEL! neq 0 (
        echo   [ERROR] React build failed!
        exit /b 1
    )
    echo   [OK] React build completed
)
echo.

REM ============================================================================
REM Step 4: Build Windows Installer (~3-5 minutes)
REM ============================================================================
echo [Step 4/5] Building Windows Installer...
echo   [INFO] This takes 3-5 minutes...
echo   [INFO] electron-builder is creating NSIS installer...
echo.

call npm run pack-installer
if !ERRORLEVEL! neq 0 (
    echo.
    echo   [ERROR] Installer build failed!
    echo.
    echo   Troubleshooting:
    echo   1. Close any programs using files in the dist folder
    echo   2. Run: rmdir /s /q dist
    echo   3. Try again with: build_installer.bat --force
    exit /b 1
)

echo   [OK] Installer built
echo.

REM ============================================================================
REM Step 5: Verify output
REM ============================================================================
echo [Step 5/5] Verifying output...

set FOUND_INSTALLER=0
for %%f in (dist\TradingBook*Setup*.exe) do (
    echo   [OK] Found: %%~nxf
    for %%A in ("%%f") do echo   [OK] Size: %%~zA bytes
    set FOUND_INSTALLER=1
)

if !FOUND_INSTALLER!==0 (
    for %%f in ("dist\TradingBook Setup*.exe") do (
        echo   [OK] Found: %%~nxf
        set FOUND_INSTALLER=1
    )
)

if !FOUND_INSTALLER!==0 (
    echo   [WARNING] Installer .exe not found in expected location
    echo   [INFO] Check dist folder manually
)

REM Calculate elapsed time
for /f "tokens=1-4 delims=:. " %%a in ("%TIME%") do (
    set /a END_H=%%a
    set /a END_M=%%b
    set /a END_S=%%c
)
set /a END_TOTAL=END_H*3600 + END_M*60 + END_S
set /a ELAPSED=END_TOTAL - START_TOTAL
if !ELAPSED! lss 0 set /a ELAPSED=ELAPSED + 86400
set /a ELAPSED_MIN=ELAPSED / 60
set /a ELAPSED_SEC=ELAPSED %% 60

echo.
echo ============================================================================
echo  BUILD COMPLETE!
echo ============================================================================
echo  Duration: !ELAPSED_MIN! min !ELAPSED_SEC! sec
echo  Output:   dist\
echo.
echo  Installer files:
dir /b dist\*Setup*.exe 2>nul
dir /b "dist\TradingBook Setup*.exe" 2>nul
echo.
echo  Next: Test the installer, then distribute with QuickStart guide
echo ============================================================================
echo   2. Share with users along with the Quick Start Guide
echo.
echo ============================================================
pause
