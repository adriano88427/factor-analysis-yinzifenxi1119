@echo off
chcp 65001 > nul
echo.
echo ========================================
echo Filesystem MCP 配置验证工具
echo ========================================
echo.

echo [1/4] 检查项目目录...
if exist "c:\Users\NINGMEI\Documents\trae_projects\WEIBO" (
    echo ✓ 项目目录存在: c:\Users\NINGMEI\Documents\trae_projects\WEIBO
) else (
    echo ✗ 项目目录不存在
    pause
    exit /b 1
)

echo.
echo [2/4] 检查MCP服务器文件...
if exist "c:\Users\NINGMEI\Documents\trae_projects\WEIBO\mcp-filesystem\index.js" (
    echo ✓ MCP服务器文件存在
) else (
    echo ✗ MCP服务器文件不存在
    pause
    exit /b 1
)

echo.
echo [3/4] 检查配置文件...
if exist "c:\Users\NINGMEI\Documents\trae_projects\WEIBO\filesystem-mcp-config.json" (
    echo ✓ 配置文件存在
) else (
    echo ✗ 配置文件不存在
    pause
    exit /b 1
)

echo.
echo [4/4] 显示IDE配置信息...
echo.
echo 请在您的IDE中使用以下配置：
echo.
echo ========================================
echo JSON配置内容:
echo ========================================
echo {
echo   "mcpServers": {
echo     "filesystem": {
echo       "command": "node",
echo       "args": ["c:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO\\mcp-filesystem\\index.js", "--allowed-directories", "c:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO"],
echo       "env": {}
echo     }
echo   }
echo }
echo ========================================
echo.
echo 注意事项:
echo 1. 确保IDE使用此配置，而不是全局安装的版本
echo 2. 配置完成后重启IDE
echo 3. 如果仍有问题，尝试使用不同的服务器名称，如"local-filesystem"
echo.
echo 配置文件位置: c:\Users\NINGMEI\Documents\trae_projects\WEIBO\filesystem-mcp-config.json
echo 详细指南: c:\Users\NINGMEI\Documents\trae_projects\WEIBO\IDE配置Filesystem MCP详细指南.md
echo.
pause