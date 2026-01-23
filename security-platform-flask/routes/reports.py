# routes/reports.py
# 报表管理 API
# Requirements: 14.5

from flask import Blueprint, request
from middleware.rbac import require_role
from middleware.response import api_response, paginated_response, not_found
from services.audit_service import audit_action
import uuid
from datetime import datetime, timedelta, timezone

reports_bp = Blueprint('reports', __name__)

# 报表历史（模拟数据，后续可迁移到数据库）
reports_history = [
    {'id': 'rpt-1', 'name': '2024年1月安全月报', 'type': 'monthly', 'created_at': (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(), 'size': '2.3 MB', 'status': 'completed'},
    {'id': 'rpt-2', 'name': '第3周安全周报', 'type': 'weekly', 'created_at': (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(), 'size': '856 KB', 'status': 'completed'},
    {'id': 'rpt-3', 'name': '勒索软件事件报告', 'type': 'incident', 'created_at': (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(), 'size': '1.1 MB', 'status': 'completed'},
    {'id': 'rpt-4', 'name': '等保合规检查报告', 'type': 'compliance', 'created_at': (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(), 'size': '3.5 MB', 'status': 'completed'},
]


@reports_bp.route('/history', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_history():
    """获取报表历史"""
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 20, type=int), 100)
    
    report_type = request.args.get('type')
    
    filtered = reports_history
    if report_type:
        filtered = [r for r in reports_history if r['type'] == report_type]
    
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    
    return paginated_response(
        items=filtered[start:end],
        total=total,
        page=page,
        page_size=page_size
    )


@reports_bp.route('/generate/<report_type>', methods=['POST'])
@require_role('analyst', 'admin')
@audit_action('create', 'report')
def generate_report(report_type):
    """生成报表"""
    type_names = {
        'monthly': '月报',
        'weekly': '周报',
        'incident': '事件报告',
        'compliance': '合规报告',
        'vulnerability': '漏洞报告',
        'asset': '资产报告'
    }
    
    report = {
        'id': f'rpt-{uuid.uuid4().hex[:8]}',
        'name': f'{datetime.now(timezone.utc).strftime("%Y-%m-%d")} {type_names.get(report_type, report_type)}',
        'type': report_type,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'size': '1.2 MB',
        'status': 'completed'
    }
    reports_history.insert(0, report)
    
    return api_response(report, '报表生成成功', 201)


@reports_bp.route('/<report_id>', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_report(report_id):
    """获取报表详情"""
    report = next((r for r in reports_history if r['id'] == report_id), None)
    if not report:
        return not_found('报表不存在')
    return api_response(report)


@reports_bp.route('/<report_id>', methods=['DELETE'])
@require_role('admin')
@audit_action('delete', 'report')
def delete_report(report_id):
    """删除报表"""
    global reports_history
    report = next((r for r in reports_history if r['id'] == report_id), None)
    if not report:
        return not_found('报表不存在')
    
    reports_history = [r for r in reports_history if r['id'] != report_id]
    return api_response(None, '报表删除成功')


@reports_bp.route('/download/<report_id>', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def download_report(report_id):
    """获取报表下载链接"""
    report = next((r for r in reports_history if r['id'] == report_id), None)
    if not report:
        return not_found('报表不存在')
    
    return api_response({
        'url': f'/static/reports/{report_id}.pdf',
        'filename': f"{report['name']}.pdf"
    })


@reports_bp.route('/templates', methods=['GET'])
@require_role('viewer', 'analyst', 'admin')
def get_templates():
    """获取报表模板"""
    return api_response([
        {'id': 'tpl-1', 'name': '安全月报模板', 'type': 'monthly', 'description': '包含安全态势、事件统计、漏洞分析等'},
        {'id': 'tpl-2', 'name': '安全周报模板', 'type': 'weekly', 'description': '本周安全事件和处置情况汇总'},
        {'id': 'tpl-3', 'name': '事件报告模板', 'type': 'incident', 'description': '单个安全事件的详细分析报告'},
        {'id': 'tpl-4', 'name': '合规检查报告', 'type': 'compliance', 'description': '合规检查结果和整改建议'},
    ])
