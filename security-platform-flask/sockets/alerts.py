# sockets/alerts.py
# 告警推送 WebSocket 事件处理
# Requirements: 6.2, 6.3, 6.4, 7.1, 7.2

from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room, disconnect


def register_alert_events(socketio):
    """注册告警相关的 WebSocket 事件处理
    
    Requirement 6.2: THE WebSocket_Server SHALL 验证连接用户的认证状态
    Requirement 6.3: THE WebSocket_Server SHALL 支持告警订阅
    Requirement 6.4: THE WebSocket_Server SHALL 按严重级别推送告警
    """
    
    @socketio.on('connect')
    def handle_connect():
        """处理 WebSocket 连接
        
        Requirement 6.2: 验证连接用户的认证状态，未认证用户拒绝连接
        """
        if not current_user.is_authenticated:
            # 拒绝未认证用户的连接
            return False
        
        # 连接成功，加入用户专属房间
        join_room(f'user_{current_user.id}')
        emit('connected', {
            'message': '连接成功',
            'user_id': current_user.id,
            'username': current_user.username
        })
        return True
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """处理 WebSocket 断开连接"""
        if current_user.is_authenticated:
            leave_room(f'user_{current_user.id}')
    
    @socketio.on('subscribe_alerts')
    def handle_subscribe_alerts(data):
        """订阅告警推送
        
        Requirement 6.3: 支持告警订阅
        Requirement 6.4: 按严重级别推送告警
        
        Args:
            data: 订阅配置
                - severity: 订阅的严重级别列表 ['critical', 'high', 'medium', 'low']
                           或 'all' 订阅所有级别
        """
        if not current_user.is_authenticated:
            emit('error', {'message': '未认证'})
            return
        
        severity = data.get('severity', 'all')
        
        # 离开之前的告警房间
        for level in ['critical', 'high', 'medium', 'low', 'all']:
            leave_room(f'alerts_{level}')
        
        # 加入新的告警房间
        if severity == 'all':
            join_room('alerts_all')
            emit('subscribed', {'severity': 'all', 'message': '已订阅所有告警'})
        elif isinstance(severity, list):
            for level in severity:
                if level in ['critical', 'high', 'medium', 'low']:
                    join_room(f'alerts_{level}')
            emit('subscribed', {'severity': severity, 'message': f'已订阅 {", ".join(severity)} 级别告警'})
        else:
            if severity in ['critical', 'high', 'medium', 'low']:
                join_room(f'alerts_{severity}')
                emit('subscribed', {'severity': severity, 'message': f'已订阅 {severity} 级别告警'})
    
    @socketio.on('unsubscribe_alerts')
    def handle_unsubscribe_alerts():
        """取消订阅告警推送"""
        for level in ['critical', 'high', 'medium', 'low', 'all']:
            leave_room(f'alerts_{level}')
        emit('unsubscribed', {'message': '已取消告警订阅'})
    
    @socketio.on('subscribe_dashboard')
    def handle_subscribe_dashboard():
        """订阅仪表盘实时更新
        
        Requirement 7.1: 仪表盘数据实时更新
        """
        if not current_user.is_authenticated:
            emit('error', {'message': '未认证'})
            return
        
        join_room('dashboard')
        emit('subscribed', {'channel': 'dashboard', 'message': '已订阅仪表盘更新'})
    
    @socketio.on('unsubscribe_dashboard')
    def handle_unsubscribe_dashboard():
        """取消订阅仪表盘更新"""
        leave_room('dashboard')
        emit('unsubscribed', {'channel': 'dashboard', 'message': '已取消仪表盘订阅'})


def push_alert(socketio, alert, severity='medium'):
    """推送告警到订阅的客户端
    
    Requirement 6.4: THE WebSocket_Server SHALL 按严重级别推送告警
    
    Args:
        socketio: SocketIO 实例
        alert: 告警数据字典
        severity: 告警严重级别 ('critical', 'high', 'medium', 'low')
    """
    alert_data = {
        'type': 'alert',
        'severity': severity,
        'data': alert
    }
    
    # 推送到对应严重级别的房间
    socketio.emit('alert', alert_data, room=f'alerts_{severity}')
    
    # 同时推送到订阅所有告警的房间
    socketio.emit('alert', alert_data, room='alerts_all')


def push_dashboard_update(socketio, data):
    """推送仪表盘更新到订阅的客户端
    
    Requirement 7.2: THE Dashboard SHALL 通过 WebSocket 接收实时数据更新
    
    Args:
        socketio: SocketIO 实例
        data: 仪表盘更新数据
    """
    socketio.emit('dashboard_update', {
        'type': 'dashboard_update',
        'data': data
    }, room='dashboard')
