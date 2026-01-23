/**
 * 全局错误处理模块
 * Requirements: 13.1, 13.2, 13.3, 13.4, 13.5
 */

class ErrorHandler {
    constructor() {
        this.isOnline = navigator.onLine;
        this.offlineBanner = null;
    }

    /**
     * 初始化错误处理
     */
    init() {
        // 全局错误处理
        window.onerror = (message, source, lineno, colno, error) => {
            this.handleError({
                type: 'RUNTIME_ERROR',
                message,
                source,
                lineno,
                colno,
                stack: error?.stack
            });
            return false;
        };

        // Promise 拒绝处理
        window.onunhandledrejection = (event) => {
            this.handleError({
                type: 'PROMISE_REJECTION',
                message: event.reason?.message || String(event.reason),
                stack: event.reason?.stack
            });
        };

        // 离线检测
        window.addEventListener('online', () => this.handleOnlineStatus(true));
        window.addEventListener('offline', () => this.handleOnlineStatus(false));
    }

    /**
     * 处理错误
     * @param {Object} error - 错误信息
     */
    handleError(error) {
        // 记录错误日志
        this.logError(error);

        // 根据错误类型显示不同提示
        const errorType = this.classifyError(error);
        this.showErrorMessage(errorType, error.message);
    }

    /**
     * 分类错误
     * Requirement 13.4: 区分错误类型
     */
    classifyError(error) {
        const message = error.message?.toLowerCase() || '';
        
        if (!navigator.onLine || message.includes('network') || message.includes('fetch')) {
            return 'NETWORK_ERROR';
        }
        if (error.status === 401 || message.includes('unauthorized') || message.includes('未登录')) {
            return 'UNAUTHORIZED';
        }
        if (error.status === 403 || message.includes('forbidden') || message.includes('权限')) {
            return 'FORBIDDEN';
        }
        if (error.status === 404 || message.includes('not found')) {
            return 'NOT_FOUND';
        }
        if (error.status >= 500 || message.includes('server')) {
            return 'SERVER_ERROR';
        }
        if (error.type === 'PROMISE_REJECTION') {
            return 'ASYNC_ERROR';
        }
        
        return 'UNKNOWN_ERROR';
    }

    /**
     * 显示错误消息
     */
    showErrorMessage(errorType, message) {
        const messages = {
            'NETWORK_ERROR': '网络连接失败，请检查网络设置',
            'UNAUTHORIZED': '登录已过期，请重新登录',
            'FORBIDDEN': '您没有权限执行此操作',
            'NOT_FOUND': '请求的资源不存在',
            'SERVER_ERROR': '服务器错误，请稍后重试',
            'ASYNC_ERROR': '操作失败，请重试',
            'UNKNOWN_ERROR': '发生未知错误'
        };

        const displayMessage = messages[errorType] || message || messages['UNKNOWN_ERROR'];
        
        if (window.NotificationManager) {
            window.NotificationManager.error(displayMessage);
        } else {
            console.error(displayMessage);
        }

        // 未授权时跳转登录
        if (errorType === 'UNAUTHORIZED') {
            setTimeout(() => {
                window.location.href = '/login';
            }, 1500);
        }
    }

    /**
     * 处理在线状态变化
     * Requirement 13.3: 离线检测
     */
    handleOnlineStatus(isOnline) {
        this.isOnline = isOnline;
        
        if (!isOnline) {
            this.showOfflineBanner();
        } else {
            this.hideOfflineBanner();
            if (window.NotificationManager) {
                window.NotificationManager.success('网络已恢复');
            }
        }
    }

    /**
     * 显示离线横幅
     */
    showOfflineBanner() {
        if (this.offlineBanner) return;
        
        this.offlineBanner = document.createElement('div');
        this.offlineBanner.className = 'offline-banner';
        this.offlineBanner.innerHTML = '⚠️ 网络已断开，部分功能可能不可用';
        document.body.prepend(this.offlineBanner);
    }

    /**
     * 隐藏离线横幅
     */
    hideOfflineBanner() {
        if (this.offlineBanner) {
            this.offlineBanner.remove();
            this.offlineBanner = null;
        }
    }

    /**
     * 记录错误日志
     * Requirement 13.5: 错误日志记录
     */
    logError(error) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            type: error.type,
            message: error.message,
            source: error.source,
            lineno: error.lineno,
            stack: error.stack,
            userAgent: navigator.userAgent,
            url: window.location.href
        };

        console.error('[ErrorHandler]', logEntry);
        
        // 可以在这里发送到服务器
        // this.sendToServer(logEntry);
    }
}

window.ErrorHandler = new ErrorHandler();
