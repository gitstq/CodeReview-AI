"""
Static analysis and pattern matching modules
静态分析和模式匹配模块
"""

import re
import ast
from typing import List, Dict, Optional, Tuple, Any
from .core import CodeIssue, Severity, IssueType


class PatternMatcher:
    """Pattern-based code analysis"""

    # Security patterns
    SECURITY_PATTERNS = {
        'hardcoded_password': {
            'pattern': r'(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
            'severity': Severity.CRITICAL,
            'message': 'Hardcoded password detected',
            'suggestion': 'Use environment variables or secure vault for credentials',
        },
        'hardcoded_secret': {
            'pattern': r'(api_key|apikey|secret|token)\s*=\s*["\'][^"\']{10,}["\']',
            'severity': Severity.CRITICAL,
            'message': 'Hardcoded secret/key detected',
            'suggestion': 'Use environment variables or secure vault for secrets',
        },
        'sql_injection': {
            'pattern': r'execute\s*\(\s*["\'].*%s.*["\']\s*%',
            'severity': Severity.CRITICAL,
            'message': 'Potential SQL injection vulnerability',
            'suggestion': 'Use parameterized queries or ORM',
        },
        'eval_usage': {
            'pattern': r'\beval\s*\(',
            'severity': Severity.HIGH,
            'message': 'Dangerous eval() usage detected',
            'suggestion': 'Use ast.literal_eval for safe evaluation or json.loads for JSON',
        },
        'exec_usage': {
            'pattern': r'\bexec\s*\(',
            'severity': Severity.HIGH,
            'message': 'Dangerous exec() usage detected',
            'suggestion': 'Avoid exec() - it can execute arbitrary code',
        },
        'pickle_load': {
            'pattern': r'pickle\.load',
            'severity': Severity.HIGH,
            'message': 'Unsafe pickle.load() usage',
            'suggestion': 'Use json or msgpack for deserialization, or verify pickle data integrity',
        },
        'yaml_load': {
            'pattern': r'yaml\.load\s*\(',
            'severity': Severity.HIGH,
            'message': 'Unsafe yaml.load() usage',
            'suggestion': 'Use yaml.safe_load() instead',
        },
        'subprocess_shell': {
            'pattern': r'subprocess\.(call|run|check_output)\s*\([^)]*shell\s*=\s*True',
            'severity': Severity.HIGH,
            'message': 'Subprocess with shell=True is dangerous',
            'suggestion': 'Avoid shell=True, pass command as list instead',
        },
        'http_url': {
            'pattern': r'http://[^\s"\']+',
            'severity': Severity.MEDIUM,
            'message': 'Insecure HTTP URL detected',
            'suggestion': 'Use HTTPS instead of HTTP',
        },
        'disable_verification': {
            'pattern': r'(verify|ssl_verify)\s*=\s*False',
            'severity': Severity.HIGH,
            'message': 'SSL/TLS verification disabled',
            'suggestion': 'Never disable SSL verification in production',
        },
        'debug_mode': {
            'pattern': r'debug\s*=\s*True',
            'severity': Severity.MEDIUM,
            'message': 'Debug mode enabled',
            'suggestion': 'Ensure debug mode is disabled in production',
        },
        'temp_file_race': {
            'pattern': r'(mktemp|tmpnam)',
            'severity': Severity.MEDIUM,
            'message': 'Insecure temporary file creation',
            'suggestion': 'Use tempfile.mkstemp() or tempfile.NamedTemporaryFile()',
        },
    }

    # Performance patterns
    PERFORMANCE_PATTERNS = {
        'list_in_loop': {
            'pattern': r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(',
            'severity': Severity.LOW,
            'message': 'Inefficient loop pattern',
            'suggestion': 'Use enumerate() or direct iteration instead of range(len())',
        },
        'string_concat_in_loop': {
            'pattern': r'for\s+.*:\s*\n\s+\w+\s*\+=\s*["\']',
            'severity': Severity.LOW,
            'message': 'String concatenation in loop',
            'suggestion': 'Use list.append() and str.join() for better performance',
        },
        'recompile_in_loop': {
            'pattern': r'for\s+.*:\s*\n\s+re\.compile',
            'severity': Severity.MEDIUM,
            'message': 'Regex compilation inside loop',
            'suggestion': 'Compile regex patterns outside of loops',
        },
        'global_variable': {
            'pattern': r'^\w+\s*=\s*[^=].*$',
            'severity': Severity.LOW,
            'message': 'Global variable usage',
            'suggestion': 'Consider encapsulating in a class or function',
        },
    }

    # Bug patterns
    BUG_PATTERNS = {
        'bare_except': {
            'pattern': r'except\s*:',
            'severity': Severity.HIGH,
            'message': 'Bare except clause catches all exceptions including KeyboardInterrupt',
            'suggestion': 'Use except Exception: or specify the exact exception type',
        },
        'empty_except': {
            'pattern': r'except[^:]*:\s*\n\s*pass',
            'severity': Severity.MEDIUM,
            'message': 'Empty exception handler',
            'suggestion': 'Handle the exception properly or remove the try-except',
        },
        'mutable_default': {
            'pattern': r'def\s+\w+\s*\([^)]*=\s*(\[\s*\]|\{\s*\})',
            'severity': Severity.HIGH,
            'message': 'Mutable default argument',
            'suggestion': 'Use None as default and initialize mutable object inside function',
        },
        'is_comparison': {
            'pattern': r'\w+\s+is\s+["\']',
            'severity': Severity.LOW,
            'message': 'Using "is" for string comparison',
            'suggestion': 'Use == for value comparison, "is" is for identity',
        },
        'hasattr_getattr': {
            'pattern': r'if\s+hasattr\s*\([^)]+\):\s*\n\s+\w+\s*=\s*getattr',
            'severity': Severity.LOW,
            'message': 'Redundant hasattr/getattr pattern',
            'suggestion': 'Use getattr(obj, attr, default) instead',
        },
        'unreachable_code': {
            'pattern': r'return\s+.+\n\s+\w+',
            'severity': Severity.MEDIUM,
            'message': 'Potential unreachable code after return',
            'suggestion': 'Remove unreachable code or fix the control flow',
        },
    }

    # Style patterns
    STYLE_PATTERNS = {
        'line_too_long': {
            'pattern': r'.{120,}',
            'severity': Severity.LOW,
            'message': 'Line exceeds 120 characters',
            'suggestion': 'Break the line into multiple lines',
        },
        'trailing_whitespace': {
            'pattern': r'[ \t]+$',
            'severity': Severity.INFO,
            'message': 'Trailing whitespace',
            'suggestion': 'Remove trailing whitespace',
        },
        'mixed_tabs_spaces': {
            'pattern': r'^(\s*\t\s* )|( \s*\t)',
            'severity': Severity.LOW,
            'message': 'Mixed tabs and spaces',
            'suggestion': 'Use consistent indentation (preferably 4 spaces)',
        },
        'multiple_blank_lines': {
            'pattern': r'\n\n\n+',
            'severity': Severity.INFO,
            'message': 'Multiple consecutive blank lines',
            'suggestion': 'Use at most 2 consecutive blank lines',
        },
        'missing_final_newline': {
            'pattern': r'[^\n]$',
            'severity': Severity.INFO,
            'message': 'File does not end with a newline',
            'suggestion': 'Add a final newline to the file',
        },
    }

    # Maintainability patterns
    MAINTAINABILITY_PATTERNS = {
        'todo_comment': {
            'pattern': r'#\s*(TODO|FIXME|XXX|HACK)',
            'severity': Severity.INFO,
            'message': 'TODO/FIXME comment found',
            'suggestion': 'Address or track these items in an issue tracker',
        },
        'complex_function': {
            'pattern': r'def\s+\w+\s*\([^)]*\):\s*\n(?:(?:\s+.+\n){30,})',
            'severity': Severity.MEDIUM,
            'message': 'Function may be too complex (>30 lines)',
            'suggestion': 'Consider breaking into smaller functions',
        },
        'nested_loop': {
            'pattern': r'for\s+.*:\s*\n\s+for\s+.*:\s*\n\s+for',
            'severity': Severity.MEDIUM,
            'message': 'Deeply nested loops (3+ levels)',
            'suggestion': 'Consider refactoring to reduce nesting depth',
        },
        'magic_number': {
            'pattern': r'[^\w](\d{3,})[^\w]',
            'severity': Severity.LOW,
            'message': 'Magic number detected',
            'suggestion': 'Define constants with meaningful names',
        },
        'duplicate_code_comment': {
            'pattern': r'#.*(?:same|similar|duplicate)',
            'severity': Severity.LOW,
            'message': 'Possible duplicate code indicated by comment',
            'suggestion': 'Refactor to eliminate duplication',
        },
    }

    def __init__(self):
        self.all_patterns = {}
        self.all_patterns.update({f"SEC-{k}": {**v, 'type': IssueType.SECURITY} for k, v in self.SECURITY_PATTERNS.items()})
        self.all_patterns.update({f"PERF-{k}": {**v, 'type': IssueType.PERFORMANCE} for k, v in self.PERFORMANCE_PATTERNS.items()})
        self.all_patterns.update({f"BUG-{k}": {**v, 'type': IssueType.BUG} for k, v in self.BUG_PATTERNS.items()})
        self.all_patterns.update({f"STYLE-{k}": {**v, 'type': IssueType.STYLE} for k, v in self.STYLE_PATTERNS.items()})
        self.all_patterns.update({f"MAINT-{k}": {**v, 'type': IssueType.MAINTAINABILITY} for k, v in self.MAINTAINABILITY_PATTERNS.items()})

    def analyze(self, code: str, file_path: str) -> List[CodeIssue]:
        """Analyze code using pattern matching"""
        issues = []
        lines = code.split('\n')

        for rule_id, pattern_info in self.all_patterns.items():
            pattern = pattern_info['pattern']
            severity = pattern_info['severity']
            message = pattern_info['message']
            suggestion = pattern_info['suggestion']
            issue_type = pattern_info['type']

            try:
                for match in re.finditer(pattern, code, re.MULTILINE):
                    # Calculate line number
                    line_num = code[:match.start()].count('\n') + 1
                    col = match.start() - code.rfind('\n', 0, match.start()) - 1

                    # Get code snippet
                    snippet_start = max(0, line_num - 2)
                    snippet_end = min(len(lines), line_num + 1)
                    snippet = '\n'.join(lines[snippet_start:snippet_end])

                    issue = CodeIssue(
                        file_path=file_path,
                        line_number=line_num,
                        column=col,
                        severity=severity,
                        issue_type=issue_type,
                        message=message,
                        suggestion=suggestion,
                        rule_id=rule_id,
                        code_snippet=snippet
                    )
                    issues.append(issue)
            except re.error:
                continue

        return issues


class StaticAnalyzer:
    """AST-based static analysis for Python code"""

    def analyze(self, code: str, file_path: str) -> List[CodeIssue]:
        """Perform static analysis on Python code"""
        issues = []

        # Pattern-based analysis (works for all languages)
        pattern_matcher = PatternMatcher()
        issues.extend(pattern_matcher.analyze(code, file_path))

        # AST-based analysis (Python only)
        if file_path.endswith('.py'):
            try:
                ast_issues = self._ast_analysis(code, file_path)
                issues.extend(ast_issues)
            except SyntaxError:
                pass  # Skip files with syntax errors

        return issues

    def _ast_analysis(self, code: str, file_path: str) -> List[CodeIssue]:
        """AST-based analysis for Python"""
        issues = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return issues

        for node in ast.walk(tree):
            # Check for unused imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if not self._is_import_used(tree, alias.name):
                        issues.append(CodeIssue(
                            file_path=file_path,
                            line_number=node.lineno,
                            column=node.col_offset,
                            severity=Severity.LOW,
                            issue_type=IssueType.MAINTAINABILITY,
                            message=f"Potentially unused import: {alias.name}",
                            suggestion="Remove unused import or use it in the code",
                            rule_id="AST-001",
                            code_snippet=self._get_node_snippet(code, node)
                        ))

            # Check for bare except
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=0,
                        severity=Severity.HIGH,
                        issue_type=IssueType.BUG,
                        message="Bare except clause catches all exceptions",
                        suggestion="Use 'except Exception:' or specify the exact exception type",
                        rule_id="AST-002",
                        code_snippet=self._get_node_snippet(code, node)
                    ))

            # Check for mutable default arguments
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append(CodeIssue(
                            file_path=file_path,
                            line_number=node.lineno,
                            column=node.col_offset,
                            severity=Severity.HIGH,
                            issue_type=IssueType.BUG,
                            message=f"Mutable default argument in function '{node.name}'",
                            suggestion="Use None as default and initialize inside function",
                            rule_id="AST-003",
                            code_snippet=self._get_node_snippet(code, node)
                        ))

                # Check function complexity
                complexity = self._calculate_complexity(node)
                if complexity > 10:
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        severity=Severity.MEDIUM,
                        issue_type=IssueType.MAINTAINABILITY,
                        message=f"Function '{node.name}' has high cyclomatic complexity ({complexity})",
                        suggestion="Consider breaking into smaller functions",
                        rule_id="AST-004",
                        code_snippet=self._get_node_snippet(code, node)
                    ))

            # Check for dangerous functions
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        issues.append(CodeIssue(
                            file_path=file_path,
                            line_number=node.lineno,
                            column=node.col_offset,
                            severity=Severity.CRITICAL,
                            issue_type=IssueType.SECURITY,
                            message=f"Dangerous function call: {node.func.id}()",
                            suggestion="Avoid using eval/exec - they can execute arbitrary code",
                            rule_id="AST-005",
                            code_snippet=self._get_node_snippet(code, node)
                        ))

        return issues

    def _is_import_used(self, tree: ast.AST, import_name: str) -> bool:
        """Check if an import is used in the code"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if node.id == import_name:
                    return True
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    if node.value.id == import_name:
                        return True
        return False

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _get_node_snippet(self, code: str, node: ast.AST, context: int = 2) -> str:
        """Get code snippet around a node"""
        lines = code.split('\n')
        start = max(0, node.lineno - context - 1)
        end = min(len(lines), node.lineno + context)
        return '\n'.join(lines[start:end])