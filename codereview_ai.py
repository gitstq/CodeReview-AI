#!/usr/bin/env python3
"""
CodeReview-AI: Lightweight AI Code Review Assistant
轻量级AI代码审查助手 - 单文件入口点

Usage:
    python codereview_ai.py review <file_or_directory>
    python codereview_ai.py diff [base_ref]
    python codereview_ai.py config
"""

import sys
from src.codereview_ai.cli import main

if __name__ == '__main__':
    sys.exit(main())