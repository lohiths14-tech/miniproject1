@echo off
echo ====================================
echo AI Grading System - Starting Server
echo ====================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Error: Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting Flask application...
echo.
echo Server will be available at:
echo - Local: http://127.0.0.1:5000
echo - Network: http://192.168.x.x:5000
echo.
echo Test Accounts:
echo Student: student@example.com / password123
echo Lecturer: lecturer@example.com / password123
echo.
echo Press Ctrl+C to stop the server
echo ====================================
echo.

py app.py