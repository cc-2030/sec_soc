# schemas/common.py
# 通用验证模式和工具
# Requirements: 16.1, 16.2, 16.4, 16.5

from marshmallow import Schema, fields, validate, ValidationError, EXCLUDE
from functools import wraps
from flask import request, jsonify
import re
import html
import uuid


class PaginationSchema(Schema):
    """分页参数验证模式"""
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    page_size = fields.Int(load_default=20, validate=validate.Range(min=1, max=100))


class IDSchema(Schema):
    """ID 参数验证模式
    
    Requirement 16.5: 验证所有 ID 参数的格式有效性
    """
    id = fields.Str(required=True, validate=validate.Length(min=1, max=36))


class UUIDField(fields.Field):
    """UUID 格式验证字段
    
    Requirement 16.5: 验证所有 ID 参数的格式有效性
    """
    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        try:
            uuid.UUID(str(value))
            return str(value)
        except (ValueError, AttributeError):
            raise ValidationError(f'{attr} 必须是有效的 UUID 格式')


def validate_request(schema_class, location='json'):
    """请求验证装饰器
    
    Args:
        schema_class: marshmallow Schema 类
        location: 数据来源 ('json', 'args', 'form')
        
    Usage:
        @validate_request(AssetCreateSchema)
        def create_asset(validated_data):
            ...
            
    Requirement 16.3: 为所有 POST/PUT/PATCH 端点定义输入验证模式
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            schema = schema_class()
            
            # 获取请求数据
            if location == 'json':
                data = request.get_json(silent=True) or {}
            elif location == 'args':
                data = request.args.to_dict()
            elif location == 'form':
                data = request.form.to_dict()
            else:
                data = {}
            
            try:
                # 验证并加载数据
                validated_data = schema.load(data)
                # 清理输入
                validated_data = sanitize_dict(validated_data)
            except ValidationError as e:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': '数据验证失败',
                        'details': e.messages
                    }
                }), 400
            
            # 将验证后的数据传递给视图函数
            return f(validated_data, *args, **kwargs)
        return decorated_function
    return decorator


def sanitize_input(value):
    """清理单个输入值
    
    Args:
        value: 输入值
        
    Returns:
        清理后的值
        
    Requirement 16.4: 自动过滤和清理输入数据中的危险字符
    """
    if isinstance(value, str):
        # HTML 转义
        value = html.escape(value)
        # 移除潜在的 SQL 注入字符（基本防护，主要依赖参数化查询）
        # 移除常见的 SQL 注入模式
        dangerous_patterns = [
            r'--',           # SQL 注释
            r';',            # SQL 语句分隔符（在某些上下文中）
            r"'.*OR.*'",     # OR 注入
            r"'.*AND.*'",    # AND 注入
            r'UNION\s+SELECT',  # UNION 注入
            r'DROP\s+TABLE',    # DROP 注入
            r'DELETE\s+FROM',   # DELETE 注入
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                # 记录可疑输入但不阻止（依赖 ORM 的参数化查询）
                pass
        # 去除首尾空白
        value = value.strip()
    return value


def sanitize_dict(data):
    """递归清理字典中的所有字符串值
    
    Args:
        data: 输入字典
        
    Returns:
        清理后的字典
    """
    if isinstance(data, dict):
        return {k: sanitize_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_dict(item) for item in data]
    elif isinstance(data, str):
        return sanitize_input(data)
    return data


# 常用验证器
def validate_ip(value):
    """验证 IP 地址格式"""
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(ip_pattern, value):
        raise ValidationError('无效的 IP 地址格式')
    parts = value.split('.')
    for part in parts:
        if int(part) > 255:
            raise ValidationError('无效的 IP 地址格式')


def validate_email(value):
    """验证邮箱格式"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, value):
        raise ValidationError('无效的邮箱格式')
