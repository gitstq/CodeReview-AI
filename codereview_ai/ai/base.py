"""
AI审查后端基类
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import json


class CommentSeverity(Enum):
    """评论严重程度"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
    
    def __str__(self):
        return self.value


@dataclass
class ReviewComment:
    """AI审查评论"""
    severity: CommentSeverity
    category: str
    message: str
    line: int = 0
    suggestion: str = ""
    code_example: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity.value,
            "category": self.category,
            "message": self.message,
            "line": self.line,
            "suggestion": self.suggestion,
            "code_example": self.code_example,
        }


@dataclass
class ReviewResult:
    """AI审查结果"""
    summary: str
    comments: List[ReviewComment] = field(default_factory=list)
    score: int = 0  # 0-100
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "comments": [c.to_dict() for c in self.comments],
            "score": self.score,
            "strengths": self.strengths,
            "improvements": self.improvements,
        }


class AIBackend(ABC):
    """AI后端基类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    @property
    @abstractmethod
    def name(self) -> str:
        """后端名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """后端描述"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查后端是否可用"""
        pass
    
    @abstractmethod
    def review(self, code: str, file_path: str, context: Optional[Dict[str, Any]] = None) -> ReviewResult:
        """
        审查代码
        
        Args:
            code: 代码内容
            file_path: 文件路径
            context: 上下文信息
            
        Returns:
            审查结果
        """
        pass
    
    def _build_system_prompt(self) -> str:
        """构建系统Prompt"""
        return """You are an expert code reviewer with deep knowledge of software engineering best practices, 
security, performance optimization, and clean code principles.

Your task is to review code and provide constructive feedback. Focus on:
1. Logic correctness and edge cases
2. Code readability and maintainability
3. Performance optimization opportunities
4. Security best practices
5. Error handling completeness
6. Code organization and architecture

Provide your review in the following JSON format:
{
    "summary": "Brief overall assessment of the code",
    "score": 85,
    "strengths": ["List of code strengths"],
    "improvements": ["List of improvement suggestions"],
    "comments": [
        {
            "severity": "high|medium|low|info",
            "category": "bug|security|performance|style|maintainability",
            "message": "Description of the issue",
            "line": 42,
            "suggestion": "How to fix it",
            "code_example": "Optional code example"
        }
    ]
}

Be thorough but concise. Only report real issues, not nitpicks."""

    def _build_user_prompt(self, code: str, file_path: str, context: Optional[Dict[str, Any]] = None) -> str:
        """构建用户Prompt"""
        language = self._detect_language(file_path)
        
        prompt = f"""Please review the following {language} code from file `{file_path}`:

```{language}
{code}
```

Provide a detailed code review focusing on:
1. Any bugs or logic errors
2. Security vulnerabilities
3. Performance issues
4. Code readability and maintainability
5. Best practices violations

Return your review in the specified JSON format."""
        
        if context:
            if "related_files" in context:
                prompt += f"\n\nRelated files: {', '.join(context['related_files'])}"
            if "project_type" in context:
                prompt += f"\nProject type: {context['project_type']}"
        
        return prompt
    
    def _detect_language(self, file_path: str) -> str:
        """检测编程语言"""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
        }
        
        for ext, lang in ext_map.items():
            if file_path.endswith(ext):
                return lang
        
        return "code"
    
    def _parse_response(self, response: str) -> ReviewResult:
        """解析AI响应"""
        try:
            # 尝试提取JSON
            json_start = response.find("{")
            json_end = response.rfind("}")
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end + 1]
                data = json.loads(json_str)
            else:
                data = json.loads(response)
            
            comments = []
            for comment_data in data.get("comments", []):
                comments.append(ReviewComment(
                    severity=CommentSeverity(comment_data.get("severity", "info")),
                    category=comment_data.get("category", "maintainability"),
                    message=comment_data.get("message", ""),
                    line=comment_data.get("line", 0),
                    suggestion=comment_data.get("suggestion", ""),
                    code_example=comment_data.get("code_example", ""),
                ))
            
            return ReviewResult(
                summary=data.get("summary", ""),
                comments=comments,
                score=data.get("score", 0),
                strengths=data.get("strengths", []),
                improvements=data.get("improvements", []),
            )
        except Exception as e:
            # 解析失败时返回基本结果
            return ReviewResult(
                summary=f"Failed to parse AI response: {str(e)}\n\nRaw response:\n{response[:500]}",
                comments=[],
                score=0,
            )
