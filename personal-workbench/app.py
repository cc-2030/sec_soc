"""Flask web application for Personal Workbench."""
from flask import Flask, render_template, request, redirect, url_for, Response, send_file, session, flash
from datetime import datetime
import requests
import os
import hashlib
import io

from src.storage.storage import Storage
from src.managers.task_manager import TaskManager
from src.managers.link_manager import LinkManager
from src.managers.statistics_module import StatisticsModule
from src.managers.user_manager import UserManager
from src.models.task import TaskStatus, TaskPriority

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = 'personal_workbench_secret_key'  # 用于session加密


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
user_manager = UserManager(storage)
statistics_module = StatisticsModule(task_manager)

# 初始化默认管理员账号
def init_admin():
    """初始化默认管理员账号"""
    # 检查是否已有管理员账号
    users = user_manager.get_all_users()
    admin_exists = any(user.is_admin for user in users)
    
    if not admin_exists:
        # 创建默认管理员账号
        try:
            user_manager.create_admin_user(
                username="admin",
                email="admin@example.com",
                password="admin123",
                phone_number="13800138000"
            )
            print("默认管理员账号创建成功: 用户名=admin, 密码=admin123")
        except ValueError as e:
            print(f"创建管理员账号失败: {e}")

# 初始化管理员账号
init_admin()

# 上下文处理器：自动将current_user传递到所有模板
@app.context_processor
def inject_current_user():
    """Inject current user into all templates."""
    return dict(current_user=get_current_user())

PRIORITY_LABELS = {'urgent': '紧急', 'high': '高', 'medium': '中', 'low': '低'}
STATUS_LABELS = {'all': '全部', 'new': '新建', 'completed': '已完成', 'overdue': '超时', 'ignored': '已忽略'}

# 辅助函数
def get_current_user():
    """Get current logged-in user."""
    user_id = session.get('user_id')
    if user_id:
        return user_manager.get_user_by_id(user_id)
    return None

def require_login():
    """Check if user is logged in, redirect to login if not."""
    if not get_current_user():
        return redirect(url_for('login'))
    return None


@app.route('/')
def index():
    """首页 - 简约风格"""
    # 检查登录状态
    login_required = require_login()
    if login_required:
        return login_required
    
    current_user = get_current_user()
    from datetime import date
    stats = statistics_module.get_statistics_summary(user_id=current_user.id)
    links = link_manager.get_all_links(user_id=current_user.id)
    
    # 获取今日任务
    today_str = date.today().strftime('%Y-%m-%d')
    all_tasks = task_manager.get_all_tasks(user_id=current_user.id)
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
                          links_grouped=link_manager.get_links_grouped_by_category(user_id=current_user.id),
                          categories=link_manager.get_categories(user_id=current_user.id),
                          all_tags=link_manager.get_all_tags(user_id=current_user.id),
                          active_page='home',
                          current_user=current_user)


@app.route('/search')
def search():
    """快速搜索 - 搜索链接和任务"""
    # 检查登录状态
    login_required = require_login()
    if login_required:
        return login_required
    
    current_user = get_current_user()
    q = request.args.get('q', '').strip()
    if not q:
        return {'links': [], 'tasks': []}
    
    q_lower = q.lower()
    
    # 搜索链接
    all_links = link_manager.get_all_links(user_id=current_user.id)
    matched_links = [
        {'id': l.id, 'name': l.name, 'url': l.url, 'icon': l.icon or l.name[0], 'category': l.category}
        for l in all_links 
        if q_lower in l.name.lower() or q_lower in l.url.lower() or any(q_lower in t.lower() for t in l.tags)
    ][:5]
    
    # 搜索任务
    all_tasks = task_manager.get_all_tasks(user_id=current_user.id)
    matched_tasks = [
        {'id': t.id, 'title': t.title, 'status': t.status.value, 'category': t.category}
        for t in all_tasks
        if q_lower in t.title.lower() or q_lower in t.description.lower()
    ][:5]
    
    return {'links': matched_links, 'tasks': matched_tasks}


