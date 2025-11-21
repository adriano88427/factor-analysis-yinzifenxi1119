@echo off
chcp 65001 >nul

echo ==================================================
echo    MCP File System 中国网络环境优化脚本
echo ==================================================
echo.

echo 📦 当前npm配置：
npm config get registry
echo.

echo 🔧 正在为中国用户配置MCP File System...
echo.

echo 📦 配置npm镜像源为淘宝...
npm config set registry https://registry.npmmirror.com
npm config set disturl https://npmmirror.com/dist
npm config set electron_mirror https://npmmirror.com/mirrors/electron/
npm config set sass_binary_site https://npmmirror.com/mirrors/node-sass/

echo.
echo 📥 安装cnpm淘宝客户端...
npm install -g cnpm --registry=https://registry.npmmirror.com

echo.
echo 🧹 清理npm缓存...
npm cache clean --force

echo.
echo 📋 检查mcp-filesystem目录...
if not exist "mcp-filesystem" (
    echo ❌ 未找到mcp-filesystem目录
    echo 请确保在正确的目录中运行此脚本
    pause
    exit /b 1
)

cd mcp-filesystem

echo.
echo 📦 安装MCP依赖包...
cnpm install

echo.
echo ✅ 验证安装结果...
if exist "node_modules\@modelcontextprotocol" (
    echo 🎉 MCP依赖安装成功！
    echo.
    echo 🚀 启动方式：
    echo    cd mcp-filesystem
    echo    node index.js
    echo.
    echo 或者：
    echo    cd mcp-filesystem
    echo    npm start
) else (
    echo ❌ 安装失败，可能存在以下问题：
    echo    1. 网络连接问题
    echo    2. 防火墙阻止访问
    echo    3. npm配置错误
    echo.
    echo 💡 解决方案：
    echo    1. 检查网络连接
    echo    2. 尝试使用VPN或代理
    echo    3. 联系网络管理员确认npm访问权限
)

echo.
echo 📋 更新后的npm配置：
npm config get registry

echo.
echo ==================================================
echo    脚本执行完成！
echo ==================================================
pause
