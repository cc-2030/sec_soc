/**
 * 数据表格组件
 * Requirement 12.1, 12.2: 创建数据表格组件
 */

class DataTable {
    constructor(container, options = {}) {
        this.container = typeof container === 'string' 
            ? document.querySelector(container) 
            : container;
        
        this.columns = options.columns || [];
        this.data = options.data || [];
        this.page = 1;
        this.pageSize = options.pageSize || 10;
        this.total = options.total || 0;
        this.sortColumn = null;
        this.sortDirection = 'asc';
        this.searchText = '';
        this.onPageChange = options.onPageChange || null;
        this.onSort = options.onSort || null;
        
        this.render();
    }

    /**
     * 设置数据
     */
    setData(data, total = null) {
        this.data = data;
        this.total = total !== null ? total : data.length;
        this.render();
    }

    /**
     * 渲染表格
     */
    render() {
        const filteredData = this.filterData();
        const sortedData = this.sortData(filteredData);
        
        this.container.innerHTML = `
            <div class="data-table-wrapper">
                <div class="data-table-toolbar">
                    <input type="text" class="data-table-search" placeholder="搜索..." value="${this.searchText}">
                </div>
                <table class="table data-table">
                    <thead>
                        <tr>
                            ${this.columns.map(col => `
                                <th class="${col.sortable ? 'sortable' : ''}" data-field="${col.field}">
                                    ${col.title}
                                    ${col.sortable ? `<span class="sort-icon">${this.getSortIcon(col.field)}</span>` : ''}
                                </th>
                            `).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${sortedData.length ? sortedData.map(row => `
                            <tr>
                                ${this.columns.map(col => `
                                    <td>${col.render ? col.render(row[col.field], row) : (row[col.field] ?? '-')}</td>
                                `).join('')}
                            </tr>
                        `).join('') : `<tr><td colspan="${this.columns.length}" class="text-center">暂无数据</td></tr>`}
                    </tbody>
                </table>
                ${this.renderPagination()}
            </div>
        `;

        this.bindEvents();
    }

    /**
     * 渲染分页
     */
    renderPagination() {
        const totalPages = Math.ceil(this.total / this.pageSize);
        if (totalPages <= 1) return '';

        return `
            <div class="data-table-pagination">
                <span class="pagination-info">共 ${this.total} 条，第 ${this.page}/${totalPages} 页</span>
                <div class="pagination-buttons">
                    <button class="btn btn-secondary btn-sm" ${this.page <= 1 ? 'disabled' : ''} data-page="prev">上一页</button>
                    <button class="btn btn-secondary btn-sm" ${this.page >= totalPages ? 'disabled' : ''} data-page="next">下一页</button>
                </div>
            </div>
        `;
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 搜索
        const searchInput = this.container.querySelector('.data-table-search');
        if (searchInput) {
            searchInput.addEventListener('input', Utils.debounce(e => {
                this.searchText = e.target.value;
                this.page = 1;
                this.render();
            }, 300));
        }

        // 排序
        this.container.querySelectorAll('th.sortable').forEach(th => {
            th.addEventListener('click', () => {
                const field = th.dataset.field;
                if (this.sortColumn === field) {
                    this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
                } else {
                    this.sortColumn = field;
                    this.sortDirection = 'asc';
                }
                if (this.onSort) {
                    this.onSort(this.sortColumn, this.sortDirection);
                } else {
                    this.render();
                }
            });
        });

        // 分页
        this.container.querySelectorAll('[data-page]').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.page;
                if (action === 'prev' && this.page > 1) {
                    this.page--;
                } else if (action === 'next') {
                    this.page++;
                }
                if (this.onPageChange) {
                    this.onPageChange(this.page, this.pageSize);
                } else {
                    this.render();
                }
            });
        });
    }

    /**
     * 过滤数据
     */
    filterData() {
        if (!this.searchText) return this.data;
        
        const search = this.searchText.toLowerCase();
        return this.data.filter(row => {
            return this.columns.some(col => {
                const value = row[col.field];
                return value && String(value).toLowerCase().includes(search);
            });
        });
    }

    /**
     * 排序数据
     */
    sortData(data) {
        if (!this.sortColumn) return data;
        
        return [...data].sort((a, b) => {
            const aVal = a[this.sortColumn];
            const bVal = b[this.sortColumn];
            
            if (aVal === bVal) return 0;
            if (aVal === null || aVal === undefined) return 1;
            if (bVal === null || bVal === undefined) return -1;
            
            const result = aVal < bVal ? -1 : 1;
            return this.sortDirection === 'asc' ? result : -result;
        });
    }

    /**
     * 获取排序图标
     */
    getSortIcon(field) {
        if (this.sortColumn !== field) return '↕';
        return this.sortDirection === 'asc' ? '↑' : '↓';
    }
}

window.DataTable = DataTable;
