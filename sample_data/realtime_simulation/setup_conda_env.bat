@echo off
REM Setup NQ Simulation Conda Environment
REM Creates the nq_sims_city environment with all dependencies

echo ================================================
echo NQ SIMULATION - CONDA ENVIRONMENT SETUP
echo ================================================
echo.

cd /d "%~dp0"

REM Check if conda is available
where conda >nul 2>&1
if errorlevel 1 (
    echo ERROR: Conda not found in PATH
    echo Please install Anaconda or Miniconda first
    pause
    exit /b 1
)

REM Check if environment already exists
conda env list | findstr /C:"nq_sims_city" >nul 2>&1
if not errorlevel 1 (
    echo Environment 'nq_sims_city' already exists.
    choice /C YN /M "Do you want to update it?"
    if errorlevel 2 (
        echo Skipping environment update.
        goto :activate
    )
    echo.
    echo Updating environment...
    conda env update -f environment.yml --prune
    goto :activate
)

echo Creating new conda environment 'nq_sims_city'...
echo This may take a few minutes...
echo.

conda env create -f environment.yml

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create conda environment
    echo.
    echo Trying alternative installation method...
    echo.
    
    REM Fallback: create minimal env and install packages separately
    conda create -n nq_sims_city python=3.11 -y
    if errorlevel 1 (
        echo ERROR: Could not create environment
        pause
        exit /b 1
    )
    
    echo Activating environment for package installation...
    call conda activate nq_sims_city
    
    echo Installing conda packages from conda-forge...
    conda install -c conda-forge numpy polars pyarrow streamlit -y
    
    echo Installing pip packages...
    pip install streamlit-echarts streamlit-autorefresh
)

:activate
echo.
echo ================================================
echo ENVIRONMENT SETUP COMPLETE!
echo ================================================
echo.
echo To activate the environment, run:
echo   conda activate nq_sims_city
echo.
echo Then generate data and run the app:
echo   python generate_tick_data.py --days 5 --seed 42
echo   streamlit run realtime_candlestick_app.py
echo.
pause
