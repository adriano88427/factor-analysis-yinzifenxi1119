# Filesystem MCP 配置指南

## 问题诊断

您遇到的错误是因为批处理文件中的中文字符编码问题，以及MCP服务器需要通过标准输入/输出与客户端通信，而不是直接在终端中运行。

## 解决方案

### 方案1：在IDE中配置Filesystem MCP

1. 打开您的IDE（如Cursor、Claude Desktop等）
2. 找到MCP服务器配置选项
3. 添加以下配置：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "node",
      "args": ["C:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO\\mcp-filesystem\\index.js", "--allowed-directories", "C:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO"],
      "env": {}
    }
  }
}
```

### 方案2：使用配置文件

1. 将修复后的 `filesystem-mcp-config.json` 文件导入到您的IDE中
2. 确保IDE使用此配置文件启动MCP服务器

### 方案3：测试MCP服务器功能

使用以下Python脚本测试MCP服务器是否正常工作：

```python
import subprocess
import json
import sys

def test_mcp_server():
    # 启动MCP服务器
    cmd = [
        "node",
        "C:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO\\mcp-filesystem\\index.js",
        "--allowed-directories",
        "C:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO"
    ]
    
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
        response = json.loads(response_line)
        
        print("MCP服务器响应:")
        print(json.dumps(response, indent=2))
        
        # 关闭进程
        process.terminate()
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)
```

## 验证步骤

1. 确保Node.js已安装（版本v24.11.1已检测到）
2. 确保Filesystem MCP文件存在（已确认）
3. 在IDE中正确配置MCP服务器
4. 重启IDE以加载新配置
5. 测试文件系统操作功能

## 常见问题

### 问题1：ENOENT错误
- **原因**：使用了示例路径而非实际路径
- **解决**：确保使用正确的项目路径

### 问题2：编码错误
- **原因**：批处理文件中的中文字符编码问题
- **解决**：使用修复版本的脚本或直接在IDE中配置

### 问题3：JSON解析错误
- **原因**：MCP服务器需要通过标准输入/输出与客户端通信
- **解决**：不要直接在终端中运行MCP服务器，而是通过IDE启动

## 下一步

1. 按照上述方案在IDE中配置Filesystem MCP
2. 如果仍有问题，请提供您的IDE类型和版本，以便提供更具体的指导
3. 一旦配置成功，您就可以使用Filesystem MCP的各种文件操作功能了