#!/usr/bin/env python3
"""
Cline Telemetry Settings Checker
Simple tool to check and fix Trae IDE telemetry settings
"""

import os
import json
import platform
from pathlib import Path

def check_trae_settings():
    """Check Trae IDE settings for telemetry"""
    print("Checking Trae IDE telemetry settings...")
    print("=" * 50)
    
    home = Path.home()
    system = platform.system()
    
    # Common Trae settings paths
    if system == "Windows":
        paths = [
            home / "AppData" / "Roaming" / "Trae" / "settings.json",
            home / "AppData" / "Local" / "Trae" / "User" / "settings.json",
        ]
    elif system == "Darwin":  # macOS
        paths = [
            home / "Library" / "Application Support" / "Trae" / "settings.json",
            home / "Library" / "Application Support" / "Trae" / "User" / "settings.json",
        ]
    else:  # Linux
        paths = [
            home / ".config" / "Trae" / "settings.json",
            home / ".config" / "Trae" / "User" / "settings.json",
        ]
    
    settings_found = False
    telemetry_enabled = False
    
    for path in paths:
        if path.exists():
            print(f"Found settings file: {path}")
            settings_found = True
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # Check telemetry settings
                telemetry_keys = [
                    'telemetry.enableTelemetry',
                    'telemetry.enableCrashReporting',
                    'telemetry.enableUsageReporting',
                    'telemetry.telemetryEnabled'
                ]
                
                for key in telemetry_keys:
                    if key in settings:
                        value = settings[key]
                        status = "ENABLED" if value else "DISABLED"
                        print(f"  {key}: {status}")
                        if value:
                            telemetry_enabled = True
                
                if not any(key in settings for key in telemetry_keys):
                    print("  No telemetry settings found")
                    
            except Exception as e:
                print(f"  Error reading settings: {e}")
    
    if not settings_found:
        print("No Trae IDE settings files found")
        print("Make sure Trae IDE is installed and has been used")
        return False
    
    return telemetry_enabled

def fix_telemetry_settings():
    """Attempt to fix telemetry settings"""
    print("\nAttempting to fix telemetry settings...")
    print("=" * 50)
    
    home = Path.home()
    system = platform.system()
    
    if system == "Windows":
        primary_path = home / "AppData" / "Roaming" / "Trae" / "settings.json"
    elif system == "Darwin":  # macOS
        primary_path = home / "Library" / "Application Support" / "Trae" / "settings.json"
    else:  # Linux
        primary_path = home / ".config" / "Trae" / "settings.json"
    
    try:
        # Ensure directory exists
        primary_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Read existing settings or create new
        if primary_path.exists():
            with open(primary_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        else:
            settings = {}
        
        # Add telemetry settings
        telemetry_settings = {
            "telemetry.enableTelemetry": True,
            "telemetry.enableCrashReporting": True,
            "telemetry.enableUsageReporting": True,
            "telemetry.telemetryEnabled": True
        }
        
        settings.update(telemetry_settings)
        
        # Backup existing file
        if primary_path.exists():
            backup_path = primary_path.with_suffix('.json.backup')
            primary_path.rename(backup_path)
            print(f"Backed up existing settings to: {backup_path}")
        
        # Write new settings
        with open(primary_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        
        print(f"Settings written to: {primary_path}")
        print("Telemetry settings have been enabled")
        return True
        
    except Exception as e:
        print(f"Failed to fix settings: {e}")
        return False

def main():
    print("Cline Telemetry Settings Fix Tool")
    print("=" * 60)
    print(f"Operating System: {platform.system()}")
    print()
    
    # Check current settings
    telemetry_ok = check_trae_settings()
    
    if not telemetry_ok:
        print("\nTelemetry settings appear to be disabled")
        response = input("Attempt to fix automatically? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            fix_telemetry_settings()
    
    print("\n" + "=" * 60)
    print("MANUAL STEPS IF NEEDED:")
    print("1. Open Trae IDE")
    print("2. Press Ctrl+, to open settings")
    print("3. Search for 'telemetry'")
    print("4. Enable the following:")
    print("   - Enable Telemetry")
    print("   - Enable Crash Reporting")
    print("   - Enable Usage Reporting")
    print("5. Save and restart Trae IDE")
    print("\nCOMPLETED!")

if __name__ == "__main__":
    main()
