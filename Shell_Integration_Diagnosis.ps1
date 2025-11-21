# Shell Integration Diagnosis and Fix Script
# For TRAE IDE + Cline Plugin Environment

Write-Host "=== Shell Integration Diagnosis and Fix Script ===" -ForegroundColor Cyan
Write-Host "Current Environment: TRAE IDE + Cline Plugin" -ForegroundColor Yellow

# 1. Check current environment
Write-Host "`n1. Checking current environment configuration..." -ForegroundColor Green

Write-Host "PowerShell Version:" -NoNewline
$PSVersionTable | Select-Object PSVersion, PSEdition, BuildVersion | Format-List

# 2. Check execution policy
Write-Host "`n2. Checking PowerShell execution policy..." -ForegroundColor Green
$ExecutionPolicy = Get-ExecutionPolicy
Write-Host "Current execution policy: $ExecutionPolicy" -ForegroundColor $(if ($ExecutionPolicy -eq 'Restricted') { 'Red' } else { 'Green' })

if ($ExecutionPolicy -eq 'Restricted') {
    Write-Host "Recommendation: Set execution policy to RemoteSigned" -ForegroundColor Yellow
    Read-Host "Do you want to set execution policy to RemoteSigned? (y/n)"
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Write-Host "Execution policy updated" -ForegroundColor Green
}

# 3. Check profile configuration
Write-Host "`n3. Checking PowerShell profile configuration..." -ForegroundColor Green
$ProfilePath = $PROFILE
Write-Host "Profile path: $ProfilePath" -ForegroundColor Cyan

if (!(Test-Path $ProfilePath)) {
    Write-Host "Profile does not exist, creating..." -ForegroundColor Yellow
    New-Item -Type File -Path $ProfilePath -Force | Out-Null
    Write-Host "Profile created" -ForegroundColor Green
} else {
    Write-Host "Profile exists" -ForegroundColor Green
}

# 4. Check environment variables
Write-Host "`n4. Checking relevant environment variables..." -ForegroundColor Green

$envVars = @{
    'PATH' = $env:PATH
    'COMSPEC' = $env:COMSPEC
    'TERM_PROGRAM' = $env:TERM_PROGRAM
    'VSCODE_INJECTION' = $env:VSCODE_INJECTION
}

foreach ($var in $envVars.Keys) {
    if ($envVars[$var]) {
        Write-Host "$var: Set" -ForegroundColor Green
    } else {
        Write-Host "$var: Not set" -ForegroundColor Yellow
    }
}

# 5. Check PowerShell executable
Write-Host "`n5. Checking PowerShell executable..." -ForegroundColor Green
try {
    $powershellPath = Get-Command powershell -ErrorAction Stop
    Write-Host "PowerShell path: $($powershellPath.Source)" -ForegroundColor Green
} catch {
    Write-Host "PowerShell not found or not available" -ForegroundColor Red
}

# 6. Provide TRAE IDE specific recommendations
Write-Host "`n=== TRAE IDE Specific Settings Recommendations ===" -ForegroundColor Cyan

Write-Host "6. TRAE IDE settings check:" -ForegroundColor Green
Write-Host "   - File → Settings → Search 'Terminal'" -ForegroundColor White
Write-Host "   - Ensure 'Shell Integration' is enabled" -ForegroundColor White
Write-Host "   - Set default terminal to PowerShell" -ForegroundColor White

Write-Host "7. Cline plugin settings check:" -ForegroundColor Green
Write-Host "   - File → Settings → Extensions → Cline" -ForegroundColor White
Write-Host "   - Ensure Shell Integration is enabled" -ForegroundColor White
Write-Host "   - Ensure Command Output Capture is enabled" -ForegroundColor White

# 8. Create test script
Write-Host "`n8. Creating Shell Integration test script..." -ForegroundColor Green
$testScriptPath = Join-Path $env:TEMP "Shell_Integration_Test.ps1"
$testScriptContent = @"
# Shell Integration Test Script
Write-Host "=== Shell Integration Test ===" -ForegroundColor Cyan

# Test basic commands
Write-Host "Test 1: Basic Output"
echo "This is test output"

Write-Host "Test 2: Variable Output"
`$TestVar = "Test Variable"
echo `$TestVar

Write-Host "Test 3: System Information"
Get-Date
`$PSVersionTable

Write-Host "Test 4: Environment Variables"
echo `$env:PATH
echo `$env:COMSPEC

Write-Host "`n=== Test Complete ===" -ForegroundColor Green
"@

$testScriptContent | Out-File -FilePath $testScriptPath -Encoding UTF8
Write-Host "Test script created: $testScriptPath" -ForegroundColor Green

# 9. Provide fix recommendations
Write-Host "`n=== Fix Recommendations Summary ===" -ForegroundColor Cyan
Write-Host "If Shell Integration is still not working, try the following steps:" -ForegroundColor Yellow

Write-Host "1. Restart TRAE IDE" -ForegroundColor White
Write-Host "2. Open new terminal in TRAE IDE" -ForegroundColor White
Write-Host "3. Run test script: powershell -ExecutionPolicy Bypass -File `"$testScriptPath`"" -ForegroundColor White
Write-Host "4. Check terminal settings and plugin configuration" -ForegroundColor White

# 10. Auto-fix PowerShell profile
Write-Host "`n10. Optimizing PowerShell profile configuration..." -ForegroundColor Green
$optimizedProfile = @"
# Optimized PowerShell Configuration

# Set output encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
`$OutputEncoding = [System.Text.Encoding]::UTF8

# Set prompt
function prompt {
    `$currentPath = Split-Path -Leaf (Get-Location)
    Write-Host "PS " -NoNewline -ForegroundColor Cyan
    Write-Host "`$currentPath" -NoNewline -ForegroundColor Yellow
    Write-Host ">" -NoNewline -ForegroundColor Cyan
    return " "
}

# Alias settings
Set-Alias ll Get-ChildItem
Set-Alias grep Select-String

# Utility functions
function Show-SystemInfo {
    Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, TotalPhysicalMemory
}

# Shell Integration compatibility
`$env:TERM = "xterm-color"
`$env:TERM_PROGRAM = "TRAE"
"@

# Only update if profile exists
if (Test-Path $ProfilePath) {
    $optimizedProfile | Out-File -FilePath $ProfilePath -Encoding UTF8
    Write-Host "PowerShell profile optimized" -ForegroundColor Green
}

Write-Host "`n=== Diagnosis and Fix Complete ===" -ForegroundColor Cyan
Write-Host "Please restart TRAE IDE and test terminal functionality" -ForegroundColor Yellow
Write-Host "If problems persist, refer to 'Shell Integration 问题解决方案.md' for detailed solutions" -ForegroundColor Yellow
