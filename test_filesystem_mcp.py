#!/usr/bin/env python3
"""
Filesystem MCP 测试脚本
用于验证MCP服务器是否正常工作
"""

import subprocess
import json
import sys
import os

def test_mcp_server():
    """测试MCP服务器是否正常工作"""
    
    # 设置路径
    project_dir = r"C:\Users\NINGMEI\Documents\trae_projects\WEIBO"
    server_script = os.path.join(project_dir, "mcp-filesystem", "index.js")
    
    # 检查文件是否存在
    if not os.path.exists(server_script):
        print(f"错误: 服务器脚本不存在: {server_script}")
        return False
    
    # 启动MCP服务器的命令
    cmd = [
        "node",
        server_script,
        "--allowed-directories",
        project_dir
    ]
    
    print(f"启动命令: {' '.join(cmd)}")
    print("正在启动MCP服务器...")
    
    try:
        # 启动服务器进程
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # 发送初始化请求
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # 发送请求
        request_json = json.dumps(init_request) + "\n"
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # 读取响应
        response_line = process.stdout.readline()
        if not response_line:
            print("错误: 没有收到服务器响应")
            # 读取错误输出
            stderr_output = process.stderr.read()
            if stderr_output:
                print(f"错误输出: {stderr_output}")
            return False
            
        response = json.loads(response_line)
        
        print("MCP服务器初始化响应:")
        print(json.dumps(response, indent=2))
        
        # 发送列出工具的请求
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        request_json = json.dumps(tools_request) + "\n"
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # 读取工具列表响应
        response_line = process.stdout.readline()
        if response_line:
            tools_response = json.loads(response_line)
            print("\n可用工具:")
            if "result" in tools_response and "tools" in tools_response["result"]:
                for tool in tools_response["result"]["tools"]:
                    print(f"- {tool['name']}: {tool.get('description', '无描述')}")
        
        # 关闭进程
        process.terminate()
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def check_prerequisites():
    """检查先决条件"""
    print("检查先决条件...")
    
    # 检查Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Node.js已安装: {result.stdout.strip()}")
        else:
            print("✗ Node.js未安装或不在PATH中")
            return False
    except FileNotFoundError:
        print("✗ Node.js未安装或不在PATH中")
        return False
    
    # 检查项目目录
    project_dir = r"C:\Users\NINGMEI\Documents\trae_projects\WEIBO"
    if os.path.exists(project_dir):
        print(f"✓ 项目目录存在: {project_dir}")
    else:
        print(f"✗ 项目目录不存在: {project_dir}")
        return False
    
    # 检查MCP服务器文件
    server_script = os.path.join(project_dir, "mcp-filesystem", "index.js")
    if os.path.exists(server_script):
        print(f"✓ MCP服务器文件存在: {server_script}")
    else:
        print(f"✗ MCP服务器文件不存在: {server_script}")
        return False
    
    return True

if __name__ == "__main__":
    print("Filesystem MCP 测试脚本")
    print("=" * 40)
    
    # 设置全局路径变量
    project_dir = r"C:\Users\NINGMEI\Documents\trae_projects\WEIBO"
    server_script = os.path.join(project_dir, "mcp-filesystem", "index.js")
    
    # 检查先决条件
    if not check_prerequisites():
        print("\n先决条件检查失败，请解决上述问题后重试。")
        sys.exit(1)
    
    print("\n开始测试MCP服务器...")
    success = test_mcp_server()
    
    if success:
        print("\n✓ 测试成功！MCP服务器工作正常。")
        print("\n下一步:")
        print("1. 在您的IDE中配置MCP服务器")
        print("2. 使用以下配置:")
        print('   命令: node')
        print(f'   参数: "{server_script}" --allowed-directories "{project_dir}"')
    else:
        print("\n✗ 测试失败。请检查错误信息并重试。")
    
    sys.exit(0 if success else 1)