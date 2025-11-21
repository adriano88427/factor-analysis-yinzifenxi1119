@echo off
echo Cline Telemetry Settings Fix Tool
echo ==================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Python found, running diagnostic...
    python telemetry_check.py
) else (
    echo Python not found in PATH
    echo.
    echo Please enable telemetry manually in Trae IDE:
    echo 1. Open Trae IDE
    echo 2. Press Ctrl+, to open settings
    echo 3. Search for "telemetry"
    echo 4. Enable the following options:
    echo    - Enable Telemetry
    echo    - Enable Crash Reporting
    echo    - Enable Usage Reporting
    echo 5. Save and restart Trae IDE
    echo.
    echo Alternative: You can also edit the settings JSON file directly:
    echo Location: %USERPROFILE%\AppData\Roaming\Trae\settings.json
    echo.
    echo Add these settings to enable telemetry:
    echo {
    echo   "telemetry.enableTelemetry": true,
    echo   "telemetry.enableCrashReporting": true,
    echo   "telemetry.enableUsageReporting": true
    echo }
)

pause
