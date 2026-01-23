/**
 * 加载指示器组件
 * Requirement 12.1, 12.4: 创建加载指示器组件
 */

class Loading {
    constructor() {
        this.overlay = null;
        this.count = 0;
    }

    /**
     * 显示全局加载遮罩
     */
    show(message = '加载中...') {
        this.count++;
        
        if (this.overlay) return;
        
        this.overlay = document.createElement('div');
        this.overlay.className = 'loading-overlay';
        this.overlay.innerHTML = `
            <div class="loading-content">
                <div class="spinner"></div>
                <div class="loading-message">${message}</div>
            </div>
        `;
        
        document.body.appendChild(this.overlay);
        requestAnimationFrame(() => {
            this.overlay.classList.add('loading-visible');
        });
    }

    /**
     * 隐藏全局加载遮罩
     */
    hide() {
        this.count--;
        if (this.count > 0) return;
        
        if (!this.overlay) return;
        
        this.overlay.classList.remove('loading-visible');
        setTimeout(() => {
            if (this.overlay && this.overlay.parentNode) {
                this.overlay.parentNode.removeChild(this.overlay);
            }
            this.overlay = null;
        }, 200);
    }

    /**
     * 设置按钮加载状态
     * @param {HTMLElement} button - 按钮元素
     * @param {boolean} loading - 是否加载中
     */
    setButtonLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            button.dataset.originalText = button.textContent;
            button.innerHTML = '<span class="btn-spinner"></span> 处理中...';
        } else {
            button.disabled = false;
            button.textContent = button.dataset.originalText || button.textContent;
        }
    }
}

window.Loading = new Loading();
