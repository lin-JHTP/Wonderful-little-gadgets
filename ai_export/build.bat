@echo off
cd /d "%~dp0"

echo ==============================
echo   AI Export Tool - Build
echo ==============================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python and add it to PATH.
    pause
    exit /b 1
)

echo [1/3] Checking PyInstaller...
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found, installing...
    pip install pyinstaller
) else (
    echo PyInstaller already installed, skipping.
)
echo.

echo [2/3] Building exe, please wait...
pyinstaller --onefile --windowed --name="AI-Export" main.py
echo.

if exist "dist\AI-Export.exe" (
    echo [3/3] Build successful!
    echo exe is located at: %~dp0dist\AI-Export.exe
    echo.
    explorer dist
) else (
    echo [ERROR] Build failed. Please check the log above.
)

pause
