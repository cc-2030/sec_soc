import { useEffect, useState } from 'react';
import { Filter } from 'lucide-react';

interface Log {
  id: string;
  timestamp: string;
  level: string;
  source: string;
  message: string;
  ip?: string;
}

export default function Logs() {
  const [logs, setLogs] = useState<Log[]>([]);
  const [filter, setFilter] = useState({ level: '', source: '' });

  useEffect(() => {
    const params = new URLSearchParams();
    if (filter.level) params.set('level', filter.level);
    if (filter.source) params.set('source', filter.source);
    fetch(`/api/logs?${params}`).then(r => r.json()).then(setLogs);
  }, [filter]);

  return (
    <div>
      <div className="page-header">
        <h2>日志分析</h2>
        <p>查看和分析安全日志</p>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
          <Filter size={18} color="#64748b" />
          <select className="btn btn-secondary" value={filter.level} onChange={e => setFilter(f => ({ ...f, level: e.target.value }))}>
            <option value="">所有级别</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
            <option value="critical">Critical</option>
          </select>
          <select className="btn btn-secondary" value={filter.source} onChange={e => setFilter(f => ({ ...f, source: e.target.value }))}>
            <option value="">所有来源</option>
            <option value="firewall">Firewall</option>
            <option value="ids">IDS</option>
            <option value="auth">Auth</option>
          </select>
        </div>
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>级别</th>
              <th>时间</th>
              <th>来源</th>
              <th>消息</th>
              <th>IP</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.id}>
                <td><span className={`log-level ${log.level}`} /> {log.level}</td>
                <td>{new Date(log.timestamp).toLocaleString()}</td>
                <td>{log.source}</td>
                <td>{log.message}</td>
                <td>{log.ip || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
