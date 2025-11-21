#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cline遥测设置诊断工具
用于检查和修复Trae IDE遥测设置问题
"""

import os
import json
import platform
from pathlib import Path

class TraeTelemetryDiagnostic:
    def __init__(self):
        self.system = platform.system()
        self.traesettings_paths = self._find_settings_paths()
        
    def _find_settings_paths(self):
        """查找Trae IDE设置文件路径"""
        paths = []
        home = Path.home()
        
        if self.system == "Windows":
            # Windows路径
            paths.extend([
                home / "AppData" / "Roaming" / "Trae" / "settings.json",
                home / "AppData" / "Local" / "Trae" / "User" / "settings.json",
            ])
        elif self.system == "Darwin":  # macOS
            # macOS路径
            paths.extend([
                home / "Library" / "Application Support" / "Trae" / "settings.json",
                home / "Library" / "Application Support" / "Trae" / "User" / "settings.json",
            ])
        else:  # Linux
            # Linux路径
            paths.extend([
                home / ".config" / "Trae" / "settings.json",
                home / ".config" / "Trae" / "User" / "settings.json",
            ])
            
        return [p for p in paths if p.exists()]
    
    def check_telemetry_settings(self):
        """检查当前遥测设置"""
        print("🔍 检查Trae IDE遥测设置...")
        print("=" * 50)
        
        if not self.traesettings_paths:
            print("❌ 未找到Trae IDE设置文件")
            print("💡 请确保Trae IDE已安装并运行过")
            return False
            
        for path in self.traesettings_paths:
            print(f"📁 检查配置文件: {path}")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # 检查遥测相关设置
                telemetry_keys = [
                    'telemetry.enableTelemetry',
                    'telemetry.enableCrashReporting', 
                    'telemetry.enableUsageReporting',
                    'telemetry.telemetryEnabled'
                ]
                
                found_telemetry = False
                for key in telemetry_keys:
                    if key in settings:
                        found_telemetry = True
                        status = "✅ 已启用" if settings[key] else "❌ 已禁用"
                        print(f"  📊 {key}: {status}")
                
                if not found_telemetry:
                    print("  ⚠️  未找到遥测设置")
                    
                print(f"  ✅ 配置文件读取成功")
                return True
                
            except json.JSONDecodeError as e:
                print(f"  ❌ JSON格式错误: {e}")
                return False
            except Exception as e:
                print(f"  ❌ 读取错误: {e}")
                return False
    
    def fix_telemetry_settings(self):
        """修复遥测设置"""
        print("\n🔧 修复遥测设置...")
        print("=" * 50)
        
        if not self.traesettings_paths:
            print("❌ 未找到Trae IDE设置文件，无法修复")
            return False
            
        for path in self.traesettings_paths:
            print(f"📁 修复配置文件: {path}")
            try:
                # 读取现有设置
                if path.exists():
                    with open(path, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                else:
                    settings = {}
                
                # 添加遥测设置
                telemetry_fix = {
                    "telemetry.enableTelemetry": True,
                    "telemetry.enableCrashReporting": True,
                    "telemetry.enableUsageReporting": True,
                    "telemetry.telemetryEnabled": True
                }
                
                settings.update(telemetry_fix)
                
                # 备份原文件
                backup_path = path.with_suffix('.json.backup')
                if path.exists() and not backup_path.exists():
                    path.rename(backup_path)
                    print(f"  💾 已备份原文件: {backup_path}")
                
                # 写入修复后的设置
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
                
                print(f"  ✅ 遥测设置已启用")
                return True
                
            except Exception as e:
                print(f"  ❌ 修复失败: {e}")
                return False
    
    def check_ide_status(self):
        """检查IDE状态"""
        print("\n🏥 Trae IDE状态检查...")
        print("=" * 50)
        
        # 检查常见IDE进程
        import psutil
        
        trae_processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'trae' in proc.info['name'].lower():
                    trae_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if trae_processes:
            print("✅ 检测到Trae IDE正在运行:")
            for proc in trae_processes:
                print(f"  - PID: {proc.pid}, 名称: {proc.name()}")
        else:
            print("⚠️  未检测到Trae IDE运行")
            print("💡 建议重启Trae IDE以应用新设置")
    
    def show_fix_instructions(self):
        """显示手动修复说明"""
        print("\n📋 手动修复步骤...")
        print("=" * 50)
        
        print("如果自动修复失败，请按以下步骤手动操作:")
        print()
        
        print("1️⃣  打开Trae IDE")
        print("2️⃣  按 Ctrl+, 打开设置")
        print("3️⃣  在搜索框输入 'telemetry'")
        print("4️⃣  找到 'Telemetry' 选项")
        print("5️⃣  启用以下选项:")
        print("    - Enable Telemetry")
        print("    - Enable Crash Reporting") 
        print("    - Enable Usage Reporting")
        print("6️⃣  保存设置并重启IDE")
        print()
        
        print("或者在设置JSON文件中添加:")
        print('''{
  "telemetry.enableTelemetry": true,
  "telemetry.enableCrashReporting": true,
  "telemetry.enableUsageReporting": true
}''')
    
    def run_diagnostic(self):
        """运行完整诊断"""
        print("🚀 Cline遥测设置诊断工具")
        print("=" * 60)
        print(f"操作系统: {self.system}")
        print(f"Python版本: {platform.python_version()}")
        print()
        
        # 检查当前设置
        settings_ok = self.check_telemetry_settings()
        
        # 提供修复选项
        if not settings_ok:
            print("\n❌ 检测到遥测设置问题")
            response = input("是否尝试自动修复? (y/n): ").lower().strip()
            if response in ['y', 'yes', '是', '1']:
                self.fix_telemetry_settings()
        
        # 检查IDE状态
        try:
            self.check_ide_status()
        except ImportError:
            print("⚠️  需要安装psutil模块来检查进程状态: pip install psutil")
        
        # 显示后续步骤
        self.show_fix_instructions()
        
        print("\n✨ 诊断完成!")
        print("请重启Trae IDE后重新启动Cline扩展")

def main():
    """主函数"""
    diagnostic = TraeTelemetryDiagnostic()
    diagnostic.run_diagnostic()

if __name__ == "__main__":
    main()
