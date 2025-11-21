# Filesystem MCP 全局配置问题解决方案

## 问题分析

您的IDE正在使用全局安装的Filesystem MCP服务器（位于`C:/Users/NINGMEI/AppData/Local/npm-cache/_npx/...`），而不是我们本地配置的版本。这个全局版本仍在使用示例路径`C:\path\to\allowed\directory`，导致ENOENT错误。

## 解决方案

### 方案1：更新全局Filesystem MCP配置（推荐）

1. 找到您的IDE的MCP配置文件
   - 对于Cursor/VS Code：通常在用户设置中
   - 对于其他IDE：查看IDE的配置目录

2. 更新配置，确保使用正确的路径：

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

### 方案2：完全卸载全局Filesystem MCP

1. 打开命令提示符或PowerShell
2. 运行以下命令卸载全局Filesystem MCP：

```bash
npm uninstall -g @modelcontextprotocol/server-filesystem
```

3. 然后重新配置IDE使用我们的本地版本

### 方案3：使用本地MCP服务器（最简单）

1. 确保您的IDE使用我们创建的`filesystem-mcp-config.json`文件
2. 或者手动指定本地服务器路径，而不是使用全局安装的版本

## 具体操作步骤

### 对于Cursor/VS Code用户

1. 打开设置（Ctrl+,）
2. 搜索"MCP"或"Model Context Protocol"
3. 找到Filesystem MCP配置
4. 替换为以下配置：

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

### 对于其他IDE用户

1. 找到IDE的MCP配置文件
2. 替换Filesystem配置为上述内容
3. 重启IDE

## 验证步骤

1. 保存配置并重启IDE
2. 检查IDE日志，确认不再出现ENOENT错误
3. 尝试使用Filesystem MCP的功能，如列出目录或读取文件

## 注意事项

- 确保路径使用双反斜杠（Windows路径）
- 确保IDE有权限访问项目目录
- 如果问题仍然存在，可能需要完全重启IDE或计算机

## 备选方案

如果上述方法都不起作用，您可以考虑：

1. 使用不同的MCP服务器名称，避免与全局版本冲突：

```json
{
  "mcpServers": {
    "local-filesystem": {
      "command": "node",
      "args": ["C:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO\\mcp-filesystem\\index.js", "--allowed-directories", "C:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO"],
      "env": {}
    }
  }
}
```

2. 或者使用绝对路径运行我们的测试脚本，确认本地服务器工作正常，然后向IDE开发者寻求帮助。