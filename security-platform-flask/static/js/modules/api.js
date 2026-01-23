/**
 * API 客户端模块
 * Requirement 11.3: 创建 API 客户端模块
 */

class ApiError extends Error {
    constructor(code, message, status) {
        super(message);
        this.code = code;
        this.status = status;
        this.name = 'ApiError';
    }
}

class ApiClient {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }

    /**
     * 发送请求
     * @param {string} url - 请求 URL
     * @param {Object} options - 请求选项
     */
    async request(url, options = {}) {
        const fullUrl = this.baseUrl + url;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
        };

        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers,
            },
        };

        try {
            const response = await fetch(fullUrl, mergedOptions);
            const data = await response.json();

            // 处理统一响应格式
            if (data.success === false) {
                throw new ApiError(
                    data.error?.code || 'UNKNOWN_ERROR',
                    data.error?.message || '请求失败',
                    response.status
                );
            }

            // 返回 data 字段或整个响应
            return data.data !== undefined ? data.data : data;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            
            // 网络错误
            throw new ApiError('NETWORK_ERROR', '网络连接失败', 0);
        }
    }

    /**
     * GET 请求
     */
    async get(url, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        return this.request(fullUrl, { method: 'GET' });
    }

    /**
     * POST 请求
     */
    async post(url, data = {}) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    /**
     * PATCH 请求
     */
    async patch(url, data = {}) {
        return this.request(url, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    }

    /**
     * DELETE 请求
     */
    async delete(url) {
        return this.request(url, { method: 'DELETE' });
    }
}

// 导出单例
window.ApiClient = new ApiClient();
window.ApiError = ApiError;
