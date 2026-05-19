"""
终端报告生成器
生成美观的终端输出
"""
from typing import Dict, List
from .base import BaseReporter, AnalysisResult
from ..analyzer.base import Issue, IssueSeverity


class ConsoleReporter(BaseReporter):
    """终端报告生成器"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.use_color = self.config.get("color", True)
        self.show_code = self.config.get("show_code", True)
    
    @property
    def name(self) -> str:
        return "console"
    
    @property
    def extension(self) -> str:
        return "txt"
    
    def generate(self, result: AnalysisResult) -> str:
        """生成终端报告"""
        lines = []
        
        # 标题
        lines.append(self._header("🔍 CodeReview-AI 报告"))
        lines.append("")
        
        # 摘要
        lines.append(self._section("📊 分析摘要"))
        lines.append(f"  分析文件数: {len(result.files_analyzed)}")
        lines.append(f"  分析耗时: {result.get_duration():.2f}秒")
        lines.append("")
        
        # 问题统计
        counts = result.get_issue_counts()
        lines.append(self._section("📈 问题统计"))
        
        severity_icons = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🔵",
            "info": "⚪",
        }
        
        for sev in ["critical", "high", "medium", "low", "info"]:
            count = counts.get(sev, 0)
            icon = severity_icons.get(sev, "⚪")
            lines.append(f"  {icon} {sev.upper()}: {count}")
        
        lines.append(f"  📋 总计: {counts['total']}")
        lines.append("")
        
        # 问题详情
        if result.issues:
            lines.append(self._section("📝 问题详情"))
            lines.append("")
            
            # 按严重程度排序
            sorted_issues = sorted(
                result.issues,
                key=lambda i: (i.severity.priority(), i.file_path, i.line)
            )
            
            for issue in sorted_issues:
                lines.extend(self._format_issue(issue))
                lines.append("")
        
        # AI审查结果
        if result.ai_review:
            lines.append(self._section("🤖 AI 审查结果"))
            lines.append("")
            lines.append(f"  代码评分: {result.ai_review.score}/100")
            lines.append("")
            
            if result.ai_review.summary:
                lines.append(f"  总体评价: {result.ai_review.summary}")
                lines.append("")
            
            if result.ai_review.strengths:
                lines.append("  ✅ 代码优点:")
                for strength in result.ai_review.strengths[:5]:
                    lines.append(f"    • {strength}")
                lines.append("")
            
            if result.ai_review.improvements:
                lines.append("  💡 改进建议:")
                for improvement in result.ai_review.improvements[:5]:
                    lines.append(f"    • {improvement}")
                lines.append("")
            
            if result.ai_review.comments:
                lines.append("  📌 AI 详细评论:")
                lines.append("")
                for comment in result.ai_review.comments[:10]:
                    lines.append(f"    [{comment.severity.value.upper()}] {comment.category}")
                    lines.append(f"    {comment.message}")
                    if comment.suggestion:
                        lines.append(f"    建议: {comment.suggestion}")
                    lines.append("")
        
        # 页脚
        lines.append(self._footer())
        
        return "\n".join(lines)
    
    def _header(self, title: str) -> str:
        """生成标题"""
        width = 60
        if self.use_color:
            return f"\033[1;36m{'=' * width}\n{title.center(width)}\n{'=' * width}\033[0m"
        return f"{'=' * width}\n{title.center(width)}\n{'=' * width}"
    
    def _section(self, title: str) -> str:
        """生成章节标题"""
        if self.use_color:
            return f"\033[1;33m{title}\033[0m"
        return title
    
    def _footer(self) -> str:
        """生成页脚"""
        width = 60
        if self.use_color:
            return f"\033[1;36m{'=' * width}\033[0m"
        return "=" * width
    
    def _format_issue(self, issue: Issue) -> List[str]:
        """格式化单个问题"""
        lines = []
        
        # 严重程度和位置
        severity_str = self._format_severity(issue.severity)
        location = issue.location_str()
        
        header = f"  [{severity_str}] {location}"
        lines.append(header)
        
        # 消息
        lines.append(f"    {issue.category.emoji()} {issue.message}")
        
        # 描述
        if issue.description:
            lines.append(f"    描述: {issue.description}")
        
        # 建议
        if issue.suggestion:
            lines.append(f"    建议: {issue.suggestion}")
        
        # 代码片段
        if self.show_code and issue.code_snippet:
            snippet = issue.code_snippet[:200] + "..." if len(issue.code_snippet) > 200 else issue.code_snippet
            lines.append(f"    代码: {snippet}")
        
        return lines
    
    def _format_severity(self, severity: IssueSeverity) -> str:
        """格式化严重程度"""
        if self.use_color:
            reset = "\033[0m"
            return f"{severity.color_code()}{severity.value.upper()}{reset}"
        return severity.value.upper()
