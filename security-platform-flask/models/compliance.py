# models/compliance.py
# 合规检查模型
# Requirements: 4.4, 4.5

from extensions import db
from datetime import datetime
import uuid


class ComplianceFramework(db.Model):
    """合规框架模型"""
    __tablename__ = 'compliance_frameworks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    total_controls = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    checks = db.relationship('ComplianceCheck', backref='framework')
    
    def __repr__(self):
        return f'<ComplianceFramework {self.name}>'


class ComplianceCheck(db.Model):
    """合规检查项模型"""
    __tablename__ = 'compliance_checks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    framework_id = db.Column(db.String(36), db.ForeignKey('compliance_frameworks.id'), nullable=False)
    control_id = db.Column(db.String(50))
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # passed, failed, pending, not_applicable
    last_check = db.Column(db.DateTime)
    evidence = db.Column(db.Text)
    remediation = db.Column(db.Text)
    
    def __repr__(self):
        return f'<ComplianceCheck {self.control_id}: {self.title}>'
