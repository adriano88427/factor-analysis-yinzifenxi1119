# Filesystem MCP 配置信息

## 问题分析
您的IDE正在使用全局安装的Filesystem MCP服务器，该服务器仍在使用示例路径`C:\path\to\allowed\directory`，导致ENOENT错误。

## 解决方案
配置IDE使用我们本地配置的版本，而不是全局版本。

## IDE配置内容

请在您的IDE中使用以下配置：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "node",
      "args": ["c:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO\\mcp-filesystem\\index.js", "--allowed-directories", "c:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO"],
      "env": {}
    }
  }
}
```

## 备选配置（如果上述配置有冲突）

```json
{
  "mcpServers": {
    "local-filesystem": {
      "command": "node",
      "args": ["c:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO\\mcp-filesystem\\index.js", "--allowed-directories", "c:\\Users\\NINGMEI\\Documents\\trae_projects\\WEIBO"],
      "env": {}
    }
  }
}
```

## 配置步骤

1. 打开您的IDE的设置或配置文件
2. 找到MCP服务器配置部分
3. 替换为上述配置之一
4. 保存配置并重启IDE

## 验证步骤

1. 检查IDE日志，确认不再出现ENOENT错误
2. 尝试使用Filesystem MCP的功能，如列出目录或读取文件

## 注意事项

- 确保IDE使用此配置，而不是全局安装的版本
- 如果问题仍然存在，尝试使用备选配置（使用"local-filesystem"作为服务器名称）
- 确保IDE有权限访问项目目录

## 相关文件

- 配置文件: `c:\Users\NINGMEI\Documents\trae_projects\WEIBO\filesystem-mcp-config.json`
- 详细指南: `c:\Users\NINGMEI\Documents\trae_projects\WEIBO\IDE配置Filesystem MCP详细指南.md`
- 全局问题解决方案: `c:\Users\NINGMEI\Documents\trae_projects\WEIBO\Filesystem_MCP_全局配置问题解决方案.md`