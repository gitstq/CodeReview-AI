"""
代码风格分析器
检查代码风格问题
"""
import ast
import re
from typing import List, Optional, Dict, Any
from .base import BaseAnalyzer, Issue, IssueSeverity, IssueCategory


class StyleAnalyzer(BaseAnalyzer):
    """代码风格分析器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.max_line_length = self.get_config("max_line_length", 100)
        self.indent_size = self.get_config("indent_size", 4)
    
    @property
    def name(self) -> str:
        return "style"
    
    @property
    def description(self) -> str:
        return "检查代码风格问题（行长度、命名规范等）"
    
    @property
    def supported_languages(self) -> List[str]:
        return ["python"]
    
    def analyze(self, file_path: str, content: str) -> List[Issue]:
        """分析代码风格"""
        self.clear_issues()
        
        if not file_path.endswith(".py"):
            return self.get_issues()
        
        lines = content.split("\n")
        
        # 检查行长度
        self._check_line_length(file_path, lines)
        
        # 检查尾随空格
        self._check_trailing_whitespace(file_path, lines)
        
        # 检查空行
        self._check_blank_lines(file_path, lines)
        
        # 检查命名规范
        self._check_naming_conventions(file_path, content)
        
        # 检查导入规范
        self._check_imports(file_path, content)
        
        return self.get_issues()
    
    def _check_line_length(self, file_path: str, lines: List[str]) -> None:
        """检查行长度"""
        for i, line in enumerate(lines, 1):
            if len(line) > self.max_line_length:
                # 检查是否是注释或字符串
                stripped = line.lstrip()
                if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                    severity = IssueSeverity.LOW
                else:
                    severity = IssueSeverity.MEDIUM
                
                self.add_issue(Issue(
                    severity=severity,
                    category=IssueCategory.STYLE,
                    message=f"行长度超过 {self.max_line_length} 字符 ({len(line)} 字符)",
                    file_path=file_path,
                    line=i,
                    column=self.max_line_length,
                    rule_id="STYLE001",
                    rule_name="line-too-long",
                    description=f"该行包含 {len(line)} 个字符，超过了 {self.max_line_length} 的限制",
                    suggestion="考虑换行或使用括号进行隐式续行"
                ))
    
    def _check_trailing_whitespace(self, file_path: str, lines: List[str]) -> None:
        """检查尾随空格"""
        for i, line in enumerate(lines, 1):
            if line.endswith(" ") or line.endswith("\t"):
                self.add_issue(Issue(
                    severity=IssueSeverity.LOW,
                    category=IssueCategory.STYLE,
                    message="行尾存在多余空格",
                    file_path=file_path,
                    line=i,
                    rule_id="STYLE002",
                    rule_name="trailing-whitespace",
                    description="行尾存在尾随空格",
                    suggestion="删除行尾多余空格"
                ))
    
    def _check_blank_lines(self, file_path: str, lines: List[str]) -> None:
        """检查文件末尾空行"""
        if lines and lines[-1].strip() == "":
            # 文件以空行结尾是正常的
            pass
        elif lines and lines[-1]:
            # 文件没有以换行符结尾
            self.add_issue(Issue(
                severity=IssueSeverity.INFO,
                category=IssueCategory.STYLE,
                message="文件末尾缺少换行符",
                file_path=file_path,
                line=len(lines),
                rule_id="STYLE003",
                rule_name="missing-final-newline",
                description="文件没有以换行符结尾",
                suggestion="在文件末尾添加一个空行"
            ))
        
        # 检查连续多个空行
        blank_count = 0
        for i, line in enumerate(lines, 1):
            if line.strip() == "":
                blank_count += 1
                if blank_count > 2:
                    self.add_issue(Issue(
                        severity=IssueSeverity.LOW,
                        category=IssueCategory.STYLE,
                        message="连续空行过多",
                        file_path=file_path,
                        line=i,
                        rule_id="STYLE004",
                        rule_name="too-many-blank-lines",
                        description="存在超过2个连续空行",
                        suggestion="删除多余的空行，保持代码紧凑"
                    ))
            else:
                blank_count = 0
    
    def _check_naming_conventions(self, file_path: str, content: str) -> None:
        """检查命名规范"""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return
        
        for node in ast.walk(tree):
            # 检查函数名 (snake_case)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_name = node.name
                if not self._is_snake_case(func_name) and not func_name.startswith("__"):
                    self.add_issue(Issue(
                        severity=IssueSeverity.LOW,
                        category=IssueCategory.STYLE,
                        message=f"函数名 '{func_name}' 不符合 snake_case 规范",
                        file_path=file_path,
                        line=node.lineno,
                        rule_id="STYLE005",
                        rule_name="invalid-function-name",
                        description=f"函数名 '{func_name}' 应该使用 snake_case 命名规范",
                        suggestion=f"建议改为 '{self._to_snake_case(func_name)}'"
                    ))
                
                # 检查参数名
                for arg in node.args.args:
                    if not self._is_snake_case(arg.arg) and arg.arg != "self":
                        self.add_issue(Issue(
                            severity=IssueSeverity.LOW,
                            category=IssueCategory.STYLE,
                            message=f"参数名 '{arg.arg}' 不符合 snake_case 规范",
                            file_path=file_path,
                            line=node.lineno,
                            rule_id="STYLE006",
                            rule_name="invalid-argument-name",
                            description=f"参数名 '{arg.arg}' 应该使用 snake_case 命名规范",
                            suggestion=f"建议改为 '{self._to_snake_case(arg.arg)}'"
                        ))
            
            # 检查类名 (PascalCase)
            elif isinstance(node, ast.ClassDef):
                class_name = node.name
                if not self._is_pascal_case(class_name):
                    self.add_issue(Issue(
                        severity=IssueSeverity.LOW,
                        category=IssueCategory.STYLE,
                        message=f"类名 '{class_name}' 不符合 PascalCase 规范",
                        file_path=file_path,
                        line=node.lineno,
                        rule_id="STYLE007",
                        rule_name="invalid-class-name",
                        description=f"类名 '{class_name}' 应该使用 PascalCase 命名规范",
                        suggestion=f"建议改为 '{self._to_pascal_case(class_name)}'"
                    ))
            
            # 检查常量 (UPPER_CASE)
            elif isinstance(node, ast.NameConstant):
                pass  # Python 3.8+ 中已弃用
            
            # 检查变量赋值
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        # 模块级别的常量应该大写
                        # 这里简化处理，只检查明显的大写常量
                        if var_name.isupper() and len(var_name) > 1:
                            # 这是正确的常量命名
                            pass
    
    def _check_imports(self, file_path: str, content: str) -> None:
        """检查导入规范"""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return
        
        imports = []
        from_imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append((alias.name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    from_imports.append((module, alias.name, node.lineno))
        
        # 检查通配符导入
        for module, name, lineno in from_imports:
            if name == "*":
                self.add_issue(Issue(
                    severity=IssueSeverity.MEDIUM,
                    category=IssueCategory.STYLE,
                    message=f"使用 'from {module} import *' 通配符导入",
                    file_path=file_path,
                    line=lineno,
                    rule_id="STYLE008",
                    rule_name="wildcard-import",
                    description=f"通配符导入会污染命名空间，难以追踪符号来源",
                    suggestion=f"改为显式导入: from {module} import specific_name"
                ))
        
        # 检查未使用的导入 (简化版，仅检查明显情况)
        # 完整实现需要更复杂的分析
    
    def _is_snake_case(self, name: str) -> bool:
        """检查是否为snake_case"""
        if not name:
            return True
        return name == name.lower() and " " not in name
    
    def _is_pascal_case(self, name: str) -> bool:
        """检查是否为PascalCase"""
        if not name:
            return True
        return name[0].isupper() and "_" not in name and " " not in name
    
    def _to_snake_case(self, name: str) -> str:
        """转换为snake_case"""
        # 处理camelCase
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append("_")
            result.append(char.lower())
        return "".join(result)
    
    def _to_pascal_case(self, name: str) -> str:
        """转换为PascalCase"""
        # 处理snake_case
        words = name.split("_")
        return "".join(word.capitalize() for word in words if word)
