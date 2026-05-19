"""
Anthropic后端
"""
import json
from typing import Optional, Dict, Any
from .base import AIBackend, ReviewResult


class AnthropicBackend(AIBackend):
    """Anthropic Claude API后端"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = self.config.get("api_key", "")
        self.model = self.config.get("model", "claude-3-haiku-20240307")
        self.base_url = self.config.get("base_url", "https://api.anthropic.com/v1")
        self.timeout = self.config.get("timeout", 60)
    
    @property
    def name(self) -> str:
        return "anthropic"
    
    @property
    def description(self) -> str:
        return f"Anthropic Claude API ({self.model})"
    
    def is_available(self) -> bool:
        """检查是否可用"""
        if not self.api_key:
            return False
        
        try:
            import urllib.request
            import urllib.error
            
            req = urllib.request.Request(
                f"{self.base_url}/models",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                },
                method="GET",
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.status == 200
        except Exception:
            return False
    
    def review(self, code: str, file_path: str, context: Optional[Dict[str, Any]] = None) -> ReviewResult:
        """使用Anthropic审查代码"""
        try:
            import urllib.request
            import urllib.error
            
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(code, file_path, context)
            
            data = {
                "model": self.model,
                "max_tokens": 4000,
                "temperature": 0.3,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": user_prompt},
                ],
            }
            
            req = urllib.request.Request(
                f"{self.base_url}/messages",
                data=json.dumps(data).encode("utf-8"),
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
                content = result["content"][0]["text"]
                return self._parse_response(content)
        
        except ImportError:
            return ReviewResult(
                summary="Error: urllib module not available",
                comments=[],
                score=0,
            )
        except Exception as e:
            return ReviewResult(
                summary=f"Anthropic API error: {str(e)}",
                comments=[],
                score=0,
            )
