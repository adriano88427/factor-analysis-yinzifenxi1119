@echo off
chcp 65001 >nul
echo Starting Filesystem MCP with correct configuration...
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

echo Starting Filesystem MCP server...
echo Allowed directory: %ALLOWED_DIR%
echo.

REM Start the filesystem MCP server with the correct directory
cd /d "%ALLOWED_DIR%"
node mcp-filesystem/index.js --allowed-directories "%ALLOWED_DIR%"

pause