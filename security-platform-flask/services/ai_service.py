# services/ai_service.py
# AI 分析服务
# Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 10.1, 10.2, 10.3, 10.4

import os
import json
import re
from typing import Generator, Optional, Dict, Any, List


class AIService:
    """AI 分析服务
    
    Requirement 9.1: THE AI_Service SHALL 集成 OpenAI API
    """
    
    # 敏感字段列表
    SENSITIVE_FIELDS = [
        'password', 'secret', 'token', 'api_key', 'apikey', 'auth',
        'credential', 'private_key', 'access_key', 'session_id',
        'ssn', 'credit_card', 'card_number', 'cvv', 'pin'
    ]
    
    # IP 地址正则
    IP_PATTERN = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    
    # 邮箱正则
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    def __init__(self):
        self.client = None
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    def _get_client(self):
        """获取 OpenAI 客户端
        
        Requirement 9.1: 初始化 OpenAI 客户端
        """
        if self.client is None:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError('OPENAI_API_KEY 环境变量未设置')
            
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        
        return self.client
    
    def _sanitize_data(self, data: Any) -> Any:
        """脱敏敏感数据
        
        Requirement 9.6: THE AI_Service SHALL 在发送数据前脱敏敏感信息
        """
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                # 检查敏感字段
                if any(sf in key.lower() for sf in self.SENSITIVE_FIELDS):
                    sanitized[key] = '[REDACTED]'
                else:
                    sanitized[key] = self._sanitize_data(value)
            return sanitized
        
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        
        elif isinstance(data, str):
            # 脱敏 IP 地址
            result = self.IP_PATTERN.sub('[IP_REDACTED]', data)
            # 脱敏邮箱
            result = self.EMAIL_PATTERN.sub('[EMAIL_REDACTED]', result)
            return result
        
        return data
    
    def _build_log_analysis_prompt(self, logs: List[Dict]) -> str:
        """构建日志分析提示词
        
        Requirement 9.2: THE AI_Service SHALL 分析安全日志
        """
        sanitized_logs = self._sanitize_data(logs)
        logs_text = json.dumps(sanitized_logs, ensure_ascii=False, indent=2)
        
        return f"""你是一个专业的安全分析师。请分析以下安全日志，识别潜在的安全威胁和异常行为。

安全日志:
{logs_text}

请提供以下分析结果（使用 JSON 格式）:
1. summary: 总体安全态势摘要
2. risk_level: 风险等级 (low/medium/high/critical)
3. findings: 发现的安全问题列表，每个包含:
   - type: 问题类型
   - severity: 严重程度 (low/medium/high/critical)
   - count: 出现次数
   - recommendation: 建议措施
4. patterns: 检测到的异常模式列表
5. recommendations: 整体安全建议列表

请确保返回有效的 JSON 格式。"""
    
    def _build_threat_detection_prompt(self, data: Dict) -> str:
        """构建威胁检测提示词
        
        Requirement 10.1: THE AI_Service SHALL 检测潜在威胁
        """
        sanitized_data = self._sanitize_data(data)
        data_text = json.dumps(sanitized_data, ensure_ascii=False, indent=2)
        
        return f"""你是一个专业的威胁情报分析师。请分析以下安全数据，检测潜在的安全威胁。

安全数据:
{data_text}

请提供以下分析结果（使用 JSON 格式）:
1. threats: 检测到的威胁列表，每个包含:
   - id: 威胁ID (如 t1, t2)
   - type: 威胁类型
   - confidence: 置信度 (0-1)
   - source: 威胁来源
   - target: 攻击目标
   - recommendation: 应对建议
2. overall_risk: 整体风险等级 (low/medium/high/critical)

请确保返回有效的 JSON 格式。"""
    
    def _get_completion(self, prompt: str) -> str:
        """获取 AI 响应
        
        Requirement 9.4: THE AI_Service SHALL 处理 API 调用错误
        """
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的安全分析助手，专注于网络安全威胁分析和日志审计。请始终返回有效的 JSON 格式响应。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            raise AIServiceError(f'AI 分析失败: {str(e)}')
    
    def _stream_completion(self, prompt: str) -> Generator[str, None, None]:
        """流式获取 AI 响应
        
        Requirement 9.3: THE AI_Service SHALL 支持流式响应
        """
        try:
            client = self._get_client()
            stream = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的安全分析助手，专注于网络安全威胁分析和日志审计。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise AIServiceError(f'AI 流式分析失败: {str(e)}')
    
    def analyze_logs(self, logs: List[Dict], stream: bool = False) -> Any:
        """分析安全日志
        
        Requirement 9.2: THE AI_Service SHALL 分析安全日志
        Requirement 9.3: THE AI_Service SHALL 支持流式响应
        
        Args:
            logs: 日志列表
            stream: 是否使用流式响应
            
        Returns:
            分析结果（字典或生成器）
        """
        prompt = self._build_log_analysis_prompt(logs)
        
        if stream:
            return self._stream_completion(prompt)
        
        response = self._get_completion(prompt)
        return self._parse_json_response(response)
    
    def detect_threats(self, data: Dict) -> Dict:
        """检测潜在威胁
        
        Requirement 10.1: THE AI_Service SHALL 检测潜在威胁
        Requirement 10.2: THE AI_Service SHALL 返回威胁置信度
        Requirement 10.3: THE AI_Service SHALL 提供应对建议
        Requirement 10.4: THE AI_Service SHALL 评估整体风险等级
        
        Args:
            data: 安全数据
            
        Returns:
            威胁检测结果
        """
        prompt = self._build_threat_detection_prompt(data)
        response = self._get_completion(prompt)
        return self._parse_json_response(response)
    
    def _parse_json_response(self, response: str) -> Dict:
        """解析 JSON 响应"""
        try:
            # 尝试直接解析
            return json.loads(response)
        except json.JSONDecodeError:
            # 尝试提取 JSON 块
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
            if json_match:
                return json.loads(json_match.group(1))
            
            # 尝试提取花括号内容
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group(0))
            
            # 返回原始响应
            return {'raw_response': response}


class AIServiceError(Exception):
    """AI 服务错误"""
    pass
