"""
Core module for CodeReview-AI
代码审查核心模块
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import urllib.request
import urllib.error


class Severity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueType(Enum):
    """Types of code issues"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUG = "bug"
    STYLE = "style"
    MAINTAINABILITY = "maintainability"
    DOCUMENTATION = "documentation"


@dataclass
class CodeIssue:
    """Represents a code issue found during review"""
    file_path: str
    line_number: int
    column: int
    severity: Severity
    issue_type: IssueType
    message: str
    suggestion: str = ""
    rule_id: str = ""
    code_snippet: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column": self.column,
            "severity": self.severity.value,
            "issue_type": self.issue_type.value,
            "message": self.message,
            "suggestion": self.suggestion,
            "rule_id": self.rule_id,
            "code_snippet": self.code_snippet,
        }


@dataclass
class ReviewResult:
    """Complete review result for a file or project"""
    file_path: str
    issues: List[CodeIssue] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, int] = field(default_factory=dict)

    def add_issue(self, issue: CodeIssue):
        self.issues.append(issue)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "issues": [issue.to_dict() for issue in self.issues],
            "summary": self.summary,
            "statistics": self.statistics,
        }


class LLMBackend:
    """Base class for LLM backends"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.base_url = base_url

    def analyze_code(self, code: str, file_path: str) -> List[CodeIssue]:
        raise NotImplementedError


class OpenAIBackend(LLMBackend):
    """OpenAI API backend"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        super().__init__(api_key)
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def analyze_code(self, code: str, file_path: str) -> List[CodeIssue]:
        """Analyze code using OpenAI API"""
        if not self.api_key:
            return []

        prompt = self._build_prompt(code, file_path)

        try:
            data = json.dumps({
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a code review assistant. Analyze the provided code and return a JSON array of issues found."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }).encode('utf-8')

            req = urllib.request.Request(
                self.base_url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                return self._parse_response(result, file_path)

        except Exception as e:
            print(f"Warning: LLM analysis failed: {e}")
            return []

    def _build_prompt(self, code: str, file_path: str) -> str:
        return f"""Analyze the following code file and identify potential issues.

File: {file_path}

```
{code}
```

Please identify issues in the following categories:
1. Security vulnerabilities
2. Performance issues
3. Potential bugs
4. Code style issues
5. Maintainability concerns

Return a JSON object with an "issues" array. Each issue should have:
- line_number: int
- severity: "critical", "high", "medium", "low", or "info"
- issue_type: "security", "performance", "bug", "style", or "maintainability"
- message: string describing the issue
- suggestion: string with recommended fix

If no issues are found, return an empty issues array."""

    def _parse_response(self, result: Dict, file_path: str) -> List[CodeIssue]:
        issues = []
        try:
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            parsed = json.loads(content)
            for item in parsed.get("issues", []):
                issue = CodeIssue(
                    file_path=file_path,
                    line_number=item.get("line_number", 1),
                    column=item.get("column", 0),
                    severity=Severity(item.get("severity", "info")),
                    issue_type=IssueType(item.get("issue_type", "maintainability")),
                    message=item.get("message", ""),
                    suggestion=item.get("suggestion", ""),
                    rule_id="LLM-001"
                )
                issues.append(issue)
        except Exception as e:
            print(f"Warning: Failed to parse LLM response: {e}")
        return issues


class AnthropicBackend(LLMBackend):
    """Anthropic Claude API backend"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-haiku-20240307"):
        super().__init__(api_key)
        self.model = model
        self.base_url = "https://api.anthropic.com/v1/messages"

    def analyze_code(self, code: str, file_path: str) -> List[CodeIssue]:
        """Analyze code using Anthropic API"""
        if not self.api_key:
            return []

        prompt = self._build_prompt(code, file_path)

        try:
            data = json.dumps({
                "model": self.model,
                "max_tokens": 4000,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }).encode('utf-8')

            req = urllib.request.Request(
                self.base_url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                return self._parse_response(result, file_path)

        except Exception as e:
            print(f"Warning: LLM analysis failed: {e}")
            return []

    def _build_prompt(self, code: str, file_path: str) -> str:
        return f"""Analyze the following code file and identify potential issues.

File: {file_path}

```
{code}
```

Please identify issues in the following categories:
1. Security vulnerabilities
2. Performance issues
3. Potential bugs
4. Code style issues
5. Maintainability concerns

Return ONLY a JSON object with an "issues" array. Each issue should have:
- line_number: int
- severity: "critical", "high", "medium", "low", or "info"
- issue_type: "security", "performance", "bug", "style", or "maintainability"
- message: string describing the issue
- suggestion: string with recommended fix

If no issues are found, return {{"issues": []}}."""

    def _parse_response(self, result: Dict, file_path: str) -> List[CodeIssue]:
        issues = []
        try:
            content = result.get("content", [{}])[0].get("text", "")
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                for item in parsed.get("issues", []):
                    issue = CodeIssue(
                        file_path=file_path,
                        line_number=item.get("line_number", 1),
                        column=item.get("column", 0),
                        severity=Severity(item.get("severity", "info")),
                        issue_type=IssueType(item.get("issue_type", "maintainability")),
                        message=item.get("message", ""),
                        suggestion=item.get("suggestion", ""),
                        rule_id="LLM-001"
                    )
                    issues.append(issue)
        except Exception as e:
            print(f"Warning: Failed to parse LLM response: {e}")
        return issues


class DeepSeekBackend(LLMBackend):
    """DeepSeek API backend"""

    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat"):
        super().__init__(api_key)
        self.model = model
        self.base_url = "https://api.deepseek.com/chat/completions"

    def analyze_code(self, code: str, file_path: str) -> List[CodeIssue]:
        """Analyze code using DeepSeek API"""
        if not self.api_key:
            return []

        prompt = self._build_prompt(code, file_path)

        try:
            data = json.dumps({
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a code review assistant. Analyze code and return JSON format issues."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }).encode('utf-8')

            req = urllib.request.Request(
                self.base_url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                return self._parse_response(result, file_path)

        except Exception as e:
            print(f"Warning: LLM analysis failed: {e}")
            return []

    def _build_prompt(self, code: str, file_path: str) -> str:
        return f"""Analyze the following code file and identify potential issues.

File: {file_path}

```
{code}
```

Identify issues in: security, performance, bugs, style, maintainability.

Return JSON: {{"issues": [{{"line_number": int, "severity": str, "issue_type": str, "message": str, "suggestion": str}}]}}"""

    def _parse_response(self, result: Dict, file_path: str) -> List[CodeIssue]:
        issues = []
        try:
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            parsed = json.loads(content)
            for item in parsed.get("issues", []):
                issue = CodeIssue(
                    file_path=file_path,
                    line_number=item.get("line_number", 1),
                    column=item.get("column", 0),
                    severity=Severity(item.get("severity", "info")),
                    issue_type=IssueType(item.get("issue_type", "maintainability")),
                    message=item.get("message", ""),
                    suggestion=item.get("suggestion", ""),
                    rule_id="LLM-001"
                )
                issues.append(issue)
        except Exception as e:
            print(f"Warning: Failed to parse LLM response: {e}")
        return issues


class CodeReviewer:
    """Main code reviewer class"""

    SUPPORTED_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
        '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.r', '.m',
        '.cs', '.fs', '.fsx', '.clj', '.cljs', '.erl', '.ex', '.exs', '.hs',
        '.lua', '.pl', '.pm', '.sh', '.bash', '.zsh', '.ps1', '.sql', '.html',
        '.css', '.scss', '.sass', '.less', '.vue', '.svelte', '.json', '.yaml', '.yml'
    }

    def __init__(
        self,
        llm_backend: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        use_static_analysis: bool = True,
        use_llm: bool = False,
        max_file_size: int = 500000,  # 500KB
    ):
        self.use_static_analysis = use_static_analysis
        self.use_llm = use_llm
        self.max_file_size = max_file_size
        self.llm = None

        if use_llm and llm_backend:
            self._init_llm(llm_backend, api_key, model)

    def _init_llm(self, backend: str, api_key: Optional[str], model: Optional[str]):
        """Initialize LLM backend"""
        backend = backend.lower()

        if backend == "openai":
            self.llm = OpenAIBackend(api_key=api_key, model=model or "gpt-4o-mini")
        elif backend in ["anthropic", "claude"]:
            self.llm = AnthropicBackend(api_key=api_key, model=model or "claude-3-haiku-20240307")
        elif backend == "deepseek":
            self.llm = DeepSeekBackend(api_key=api_key, model=model or "deepseek-chat")
        else:
            raise ValueError(f"Unsupported LLM backend: {backend}")

    def review_file(self, file_path: str) -> ReviewResult:
        """Review a single file"""
        result = ReviewResult(file_path=file_path)

        if not os.path.exists(file_path):
            result.summary = {"error": "File not found"}
            return result

        # Check file size
        if os.path.getsize(file_path) > self.max_file_size:
            result.summary = {"error": "File too large"}
            return result

        # Check extension
        ext = Path(file_path).suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            result.summary = {"error": f"Unsupported file type: {ext}"}
            return result

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
        except Exception as e:
            result.summary = {"error": f"Failed to read file: {e}"}
            return result

        # Static analysis
        if self.use_static_analysis:
            from .analyzers import StaticAnalyzer
            analyzer = StaticAnalyzer()
            static_issues = analyzer.analyze(code, file_path)
            for issue in static_issues:
                result.add_issue(issue)

        # LLM analysis
        if self.use_llm and self.llm:
            llm_issues = self.llm.analyze_code(code, file_path)
            for issue in llm_issues:
                result.add_issue(issue)

        # Calculate statistics
        result.statistics = self._calculate_statistics(result.issues)
        result.summary = {
            "total_issues": len(result.issues),
            "file_size": len(code),
            "lines_of_code": code.count('\n') + 1,
        }

        return result

    def review_directory(self, directory: str, exclude_patterns: Optional[List[str]] = None) -> List[ReviewResult]:
        """Review all files in a directory"""
        results = []
        exclude_patterns = exclude_patterns or ['.git', '__pycache__', 'node_modules', 'venv', '.venv', 'dist', 'build']

        for root, dirs, files in os.walk(directory):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_patterns and not d.startswith('.')]

            for file in files:
                file_path = os.path.join(root, file)
                ext = Path(file).suffix.lower()

                if ext in self.SUPPORTED_EXTENSIONS:
                    result = self.review_file(file_path)
                    if result.issues or not result.summary.get("error"):
                        results.append(result)

        return results

    def review_git_diff(self, repo_path: str = ".", base_ref: str = "HEAD~1") -> List[ReviewResult]:
        """Review files changed in git diff"""
        results = []

        try:
            # Get list of changed files
            cmd = ['git', '-C', repo_path, 'diff', '--name-only', base_ref]
            output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
            changed_files = [f.strip() for f in output.split('\n') if f.strip()]

            for file_path in changed_files:
                full_path = os.path.join(repo_path, file_path)
                if os.path.exists(full_path):
                    ext = Path(file_path).suffix.lower()
                    if ext in self.SUPPORTED_EXTENSIONS:
                        result = self.review_file(full_path)
                        results.append(result)

        except subprocess.CalledProcessError:
            print("Warning: Failed to get git diff")
        except FileNotFoundError:
            print("Warning: Git not found")

        return results

    def _calculate_statistics(self, issues: List[CodeIssue]) -> Dict[str, int]:
        """Calculate issue statistics"""
        stats = {
            "total": len(issues),
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }

        type_stats = {}

        for issue in issues:
            stats[issue.severity.value] += 1
            type_name = issue.issue_type.value
            type_stats[type_name] = type_stats.get(type_name, 0) + 1

        stats["by_type"] = type_stats
        return stats