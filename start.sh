#!/bin/bash

# SBET & BMNR mNAV 实时追踪系统启动脚本

echo "🚀 启动 SBET & BMNR mNAV 实时追踪系统..."

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: Python3 未安装"
    exit 1
fi

# 检查并激活 conda crypto 环境
if command -v conda &> /dev/null; then
    echo "📦 激活 conda crypto 环境..."
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate crypto
else
    echo "⚠️  警告: conda 未安装，使用系统 Python"
fi

# 检查依赖包
echo "🔍 检查依赖包..."
python3 -c "import flask, yfinance, apscheduler" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📥 安装依赖包..."
    pip install -r requirements.txt
fi

# 设置环境变量
export FLASK_APP=app.py
export FLASK_ENV=development

# 启动应用
echo "🌐 启动 Web 应用程序..."
echo "📍 访问地址: http://localhost:5000"
echo "⏰ 每30分钟自动更新数据"
echo "🛑 按 Ctrl+C 停止服务"
echo ""

python3 app.py 