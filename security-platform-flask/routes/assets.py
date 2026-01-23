# routes/assets.py
# 资产管理 API
# Requirements: 2.2, 14.5, 7.2

from flask import Blueprint, request
from middleware.rbac import require_role
from middleware.response import api_response, paginated_response, not_found
from services.audit_service import audit_action
from schemas.asset import AssetCreateSchema, AssetUpdateSchema
from schemas.common import validate_request
from extensions import db, socketio
from models import Asset
from datetime import datetime, timezone
import random

assets_bp = Blueprint('assets', __name__)


def notify_dashboard_update():
    """通知仪表盘数据已更新
    
    Requirement 7.2: 在数据变更时触发推送
    """
    from sockets.alerts import push_dashboard_update
    push_dashboard_update(socketio, {'type': 'assets_changed'})


def serialize_asset(asset):
    """序列化资产对象"""
    return {
        'id': asset.id,
        'name': asset.name,
        'type': asset.type,
        'ip': asset.ip,
        'os': asset.os,
        'owner': asset.owner,
        'department': asset.department,
        'criticality': asset.criticality,
        'status': asset.status,
        'risk_score': asset.risk_score,
        'tags': asset.tags or [],
        'compliant': asset.compliant,
        'patch_pending': asset.patch_pending,
        'last_scan': asset.last_scan.isoformat() if asset.last_scan else None,
        'created_at': asset.created_at.isoformat() if asset.created_at else None,
        'updated_at': asset.updated_at.isoformat() if asset.updated_at else None
    }


@assets_bp.route('/', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_assets():
    """获取资产列表
    ---
    tags:
      - 资产管理
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: 页码
      - name: page_size
        in: query
        type: integer
        default: 20
        description: 每页条数
      - name: type
        in: query
        type: string
        description: 资产类型筛选
      - name: department
        in: query
        type: string
        description: 部门筛选
      - name: status
        in: query
        type: string
        description: 状态筛选
    responses:
      200:
        description: 资产列表（分页）
      401:
        description: 未登录
    """
    # 分页参数
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 20, type=int), 100)
    
    # 构建查询
    query = Asset.query
    
    # 筛选条件
    if request.args.get('type'):
        query = query.filter(Asset.type == request.args.get('type'))
    if request.args.get('department'):
        query = query.filter(Asset.department == request.args.get('department'))
    if request.args.get('status'):
        query = query.filter(Asset.status == request.args.get('status'))
    
    # 排序
    query = query.order_by(Asset.created_at.desc())
    
    # 计算总数
    total = query.count()
    
    # 分页查询
    assets = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return paginated_response(
        items=[serialize_asset(a) for a in assets],
        total=total,
        page=page,
        page_size=page_size
    )


@assets_bp.route('/', methods=['POST'])
@require_role('analyst', 'admin')
@validate_request(AssetCreateSchema)
@audit_action('create', 'asset')
def add_asset(validated_data):
    """创建新资产
    ---
    tags:
      - 资产管理
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - type
            - ip
          properties:
            name:
              type: string
            type:
              type: string
              enum: [server, endpoint, network, application, database, cloud]
            ip:
              type: string
            os:
              type: string
            owner:
              type: string
            department:
              type: string
            criticality:
              type: string
              enum: [critical, high, medium, low]
            tags:
              type: array
              items:
                type: string
    responses:
      201:
        description: 创建成功
      400:
        description: 请求参数错误
      401:
        description: 未登录
      403:
        description: 权限不足
    """
    asset = Asset(
        name=validated_data['name'],
        type=validated_data['type'],
        ip=validated_data['ip'],
        os=validated_data.get('os'),
        owner=validated_data.get('owner'),
        department=validated_data.get('department'),
        criticality=validated_data.get('criticality', 'medium'),
        status=validated_data.get('status', 'online'),
        tags=validated_data.get('tags', []),
        risk_score=random.randint(10, 50),
        compliant=True,
        patch_pending=False
    )
    
    db.session.add(asset)
    db.session.commit()
    
    # 通知仪表盘更新
    notify_dashboard_update()
    
    return api_response(serialize_asset(asset), '资产创建成功', 201)


@assets_bp.route('/<asset_id>', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_asset(asset_id):
    """获取单个资产详情
    ---
    tags:
      - 资产管理
    parameters:
      - name: asset_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: 资产详情
      404:
        description: 资产不存在
    """
    asset = Asset.query.get(asset_id)
    if not asset:
        return not_found('资产不存在')
    return api_response(serialize_asset(asset))


@assets_bp.route('/<asset_id>', methods=['PATCH'])
@require_role('analyst', 'admin')
@validate_request(AssetUpdateSchema)
@audit_action('update', 'asset')
def update_asset(validated_data, asset_id):
    """更新资产
    ---
    tags:
      - 资产管理
    parameters:
      - name: asset_id
        in: path
        type: string
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
            type:
              type: string
            ip:
              type: string
            status:
              type: string
    responses:
      200:
        description: 更新成功
      404:
        description: 资产不存在
    """
    asset = Asset.query.get(asset_id)
    if not asset:
        return not_found('资产不存在')
    
    # 更新字段
    for key, value in validated_data.items():
        if hasattr(asset, key) and value is not None:
            setattr(asset, key, value)
    
    asset.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    
    # 通知仪表盘更新
    notify_dashboard_update()
    
    return api_response(serialize_asset(asset), '资产更新成功')


@assets_bp.route('/<asset_id>', methods=['DELETE'])
@require_role('admin')
@audit_action('delete', 'asset')
def delete_asset(asset_id):
    """删除资产
    ---
    tags:
      - 资产管理
    parameters:
      - name: asset_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: 删除成功
      404:
        description: 资产不存在
    """
    asset = Asset.query.get(asset_id)
    if not asset:
        return not_found('资产不存在')
    
    db.session.delete(asset)
    db.session.commit()
    
    # 通知仪表盘更新
    notify_dashboard_update()
    
    return api_response(None, '资产删除成功')


@assets_bp.route('/<asset_id>/scan', methods=['POST'])
@require_role('analyst', 'admin')
@audit_action('update', 'asset')
def scan_asset(asset_id):
    """扫描资产
    ---
    tags:
      - 资产管理
    parameters:
      - name: asset_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: 扫描完成
      404:
        description: 资产不存在
    """
    asset = Asset.query.get(asset_id)
    if not asset:
        return not_found('资产不存在')
    
    asset.risk_score = random.randint(10, 80)
    asset.last_scan = datetime.now(timezone.utc)
    db.session.commit()
    
    return api_response({
        'status': 'completed',
        'risk_score': asset.risk_score,
        'last_scan': asset.last_scan.isoformat()
    }, '扫描完成')