@app.route('/links')
def links_page():
    """快捷链接页面"""
    # 检查登录状态
    login_required = require_login()
    if login_required:
        return login_required
    
    current_user = get_current_user()
    category_filter = request.args.get('category', '')
    tag_filter = request.args.get('tag', '')
    
    if tag_filter:
        links = link_manager.get_links_by_tag(tag_filter, user_id=current_user.id)
    elif category_filter:
        links = link_manager.get_links_by_category(category_filter, user_id=current_user.id)
    else:
        links = link_manager.get_all_links(user_id=current_user.id)
    
    links_grouped = link_manager.get_links_grouped_by_category(user_id=current_user.id)
    categories = link_manager.get_categories(user_id=current_user.id)
    all_tags = link_manager.get_all_tags(user_id=current_user.id)
    
    return render_template('links.html', links=links, links_grouped=links_grouped,
                          categories=categories, all_tags=all_tags,
                          category_filter=category_filter, tag_filter=tag_filter,
                          active_page='links',
                          current_user=current_user)


@app.route('/tasks')
def tasks_page():
    """任务管理页面"""
    # 检查登录状态
    login_required = require_login()
    if login_required:
        return login_required
    
    current_user = get_current_user()
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
        priority=priority, search=search, sort_by=sort_by, sort_order=sort_order,
        user_id=current_user.id
    )
    
    stats = statistics_module.get_statistics_summary(user_id=current_user.id)
    categories = task_manager.get_categories(user_id=current_user.id)
    
    return render_template('tasks.html', tasks=tasks, stats=stats, categories=categories,
                          page=page, per_page=per_page, total=total, total_pages=total_pages,
                          status_filter=status_filter, category_filter=category_filter,
                          priority_filter=priority_filter, search=search,
                          sort_by=sort_by, sort_order=sort_order,
                          priority_labels=PRIORITY_LABELS, status_labels=STATUS_LABELS,
                          active_page='tasks',
                          current_user=current_user)


@app.route('/calendar')
def calendar_page():
    """日历视图页面"""
    # 检查登录状态
    login_required = require_login()
    if login_required:
        return login_required
    
    current_user = get_current_user()
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
    all_tasks = task_manager.get_all_tasks(user_id=current_user.id)
    
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
    
    stats = statistics_module.get_statistics_summary(user_id=current_user.id)
    
    return render_template('calendar.html',
                          year=year, month=month,
                          month_name=month_names[month],
                          month_days=month_days,
                          tasks_by_date=tasks_by_date,
                          today=today,
                          stats=stats,
                          priority_labels=PRIORITY_LABELS,
                          status_labels=STATUS_LABELS,
                          active_page='calendar',
                          current_user=current_user)


# Task routes
@app.route('/task/add', methods=['POST'])
def add_task():
    # 检查登录状态
    login_required = require_login()
    if login_required:
        return login_required
    
    current_user = get_current_user()
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
        task_manager.create_task(title, description, due_date, category, priority, user_id=current_user.id)
    except ValueError:
        pass
    
    return redirect(request.referrer or url_for('tasks_page'))


@app.route('/task/complete/<task_id>', methods=['POST'])
def complete_task(task_id):
    # 检查登录状态
    login_required = require_login()
    if login_required:
        return login_required
    
    try:
        task_manager.complete_task(task_id)
    except KeyError:
        pass
    return redirect(request.referrer or url_for('tasks_page'))


@app.route('/task/ignore/<task_id>', methods=['POST'])
def ignore_task(task_id):
    # 检查登录状态
    login_required = require_login()
    if login_required:
        return login_required
    
    reason = request.form.get('reason', '').strip()
    try:
        task_manager.ignore_task(task_id, reason)
    except KeyError:
        pass
    return redirect(request.referrer or url_for('tasks_page'))


# Link routes
@app.route('/link/add', methods=['POST'])
def add_link():
    # 检查登录状态
    login_required = require_login()
    if login_required:
        return login_required
    
    current_user = get_current_user()
    name = request.form.get('name', '').strip()
    url = request.form.get('url', '').strip()
    category = request.form.get('category', '').strip()
    tags = request.form.get('tags', '').strip()
    icon = request.form.get('icon', '').strip()
    
    try:
        link_manager.add_link(name, url, category, tags, icon, user_id=current_user.id)
    except ValueError:
        pass
    
    return redirect(request.referrer or url_for('links_page'))


