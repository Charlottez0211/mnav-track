# SBET & BMNR mNAV 追踪系统 - Vercel 部署指南

## 📋 部署概述

本指南将详细说明如何将 SBET & BMNR mNAV 追踪系统部署到 Vercel 平台上。项目已经过优化，完全适配 Vercel 的无服务器环境。

### 🎯 部署目标
- ✅ 零配置部署到 Vercel
- ✅ 自动 HTTPS 和全球 CDN
- ✅ 无服务器函数运行
- ✅ 实时股票和 ETH 价格追踪

## 🚀 快速部署步骤

### 第一步：访问 Vercel 官网
1. 打开浏览器，访问：https://vercel.com
2. 点击右上角 **"Sign up"** 或 **"Log in"**
3. 选择 **"Continue with GitHub"** 选项
4. 授权 Vercel 访问您的 GitHub 账户

### 第二步：导入 GitHub 项目
1. 登录成功后，进入 Vercel 控制台
2. 点击 **"Add New..."** 按钮
3. 选择 **"Project"** 选项
4. 在 "Import Git Repository" 页面中：
   - 搜索 `mnav-track` 仓库
   - 或者直接输入仓库 URL：`https://github.com/Charlottez0211/mnav-track`
5. 点击仓库旁边的 **"Import"** 按钮

### 第三步：配置项目设置
在项目配置页面：

#### 基本设置
- **Project Name**: `mnav-track` （或您喜欢的名称）
- **Framework Preset**: `Other` （Vercel 会自动检测）
- **Root Directory**: `.` （保持默认）

#### 构建设置
- **Build Command**: 留空（使用默认）
- **Output Directory**: 留空（使用默认）
- **Install Command**: 留空（使用默认）

#### 环境变量（可选）
目前项目不需要额外的环境变量，API 密钥已内置。

### 第四步：开始部署
1. 检查所有设置无误后，点击 **"Deploy"** 按钮
2. Vercel 将开始自动部署过程：
   - 🔄 克隆 GitHub 仓库
   - 📦 安装 Python 依赖
   - 🏗️ 构建 Flask 应用
   - 🚀 部署到全球 CDN

### 第五步：等待部署完成
部署过程通常需要 2-3 分钟：
- ✅ **Building**: 安装依赖和构建应用
- ✅ **Deploying**: 部署到 Vercel 边缘网络
- ✅ **Ready**: 部署完成，应用可访问

### 第六步：访问您的应用
1. 部署完成后，Vercel 会显示应用 URL
2. 点击 URL 或复制链接在新标签页中打开
3. 您的 mNAV 追踪系统现在已在线运行！

## 🔧 详细配置说明

### 项目结构验证
确保您的项目包含以下文件：
```
mnav-track/
├── app.py              # Flask 主应用
├── requirements.txt    # Python 依赖
├── vercel.json        # Vercel 配置
├── .gitignore         # Git 忽略文件
├── README.md          # 项目说明
├── templates/
│   └── index.html     # 前端模板
└── static/
    ├── css/style.css  # 样式文件
    └── js/main.js     # JavaScript 逻辑
```

### Vercel 配置文件详解
`vercel.json` 文件内容：
```json
{
    "version": 2,
    "builds": [
        {
            "src": "app.py",
            "use": "@vercel/python"
        }
    ],
    "routes": [
        {
            "src": "/(.*)",
            "dest": "/app.py"
        }
    ]
}
```

### Python 依赖说明
`requirements.txt` 文件内容：
```
Flask==2.3.3
requests==2.31.0
```

## 🌐 部署后配置

### 自定义域名（可选）
1. 在 Vercel 项目控制台中，点击 **"Domains"** 标签
2. 点击 **"Add"** 按钮
3. 输入您的自定义域名
4. 按照提示配置 DNS 记录

### 环境变量管理
1. 在项目设置中，找到 **"Environment Variables"** 部分
2. 如需添加 API 密钥等敏感信息：
   - Name: `FINNHUB_API_KEY`
   - Value: 您的 Finnhub API 密钥
   - Environment: 选择 `Production`, `Preview`, `Development`

