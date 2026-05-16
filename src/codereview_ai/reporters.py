"""
Report generation modules
报告生成模块
"""

import json
from typing import List, Dict, Any
from datetime import datetime
from .core import ReviewResult, CodeIssue, Severity


class ConsoleReporter:
    """Console/terminal output reporter"""

    # ANSI color codes
    COLORS = {
        'critical': '\033[91m',  # Red
        'high': '\033[31m',      # Dark Red
        'medium': '\033[93m',    # Yellow
        'low': '\033[94m',       # Blue
        'info': '\033[90m',      # Gray
        'reset': '\033[0m',
        'bold': '\033[1m',
        'green': '\033[92m',
    }

    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors

    def _color(self, text: str, color: str) -> str:
        if self.use_colors:
            return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"
        return text

    def report(self, results: List[ReviewResult]) -> str:
        """Generate console report"""
        lines = []

        # Header
        lines.append(self._color("=" * 80, 'bold'))
        lines.append(self._color("  CodeReview-AI Report", 'bold'))
        lines.append(self._color(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'info'))
        lines.append(self._color("=" * 80, 'bold'))
        lines.append("")

        # Summary statistics
        total_issues = sum(len(r.issues) for r in results)
        critical = sum(1 for r in results for i in r.issues if i.severity == Severity.CRITICAL)
        high = sum(1 for r in results for i in r.issues if i.severity == Severity.HIGH)
        medium = sum(1 for r in results for i in r.issues if i.severity == Severity.MEDIUM)
        low = sum(1 for r in results for i in r.issues if i.severity == Severity.LOW)
        info = sum(1 for r in results for i in r.issues if i.severity == Severity.INFO)

        lines.append(self._color("📊 Summary", 'bold'))
        lines.append(f"  Files analyzed: {len(results)}")
        lines.append(f"  Total issues: {total_issues}")

        if critical > 0:
            lines.append(self._color(f"  🔴 Critical: {critical}", 'critical'))
        if high > 0:
            lines.append(self._color(f"  🟠 High: {high}", 'high'))
        if medium > 0:
            lines.append(self._color(f"  🟡 Medium: {medium}", 'medium'))
        if low > 0:
            lines.append(self._color(f"  🔵 Low: {low}", 'low'))
        if info > 0:
            lines.append(self._color(f"  ⚪ Info: {info}", 'info'))

        lines.append("")

        # Detailed issues
        for result in results:
            if result.issues:
                lines.append(self._color(f"📁 {result.file_path}", 'bold'))
                lines.append(self._color("-" * 80, 'info'))

                # Sort issues by severity
                sorted_issues = sorted(result.issues, key=lambda x: (
                    Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO
                ).index(x.severity))

                for issue in sorted_issues:
                    severity_color = issue.severity.value
                    icon = {
                        'critical': '🔴',
                        'high': '🟠',
                        'medium': '🟡',
                        'low': '🔵',
                        'info': '⚪'
                    }.get(issue.severity.value, '⚪')

                    lines.append(f"  {icon} {self._color(issue.severity.value.upper(), severity_color)} | {issue.rule_id}")
                    lines.append(f"     Line {issue.line_number}, Col {issue.column}: {issue.message}")
                    if issue.suggestion:
                        lines.append(f"     💡 {issue.suggestion}")
                    if issue.code_snippet:
                        snippet_lines = issue.code_snippet.split('\n')
                        for snippet_line in snippet_lines:
                            lines.append(f"        {self._color('|', 'info')} {snippet_line}")
                    lines.append("")

        # Footer
        if total_issues == 0:
            lines.append(self._color("✅ No issues found! Great job! 🎉", 'green'))
        else:
            lines.append(self._color(f"⚠️  Found {total_issues} issue(s) that need attention", 'high'))

        lines.append("")
        lines.append(self._color("=" * 80, 'bold'))

        return '\n'.join(lines)