@app.route('/link/delete/<link_id>', methods=['POST'])
def delete_link(link_id):
    # 检查登录状态
    login_required = require_login()
    if login_required:
        return login_required
    
    try:
        link_manager.delete_link(link_id)
    except KeyError:
        pass
    
    return redirect(request.referrer or url_for('links_page'))

@app.route('/link/edit', methods=['POST'])
def edit_link():
    # 检查登录状态
    login_required = require_login()
    if login_required:
        return login_required
    
    link_id = request.form.get('id', '').strip()
    name = request.form.get('name', '').strip()
    url = request.form.get('url', '').strip()
    category = request.form.get('category', '').strip()
    tags = request.form.get('tags', '').strip()
    icon = request.form.get('icon', '').strip()
    
    try:
        link_manager.update_link(
            link_id=link_id,
            name=name,
            url=url,
            category=category,
            tags=tags,
            icon=icon
        )
    except (KeyError, ValueError):
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


# 用户认证路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    # 如果已登录，直接跳转到首页
    if get_current_user():
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # 检查是手机号登录还是账号密码登录
        if 'phone' in request.form:
            # 手机号验证码登录
            phone = request.form.get('phone', '').strip()
            code = request.form.get('code', '').strip()
            
            # 验证用户
            user = user_manager.authenticate_user_by_phone(phone, code)
            if user:
                # 设置登录状态
                session['user_id'] = user.id
                session['username'] = user.username
                flash('登录成功！', 'success')
                return redirect(url_for('index'))
            else:
                flash('验证码错误或已过期', 'error')
        else:
            # 账号密码登录
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            # 验证用户
            user = user_manager.authenticate_user(username, password)
            if user:
                # 设置登录状态
                session['user_id'] = user.id
                session['username'] = user.username
                flash('登录成功！', 'success')
                return redirect(url_for('index'))
            else:
                flash('用户名或密码错误', 'error')
    
    return render_template('login.html', active_page='login')


@app.route('/send_code', methods=['POST'])
def send_code():
    """发送验证码"""
    phone = request.form.get('phone', '').strip()
    
    # 验证手机号格式（简单验证）
    if not phone or len(phone) != 11 or not phone.isdigit():
        return {'status': 'error', 'message': '请输入正确的手机号'}
    
    try:
        # 生成验证码
        user_manager.generate_verification_code(phone)
        return {'status': 'success', 'message': '验证码已发送，请注意查收'}
    except Exception as e:
        return {'status': 'error', 'message': f'发送失败：{str(e)}'}


@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册页面"""
    # 如果已登录，直接跳转到首页
    if get_current_user():
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # 验证输入
        if not username:
            flash('用户名不能为空', 'error')
        elif not password:
            flash('密码不能为空', 'error')
        elif len(password) < 6:
            flash('密码长度至少6位', 'error')
        elif password != confirm_password:
            flash('两次输入的密码不一致', 'error')
        else:
            try:
                # 创建用户
                user = user_manager.create_user(username, email, password, phone)
                # 自动登录
                session['user_id'] = user.id
                session['username'] = user.username
                flash('注册成功！', 'success')
                return redirect(url_for('index'))
            except ValueError as e:
                flash(str(e), 'error')
    
    return render_template('register.html', active_page='register')


@app.route('/logout')
def logout():
    """注销"""
    # 清除会话
    session.clear()
    flash('已成功注销', 'success')
    return redirect(url_for('login'))


# 管理员路由
@app.route('/admin/users')
def admin_users():
    """管理员用户管理页面"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('无权限访问', 'error')
        return redirect(url_for('index'))
    
    users = user_manager.get_all_users()
    return render_template('admin/users.html', users=users, active_page='admin')


@app.route('/admin/create_admin', methods=['GET', 'POST'])
def create_admin():
    """创建管理员账号"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('无权限访问', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        phone = request.form.get('phone', '').strip()
        
        try:
            user_manager.create_admin_user(username, email, password, phone)
            flash('管理员账号创建成功', 'success')
            return redirect(url_for('admin_users'))
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('admin/create_admin.html', active_page='admin')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
