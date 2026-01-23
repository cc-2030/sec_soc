# models/incident.py
# 事件模型
# Requirements: 4.4, 4.5

from extensions import db
from datetime import datetime
import uuid


class Incident(db.Model):
    """事件模型"""
    __tablename__ = 'incidents'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(300), nullable=False)
    type = db.Column(db.String(50), nullable=False, index=True)  # malware, unauthorized_access, data_breach, phishing, etc.
    severity = db.Column(db.String(20), nullable=False, index=True)  # critical, high, medium, low
    status = db.Column(db.String(20), default='new', index=True)  # new, investigating, containing, eradicating, recovering, closed
    description = db.Column(db.Text)
    assignee_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    affected_assets = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    
    assignee = db.relationship('User', backref='assigned_incidents')
    timeline = db.relationship('IncidentTimeline', backref='incident', order_by='IncidentTimeline.timestamp')
    
    def __repr__(self):
        return f'<Incident {self.title}>'


class IncidentTimeline(db.Model):
    """事件时间线模型"""
    __tablename__ = 'incident_timeline'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = db.Column(db.String(36), db.ForeignKey('incidents.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # created, status_change, comment, playbook, etc.
    action = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<IncidentTimeline {self.type} {self.action}>'
