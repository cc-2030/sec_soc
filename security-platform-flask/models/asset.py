# models/asset.py
# 资产模型
# Requirements: 4.4, 4.5

from extensions import db
from datetime import datetime
import uuid


class Asset(db.Model):
    """资产模型"""
    __tablename__ = 'assets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False, index=True)  # server, endpoint, network, application, database, cloud
    ip = db.Column(db.String(45), index=True)
    os = db.Column(db.String(100))
    owner = db.Column(db.String(100))
    department = db.Column(db.String(100), index=True)
    criticality = db.Column(db.String(20), default='medium')  # critical, high, medium, low
    status = db.Column(db.String(20), default='online')  # online, offline, maintenance
    risk_score = db.Column(db.Integer, default=0)
    tags = db.Column(db.JSON, default=list)
    compliant = db.Column(db.Boolean, default=True)
    patch_pending = db.Column(db.Boolean, default=False)
    last_scan = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    vulnerabilities = db.relationship('Vulnerability', secondary='asset_vulnerabilities', backref='assets')
    
    def __repr__(self):
        return f'<Asset {self.name}>'
