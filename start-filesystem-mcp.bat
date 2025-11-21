@echo off
chcp 65001 >nul

echo ==================================================
echo    Filesystem MCP 启动脚本（修复版）
echo ==================================================
echo.

echo 📂 设置允许访问的目录...
set ALLOWED_DIR=C:\Users\NINGMEI\Documents\trae_projects\WEIBO

echo 🚀 启动Filesystem MCP服务器...
echo 允许访问的目录: %ALLOWED_DIR%
echo.

cd /d "%~dp0mcp-filesystem"
node index.js "%ALLOWED_DIR%"

echo.
echo ==================================================
echo    如果看到错误信息，请检查：
echo    1. 目录路径是否正确
echo    2. mcp-filesystem目录是否存在
echo    3. node.js是否已正确安装
echo ==================================================
pause