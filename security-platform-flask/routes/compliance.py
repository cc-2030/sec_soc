# routes/compliance.py
# 合规管理 API
# Requirements: 14.5

from flask import Blueprint, request
from middleware.rbac import require_role
from middleware.response import api_response, paginated_response, not_found
from services.audit_service import audit_action
from extensions import db
from models import ComplianceFramework, ComplianceCheck
from datetime import datetime, timezone
import uuid

compliance_bp = Blueprint('compliance', __name__)


def serialize_framework(framework):
    """序列化合规框架"""
    checks = framework.checks
    passed = sum(1 for c in checks if c.status == 'passed')
    total = len(checks)
    
    return {
        'id': framework.id,
        'name': framework.name,
        'description': framework.description,
        'total_controls': framework.total_controls or total,
        'passed': passed,
        'score': int(passed / total * 100) if total > 0 else 0,
        'created_at': framework.created_at.isoformat() if framework.created_at else None
    }


def serialize_check(check):
    """序列化合规检查"""
    return {
        'id': check.id,
        'framework_id': check.framework_id,
        'control_id': check.control_id,
        'title': check.title,
        'description': check.description,
        'status': check.status,
        'last_check': check.last_check.isoformat() if check.last_check else None,
        'evidence': check.evidence,
        'remediation': check.remediation
    }


@compliance_bp.route('/frameworks', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_frameworks():
    """获取合规框架列表"""
    frameworks = ComplianceFramework.query.all()
    return api_response([serialize_framework(f) for f in frameworks])


@compliance_bp.route('/frameworks/<framework_id>', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_framework(framework_id):
    """获取合规框架详情"""
    framework = ComplianceFramework.query.get(framework_id)
    if not framework:
        return not_found('合规框架不存在')
    return api_response(serialize_framework(framework))


@compliance_bp.route('/frameworks/<framework_id>/checks', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_framework_checks(framework_id):
    """获取框架的检查项"""
    framework = ComplianceFramework.query.get(framework_id)
    if not framework:
        return not_found('合规框架不存在')
    
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 20, type=int), 100)
    
    query = ComplianceCheck.query.filter_by(framework_id=framework_id)
    
    if request.args.get('status'):
        query = query.filter(ComplianceCheck.status == request.args.get('status'))
    
    total = query.count()
    checks = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return paginated_response(
        items=[serialize_check(c) for c in checks],
        total=total,
        page=page,
        page_size=page_size
    )


@compliance_bp.route('/checks/<check_id>', methods=['PATCH'])
@require_role('analyst', 'admin')
@audit_action('update', 'compliance_check')
def update_check(check_id):
    """更新检查项状态"""
    check = ComplianceCheck.query.get(check_id)
    if not check:
        return not_found('检查项不存在')
    
    data = request.get_json() or {}
    
    if 'status' in data:
        check.status = data['status']
    if 'evidence' in data:
        check.evidence = data['evidence']
    if 'remediation' in data:
        check.remediation = data['remediation']
    
    check.last_check = datetime.now(timezone.utc)
    db.session.commit()
    
    return api_response(serialize_check(check), '检查项更新成功')


@compliance_bp.route('/remediations', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_remediations():
    """获取待整改项"""
    checks = ComplianceCheck.query.filter(
        ComplianceCheck.status.in_(['failed', 'pending'])
    ).all()
    
    return api_response([{
        'id': c.id,
        'title': c.title,
        'framework': c.framework.name if c.framework else None,
        'priority': 'high' if c.status == 'failed' else 'medium',
        'status': 'open' if c.status == 'failed' else 'pending',
        'remediation': c.remediation
    } for c in checks])


@compliance_bp.route('/check', methods=['POST'])
@require_role('analyst', 'admin')
@audit_action('execute', 'compliance_check')
def run_check():
    """执行合规检查"""
    return api_response({
        'status': 'started',
        'check_id': str(uuid.uuid4())
    }, '合规检查已启动')
