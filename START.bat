@echo off
setlocal

REM Adaptive Notes Generator - Windows Startup Script

echo.
echo ============================================================
echo   Adaptive Notes Generator
echo   Starting Flask Server...
echo ============================================================
echo.

set "PYTHON_EXE="
set "VENV_PYTHON=%~dp0venv\Scripts\python.exe"

if exist "%VENV_PYTHON%" (
    "%VENV_PYTHON%" -c "import sys; print(sys.version)" >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_EXE=%VENV_PYTHON%"
    )
)

if not defined PYTHON_EXE (
    py -3.11 --version >nul 2>&1
    if not errorlevel 1 (
        echo Creating local virtual environment with Python 3.11...
        py -3.11 -m venv venv
        set "PYTHON_EXE=%VENV_PYTHON%"
    )
)

if not defined PYTHON_EXE (
    py --version >nul 2>&1
    if not errorlevel 1 (
        echo Creating local virtual environment with the default Python launcher...
        py -m venv venv
        set "PYTHON_EXE=%VENV_PYTHON%"
    )
)

if not defined PYTHON_EXE (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python is not installed or not in PATH
        pause
        exit /b 1
    )
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" -c "import flask, flask_cors, pymongo, docx, reportlab, dotenv" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    "%PYTHON_EXE%" -m pip install -r requirements.txt
)

if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs
if not exist "outputs\pdf" mkdir outputs\pdf
if not exist "outputs\docx" mkdir outputs\docx
if not exist "static\temp" mkdir static\temp

for /f "tokens=1,2 delims==" %%A in (env) do (
    if /I "%%A"=="PORT" set APP_PORT=%%B
)
if "%APP_PORT%"=="" set APP_PORT=5000

echo.
echo Starting application on http://127.0.0.1:%APP_PORT%
echo Press Ctrl+C to stop the server
echo.

"%PYTHON_EXE%" app.py
pause
