/**
 * 工具函数模块
 * Requirement 11.3: 创建工具函数模块
 */

/**
 * 格式化时间
 * @param {string} isoString - ISO 格式时间字符串
 * @param {Object} options - 格式化选项
 */
function formatTime(isoString, options = {}) {
    if (!isoString) return '-';
    
    const date = new Date(isoString);
    const now = new Date();
    const diff = now - date;
    
    // 相对时间
    if (options.relative) {
        if (diff < 60000) return '刚刚';
        if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`;
        if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`;
    }
    
    // 完整格式
    const pad = n => n.toString().padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

/**
 * 格式化数字（千分位）
 * @param {number} num - 数字
 */
function formatNumber(num) {
    if (num === null || num === undefined) return '-';
    return num.toLocaleString('zh-CN');
}

/**
 * 防抖函数
 * @param {Function} fn - 要防抖的函数
 * @param {number} delay - 延迟时间（毫秒）
 */
function debounce(fn, delay = 300) {
    let timer = null;
    return function (...args) {
        if (timer) clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

/**
 * 节流函数
 * @param {Function} fn - 要节流的函数
 * @param {number} delay - 间隔时间（毫秒）
 */
function throttle(fn, delay = 300) {
    let lastTime = 0;
    return function (...args) {
        const now = Date.now();
        if (now - lastTime >= delay) {
            lastTime = now;
            fn.apply(this, args);
        }
    };
}

/**
 * 深拷贝
 */
function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

/**
 * 生成 UUID
 */
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// 导出
window.Utils = {
    formatTime,
    formatNumber,
    debounce,
    throttle,
    deepClone,
    generateUUID
};
