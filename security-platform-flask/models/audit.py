# models/audit.py
# 审计日志模型
# Requirements: 4.4, 4.5

from extensions import db
from datetime import datetime
import uuid


class AuditLog(db.Model):
    """审计日志模型"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), index=True)
    username = db.Column(db.String(80))
    action_type = db.Column(db.String(50), nullable=False, index=True)  # create, update, delete, login, logout
    resource_type = db.Column(db.String(50), index=True)  # asset, vulnerability, incident, etc.
    resource_id = db.Column(db.String(36))
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    user = db.relationship('User', backref='audit_logs')
    
    # 复合索引优化查询性能
    __table_args__ = (
        db.Index('idx_audit_time_user', 'timestamp', 'user_id'),
        db.Index('idx_audit_resource', 'resource_type', 'resource_id'),
    )
    
    def __repr__(self):
        return f'<AuditLog {self.action_type} {self.resource_type}>'
