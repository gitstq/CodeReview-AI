"""
重复代码检测器
检测代码重复
"""
import ast
import hashlib
from typing import List, Optional, Dict, Any, Set, Tuple
from collections import defaultdict
from .base import BaseAnalyzer, Issue, IssueSeverity, IssueCategory


class DuplicateAnalyzer(BaseAnalyzer):
    """重复代码检测器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.min_duplicate_lines = self.get_config("min_duplicate_lines", 6)
        self.similarity_threshold = self.get_config("similarity_threshold", 0.8)
    
    @property
    def name(self) -> str:
        return "duplicate"
    
    @property
    def description(self) -> str:
        return "检测重复代码块"
    
    @property
    def supported_languages(self) -> List[str]:
        return ["python"]
    
    def analyze(self, file_path: str, content: str) -> List[Issue]:
        """分析代码重复"""
        self.clear_issues()
        
        if not file_path.endswith(".py"):
            return self.get_issues()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return self.get_issues()
        
        lines = content.split("\n")
        
        # 检测完全相同的代码块
        self._detect_exact_duplicates(file_path, lines)
        
        # 检测函数级别的重复
        self._detect_function_duplicates(file_path, tree, lines)
        
        return self.get_issues()
    
    def _detect_exact_duplicates(self, file_path: str, lines: List[str]) -> None:
        """检测完全相同的代码块"""
        # 使用滑动窗口检测重复
        block_hashes: Dict[str, List[Tuple[int, int]]] = defaultdict(list)
        
        for start_line in range(len(lines)):
            for block_size in range(self.min_duplicate_lines, min(self.min_duplicate_lines + 5, len(lines) - start_line + 1)):
                end_line = start_line + block_size
                block = "\n".join(lines[start_line:end_line])
                
                # 规范化代码块（去除空白和注释）
                normalized = self._normalize_code_block(block)
                if len(normalized) < 20:  # 跳过太短的块
                    continue
                
                block_hash = hashlib.md5(normalized.encode()).hexdigest()
                block_hashes[block_hash].append((start_line + 1, end_line))
        
        # 报告重复
        reported_blocks = set()
        for block_hash, locations in block_hashes.items():
            if len(locations) > 1:
                # 检查是否已经报告过（避免重复报告子集）
                if any(self._is_subset(loc, reported) for loc in locations for reported in reported_blocks):
                    continue
                
                for start, end in locations:
                    reported_blocks.add((start, end))
                
                location_str = ", ".join([f"{s}-{e}" for s, e in locations])
                self.add_issue(Issue(
                    severity=IssueSeverity.LOW,
                    category=IssueCategory.DUPLICATION,
                    message=f"发现重复代码块（{len(locations)}处）: 行 {location_str}",
                    file_path=file_path,
                    line=locations[0][0],
                    rule_id="DUP001",
                    rule_name="duplicate-code-block",
                    description=f"发现{len(locations)}处完全相同的代码块，每块{locations[0][1] - locations[0][0]}行",
                    suggestion="考虑提取重复代码为函数或类，减少维护成本",
                    code_snippet="\n".join(lines[locations[0][0]-1:locations[0][1]])
                ))
    
    def _detect_function_duplicates(self, file_path: str, tree: ast.AST, lines: List[str]) -> None:
        """检测相似函数"""
        functions: List[Tuple[str, ast.FunctionDef, str]] = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # 提取函数签名和主体的简化表示
                func_sig = self._extract_function_signature(node)
                functions.append((node.name, node, func_sig))
        
        # 检测相似函数
        checked_pairs = set()
        for i, (name1, node1, sig1) in enumerate(functions):
            for j, (name2, node2, sig2) in enumerate(functions):
                if i >= j:
                    continue
                
                pair_key = tuple(sorted([name1, name2]))
                if pair_key in checked_pairs:
                    continue
                checked_pairs.add(pair_key)
                
                similarity = self._calculate_similarity(sig1, sig2)
                
                if similarity >= self.similarity_threshold:
                    self.add_issue(Issue(
                        severity=IssueSeverity.LOW,
                        category=IssueCategory.DUPLICATION,
                        message=f"函数 '{name1}' 和 '{name2}' 相似度过高 ({similarity:.0%})",
                        file_path=file_path,
                        line=node1.lineno,
                        rule_id="DUP002",
                        rule_name="similar-functions",
                        description=f"两个函数的实现相似度为{similarity:.0%}，可能存在代码重复",
                        suggestion="考虑合并相似函数，使用参数化或策略模式消除重复",
                    ))
    
    def _normalize_code_block(self, block: str) -> str:
        """规范化代码块用于比较"""
        lines = block.split("\n")
        normalized = []
        
        for line in lines:
            # 去除行首空格
            stripped = line.lstrip()
            # 跳过空行和注释
            if not stripped or stripped.startswith("#"):
                continue
            # 去除行尾注释
            if "#" in stripped:
                stripped = stripped[:stripped.index("#")].rstrip()
            normalized.append(stripped)
        
        return "\n".join(normalized)
    
    def _is_subset(self, loc1: Tuple[int, int], loc2: Tuple[int, int]) -> bool:
        """检查loc1是否是loc2的子集"""
        return loc1[0] >= loc2[0] and loc1[1] <= loc2[1]
    
    def _extract_function_signature(self, node: ast.FunctionDef) -> str:
        """提取函数的简化签名"""
        parts = []
        
        # 函数名
        parts.append(node.name)
        
        # 参数数量
        arg_count = len(node.args.args) + len(node.args.kwonlyargs)
        if node.args.vararg:
            arg_count += 1
        if node.args.kwarg:
            arg_count += 1
        parts.append(f"args:{arg_count}")
        
        # 语句类型统计
        stmt_types = defaultdict(int)
        for stmt in ast.walk(node):
            stmt_types[type(stmt).__name__] += 1
        
        # 关键语句
        for stmt_type in ["If", "For", "While", "Try", "With", "Return"]:
            if stmt_types.get(stmt_type, 0) > 0:
                parts.append(f"{stmt_type}:{stmt_types[stmt_type]}")
        
        return "|".join(parts)
    
    def _calculate_similarity(self, sig1: str, sig2: str) -> float:
        """计算两个签名的相似度"""
        parts1 = set(sig1.split("|"))
        parts2 = set(sig2.split("|"))
        
        if not parts1 or not parts2:
            return 0.0
        
        intersection = parts1 & parts2
        union = parts1 | parts2
        
        return len(intersection) / len(union)
