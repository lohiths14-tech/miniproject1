@echo off
echo ====================================
echo AI Grading System - Setup Script
echo ====================================
echo.

echo [1/4] Creating virtual environment...
py -m venv venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment
    echo Please ensure Python 3.8+ is installed
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/4] Setup complete!
echo.
echo ====================================
echo SETUP COMPLETED SUCCESSFULLY!
echo ====================================
echo.
echo To run the application:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Start the server: py app.py
echo 3. Open browser: http://127.0.0.1:5000
echo.
echo Test Accounts:
echo Student: student@example.com / password123
echo Lecturer: lecturer@example.com / password123
echo.
pause