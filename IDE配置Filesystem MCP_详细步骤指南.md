# IDE配置Filesystem MCP - 详细步骤指南

## 问题确认
您的IDE正在使用全局安装的Filesystem MCP服务器，该服务器仍在使用示例路径`C:\path\to\allowed\directory`，导致ENOENT错误。

## 解决方案
配置IDE使用我们本地配置的版本，而不是全局版本。

## 通用配置内容

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

## 不同IDE的具体配置步骤

### 1. Cursor/VS Code

#### 方法1：通过设置界面
1. 打开设置（Ctrl+,）
2. 搜索"MCP"或"Model Context Protocol"
3. 找到MCP服务器配置
4. 点击"添加服务器"或编辑现有服务器
5. 输入服务器名称：`filesystem`
6. 输入命令：`node`
7. 输入参数：`["C:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO\\mcp-filesystem\\index.js", "--allowed-directories", "C:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO"]`
8. 保存配置

#### 方法2：通过settings.json文件
1. 打开设置文件（Ctrl+Shift+P，输入"Open Settings (JSON)"）
2. 添加以下配置：
```json
{
  "mcp.mcpServers": {
    "filesystem": {
      "command": "node",
      "args": ["C:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO\\mcp-filesystem\\index.js", "--allowed-directories", "C:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO"],
      "env": {}
    }
  }
}
```

### 2. Claude Desktop

1. 打开运行对话框（Win+R）
2. 输入`%APPDATA%\Claude`并回车
3. 打开或创建`claude_desktop_config.json`文件
4. 添加以下配置：
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
5. 保存文件并重启Claude Desktop

### 3. 其他IDE

1. 找到IDE的MCP配置文件或设置
2. 添加或替换相同的配置
3. 保存配置并重启IDE

## 备选配置（如果上述配置有冲突）

如果您的IDE仍然尝试使用全局版本，请尝试使用不同的服务器名称：

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

## 验证步骤

1. 保存配置并重启IDE
2. 检查IDE日志，确认不再出现ENOENT错误
3. 尝试使用Filesystem MCP的功能，如列出目录或读取文件

## 常见问题解决

### 问题1：IDE仍然显示ENOENT错误
- 确认IDE确实使用了我们的配置，而不是全局版本
- 检查IDE日志，确认它正在加载正确的MCP服务器路径
- 尝试使用备选配置（使用"local-filesystem"作为服务器名称）

### 问题2：IDE找不到MCP服务器
- 确认Node.js已正确安装
- 确认路径`C:\Users\NINGMEI\Documents\trae_projects\WEIBO\mcp-filesystem\index.js`存在
- 确认IDE有权限访问项目目录

### 问题3：配置文件格式错误
- 确认JSON格式正确
- 确认所有路径都使用双反斜杠
- 确认所有引号和括号都匹配

## 相关文件

- 本地MCP服务器：`C:\Users\NINGMEI\Documents\trae_projects\WEIBO\mcp-filesystem\index.js`
- 配置文件：`C:\Users\NINGMEI\Documents\trae_projects\WEIBO\filesystem-mcp-config.json`
- 卸载脚本：`C:\Users\NINGMEI\Documents\trae_projects\WEIBO\uninstall-global-filesystem-mcp.bat`

## 下一步

配置完成后，请重启IDE，然后检查是否还有ENOENT错误。如果仍有问题，请查看IDE日志并提供更多信息，我们将进一步协助您解决。