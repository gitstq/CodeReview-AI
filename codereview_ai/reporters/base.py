"""
报告生成器基类
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from ..analyzer.base import Issue, IssueSeverity
from ..ai.base import ReviewResult


@dataclass
class AnalysisResult:
    """分析结果"""
    issues: List[Issue] = field(default_factory=list)
    ai_review: Optional[ReviewResult] = None
    files_analyzed: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def get_duration(self) -> float:
        """获取分析耗时（秒）"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    def get_issues_by_severity(self, severity: IssueSeverity) -> List[Issue]:
        """按严重程度获取问题"""
        return [i for i in self.issues if i.severity == severity]
    
    def get_issue_counts(self) -> Dict[str, int]:
        """获取问题统计"""
        counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
            "total": len(self.issues),
        }
        
        for issue in self.issues:
            counts[issue.severity.value] += 1
        
        return counts
    
    def get_issues_by_file(self) -> Dict[str, List[Issue]]:
        """按文件分组获取问题"""
        result: Dict[str, List[Issue]] = {}
        for issue in self.issues:
            if issue.file_path not in result:
                result[issue.file_path] = []
            result[issue.file_path].append(issue)
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "issues": [i.to_dict() for i in self.issues],
            "ai_review": self.ai_review.to_dict() if self.ai_review else None,
            "files_analyzed": self.files_analyzed,
            "duration": self.get_duration(),
            "issue_counts": self.get_issue_counts(),
        }


class BaseReporter(ABC):
    """报告生成器基类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    @property
    @abstractmethod
    def name(self) -> str:
        """报告格式名称"""
        pass
    
    @property
    @abstractmethod
    def extension(self) -> str:
        """文件扩展名"""
        pass
    
    @abstractmethod
    def generate(self, result: AnalysisResult) -> str:
        """
        生成报告
        
        Args:
            result: 分析结果
            
        Returns:
            报告内容字符串
        """
        pass
    
    def save(self, result: AnalysisResult, output_path: str) -> None:
        """保存报告到文件"""
        content = self.generate(result)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def _format_severity(self, severity: IssueSeverity, use_color: bool = False) -> str:
        """格式化严重程度"""
        if use_color:
            reset = "\033[0m"
            return f"{severity.color_code()}{severity.value.upper()}{reset}"
        return severity.value.upper()
