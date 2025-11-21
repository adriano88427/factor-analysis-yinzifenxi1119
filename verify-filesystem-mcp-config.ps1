# Filesystem MCP 配置验证工具

Write-Host "========================================" -ForegroundColor Green
Write-Host "Filesystem MCP 配置验证工具" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 检查项目目录
Write-Host "[1/4] 检查项目目录..." -ForegroundColor Yellow
if (Test-Path "c:\Users\NINGMEI\Documents\trae_projects\WEIBO") {
    Write-Host "✓ 项目目录存在: c:\Users\NINGMEI\Documents\trae_projects\WEIBO" -ForegroundColor Green
} else {
    Write-Host "✗ 项目目录不存在" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 检查MCP服务器文件
Write-Host ""
Write-Host "[2/4] 检查MCP服务器文件..." -ForegroundColor Yellow
if (Test-Path "c:\Users\NINGMEI\Documents\trae_projects\WEIBO\mcp-filesystem\index.js") {
    Write-Host "✓ MCP服务器文件存在" -ForegroundColor Green
} else {
    Write-Host "✗ MCP服务器文件不存在" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 检查配置文件
Write-Host ""
Write-Host "[3/4] 检查配置文件..." -ForegroundColor Yellow
if (Test-Path "c:\Users\NINGMEI\Documents\trae_projects\WEIBO\filesystem-mcp-config.json") {
    Write-Host "✓ 配置文件存在" -ForegroundColor Green
} else {
    Write-Host "✗ 配置文件不存在" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 显示IDE配置信息
Write-Host ""
Write-Host "[4/4] 显示IDE配置信息..." -ForegroundColor Yellow
Write-Host ""
Write-Host "请在您的IDE中使用以下配置:" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "JSON配置内容:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "{"
Write-Host '  "mcpServers": {'
Write-Host '    "filesystem": {'
Write-Host '      "command": "node",'
Write-Host '      "args": ["c:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO\\mcp-filesystem\\index.js", "--allowed-directories", "c:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO"],'
Write-Host '      "env": {}'
Write-Host "    }"
Write-Host "  }"
Write-Host "}"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "注意事项:" -ForegroundColor Magenta
Write-Host "1. 确保IDE使用此配置，而不是全局安装的版本" -ForegroundColor White
Write-Host "2. 配置完成后重启IDE" -ForegroundColor White
Write-Host "3. 如果仍有问题，尝试使用不同的服务器名称，如'local-filesystem'" -ForegroundColor White
Write-Host ""
Write-Host "配置文件位置: c:\Users\NINGMEI\Documents\trae_projects\WEIBO\filesystem-mcp-config.json" -ForegroundColor Gray
Write-Host "详细指南: c:\Users\NINGMEI\Documents\trae_projects\WEIBO\IDE配置Filesystem MCP详细指南.md" -ForegroundColor Gray
Write-Host ""
Read-Host "按Enter键退出"