# Filesystem MCP 配置修复指南

## 问题说明

您遇到的错误：
```
Error accessing directory C:\path\to\allowed\directory: Error: ENOENT: no such file or directory
```

这是因为Filesystem MCP配置中使用了示例路径 `C:\path\to\allowed\directory`，而不是您实际想要访问的目录路径。

## 解决方案

### 方案1：使用修复后的启动脚本（推荐）

1. 使用我创建的 `start-filesystem-mcp.bat` 脚本
2. 双击运行或在命令行中执行
3. 脚本会自动设置正确的目录路径并启动Filesystem MCP

### 方案2：手动配置

1. 打开命令行
2. 导航到mcp-filesystem目录：
   ```
   cd C:\Users\NINGMEI\Documents\trae_projects\WEIBO\mcp-filesystem
   ```
3. 使用正确的目录路径启动：
   ```
   node index.js "C:\Users\NINGMEI\Documents\trae_projects\WEIBO"
   ```

### 方案3：修改现有配置

如果您有现有的MCP配置文件（如Claude Desktop的配置文件），请将以下部分：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "node",
      "args": ["path/to/index.js", "C:\\path\\to\\allowed\\directory"]
    }
  }
}
```

修改为：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "node",
      "args": ["C:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO\\mcp-filesystem\\index.js", "C:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO"]
    }
  }
}
```

## 允许访问多个目录

如果您需要允许访问多个目录，可以修改启动脚本或配置文件，例如：

```
node index.js "C:\Users\NINGMEI\Documents\trae_projects\WEIBO" "C:\Users\NINGMEI\Documents\trae_projects"
```

## 验证修复

修复后，您应该能够：
1. 成功启动Filesystem MCP服务器
2. 通过MCP工具访问您指定的目录
3. 不再看到 `ENOENT: no such file or directory` 错误

## 注意事项

1. 确保路径使用双反斜杠或正斜杠
2. 路径中不要包含特殊字符
3. 确保指定的目录确实存在
4. 如果使用Claude Desktop，可能需要重启应用以加载新配置

## 故障排除

如果仍然遇到问题：

1. 检查Node.js是否正确安装：
   ```
   node --version
   ```

2. 检查mcp-filesystem目录是否存在：
   ```
   dir "C:\Users\NINGMEI\Documents\trae_projects\WEIBO\mcp-filesystem"
   ```

3. 检查index.js文件是否存在：
   ```
   dir "C:\Users\NINGMEI\Documents\trae_projects\WEIBO\mcp-filesystem\index.js"
   ```

4. 尝试手动运行以查看详细错误信息：
   ```
   cd "C:\Users\NINGMEI\Documents\trae_projects\WEIBO\mcp-filesystem"
   node index.js "C:\Users\NINGMEI\Documents\trae_projects\WEIBO"
   ```