# schemas/asset.py
# 资产相关验证模式
# Requirements: 16.1, 16.3

from marshmallow import Schema, fields, validate


ASSET_TYPES = ['server', 'endpoint', 'network', 'application', 'database', 'cloud']
CRITICALITY_LEVELS = ['critical', 'high', 'medium', 'low']
ASSET_STATUS = ['online', 'offline', 'maintenance']


class AssetCreateSchema(Schema):
    """创建资产请求验证模式"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    type = fields.Str(required=True, validate=validate.OneOf(ASSET_TYPES))
    ip = fields.Str(required=True, validate=validate.Length(max=45))
    os = fields.Str(validate=validate.Length(max=100))
    owner = fields.Str(validate=validate.Length(max=100))
    department = fields.Str(validate=validate.Length(max=100))
    criticality = fields.Str(
        load_default='medium',
        validate=validate.OneOf(CRITICALITY_LEVELS)
    )
    status = fields.Str(
        load_default='online',
        validate=validate.OneOf(ASSET_STATUS)
    )
    tags = fields.List(fields.Str(validate=validate.Length(max=50)), load_default=[])


class AssetUpdateSchema(Schema):
    """更新资产请求验证模式"""
    name = fields.Str(validate=validate.Length(min=1, max=200))
    type = fields.Str(validate=validate.OneOf(ASSET_TYPES))
    ip = fields.Str(validate=validate.Length(max=45))
    os = fields.Str(validate=validate.Length(max=100))
    owner = fields.Str(validate=validate.Length(max=100))
    department = fields.Str(validate=validate.Length(max=100))
    criticality = fields.Str(validate=validate.OneOf(CRITICALITY_LEVELS))
    status = fields.Str(validate=validate.OneOf(ASSET_STATUS))
    tags = fields.List(fields.Str(validate=validate.Length(max=50)))
    compliant = fields.Bool()
    patch_pending = fields.Bool()
