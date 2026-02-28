@echo off
REM Start the HTTPS server with self-signed certificate
echo Starting LifeLine HTTPS Server...
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check if openssl is available
where openssl >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  OpenSSL not found. Installing...
    pip install certifi pyopenssl -q
)

REM Run HTTPS server
echo.
echo 🔐 Starting HTTPS server on https://182.18.2.8:8000
echo ⚠️  Browser will show security warning - click "Advanced" then "Proceed"
echo.
python -m uvicorn newalert.backend.main:app --host 182.18.2.8 --port 8000 --reload --ssl-certfile certs/cert.pem --ssl-keyfile certs/key.pem

pause
