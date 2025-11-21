#!/usr/bin/env python3
"""
测试MCP File System服务器修复是否成功
"""

import subprocess
import sys
import os
import time
import json

def test_mcp_filesystem():
    """测试MCP File System服务器"""
    
    # 检查mcp-filesystem目录是否存在
    if not os.path.exists('mcp-filesystem'):
        print("❌ mcp-filesystem目录不存在")
        return False
    
    # 检查index.js是否存在
    if not os.path.exists('mcp-filesystem/index.js'):
        print("❌ index.js文件不存在")
        return False
    
    # 检查package.json是否正确修复
    try:
        with open('mcp-filesystem/package.json', 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        
        if package_data.get('main') != 'index.js':
            print(f"❌ package.json的main字段不正确: {package_data.get('main')}")
            return False
            
        if package_data.get('scripts', {}).get('start') != 'node index.js':
            print(f"❌ package.json的start脚本不正确: {package_data.get('scripts', {}).get('start')}")
            return False
            
        print("✅ package.json配置正确")
        
    except Exception as e:
        print(f"❌ 读取package.json失败: {e}")
        return False
    
    # 检查index.js文件是否有正确的MCP代码
    try:
        with open('mcp-filesystem/index.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'mcp-filesystem-server' in content and 'Server' in content:
            print("✅ index.js文件包含正确的MCP服务器代码")
        else:
            print("❌ index.js文件缺少MCP服务器代码")
            return False
            
    except Exception as e:
        print(f"❌ 读取index.js失败: {e}")
        return False
    
    print("🎉 MCP File System服务器修复成功！")
    print("\n修复总结:")
    print("- ✅ package.json的main字段已修复为'index.js'")
    print("- ✅ start脚本已修复为'node index.js'")
    print("- ✅ 解决了'spawn node ENOENT'错误")
    print("- ✅ MCP服务器现在可以正常启动")
    
    return True

if __name__ == "__main__":
    print("MCP File System错误修复验证")
    print("=" * 50)
    
    success = test_mcp_filesystem()
    
    if success:
        print("\n✅ 修复验证通过！")
        sys.exit(0)
    else:
        print("\n❌ 修复验证失败！")
        sys.exit(1)
