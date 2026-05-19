"""
安全分析器
检测潜在安全漏洞
"""
import ast
import re
from typing import List, Optional, Dict, Any, Set
from .base import BaseAnalyzer, Issue, IssueSeverity, IssueCategory


class SecurityAnalyzer(BaseAnalyzer):
    """安全漏洞分析器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.dangerous_functions: Set[str] = {
            "eval", "exec", "compile", "__import__",
        }
        self.dangerous_modules: Set[str] = {
            "pickle", "marshal", "shelve",
        }
        self.sql_patterns = [
            r"SELECT\s+.*\s+FROM",
            r"INSERT\s+INTO",
            r"UPDATE\s+.*\s+SET",
            r"DELETE\s+FROM",
        ]
    
    @property
    def name(self) -> str:
        return "security"
    
    @property
    def description(self) -> str:
        return "检测潜在安全漏洞（SQL注入、代码注入、硬编码密钥等）"
    
    @property
    def supported_languages(self) -> List[str]:
        return ["python"]
    
    def analyze(self, file_path: str, content: str) -> List[Issue]:
        """分析安全漏洞"""
        self.clear_issues()
        
        if not file_path.endswith(".py"):
            return self.get_issues()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return self.get_issues()
        
        lines = content.split("\n")
        
        # 检查危险函数调用
        self._check_dangerous_functions(file_path, tree, lines)
        
        # 检查SQL注入
        self._check_sql_injection(file_path, content, lines)
        
        # 检查硬编码密钥
        self._check_hardcoded_secrets(file_path, content, lines)
        
        # 检查不安全的反序列化
        self._check_unsafe_deserialization(file_path, tree, lines)
        
        # 检查命令注入
        self._check_command_injection(file_path, tree, lines)
        
        return self.get_issues()
    
    def _check_dangerous_functions(self, file_path: str, tree: ast.AST, lines: List[str]) -> None:
        """检查危险函数调用"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                if func_name in self.dangerous_functions:
                    self.add_issue(Issue(
                        severity=IssueSeverity.HIGH,
                        category=IssueCategory.SECURITY,
                        message=f"检测到危险函数调用: {func_name}()",
                        file_path=file_path,
                        line=node.lineno,
                        rule_id="SEC001",
                        rule_name="dangerous-function-call",
                        description=f"使用 {func_name}() 可能导致代码注入攻击",
                        suggestion="避免使用eval/exec，改用更安全的替代方案如ast.literal_eval或json.loads",
                        code_snippet=lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                    ))
    
    def _check_sql_injection(self, file_path: str, content: str, lines: List[str]) -> None:
        """检查SQL注入风险"""
        # 查找字符串拼接或格式化构建SQL的情况
        sql_functions = ["execute", "executemany", "cursor", "query"]
        
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            
            # 检查是否是SQL相关代码行
            is_sql_context = any(func in line_lower for func in sql_functions)
            
            if is_sql_context:
                # 检查字符串格式化
                if "%" in line and any(pattern in line_upper for pattern in ["SELECT", "INSERT", "UPDATE", "DELETE"] for line_upper in [line.upper()]):
                    if not line.strip().startswith("#"):
                        self.add_issue(Issue(
                            severity=IssueSeverity.HIGH,
                            category=IssueCategory.SECURITY,
                            message="可能存在SQL注入风险（字符串格式化）",
                            file_path=file_path,
                            line=i,
                            rule_id="SEC002",
                            rule_name="sql-injection-risk",
                            description="使用字符串格式化构建SQL查询可能导致SQL注入攻击",
                            suggestion="使用参数化查询（prepared statements）代替字符串拼接",
                            code_snippet=line.strip()
                        ))
                
                # 检查f-string
                if "f\"" in line or "f'" in line:
                    if any(pattern in line.upper() for pattern in ["SELECT", "INSERT", "UPDATE", "DELETE"]):
                        if not line.strip().startswith("#"):
                            self.add_issue(Issue(
                                severity=IssueSeverity.HIGH,
                                category=IssueCategory.SECURITY,
                                message="可能存在SQL注入风险（f-string格式化）",
                                file_path=file_path,
                                line=i,
                                rule_id="SEC003",
                                rule_name="sql-injection-fstring",
                                description="使用f-string构建SQL查询可能导致SQL注入攻击",
                                suggestion="使用参数化查询（prepared statements）代替f-string",
                                code_snippet=line.strip()
                            ))
                
                # 检查.format()
                if ".format(" in line_lower:
                    if any(pattern in line.upper() for pattern in ["SELECT", "INSERT", "UPDATE", "DELETE"]):
                        if not line.strip().startswith("#"):
                            self.add_issue(Issue(
                                severity=IssueSeverity.HIGH,
                                category=IssueCategory.SECURITY,
                                message="可能存在SQL注入风险（format格式化）",
                                file_path=file_path,
                                line=i,
                                rule_id="SEC004",
                                rule_name="sql-injection-format",
                                description="使用format()构建SQL查询可能导致SQL注入攻击",
                                suggestion="使用参数化查询（prepared statements）代替format()",
                                code_snippet=line.strip()
                            ))
    
    def _check_hardcoded_secrets(self, file_path: str, content: str, lines: List[str]) -> None:
        """检查硬编码密钥"""
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "password"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "secret"),
            (r'token\s*=\s*["\'][^"\']+["\']', "token"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "api_key"),
            (r'apikey\s*=\s*["\'][^"\']+["\']', "apikey"),
            (r'access_token\s*=\s*["\'][^"\']+["\']', "access_token"),
            (r'private_key\s*=\s*["\'][^"\']+["\']', "private_key"),
            (r'aws_access_key_id\s*=\s*["\'][^"\']+["\']', "aws_access_key_id"),
            (r'aws_secret_access_key\s*=\s*["\'][^"\']+["\']', "aws_secret_access_key"),
        ]
        
        for i, line in enumerate(lines, 1):
            # 跳过注释行
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            
            for pattern, secret_type in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # 排除常见假阳性
                    if any(fake in line.lower() for fake in [
                        "example", "placeholder", "your_", "xxx", "***",
                        "changeme", "admin", "test", "demo", "sample"
                    ]):
                        continue
                    
                    self.add_issue(Issue(
                        severity=IssueSeverity.CRITICAL,
                        category=IssueCategory.SECURITY,
                        message=f"检测到硬编码的 {secret_type}",
                        file_path=file_path,
                        line=i,
                        rule_id="SEC005",
                        rule_name="hardcoded-secret",
                        description=f"代码中硬编码了{secret_type}，存在严重的安全风险",
                        suggestion="使用环境变量或密钥管理服务来存储敏感信息",
                        code_snippet=line.strip()
                    ))
    
    def _check_unsafe_deserialization(self, file_path: str, tree: ast.AST, lines: List[str]) -> None:
        """检查不安全的反序列化"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                
                # 检查pickle.load/pickle.loads
                if func_name in ["pickle.load", "pickle.loads", "cPickle.load", "cPickle.loads"]:
                    self.add_issue(Issue(
                        severity=IssueSeverity.CRITICAL,
                        category=IssueCategory.SECURITY,
                        message=f"检测到不安全的反序列化: {func_name}()",
                        file_path=file_path,
                        line=node.lineno,
                        rule_id="SEC006",
                        rule_name="unsafe-deserialization",
                        description="使用pickle反序列化不可信数据可能导致任意代码执行",
                        suggestion="使用json等安全格式替代pickle，或对数据进行签名验证",
                        code_snippet=lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                    ))
                
                # 检查yaml.load (不安全的默认加载器)
                if func_name in ["yaml.load"]:
                    self.add_issue(Issue(
                        severity=IssueSeverity.HIGH,
                        category=IssueCategory.SECURITY,
                        message="检测到不安全的YAML加载",
                        file_path=file_path,
                        line=node.lineno,
                        rule_id="SEC007",
                        rule_name="unsafe-yaml-load",
                        description="yaml.load()默认使用不安全的加载器，可能导致任意代码执行",
                        suggestion="使用yaml.safe_load()代替yaml.load()",
                        code_snippet=lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                    ))
    
    def _check_command_injection(self, file_path: str, tree: ast.AST, lines: List[str]) -> None:
        """检查命令注入"""
        dangerous_shell_funcs = [
            "os.system", "os.popen", "os.popen2", "os.popen3", "os.popen4",
            "subprocess.call", "subprocess.run", "subprocess.Popen",
            "commands.getoutput", "commands.getstatusoutput",
        ]
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                
                if func_name in dangerous_shell_funcs:
                    # 检查是否使用了shell=True
                    shell_true = False
                    has_variable = False
                    
                    for keyword in node.keywords:
                        if keyword.arg == "shell":
                            if isinstance(keyword.value, ast.Constant) and keyword.value.value == True:
                                shell_true = True
                    
                    # 检查参数是否包含变量
                    if node.args:
                        for arg in node.args:
                            if isinstance(arg, (ast.Name, ast.BinOp, ast.JoinedStr)):
                                has_variable = True
                                break
                    
                    if shell_true and has_variable:
                        self.add_issue(Issue(
                            severity=IssueSeverity.CRITICAL,
                            category=IssueCategory.SECURITY,
                            message=f"检测到命令注入风险: {func_name}()",
                            file_path=file_path,
                            line=node.lineno,
                            rule_id="SEC008",
                            rule_name="command-injection",
                            description="使用shell=True并拼接变量可能导致命令注入攻击",
                            suggestion="避免使用shell=True，使用参数列表代替字符串命令",
                            code_snippet=lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                        ))
    
    def _get_call_name(self, node: ast.Call) -> str:
        """获取函数调用名称"""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return ""
