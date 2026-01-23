# routes/incidents.py
# 事件响应 API
# Requirements: 2.2, 6.4, 7.2, 14.5

from flask import Blueprint, request
from flask_login import current_user
from middleware.rbac import require_role
from middleware.response import api_response, paginated_response, not_found
from services.audit_service import audit_action
from schemas.incident import IncidentCreateSchema, IncidentUpdateSchema
from schemas.common import validate_request
from extensions import db, socketio
from models import Incident, IncidentTimeline
from datetime import datetime, timezone

incidents_bp = Blueprint('incidents', __name__)


def notify_dashboard_update():
    """通知仪表盘数据已更新"""
    from sockets.alerts import push_dashboard_update
    push_dashboard_update(socketio, {'type': 'incidents_changed'})


def notify_alert(incident, severity):
    """推送告警通知
    
    Requirement 6.4: 按严重级别推送告警
    """
    from sockets.alerts import push_alert
    push_alert(socketio, {
        'id': incident.id,
        'title': incident.title,
        'type': incident.type,
        'status': incident.status,
        'created_at': incident.created_at.isoformat() if incident.created_at else None
    }, severity)


def serialize_incident(incident):
    """序列化事件对象"""
    return {
        'id': incident.id,
        'title': incident.title,
        'type': incident.type,
        'severity': incident.severity,
        'status': incident.status,
        'description': incident.description,
        'assignee_id': incident.assignee_id,
        'assignee': incident.assignee.username if incident.assignee else None,
        'affected_assets': incident.affected_assets or [],
        'created_at': incident.created_at.isoformat() if incident.created_at else None,
        'updated_at': incident.updated_at.isoformat() if incident.updated_at else None,
        'closed_at': incident.closed_at.isoformat() if incident.closed_at else None
    }


def serialize_timeline(entry):
    """序列化时间线条目"""
    return {
        'id': entry.id,
        'type': entry.type,
        'action': entry.action,
        'user': entry.user.username if entry.user else 'System',
        'timestamp': entry.timestamp.isoformat() if entry.timestamp else None
    }


@incidents_bp.route('/', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_incidents():
    """获取事件列表"""
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 20, type=int), 100)
    
    query = Incident.query
    
    if request.args.get('status'):
        query = query.filter(Incident.status == request.args.get('status'))
    if request.args.get('severity'):
        query = query.filter(Incident.severity == request.args.get('severity'))
    if request.args.get('type'):
        query = query.filter(Incident.type == request.args.get('type'))
    
    query = query.order_by(Incident.created_at.desc())
    
    total = query.count()
    incidents = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return paginated_response(
        items=[serialize_incident(i) for i in incidents],
        total=total,
        page=page,
        page_size=page_size
    )


@incidents_bp.route('/', methods=['POST'])
@require_role('analyst', 'admin')
@validate_request(IncidentCreateSchema)
@audit_action('create', 'incident')
def create_incident(validated_data):
    """创建安全事件"""
    incident = Incident(
        title=validated_data['title'],
        type=validated_data['type'],
        severity=validated_data['severity'],
        status='new',
        description=validated_data.get('description'),
        assignee_id=validated_data.get('assignee_id'),
        affected_assets=validated_data.get('affected_assets', [])
    )
    
    db.session.add(incident)
    db.session.flush()
    
    # 添加创建时间线
    timeline = IncidentTimeline(
        incident_id=incident.id,
        type='created',
        action='事件创建',
        user_id=current_user.id if current_user.is_authenticated else None
    )
    db.session.add(timeline)
    db.session.commit()
    
    # 推送告警和仪表盘更新
    notify_alert(incident, incident.severity)
    notify_dashboard_update()
    
    return api_response(serialize_incident(incident), '事件创建成功', 201)


