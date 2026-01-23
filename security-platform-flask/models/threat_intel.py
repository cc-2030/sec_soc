# models/threat_intel.py
# 威胁情报模型
# Requirements: 4.4, 4.5

from extensions import db
from datetime import datetime
import uuid


class IOC(db.Model):
    """IOC (Indicator of Compromise) 模型"""
    __tablename__ = 'iocs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = db.Column(db.String(20), nullable=False, index=True)  # ip, domain, hash, url, email
    value = db.Column(db.String(500), nullable=False, index=True)
    threat_type = db.Column(db.String(100))
    confidence = db.Column(db.Integer, default=50)  # 0-100
    source = db.Column(db.String(100))
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 复合索引优化查询性能
    __table_args__ = (
        db.Index('idx_ioc_type_value', 'type', 'value'),
    )
    
    def __repr__(self):
        return f'<IOC {self.type}:{self.value}>'


class ThreatFeed(db.Model):
    """威胁情报源模型"""
    __tablename__ = 'threat_feeds'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))  # STIX/TAXII, API, RSS
    url = db.Column(db.String(500))
    api_key = db.Column(db.String(200))
    enabled = db.Column(db.Boolean, default=True)
    last_update = db.Column(db.DateTime)
    ioc_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ThreatFeed {self.name}>'
