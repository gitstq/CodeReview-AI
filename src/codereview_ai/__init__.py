"""
CodeReview-AI: Lightweight AI Code Review Assistant
轻量级AI代码审查助手

A zero-dependency CLI tool for automated code review using multiple LLM backends.
支持多LLM后端的零依赖自动化代码审查CLI工具。

Author: gitstq
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "gitstq"
__license__ = "MIT"

from .core import CodeReviewer
from .analyzers import StaticAnalyzer, PatternMatcher
from .reporters import ConsoleReporter, JSONReporter, MarkdownReporter

__all__ = [
    "CodeReviewer",
    "StaticAnalyzer",
    "PatternMatcher",
    "ConsoleReporter",
    "JSONReporter",
    "MarkdownReporter",
]