@incidents_bp.route('/<incident_id>', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_incident(incident_id):
    """获取事件详情"""
    incident = Incident.query.get(incident_id)
    if not incident:
        return not_found('事件不存在')
    return api_response(serialize_incident(incident))


@incidents_bp.route('/<incident_id>', methods=['PATCH'])
@require_role('analyst', 'admin')
@validate_request(IncidentUpdateSchema)
@audit_action('update', 'incident')
def update_incident(validated_data, incident_id):
    """更新事件"""
    incident = Incident.query.get(incident_id)
    if not incident:
        return not_found('事件不存在')
    
    old_status = incident.status
    
    for key, value in validated_data.items():
        if hasattr(incident, key) and value is not None:
            setattr(incident, key, value)
    
    # 状态变更时添加时间线
    if validated_data.get('status') and validated_data['status'] != old_status:
        timeline = IncidentTimeline(
            incident_id=incident.id,
            type='status_change',
            action=f'状态变更为: {validated_data["status"]}',
            user_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(timeline)
        
        if validated_data['status'] == 'closed':
            incident.closed_at = datetime.now(timezone.utc)
    
    incident.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    
    # 通知仪表盘更新
    notify_dashboard_update()
    
    return api_response(serialize_incident(incident), '事件更新成功')


@incidents_bp.route('/<incident_id>', methods=['DELETE'])
@require_role('admin')
@audit_action('delete', 'incident')
def delete_incident(incident_id):
    """删除事件"""
    incident = Incident.query.get(incident_id)
    if not incident:
        return not_found('事件不存在')
    
    db.session.delete(incident)
    db.session.commit()
    
    # 通知仪表盘更新
    notify_dashboard_update()
    
    return api_response(None, '事件删除成功')


@incidents_bp.route('/<incident_id>/timeline', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_incident_timeline(incident_id):
    """获取事件时间线"""
    incident = Incident.query.get(incident_id)
    if not incident:
        return not_found('事件不存在')
    
    return api_response([serialize_timeline(t) for t in incident.timeline])


@incidents_bp.route('/<incident_id>/timeline', methods=['POST'])
@require_role('analyst', 'admin')
@audit_action('update', 'incident')
def add_timeline_entry(incident_id):
    """添加时间线条目"""
    incident = Incident.query.get(incident_id)
    if not incident:
        return not_found('事件不存在')
    
    data = request.get_json() or {}
    
    timeline = IncidentTimeline(
        incident_id=incident.id,
        type=data.get('type', 'comment'),
        action=data.get('action', ''),
        user_id=current_user.id if current_user.is_authenticated else None
    )
    
    db.session.add(timeline)
    db.session.commit()
    
    return api_response(serialize_timeline(timeline), '时间线添加成功', 201)


@incidents_bp.route('/activities', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_activities():
    """获取最近活动"""
    activities = IncidentTimeline.query.order_by(
        IncidentTimeline.timestamp.desc()
    ).limit(20).all()
    
    return api_response([{
        'type': a.type,
        'description': a.action,
        'timestamp': a.timestamp.isoformat() if a.timestamp else None,
        'incident_id': a.incident_id
    } for a in activities])


# Playbooks (保持模拟数据)
playbooks_data = [
    {'id': 'pb-1', 'name': '恶意软件响应', 'trigger_type': '恶意软件告警', 'enabled': True, 'steps': ['隔离主机', '采集样本', '扫描关联主机', '清除恶意文件']},
    {'id': 'pb-2', 'name': '钓鱼邮件处置', 'trigger_type': '钓鱼邮件告警', 'enabled': True, 'steps': ['提取IOC', '封禁发件人', '全网搜索', '通知用户']},
    {'id': 'pb-3', 'name': '暴力破解响应', 'trigger_type': '暴力破解告警', 'enabled': True, 'steps': ['封禁IP', '重置密码', '检查登录日志', '加固认证']},
    {'id': 'pb-4', 'name': '数据泄露响应', 'trigger_type': '数据泄露告警', 'enabled': False, 'steps': ['阻断传输', '溯源分析', '影响评估', '上报管理层']},
]


@incidents_bp.route('/playbooks', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_playbooks():
    """获取剧本列表"""
    return api_response(playbooks_data)


@incidents_bp.route('/playbooks/<playbook_id>/run', methods=['POST'])
@require_role('analyst', 'admin')
@audit_action('execute', 'playbook')
def run_playbook(playbook_id):
    """执行剧本"""
    playbook = next((p for p in playbooks_data if p['id'] == playbook_id), None)
    if not playbook:
        return not_found('剧本不存在')
    
    return api_response({
        'status': 'completed',
        'playbook_id': playbook_id,
        'playbook_name': playbook['name']
    }, '剧本执行完成')
