"""
SBET 和 BMNR mNAV 实时追踪网页应用 - Vercel版本
主要功能：
1. 实时获取股价和 ETH 价格
2. 计算 mNAV 数据
3. 提供 Web 界面显示
4. 适配Vercel无服务器环境
"""

from flask import Flask, render_template, jsonify, request
import os
import json
import logging
from datetime import datetime, date
import threading
import time
import requests

# 配置日志 - 适配Vercel环境
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Vercel不支持文件日志，只使用控制台输出
    ]
)

app = Flask(__name__)

# Finnhub API 配置
FINNHUB_API_KEY = "d2bjrs9r01qrj4im3kkgd2bjrs9r01qrj4im3kl0"

# 股票配置数据 - 使用内存存储
STOCK_CONFIG = {
    'SBET': {
        'shares_outstanding': 129038060.0,  # 默认股本数量
        'eth_holdings': 521939.0,           # 默认ETH持仓量
        'symbol': 'SBET'
    },
    'BMNR': {
        'shares_outstanding': 121700000.0,  # 默认股本数量
        'eth_holdings': 833137.0,           # 默认ETH持仓量
        'symbol': 'BMNR'
    }
}

# 内存数据存储 - 替代SQLite数据库
class MemoryStorage:
    def __init__(self):
        self.price_data = []
        self.mnav_data = []
        self.config_data = STOCK_CONFIG.copy()
        
    def add_price_data(self, sbet_price, bmnr_price, eth_price):
        """添加价格数据"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'sbet_price': sbet_price,
            'bmnr_price': bmnr_price,
            'eth_price': eth_price
        }
        self.price_data.append(entry)
        # 只保留最近100条记录以节省内存
        if len(self.price_data) > 100:
            self.price_data = self.price_data[-100:]
    
    def add_mnav_data(self, sbet_mnav, bmnr_mnav):
        """添加mNAV数据"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'sbet_mnav': sbet_mnav,
            'bmnr_mnav': bmnr_mnav
        }
        self.mnav_data.append(entry)
        # 只保留最近100条记录以节省内存
        if len(self.mnav_data) > 100:
            self.mnav_data = self.mnav_data[-100:]
    
    def get_latest_price_data(self):
        """获取最新价格数据"""
        if self.price_data:
            latest = self.price_data[-1]
            return (latest['timestamp'], latest['sbet_price'], latest['bmnr_price'], latest['eth_price'])
        return None
    
    def get_latest_mnav_data(self):
        """获取最新mNAV数据"""
        if self.mnav_data:
            latest = self.mnav_data[-1]
            return (latest['timestamp'], latest['sbet_mnav'], latest['bmnr_mnav'])
        return None
    
    def update_config(self, symbol, shares_outstanding, eth_holdings):
        """更新配置数据"""
        if symbol in self.config_data:
            self.config_data[symbol]['shares_outstanding'] = shares_outstanding
            self.config_data[symbol]['eth_holdings'] = eth_holdings
            return True
        return False

# 创建全局存储实例
storage = MemoryStorage()

class MNAVTracker:
    def __init__(self):
        """初始化 mNAV 追踪器"""
        self.lock = threading.Lock()
        
        # 设置 HTTP 会话用于 API 请求
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
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
                config_data = storage.config_data
                
                # 存储价格数据到内存
                storage.add_price_data(sbet_price, bmnr_price, eth_price)
                
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
                
                # 存储mNAV数据到内存
                storage.add_mnav_data(sbet_mnav, bmnr_mnav)
                
                logging.info("价格和 mNAV 数据更新完成")
                
            except Exception as e:
                logging.error(f"更新数据时出错: {str(e)}")
    
    def get_latest_data(self):
        """获取最新的价格和 mNAV 数据"""
        try:
            return {
                'price_data': storage.get_latest_price_data(),
                'mnav_data': storage.get_latest_mnav_data(),
                'config': storage.config_data
            }
        except Exception as e:
            logging.error(f"获取最新数据时出错: {str(e)}")
            return None

# 创建全局追踪器实例
tracker = MNAVTracker()

# Vercel环境下不使用定时任务调度器，因为无服务器函数是无状态的
# 在每次请求时按需更新数据

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

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
        
        # 更新内存中的配置
        success = storage.update_config(symbol, float(shares_outstanding), float(eth_holdings))
        
        if success:
            logging.info(f"配置更新成功: {symbol} - 股本: {shares_outstanding}, ETH持仓: {eth_holdings}")
            
            return jsonify({
                'success': True,
                'message': f'{symbol} 配置更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'未知股票代码: {symbol}'
            }), 400
        
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

# Vercel部署需要的应用对象
app_instance = app

if __name__ == '__main__':
    # 本地开发时启动应用
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 