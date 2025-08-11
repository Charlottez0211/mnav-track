/**
 * SBET & BMNR mNAV 实时追踪系统前端 JavaScript
 * 功能：数据获取、界面更新、用户交互处理
 */

class MNAVApp {
    constructor() {
        this.isUpdating = false;
        this.updateInterval = null;
        this.initializeApp();
    }

    /**
     * 初始化应用
     */
    async initializeApp() {
        this.setupEventListeners();
        
        // 先检查配置状态
        await this.checkConfigStatus();
        
        // 然后加载数据
        await this.loadData();
        
        this.startAutoRefresh();
        this.showNotification('系统启动成功', 'success');
    }

    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 手动更新按钮
        const manualUpdateBtn = document.getElementById('manual-update-btn');
        manualUpdateBtn.addEventListener('click', () => this.manualUpdate());

        // SBET 配置表单
        const sbetForm = document.getElementById('sbet-config-form');
        sbetForm.addEventListener('submit', (e) => this.handleConfigUpdate(e, 'SBET'));

        // BMNR 配置表单
        const bmnrForm = document.getElementById('bmnr-config-form');
        bmnrForm.addEventListener('submit', (e) => this.handleConfigUpdate(e, 'BMNR'));

        // 图表刷新按钮 (已注释)
        // const refreshChartBtn = document.getElementById('refresh-chart-btn');
        // refreshChartBtn.addEventListener('click', () => this.refreshChart());

