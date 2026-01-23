# middleware/rbac.py
# RBAC 权限控制中间件
# Requirements: 2.1, 2.2, 2.4

from functools import wraps
from flask import jsonify, abort
from flask_login import current_user


# 角色定义及其权限
# Requirement 2.1: THE RBAC_System SHALL 定义三种角色：admin, analyst, viewer
ROLES = {
    'admin': {
        'description': '系统管理员，拥有所有权限',
        'permissions': ['*']  # 通配符表示所有权限
    },
    'analyst': {
        'description': '安全分析师，可查看和编辑安全数据',
        'permissions': [
            'assets:read', 'assets:write',
            'vulnerabilities:read', 'vulnerabilities:write',
            'incidents:read', 'incidents:write',
            'threat_intel:read', 'threat_intel:write',
            'compliance:read',
            'reports:read', 'reports:generate',
            'ai:analyze'
        ]
    },
    'viewer': {
        'description': '只读用户，只能查看数据',
        'permissions': [
            'assets:read',
            'vulnerabilities:read',
            'incidents:read',
            'threat_intel:read',
            'compliance:read',
            'reports:read'
        ]
    }
}


def require_role(*roles):
    """要求用户具有指定角色之一
    
    Args:
        *roles: 允许访问的角色名称列表
        
    Returns:
        装饰器函数
        
    Requirement 2.2: THE RBAC_System SHALL 根据用户角色限制功能访问
    
    Usage:
        @require_role('admin')
        def admin_only_view():
            ...
            
        @require_role('admin', 'analyst')
        def admin_or_analyst_view():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'UNAUTHORIZED',
                        'message': '请先登录'
                    }
                }), 401
            
            if not current_user.has_any_role(list(roles)):
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'FORBIDDEN',
                        'message': '您没有权限执行此操作'
                    }
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_permission(permission):
    """要求用户具有指定权限
    
    Args:
        permission: 权限名称，格式为 'resource:action'
                   例如 'assets:read', 'vulnerabilities:write'
        
    Returns:
        装饰器函数
        
    Requirement 2.4: THE RBAC_System SHALL 支持细粒度权限控制
    
    Usage:
        @require_permission('assets:write')
        def create_asset():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'UNAUTHORIZED',
                        'message': '请先登录'
                    }
                }), 401
            
            if not current_user.has_permission(permission):
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'FORBIDDEN',
                        'message': f'您没有 {permission} 权限'
                    }
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def api_login_required(f):
    """API 端点的登录验证装饰器
    
    与 @login_required 类似，但返回 JSON 格式的错误响应
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': '请先登录'
                }
            }), 401
        return f(*args, **kwargs)
    return decorated_function
