@echo off
REM ====================================================================
REM LifeLine Complete Startup Script
REM ====================================================================
REM This script starts the complete LifeLine application

cd /d D:\newalert

echo.
echo ====================================================================
echo    LIFELINE - Emergency SOS Application
echo ====================================================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo [1/4] Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo [1/4] Virtual environment already active
)

echo.
echo [2/4] Initializing database...
python -c "from newalert.backend.database import init_db; init_db(); print('✓ Database ready')"

if errorlevel 1 (
    echo ❌ Database initialization failed
    pause
    exit /b 1
)

echo.
echo [3/4] Starting backend server...
echo        Host: 182.18.2.8
echo        Port: 8000
echo        URL:  http://182.18.2.8:8000
echo.
echo ====================================================================
echo Press Ctrl+C to stop the server
echo ====================================================================
echo.

REM Start the main application server
python -m uvicorn newalert.backend.main:app --reload --host 182.18.2.8 --port 8000

echo.
echo Server stopped.
pause
