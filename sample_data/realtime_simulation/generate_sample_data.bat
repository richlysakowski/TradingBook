@echo off
REM Generate NQ Futures Tick Data for Real-Time Simulation
REM Creates a 5-day dataset with ~288,000 tick records

echo ================================================
echo NQ FUTURES TICK DATA GENERATOR
echo ================================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.8+ or activate your conda environment
    pause
    exit /b 1
)

REM Check for required packages
echo Checking dependencies...
python -c "import numpy, pandas" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install numpy pandas
)

echo.
echo Generating 5 days of 1-second tick data...
echo This may take 2-3 minutes...
echo.

python generate_tick_data.py --days 5 --seed 42 --aggregate

if errorlevel 1 (
    echo.
    echo ERROR: Data generation failed
    pause
    exit /b 1
)

echo.
echo ================================================
echo DATA GENERATION COMPLETE!
echo ================================================
echo.
echo Database created: nq_tick_simulation.db
echo.
echo To run the simulation app:
echo   streamlit run realtime_candlestick_app.py
echo.
pause
