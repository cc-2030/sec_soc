import { useEffect, useState } from 'react';
import { Clock, Target, TrendingUp, Shield } from 'lucide-react';

interface Operations {
  mttr: number;
  mttd: number;
  incidentsThisMonth: number;
  complianceScore: number;
  patchStatus: { upToDate: number; pending: number; critical: number };
}

interface Assets {
  servers: { total: number; healthy: number; warning: number; critical: number };
  endpoints: { total: number; healthy: number; warning: number; critical: number };
  applications: { total: number; healthy: number; warning: number; critical: number };
}

export default function Operations() {
  const [ops, setOps] = useState<Operations | null>(null);
  const [assets, setAssets] = useState<Assets | null>(null);

  useEffect(() => {
    fetch('/api/dashboard/operations').then(r => r.json()).then(setOps);
    fetch('/api/dashboard/assets').then(r => r.json()).then(setAssets);
  }, []);

  const AssetBar = ({ data }: { data: { total: number; healthy: number; warning: number; critical: number } }) => (
    <div style={{ display: 'flex', height: 8, borderRadius: 4, overflow: 'hidden', background: '#334155' }}>
      <div style={{ width: `${(data.healthy / data.total) * 100}%`, background: '#22c55e' }} />
      <div style={{ width: `${(data.warning / data.total) * 100}%`, background: '#eab308' }} />
      <div style={{ width: `${(data.critical / data.total) * 100}%`, background: '#ef4444' }} />
    </div>
  );

  return (
    <div>
      <div className="page-header">
        <h2>安全运营</h2>
        <p>运营指标和资产状态</p>
      </div>

      <div className="grid grid-4" style={{ marginBottom: 20 }}>
        <div className="card">
          <div className="card-header"><span className="card-title">平均检测时间</span><Target color="#38bdf8" /></div>
          <div className="stat-value blue">{ops?.mttd || '-'}<span style={{ fontSize: 16, color: '#64748b' }}> 分钟</span></div>
        </div>
        <div className="card">
          <div className="card-header"><span className="card-title">平均修复时间</span><Clock color="#eab308" /></div>
          <div className="stat-value yellow">{ops?.mttr || '-'}<span style={{ fontSize: 16, color: '#64748b' }}> 分钟</span></div>
        </div>
        <div className="card">
          <div className="card-header"><span className="card-title">本月事件</span><TrendingUp color="#ef4444" /></div>
          <div className="stat-value red">{ops?.incidentsThisMonth || '-'}</div>
        </div>
        <div className="card">
          <div className="card-header"><span className="card-title">合规评分</span><Shield color="#22c55e" /></div>
          <div className="stat-value green">{ops?.complianceScore || '-'}%</div>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <div className="card-header"><span className="card-title">资产健康状态</span></div>
          {assets && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {(['servers', 'endpoints', 'applications'] as const).map(type => (
                <div key={type}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <span style={{ textTransform: 'capitalize' }}>{type === 'servers' ? '服务器' : type === 'endpoints' ? '终端' : '应用'}</span>
                    <span style={{ color: '#64748b' }}>{assets[type].total} 总计</span>
                  </div>
                  <AssetBar data={assets[type]} />
                  <div style={{ display: 'flex', gap: 16, marginTop: 8, fontSize: 12 }}>
                    <span style={{ color: '#22c55e' }}>● 健康 {assets[type].healthy}</span>
                    <span style={{ color: '#eab308' }}>● 警告 {assets[type].warning}</span>
                    <span style={{ color: '#ef4444' }}>● 严重 {assets[type].critical}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-header"><span className="card-title">补丁状态</span></div>
          {ops && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #334155' }}>
                <span>已更新</span>
                <span style={{ color: '#22c55e', fontWeight: 600 }}>{ops.patchStatus.upToDate}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #334155' }}>
                <span>待更新</span>
                <span style={{ color: '#eab308', fontWeight: 600 }}>{ops.patchStatus.pending}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0' }}>
                <span>紧急补丁</span>
                <span style={{ color: '#ef4444', fontWeight: 600 }}>{ops.patchStatus.critical}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
