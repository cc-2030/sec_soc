# routes/auth.py
# 认证路由
# Requirements: 1.1, 1.2, 1.3, 1.4, 2.3, 3.4, 3.5

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from services.auth_service import AuthService
from services.audit_service import AuditService, audit_action
from middleware.rbac import require_role

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面和处理
    
    GET: 显示登录页面
    POST: 处理登录请求
    
    Requirement 1.1: THE Authentication_System SHALL 要求用户登录后才能访问系统
    Requirement 1.2: THE Authentication_System SHALL 验证用户凭据
    """
    # 如果用户已登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False) == 'on'
        
        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return render_template('auth/login.html')
        
        user = AuthService.authenticate(username, password)
        
        if user:
            login_user(user, remember=remember)
            # 记录登录审计日志
            AuditService.log(
                action_type='login',
                resource_type='auth',
                user_id=user.id,
                username=user.username,
                details={'remember': remember}
            )
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            # 记录登录失败审计日志
            AuditService.log(
                action_type='login_failed',
                resource_type='auth',
                details={'username': username}
            )
            flash('用户名或密码错误', 'error')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """登出
    
    Requirement 1.4: THE Authentication_System SHALL 支持用户登出
    Requirement 3.3: THE Audit_Logger SHALL 记录认证事件
    """
    # 记录登出审计日志
    AuditService.log(
        action_type='logout',
        resource_type='auth',
        user_id=current_user.id,
        username=current_user.username
    )
    logout_user()
    flash('您已成功登出', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/api/auth/me')
@login_required
def get_current_user():
    """获取当前登录用户信息
    ---
    tags:
      - 认证
    responses:
      200:
        description: 当前用户信息
        schema:
          type: object
          properties:
            id:
              type: string
              description: 用户ID
            username:
              type: string
              description: 用户名
            email:
              type: string
              description: 邮箱
            roles:
              type: array
              items:
                type: string
              description: 角色列表
            is_active:
              type: boolean
              description: 是否激活
            last_login:
              type: string
              description: 最后登录时间
      401:
        description: 未登录
    """
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'roles': [role.name for role in current_user.roles],
        'is_active': current_user.is_active,
        'last_login': current_user.last_login.isoformat() if current_user.last_login else None
    })



# ==================== 用户管理 API ====================
# Requirement 2.3: THE RBAC_System SHALL 支持管理员管理用户角色

@auth_bp.route('/api/users', methods=['GET'])
@require_role('admin')
def list_users():
    """获取用户列表
    ---
    tags:
      - 用户管理
    responses:
      200:
        description: 用户列表
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
              username:
                type: string
              email:
                type: string
              roles:
                type: array
                items:
                  type: string
              is_active:
                type: boolean
              created_at:
                type: string
              last_login:
                type: string
      401:
        description: 未登录
      403:
        description: 权限不足（需要管理员权限）
    """
    from models import User
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'roles': [r.name for r in u.roles],
        'is_active': u.is_active,
        'created_at': u.created_at.isoformat() if u.created_at else None,
        'last_login': u.last_login.isoformat() if u.last_login else None
    } for u in users])


@auth_bp.route('/api/users', methods=['POST'])
@require_role('admin')
@audit_action('create', 'user')
def create_user():
    """创建用户（仅管理员）"""
    data = request.json
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    role_names = data.get('roles', ['viewer'])
    
    if not username or not email or not password:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': '用户名、邮箱和密码不能为空'}
        }), 400
    
    try:
        user = AuthService.create_user(username, email, password, role_names)
        return jsonify({
            'success': True,
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'roles': [r.name for r in user.roles]
            }
        }), 201
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}
        }), 400


@auth_bp.route('/api/users/<user_id>', methods=['PATCH'])
@require_role('admin')
@audit_action('update', 'user')
def update_user(user_id):
    """更新用户（仅管理员）"""
    from models import User, Role
    from extensions import db
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'success': False,
            'error': {'code': 'NOT_FOUND', 'message': '用户不存在'}
        }), 404
    
    data = request.json
    
    # 更新角色
    if 'roles' in data:
        user.roles.clear()
        for role_name in data['roles']:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                user.roles.append(role)
    
    # 更新激活状态
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'roles': [r.name for r in user.roles],
            'is_active': user.is_active
        }
    })


@auth_bp.route('/api/users/<user_id>', methods=['DELETE'])
@require_role('admin')
@audit_action('delete', 'user')
def delete_user(user_id):
    """删除用户（仅管理员）"""
    from models import User
    from extensions import db
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'success': False,
            'error': {'code': 'NOT_FOUND', 'message': '用户不存在'}
        }), 404
    
    # 不允许删除自己
    if user.id == current_user.id:
        return jsonify({
            'success': False,
            'error': {'code': 'FORBIDDEN', 'message': '不能删除自己的账户'}
        }), 403
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '用户已删除'})


@auth_bp.route('/api/roles', methods=['GET'])
@require_role('admin')
def list_roles():
    """获取角色列表（仅管理员）"""
    from models import Role
    roles = Role.query.all()
    return jsonify([{
        'id': r.id,
        'name': r.name,
        'description': r.description,
        'permissions': r.permissions
    } for r in roles])


# ==================== 审计日志 API ====================
# Requirement 3.4: THE Audit_Logger SHALL 提供审计日志查询 API
# Requirement 3.5: THE Audit_Logger SHALL 确保审计日志不可被普通用户修改或删除

@auth_bp.route('/api/audit-logs', methods=['GET'])
@require_role('admin')
def get_audit_logs():
    """查询审计日志（仅管理员）
    
    支持的查询参数：
    - start_time: 开始时间 (ISO 格式)
    - end_time: 结束时间 (ISO 格式)
    - user_id: 用户 ID
    - action_type: 操作类型 (create, update, delete, login, logout, login_failed)
    - resource_type: 资源类型 (asset, vulnerability, incident, user, auth, etc.)
    - page: 页码（默认 1）
    - page_size: 每页条数（默认 50，最大 100）
    
    Requirement 3.4: 提供按时间范围、用户、操作类型查询审计日志的 API
    """
    from datetime import datetime
    
    # 解析查询参数
    start_time = None
    end_time = None
    
    if request.args.get('start_time'):
        try:
            start_time = datetime.fromisoformat(request.args.get('start_time').replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'success': False,
                'error': {'code': 'VALIDATION_ERROR', 'message': 'start_time 格式无效'}
            }), 400
    
    if request.args.get('end_time'):
        try:
            end_time = datetime.fromisoformat(request.args.get('end_time').replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'success': False,
                'error': {'code': 'VALIDATION_ERROR', 'message': 'end_time 格式无效'}
            }), 400
    
    user_id = request.args.get('user_id')
    action_type = request.args.get('action_type')
    resource_type = request.args.get('resource_type')
    
    try:
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 50)), 100)
    except ValueError:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': 'page 和 page_size 必须是整数'}
        }), 400
    
    # 查询审计日志
    result = AuditService.query(
        start_time=start_time,
        end_time=end_time,
        user_id=user_id,
        action_type=action_type,
        resource_type=resource_type,
        page=page,
        page_size=page_size
    )
    
    return jsonify({
        'success': True,
        'data': result
    })


@auth_bp.route('/api/audit-logs/stats', methods=['GET'])
@require_role('admin')
def get_audit_stats():
    """获取审计日志统计信息（仅管理员）"""
    from models import AuditLog
    from sqlalchemy import func
    from datetime import datetime, timedelta, timezone
    
    # 最近 24 小时的统计
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    
    # 按操作类型统计
    action_stats = db.session.query(
        AuditLog.action_type,
        func.count(AuditLog.id)
    ).filter(
        AuditLog.timestamp >= since
    ).group_by(AuditLog.action_type).all()
    
    # 按资源类型统计
    resource_stats = db.session.query(
        AuditLog.resource_type,
        func.count(AuditLog.id)
    ).filter(
        AuditLog.timestamp >= since
    ).group_by(AuditLog.resource_type).all()
    
    # 总数
    total_24h = AuditLog.query.filter(AuditLog.timestamp >= since).count()
    total_all = AuditLog.query.count()
    
    return jsonify({
        'success': True,
        'data': {
            'total_24h': total_24h,
            'total_all': total_all,
            'by_action': {action: count for action, count in action_stats},
            'by_resource': {resource: count for resource, count in resource_stats if resource}
        }
    })
