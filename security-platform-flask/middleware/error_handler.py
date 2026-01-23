# middleware/error_handler.py
# 全局错误处理
# Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6

from flask import Flask, jsonify, g
from werkzeug.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask):
    """注册全局错误处理器
    
    Args:
        app: Flask 应用实例
        
    Requirement 15.1: 实现全局异常处理器捕获所有未处理的异常
    """
    
    @app.errorhandler(400)
    def handle_bad_request(e):
        """处理 400 Bad Request
        
        Requirement 15.2: 验证错误返回 400 状态码
        """
        return _error_response('BAD_REQUEST', str(e.description) if hasattr(e, 'description') else '请求参数错误', 400)
    
    @app.errorhandler(401)
    def handle_unauthorized(e):
        """处理 401 Unauthorized
        
        Requirement 15.3: 认证错误返回 401 状态码
        """
        return _error_response('UNAUTHORIZED', '请先登录', 401)
    
    @app.errorhandler(403)
    def handle_forbidden(e):
        """处理 403 Forbidden
        
        Requirement 15.4: 权限错误返回 403 状态码
        """
        return _error_response('FORBIDDEN', '权限不足', 403)
    
    @app.errorhandler(404)
    def handle_not_found(e):
        """处理 404 Not Found
        
        Requirement 15.5: 资源不存在返回 404 状态码
        """
        return _error_response('NOT_FOUND', '资源不存在', 404)
    
    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        """处理 405 Method Not Allowed"""
        return _error_response('METHOD_NOT_ALLOWED', '请求方法不允许', 405)
    
    @app.errorhandler(422)
    def handle_unprocessable_entity(e):
        """处理 422 Unprocessable Entity"""
        return _error_response('VALIDATION_ERROR', str(e.description) if hasattr(e, 'description') else '数据验证失败', 422)
    
    @app.errorhandler(429)
    def handle_too_many_requests(e):
        """处理 429 Too Many Requests"""
        return _error_response('RATE_LIMITED', '请求过于频繁，请稍后再试', 429)
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        """处理 500 Internal Server Error
        
        Requirement 15.6: 服务器内部错误返回 500 状态码并记录详细错误日志
        """
        logger.error(f'Internal server error: {e}', exc_info=True)
        return _error_response('INTERNAL_ERROR', '服务器内部错误', 500)
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """处理所有未捕获的异常
        
        Requirement 15.1: 实现全局异常处理器
        """
        # 如果是 HTTP 异常，使用其状态码
        if isinstance(e, HTTPException):
            return _error_response(
                'HTTP_ERROR',
                e.description or str(e),
                e.code
            )
        
        # 记录未知异常
        logger.error(f'Unhandled exception: {e}', exc_info=True)
        return _error_response('INTERNAL_ERROR', '服务器内部错误', 500)
    
    # 尝试注册 marshmallow ValidationError 处理器
    try:
        from marshmallow import ValidationError
        
        @app.errorhandler(ValidationError)
        def handle_validation_error(e):
            """处理 marshmallow 验证错误
            
            Requirement 15.2: 验证错误返回 400 状态码和详细的验证错误信息
            """
            return _error_response(
                'VALIDATION_ERROR',
                '数据验证失败',
                400,
                e.messages
            )
    except ImportError:
        pass  # marshmallow 未安装


def _error_response(code: str, message: str, status_code: int, details=None):
    """构建错误响应"""
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
    try:
        if hasattr(g, 'request_id'):
            response['request_id'] = g.request_id
    except RuntimeError:
        pass  # 在应用上下文外
    
    return jsonify(response), status_code
