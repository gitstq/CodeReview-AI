"""
配置管理模块
"""
import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


DEFAULT_CONFIG = {
    # 分析器配置
    "analyzers": {
        "complexity": {
            "enabled": True,
            "max_cyclomatic_complexity": 10,
            "max_cognitive_complexity": 15,
            "max_function_lines": 50,
            "max_file_lines": 500,
            "max_parameters": 5,
        },
        "style": {
            "enabled": True,
            "max_line_length": 100,
            "indent_size": 4,
        },
        "security": {
            "enabled": True,
        },
        "duplicate": {
            "enabled": True,
            "min_duplicate_lines": 6,
            "similarity_threshold": 0.8,
        },
    },
    
    # AI配置
    "ai": {
        "enabled": False,
        "backend": "openai",  # openai, anthropic, ollama
        "model": "gpt-4o-mini",
        "api_key": "",
        "base_url": "",
        "timeout": 60,
    },
    
    # 报告配置
    "report": {
        "format": "console",  # console, markdown, json, html, sarif
        "output": "",
        "color": True,
        "show_code": True,
    },
    
    # 文件过滤
    "include": ["**/*.py"],
    "exclude": [
        "**/venv/**",
        "**/.venv/**",
        "**/env/**",
        "**/__pycache__/**",
        "**/.git/**",
        "**/node_modules/**",
        "**/build/**",
        "**/dist/**",
        "**/*.min.js",
        "**/*.min.css",
    ],
    
    # 忽略规则
    "ignore": {
        "rules": [],
        "files": [],
        "paths": [],
    },
}


class Config:
    """配置类"""
    
    CONFIG_FILE_NAMES = [
        ".codereview-ai.yml",
        ".codereview-ai.yaml",
        "codereview-ai.yml",
        "codereview-ai.yaml",
        ".reviewrc.yml",
        ".reviewrc.yaml",
    ]
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        self._config = self._deep_merge(DEFAULT_CONFIG.copy(), config_dict or {})
    
    @classmethod
    def load(cls, path: Optional[str] = None) -> "Config":
        """
        从文件加载配置
        
        Args:
            path: 配置文件路径，如果为None则自动查找
        
        Returns:
            Config对象
        """
        config_dict = {}
        
        if path:
            # 加载指定路径
            if os.path.isfile(path):
                config_dict = cls._load_yaml(path)
        else:
            # 自动查找配置文件
            for config_name in cls.CONFIG_FILE_NAMES:
                if os.path.isfile(config_name):
                    config_dict = cls._load_yaml(config_name)
                    break
        
        # 从环境变量加载
        env_config = cls._load_from_env()
        config_dict = cls._deep_merge(config_dict, env_config)
        
        return cls(config_dict)
    
    @classmethod
    def init_config_file(cls, path: str = ".codereview-ai.yml") -> str:
        """初始化配置文件"""
        config_content = """# CodeReview-AI 配置文件
# 文档: https://github.com/yourusername/codereview-ai

# 分析器配置
analyzers:
  complexity:
    enabled: true
    max_cyclomatic_complexity: 10
    max_cognitive_complexity: 15
    max_function_lines: 50
    max_file_lines: 500
    max_parameters: 5
  
  style:
    enabled: true
    max_line_length: 100
    indent_size: 4
  
  security:
    enabled: true
  
  duplicate:
    enabled: true
    min_duplicate_lines: 6
    similarity_threshold: 0.8

# AI审查配置 (可选)
ai:
  enabled: false
  backend: openai  # openai, anthropic, ollama
  model: gpt-4o-mini
  # api_key: your-api-key-here
  # base_url: https://api.openai.com/v1
  timeout: 60

# 报告配置
report:
  format: console  # console, markdown, json, html, sarif
  # output: report.html
  color: true
  show_code: true

# 文件包含/排除模式
include:
  - "**/*.py"

exclude:
  - "**/venv/**"
  - "**/__pycache__/**"
  - "**/.git/**"
  - "**/node_modules/**"

# 忽略规则
ignore:
  rules: []  # 忽略的规则ID列表
  files: []  # 忽略的文件列表
  paths: []  # 忽略的路径列表
"""
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(config_content)
        
        return path
    
    @staticmethod
    def _load_yaml(path: str) -> Dict[str, Any]:
        """加载YAML文件"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    
    @staticmethod
    def _load_from_env() -> Dict[str, Any]:
        """从环境变量加载配置"""
        config = {}
        
        # AI配置
        if os.getenv("CODEREVIEW_AI_API_KEY"):
            config.setdefault("ai", {})["api_key"] = os.getenv("CODEREVIEW_AI_API_KEY")
        
        if os.getenv("CODEREVIEW_AI_BACKEND"):
            config.setdefault("ai", {})["backend"] = os.getenv("CODEREVIEW_AI_BACKEND")
        
        if os.getenv("CODEREVIEW_AI_MODEL"):
            config.setdefault("ai", {})["model"] = os.getenv("CODEREVIEW_AI_MODEL")
        
        if os.getenv("OPENAI_API_KEY"):
            config.setdefault("ai", {})["api_key"] = os.getenv("OPENAI_API_KEY")
        
        if os.getenv("ANTHROPIC_API_KEY"):
            config.setdefault("ai", {})["api_key"] = os.getenv("ANTHROPIC_API_KEY")
            config.setdefault("ai", {})["backend"] = "anthropic"
        
        return config
    
    @staticmethod
    def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并字典"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Config._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项"""
        keys = key.split(".")
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self._config.copy()
    
    def is_analyzer_enabled(self, analyzer_name: str) -> bool:
        """检查分析器是否启用"""
        return self.get(f"analyzers.{analyzer_name}.enabled", True)
    
    def get_analyzer_config(self, analyzer_name: str) -> Dict[str, Any]:
        """获取分析器配置"""
        return self.get(f"analyzers.{analyzer_name}", {})
    
    def get_ai_config(self) -> Dict[str, Any]:
        """获取AI配置"""
        return self.get("ai", {})
    
    def get_report_config(self) -> Dict[str, Any]:
        """获取报告配置"""
        return self.get("report", {})
