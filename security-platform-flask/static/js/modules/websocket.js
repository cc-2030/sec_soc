/**
 * WebSocket 客户端模块
 * Requirement 6.5: 前端 WebSocket 集成
 */

class WebSocketClient {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.eventHandlers = {};
    }

    /**
     * 连接 WebSocket 服务器
     */
    connect() {
        if (this.socket && this.connected) {
            return Promise.resolve();
        }

        return new Promise((resolve, reject) => {
            // 使用 socket.io 客户端
            this.socket = io({
                transports: ['websocket', 'polling'],
                reconnection: true,
                reconnectionAttempts: this.maxReconnectAttempts,
                reconnectionDelay: this.reconnectDelay,
                reconnectionDelayMax: 5000
            });

            this.socket.on('connect', () => {
                console.log('WebSocket 连接成功');
                this.connected = true;
                this.reconnectAttempts = 0;
                this._emit('connected', { connected: true });
                resolve();
            });

            this.socket.on('disconnect', (reason) => {
                console.log('WebSocket 断开连接:', reason);
                this.connected = false;
                this._emit('disconnected', { reason });
            });

            this.socket.on('connect_error', (error) => {
                console.error('WebSocket 连接错误:', error);
                this.reconnectAttempts++;
                if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                    this._emit('connection_failed', { error });
                    reject(error);
                }
            });

            // 监听服务器事件
            this.socket.on('connected', (data) => {
                this._emit('server_connected', data);
            });

            this.socket.on('alert', (data) => {
                this._emit('alert', data);
            });

            this.socket.on('dashboard_update', (data) => {
                this._emit('dashboard_update', data);
            });

            this.socket.on('subscribed', (data) => {
                this._emit('subscribed', data);
            });

            this.socket.on('error', (data) => {
                this._emit('error', data);
            });
        });
    }

    /**
     * 断开连接
     */
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
            this.connected = false;
        }
    }

    /**
     * 订阅告警
     * @param {string|string[]} severity - 严重级别或 'all'
     */
    subscribeAlerts(severity = 'all') {
        if (this.socket && this.connected) {
            this.socket.emit('subscribe_alerts', { severity });
        }
    }

    /**
     * 取消订阅告警
     */
    unsubscribeAlerts() {
        if (this.socket && this.connected) {
            this.socket.emit('unsubscribe_alerts');
        }
    }

    /**
     * 订阅仪表盘更新
     */
    subscribeDashboard() {
        if (this.socket && this.connected) {
            this.socket.emit('subscribe_dashboard');
        }
    }

    /**
     * 取消订阅仪表盘更新
     */
    unsubscribeDashboard() {
        if (this.socket && this.connected) {
            this.socket.emit('unsubscribe_dashboard');
        }
    }

    /**
     * 注册事件处理器
     * @param {string} event - 事件名称
     * @param {Function} handler - 处理函数
     */
    on(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }

    /**
     * 移除事件处理器
     * @param {string} event - 事件名称
     * @param {Function} handler - 处理函数
     */
    off(event, handler) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event] = this.eventHandlers[event].filter(h => h !== handler);
        }
    }

    /**
     * 触发事件
     * @param {string} event - 事件名称
     * @param {*} data - 事件数据
     */
    _emit(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => {
                try {
                    handler(data);
                } catch (e) {
                    console.error('事件处理器错误:', e);
                }
            });
        }
    }

    /**
     * 检查连接状态
     */
    isConnected() {
        return this.connected;
    }
}

// 导出单例
window.WebSocketClient = new WebSocketClient();
