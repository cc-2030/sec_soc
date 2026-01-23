# routes/vulnerabilities.py
# 漏洞管理 API
# Requirements: 2.2, 14.5

from flask import Blueprint, request
from middleware.rbac import require_role
from middleware.response import api_response, paginated_response, not_found
from services.audit_service import audit_action
from schemas.vulnerability import VulnerabilityCreateSchema, VulnerabilityUpdateSchema
from schemas.common import validate_request
from extensions import db
from models import Vulnerability
from datetime import datetime, timezone
import uuid

vulns_bp = Blueprint('vulnerabilities', __name__)


def serialize_vulnerability(vuln):
    """序列化漏洞对象"""
    return {
        'id': vuln.id,
        'cve_id': vuln.cve_id,
        'title': vuln.title,
        'description': vuln.description,
        'severity': vuln.severity,
        'cvss_score': vuln.cvss_score,
        'status': vuln.status,
        'remediation': vuln.remediation,
        'references': vuln.references or [],
        'discovered_at': vuln.discovered_at.isoformat() if vuln.discovered_at else None,
        'fixed_at': vuln.fixed_at.isoformat() if vuln.fixed_at else None,
        'created_at': vuln.created_at.isoformat() if vuln.created_at else None,
        'updated_at': vuln.updated_at.isoformat() if vuln.updated_at else None,
        'affected_assets': len(vuln.assets) if vuln.assets else 0
    }


@vulns_bp.route('/', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_vulnerabilities():
    """获取漏洞列表
    ---
    tags:
      - 漏洞管理
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
      - name: page_size
        in: query
        type: integer
        default: 20
      - name: status
        in: query
        type: string
        description: 状态筛选 (open, in_progress, fixed, accepted)
      - name: severity
        in: query
        type: string
        description: 严重程度筛选
    responses:
      200:
        description: 漏洞列表（分页）
    """
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 20, type=int), 100)
    
    query = Vulnerability.query
    
    if request.args.get('status'):
        query = query.filter(Vulnerability.status == request.args.get('status'))
    if request.args.get('severity'):
        query = query.filter(Vulnerability.severity == request.args.get('severity'))
    
    query = query.order_by(Vulnerability.discovered_at.desc())
    
    total = query.count()
    vulns = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return paginated_response(
        items=[serialize_vulnerability(v) for v in vulns],
        total=total,
        page=page,
        page_size=page_size
    )


@vulns_bp.route('/<vuln_id>', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_vulnerability(vuln_id):
    """获取漏洞详情"""
    vuln = Vulnerability.query.get(vuln_id)
    if not vuln:
        return not_found('漏洞不存在')
    return api_response(serialize_vulnerability(vuln))


@vulns_bp.route('/', methods=['POST'])
@require_role('analyst', 'admin')
@validate_request(VulnerabilityCreateSchema)
@audit_action('create', 'vulnerability')
def create_vulnerability(validated_data):
    """创建漏洞记录"""
    vuln = Vulnerability(
        cve_id=validated_data.get('cve_id'),
        title=validated_data['title'],
        description=validated_data.get('description'),
        severity=validated_data['severity'],
        cvss_score=validated_data.get('cvss_score'),
        status=validated_data.get('status', 'open'),
        remediation=validated_data.get('remediation'),
        references=validated_data.get('references', []),
        discovered_at=datetime.now(timezone.utc)
    )
    
    db.session.add(vuln)
    db.session.commit()
    
    return api_response(serialize_vulnerability(vuln), '漏洞创建成功', 201)


@vulns_bp.route('/<vuln_id>', methods=['PATCH'])
@require_role('analyst', 'admin')
@validate_request(VulnerabilityUpdateSchema)
@audit_action('update', 'vulnerability')
def update_vulnerability(validated_data, vuln_id):
    """更新漏洞状态"""
    vuln = Vulnerability.query.get(vuln_id)
    if not vuln:
        return not_found('漏洞不存在')
    
    for key, value in validated_data.items():
        if hasattr(vuln, key) and value is not None:
            setattr(vuln, key, value)
    
    if validated_data.get('status') == 'fixed':
        vuln.fixed_at = datetime.now(timezone.utc)
    
    vuln.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    
    return api_response(serialize_vulnerability(vuln), '漏洞更新成功')


@vulns_bp.route('/<vuln_id>', methods=['DELETE'])
@require_role('admin')
@audit_action('delete', 'vulnerability')
def delete_vulnerability(vuln_id):
    """删除漏洞"""
    vuln = Vulnerability.query.get(vuln_id)
    if not vuln:
        return not_found('漏洞不存在')
    
    db.session.delete(vuln)
    db.session.commit()
    
    return api_response(None, '漏洞删除成功')


@vulns_bp.route('/affected-assets', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_affected_assets():
    """获取受影响资产统计"""
    from models import Asset
    from sqlalchemy import func
    
    # 统计每个资产的漏洞数量
    stats = db.session.query(
        Asset.name,
        func.count(Vulnerability.id).label('vuln_count')
    ).join(
        Vulnerability.assets
    ).group_by(Asset.id).order_by(func.count(Vulnerability.id).desc()).limit(10).all()
    
    return api_response([
        {'name': name, 'vuln_count': count}
        for name, count in stats
    ])


@vulns_bp.route('/scan', methods=['POST'])
@require_role('analyst', 'admin')
@audit_action('create', 'vulnerability_scan')
def start_scan():
    """启动漏洞扫描"""
    return api_response({
        'status': 'started',
        'scan_id': str(uuid.uuid4())
    }, '扫描已启动')