        // 页面可见性改变时的处理
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.loadData(); // 页面重新可见时刷新数据
            }
        });
    }

    /**
     * 从服务器加载数据
     */
    async loadData() {
        try {
            this.updateSystemStatus('loading', '正在获取数据...');
            
            const response = await fetch('/api/data');
            const result = await response.json();

            if (result.success && result.data) {
                this.updateUI(result.data);
                this.updateSystemStatus('online', '系统正常');
                this.updateLastUpdateTime();
                
                // 调试信息：显示当前配置
                if (result.data.config) {
                    console.log('当前加载的配置数据:', result.data.config);
                    this.updateConfigStatus('已加载', '--');
                }
            } else {
                throw new Error(result.error || '数据格式错误');
            }
        } catch (error) {
            console.error('获取数据失败:', error);
            this.updateSystemStatus('error', '连接失败');
            this.showNotification(`获取数据失败: ${error.message}`, 'error');
        }
    }

    /**
     * 更新用户界面
     */
    updateUI(data) {
        const { price_data, mnav_data, config } = data;

        // 更新价格数据
        if (price_data) {
            const [timestamp, sbetPrice, bmnrPrice, ethPrice] = price_data;
            
            this.updateElement('sbet-price', sbetPrice ? `$${sbetPrice.toFixed(4)}` : '$--');
            this.updateElement('bmnr-price', bmnrPrice ? `$${bmnrPrice.toFixed(4)}` : '$--');
            this.updateElement('eth-price', ethPrice ? `$${ethPrice.toFixed(2)}` : '$--');
            
            // 更新状态指示器
            this.updateCardStatus('sbet-status', sbetPrice !== null);
            this.updateCardStatus('bmnr-status', bmnrPrice !== null);
            this.updateCardStatus('eth-status', ethPrice !== null);
        }

        // 更新 mNAV 数据
        if (mnav_data) {
            const [timestamp, sbetMNAV, bmnrMNAV] = mnav_data;
            
            this.updateElement('sbet-mnav', sbetMNAV ? sbetMNAV.toFixed(6) : '--');
            this.updateElement('bmnr-mnav', bmnrMNAV ? bmnrMNAV.toFixed(6) : '--');
        }

        // 更新配置信息
        if (config) {
            if (config.SBET) {
                this.updateElement('sbet-shares', config.SBET.shares_outstanding.toLocaleString());
                this.updateElement('sbet-eth-holdings', config.SBET.eth_holdings.toLocaleString());
                
                // 更新配置表单的当前值
                const sbetSharesInput = document.getElementById('sbet-shares-input');
                const sbetEthInput = document.getElementById('sbet-eth-input');
                if (sbetSharesInput.value === '') sbetSharesInput.value = config.SBET.shares_outstanding;
                if (sbetEthInput.value === '') sbetEthInput.value = config.SBET.eth_holdings;
            }

            if (config.BMNR) {
                this.updateElement('bmnr-shares', config.BMNR.shares_outstanding.toLocaleString());
                this.updateElement('bmnr-eth-holdings', config.BMNR.eth_holdings.toLocaleString());
                
                // 更新配置表单的当前值
                const bmnrSharesInput = document.getElementById('bmnr-shares-input');
                const bmnrEthInput = document.getElementById('bmnr-eth-input');
                if (bmnrSharesInput.value === '') bmnrSharesInput.value = config.BMNR.shares_outstanding;
                if (bmnrEthInput.value === '') bmnrEthInput.value = config.BMNR.eth_holdings;
            }
        }
    }

    /**
     * 更新单个元素的内容
     */
    updateElement(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    /**
     * 更新卡片状态指示器
     */
    updateCardStatus(statusId, isOnline) {
        const statusElement = document.getElementById(statusId);
        if (statusElement) {
            statusElement.className = `card-status ${isOnline ? 'online' : 'error'}`;
        }
    }

    /**
     * 更新系统状态
     */
    updateSystemStatus(status, message) {
        const statusElement = document.getElementById('system-status');
        if (statusElement) {
            statusElement.className = `status-value ${status}`;
            statusElement.textContent = message;
        }
    }

    /**
     * 更新最后更新时间
     */
    updateLastUpdateTime() {
        const lastUpdateElement = document.getElementById('last-update');
        if (lastUpdateElement) {
            const now = new Date();
            const timeString = now.toLocaleTimeString('zh-CN', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            lastUpdateElement.textContent = timeString;
        }
    }

    /**
     * 手动更新数据
     */
    async manualUpdate() {
        if (this.isUpdating) return;

        this.isUpdating = true;
        const updateBtn = document.getElementById('manual-update-btn');
        const icon = updateBtn.querySelector('i');
        
        // 添加加载状态
        updateBtn.classList.add('loading');
        icon.classList.add('fa-spin');
        updateBtn.disabled = true;

        try {
            // 先触发服务器更新
            const updateResponse = await fetch('/api/manual_update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const updateResult = await updateResponse.json();
            
            if (updateResult.success) {
                // 更新成功后获取最新数据
                await this.loadData();
                this.showNotification('数据更新成功', 'success');
            } else {
                throw new Error(updateResult.error || '更新失败');
            }
        } catch (error) {
            console.error('手动更新失败:', error);
            this.showNotification(`更新失败: ${error.message}`, 'error');
        } finally {
            // 移除加载状态
            updateBtn.classList.remove('loading');
            icon.classList.remove('fa-spin');
            updateBtn.disabled = false;
            this.isUpdating = false;
        }
    }

    /**
     * 处理配置更新
     */
    async handleConfigUpdate(event, symbol) {
        event.preventDefault();
        
        const form = event.target;
        const sharesInput = form.querySelector(`#${symbol.toLowerCase()}-shares-input`);
        const ethInput = form.querySelector(`#${symbol.toLowerCase()}-eth-input`);
        const submitBtn = form.querySelector('button[type="submit"]');

        const shares = parseFloat(sharesInput.value);
        const ethHoldings = parseFloat(ethInput.value);

        if (isNaN(shares) || isNaN(ethHoldings) || shares <= 0 || ethHoldings <= 0) {
            this.showNotification('请输入有效的数值', 'error');
            return;
        }

        // 添加加载状态
        submitBtn.disabled = true;
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 保存中...';

        try {
            const response = await fetch('/api/update_config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    symbol: symbol,
                    shares_outstanding: shares,
                    eth_holdings: ethHoldings
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification(`${symbol} 配置保存成功，mNAV已重新计算`, 'success');
                
                // 更新配置状态显示
                const currentTime = new Date().toISOString();
                const localTime = this.formatLocalTime(currentTime);
                this.updateConfigStatus('已保存并重新计算', localTime);
                
                // 立即更新界面显示最新的数据
                if (result.latest_data) {
                    this.updateUI(result.latest_data);
                    console.log(`${symbol} 配置更新后的最新数据:`, result.latest_data);
                } else {
                    // 如果没有最新数据，则重新加载
                    await this.loadData();
                }
                
                // 保存到本地存储作为备份
                this.saveToLocalStorage(symbol, shares, ethHoldings);
                
                // 显示当前配置信息
                console.log(`${symbol} 配置已更新:`, result.config);
                
                // 验证界面是否已更新
                this.validateUIUpdate(symbol, shares, ethHoldings);
            } else {
                throw new Error(result.error || '配置保存失败');
            }
        } catch (error) {
            console.error('配置保存失败:', error);
            this.showNotification(`配置保存失败: ${error.message}`, 'error');
            
            // 显示详细的错误信息
            if (error.message.includes('未知股票代码')) {
                this.showNotification('系统错误：股票代码配置问题，请联系管理员', 'error');
            }
        } finally {
            // 恢复按钮状态
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    }

    /**
     * 验证界面更新是否正确
     */
    validateUIUpdate(symbol, shares, ethHoldings) {
        setTimeout(() => {
            const sharesElement = document.getElementById(`${symbol.toLowerCase()}-shares`);
            const ethElement = document.getElementById(`${symbol.toLowerCase()}-eth-holdings`);
            
            if (sharesElement && ethElement) {
                const displayedShares = parseFloat(sharesElement.textContent.replace(/,/g, ''));
                const displayedEth = parseFloat(ethElement.textContent.replace(/,/g, ''));
                
                console.log(`界面验证 - ${symbol}:`);
                console.log(`  期望: 股本=${shares}, ETH持仓=${ethHoldings}`);
                console.log(`  实际: 股本=${displayedShares}, ETH持仓=${displayedEth}`);
                
                if (Math.abs(displayedShares - shares) < 1 && Math.abs(displayedEth - ethHoldings) < 1) {
                    console.log(`✓ ${symbol} 界面更新正确`);
                } else {
                    console.warn(`⚠ ${symbol} 界面更新可能有问题`);
                }
            }
        }, 1000); // 延迟1秒检查，确保DOM已更新
    }

    /**
     * 保存配置到本地存储
     */
    saveToLocalStorage(symbol, shares, ethHoldings) {
        try {
            const config = {
                symbol: symbol,
                shares_outstanding: shares,
                eth_holdings: ethHoldings,
                timestamp: new Date().toISOString()
            };
            
            localStorage.setItem(`mnav_config_${symbol}`, JSON.stringify(config));
            console.log(`${symbol} 配置已保存到本地存储`);
        } catch (error) {
            console.error('保存到本地存储失败:', error);
        }
    }

    /**
     * 从本地存储加载配置
     */
    loadFromLocalStorage(symbol) {
        try {
            const stored = localStorage.getItem(`mnav_config_${symbol}`);
            if (stored) {
                const config = JSON.parse(stored);
                console.log(`从本地存储加载 ${symbol} 配置:`, config);
                return config;
            }
        } catch (error) {
            console.error('从本地存储加载配置失败:', error);
        }
        return null;
    }

    /**
     * 重置配置到默认值
     */
    resetConfig(symbol) {
        const defaultConfig = {
            'SBET': { shares: 129038060.0, eth: 521939.0 },
            'BMNR': { shares: 121700000.0, eth: 833137.0 }
        };
        
        const config = defaultConfig[symbol];
        if (config) {
            const sharesInput = document.getElementById(`${symbol.toLowerCase()}-shares-input`);
            const ethInput = document.getElementById(`${symbol.toLowerCase()}-eth-input`);
            
            if (sharesInput && ethInput) {
                sharesInput.value = config.shares;
                ethInput.value = config.eth;
                
                this.showNotification(`${symbol} 配置已重置为默认值`, 'info');
                
                // 自动保存重置后的配置
                this.autoSaveConfig(symbol, config.shares, config.eth);
            }
        }
    }

    /**
     * 自动保存配置（用于重置后）
     */
    async autoSaveConfig(symbol, shares, ethHoldings) {
        try {
            const response = await fetch('/api/update_config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    symbol: symbol,
                    shares_outstanding: shares,
                    eth_holdings: ethHoldings
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showNotification(`${symbol} 默认配置已自动保存`, 'success');
                
                // 更新配置状态显示
                const currentTime = new Date().toISOString();
                const localTime = this.formatLocalTime(currentTime);
                this.updateConfigStatus('已重置并保存', localTime);
                
                // 刷新数据
                await this.loadData();
            }
        } catch (error) {
            console.error('自动保存配置失败:', error);
        }
    }

    /**
     * 更新配置状态显示
     */
    updateConfigStatus(status, lastSaveTime) {
        const statusElement = document.getElementById('config-status');
        const lastSaveElement = document.getElementById('last-save-time');
        
        if (statusElement) {
            statusElement.textContent = status;
        }
        
        if (lastSaveElement && lastSaveTime) {
            lastSaveElement.textContent = lastSaveTime;
        }
    }

    /**
     * 初始化配置表单
     */
    initializeConfigForms() {
        // 为每个配置表单添加重置功能
        const sbetForm = document.getElementById('sbet-config-form');
        const bmnrForm = document.getElementById('bmnr-config-form');
        
        if (sbetForm) {
            // 检查是否有本地存储的配置
            const sbetLocalConfig = this.loadFromLocalStorage('SBET');
            if (sbetLocalConfig) {
                const sharesInput = document.getElementById('sbet-shares-input');
                const ethInput = document.getElementById('sbet-eth-input');
                if (sharesInput && ethInput) {
                    sharesInput.value = sbetLocalConfig.shares_outstanding;
                    ethInput.value = sbetLocalConfig.eth_holdings;
                }
            }
        }
        
        if (bmnrForm) {
            // 检查是否有本地存储的配置
            const bmnrLocalConfig = this.loadFromLocalStorage('BMNR');
            if (bmnrLocalConfig) {
                const sharesInput = document.getElementById('bmnr-shares-input');
                const ethInput = document.getElementById('bmnr-eth-input');
                if (sharesInput && ethInput) {
                    sharesInput.value = bmnrLocalConfig.shares_outstanding;
                    ethInput.value = bmnrLocalConfig.eth_holdings;
                }
            }
        }
    }

    /**
     * 显示通知
     */
    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');
        const notification = document.createElement('div');
        
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <i class="fas ${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;

        container.appendChild(notification);

        // 3秒后自动移除通知
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease forwards';
                setTimeout(() => {
                    container.removeChild(notification);
                }, 300);
            }
        }, 3000);
    }

    /**
     * 根据通知类型获取图标
     */
    getNotificationIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            info: 'fa-info-circle',
            warning: 'fa-exclamation-triangle'
        };
        return icons[type] || icons.info;
    }

    /**
     * 刷新图表 (已注释)
     */
    // async refreshChart() {
    //     const chartLoading = document.getElementById('chart-loading');
    //     const chartContent = document.getElementById('chart-content');
    //     const chartImg = document.getElementById('historical-chart');
    //     const chartPlaceholder = document.getElementById('chart-placeholder');
    //     const refreshBtn = document.getElementById('refresh-chart-btn');

    //     try {
    //         // 显示加载状态
    //         chartLoading.style.display = 'flex';
    //         chartContent.style.display = 'none';
    //         refreshBtn.disabled = true;
    //         refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 生成中...';

    //         // 获取图表数据
    //         const response = await fetch('/api/chart');
    //         const result = await response.json();

    //         if (result.success && result.chart) {
    //             // 显示图表
    //             chartImg.src = `data:image/png;base64,${result.chart}`;
    //             chartImg.style.display = 'block';
    //             chartPlaceholder.style.display = 'none';
    //             this.showNotification('图表更新成功', 'success');
    //         } else {
    //             throw new Error(result.error || '获取图表失败');
    //         }

    //     } catch (error) {
    //         console.error('刷新图表失败:', error);
    //         this.showNotification(`图表生成失败: ${error.message}`, 'error');
            
    //         // 显示占位符
    //         chartImg.style.display = 'none';
    //         chartPlaceholder.style.display = 'flex';
    //     } finally {
    //         // 隐藏加载状态
    //         chartLoading.style.display = 'none';
    //         chartContent.style.display = 'block';
            
    //         // 恢复按钮状态
    //         refreshBtn.disabled = false;
    //         refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> 刷新图表';
    //     }
    // }

    /**
     * 获取历史数据
     */
    async getHistoricalData() {
        try {
            const response = await fetch('/api/historical_data');
            const result = await response.json();

            if (result.success) {
                return result.data;
            } else {
                throw new Error(result.error || '获取历史数据失败');
            }
        } catch (error) {
            console.error('获取历史数据失败:', error);
            this.showNotification(`获取历史数据失败: ${error.message}`, 'error');
            return [];
        }
    }

    /**
     * 开始自动刷新
     */
    startAutoRefresh() {
        // 每5分钟自动刷新一次界面数据（服务器每30分钟更新一次数据）
        this.updateInterval = setInterval(() => {
            if (!document.hidden) { // 只在页面可见时刷新
                this.loadData();
            }
        }, 5 * 60 * 1000); // 5分钟
    }

    /**
     * 停止自动刷新
     */
    stopAutoRefresh() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    /**
     * 检查配置状态
     */
    async checkConfigStatus() {
        try {
            const response = await fetch('/api/config_status');
            const result = await response.json();
            
            if (result.success) {
                console.log('当前配置状态:', result);
                
                // 将UTC时间转换为本地时间显示
                const localTime = this.formatLocalTime(result.timestamp);
                this.updateConfigStatus('已加载', localTime);
                
                // 更新配置表单的当前值
                this.updateConfigFormValues(result.config);
                
                return result.config;
            } else {
                console.error('获取配置状态失败:', result.error);
                return null;
            }
        } catch (error) {
            console.error('检查配置状态时出错:', error);
            return null;
        }
    }

    /**
     * 将UTC时间转换为本地时间显示
     */
    formatLocalTime(utcTimestamp) {
        try {
            // 解析UTC时间戳
            const utcDate = new Date(utcTimestamp);
            
            // 检查是否为有效日期
            if (isNaN(utcDate.getTime())) {
                throw new Error('无效的时间戳');
            }
            
            // 获取当前时区偏移量（分钟）
            const timezoneOffset = new Date().getTimezoneOffset();
            
            // 转换为本地时间
            const localDate = new Date(utcDate.getTime() - (timezoneOffset * 60 * 1000));
            
            // 格式化为易读的本地时间字符串
            const year = localDate.getFullYear();
            const month = String(localDate.getMonth() + 1).padStart(2, '0');
            const day = String(localDate.getDate()).padStart(2, '0');
            const hours = String(localDate.getHours()).padStart(2, '0');
            const minutes = String(localDate.getMinutes()).padStart(2, '0');
            const seconds = String(localDate.getSeconds()).padStart(2, '0');
            
            // 获取时区信息
            const timezone = this.getTimezoneInfo();
            
            return `${year}-${month}-${day} ${hours}:${minutes}:${seconds} ${timezone}`;
        } catch (error) {
            console.error('时间转换失败:', error);
            // 如果转换失败，返回原始时间戳
            return utcTimestamp;
        }
    }

    /**
     * 获取时区信息
     */
    getTimezoneInfo() {
        try {
            const now = new Date();
            const timezoneOffset = now.getTimezoneOffset();
            const timezoneHours = Math.abs(Math.floor(timezoneOffset / 60));
            const timezoneMinutes = Math.abs(timezoneOffset % 60);
            
            let timezoneString = '';
            if (timezoneOffset <= 0) {
                // 东半球（UTC+）
                timezoneString = `(UTC+${timezoneHours.toString().padStart(2, '0')}:${timezoneMinutes.toString().padStart(2, '0')})`;
            } else {
                // 西半球（UTC-）
                timezoneString = `(UTC-${timezoneHours.toString().padStart(2, '0')}:${timezoneMinutes.toString().padStart(2, '0')})`;
            }
            
            return timezoneString;
        } catch (error) {
            console.error('获取时区信息失败:', error);
            return '(本地时间)';
        }
    }

    /**
     * 更新配置表单的值
     */
    updateConfigFormValues(config) {
        if (config.SBET) {
            const sbetSharesInput = document.getElementById('sbet-shares-input');
            const sbetEthInput = document.getElementById('sbet-eth-input');
            if (sbetSharesInput && sbetEthInput) {
                sbetSharesInput.value = config.SBET.shares_outstanding;
                sbetEthInput.value = config.SBET.eth_holdings;
            }
        }
        
        if (config.BMNR) {
            const bmnrSharesInput = document.getElementById('bmnr-shares-input');
            const bmnrEthInput = document.getElementById('bmnr-eth-input');
            if (bmnrSharesInput && bmnrEthInput) {
                bmnrSharesInput.value = config.BMNR.shares_outstanding;
                bmnrEthInput.value = config.BMNR.eth_holdings;
            }
        }
    }
}

// 添加滑出动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.mnavApp = new MNAVApp();
});

// 页面卸载时清理资源
window.addEventListener('beforeunload', () => {
    if (window.mnavApp) {
        window.mnavApp.stopAutoRefresh();
    }
}); 