# TRAE IDE MCP路径修复方案

## 问题诊断
**错误现象**：
- TRAE IDE的Cline试图加载 `D:\Trae CN\mcp-filesystem\index.js`
- 实际文件位置：`C:\Users\NINGMEI\Documents\trae_projects\WEIBO\mcp-filesystem\index.js`
- 路径不匹配导致MODULE_NOT_FOUND错误

## 解决方案

### 方案1：创建符号链接（推荐）
在Windows中创建符号链接，让TRAE能找到正确位置：

```cmd
# 以管理员身份运行命令提示符，执行：
mklink /D "D:\Trae CN\mcp-filesystem" "C:\Users\NINGMEI\Documents\trae_projects\WEIBO\mcp-filesystem"
```

### 方案2：复制文件
将整个mcp-filesystem文件夹复制到TRAE期望的位置：

```cmd
# 创建目标目录
mkdir "D:\Trae CN\mcp-filesystem"

# 复制所有文件
xcopy "C:\Users\NINGMEI\Documents\trae_projects\WEIBO\mcp-filesystem\*" "D:\Trae CN\mcp-filesystem\" /E /H /C /I
```

### 方案3：修改TRAE配置（如果能找到配置文件）
查找TRAE IDE的配置文件，通常位于：
- `%APPDATA%\Trae\settings.json`
- `%LOCALAPPDATA%\Trae\config.json`
- 用户主目录的.traerc
- 项目目录的.traerc.json

## 推荐步骤

1. **首先尝试方案1**（符号链接）
   - 效率最高，不占用额外空间
   - 修改文件时两边同步

2. **如果权限不足，使用方案2**（复制文件）
   - 可能需要以管理员身份运行
   - 文件更新需要手动同步

3. **如果能找到配置文件，使用方案3**
   - 最根本的解决方案
   - 需要找到配置位置

## 验证修复
修复后应该能：
- TRAE IDE正常加载MCP File System
- 不再出现MODULE_NOT_FOUND错误
- MCP服务器可以正常启动
