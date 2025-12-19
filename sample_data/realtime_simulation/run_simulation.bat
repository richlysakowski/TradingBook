@echo off
REM Run the Real-Time Candlestick Simulation App

echo ================================================
echo NQ FUTURES REAL-TIME CANDLESTICK SIMULATION
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

REM Check if database exists
if not exist "nq_tick_simulation.db" (
    echo WARNING: No tick data found!
    echo.
    echo Please run generate_sample_data.bat first to create the dataset.
    echo.
    choice /C YN /M "Generate sample data now?"
    if errorlevel 2 (
        echo Exiting...
        exit /b 0
    )
    call generate_sample_data.bat
    if errorlevel 1 exit /b 1
)

REM Check for Streamlit
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Installing Streamlit and dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting Streamlit app...
echo The app will open in your default browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server.
echo.

streamlit run realtime_candlestick_app.py
