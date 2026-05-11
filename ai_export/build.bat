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

echo [1/3] Installing PyInstaller...
pip install pyinstaller
echo.

echo [2/3] Building exe, please wait...
pyinstaller --onefile --windowed ^
    --name="AI-Export" ^
    --add-data "app.py;." ^
    --add-data "core;core" ^
    --add-data "plugins;plugins" ^
    main.py
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
