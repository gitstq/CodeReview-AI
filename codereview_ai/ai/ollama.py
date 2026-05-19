"""
Ollama本地模型后端
"""
import json
from typing import Optional, Dict, Any
from .base import AIBackend, ReviewResult


class OllamaBackend(AIBackend):
    """Ollama本地LLM后端"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.model = self.config.get("model", "codellama")
        self.base_url = self.config.get("base_url", "http://localhost:11434")
        self.timeout = self.config.get("timeout", 120)
    
    @property
    def name(self) -> str:
        return "ollama"
    
    @property
    def description(self) -> str:
        return f"Ollama Local LLM ({self.model})"
    
    def is_available(self) -> bool:
        """检查Ollama服务是否可用"""
        try:
            import urllib.request
            import urllib.error
            
            req = urllib.request.Request(
                f"{self.base_url}/api/tags",
                method="GET",
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except Exception:
            return False
    
    def review(self, code: str, file_path: str, context: Optional[Dict[str, Any]] = None) -> ReviewResult:
        """使用Ollama本地模型审查代码"""
        try:
            import urllib.request
            import urllib.error
            
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(code, file_path, context)
            
            # Ollama使用简单的prompt格式
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            data = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 4000,
                },
            }
            
            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=json.dumps(data).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
                content = result.get("response", "")
                return self._parse_response(content)
        
        except ImportError:
            return ReviewResult(
                summary="Error: urllib module not available",
                comments=[],
                score=0,
            )
        except Exception as e:
            return ReviewResult(
                summary=f"Ollama error: {str(e)}. Make sure Ollama is running locally.",
                comments=[],
                score=0,
            )
    
    def list_models(self) -> list:
        """列出可用的本地模型"""
        try:
            import urllib.request
            
            req = urllib.request.Request(
                f"{self.base_url}/api/tags",
                method="GET",
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                result = json.loads(response.read().decode("utf-8"))
                return [model["name"] for model in result.get("models", [])]
        except Exception:
            return []
