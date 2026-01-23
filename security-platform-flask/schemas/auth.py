# schemas/auth.py
# 认证相关验证模式
# Requirements: 16.1, 16.3

from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    """登录请求验证模式"""
    username = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    password = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    remember = fields.Bool(load_default=False)


class UserCreateSchema(Schema):
    """创建用户请求验证模式"""
    username = fields.Str(
        required=True, 
        validate=[
            validate.Length(min=3, max=80),
            validate.Regexp(r'^[a-zA-Z0-9_]+$', error='用户名只能包含字母、数字和下划线')
        ]
    )
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(
        required=True, 
        validate=validate.Length(min=6, max=128, error='密码长度必须在 6-128 个字符之间')
    )
    roles = fields.List(
        fields.Str(validate=validate.OneOf(['admin', 'analyst', 'viewer'])),
        load_default=['viewer']
    )


class UserUpdateSchema(Schema):
    """更新用户请求验证模式"""
    roles = fields.List(
        fields.Str(validate=validate.OneOf(['admin', 'analyst', 'viewer']))
    )
    is_active = fields.Bool()
