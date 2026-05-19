"""
代码分析器基类
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Dict, Any
import json


class IssueSeverity(Enum):
    """问题严重程度"""
    CRITICAL = "critical"      # 严重问题，必须修复
    HIGH = "high"              # 高风险问题
    MEDIUM = "medium"          # 中等问题
    LOW = "low"                # 低优先级问题
    INFO = "info"              # 信息提示
    
    def __str__(self):
        return self.value
    
    def color_code(self) -> str:
        """获取ANSI颜色代码"""
        colors = {
            IssueSeverity.CRITICAL: "\033[91m",  # 亮红
            IssueSeverity.HIGH: "\033[31m",      # 红
            IssueSeverity.MEDIUM: "\033[93m",    # 黄
            IssueSeverity.LOW: "\033[94m",       # 蓝
            IssueSeverity.INFO: "\033[90m",      # 灰
        }
        return colors.get(self, "\033[0m")
    
    def priority(self) -> int:
        """获取优先级数值，越小越严重"""
        priorities = {
            IssueSeverity.CRITICAL: 0,
            IssueSeverity.HIGH: 1,
            IssueSeverity.MEDIUM: 2,
            IssueSeverity.LOW: 3,
            IssueSeverity.INFO: 4,
        }
        return priorities.get(self, 5)


class IssueCategory(Enum):
    """问题分类"""
    BUG = "bug"                    # 潜在Bug
    SECURITY = "security"          # 安全问题
    PERFORMANCE = "performance"    # 性能问题
    STYLE = "style"                # 代码风格
    MAINTAINABILITY = "maintainability"  # 可维护性
    COMPLEXITY = "complexity"      # 复杂度
    DUPLICATION = "duplication"    # 代码重复
    AI_REVIEW = "ai_review"        # AI审查发现
    
    def __str__(self):
        return self.value
    
    def emoji(self) -> str:
        """获取分类表情符号"""
        emojis = {
            IssueCategory.BUG: "🐛",
            IssueCategory.SECURITY: "🔒",
            IssueCategory.PERFORMANCE: "⚡",
            IssueCategory.STYLE: "🎨",
            IssueCategory.MAINTAINABILITY: "🔧",
            IssueCategory.COMPLEXITY: "📊",
            IssueCategory.DUPLICATION: "📋",
            IssueCategory.AI_REVIEW: "🤖",
        }
        return emojis.get(self, "📌")


@dataclass
class Issue:
    """代码问题"""
    severity: IssueSeverity
    category: IssueCategory
    message: str
    file_path: str
    line: int = 0
    column: int = 0
    end_line: int = 0
    end_column: int = 0
    rule_id: str = ""
    rule_name: str = ""
    description: str = ""
    suggestion: str = ""
    code_snippet: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "severity": self.severity.value,
            "category": self.category.value,
            "message": self.message,
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
            "end_line": self.end_line,
            "end_column": self.end_column,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "description": self.description,
            "suggestion": self.suggestion,
            "code_snippet": self.code_snippet,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Issue":
        """从字典创建"""
        return cls(
            severity=IssueSeverity(data.get("severity", "info")),
            category=IssueCategory(data.get("category", "maintainability")),
            message=data.get("message", ""),
            file_path=data.get("file_path", ""),
            line=data.get("line", 0),
            column=data.get("column", 0),
            end_line=data.get("end_line", 0),
            end_column=data.get("end_column", 0),
            rule_id=data.get("rule_id", ""),
            rule_name=data.get("rule_name", ""),
            description=data.get("description", ""),
            suggestion=data.get("suggestion", ""),
            code_snippet=data.get("code_snippet", ""),
        )
    
    def location_str(self) -> str:
        """获取位置字符串"""
        if self.line > 0:
            if self.column > 0:
                return f"{self.file_path}:{self.line}:{self.column}"
            return f"{self.file_path}:{self.line}"
        return self.file_path
    
    def __str__(self) -> str:
        severity_str = f"[{self.severity.value.upper()}]"
        return f"{severity_str} {self.location_str()}: {self.message}"


class BaseAnalyzer(ABC):
    """代码分析器基类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._issues: List[Issue] = []
    
    @property
    @abstractmethod
    def name(self) -> str:
        """分析器名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """分析器描述"""
        pass
    
    @property
    def supported_languages(self) -> List[str]:
        """支持的语言列表"""
        return ["*"]  # 默认支持所有语言
    
    def can_analyze(self, file_path: str) -> bool:
        """检查是否支持分析指定文件"""
        if "*" in self.supported_languages:
            return True
        
        # 根据文件扩展名判断
        ext = file_path.split(".")[-1].lower() if "." in file_path else ""
        lang_map = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "go": "go",
            "rs": "rust",
            "java": "java",
            "c": "c",
            "cpp": "cpp",
            "h": "c",
            "hpp": "cpp",
        }
        language = lang_map.get(ext, ext)
        return language in self.supported_languages
    
    @abstractmethod
    def analyze(self, file_path: str, content: str) -> List[Issue]:
        """
        分析文件内容
        
        Args:
            file_path: 文件路径
            content: 文件内容
            
        Returns:
            发现的问题列表
        """
        pass
    
    def add_issue(self, issue: Issue) -> None:
        """添加问题"""
        self._issues.append(issue)
    
    def get_issues(self) -> List[Issue]:
        """获取所有问题"""
        return self._issues.copy()
    
    def clear_issues(self) -> None:
        """清空问题列表"""
        self._issues.clear()
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)
