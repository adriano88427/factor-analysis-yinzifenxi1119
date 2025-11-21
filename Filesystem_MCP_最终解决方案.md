# Filesystem MCP 最终解决方案

## 问题确认
您的IDE正在使用全局安装的Filesystem MCP服务器（位于`C:/Users/NINGMEI/AppData/Local/npm-cache/_npx/...`），该服务器仍在使用示例路径`C:\path\to\allowed\directory`，导致ENOENT错误。

## 最终解决方案

### 步骤1：完全卸载全局Filesystem MCP

打开命令提示符（CMD）并运行：
```
npm uninstall -g @modelcontextprotocol/server-filesystem
```

### 步骤2：配置IDE使用本地MCP服务器

在您的IDE中，使用以下配置替换现有的Filesystem MCP配置：

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

### 步骤3：如果仍有冲突，使用不同的服务器名称

如果上述配置仍有冲突，请使用以下配置（更改服务器名称）：

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

## 不同IDE的配置位置

### Cursor/VS Code
1. 打开设置（Ctrl+,）
2. 搜索"MCP"或"Model Context Protocol"
3. 找到MCP服务器配置
4. 替换为上述配置

### Claude Desktop
1. 打开配置文件：`%APPDATA%\Claude\claude_desktop_config.json`
2. 替换为上述配置

### 其他IDE
1. 找到IDE的MCP配置文件或设置
2. 替换为上述配置

## 验证步骤

1. 保存配置并重启IDE
2. 检查IDE日志，确认不再出现ENOENT错误
3. 尝试使用Filesystem MCP的功能，如列出目录或读取文件

## 如果问题仍然存在

1. 确认IDE确实使用了我们的配置，而不是全局版本
2. 检查IDE日志，确认它正在加载正确的MCP服务器路径
3. 确保IDE有权限访问项目目录

## 相关文件

- 本地MCP服务器：`C:\Users\NINGMEI\Documents\trae_projects\WEIBO\mcp-filesystem\index.js`
- 配置文件：`C:\Users\NINGMEI\Documents\trae_projects\WEIBO\filesystem-mcp-config.json`
- 详细指南：`C:\Users\NINGMEI\Documents\trae_projects\WEIBO\IDE配置Filesystem MCP详细指南.md`