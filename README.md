# SBET & BMNR mNAV 实时追踪系统

## 📋 项目概述

本项目是一个实时追踪 SBET 和 BMNR 两只股票 mNAV 数据的 Web 应用系统。系统会每30分钟自动更新股价和 ETH 价格，并计算相应的 mNAV 值。

### mNAV 计算公式
```
mNAV = 股价 × 股本数量 ÷ ETH持仓量 ÷ ETH价格
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Conda 环境管理器 (推荐)
- 网络连接 (用于获取实时价格数据)

### 安装步骤

1. **克隆或下载项目到本地**
   ```bash
   cd "/Users/charlotte/Documents/Code/sbet bmnr website"
   ```

2. **激活 conda crypto 环境** (如果有)
   ```bash
   conda activate crypto
   ```

3. **安装依赖包**
   ```bash
   pip install -r requirements.txt
   ```

4. **启动应用**
   ```bash
   # 使用启动脚本 (推荐)
   chmod +x start.sh
   ./start.sh
   
   # 或直接运行
   python app.py
   ```

5. **访问应用**
   - 打开浏览器
   - 访问: http://localhost:5000

## 🎯 主要功能

### 1. 实时数据监控
- **股价追踪**: 实时获取 SBET 和 BMNR 股价
- **ETH 价格**: 实时获取 ETH/USD 价格
- **mNAV 计算**: 自动计算并显示 mNAV 值
- **状态指示**: 实时显示各项数据的获取状态

### 2. 自动更新机制
- **服务器端**: 每30分钟自动更新价格数据
- **客户端**: 每5分钟自动刷新界面显示
- **手动更新**: 点击"手动更新"按钮立即刷新

### 3. 配置管理
- **股本数量**: 手动设置和更新股本数量
- **ETH持仓量**: 手动设置和更新 ETH 持仓量
- **实时保存**: 配置更改立即保存到数据库

### 4. 用户界面特性
- **响应式设计**: 支持桌面和移动设备
- **实时状态**: 显示系统运行状态和最后更新时间
- **通知系统**: 操作成功/失败的即时反馈
- **现代化界面**: 美观的卡片式布局和动画效果

## 📊 界面说明

### 主要数据卡片
1. **SBET 卡片**
   - mNAV 值显示
   - 当前股价
   - 股本数量
   - ETH 持仓量

2. **BMNR 卡片**
   - mNAV 值显示
   - 当前股价
   - 股本数量
   - ETH 持仓量

3. **ETH 价格卡片**
   - 当前 ETH/USD 价格

### 配置区域
- **SBET 配置**: 设置股本数量和 ETH 持仓量
- **BMNR 配置**: 设置股本数量和 ETH 持仓量

## 🔧 技术架构

### 后端技术
- **Flask**: Web 框架
- **SQLite**: 数据存储
- **yfinance**: 股价和 ETH 价格获取
- **APScheduler**: 定时任务调度

### 前端技术
- **HTML5**: 页面结构
- **CSS3**: 样式和动画
- **JavaScript (ES6+)**: 交互逻辑
- **Font Awesome**: 图标库

### 数据源
- **Yahoo Finance API**: 获取股价和 ETH 价格数据

## 📁 项目结构

```
sbet bmnr website/
├── app.py                 # Flask 主应用
├── requirements.txt       # Python 依赖包
├── start.sh              # 启动脚本
├── README.md             # 项目说明
├── mnav_data.db          # SQLite 数据库 (自动创建)
├── mnav_tracker.log      # 应用日志 (自动创建)
├── templates/
│   └── index.html        # 主页面模板
└── static/
    ├── css/
    │   └── style.css     # 样式文件
    └── js/
        └── main.js       # JavaScript 逻辑
```

## ⚙️ 配置说明

### 初次使用配置
1. 启动应用后访问 http://localhost:5000
2. 在配置区域分别设置:
   - SBET 的股本数量和 ETH 持仓量
   - BMNR 的股本数量和 ETH 持仓量
3. 点击"更新"按钮保存配置
4. 系统会自动开始计算 mNAV

### 数据更新配置
- **自动更新**: 每30分钟自动执行
- **手动更新**: 点击"手动更新"按钮
- **界面刷新**: 每5分钟自动刷新显示

## 🚦 系统状态

### 状态指示器
- **🟢 在线**: 数据获取正常
- **🔵 加载中**: 正在获取数据
- **🔴 错误**: 数据获取失败

### 日志监控
- 查看 `mnav_tracker.log` 文件了解系统运行状态
- 日志包含价格获取、计算过程和错误信息

## 🛠️ 故障排除

### 常见问题

1. **无法获取股价数据**
   - 检查网络连接
   - 确认股票代码正确 (SBET, BMNR)
   - 检查是否在交易时间

2. **ETH 价格获取失败**
   - 检查网络连接
   - Yahoo Finance API 可能暂时不可用

3. **配置更新失败**
   - 检查输入的数值是否有效
   - 确保数值大于0

4. **页面无法访问**
   - 确认 Flask 应用正在运行
   - 检查端口5000是否被占用

### 调试方法
```bash
# 查看应用日志
tail -f mnav_tracker.log

# 检查数据库
sqlite3 mnav_data.db
.tables
.schema
```

## 📈 数据说明

### 数据存储
- **price_data**: 存储历史价格数据
- **mnav_data**: 存储历史 mNAV 计算结果
- **stock_config**: 存储股本和持仓配置

### 数据精度
- **股价**: 保留4位小数
- **ETH价格**: 保留2位小数
- **mNAV**: 保留6位小数

## 🔒 安全注意事项

- 本应用仅用于数据展示，不涉及交易功能
- 数据来源于公开的金融 API
- 建议在内网环境中使用
- 定期备份数据库文件

## 📞 技术支持

如遇到问题，请检查:
1. 系统日志 (`mnav_tracker.log`)
2. 网络连接状态
3. Python 环境和依赖包

---

**版权信息**: © 2024 mNAV 追踪系统 | 数据来源: Yahoo Finance 