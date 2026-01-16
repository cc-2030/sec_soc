import { Router } from 'express';

const router = Router();

interface SecurityTool {
  id: string;
  name: string;
  category: string;
  description: string;
  status: 'active' | 'inactive' | 'error';
  lastRun?: string;
}

const tools: SecurityTool[] = [
  { id: 'vuln-scanner', name: '漏洞扫描器', category: 'scanning', description: '自动扫描系统漏洞', status: 'active', lastRun: new Date().toISOString() },
  { id: 'port-scanner', name: '端口扫描', category: 'scanning', description: '扫描开放端口', status: 'active' },
  { id: 'malware-detector', name: '恶意软件检测', category: 'detection', description: '检测恶意文件和行为', status: 'active' },
  { id: 'traffic-analyzer', name: '流量分析', category: 'monitoring', description: '实时网络流量分析', status: 'active' },
  { id: 'log-collector', name: '日志采集器', category: 'collection', description: '多源日志统一采集', status: 'active' },
];

// 获取工具列表
router.get('/', (req, res) => {
  res.json(tools);
});

// 执行工具
router.post('/:id/run', (req, res) => {
  const tool = tools.find(t => t.id === req.params.id);
  if (!tool) return res.status(404).json({ error: '工具不存在' });
  
  tool.lastRun = new Date().toISOString();
  // 模拟执行结果
  res.json({
    toolId: tool.id,
    status: 'completed',
    startTime: tool.lastRun,
    results: { findings: Math.floor(Math.random() * 10), scanned: Math.floor(Math.random() * 1000) }
  });
});

// 获取工具状态
router.get('/:id/status', (req, res) => {
  const tool = tools.find(t => t.id === req.params.id);
  if (!tool) return res.status(404).json({ error: '工具不存在' });
  res.json({ id: tool.id, status: tool.status, lastRun: tool.lastRun });
});

export { router as toolRoutes };
