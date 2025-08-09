"""
SBET 和 BMNR mNAV 实时追踪网页应用
主要功能：
1. 实时获取股价和 ETH 价格
2. 计算 mNAV 数据
3. 每30分钟自动更新
4. 提供 Web 界面显示
"""

from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import logging
from datetime import datetime, date
import atexit
import threading
import time
import requests
# 图表功能相关导入（已注释）
# import pandas as pd
# import io
# import base64
# import matplotlib
# matplotlib.use('Agg')  # 使用非交互式后端
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# from matplotlib.figure import Figure

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mnav_tracker.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

# Finnhub API 配置
FINNHUB_API_KEY = "d2bjrs9r01qrj4im3kkgd2bjrs9r01qrj4im3kl0"

# 股票配置数据
STOCK_CONFIG = {
    'SBET': {
        'shares_outstanding': 0,  # 股本数量，需要手动设置
        'eth_holdings': 0,        # ETH持仓量，需要手动设置
        'symbol': 'SBET'          # 股票代码
    },
    'BMNR': {
        'shares_outstanding': 0,  # 股本数量，需要手动设置
        'eth_holdings': 0,        # ETH持仓量，需要手动设置
        'symbol': 'BMNR'          # 股票代码
    }
}

class MNAVTracker:
    def __init__(self):
        """初始化 mNAV 追踪器"""
        self.init_database()
        self.lock = threading.Lock()
        
        # 设置 HTTP 会话用于 API 请求
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_db_path(self):
        """获取数据库路径（Vercel兼容）"""
        import os
        if os.getenv('VERCEL') == '1':
            return '/tmp/mnav_data.db'
        else:
            return 'mnav_data.db'
        
    def init_database(self):
        """初始化数据库表结构"""
        try:
            with sqlite3.connect(self.get_db_path()) as conn:
            cursor = conn.cursor()
            
            # 创建价格数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    sbet_price REAL,
                    bmnr_price REAL,
                    eth_price REAL
                )
            ''')
            
            # 创建 mNAV 数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mnav_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    sbet_mnav REAL,
                    bmnr_mnav REAL
                )
            ''')
            
            # 创建配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_config (
                    symbol TEXT PRIMARY KEY,
                    shares_outstanding REAL,
                    eth_holdings REAL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logging.info("数据库初始化完成")
        except Exception as e:
            logging.error(f"数据库初始化失败: {str(e)}")
            raise
    
    def get_stock_price(self, symbol):
        """使用 Finnhub API 获取股票价格"""
        try:
            url = "https://finnhub.io/api/v1/quote"
            params = {
                'symbol': symbol,
                'token': FINNHUB_API_KEY
            }
            
            logging.info(f"正在从 Finnhub 获取 {symbol} 价格...")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # 检查是否有错误信息
            if 'error' in data:
                logging.error(f"Finnhub API 错误: {data['error']}")
                return None
            
            # 检查是否有有效的价格数据
            if 'c' in data and data['c'] is not None and data['c'] > 0:
                current_price = float(data['c'])
                change = data.get('d', 0)
                change_percent = data.get('dp', 0)
                
                logging.info(f"✓ 从 Finnhub 获取 {symbol} 价格成功: ${current_price:.4f}")
                logging.info(f"  价格变化: ${change:.4f} ({change_percent:.2f}%)")
                
                return current_price
            else:
                logging.warning(f"Finnhub 未返回 {symbol} 的有效价格数据")
                return None
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Finnhub API 请求失败: {str(e)}")
            return None
        except (ValueError, KeyError) as e:
            logging.error(f"Finnhub API 响应解析失败: {str(e)}")
            logging.error(f"响应内容: {data}")
            return None
        except Exception as e:
            logging.error(f"获取 {symbol} 价格时出错: {str(e)}")
            return None
    
    def get_eth_price(self):
        """从 CoinGecko 获取 ETH 价格"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'ethereum',
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'ethereum' in data and 'usd' in data['ethereum']:
                price = float(data['ethereum']['usd'])
                
                # 记录额外信息（如果有的话）
                change_24h = data['ethereum'].get('usd_24h_change')
                market_cap = data['ethereum'].get('usd_market_cap')
                volume_24h = data['ethereum'].get('usd_24h_vol')
                
                logging.info(f"从 CoinGecko 获取 ETH 价格成功: ${price:.2f}")
                
                if change_24h is not None:
                    logging.info(f"24小时变化: {change_24h:.2f}%")
                if market_cap is not None:
                    logging.info(f"市值: ${market_cap:,.0f}")
                if volume_24h is not None:
                    logging.info(f"24小时成交量: ${volume_24h:,.0f}")
                
                return price
            else:
                logging.warning("CoinGecko 未返回 ETH 的有效价格数据")
                return None
                
        except requests.exceptions.RequestException as e:
            logging.error(f"CoinGecko API 请求失败: {str(e)}")
            return None
        except KeyError as e:
            logging.error(f"CoinGecko API 响应格式错误: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"CoinGecko ETH 价格获取失败: {str(e)}")
            return None
    
    def calculate_mnav(self, stock_price, shares_outstanding, eth_holdings, eth_price):
        """计算 mNAV
        mNAV = 股价 * 股本数量 / ETH持仓量 / ETH价格
        """
        if all(v is not None and v > 0 for v in [stock_price, shares_outstanding, eth_holdings, eth_price]):
            mnav = (stock_price * shares_outstanding) / (eth_holdings * eth_price)
            return mnav
        return None
    
    def update_prices_and_mnav(self):
        """更新价格和计算 mNAV"""
        with self.lock:
            try:
                logging.info("开始更新价格和 mNAV 数据...")
                
                # 获取价格数据，在请求之间添加延迟避免API速率限制
                sbet_price = self.get_stock_price('SBET')
                time.sleep(2)  # 等待2秒
                
                bmnr_price = self.get_stock_price('BMNR')
                time.sleep(2)  # 等待2秒
                
                eth_price = self.get_eth_price()
                
                # 获取配置数据
                config_data = self.get_config_from_db()
                
                # 存储价格数据
                with sqlite3.connect(self.get_db_path()) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO price_data (sbet_price, bmnr_price, eth_price)
                        VALUES (?, ?, ?)
                    ''', (sbet_price, bmnr_price, eth_price))
                    
                    # 计算和存储 mNAV
                    sbet_mnav = None
                    bmnr_mnav = None
                    
                    if 'SBET' in config_data and sbet_price is not None and eth_price is not None:
                        sbet_mnav = self.calculate_mnav(
                            sbet_price,
                            config_data['SBET']['shares_outstanding'],
                            config_data['SBET']['eth_holdings'],
                            eth_price
                        )
                    
                    if 'BMNR' in config_data and bmnr_price is not None and eth_price is not None:
                        bmnr_mnav = self.calculate_mnav(
                            bmnr_price,
                            config_data['BMNR']['shares_outstanding'],
                            config_data['BMNR']['eth_holdings'],
                            eth_price
                        )
                    
                    cursor.execute('''
                        INSERT INTO mnav_data (sbet_mnav, bmnr_mnav)
                        VALUES (?, ?)
                    ''', (sbet_mnav, bmnr_mnav))
                    
                    conn.commit()
                    
                # 更新历史数据CSV文件
                self.update_historical_csv(sbet_price, bmnr_price, eth_price, sbet_mnav, bmnr_mnav)
                
                logging.info("价格和 mNAV 数据更新完成")
                
            except Exception as e:
                logging.error(f"更新数据时出错: {str(e)}")
    
    def get_config_from_db(self):
        """从数据库获取配置信息"""
        try:
            with sqlite3.connect(self.get_db_path()) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT symbol, shares_outstanding, eth_holdings FROM stock_config')
                rows = cursor.fetchall()
                
                config = {}
                for row in rows:
                    symbol, shares, holdings = row
                    config[symbol] = {
                        'shares_outstanding': shares,
                        'eth_holdings': holdings
                    }
                return config
        except Exception as e:
            logging.error(f"获取配置数据时出错: {str(e)}")
            return {}
    
    def update_historical_csv(self, sbet_price, bmnr_price, eth_price, sbet_mnav, bmnr_mnav):
        """更新历史数据CSV文件"""
        try:
            csv_file = 'historical_data.csv'
            today = date.today().strftime('%Y-%m-%d')
            
            # 读取现有CSV文件
            try:
                df = pd.read_csv(csv_file)
            except FileNotFoundError:
                logging.warning("历史数据文件不存在，将创建新文件")
                return
            
            # 检查今天的数据是否已存在
            if today in df['date'].values:
                # 更新今天的数据
                mask = df['date'] == today
                if sbet_price is not None:
                    df.loc[mask, 'sbet_price'] = sbet_price
                if bmnr_price is not None:
                    df.loc[mask, 'bmnr_price'] = bmnr_price
                if eth_price is not None:
                    df.loc[mask, 'eth_price'] = eth_price
                if sbet_mnav is not None:
                    df.loc[mask, 'sbet_mnav'] = sbet_mnav
                if bmnr_mnav is not None:
                    df.loc[mask, 'bmnr_mnav'] = bmnr_mnav
                    
                logging.info(f"更新了 {today} 的历史数据")
            else:
                # 添加新的一天数据
                new_row = {
                    'date': today,
                    'sbet_price': sbet_price,
                    'bmnr_price': bmnr_price,
                    'eth_price': eth_price,
                    'sbet_shares': 129038060.0,
                    'bmnr_shares': 121700000.0,
                    'sbet_eth_holdings': 521939.0,
                    'bmnr_eth_holdings': 833137.0,
                    'sbet_mnav': sbet_mnav,
                    'bmnr_mnav': bmnr_mnav
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                logging.info(f"添加了 {today} 的新历史数据")
            
            # 保存更新后的CSV文件
            df.to_csv(csv_file, index=False)
            
        except Exception as e:
            logging.error(f"更新历史数据CSV文件时出错: {str(e)}")
    
    # 图表功能 - 获取历史数据（已注释）
    # def get_historical_data(self):
    #     """获取历史数据"""
    #     try:
    #         csv_file = 'historical_data.csv'
    #         df = pd.read_csv(csv_file)
    #         
    #         # 过滤掉价格为空的行
    #         df = df.dropna(subset=['sbet_price', 'bmnr_price'])
    #         
    #         # 转换日期格式
    #         df['date'] = pd.to_datetime(df['date'])
    #         
    #         # 按日期排序
    #         df = df.sort_values('date')
    #         
    #         return df
    #         
    #     except Exception as e:
    #         logging.error(f"获取历史数据时出错: {str(e)}")
    #         return pd.DataFrame()
    
    # 图表功能 - 生成历史图表（已注释）
    # def generate_chart(self):
    #     """生成历史价格和mNAV图表"""
    #     try:
    #         df = self.get_historical_data()
    #         
    #         if df.empty:
    #             logging.warning("没有历史数据可用于生成图表")
    #             return None
    #         
    #         # 设置中文字体
    #         plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
    #         plt.rcParams['axes.unicode_minus'] = False
    #         
    #         # 创建图表
    #         fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    #         
    #         # 绘制股价图
    #         ax1.plot(df['date'], df['sbet_price'], label='SBET Price', color='blue', linewidth=2)
    #         ax1.plot(df['date'], df['bmnr_price'], label='BMNR Price', color='red', linewidth=2)
    #         ax1.set_ylabel('股价 (USD)', fontsize=12)
    #         ax1.set_title('SBET & BMNR 股价历史走势', fontsize=14, fontweight='bold')
    #         ax1.legend()
    #         ax1.grid(True, alpha=0.3)
    #         
    #         # 绘制mNAV图
    #         ax2.plot(df['date'], df['sbet_mnav'], label='SBET mNAV', color='darkblue', linewidth=2)
    #         ax2.plot(df['date'], df['bmnr_mnav'], label='BMNR mNAV', color='darkred', linewidth=2)
    #         ax2.set_ylabel('mNAV', fontsize=12)
    #         ax2.set_xlabel('日期', fontsize=12)
    #         ax2.set_title('SBET & BMNR mNAV 历史走势', fontsize=14, fontweight='bold')
    #         ax2.legend()
    #         ax2.grid(True, alpha=0.3)
    #         
    #         # 设置日期格式
    #         ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    #         ax2.xaxis.set_major_locator(mdates.WeekdayLocator())
    #         plt.xticks(rotation=45)
    #         
    #         # 调整布局
    #         plt.tight_layout()
    #         
    #         # 将图表转换为base64字符串
    #         img_buffer = io.BytesIO()
    #         plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    #         img_buffer.seek(0)
    #         img_string = base64.b64encode(img_buffer.read()).decode('utf-8')
    #         plt.close(fig)
    #         
    #         logging.info("成功生成历史图表")
    #         return img_string
    #         
    #     except Exception as e:
    #         logging.error(f"生成图表时出错: {str(e)}")
    #         return None
    
    def should_update_data(self):
        """检查是否需要更新数据（Vercel部署用）"""
        try:
            with sqlite3.connect(self.get_db_path()) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT timestamp FROM price_data
                    ORDER BY timestamp DESC
                    LIMIT 1
                ''')
                result = cursor.fetchone()
                
                if not result:
                    return True  # 没有数据，需要更新
                
                last_update = datetime.fromisoformat(result[0])
                now = datetime.now()
                
                # 如果超过1小时没有更新，则需要更新
                time_diff = (now - last_update).total_seconds()
                return time_diff > 3600  # 3600秒 = 1小时
                
        except Exception as e:
            logging.error(f"检查更新时间时出错: {str(e)}")
            return True  # 出错时默认需要更新

    def get_latest_data(self):
        """获取最新的价格和 mNAV 数据"""
        try:
            # Vercel部署：检查是否需要更新数据
            if os.getenv('VERCEL') == '1' and self.should_update_data():
                logging.info("Vercel环境：检测到数据需要更新，执行更新...")
                self.update_prices_and_mnav()
            
            with sqlite3.connect(self.get_db_path()) as conn:
                cursor = conn.cursor()
                
                # 获取最新价格数据
                cursor.execute('''
                    SELECT timestamp, sbet_price, bmnr_price, eth_price
                    FROM price_data
                    ORDER BY timestamp DESC
                    LIMIT 1
                ''')
                price_row = cursor.fetchone()
                
                # 获取最新 mNAV 数据
                cursor.execute('''
                    SELECT timestamp, sbet_mnav, bmnr_mnav
                    FROM mnav_data
                    ORDER BY timestamp DESC
                    LIMIT 1
                ''')
                mnav_row = cursor.fetchone()
                
                return {
                    'price_data': price_row,
                    'mnav_data': mnav_row,
                    'config': self.get_config_from_db()
                }
        except Exception as e:
            logging.error(f"获取最新数据时出错: {str(e)}")
            return None

# 创建全局追踪器实例
tracker = MNAVTracker()

# Vercel部署：后台调度器不可用，改为按需更新
# 在serverless环境中，我们无法使用持久的后台调度器
# 数据更新将在每次API调用时检查并按需更新

# 本地开发时的调度器（Vercel部署时不会使用）
if os.getenv('VERCEL') != '1':  # 只在非Vercel环境启用调度器
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=tracker.update_prices_and_mnav,
        trigger="interval",
        minutes=60,
        id='update_mnav_job'
    )
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

@app.route('/')
def index():
    """主页面"""
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"首页渲染错误: {str(e)}")
        return f"应用启动中，请稍后刷新页面。错误: {str(e)}", 500

@app.route('/health')
def health_check():
    """健康检查端点"""
    return {"status": "ok", "message": "应用运行正常"}

@app.route('/api/data')
def get_data():
    """获取最新数据的 API 端点"""
    data = tracker.get_latest_data()
    if data:
        return jsonify({
            'success': True,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'success': False,
            'error': '无法获取数据'
        }), 500

@app.route('/api/update_config', methods=['POST'])
def update_config():
    """更新股本和ETH持仓配置"""
    try:
        data = request.json
        symbol = data.get('symbol')
        shares_outstanding = data.get('shares_outstanding')
        eth_holdings = data.get('eth_holdings')
        
        if not all([symbol, shares_outstanding, eth_holdings]):
            return jsonify({
                'success': False,
                'error': '缺少必要参数'
            }), 400
        
        with sqlite3.connect(self.get_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO stock_config (symbol, shares_outstanding, eth_holdings)
                VALUES (?, ?, ?)
            ''', (symbol, float(shares_outstanding), float(eth_holdings)))
            conn.commit()
        
        logging.info(f"配置更新成功: {symbol} - 股本: {shares_outstanding}, ETH持仓: {eth_holdings}")
        
        return jsonify({
            'success': True,
            'message': f'{symbol} 配置更新成功'
        })
        
    except Exception as e:
        logging.error(f"更新配置时出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/manual_update', methods=['POST'])
def manual_update():
    """手动触发数据更新"""
    try:
        tracker.update_prices_and_mnav()
        return jsonify({
            'success': True,
            'message': '数据更新成功',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logging.error(f"手动更新时出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 图表功能 - 图表API路由（已注释）
# @app.route('/api/chart')
# def get_chart():
#     """获取历史图表"""
#     try:
#         chart_image = tracker.generate_chart()
#         
#         if chart_image:
#             return jsonify({
#                 'success': True,
#                 'chart': chart_image,
#                 'timestamp': datetime.now().isoformat()
#             })
#         else:
#             return jsonify({
#                 'success': False,
#                 'error': '无法生成图表'
#             }), 500
#             
#     except Exception as e:
#         logging.error(f"获取图表时出错: {str(e)}")
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# 图表功能 - 历史数据API路由（已注释）
# @app.route('/api/historical_data')
# def get_historical_data_api():
#     """获取历史数据API"""
#     try:
#         df = tracker.get_historical_data()
#         
#         if not df.empty:
#             # 转换为JSON格式
#             data = []
#             for _, row in df.iterrows():
#                 data.append({
#                     'date': row['date'].strftime('%Y-%m-%d'),
#                     'sbet_price': float(row['sbet_price']) if pd.notna(row['sbet_price']) else None,
#                     'bmnr_price': float(row['bmnr_price']) if pd.notna(row['bmnr_price']) else None,
#                     'eth_price': float(row['eth_price']) if pd.notna(row['eth_price']) else None,
#                     'sbet_mnav': float(row['sbet_mnav']) if pd.notna(row['sbet_mnav']) else None,
#                     'bmnr_mnav': float(row['bmnr_mnav']) if pd.notna(row['bmnr_mnav']) else None
#                 })
#             
#             return jsonify({
#                 'success': True,
#                 'data': data,
#                 'count': len(data),
#                 'timestamp': datetime.now().isoformat()
#             })
#         else:
#             return jsonify({
#                 'success': False,
#                 'error': '没有历史数据',
#                 'data': []
#             })
#             
#     except Exception as e:
#         logging.error(f"获取历史数据时出错: {str(e)}")
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

def find_available_port(start_port=5000, max_port=5010):
    """查找可用端口"""
    import socket
    for port in range(start_port, max_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

# Vercel部署支持
import os

# 初始化应用和追踪器 (仅在非Vercel环境)
if not hasattr(app, 'tracker_initialized') and os.getenv('VERCEL') != '1':
    try:
        tracker.update_prices_and_mnav()
        app.tracker_initialized = True
    except Exception as e:
        logging.error(f"初始化数据更新失败: {str(e)}")
        # Vercel环境中不要阻止启动
        pass

# 本地开发运行
if __name__ == '__main__':
    # 查找可用端口
    available_port = find_available_port()
    
    if available_port:
        print(f"在端口 {available_port} 启动服务...")
        print(f"访问地址: http://localhost:{available_port}")
        app.run(host='0.0.0.0', port=available_port, debug=True)
    else:
        print("无法找到可用端口 (5000-5009)，请手动指定端口") 