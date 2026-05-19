"""
🔍 CodeReview-AI
轻量级AI驱动代码审查与质量分析引擎

A lightweight AI-powered code review and quality analysis engine.
"""

__version__ = "1.0.0"
__author__ = "CodeReview-AI Team"
__license__ = "MIT"

from .analyzer.base import BaseAnalyzer, Issue, IssueSeverity, IssueCategory
from .ai.base import AIBackend, ReviewResult
from .reporters.base import BaseReporter, AnalysisResult

__all__ = [
    "BaseAnalyzer",
    "Issue",
    "IssueSeverity",
    "IssueCategory",
    "AIBackend",
    "ReviewResult",
    "BaseReporter",
    "AnalysisResult",
]
