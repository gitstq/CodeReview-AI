"""
复杂度分析器
分析代码复杂度指标
"""
import ast
import re
from typing import List, Optional, Dict, Any, Set
from .base import BaseAnalyzer, Issue, IssueSeverity, IssueCategory


class ComplexityAnalyzer(BaseAnalyzer):
    """代码复杂度分析器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.max_cyclomatic_complexity = self.get_config("max_cyclomatic_complexity", 10)
        self.max_cognitive_complexity = self.get_config("max_cognitive_complexity", 15)
        self.max_function_lines = self.get_config("max_function_lines", 50)
        self.max_file_lines = self.get_config("max_file_lines", 500)
        self.max_parameters = self.get_config("max_parameters", 5)
    
    @property
    def name(self) -> str:
        return "complexity"
    
    @property
    def description(self) -> str:
        return "分析代码复杂度指标（圈复杂度、认知复杂度、函数长度等）"
    
    @property
    def supported_languages(self) -> List[str]:
        return ["python"]
    
    def analyze(self, file_path: str, content: str) -> List[Issue]:
        """分析Python文件复杂度"""
        self.clear_issues()
        
        if not file_path.endswith(".py"):
            return self.get_issues()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return self.get_issues()
        
        lines = content.split("\n")
        
        # 检查文件长度
        self._check_file_length(file_path, len(lines))
        
        # 遍历AST节点
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._analyze_function(file_path, node, lines)
        
        return self.get_issues()
    
    def _check_file_length(self, file_path: str, line_count: int) -> None:
        """检查文件长度"""
        if line_count > self.max_file_lines:
            self.add_issue(Issue(
                severity=IssueSeverity.MEDIUM,
                category=IssueCategory.COMPLEXITY,
                message=f"文件过长 ({line_count} 行)，建议拆分为多个小文件",
                file_path=file_path,
                line=1,
                rule_id="COMPLEX001",
                rule_name="file-too-long",
                description=f"文件包含 {line_count} 行代码，超过了建议的 {self.max_file_lines} 行限制",
                suggestion="考虑将大文件拆分为多个职责单一的小文件，提高可维护性"
            ))
    
    def _analyze_function(self, file_path: str, node: ast.FunctionDef, lines: List[str]) -> None:
        """分析函数复杂度"""
        func_name = node.name
        func_start = node.lineno
        func_end = node.end_lineno or func_start
        func_lines = func_end - func_start + 1
        
        # 检查函数长度
        if func_lines > self.max_function_lines:
            self.add_issue(Issue(
                severity=IssueSeverity.MEDIUM,
                category=IssueCategory.COMPLEXITY,
                message=f"函数 '{func_name}' 过长 ({func_lines} 行)",
                file_path=file_path,
                line=func_start,
                rule_id="COMPLEX002",
                rule_name="function-too-long",
                description=f"函数包含 {func_lines} 行代码，超过了建议的 {self.max_function_lines} 行限制",
                suggestion="考虑将长函数拆分为多个小函数，每个函数只做一件事"
            ))
        
        # 检查参数数量
        param_count = len(node.args.args) + len(node.args.kwonlyargs)
        if node.args.vararg:
            param_count += 1
        if node.args.kwarg:
            param_count += 1
        
        if param_count > self.max_parameters:
            self.add_issue(Issue(
                severity=IssueSeverity.LOW,
                category=IssueCategory.COMPLEXITY,
                message=f"函数 '{func_name}' 参数过多 ({param_count} 个)",
                file_path=file_path,
                line=func_start,
                rule_id="COMPLEX003",
                rule_name="too-many-parameters",
                description=f"函数有 {param_count} 个参数，超过了建议的 {self.max_parameters} 个限制",
                suggestion="考虑使用配置对象或数据类来封装相关参数"
            ))
        
        # 计算圈复杂度
        cyclomatic = self._calculate_cyclomatic_complexity(node)
        if cyclomatic > self.max_cyclomatic_complexity:
            self.add_issue(Issue(
                severity=IssueSeverity.HIGH if cyclomatic > 20 else IssueSeverity.MEDIUM,
                category=IssueCategory.COMPLEXITY,
                message=f"函数 '{func_name}' 圈复杂度过高 ({cyclomatic})",
                file_path=file_path,
                line=func_start,
                rule_id="COMPLEX004",
                rule_name="high-cyclomatic-complexity",
                description=f"函数圈复杂度为 {cyclomatic}，超过了建议的 {self.max_cyclomatic_complexity}",
                suggestion="考虑简化条件逻辑，使用卫语句或策略模式降低复杂度"
            ))
        
        # 计算认知复杂度
        cognitive = self._calculate_cognitive_complexity(node)
        if cognitive > self.max_cognitive_complexity:
            self.add_issue(Issue(
                severity=IssueSeverity.MEDIUM,
                category=IssueCategory.COMPLEXITY,
                message=f"函数 '{func_name}' 认知复杂度过高 ({cognitive})",
                file_path=file_path,
                line=func_start,
                rule_id="COMPLEX005",
                rule_name="high-cognitive-complexity",
                description=f"函数认知复杂度为 {cognitive}，超过了建议的 {self.max_cognitive_complexity}",
                suggestion="考虑提取嵌套逻辑为独立函数，提高代码可读性"
            ))
    
    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """
        计算圈复杂度
        基于McCabe复杂度：1 + 决策点数量
        """
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
                # 检查是否有and/or
                if isinstance(child, ast.If) and isinstance(child.test, (ast.BoolOp,)):
                    complexity += len(child.test.values) - 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With):
                complexity += len(child.items)
            elif isinstance(child, ast.comprehension):
                complexity += 1
                if child.ifs:
                    complexity += len(child.ifs)
            elif isinstance(child, ast.Assert):
                complexity += 1
        
        return complexity
    
    def _calculate_cognitive_complexity(self, node: ast.AST, nesting_level: int = 0) -> int:
        """
        计算认知复杂度
        基于嵌套深度加权计算
        """
        complexity = 0
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1 + nesting_level
                complexity += self._calculate_cognitive_complexity(child, nesting_level + 1)
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1 + nesting_level
                complexity += self._calculate_cognitive_complexity(child, nesting_level + 1)
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # 不进入嵌套函数/类
                pass
            else:
                complexity += self._calculate_cognitive_complexity(child, nesting_level)
        
        return complexity
