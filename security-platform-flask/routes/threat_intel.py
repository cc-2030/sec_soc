# routes/threat_intel.py
# 威胁情报 API
# Requirements: 14.5

from flask import Blueprint, request
from middleware.rbac import require_role
from middleware.response import api_response, paginated_response, not_found
from services.audit_service import audit_action
from extensions import db
from models import IOC, ThreatFeed
from datetime import datetime, timezone

threat_intel_bp = Blueprint('threat_intel', __name__)


def serialize_ioc(ioc):
    """序列化 IOC 对象"""
    return {
        'id': ioc.id,
        'type': ioc.type,
        'value': ioc.value,
        'threat_type': ioc.threat_type,
        'confidence': ioc.confidence,
        'source': ioc.source,
        'first_seen': ioc.first_seen.isoformat() if ioc.first_seen else None,
        'last_seen': ioc.last_seen.isoformat() if ioc.last_seen else None,
        'created_at': ioc.created_at.isoformat() if ioc.created_at else None
    }


def serialize_feed(feed):
    """序列化威胁源对象"""
    return {
        'id': feed.id,
        'name': feed.name,
        'type': feed.type,
        'url': feed.url,
        'enabled': feed.enabled,
        'last_update': feed.last_update.isoformat() if feed.last_update else None,
        'ioc_count': feed.ioc_count,
        'created_at': feed.created_at.isoformat() if feed.created_at else None
    }


@threat_intel_bp.route('/iocs', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_iocs():
    """获取 IOC 列表"""
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 20, type=int), 100)
    
    query = IOC.query
    
    if request.args.get('type'):
        query = query.filter(IOC.type == request.args.get('type'))
    if request.args.get('threat_type'):
        query = query.filter(IOC.threat_type == request.args.get('threat_type'))
    
    query = query.order_by(IOC.last_seen.desc())
    
    total = query.count()
    iocs = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return paginated_response(
        items=[serialize_ioc(i) for i in iocs],
        total=total,
        page=page,
        page_size=page_size
    )


@threat_intel_bp.route('/iocs', methods=['POST'])
@require_role('analyst', 'admin')
@audit_action('create', 'ioc')
def add_ioc():
    """添加 IOC"""
    data = request.get_json() or {}
    
    ioc = IOC(
        type=data.get('type'),
        value=data.get('value'),
        threat_type=data.get('threat_type'),
        confidence=data.get('confidence', 50),
        source=data.get('source', '手动添加'),
        first_seen=datetime.now(timezone.utc),
        last_seen=datetime.now(timezone.utc)
    )
    
    db.session.add(ioc)
    db.session.commit()
    
    return api_response(serialize_ioc(ioc), 'IOC 添加成功', 201)


@threat_intel_bp.route('/iocs/<ioc_id>', methods=['DELETE'])
@require_role('admin')
@audit_action('delete', 'ioc')
def delete_ioc(ioc_id):
    """删除 IOC"""
    ioc = IOC.query.get(ioc_id)
    if not ioc:
        return not_found('IOC 不存在')
    
    db.session.delete(ioc)
    db.session.commit()
    
    return api_response(None, 'IOC 删除成功')


@threat_intel_bp.route('/feeds', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_feeds():
    """获取威胁源列表"""
    feeds = ThreatFeed.query.all()
    return api_response([serialize_feed(f) for f in feeds])


@threat_intel_bp.route('/feeds', methods=['POST'])
@require_role('admin')
@audit_action('create', 'threat_feed')
def add_feed():
    """添加威胁源"""
    data = request.get_json() or {}
    
    feed = ThreatFeed(
        name=data.get('name'),
        type=data.get('type'),
        url=data.get('url'),
        api_key=data.get('api_key'),
        enabled=data.get('enabled', True)
    )
    
    db.session.add(feed)
    db.session.commit()
    
    return api_response(serialize_feed(feed), '威胁源添加成功', 201)


@threat_intel_bp.route('/feeds/<feed_id>', methods=['PATCH'])
@require_role('admin')
@audit_action('update', 'threat_feed')
def update_feed(feed_id):
    """更新威胁源"""
    feed = ThreatFeed.query.get(feed_id)
    if not feed:
        return not_found('威胁源不存在')
    
    data = request.get_json() or {}
    
    if 'enabled' in data:
        feed.enabled = data['enabled']
    if 'name' in data:
        feed.name = data['name']
    if 'url' in data:
        feed.url = data['url']
    
    db.session.commit()
    
    return api_response(serialize_feed(feed), '威胁源更新成功')


@threat_intel_bp.route('/stats', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_stats():
    """获取威胁情报统计"""
    from sqlalchemy import func
    from datetime import timedelta
    
    today = datetime.now(timezone.utc).date()
    
    total_iocs = IOC.query.count()
    new_today = IOC.query.filter(
        func.date(IOC.created_at) == today
    ).count()
    
    return api_response({
        'total_iocs': total_iocs,
        'new_today': new_today,
        'hit_alerts': 0,  # 需要实现告警关联
        'sources': ThreatFeed.query.filter_by(enabled=True).count()
    })


@threat_intel_bp.route('/search', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def search_ioc():
    """搜索 IOC"""
    q = request.args.get('q', '').lower()
    
    if not q:
        return api_response({'found': False})
    
    ioc = IOC.query.filter(IOC.value.ilike(f'%{q}%')).first()
    
    if ioc:
        return api_response({
            'found': True,
            'threat_level': 'high' if ioc.confidence > 80 else 'medium',
            'description': f"匹配到威胁情报: {ioc.threat_type}",
            'ioc': serialize_ioc(ioc)
        })
    
    return api_response({'found': False})
