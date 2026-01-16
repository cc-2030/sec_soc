import { Router } from 'express';
import OpenAI from 'openai';

const router = Router();

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// AI 日志分析
router.post('/analyze-logs', async (req, res) => {
  const { logs } = req.body;
  
  if (!process.env.OPENAI_API_KEY) {
    // 模拟 AI 分析结果
    return res.json({
      summary: '检测到潜在安全威胁',
      riskLevel: 'medium',
      findings: [
        { type: 'sql_injection', severity: 'high', count: 1, recommendation: '加强输入验证，使用参数化查询' },
        { type: 'abnormal_traffic', severity: 'medium', count: 3, recommendation: '检查防火墙规则，考虑限流' },
      ],
      patterns: ['多次失败登录尝试', '非工作时间访问'],
      recommendations: ['启用双因素认证', '审查访问控制策略', '增加日志监控频率'],
    });
  }

  try {
    const completion = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        { role: 'system', content: '你是一个安全分析专家，分析安全日志并提供威胁评估和建议。返回JSON格式。' },
        { role: 'user', content: `分析以下安全日志，识别威胁模式和异常行为：\n${JSON.stringify(logs, null, 2)}` }
      ],
    });
    res.json({ analysis: completion.choices[0].message.content });
  } catch (error) {
    res.status(500).json({ error: 'AI分析失败' });
  }
});

// AI 威胁检测
router.post('/detect-threats', async (req, res) => {
  const { data } = req.body;
  
  // 模拟威胁检测结果
  res.json({
    threats: [
      { id: 't1', type: 'brute_force', confidence: 0.85, source: '10.0.0.55', target: 'auth-service' },
      { id: 't2', type: 'data_exfiltration', confidence: 0.72, source: '192.168.1.100', target: 'database' },
    ],
    overallRisk: 'medium',
    timestamp: new Date().toISOString(),
  });
});

// AI 安全建议
router.get('/recommendations', async (req, res) => {
  res.json({
    recommendations: [
      { priority: 'high', category: 'access_control', title: '启用多因素认证', description: '为所有管理员账户启用MFA' },
      { priority: 'medium', category: 'network', title: '更新防火墙规则', description: '限制非必要端口的外部访问' },
      { priority: 'low', category: 'monitoring', title: '增加日志保留期', description: '将日志保留期从7天延长至30天' },
    ],
  });
});

export { router as aiRoutes };
