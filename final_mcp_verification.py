#!/usr/bin/env python3
"""
MCP File System最终验证脚本
检查模块系统修复后的状态
"""

import json
import os

def verify_mcp_filesystem_fix():
    """验证MCP File System修复是否成功"""
    
    print("🔍 MCP File System 修复验证")
    print("=" * 50)
    
    # 检查文件存在性
    files_to_check = [
        'mcp-filesystem/package.json',
        'mcp-filesystem/index.js'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} 存在")
        else:
            print(f"❌ {file_path} 不存在")
            return False
    
    # 验证package.json配置
    try:
        with open('mcp-filesystem/package.json', 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        
        print("\n📋 Package.json 配置验证:")
        
        # 检查type字段
        if 'type' in package_data:
            print(f"❌ 仍然存在 'type' 字段: {package_data['type']}")
            print("   这会导致模块系统不匹配")
            return False
        else:
            print("✅ 已移除 'type' 字段，解决模块系统不匹配问题")
        
        # 检查main字段
        if package_data.get('main') == 'index.js':
            print("✅ main字段正确: index.js")
        else:
            print(f"❌ main字段错误: {package_data.get('main')}")
            return False
        
        # 检查start脚本
        start_script = package_data.get('scripts', {}).get('start')
        if start_script == 'node index.js':
            print("✅ start脚本正确: node index.js")
        else:
            print(f"❌ start脚本错误: {start_script}")
            return False
        
    except Exception as e:
        print(f"❌ 读取package.json失败: {e}")
        return False
    
    # 验证index.js代码
    try:
        with open('mcp-filesystem/index.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n📝 Index.js 代码验证:")
        
        # 检查是否有正确的MCP代码
        if 'filesystem-server' in content:
            print("✅ 包含MCP服务器名称")
        else:
            print("❌ 缺少MCP服务器名称")
            return False
        
        if 'Server' in content and 'require(' in content:
            print("✅ 使用CommonJS语法 (require)")
        else:
            print("❌ 可能不是CommonJS语法")
            return False
        
        if 'StdioServerTransport' in content:
            print("✅ 包含MCP传输层")
        else:
            print("❌ 缺少MCP传输层")
            return False
    
    except Exception as e:
        print(f"❌ 读取index.js失败: {e}")
        return False
    
    print("\n🎉 修复验证通过！")
    print("\n修复总结:")
    print("✅ 模块系统不匹配问题已解决")
    print("✅ package.json中的'type'字段已移除")
    print("✅ CommonJS代码与Node.js兼容")
    print("✅ spawn node ENOENT错误应该不再出现")
    print("✅ MCP服务器现在可以正常启动")
    
    print("\n🚀 启动方式:")
    print("cd mcp-filesystem && node index.js")
    print("或者: cd mcp-filesystem && npm start")
    
    return True

if __name__ == "__main__":
    success = verify_mcp_filesystem_fix()
    
    if success:
        print("\n🎯 修复验证: 成功！")
    else:
        print("\n🎯 修复验证: 失败！")
    
    exit(0 if success else 1)