class JSONReporter:
    """JSON format reporter"""

    def report(self, results: List[ReviewResult]) -> str:
        """Generate JSON report"""
        report_data = {
            "meta": {
                "tool": "CodeReview-AI",
                "version": "1.0.0",
                "generated_at": datetime.now().isoformat(),
            },
            "summary": self._calculate_summary(results),
            "results": [r.to_dict() for r in results]
        }
        return json.dumps(report_data, indent=2, ensure_ascii=False)

    def _calculate_summary(self, results: List[ReviewResult]) -> Dict[str, Any]:
        """Calculate summary statistics"""
        total_issues = sum(len(r.issues) for r in results)

        severity_counts = {
            'critical': sum(1 for r in results for i in r.issues if i.severity == Severity.CRITICAL),
            'high': sum(1 for r in results for i in r.issues if i.severity == Severity.HIGH),
            'medium': sum(1 for r in results for i in r.issues if i.severity == Severity.MEDIUM),
            'low': sum(1 for r in results for i in r.issues if i.severity == Severity.LOW),
            'info': sum(1 for r in results for i in r.issues if i.severity == Severity.INFO),
        }

        type_counts = {}
        for result in results:
            for issue in result.issues:
                type_name = issue.issue_type.value
                type_counts[type_name] = type_counts.get(type_name, 0) + 1

        return {
            "total_files": len(results),
            "total_issues": total_issues,
            "by_severity": severity_counts,
            "by_type": type_counts,
        }


