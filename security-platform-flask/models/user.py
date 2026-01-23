# models/user.py
# 用户和角色模型
# Requirements: 4.4, 4.5

from extensions import db
from flask_login import UserMixin
from datetime import datetime
import uuid

# 用户-角色关联表
user_roles = db.Table('user_roles',
    db.Column('user_id', db.String(36), db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.String(36), db.ForeignKey('roles.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    roles = db.relationship('Role', secondary=user_roles, backref='users')
    
    def has_role(self, role_name: str) -> bool:
        """检查用户是否具有指定角色"""
        return any(r.name == role_name for r in self.roles)
    
    def has_any_role(self, role_names: list) -> bool:
        """检查用户是否具有指定角色之一"""
        return any(self.has_role(r) for r in role_names)
    
    def has_permission(self, permission: str) -> bool:
        """检查用户是否具有指定权限"""
        for role in self.roles:
            if '*' in role.permissions or permission in role.permissions:
                return True
        return False
    
    def __repr__(self):
        return f'<User {self.username}>'


class Role(db.Model):
    """角色模型"""
    __tablename__ = 'roles'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Role {self.name}>'
