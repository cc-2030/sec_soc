"""Flask web application for Personal Workbench."""
from flask import Flask, render_template, request, redirect, url_for, Response, send_file
from datetime import datetime
import requests
import os
import hashlib
import io

from src.storage.storage import Storage
from src.managers.task_manager import TaskManager
from src.managers.link_manager import LinkManager
from src.managers.statistics_module import StatisticsModule
from src.models.task import TaskStatus, TaskPriority

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.after_request
def add_no_cache_headers(response):
    """禁用浏览器缓存，确保模板更新立即生效"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

storage = Storage("workbench_data.json")
task_manager = TaskManager(storage)
link_manager = LinkManager(storage)
statistics_module = StatisticsModule(task_manager)

PRIORITY_LABELS = {'urgent': '紧急', 'high': '高', 'medium': '中', 'low': '低'}
STATUS_LABELS = {'all': '全部', 'new': '新建', 'completed': '已完成', 'overdue': '超时', 'ignored': '已忽略'}


@app.route('/')
def index():
    """首页 - 简约风格"""
    from datetime import date
    stats = statistics_module.get_statistics_summary()
    links = link_manager.get_all_links()
    
    # 获取今日任务
    today_str = date.today().strftime('%Y-%m-%d')
    all_tasks = task_manager.get_all_tasks()
    today_tasks = []
    for t in all_tasks:
        is_today = False
        if t.due_date and t.due_date.strftime('%Y-%m-%d') == today_str:
            is_today = True
        if t.created_at.strftime('%Y-%m-%d') == today_str:
            is_today = True
        if is_today and t not in today_tasks:
            today_tasks.append(t)
    
    return render_template('index.html', stats=stats, links=links,
                          today_tasks=today_tasks,
                          links_grouped=link_manager.get_links_grouped_by_category(),
                          categories=link_manager.get_categories(),
                          all_tags=link_manager.get_all_tags(),
                          active_page='home')


@app.route('/search')
def search():
    """快速搜索 - 搜索链接和任务"""
    q = request.args.get('q', '').strip()
    if not q:
        return {'links': [], 'tasks': []}
    
    q_lower = q.lower()
    
    # 搜索链接
    all_links = link_manager.get_all_links()
    matched_links = [
        {'id': l.id, 'name': l.name, 'url': l.url, 'icon': l.icon or l.name[0], 'category': l.category}
        for l in all_links 
        if q_lower in l.name.lower() or q_lower in l.url.lower() or any(q_lower in t.lower() for t in l.tags)
    ][:5]
    
    # 搜索任务
    all_tasks = task_manager.get_all_tasks()
    matched_tasks = [
        {'id': t.id, 'title': t.title, 'status': t.status.value, 'category': t.category}
        for t in all_tasks
        if q_lower in t.title.lower() or q_lower in t.description.lower()
    ][:5]
    
    return {'links': matched_links, 'tasks': matched_tasks}


@app.route('/links')
def links_page():
    """快捷链接页面"""
    category_filter = request.args.get('category', '')
    tag_filter = request.args.get('tag', '')
    
    if tag_filter:
        links = link_manager.get_links_by_tag(tag_filter)
    elif category_filter:
        links = link_manager.get_links_by_category(category_filter)
    else:
        links = link_manager.get_all_links()
    
    links_grouped = link_manager.get_links_grouped_by_category()
    categories = link_manager.get_categories()
    all_tags = link_manager.get_all_tags()
    
    return render_template('links.html', links=links, links_grouped=links_grouped,
                          categories=categories, all_tags=all_tags,
                          category_filter=category_filter, tag_filter=tag_filter,
                          active_page='links')


@app.route('/tasks')
def tasks_page():
    """任务管理页面"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 15, type=int)
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    priority_filter = request.args.get('priority', '')
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'created_at')
    sort_order = request.args.get('order', 'desc')
    
    status = TaskStatus(status_filter) if status_filter else None
    priority = TaskPriority(priority_filter) if priority_filter else None
    
    tasks, total, total_pages = task_manager.get_tasks_paginated(
        page=page, per_page=per_page, status=status, category=category_filter or None,
        priority=priority, search=search, sort_by=sort_by, sort_order=sort_order
    )
    
    stats = statistics_module.get_statistics_summary()
    categories = task_manager.get_categories()
    
    return render_template('tasks.html', tasks=tasks, stats=stats, categories=categories,
                          page=page, per_page=per_page, total=total, total_pages=total_pages,
                          status_filter=status_filter, category_filter=category_filter,
                          priority_filter=priority_filter, search=search,
                          sort_by=sort_by, sort_order=sort_order,
                          priority_labels=PRIORITY_LABELS, status_labels=STATUS_LABELS,
                          active_page='tasks')