class MarkdownReporter:
    """Markdown format reporter"""

    def report(self, results: List[ReviewResult]) -> str:
        """Generate Markdown report"""
        lines = []

        # Header
        lines.append("# CodeReview-AI Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Summary
        lines.append("## 📊 Summary")
        lines.append("")

        total_issues = sum(len(r.issues) for r in results)
        critical = sum(1 for r in results for i in r.issues if i.severity == Severity.CRITICAL)
        high = sum(1 for r in results for i in r.issues if i.severity == Severity.HIGH)
        medium = sum(1 for r in results for i in r.issues if i.severity == Severity.MEDIUM)
        low = sum(1 for r in results for i in r.issues if i.severity == Severity.LOW)
        info = sum(1 for r in results for i in r.issues if i.severity == Severity.INFO)

        lines.append(f"- **Files analyzed:** {len(results)}")
        lines.append(f"- **Total issues:** {total_issues}")
        lines.append("")

        # Severity table
        lines.append("### Issues by Severity")
        lines.append("")
        lines.append("| Severity | Count |")
        lines.append("|----------|-------|")
        lines.append(f"| 🔴 Critical | {critical} |")
        lines.append(f"| 🟠 High | {high} |")
        lines.append(f"| 🟡 Medium | {medium} |")
        lines.append(f"| 🔵 Low | {low} |")
        lines.append(f"| ⚪ Info | {info} |")
        lines.append("")

        # Detailed findings
        lines.append("## 🔍 Detailed Findings")
        lines.append("")

        for result in results:
            if result.issues:
                lines.append(f"### {result.file_path}")
                lines.append("")

                # Sort issues by severity
                sorted_issues = sorted(result.issues, key=lambda x: (
                    Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO
                ).index(x.severity))

                for issue in sorted_issues:
                    severity_emoji = {
                        'critical': '🔴',
                        'high': '🟠',
                        'medium': '🟡',
                        'low': '🔵',
                        'info': '⚪'
                    }.get(issue.severity.value, '⚪')

                    lines.append(f"#### {severity_emoji} {issue.severity.value.upper()} - {issue.rule_id}")
                    lines.append("")
                    lines.append(f"- **Location:** Line {issue.line_number}, Column {issue.column}")
                    lines.append(f"- **Type:** {issue.issue_type.value}")
                    lines.append(f"- **Message:** {issue.message}")
                    if issue.suggestion:
                        lines.append(f"- **Suggestion:** {issue.suggestion}")
                    lines.append("")

                    if issue.code_snippet:
                        lines.append("**Code snippet:**")
                        lines.append("```python")
                        lines.append(issue.code_snippet)
                        lines.append("```")
                        lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        if total_issues == 0:
            lines.append("✅ **No issues found! Great job!** 🎉")
        else:
            lines.append(f"⚠️ **Found {total_issues} issue(s) that need attention**")
        lines.append("")
        lines.append("*Generated by [CodeReview-AI](https://github.com/gitstq/codereview-ai)*")

        return '\n'.join(lines)


class HTMLReporter:
    """HTML format reporter"""

    def report(self, results: List[ReviewResult]) -> str:
        """Generate HTML report"""
        total_issues = sum(len(r.issues) for r in results)
        critical = sum(1 for r in results for i in r.issues if i.severity == Severity.CRITICAL)
        high = sum(1 for r in results for i in r.issues if i.severity == Severity.HIGH)
        medium = sum(1 for r in results for i in r.issues if i.severity == Severity.MEDIUM)
        low = sum(1 for r in results for i in r.issues if i.severity == Severity.LOW)
        info = sum(1 for r in results for i in r.issues if i.severity == Severity.INFO)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeReview-AI Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{ margin-bottom: 10px; }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-card.critical {{ border-top: 4px solid #dc3545; }}
        .stat-card.high {{ border-top: 4px solid #fd7e14; }}
        .stat-card.medium {{ border-top: 4px solid #ffc107; }}
        .stat-card.low {{ border-top: 4px solid #17a2b8; }}
        .stat-card.info {{ border-top: 4px solid #6c757d; }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .file-section {{
            background: white;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .file-header {{
            background: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 1px solid #e9ecef;
            font-weight: bold;
        }}
        .issue {{
            padding: 15px 20px;
            border-bottom: 1px solid #e9ecef;
        }}
        .issue:last-child {{ border-bottom: none; }}
        .issue-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}
        .badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .badge.critical {{ background: #dc3545; color: white; }}
        .badge.high {{ background: #fd7e14; color: white; }}
        .badge.medium {{ background: #ffc107; color: #333; }}
        .badge.low {{ background: #17a2b8; color: white; }}
        .badge.info {{ background: #6c757d; color: white; }}
        .issue-message {{ margin-bottom: 8px; }}
        .issue-suggestion {{
            color: #28a745;
            font-style: italic;
        }}
        .code-snippet {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 10px;
            margin-top: 10px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
            overflow-x: auto;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 CodeReview-AI Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="summary">
            <div class="stat-card">
                <div>Files Analyzed</div>
                <div class="stat-number">{len(results)}</div>
            </div>
            <div class="stat-card critical">
                <div>Critical</div>
                <div class="stat-number">{critical}</div>
            </div>
            <div class="stat-card high">
                <div>High</div>
                <div class="stat-number">{high}</div>
            </div>
            <div class="stat-card medium">
                <div>Medium</div>
                <div class="stat-number">{medium}</div>
            </div>
            <div class="stat-card low">
                <div>Low</div>
                <div class="stat-number">{low}</div>
            </div>
            <div class="stat-card info">
                <div>Info</div>
                <div class="stat-number">{info}</div>
            </div>
        </div>
"""

        # Add file sections
        for result in results:
            if result.issues:
                html += f"""
        <div class="file-section">
            <div class="file-header">📁 {result.file_path}</div>
"""
                sorted_issues = sorted(result.issues, key=lambda x: (
                    Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO
                ).index(x.severity))

                for issue in sorted_issues:
                    html += f"""
            <div class="issue">
                <div class="issue-header">
                    <span class="badge {issue.severity.value}">{issue.severity.value.upper()}</span>
                    <span>{issue.rule_id}</span>
                    <span>Line {issue.line_number}</span>
                </div>
                <div class="issue-message">{issue.message}</div>
                {f'<div class="issue-suggestion">💡 {issue.suggestion}</div>' if issue.suggestion else ''}
                {f'<div class="code-snippet"><pre>{issue.code_snippet}</pre></div>' if issue.code_snippet else ''}
            </div>
"""
                html += "        </div>\n"

        html += f"""
        <div class="footer">
            <p>Generated by CodeReview-AI v1.0.0</p>
        </div>
    </div>
</body>
</html>"""

        return html