# services/audit_service.py
# 审计日志服务
# Requirements: 3.1, 3.2, 3.4

from functools import wraps
from flask import request, g
from flask_login import current_user
from extensions import db
from models import AuditLog
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any


class AuditService:
    """审计日志服务类
    
    提供审计日志的记录和查询功能。
    Requirement 3.1: 记录所有写操作
    Requirement 3.2: 记录完整的审计字段
    Requirement 3.4: 提供审计日志查询 API
    """
    
    @staticmethod
    def log(
        action_type: str,
        resource_type: str = None,
        resource_id: str = None,
        details: Dict[str, Any] = None,
        user_id: str = None,
        username: str = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> AuditLog:
        """记录审计日志
        
        Args:
            action_type: 操作类型 (create, update, delete, login, logout)
            resource_type: 资源类型 (asset, vulnerability, incident, etc.)
            resource_id: 资源 ID
            details: 操作详情
            user_id: 用户 ID（可选，默认从 current_user 获取）
            username: 用户名（可选，默认从 current_user 获取）
            ip_address: IP 地址（可选，默认从 request 获取）
            user_agent: User Agent（可选，默认从 request 获取）
            
        Returns:
            创建的 AuditLog 对象
            
        Requirement 3.2: 记录时间戳、用户ID、用户名、操作类型、资源类型、资源ID、操作详情、IP地址
        """
        # 获取用户信息
        if user_id is None and current_user and current_user.is_authenticated:
            user_id = current_user.id
            username = current_user.username
        
        # 获取请求信息
        if ip_address is None:
            try:
                ip_address = request.remote_addr
            except RuntimeError:
                ip_address = None
        
        if user_agent is None:
            try:
                user_agent = request.headers.get('User-Agent', '')[:500]
            except RuntimeError:
                user_agent = None
        
        # 创建审计日志
        audit_log = AuditLog(
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            username=username,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return audit_log
    
    @staticmethod
    def query(
        start_time: datetime = None,
        end_time: datetime = None,
        user_id: str = None,
        action_type: str = None,
        resource_type: str = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """查询审计日志
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            user_id: 用户 ID
            action_type: 操作类型
            resource_type: 资源类型
            page: 页码（从 1 开始）
            page_size: 每页条数
            
        Returns:
            包含 items, total, page, page_size 的字典
            
        Requirement 3.4: 提供按时间范围、用户、操作类型查询审计日志的 API
        """
        query = AuditLog.query
        
        # 应用过滤条件
        if start_time:
            query = query.filter(AuditLog.timestamp >= start_time)
        if end_time:
            query = query.filter(AuditLog.timestamp <= end_time)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action_type:
            query = query.filter(AuditLog.action_type == action_type)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        # 按时间倒序排列
        query = query.order_by(AuditLog.timestamp.desc())
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        
        return {
            'items': [AuditService._serialize_log(log) for log in items],
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    @staticmethod
    def _serialize_log(log: AuditLog) -> Dict[str, Any]:
        """序列化审计日志"""
        return {
            'id': log.id,
            'timestamp': log.timestamp.isoformat() if log.timestamp else None,
            'user_id': log.user_id,
            'username': log.username,
            'action_type': log.action_type,
            'resource_type': log.resource_type,
            'resource_id': log.resource_id,
            'details': log.details,
            'ip_address': log.ip_address
        }


def audit_action(action_type: str, resource_type: str):
    """记录操作审计日志的装饰器
    
    Args:
        action_type: 操作类型 (create, update, delete)
        resource_type: 资源类型 (asset, vulnerability, incident, etc.)
        
    Usage:
        @audit_action('create', 'asset')
        def create_asset():
            ...
            
    Requirement 3.1: WHEN 用户执行任何写操作 THEN 记录操作详情
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 执行原函数
            result = f(*args, **kwargs)
            
            # 获取资源 ID
            resource_id = kwargs.get('id') or kwargs.get('asset_id') or kwargs.get('vulnerability_id')
            
            # 获取请求数据作为详情
            details = None
            try:
                if request.is_json:
                    details = request.get_json(silent=True)
            except RuntimeError:
                pass
            
            # 记录审计日志
            try:
                AuditService.log(
                    action_type=action_type,
                    resource_type=resource_type,
                    resource_id=str(resource_id) if resource_id else None,
                    details=details
                )
            except Exception as e:
                # 审计日志记录失败不应影响主业务
                import logging
                logging.error(f'Failed to log audit: {e}')
            
            return result
        return decorated_function
    return decorator
