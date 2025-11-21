# Shell Integration 快速诊断和修复脚本
# 适用于 TRAE IDE + Cline 插件环境

Write-Host "=== Shell Integration 诊断和修复脚本 ===" -ForegroundColor Cyan
Write-Host "当前环境: TRAE IDE + Cline 插件" -ForegroundColor Yellow

# 1. 检查当前环境
Write-Host "`n1. 检查当前环境配置..." -ForegroundColor Green

Write-Host "PowerShell 版本:" -NoNewline
$PSVersionTable | Select-Object PSVersion, PSEdition, BuildVersion | Format-List

# 2. 检查执行策略
Write-Host "`n2. 检查 PowerShell 执行策略..." -ForegroundColor Green
$ExecutionPolicy = Get-ExecutionPolicy
Write-Host "当前执行策略: $ExecutionPolicy" -ForegroundColor $(if ($ExecutionPolicy -eq 'Restricted') { 'Red' } else { 'Green' })

if ($ExecutionPolicy -eq 'Restricted') {
    Write-Host "建议设置执行策略为 RemoteSigned" -ForegroundColor Yellow
    Read-Host "是否要设置执行策略为 RemoteSigned？(y/n)"
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Write-Host "执行策略已更新" -ForegroundColor Green
}

# 3. 检查配置文件
Write-Host "`n3. 检查 PowerShell 配置文件..." -ForegroundColor Green
$ProfilePath = $PROFILE
Write-Host "配置文件路径: $ProfilePath" -ForegroundColor Cyan

if (!(Test-Path $ProfilePath)) {
    Write-Host "配置文件不存在，正在创建..." -ForegroundColor Yellow
    New-Item -Type File -Path $ProfilePath -Force | Out-Null
    Write-Host "配置文件已创建" -ForegroundColor Green
} else {
    Write-Host "配置文件存在" -ForegroundColor Green
}

# 4. 检查环境变量
Write-Host "`n4. 检查相关环境变量..." -ForegroundColor Green

$envVars = @{
    'PATH' = $env:PATH
    'COMSPEC' = $env:COMSPEC
    'TERM_PROGRAM' = $env:TERM_PROGRAM
    'VSCODE_INJECTION' = $env:VSCODE_INJECTION
}

foreach ($var in $envVars.Keys) {
    if ($envVars[$var]) {
        Write-Host "$var: 已设置" -ForegroundColor Green
    } else {
        Write-Host "$var: 未设置" -ForegroundColor Yellow
    }
}

# 5. 检查 PowerShell 可执行文件
Write-Host "`n5. 检查 PowerShell 可执行文件..." -ForegroundColor Green
try {
    $powershellPath = Get-Command powershell -ErrorAction Stop
    Write-Host "PowerShell 路径: $($powershellPath.Source)" -ForegroundColor Green
} catch {
    Write-Host "PowerShell 未找到或不可用" -ForegroundColor Red
}

# 6. 提供 TRAE IDE 特定建议
Write-Host "`n=== TRAE IDE 特定设置建议 ===" -ForegroundColor Cyan

Write-Host "6. TRAE IDE 设置检查项:" -ForegroundColor Green
Write-Host "   - 文件 → 设置 → 搜索 'Terminal'" -ForegroundColor White
Write-Host "   - 确保启用 'Shell Integration'" -ForegroundColor White
Write-Host "   - 设置默认终端为 PowerShell" -ForegroundColor White

Write-Host "7. Cline 插件设置检查项:" -ForegroundColor Green
Write-Host "   - 文件 → 设置 → 扩展 → Cline" -ForegroundColor White
Write-Host "   - 确保启用 Shell Integration" -ForegroundColor White
Write-Host "   - 确保启用 Command Output Capture" -ForegroundColor White

# 8. 创建测试脚本
Write-Host "`n8. 创建 Shell Integration 测试脚本..." -ForegroundColor Green
$testScriptPath = Join-Path $env:TEMP "Shell_Integration_Test.ps1"
$testScriptContent = @"
# Shell Integration 测试脚本
Write-Host "=== Shell Integration 测试 ===" -ForegroundColor Cyan

# 测试基本命令
Write-Host "测试 1: 基本输出"
echo "这是测试输出"

Write-Host "测试 2: 变量输出"
`$TestVar = "测试变量"
echo `$TestVar

Write-Host "测试 3: 系统信息"
Get-Date
`$PSVersionTable

Write-Host "测试 4: 环境变量"
echo `$env:PATH
echo `$env:COMSPEC

Write-Host "`n=== 测试完成 ===" -ForegroundColor Green
"@

$testScriptContent | Out-File -FilePath $testScriptPath -Encoding UTF8
Write-Host "测试脚本已创建: $testScriptPath" -ForegroundColor Green

# 9. 验证修复建议
Write-Host "`n=== 修复建议总结 ===" -ForegroundColor Cyan
Write-Host "如果 Shell Integration 仍然不可用，请尝试以下步骤:" -ForegroundColor Yellow

Write-Host "1. 重启 TRAE IDE" -ForegroundColor White
Write-Host "2. 在 TRAE IDE 中打开新终端" -ForegroundColor White
Write-Host "3. 运行测试脚本: powershell -ExecutionPolicy Bypass -File `"$testScriptPath`"" -ForegroundColor White
Write-Host "4. 检查终端设置和插件配置" -ForegroundColor White

# 10. 自动修复 PowerShell 配置文件
Write-Host "`n10. 正在优化 PowerShell 配置文件..." -ForegroundColor Green
$optimizedProfile = @"
# 优化的 PowerShell 配置

# 设置输出编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
`$OutputEncoding = [System.Text.Encoding]::UTF8

# 设置提示符
function prompt {
    `$currentPath = Split-Path -Leaf (Get-Location)
    Write-Host "PS " -NoNewline -ForegroundColor Cyan
    Write-Host "`$currentPath" -NoNewline -ForegroundColor Yellow
    Write-Host ">" -NoNewline -ForegroundColor Cyan
    return " "
}

# 别名设置
Set-Alias ll Get-ChildItem
Set-Alias grep Select-String

# 快捷函数
function Show-SystemInfo {
    Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, TotalPhysicalMemory
}

# Shell Integration 兼容性
`$env:TERM = "xterm-color"
`$env:TERM_PROGRAM = "TRAE"
"@

# 只有在配置文件存在时才更新
if (Test-Path $ProfilePath) {
    $optimizedProfile | Out-File -FilePath $ProfilePath -Encoding UTF8
    Write-Host "PowerShell 配置文件已优化" -ForegroundColor Green
}

Write-Host "`n=== 诊断和修复完成 ===" -ForegroundColor Cyan
Write-Host "请重启 TRAE IDE 并测试终端功能" -ForegroundColor Yellow
Write-Host "如果问题仍然存在，请查看 'Shell Integration 问题解决方案.md' 获取更详细的解决方案" -ForegroundColor Yellow
