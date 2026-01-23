# schemas/incident.py
# 事件相关验证模式
# Requirements: 16.1, 16.3

from marshmallow import Schema, fields, validate


INCIDENT_TYPES = ['malware', 'unauthorized_access', 'data_breach', 'phishing', 'ddos', 'insider_threat', 'other']
SEVERITY_LEVELS = ['critical', 'high', 'medium', 'low']
INCIDENT_STATUS = ['new', 'investigating', 'containing', 'eradicating', 'recovering', 'closed']


class IncidentCreateSchema(Schema):
    """创建事件请求验证模式"""
    title = fields.Str(required=True, validate=validate.Length(min=1, max=300))
    type = fields.Str(required=True, validate=validate.OneOf(INCIDENT_TYPES))
    severity = fields.Str(required=True, validate=validate.OneOf(SEVERITY_LEVELS))
    description = fields.Str()
    affected_assets = fields.List(fields.Str(), load_default=[])
    assignee_id = fields.Str(validate=validate.Length(max=36))


class IncidentUpdateSchema(Schema):
    """更新事件请求验证模式"""
    title = fields.Str(validate=validate.Length(min=1, max=300))
    type = fields.Str(validate=validate.OneOf(INCIDENT_TYPES))
    severity = fields.Str(validate=validate.OneOf(SEVERITY_LEVELS))
    status = fields.Str(validate=validate.OneOf(INCIDENT_STATUS))
    description = fields.Str()
    affected_assets = fields.List(fields.Str())
    assignee_id = fields.Str(validate=validate.Length(max=36), allow_none=True)


class IncidentTimelineSchema(Schema):
    """事件时间线条目验证模式"""
    type = fields.Str(required=True, validate=validate.OneOf(['comment', 'status_change', 'playbook', 'evidence']))
    action = fields.Str(required=True, validate=validate.Length(min=1, max=500))
