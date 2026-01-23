/**
 * 通知管理模块
 * Requirements: 8.1, 8.2, 8.4
 */

class NotificationManager {
    constructor() {
        this.permission = 'default';
        this.container = null;
    }

    /**
     * 初始化通知系统
     */
    init() {
        // 创建页面内通知容器
        this.container = document.createElement('div');
        this.container.id = 'notification-container';
        this.container.className = 'notification-container';
        document.body.appendChild(this.container);

        // 检查浏览器通知权限
        if ('Notification' in window) {
            this.permission = Notification.permission;
        }
    }

    /**
     * 请求浏览器通知权限
     * Requirement 8.1: 请求浏览器通知权限
     */
    async requestPermission() {
        if (!('Notification' in window)) {
            console.warn('浏览器不支持桌面通知');
            return false;
        }

        if (Notification.permission === 'granted') {
            this.permission = 'granted';
            return true;
        }

        if (Notification.permission !== 'denied') {
            const permission = await Notification.requestPermission();
            this.permission = permission;
            return permission === 'granted';
        }

        return false;
    }

    /**
     * 发送桌面通知
     * Requirement 8.2: 高危告警发送桌面通知
     * @param {string} title - 通知标题
     * @param {Object} options - 通知选项
     */
    sendDesktopNotification(title, options = {}) {
        if (this.permission !== 'granted') {
            return null;
        }

        const notification = new Notification(title, {
            icon: '/static/img/alert-icon.png',
            badge: '/static/img/badge.png',
            tag: options.tag || 'security-alert',
            requireInteraction: options.severity === 'critical',
            ...options
        });

        // Requirement 8.4: 点击通知跳转到告警详情
        notification.onclick = () => {
            window.focus();
            if (options.url) {
                window.location.href = options.url;
            }
            notification.close();
        };

        return notification;
    }

    /**
     * 显示页面内通知
     * @param {string} message - 消息内容
     * @param {string} type - 类型 (success, error, warning, info)
     * @param {number} duration - 显示时长（毫秒）
     */
    show(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icon = this._getIcon(type);
        notification.innerHTML = `
            <span class="notification-icon">${icon}</span>
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        `;

        // 关闭按钮
        notification.querySelector('.notification-close').onclick = () => {
            this._remove(notification);
        };

        this.container.appendChild(notification);

        // 自动消失
        if (duration > 0) {
            setTimeout(() => this._remove(notification), duration);
        }

        return notification;
    }

    /**
     * 显示成功通知
     */
    success(message, duration = 3000) {
        return this.show(message, 'success', duration);
    }

    /**
     * 显示错误通知
     */
    error(message, duration = 5000) {
        return this.show(message, 'error', duration);
    }

    /**
     * 显示警告通知
     */
    warning(message, duration = 4000) {
        return this.show(message, 'warning', duration);
    }

    /**
     * 显示信息通知
     */
    info(message, duration = 3000) {
        return this.show(message, 'info', duration);
    }

    /**
     * 处理告警通知
     * @param {Object} alert - 告警数据
     */
    handleAlert(alert) {
        const severity = alert.severity || 'medium';
        const title = alert.data?.title || '安全告警';
        
        // 页面内通知
        const typeMap = {
            'critical': 'error',
            'high': 'warning',
            'medium': 'warning',
            'low': 'info'
        };
        this.show(`[${severity.toUpperCase()}] ${title}`, typeMap[severity] || 'info');

        // 高危告警发送桌面通知
        if (severity === 'critical' || severity === 'high') {
            this.sendDesktopNotification(`安全告警: ${title}`, {
                body: `严重级别: ${severity}`,
                severity: severity,
                url: `/incidents/${alert.data?.id || ''}`,
                tag: `alert-${alert.data?.id || Date.now()}`
            });
        }
    }

    /**
     * 获取图标
     */
    _getIcon(type) {
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        return icons[type] || icons.info;
    }

    /**
     * 移除通知
     */
    _remove(notification) {
        notification.classList.add('notification-fade-out');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }
}

// 导出单例
window.NotificationManager = new NotificationManager();
