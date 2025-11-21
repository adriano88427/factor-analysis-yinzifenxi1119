@echo off

echo ==================================================
echo    Node.js + MCP File System Installation Script
echo ==================================================
echo.

echo Checking Node.js installation...
echo.

node --version 2>nul
if %errorlevel% neq 0 (
    echo.
    echo Node.js is NOT installed!
    echo.
    echo Please install Node.js first:
    echo 1. Visit https://nodejs.org/zh-cn/
    echo 2. Download and install LTS version
    echo 3. Run this script again
    echo.
    pause
    exit /b 0
)

echo Node.js is installed!
node --version
echo.

echo Checking npm installation...
echo.

npm --version 2>nul
if %errorlevel% neq 0 (
    echo npm is NOT installed. Please reinstall Node.js.
    echo npm is usually installed with Node.js
    echo.
    pause
    exit /b 1
)

echo npm is installed!
npm --version
echo.

echo ==================================================
echo    Starting MCP File System Configuration
echo ==================================================
echo.

echo Current npm registry:
npm config get registry
echo.

echo Configuring taobao registry...
npm config set registry https://registry.npmmirror.com
echo Registry configured successfully
echo.

echo Checking mcp-filesystem directory...
if not exist "mcp-filesystem" (
    echo ERROR: mcp-filesystem directory not found
    echo Please run this script in the parent directory of mcp-filesystem
    echo.
    echo Current directory: %cd%
    echo.
    pause
    exit /b 1
)

cd mcp-filesystem
echo Found mcp-filesystem directory
echo.

echo Installing MCP dependencies...
echo Please wait, this may take several minutes...
echo.

if exist package.json (
    echo Installing packages with npm...
    npm install
    echo Dependencies installed successfully
) else (
    echo ERROR: package.json not found
    echo The mcp-filesystem directory may be incomplete
    echo.
    pause
    exit /b 1
)

echo.
echo Verifying installation...
echo.

if exist "node_modules\@modelcontextprotocol" (
    echo.
    echo ================================================
    echo SUCCESS! MCP dependencies installed!
    echo ================================================
    echo.
    echo To start MCP server:
    echo   cd mcp-filesystem
    echo   node index.js
    echo.
    echo Or:
    echo   cd mcp-filesystem
    echo   npm start
    echo.
) else (
    echo.
    echo Installation failed. Possible issues:
    echo   1. Network connection problems
    echo   2. Firewall blocking access
    echo   3. npm configuration errors
    echo.
    echo Solutions:
    echo   1. Check network connection
    echo   2. Try using VPN or proxy
    echo   3. Contact network administrator for npm access
)

echo.
echo Final npm registry configuration:
npm config get registry

echo.
echo ==================================================
echo Installation completed!
echo ==================================================
echo.
pause
