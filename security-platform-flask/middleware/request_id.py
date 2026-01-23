# middleware/request_id.py
# 请求追踪 ID 中间件
# Requirements: 14.4

from flask import Flask, g, request
import uuid


def register_request_id_middleware(app: Flask):
    """注册请求追踪 ID 中间件
    
    Args:
        app: Flask 应用实例
        
    Requirement 14.4: 在响应头中包含请求追踪 ID 以便调试
    """
    
    @app.before_request
    def generate_request_id():
        """在每个请求开始时生成唯一的追踪 ID"""
        # 优先使用客户端传入的追踪 ID
        request_id = request.headers.get('X-Request-ID')
        
        if not request_id:
            request_id = str(uuid.uuid4())
        
        g.request_id = request_id
    
    @app.after_request
    def add_request_id_header(response):
        """在响应头中添加追踪 ID"""
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        return response
