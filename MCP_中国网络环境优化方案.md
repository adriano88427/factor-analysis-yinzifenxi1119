# MCP File System 中国网络环境优化方案

## 🌐 问题分析

在中国使用MCP File System可能遇到的网络问题：

### 1. npm registry访问问题
- **默认npm源**：registry.npmjs.org 在中国访问速度慢或被限制
- **依赖包下载失败**：`@modelcontextprotocol/sdk` 可能无法正常下载
- **网络超时**：安装过程可能因为网络问题而失败

### 2. 模块加载问题
- **spawn node ENOENT** 错误可能是因为依赖包未正确安装
- Node.js无法找到 `@modelcontextprotocol/sdk` 模块
- 实际根源是网络问题导致包下载不完整

### 3. 防火墙限制
- 某些npm包的CDN域名可能被限制
- GitHub相关域名访问可能受限

## 🛠️ 完整解决方案

### 方案1：配置国内npm镜像源（推荐）

#### 1.1 配置淘宝镜像
```bash
# 设置npm镜像源为淘宝
npm config set registry https://registry.npmmirror.com

# 验证配置
npm config get registry
```

#### 1.2 配置yarn镜像（如果使用yarn）
```bash
yarn config set registry https://registry.npmmirror.com
```

### 方案2：手动安装依赖

#### 2.1 清理缓存
```bash
npm cache clean --force
```

#### 2.2 使用cnpm（淘宝npm镜像客户端）
```bash
# 安装cnpm
npm install -g cnpm --registry=https://registry.npmmirror.com

# 使用cnpm安装依赖
cnpm install
```

#### 2.3 使用中国镜像安装
```bash
npm install --registry=https://registry.npmmirror.com
```

### 方案3：离线安装方案

#### 3.1 手动下载依赖包
如果网络完全无法连接，可以手动下载所需的npm包：

**需要的核心包**：
- `@modelcontextprotocol/sdk@^0.4.0`
- `typescript@^5.0.0`
- `@types/node@^20.0.0`

#### 3.2 创建离线安装包
```bash
# 在有网络的环境下
npm pack @modelcontextprotocol/sdk@^0.4.0
npm pack typescript@^5.0.0
npm pack @types/node@^20.0.0

# 将.tgz文件传输到目标机器后
npm install *.tgz
```

### 方案4：创建简化版MCP服务器

如果依赖包问题持续存在，可以创建一个不依赖外部包的版本：

#### 4.1 创建最小可用版本
```javascript
// minimal-mcp-server.js
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// 简化的MCP服务器，使用Node.js内置模块
```

### 方案5：使用本地包管理器

#### 5.1 设置私有registry
创建`.npmrc`文件：
```
registry=https://registry.npmmirror.com
disturl=https://npmmirror.com/dist
electron_mirror=https://npmmirror.com/mirrors/electron/
sass_binary_site=https://npmmirror.com/mirrors/node-sass/
phantomjs_cdnurl=https://npmmirror.com/mirrors/phantomjs/
```

## 🚀 快速修复脚本

### 中国用户专用修复脚本

创建 `setup-mcp-china.sh`：
```bash
#!/bin/bash

echo "🔧 正在为中国用户配置MCP File System..."

# 1. 配置淘宝镜像
echo "📦 配置npm镜像源为淘宝..."
npm config set registry https://registry.npmmirror.com

# 2. 安装cnpm
echo "📥 安装cnpm淘宝客户端..."
npm install -g cnpm --registry=https://registry.npmmirror.com

# 3. 清理缓存
echo "🧹 清理npm缓存..."
npm cache clean --force

# 4. 进入目录并安装依赖
echo "📋 进入mcp-filesystem目录..."
cd mcp-filesystem

# 5. 使用cnpm安装依赖
echo "📦 安装MCP依赖包..."
cnpm install

# 6. 验证安装
echo "✅ 验证安装结果..."
if [ -d "node_modules/@modelcontextprotocol" ]; then
    echo "🎉 MCP依赖安装成功！"
    echo "🚀 现在可以使用: cd mcp-filesystem && node index.js"
else
    echo "❌ 安装失败，请检查网络连接"
fi
```

### Windows用户批处理脚本

创建 `setup-mcp-china.bat`：
```batch
@echo off
chcp 65001 >nul
echo 🔧 正在为中国用户配置MCP File System...

echo 📦 配置npm镜像源为淘宝...
npm config set registry https://registry.npmmirror.com

echo 📥 安装cnpm淘宝客户端...
npm install -g cnpm --registry=https://registry.npmmirror.com

echo 🧹 清理npm缓存...
npm cache clean --force

echo 📋 进入mcp-filesystem目录...
cd mcp-filesystem

echo 📦 安装MCP依赖包...
cnpm install

echo ✅ 验证安装结果...
if exist "node_modules\@modelcontextprotocol" (
    echo 🎉 MCP依赖安装成功！
    echo 🚀 现在可以使用: cd mcp-filesystem && node index.js
) else (
    echo ❌ 安装失败，请检查网络连接
)

pause
```

## 📋 操作步骤

### 推荐操作流程

1. **检查当前配置**
   ```bash
   npm config get registry
   ```

2. **执行修复脚本**
   - Windows: 运行 `setup-mcp-china.bat`
   - Linux/Mac: 运行 `bash setup-mcp-china.sh`

3. **验证安装**
   ```bash
   cd mcp-filesystem
   ls node_modules/@modelcontextprotocol
   ```

4. **启动测试**
   ```bash
   node index.js
   ```

## 🔍 故障排除

### 如果仍然失败

1. **检查防火墙设置**
   - 确保没有阻止npm连接
   - 检查代理设置

2. **尝试不同的镜像源**
   ```bash
   # 使用中科大镜像
   npm config set registry https://npmreg.proxy.ustclug.org
   
   # 使用清华大学镜像
   npm config set registry https://mirrors.tuna.tsinghua.edu.cn/npm-registry/
   ```

3. **使用VPN或代理**
   - 如果有合法的代理服务，可以使用：
   ```bash
   npm config set proxy http://proxy-server:port
   npm config set https-proxy http://proxy-server:port
   ```

4. **联系网络管理员**
   - 询问公司或学校的网络策略
   - 确认是否有npm访问限制

## 📞 技术支持

如果问题仍然存在，请提供以下信息：
- 操作系统版本
- Node.js版本 (`node --version`)
- npm版本 (`npm --version`)
- 当前npm registry配置
- 完整的错误日志

---

**修复日期**：2025年11月21日  
**适用地区**：中国大陆  
**修复类型**：网络环境优化  
**预期效果**：解决MCP在中国无法使用的网络问题
