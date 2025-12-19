@echo off
REM ============================================================================
REM TradingBook - Quick Start Script
REM ============================================================================
REM Use this script to quickly launch TradingBook after initial setup
REM ============================================================================

setlocal enabledelayedexpansion

title TradingBook
color 0A

echo.
echo  ============================================================
echo   TradingBook - Quick Start
echo  ============================================================
echo.

REM Check if we're in the right directory
if not exist "package.json" (
    echo [ERROR] package.json not found!
    echo [ERROR] Please run this script from the TradingBook root directory.
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "node_modules" (
    echo [WARNING] node_modules not found!
    echo [INFO] Running initial setup...
    echo.
    call scripts\windows_setup.bat
    exit /b
)

REM Check for Node.js
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)

echo [INFO] Starting TradingBook...
echo [INFO] Press Ctrl+C to stop the application
echo.
echo  ============================================================
echo.

REM Start in development mode
call npm run electron-dev

echo.
echo [INFO] TradingBook has stopped.
pause
