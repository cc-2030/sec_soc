/**
 * 模态框组件
 * Requirement 12.1, 12.3: 创建模态框组件
 */

class Modal {
    constructor(options = {}) {
        this.title = options.title || '';
        this.content = options.content || '';
        this.buttons = options.buttons || [];
        this.onClose = options.onClose || null;
        this.element = null;
    }

    /**
     * 显示模态框
     */
    show() {
        this.element = document.createElement('div');
        this.element.className = 'modal-overlay';
        this.element.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3 class="modal-title">${this.title}</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-content">${this.content}</div>
                ${this.buttons.length ? `
                    <div class="modal-footer">
                        ${this.buttons.map((btn, i) => `
                            <button class="btn ${btn.primary ? 'btn-primary' : 'btn-secondary'}" data-btn-index="${i}">
                                ${btn.text}
                            </button>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;

        document.body.appendChild(this.element);
        this.bindEvents();
        
        // 动画
        requestAnimationFrame(() => {
            this.element.classList.add('modal-visible');
        });
    }

    /**
     * 关闭模态框
     */
    close() {
        if (!this.element) return;
        
        this.element.classList.remove('modal-visible');
        setTimeout(() => {
            if (this.element && this.element.parentNode) {
                this.element.parentNode.removeChild(this.element);
            }
            if (this.onClose) this.onClose();
        }, 200);
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 关闭按钮
        this.element.querySelector('.modal-close').addEventListener('click', () => this.close());
        
        // 点击遮罩关闭
        this.element.addEventListener('click', e => {
            if (e.target === this.element) this.close();
        });
        
        // 按钮点击
        this.element.querySelectorAll('[data-btn-index]').forEach(btn => {
            btn.addEventListener('click', () => {
                const index = parseInt(btn.dataset.btnIndex);
                const buttonConfig = this.buttons[index];
                if (buttonConfig && buttonConfig.onClick) {
                    buttonConfig.onClick(this);
                }
            });
        });
        
        // ESC 关闭
        this._escHandler = e => {
            if (e.key === 'Escape') this.close();
        };
        document.addEventListener('keydown', this._escHandler);
    }

    /**
     * 确认对话框
     */
    static confirm(message, options = {}) {
        return new Promise(resolve => {
            const modal = new Modal({
                title: options.title || '确认',
                content: `<p>${message}</p>`,
                buttons: [
                    { text: '取消', onClick: m => { m.close(); resolve(false); } },
                    { text: options.confirmText || '确定', primary: true, onClick: m => { m.close(); resolve(true); } }
                ]
            });
            modal.show();
        });
    }

    /**
     * 提示对话框
     */
    static alert(message, options = {}) {
        return new Promise(resolve => {
            const modal = new Modal({
                title: options.title || '提示',
                content: `<p>${message}</p>`,
                buttons: [
                    { text: '确定', primary: true, onClick: m => { m.close(); resolve(); } }
                ]
            });
            modal.show();
        });
    }
}

window.Modal = Modal;