### 部署设置
- **Git Integration**: 已自动配置
- **Auto Deploy**: 推送到 `main` 分支自动部署
- **Production Branch**: `main`

## 📊 功能验证

### 部署后测试清单
访问您的应用 URL，确认以下功能正常：

1. **页面加载**
   - ✅ 主页正常显示
   - ✅ CSS 样式加载正确
   - ✅ JavaScript 功能正常

2. **数据获取**
   - ✅ 点击"手动更新"按钮
   - ✅ 确认 SBET 和 BMNR 股价显示
   - ✅ 确认 ETH 价格显示
   - ✅ 确认 mNAV 计算结果

3. **配置功能**
   - ✅ 修改 SBET 股本数量和 ETH 持仓
   - ✅ 修改 BMNR 股本数量和 ETH 持仓
   - ✅ 确认配置保存成功

4. **响应式设计**
   - ✅ 桌面端显示正常
   - ✅ 移动端显示正常
   - ✅ 界面自适应不同屏幕尺寸

## 🛠️ 故障排除

### 常见部署问题

#### 1. 部署失败
**问题**: 构建过程中出现错误
**解决方案**:
- 检查 `requirements.txt` 文件格式
- 确认 Python 代码语法正确
- 查看 Vercel 部署日志获取详细错误信息

#### 2. 应用无法访问
**问题**: 部署成功但页面无法加载
**解决方案**:
- 检查 `vercel.json` 配置是否正确
- 确认 Flask 应用入口点设置正确
- 查看 Function 日志排查运行时错误

#### 3. API 请求失败
**问题**: 无法获取股价或 ETH 价格数据
**解决方案**:
- 检查网络连接
- 验证 API 密钥是否有效
- 确认 API 服务商是否正常运行

#### 4. 静态文件加载失败
**问题**: CSS 或 JavaScript 文件无法加载
**解决方案**:
- 检查文件路径是否正确
- 确认静态文件已正确上传到 GitHub
- 验证 Flask 静态文件配置

### 调试方法
1. **查看部署日志**:
   - 在 Vercel 项目页面点击部署记录
   - 展开 "Build Logs" 查看构建过程
   - 检查 "Function Logs" 查看运行时日志

2. **本地测试**:
   ```bash
   # 克隆仓库到本地
   git clone https://github.com/Charlottez0211/mnav-track.git
   cd mnav-track
   
   # 安装依赖
   pip install -r requirements.txt
   
   # 本地运行
   python app.py
   ```

3. **检查网络请求**:
   - 使用浏览器开发者工具
   - 查看 Network 标签页
   - 检查 API 请求和响应状态

## 🔄 更新和维护

### 代码更新流程
1. 在本地修改代码
2. 提交并推送到 GitHub：
   ```bash
   git add .
   git commit -m "更新说明"
   git push origin main
   ```
3. Vercel 将自动重新部署

### 监控和分析
- **访问统计**: 在 Vercel 控制台查看访问量
- **性能监控**: 查看函数执行时间和错误率
- **日志分析**: 定期检查函数日志排查问题

### 备份建议
- 定期备份 GitHub 仓库
- 导出 Vercel 项目配置
- 记录重要的配置参数

## 📞 技术支持

### 获取帮助
1. **Vercel 官方文档**: https://vercel.com/docs
2. **Flask 文档**: https://flask.palletsprojects.com/
3. **GitHub Issues**: 在项目仓库中提交问题

### 联系方式
如遇到部署问题，可以：
- 查看 Vercel 社区论坛
- 参考官方示例项目
- 联系 Vercel 技术支持

---

## ✅ 部署完成确认

当您成功完成所有步骤后，您将拥有：
- 🌐 一个完全托管的 Web 应用
- 🔒 自动 HTTPS 加密
- ⚡ 全球 CDN 加速
- 📱 响应式移动友好界面
- 📊 实时股票数据追踪
- 🔄 自动部署流水线

**恭喜！您的 SBET & BMNR mNAV 追踪系统现已成功部署到 Vercel！**

---

**部署日期**: $(date)  
**项目仓库**: https://github.com/Charlottez0211/mnav-track  
**技术栈**: Flask + Python + Vercel Functions 