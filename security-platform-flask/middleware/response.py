# middleware/response.py
# 统一 API 响应格式
# Requirements: 14.1, 14.2, 14.3

from flask import jsonify, g
from typing import Any, Optional, List


def api_response(data: Any = None, message: str = None, status_code: int = 200):
    """统一成功响应格式
    
    Args:
        data: 响应数据
        message: 响应消息
        status_code: HTTP 状态码
        
    Returns:
        Flask Response 对象
        
    Requirement 14.1: 定义统一的成功响应格式
    """
    response = {
        'success': True,
        'data': data,
        'message': message
    }
    
    # 添加请求追踪 ID（如果存在）
    if hasattr(g, 'request_id'):
        response['request_id'] = g.request_id
    
    return jsonify(response), status_code


def paginated_response(
    items: List[Any],
    total: int,
    page: int,
    page_size: int,
    message: str = None
):
    """分页响应格式
    
    Args:
        items: 数据列表
        total: 总数
        page: 当前页码
        page_size: 每页条数
        message: 响应消息
        
    Returns:
        Flask Response 对象
        
    Requirement 14.3: 为所有列表 API 返回分页信息
    """
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    return api_response({
        'items': items,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1
    }, message)


def error_response(
    code: str,
    message: str,
    status_code: int = 400,
    details: Any = None
):
    """统一错误响应格式
    
    Args:
        code: 错误代码
        message: 错误消息
        status_code: HTTP 状态码
        details: 错误详情（如验证错误的字段信息）
        
    Returns:
        Flask Response 对象
        
    Requirement 14.2: 定义统一的错误响应格式
    """
    error = {
        'code': code,
        'message': message
    }
    
    if details is not None:
        error['details'] = details
    
    response = {
        'success': False,
        'error': error
    }
    
    # 添加请求追踪 ID（如果存在）
    if hasattr(g, 'request_id'):
        response['request_id'] = g.request_id
    
    return jsonify(response), status_code


# 常用错误响应快捷方法
def bad_request(message: str = '请求参数错误', details: Any = None):
    """400 Bad Request"""
    return error_response('BAD_REQUEST', message, 400, details)


def unauthorized(message: str = '请先登录'):
    """401 Unauthorized"""
    return error_response('UNAUTHORIZED', message, 401)


def forbidden(message: str = '权限不足'):
    """403 Forbidden"""
    return error_response('FORBIDDEN', message, 403)


def not_found(message: str = '资源不存在'):
    """404 Not Found"""
    return error_response('NOT_FOUND', message, 404)


def conflict(message: str = '资源冲突'):
    """409 Conflict"""
    return error_response('CONFLICT', message, 409)


def internal_error(message: str = '服务器内部错误'):
    """500 Internal Server Error"""
    return error_response('INTERNAL_ERROR', message, 500)


def validation_error(message: str = '数据验证失败', details: Any = None):
    """422 Validation Error"""
    return error_response('VALIDATION_ERROR', message, 422, details)
