# Vercel 部署指南

本文档详细说明如何将 SBET & BMNR mNAV 追踪系统部署到 Vercel 平台。

## 🚀 部署步骤

### 1. 准备代码
确保你的代码已经推送到 GitHub 仓库 `Charlottez0211/mnav-track`。

### 2. 连接 Vercel
1. 访问 [Vercel](https://vercel.com) 并登录
2. 点击 "New Project"
3. 选择 "Import Git Repository"
4. 选择 `Charlottez0211/mnav-track` 仓库
5. 点击 "Import"

### 3. 配置项目
- **Framework Preset**: 选择 "Other"
- **Root Directory**: 保持默认 (./)
- **Build Command**: 留空
- **Output Directory**: 留空
- **Install Command**: 留空

### 4. 环境变量（可选）
如果需要自定义配置，可以添加以下环境变量：
- `FINNHUB_API_KEY`: Finnhub API 密钥（当前已硬编码）

### 5. 部署
点击 "Deploy" 按钮，Vercel 将自动构建和部署你的应用。

## 📁 项目结构要求

确保你的项目包含以下文件：

```
sbet bmnr website_vercel/
├── app.py                 # Flask 主应用
├── vercel.json           # Vercel 配置
├── requirements.txt      # Python 依赖
├── user_config.json     # 用户配置文件
├── templates/           # HTML 模板
│   └── index.html
└── static/             # 静态文件
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## ⚙️ 关键配置文件

### vercel.json
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

### requirements.txt
```
Flask==2.3.3
requests==2.31.0
```

## 🔧 部署后配置

### 1. 自动部署
- 每次推送到 `main` 分支时，Vercel 会自动重新部署
- 可以在 Vercel 控制台查看部署状态

### 2. 自定义域名
- 在 Vercel 控制台可以添加自定义域名
- 支持 HTTPS 自动配置

### 3. 环境变量管理
- 在 Vercel 控制台可以管理环境变量
- 支持不同环境的变量配置

## 📊 监控和日志

### 1. 访问日志
- 在 Vercel 控制台可以查看访问统计
- 支持实时监控

### 2. 函数日志
- 查看 Flask 应用的运行日志
- 调试 API 调用和错误

### 3. 性能监控
- 监控响应时间和错误率
- 自动性能优化

## 🛠️ 故障排除

### 常见问题

1. **部署失败**
   - 检查 `vercel.json` 配置是否正确
   - 确保所有必需文件都存在
   - 查看构建日志中的错误信息

2. **运行时错误**
   - 检查 Flask 应用代码
   - 查看函数日志
   - 验证 API 密钥是否有效

3. **静态文件无法访问**
   - 确保 `static` 目录结构正确
   - 检查 Flask 静态文件配置

### 调试技巧

1. **本地测试**
   ```bash
   python app.py
   ```

2. **检查依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **验证配置**
   - 检查 `user_config.json` 格式
   - 验证 API 端点是否正常

## 🔄 更新部署

### 自动更新
- 推送代码到 GitHub 后，Vercel 自动重新部署
- 无需手动操作

### 手动重新部署
- 在 Vercel 控制台点击 "Redeploy"
- 适用于紧急修复或配置更改

## 📈 性能优化

### 1. 缓存策略
- 静态文件自动 CDN 缓存
- API 响应缓存优化

### 2. 冷启动优化
- 使用 Vercel 的 Python 运行时
- 优化依赖包大小

### 3. 监控和告警
- 设置性能阈值告警
- 监控 API 调用频率

## 🔒 安全考虑

### 1. API 密钥管理
- 生产环境建议使用环境变量
- 定期轮换 API 密钥

### 2. 访问控制
- 考虑添加身份验证
- 限制 API 调用频率

### 3. 数据安全
- 用户配置数据本地存储
- 不涉及敏感金融信息

## 📞 支持

如果遇到部署问题：

1. 查看 Vercel 官方文档
2. 检查项目 GitHub Issues
3. 查看 Vercel 社区论坛

---

**注意**: 确保你的 GitHub 仓库是公开的，或者 Vercel 账户有访问私有仓库的权限。 