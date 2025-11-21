# IDE配置Filesystem MCP详细指南

## 问题原因

您的IDE正在使用全局安装的Filesystem MCP服务器，该服务器仍在使用示例路径`C:\path\to\allowed\directory`，导致ENOENT错误。我们需要配置IDE使用我们本地配置的版本。

## 解决方案：配置IDE使用本地MCP服务器

### 方法1：使用我们创建的配置文件

我们已经创建了正确的配置文件：`c:\Users\NINGMEI\Documents\trae_projects\WEIBO\filesystem-mcp-config.json`

在您的IDE中，指定使用此配置文件。

### 方法2：手动配置IDE

以下是在不同IDE中手动配置Filesystem MCP的步骤：

#### 对于Cursor/VS Code

1. 打开设置（Ctrl+,）
2. 搜索"MCP"或"Model Context Protocol"
3. 找到MCP服务器配置
4. 添加或替换以下配置：

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

#### 对于Claude Desktop

1. 找到Claude Desktop的配置文件（通常在`%APPDATA%\Claude\claude_desktop_config.json`）
2. 添加或替换以下配置：

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

#### 对于其他IDE

1. 找到IDE的MCP配置文件或设置
2. 添加或替换相同的配置

## 配置要点

1. **使用绝对路径**：确保所有路径都是绝对路径
2. **正确的参数格式**：使用`--allowed-directories`参数指定允许访问的目录
3. **双反斜杠**：在Windows路径中使用双反斜杠

## 验证配置

1. 保存配置并重启IDE
2. 检查IDE日志，确认不再出现ENOENT错误
3. 尝试使用Filesystem MCP的功能，如列出目录或读取文件

## 如果问题仍然存在

1. 确认IDE确实使用了我们的配置，而不是全局版本
2. 尝试使用不同的服务器名称，如"local-filesystem"，避免冲突：

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

3. 确保IDE有权限访问项目目录

## 多目录配置

如果您需要访问多个目录，可以这样配置：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "node",
      "args": ["C:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO\\mcp-filesystem\\index.js", "--allowed-directories", "C:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO", "C:\\Another\\Path", "C:\\Yet\\Another\\Path"],
      "env": {}
    }
  }
}
```

## 测试配置

配置完成后，您可以尝试以下测试：

1. 列出项目目录：`list_directory C:\Users\NINGMEI\Documents\trae_projects\WEIBO`
2. 读取文件：`read_text_file C:\Users\NINGMEI\Documents\trae_projects\WEIBO\README.md`

如果这些操作成功，说明配置正确。