# Cline Telemetry Settings Fix Tool - PowerShell Version
# For advanced users who prefer PowerShell

Write-Host "Cline Telemetry Settings Fix Tool (PowerShell)" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
Write-Host ""

# Check if Trae IDE settings file exists
$homeDir = $env:USERPROFILE
$settingsPaths = @(
    "$homeDir\AppData\Roaming\Trae\settings.json",
    "$homeDir\AppData\Local\Trae\User\settings.json"
)

Write-Host "Checking for Trae IDE settings files..." -ForegroundColor Yellow

$settingsFound = $false
$telemetryEnabled = $false

foreach ($path in $settingsPaths) {
    if (Test-Path $path) {
        Write-Host "Found settings file: $path" -ForegroundColor Green
        $settingsFound = $true
        
        try {
            $settings = Get-Content $path | ConvertFrom-Json
            
            # Check telemetry settings
            $telemetryKeys = @(
                'telemetry.enableTelemetry',
                'telemetry.enableCrashReporting',
                'telemetry.enableUsageReporting',
                'telemetry.telemetryEnabled'
            )
            
            foreach ($key in $telemetryKeys) {
                if ($settings.PSObject.Properties.Name -contains $key) {
                    $value = $settings.$key
                    $status = if ($value) { "ENABLED" } else { "DISABLED" }
                    Write-Host "  $key`: $status" -ForegroundColor $(if ($value) { "Green" } else { "Red" })
                    if ($value) { $telemetryEnabled = $true }
                }
            }
            
            # Check if no telemetry settings found
            $hasTelemetrySettings = $telemetryKeys | Where-Object { $settings.PSObject.Properties.Name -contains $_ }
            if (-not $hasTelemetrySettings) {
                Write-Host "  No telemetry settings found" -ForegroundColor Yellow
            }
            
        } catch {
            Write-Host "  Error reading settings: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

if (-not $settingsFound) {
    Write-Host "No Trae IDE settings files found" -ForegroundColor Red
    Write-Host "Make sure Trae IDE is installed and has been used at least once" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Manual steps:" -ForegroundColor Cyan
    Write-Host "1. Open Trae IDE"
    Write-Host "2. Press Ctrl+, to open settings"
    Write-Host "3. Search for 'telemetry'"
    Write-Host "4. Enable: Enable Telemetry, Enable Crash Reporting, Enable Usage Reporting"
    Write-Host "5. Save and restart Trae IDE"
    exit
}

if (-not $telemetryEnabled) {
    Write-Host "`nTelemetry settings appear to be disabled" -ForegroundColor Yellow
    
    $response = Read-Host "Attempt to fix automatically? (y/n)"
    if ($response -eq "y" -or $response -eq "Y" -or $response -eq "yes") {
        Write-Host "`nAttempting to fix telemetry settings..." -ForegroundColor Cyan
        
        $targetPath = $settingsPaths[0]  # Primary path
        
        try {
            # Ensure directory exists
            $directory = Split-Path $targetPath -Parent
            if (-not (Test-Path $directory)) {
                New-Item -ItemType Directory -Path $directory -Force | Out-Null
            }
            
            # Read existing settings or create new
            if (Test-Path $targetPath) {
                $settings = Get-Content $targetPath | ConvertFrom-Json
                Write-Host "Backed up existing settings" -ForegroundColor Green
                $backupPath = $targetPath -replace '\.json$', '.json.backup'
                Copy-Item $targetPath $backupPath
            } else {
                $settings = New-Object PSCustomObject
            }
            
            # Add telemetry settings
            $settings | Add-Member -NotePropertyName "telemetry.enableTelemetry" -NotePropertyValue $true -Force
            $settings | Add-Member -NotePropertyName "telemetry.enableCrashReporting" -NotePropertyValue $true -Force
            $settings | Add-Member -NotePropertyName "telemetry.enableUsageReporting" -NotePropertyValue $true -Force
            $settings | Add-Member -NotePropertyName "telemetry.telemetryEnabled" -NotePropertyValue $true -Force
            
            # Write new settings
            $settings | ConvertTo-Json -Depth 10 | Set-Content $targetPath -Encoding UTF8
            
            Write-Host "Settings written to: $targetPath" -ForegroundColor Green
            Write-Host "Telemetry settings have been enabled" -ForegroundColor Green
            
        } catch {
            Write-Host "Failed to fix settings: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host "`n" + "=" * 60
Write-Host "MANUAL STEPS (if needed):" -ForegroundColor Cyan
Write-Host "1. Open Trae IDE"
Write-Host "2. Press Ctrl+, to open settings"
Write-Host "3. Search for 'telemetry'"
Write-Host "4. Enable the following:"
Write-Host "   - Enable Telemetry"
Write-Host "   - Enable Crash Reporting"
Write-Host "   - Enable Usage Reporting"
Write-Host "5. Save and restart Trae IDE"
Write-Host "`nCOMPLETED!" -ForegroundColor Green

# Keep window open
Read-Host "Press Enter to exit"
