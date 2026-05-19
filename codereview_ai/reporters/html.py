"""
HTML报告生成器
"""
from typing import List
from .base import BaseReporter, AnalysisResult
from ..analyzer.base import Issue, IssueSeverity


class HTMLReporter(BaseReporter):
    """HTML报告生成器"""
    
    def __init__(self, config=None):
        super().__init__(config)
    
    @property
    def name(self) -> str:
        return "html"
    
    @property
    def extension(self) -> str:
        return "html"
    
    def generate(self, result: AnalysisResult) -> str:
        """生成HTML报告"""
        counts = result.get_issue_counts()
        
        html_parts = []
        
        # HTML头部
        html_parts.append(self._get_html_head())
        
        # 主体内容
        html_parts.append("<body>")
        html_parts.append("<div class='container'>")
        
        # 标题
        html_parts.append("<h1>🔍 CodeReview-AI 报告</h1>")
        
        # 摘要
        html_parts.append("<div class='summary'>")
        html_parts.append("<h2>📊 分析摘要</h2>")
        html_parts.append(f"<p><strong>分析文件数</strong>: {len(result.files_analyzed)}</p>")
        html_parts.append(f"<p><strong>分析耗时</strong>: {result.get_duration():.2f}秒</p>")
        html_parts.append("</div>")
        
        # 问题统计
        html_parts.append("<div class='stats'>")
        html_parts.append("<h2>📈 问题统计</h2>")
        html_parts.append("<table>")
        html_parts.append("<tr><th>严重程度</th><th>数量</th></tr>")
        html_parts.append(f"<tr class='critical'><td>🔴 Critical</td><td>{counts['critical']}</td></tr>")
        html_parts.append(f"<tr class='high'><td>🟠 High</td><td>{counts['high']}</td></tr>")
        html_parts.append(f"<tr class='medium'><td>🟡 Medium</td><td>{counts['medium']}</td></tr>")
        html_parts.append(f"<tr class='low'><td>🔵 Low</td><td>{counts['low']}</td></tr>")
        html_parts.append(f"<tr class='info'><td>⚪ Info</td><td>{counts['info']}</td></tr>")
        html_parts.append(f"<tr class='total'><td><strong>总计</strong></td><td><strong>{counts['total']}</strong></td></tr>")
        html_parts.append("</table>")
        html_parts.append("</div>")
        
        # 问题详情
        if result.issues:
            html_parts.append("<div class='issues'>")
            html_parts.append("<h2>📝 问题详情</h2>")
            
            # 按文件分组
            issues_by_file = result.get_issues_by_file()
            
            for file_path, issues in sorted(issues_by_file.items()):
                html_parts.append(f"<div class='file-section'>")
                html_parts.append(f"<h3>{file_path}</h3>")
                
                # 按严重程度排序
                sorted_issues = sorted(issues, key=lambda i: i.severity.priority())
                
                for issue in sorted_issues:
                    html_parts.extend(self._format_issue(issue))
                
                html_parts.append("</div>")
            
            html_parts.append("</div>")
        
        # AI审查结果
        if result.ai_review:
            html_parts.append("<div class='ai-review'>")
            html_parts.append("<h2>🤖 AI 审查结果</h2>")
            
            # 评分
            score = result.ai_review.score
            score_class = "score-high" if score >= 80 else "score-medium" if score >= 60 else "score-low"
            html_parts.append(f"<div class='score {score_class}'>代码评分: {score}/100</div>")
            
            if result.ai_review.summary:
                html_parts.append("<h3>总体评价</h3>")
                html_parts.append(f"<p>{result.ai_review.summary}</p>")
            
            if result.ai_review.strengths:
                html_parts.append("<h3>✅ 代码优点</h3>")
                html_parts.append("<ul>")
                for strength in result.ai_review.strengths:
                    html_parts.append(f"<li>{strength}</li>")
                html_parts.append("</ul>")
            
            if result.ai_review.improvements:
                html_parts.append("<h3>💡 改进建议</h3>")
                html_parts.append("<ul>")
                for improvement in result.ai_review.improvements:
                    html_parts.append(f"<li>{improvement}</li>")
                html_parts.append("</ul>")
            
            if result.ai_review.comments:
                html_parts.append("<h3>📌 AI 详细评论</h3>")
                
                for comment in result.ai_review.comments:
                    html_parts.append(f"<div class='comment severity-{comment.severity.value}'>")
                    html_parts.append(f"<h4>[{comment.severity.value.upper()}] {comment.category}</h4>")
                    html_parts.append(f"<p>{comment.message}</p>")
                    if comment.suggestion:
                        html_parts.append(f"<p><strong>建议:</strong> {comment.suggestion}</p>")
                    if comment.code_example:
                        html_parts.append(f"<pre><code>{comment.code_example}</code></pre>")
                    html_parts.append("</div>")
            
            html_parts.append("</div>")
        
        # 页脚
        html_parts.append("<div class='footer'>")
        html_parts.append("<p>Generated by CodeReview-AI</p>")
        html_parts.append("</div>")
        
        html_parts.append("</div>")
        html_parts.append("</body>")
        html_parts.append("</html>")
        
        return "\n".join(html_parts)
    
    def _get_html_head(self) -> str:
        """获取HTML头部"""
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeReview-AI 报告</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        h3 { color: #7f8c8d; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th { background: #f8f9fa; font-weight: 600; }
        tr:hover { background: #f8f9fa; }
        .critical { color: #e74c3c; }
        .high { color: #e67e22; }
        .medium { color: #f39c12; }
        .low { color: #3498db; }
        .info { color: #95a5a6; }
        .issue {
            border-left: 4px solid #ddd;
            padding: 15px;
            margin: 15px 0;
            background: #f8f9fa;
            border-radius: 4px;
        }
        .issue.critical { border-left-color: #e74c3c; }
        .issue.high { border-left-color: #e67e22; }
        .issue.medium { border-left-color: #f39c12; }
        .issue.low { border-left-color: #3498db; }
        .issue.info { border-left-color: #95a5a6; }
        .issue-header {
            font-weight: 600;
            margin-bottom: 8px;
        }
        .issue-meta { color: #7f8c8d; font-size: 0.9em; }
        .issue-description { margin: 10px 0; }
        .issue-suggestion { color: #27ae60; }
        pre {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }
        code {
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
        }
        .score {
            font-size: 2em;
            font-weight: bold;
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .score-high { background: #d4edda; color: #155724; }
        .score-medium { background: #fff3cd; color: #856404; }
        .score-low { background: #f8d7da; color: #721c24; }
        .comment {
            border: 1px solid #ddd;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }
        .comment.severity-critical { border-color: #e74c3c; background: #fdf2f2; }
        .comment.severity-high { border-color: #e67e22; background: #fef6f0; }
        .comment.severity-medium { border-color: #f39c12; background: #fffbf0; }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #95a5a6;
        }
    </style>
</head>"""
    
    def _format_issue(self, issue: Issue) -> List[str]:
        """格式化单个问题"""
        lines = []
        
        severity_class = issue.severity.value
        
        lines.append(f"<div class='issue {severity_class}'>")
        lines.append(f"<div class='issue-header'>[{issue.severity.value.upper()}] {issue.rule_name}</div>")
        
        # 位置
        if issue.line > 0:
            lines.append(f"<div class='issue-meta'>位置: {issue.file_path}:{issue.line}</div>")
        else:
            lines.append(f"<div class='issue-meta'>文件: {issue.file_path}</div>")
        
        # 消息
        lines.append(f"<div class='issue-description'><strong>问题:</strong> {issue.message}</div>")
        
        # 描述
        if issue.description:
            lines.append(f"<div class='issue-description'>{issue.description}</div>")
        
        # 建议
        if issue.suggestion:
            lines.append(f"<div class='issue-suggestion'>💡 <strong>建议:</strong> {issue.suggestion}</div>")
        
        # 代码片段
        if issue.code_snippet:
            lines.append("<pre><code>")
            lines.append(issue.code_snippet)
            lines.append("</code></pre>")
        
        lines.append("</div>")
        
        return lines
