@echo off
title Disk Space Transfer Tool

:: -------------------------------------------------------
:: Step 1: If not admin, re-launch this BAT as admin
:: -------------------------------------------------------
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Not running as administrator.
    echo [INFO] Requesting elevation via UAC...
    powershell -Command "Start-Process cmd -ArgumentList '/k \"%~f0\"' -Verb RunAs -WorkingDirectory '%~dp0'"
    exit /b
)

:: -------------------------------------------------------
:: Step 2: Now we have admin rights - run the tool
:: -------------------------------------------------------
cd /d "%~dp0"

echo ============================================
echo   Windows Disk Space Transfer Tool
echo   Wonderful Little Gadgets
echo ============================================
echo.
echo [INFO] Running as Administrator. OK
echo [INFO] Launching disk_transfer.py ...
echo.

python disk_transfer.py

if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Launch failed. Possible reasons:
    echo   1. Python 3.9+ is not installed or not in PATH
    echo   2. disk_transfer.py has an error
    echo.
    echo [INFO] Download Python: https://www.python.org/downloads/
)

echo.
echo [INFO] Program exited. Press any key to close this window.
pause >nul