@app.route('/calendar')
def calendar_page():
    """日历视图页面"""
    import calendar
    from datetime import date, timedelta
    
    # 获取年月参数
    today = date.today()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)
    
    # 处理月份越界
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1
    
    # 获取该月的日历数据
    cal = calendar.Calendar(firstweekday=6)  # 周日开始
    month_days = cal.monthdayscalendar(year, month)
    
    # 获取所有任务
    all_tasks = task_manager.get_all_tasks()
    
    # 按日期分组任务（优先使用截止日期，没有则使用创建日期）
    tasks_by_date = {}
    added_task_ids = set()  # 避免重复添加
    
    for task in all_tasks:
        # 优先按截止日期分组
        if task.due_date:
            date_key = task.due_date.strftime('%Y-%m-%d')
            if date_key not in tasks_by_date:
                tasks_by_date[date_key] = []
            tasks_by_date[date_key].append(task)
            added_task_ids.add((task.id, date_key))
    
    # 再按创建日期分组（没有截止日期的任务，或者截止日期不同于创建日期的也显示在创建日期）
    for task in all_tasks:
        created_date_key = task.created_at.strftime('%Y-%m-%d')
        # 如果任务没有截止日期，或者截止日期与创建日期不同，则在创建日期也显示
        if (task.id, created_date_key) not in added_task_ids:
            if created_date_key not in tasks_by_date:
                tasks_by_date[created_date_key] = []
            tasks_by_date[created_date_key].append(task)
    
    # 月份名称
    month_names = ['', '一月', '二月', '三月', '四月', '五月', '六月', 
                   '七月', '八月', '九月', '十月', '十一月', '十二月']
    
    stats = statistics_module.get_statistics_summary()
    
    return render_template('calendar.html',
                          year=year, month=month,
                          month_name=month_names[month],
                          month_days=month_days,
                          tasks_by_date=tasks_by_date,
                          today=today,
                          stats=stats,
                          priority_labels=PRIORITY_LABELS,
                          status_labels=STATUS_LABELS,
                          active_page='calendar')


# Task routes
@app.route('/task/add', methods=['POST'])
def add_task():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    due_date_str = request.form.get('due_date', '').strip()
    category = request.form.get('category', '').strip()
    priority = request.form.get('priority', 'medium')
    
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        except ValueError:
            pass
    
    try:
        task_manager.create_task(title, description, due_date, category, priority)
    except ValueError:
        pass
    
    return redirect(request.referrer or url_for('tasks_page'))


@app.route('/task/complete/<task_id>', methods=['POST'])
def complete_task(task_id):
    try:
        task_manager.complete_task(task_id)
    except KeyError:
        pass
    return redirect(request.referrer or url_for('tasks_page'))


@app.route('/task/ignore/<task_id>', methods=['POST'])
def ignore_task(task_id):
    reason = request.form.get('reason', '').strip()
    try:
        task_manager.ignore_task(task_id, reason)
    except KeyError:
        pass
    return redirect(request.referrer or url_for('tasks_page'))


# Link routes
@app.route('/link/add', methods=['POST'])
def add_link():
    name = request.form.get('name', '').strip()
    url = request.form.get('url', '').strip()
    category = request.form.get('category', '').strip()
    tags = request.form.get('tags', '').strip()
    icon = request.form.get('icon', '').strip()
    
    try:
        link_manager.add_link(name, url, category, tags, icon)
    except ValueError:
        pass
    
    return redirect(request.referrer or url_for('links_page'))


@app.route('/link/delete/<link_id>', methods=['POST'])
def delete_link(link_id):
    try:
        link_manager.delete_link(link_id)
    except KeyError:
        pass
    return redirect(request.referrer or url_for('links_page'))


# Favicon 缓存目录
FAVICON_CACHE_DIR = os.path.join(os.path.dirname(__file__), '.favicon_cache')
os.makedirs(FAVICON_CACHE_DIR, exist_ok=True)


@app.route('/favicon/<path:domain>')
def favicon_proxy(domain):
    """代理获取网站 favicon，带本地缓存"""
    # 检查缓存
    cache_key = hashlib.md5(domain.encode()).hexdigest()
    cache_path = os.path.join(FAVICON_CACHE_DIR, cache_key)
    
    if os.path.exists(cache_path):
        return send_file(cache_path, mimetype='image/png')
    
    # 多个 favicon 源，按优先级尝试
    sources = [
        f'https://{domain}/favicon.ico',
        f'https://favicon.im/{domain}',
        f'https://api.iowen.cn/favicon/{domain}.png',
        f'https://www.google.com/s2/favicons?domain={domain}&sz=32',
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for src in sources:
        try:
            resp = requests.get(src, headers=headers, timeout=5, allow_redirects=True)
            ct = resp.headers.get('content-type', '')
            if resp.status_code == 200 and len(resp.content) > 100 and ('image' in ct or 'icon' in ct or 'octet' in ct):
                # 缓存到本地
                with open(cache_path, 'wb') as f:
                    f.write(resp.content)
                return Response(resp.content, mimetype=ct.split(';')[0] if ct else 'image/x-icon')
        except Exception:
            continue
    
    # 全部失败，返回 1x1 透明 PNG 触发前端 fallback
    transparent_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    return Response(transparent_png, mimetype='image/png', status=404)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
