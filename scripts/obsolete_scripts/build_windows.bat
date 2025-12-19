@echo off
REM ============================================================================
REM TradingBook - Build Windows Executables
REM ============================================================================
REM Creates both installer and portable versions
REM ============================================================================

setlocal enabledelayedexpansion

title TradingBook Build
color 0B

echo.
echo  ============================================================
echo   TradingBook - Build Windows Executables
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
    echo [ERROR] node_modules not found!
    echo [INFO] Please run windows_setup.bat first.
    pause
    exit /b 1
)

echo [INFO] Building production React app...
call npm run build

if %ERRORLEVEL% neq 0 (
    echo [ERROR] React build failed!
    pause
    exit /b 1
)

echo.
echo [OK] React build complete!
echo.
echo What would you like to build?
echo.
echo   1. Windows Installer (NSIS .exe)
echo   2. Windows Portable (.exe)
echo   3. Both
echo.
set /p CHOICE="Enter choice (1-3): "

if "%CHOICE%"=="1" goto BUILD_INSTALLER
if "%CHOICE%"=="2" goto BUILD_PORTABLE
if "%CHOICE%"=="3" goto BUILD_BOTH
goto BUILD_BOTH

:BUILD_INSTALLER
echo.
echo [INFO] Building Windows Installer...
call npx electron-builder --win nsis
goto DONE

:BUILD_PORTABLE
echo.
echo [INFO] Building Windows Portable...
call npx electron-builder --win portable
goto DONE

:BUILD_BOTH
echo.
echo [INFO] Building both Installer and Portable...
call npm run build-windows-both
goto DONE

:DONE
if %ERRORLEVEL% equ 0 (
    echo.
    echo [OK] Build complete!
    echo [INFO] Output files are in the dist\ folder:
    echo.
    dir /b dist\*.exe 2>nul
    echo.
    start dist
) else (
    echo.
    echo [ERROR] Build failed! Check the output above for errors.
)

echo.
pause
