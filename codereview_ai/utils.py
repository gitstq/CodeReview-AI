"""
通用工具模块
"""
import os
import fnmatch
from typing import List, Iterator
from pathlib import Path


def find_files(
    paths: List[str],
    include_patterns: List[str] = None,
    exclude_patterns: List[str] = None,
) -> Iterator[str]:
    """
    查找匹配的文件
    
    Args:
        paths: 要搜索的路径列表
        include_patterns: 包含模式列表 (glob格式)
        exclude_patterns: 排除模式列表 (glob格式)
    
    Yields:
        匹配的文件路径
    """
    include_patterns = include_patterns or ["**/*"]
    exclude_patterns = exclude_patterns or []
    
    for path in paths:
        if os.path.isfile(path):
            # 如果是文件，直接检查
            if _should_include(path, include_patterns, exclude_patterns):
                yield path
        elif os.path.isdir(path):
            # 如果是目录，递归查找
            for root, dirs, files in os.walk(path):
                # 过滤目录
                dirs[:] = [
                    d for d in dirs
                    if not any(fnmatch.fnmatch(os.path.join(root, d), p) for p in exclude_patterns)
                    and d not in [".git", "__pycache__", "node_modules", "venv", ".venv", "env"]
                ]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    if _should_include(file_path, include_patterns, exclude_patterns):
                        yield file_path


def _should_include(file_path: str, include_patterns: List[str], exclude_patterns: List[str]) -> bool:
    """检查文件是否应该被包含"""
    # 首先检查排除模式
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
            return False
    
    # 然后检查包含模式
    for pattern in include_patterns:
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
            return True
    
    return False


def read_file(file_path: str) -> str:
    """读取文件内容"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        # 尝试其他编码
        try:
            with open(file_path, "r", encoding="gbk") as f:
                return f.read()
        except Exception:
            return ""
    except Exception:
        return ""


def truncate_string(s: str, max_length: int, suffix: str = "...") -> str:
    """截断字符串"""
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def format_duration(seconds: float) -> str:
    """格式化持续时间"""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"


def pluralize(count: int, singular: str, plural: str = None) -> str:
    """复数化"""
    if plural is None:
        plural = singular + "s"
    return f"{count} {singular if count == 1 else plural}"


class Colors:
    """ANSI颜色代码"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    @classmethod
    def disable(cls):
        """禁用颜色"""
        for attr in dir(cls):
            if not attr.startswith("_") and isinstance(getattr(cls, attr), str):
                setattr(cls, attr, "")


def print_colored(text: str, color: str, bold: bool = False) -> None:
    """打印彩色文本"""
    prefix = ""
    if bold:
        prefix += Colors.BOLD
    prefix += color
    print(f"{prefix}{text}{Colors.RESET}")
