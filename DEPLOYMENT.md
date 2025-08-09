# mNAV追踪网站 Vercel 部署指南

## 📋 部署前准备

### 1. 环境要求
- Git（用于代码管理）
- Vercel账号（免费）
- GitHub账号（推荐）

### 2. 代码准备
项目已经为Vercel部署进行了优化：
- ✅ 添加了 `vercel.json` 配置文件
- ✅ 修改了应用以支持serverless环境
- ✅ 调整了调度器逻辑（改为按需更新）
- ✅ 优化了数据库连接

## 🚀 部署步骤

### 方法一：通过GitHub部署（推荐）

#### 1. 上传代码到GitHub
```bash
cd "/Users/charlotte/Documents/Code/sbet bmnr website"

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交代码
git commit -m "Initial commit: mNAV tracking website"

# 添加远程仓库（替换为你的GitHub仓库地址）
git remote add origin https://github.com/你的用户名/mnav-tracker.git

# 推送代码
git push -u origin main
```

#### 2. 连接Vercel
1. 访问 [vercel.com](https://vercel.com)
2. 点击 "Sign up" 并用GitHub账号注册
3. 登录后点击 "New Project"
4. 选择你的GitHub仓库 `mnav-tracker`
5. 点击 "Import"

#### 3. 配置项目设置
- **Framework Preset**: 选择 "Other"
- **Build Command**: 留空
- **Output Directory**: 留空
- **Install Command**: `pip install -r requirements.txt`

#### 4. 环境变量设置
在Vercel项目设置中添加环境变量：
- `VERCEL`: `1` （标识Vercel环境）
- `PYTHONPATH`: `.`

#### 5. 部署
点击 "Deploy" 开始部署，等待部署完成。

### 方法二：通过Vercel CLI部署

#### 1. 安装Vercel CLI
```bash
npm install -g vercel
```

#### 2. 登录Vercel
```bash
vercel login
```

#### 3. 部署项目
```bash
cd "/Users/charlotte/Documents/Code/sbet bmnr website"
vercel
```

按照提示完成配置：
- Set up and deploy: `Y`
- Which scope: 选择你的账号
- Link to existing project: `N`
- Project name: `mnav-tracker`
- Directory: `.`

## ⚙️ 部署后配置

### 1. 数据库初始化
首次部署后，访问网站会自动创建数据库并初始化数据。

### 2. 股票配置
部署成功后，需要在网页上配置：
- SBET股本数量和ETH持仓量
- BMNR股本数量和ETH持仓量

### 3. 域名配置（可选）
在Vercel控制台中可以：
- 使用免费的 `.vercel.app` 域名
- 绑定自定义域名

## 🔧 技术说明

### Serverless适配
- **调度器**: 移除了持久后台调度器，改为按需更新
- **数据更新**: 每次API调用时检查数据时效性，超过1小时自动更新
- **状态管理**: 使用SQLite数据库持久化存储状态

### API限制处理
- **Finnhub API**: 免费版每分钟60次请求，已添加适当延迟
- **CoinGecko API**: 用于ETH价格，稳定可靠

### 数据存储
- 使用SQLite数据库（Vercel支持）
- 历史数据CSV文件保留，便于数据分析

## 📊 功能特性

部署后的网站提供：
- ✅ 实时股价获取（SBET、BMNR）
- ✅ 实时ETH价格获取
- ✅ 自动mNAV计算
- ✅ 智能数据更新（每小时）
- ✅ 手动刷新功能
- ✅ 配置管理界面
- ✅ 响应式设计

## 🐛 故障排除

### 常见问题
1. **部署失败**: 检查 `requirements.txt` 是否正确
2. **API错误**: 确认Finnhub API密钥有效
3. **数据不更新**: 手动点击"手动更新"按钮

### 日志查看
在Vercel控制台的 "Functions" 标签页可以查看日志。

### 重新部署
代码更新后，推送到GitHub会自动触发重新部署。

## 📋 项目文件结构

```
sbet bmnr website/
├── app.py                 # 主应用程序
├── vercel.json           # Vercel配置
├── requirements.txt      # Python依赖
├── templates/
│   └── index.html       # 前端模板
├── static/
│   ├── css/style.css    # 样式文件
│   └── js/main.js       # JavaScript
├── historical_data.csv  # 历史数据
├── mnav_data.db         # SQLite数据库
└── README.md            # 项目说明
```

## 🔗 访问地址

部署成功后，你会获得一个类似这样的地址：
`https://mnav-tracker-你的用户名.vercel.app`

祝部署成功！🎉 