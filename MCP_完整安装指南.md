# MCP File System 完整安装和修复指南

## 🚨 重要发现
**真正的问题根源**：系统上没有安装Node.js和npm！

这解释了为什么会出现`'npm' is not recognized as an internal or external command`错误。

## 📋 完整解决步骤

### 第一步：安装Node.js和npm

#### Windows系统安装方法

**方法1：官方安装包（推荐）**
1. 访问 https://nodejs.org/zh-cn/
2. 下载LTS版本（推荐）
3. 运行安装包，按照向导完成安装
4. 重启命令行

**方法2：使用Chocolatey包管理器**
```powershell
# 如果已安装Chocolatey
choco install nodejs
```

**方法3：使用winget包管理器**
```powershell
# 如果已安装winget
winget install OpenJS.NodeJS
```

#### Linux系统安装方法

**Ubuntu/Debian**：
```bash
# 更新包索引
sudo apt update

# 安装Node.js和npm
sudo apt install nodejs npm

# 验证安装
node --version
npm --version
```

**CentOS/RHEL**：
```bash
# 安装Node.js和npm
sudo yum install nodejs npm

# 或使用dnf（较新版本）
sudo dnf install nodejs npm
```

**使用NodeSource仓库（获取更新版本）**：
```bash
# 添加NodeSource仓库
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -

# 安装Node.js
sudo yum install nodejs

# 验证安装
node --version
npm --version
```

**macOS安装方法**：
```bash
# 使用Homebrew（如果已安装）
brew install node

# 验证安装
node --version
npm --version
```

### 第二步：配置npm镜像源

#### 快速配置命令
```bash
# 配置淘宝镜像源
npm config set registry https://registry.npmmirror.com

# 配置其他国内镜像
npm config set disturl https://npmmirror.com/dist
npm config set electron_mirror https://npmmirror.com/mirrors/electron/
npm config set sass_binary_site https://npmmirror.com/mirrors/node-sass/

# 验证配置
npm config get registry
```

### 第三步：安装MCP依赖

```bash
# 进入MCP目录
cd mcp-filesystem

# 安装依赖
npm install

# 或者使用cnpm（淘宝客户端）
npm install -g cnpm --registry=https://registry.npmmirror.com
cnpm install

# 验证安装
ls node_modules/@modelcontextprotocol
```

### 第四步：启动MCP服务器

```bash
# 方法1：直接启动
cd mcp-filesystem
node index.js

# 方法2：使用npm脚本
cd mcp-filesystem
npm start
```

## 🔧 自动化脚本

### 完整的Node.js + MCP安装脚本

创建 `install-nodejs-mcp-china.bat`：
```batch
@echo off
chcp 65001 >nul

echo ==================================================
echo    Node.js + MCP File System 完整安装脚本
echo ==================================================
echo.

echo 🔍 检查Node.js是否已安装...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Node.js已安装
    node --version
) else (
    echo ❌ Node.js未安装
    echo.
    echo 💡 请先安装Node.js：
    echo    1. 访问 https://nodejs.org/zh-cn/
    echo    2. 下载并安装LTS版本
    echo    3. 重启此脚本
    echo.
    pause
    exit /b 1
)

echo.
echo 🔍 检查npm是否已安装...
npm --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ npm已安装
    npm --version
) else (
    echo ❌ npm未安装，请重新安装Node.js
    echo    npm通常与Node.js一起安装
    pause
    exit /b 1
)

echo.
echo ==================================================
echo    开始配置MCP File System
echo ==================================================
echo.

echo 📦 当前npm配置：
npm config get registry

echo.
echo 🔧 配置npm镜像源为淘宝...
npm config set registry https://registry.npmmirror.com
npm config set disturl https://npmmirror.com/dist
npm config set electron_mirror https://npmmirror.com/mirrors/electron/
npm config set sass_binary_site https://npmmirror.com/mirrors/node-sass/

echo.
echo 📥 安装cnpm淘宝客户端...
npm install -g cnpm --registry=https://registry.npmmirror.com

echo.
echo 🧹 清理npm缓存...
npm cache clean --force

echo.
echo 📋 检查mcp-filesystem目录...
if not exist "mcp-filesystem" (
    echo ❌ 未找到mcp-filesystem目录
    echo 请确保在包含mcp-filesystem的目录中运行此脚本
    pause
    exit /b 1
)

cd mcp-filesystem

echo.
echo 📦 安装MCP依赖包...
npm install

echo.
echo ✅ 验证安装结果...
if exist "node_modules\@modelcontextprotocol" (
    echo 🎉 MCP依赖安装成功！
    echo.
    echo 🚀 启动MCP服务器：
    echo    cd mcp-filesystem
    echo    node index.js
    echo.
    echo 或者：
    echo    cd mcp-filesystem
    echo    npm start
) else (
    echo ❌ 安装失败，可能存在以下问题：
    echo    1. 网络连接问题
    echo    2. 防火墙阻止访问
    echo    3. npm配置错误
    echo.
    echo 💡 解决方案：
    echo    1. 检查网络连接
    echo    2. 尝试使用VPN或代理
    echo    3. 联系网络管理员确认npm访问权限
)

echo.
echo 📋 最终npm配置：
npm config get registry

echo.
echo ==================================================
echo    安装完成！
echo ==================================================
pause
```

## 🔍 故障排除

### 如果Node.js安装后仍然显示"npm不是内部或外部命令"

1. **检查安装路径**
   ```bash
   # 在Windows上检查环境变量
   echo %PATH%
   
   # 查找Node.js安装路径
   where node
   ```

2. **重启命令行**
   - 关闭所有命令行窗口
   - 以管理员身份重新打开命令行
   - 再次运行安装脚本

3. **手动添加环境变量**
   - Node.js通常会自动添加到PATH
   - 如果没有，需要手动添加`C:\Program Files\nodejs\`到PATH

### 如果npm安装依赖失败

1. **检查网络连接**
   ```bash
   # 测试淘宝镜像源是否可访问
   curl -I https://registry.npmmirror.com
   ```

2. **清理npm缓存**
   ```bash
   npm cache clean --force
   npm cache verify
   ```

3. **使用不同镜像源**
   ```bash
   # 尝试中科大镜像
   npm config set registry https://npmreg.proxy.ustclug.org
   
   # 尝试清华大学镜像
   npm config set registry https://mirrors.tuna.tsinghua.edu.cn/npm-registry/
   ```

## 📞 技术支持

如果仍然遇到问题，请提供以下信息：
- 操作系统版本（如Windows 10, Ubuntu 20.04等）
- Node.js版本 (`node --version`)
- npm版本 (`npm --version`)
- 完整的错误信息
- 网络环境（公司网络/家庭网络/校园网等）

## 🎯 预期结果

完成以上所有步骤后，MCP File System应该能够：
- ✅ 正确安装Node.js和npm
- ✅ 成功下载MCP依赖包
- ✅ 启动MCP服务器
- ✅ 不再出现"spawn node ENOENT"错误
- ✅ 正常处理文件系统操作
