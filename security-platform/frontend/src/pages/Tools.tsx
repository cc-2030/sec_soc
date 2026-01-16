import { useEffect, useState } from 'react';
import { Play, RefreshCw } from 'lucide-react';

interface Tool {
  id: string;
  name: string;
  category: string;
  description: string;
  status: string;
  lastRun?: string;
}

export default function Tools() {
  const [tools, setTools] = useState<Tool[]>([]);
  const [running, setRunning] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/tools').then(r => r.json()).then(setTools);
  }, []);

  const runTool = async (id: string) => {
    setRunning(id);
    await fetch(`/api/tools/${id}/run`, { method: 'POST' });
    const updated = await fetch('/api/tools').then(r => r.json());
    setTools(updated);
    setRunning(null);
  };

  return (
    <div>
      <div className="page-header">
        <h2>安全工具</h2>
        <p>管理和运行安全扫描工具</p>
      </div>

      <div className="grid grid-2">
        {tools.map(tool => (
          <div key={tool.id} className="card tool-card">
            <div className="tool-info">
              <h4>{tool.name}</h4>
              <p>{tool.description}</p>
              <div style={{ marginTop: 8 }}>
                <span className={`badge ${tool.status === 'active' ? 'active' : 'inactive'}`}>{tool.status}</span>
                {tool.lastRun && <span style={{ marginLeft: 10, fontSize: 12, color: '#64748b' }}>上次运行: {new Date(tool.lastRun).toLocaleString()}</span>}
              </div>
            </div>
            <button className="btn btn-primary" onClick={() => runTool(tool.id)} disabled={running === tool.id}>
              {running === tool.id ? <RefreshCw size={16} className="spin" /> : <Play size={16} />}
              {running === tool.id ? ' 运行中...' : ' 运行'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
