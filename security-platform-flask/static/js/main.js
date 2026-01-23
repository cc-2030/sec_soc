/**
 * 主入口文件
 * Requirements: 11.1, 11.2
 */

document.addEventListener('DOMContentLoaded', () => {
    // 初始化全局错误处理
    if (window.ErrorHandler) {
        window.ErrorHandler.init();
    }

    // 初始化通知系统
    if (window.NotificationManager) {
        window.NotificationManager.init();
        window.NotificationManager.requestPermission();
    }

    // 初始化 WebSocket 连接
    initWebSocket();

    // 根据页面加载对应模块
    const page = document.body.dataset.page;
    if (page) {
        loadPageModule(page);
    }
});

/**
 * 初始化 WebSocket
 */
async function initWebSocket() {
    if (!window.WebSocketClient) return;

    try {
        await window.WebSocketClient.connect();
        
        // 订阅告警
        window.WebSocketClient.subscribeAlerts('all');
        
        // 处理告警
        window.WebSocketClient.on('alert', (data) => {
            if (window.NotificationManager) {
                window.NotificationManager.handleAlert(data);
            }
        });
        
        console.log('WebSocket 已连接');
    } catch (e) {
        console.warn('WebSocket 连接失败:', e);
    }
}

/**
 * 加载页面模块
 */
function loadPageModule(page) {
    const modules = {
        'dashboard': () => import('/static/js/pages/dashboard.js'),
        'assets': () => import('/static/js/pages/assets.js'),
        'vulnerabilities': () => import('/static/js/pages/vulnerabilities.js'),
        'incidents': () => import('/static/js/pages/incidents.js'),
    };

    if (modules[page]) {
        modules[page]().then(module => {
            if (module.init) module.init();
        }).catch(e => {
            console.warn(`页面模块 ${page} 加载失败:`, e);
        });
    }
}
