@echo off
chcp 65001 >nul
echo Testing Filesystem MCP Configuration
echo ===================================
echo.

REM Set the allowed directory to your actual project path
set ALLOWED_DIR=C:\Users\NINGMEI\Documents\trae_projects\WEIBO

REM Check if the directory exists
if not exist "%ALLOWED_DIR%" (
    echo ERROR: Directory does not exist: %ALLOWED_DIR%
    echo Please update the ALLOWED_DIR variable in this script
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js first
    pause
    exit /b 1
)

REM Check if the filesystem server exists
if not exist "%ALLOWED_DIR%\mcp-filesystem\index.js" (
    echo ERROR: Filesystem MCP server not found at %ALLOWED_DIR%\mcp-filesystem\index.js
    echo Please make sure the filesystem MCP is properly installed
    pause
    exit /b 1
)

echo All checks passed!
echo.
echo Directory: %ALLOWED_DIR%
echo Node.js version:
node --version
echo.
echo Filesystem server files:
dir /b "%ALLOWED_DIR%\mcp-filesystem\"
echo.
echo To use Filesystem MCP with your IDE, you need to:
echo 1. Configure your IDE to use the filesystem-mcp-config.json file
echo 2. Or update your IDE's MCP settings to include:
echo    - Command: node
echo    - Arguments: "%ALLOWED_DIR%\mcp-filesystem\index.js" --allowed-directories "%ALLOWED_DIR%"
echo.
pause