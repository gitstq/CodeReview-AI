"""
命令行接口
"""
import sys
import argparse
from typing import List, Optional
from pathlib import Path

from . import __version__
from .config import Config
from .analyzer import (
    ComplexityAnalyzer,
    StyleAnalyzer,
    SecurityAnalyzer,
    DuplicateAnalyzer,
)
from .ai import OpenAIBackend, AnthropicBackend, OllamaBackend
from .reporters import (
    ConsoleReporter,
    MarkdownReporter,
    JSONReporter,
    HTMLReporter,
    SARIFReporter,
)
from .git_utils import GitUtils
from .utils import find_files, read_file
from .reporters.base import AnalysisResult
from datetime import datetime


def create_parser() -> argparse.ArgumentParser:
    """创建参数解析器"""
    parser = argparse.ArgumentParser(
        prog="codereview-ai",
        description="🔍 CodeReview-AI - 轻量级AI驱动代码审查与质量分析引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                          # 审查当前目录所有文件
  %(prog)s src/                     # 审查指定目录
  %(prog)s main.py utils.py         # 审查指定文件
  %(prog)s --git                    # 审查Git变更文件
  %(prog)s --git --staged           # 审查暂存区文件
  %(prog)s --ai                     # 启用AI审查
  %(prog)s --format markdown -o report.md
  %(prog)s --init                   # 初始化配置文件
        """,
    )
    
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="要审查的文件或目录路径 (默认: 当前目录)",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    
    parser.add_argument(
        "--init",
        action="store_true",
        help="初始化配置文件",
    )
    
    # Git集成选项
    git_group = parser.add_argument_group("Git 集成")
    git_group.add_argument(
        "--git",
        action="store_true",
        help="只审查Git变更的文件",
    )
    git_group.add_argument(
        "--staged",
        action="store_true",
        help="只审查暂存区的文件",
    )
    git_group.add_argument(
        "--commit-range",
        metavar="RANGE",
        help="审查指定commit范围的变更 (如: HEAD~3..HEAD)",
    )
    
    # AI选项
    ai_group = parser.add_argument_group("AI 审查")
    ai_group.add_argument(
        "--ai",
        action="store_true",
        help="启用AI审查",
    )
    ai_group.add_argument(
        "--backend",
        choices=["openai", "anthropic", "ollama"],
        help="AI后端类型",
    )
    ai_group.add_argument(
        "--model",
        help="AI模型名称",
    )
    ai_group.add_argument(
        "--api-key",
        help="API密钥",
    )
    
    # 报告选项
    report_group = parser.add_argument_group("报告输出")
    report_group.add_argument(
        "--format",
        choices=["console", "markdown", "json", "html", "sarif"],
        default="console",
        help="报告格式 (默认: console)",
    )
    report_group.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="输出文件路径",
    )
    report_group.add_argument(
        "--no-color",
        action="store_true",
        help="禁用彩色输出",
    )
    
    # 配置选项
    config_group = parser.add_argument_group("配置")
    config_group.add_argument(
        "--config",
        metavar="FILE",
        help="指定配置文件",
    )
    config_group.add_argument(
        "--exclude",
        action="append",
        metavar="PATTERN",
        help="排除模式 (可多次使用)",
    )
    
    return parser


def run_analysis(args, config: Config) -> AnalysisResult:
    """运行分析"""
    result = AnalysisResult()
    result.start_time = datetime.now()
    
    # 确定要分析的文件
    files_to_analyze = []
    
    if args.git or args.staged or args.commit_range:
        # Git模式
        if not GitUtils.is_git_repo():
            print("错误: 当前目录不是Git仓库", file=sys.stderr)
            sys.exit(1)
        
        changed_files = GitUtils.get_changed_files(
            staged=args.staged,
            commit_range=args.commit_range,
        )
        
        # 过滤存在的Python文件
        files_to_analyze = [
            f for f in changed_files
            if f.endswith(".py") and Path(f).exists()
        ]
        
        print(f"发现 {len(files_to_analyze)} 个变更的Python文件")
    else:
        # 普通模式
        include_patterns = config.get("include", ["**/*.py"])
        exclude_patterns = config.get("exclude", [])
        
        if args.exclude:
            exclude_patterns.extend(args.exclude)
        
        for file_path in find_files(args.paths, include_patterns, exclude_patterns):
            if file_path.endswith(".py"):
                files_to_analyze.append(file_path)
    
    if not files_to_analyze:
        print("没有找到要分析的文件")
        return result
    
    result.files_analyzed = files_to_analyze
    
    # 初始化分析器
    analyzers = []
    
    if config.is_analyzer_enabled("complexity"):
        analyzers.append(ComplexityAnalyzer(config.get_analyzer_config("complexity")))
    
    if config.is_analyzer_enabled("style"):
        analyzers.append(StyleAnalyzer(config.get_analyzer_config("style")))
    
    if config.is_analyzer_enabled("security"):
        analyzers.append(SecurityAnalyzer(config.get_analyzer_config("security")))
    
    if config.is_analyzer_enabled("duplicate"):
        analyzers.append(DuplicateAnalyzer(config.get_analyzer_config("duplicate")))
    
    # 运行静态分析
    print(f"正在分析 {len(files_to_analyze)} 个文件...")
    
    for file_path in files_to_analyze:
        content = read_file(file_path)
        if not content:
            continue
        
        for analyzer in analyzers:
            if analyzer.can_analyze(file_path):
                issues = analyzer.analyze(file_path, content)
                result.issues.extend(issues)
    
    print(f"静态分析完成，发现 {len(result.issues)} 个问题")
    
    # AI审查
    if args.ai or config.get("ai.enabled", False):
        ai_config = config.get_ai_config()
        
        backend_name = args.backend or ai_config.get("backend", "openai")
        model = args.model or ai_config.get("model")
        api_key = args.api_key or ai_config.get("api_key")
        
        backend = None
        
        if backend_name == "openai":
            backend = OpenAIBackend({
                "api_key": api_key,
                "model": model or "gpt-4o-mini",
            })
        elif backend_name == "anthropic":
            backend = AnthropicBackend({
                "api_key": api_key,
                "model": model or "claude-3-haiku-20240307",
            })
        elif backend_name == "ollama":
            backend = OllamaBackend({
                "model": model or "codellama",
            })
        
        if backend and backend.is_available():
            print(f"正在进行AI审查 ({backend.description})...")
            
            # 对每个文件进行AI审查
            ai_results = []
            for file_path in files_to_analyze[:5]:  # 限制前5个文件
                content = read_file(file_path)
                if len(content) > 10000:  # 限制文件大小
                    content = content[:10000] + "\n... (truncated)"
                
                review_result = backend.review(content, file_path)
                ai_results.append(review_result)
            
            # 合并AI审查结果
            if ai_results:
                from .ai.base import ReviewResult, ReviewComment
                
                all_comments = []
                all_strengths = []
                all_improvements = []
                
                for r in ai_results:
                    all_comments.extend(r.comments)
                    all_strengths.extend(r.strengths)
                    all_improvements.extend(r.improvements)
                
                result.ai_review = ReviewResult(
                    summary=f"AI审查了 {len(ai_results)} 个文件",
                    comments=all_comments[:20],  # 限制评论数量
                    score=int(sum(r.score for r in ai_results) / len(ai_results)),
                    strengths=list(set(all_strengths))[:10],
                    improvements=list(set(all_improvements))[:10],
                )
        else:
            print(f"警告: AI后端 '{backend_name}' 不可用，请检查配置")
    
    result.end_time = datetime.now()
    
    return result


def generate_report(result: AnalysisResult, args, config: Config) -> str:
    """生成报告"""
    report_format = args.format or config.get("report.format", "console")
    
    reporter_config = {
        "color": not args.no_color and config.get("report.color", True),
        "show_code": config.get("report.show_code", True),
    }
    
    if report_format == "console":
        reporter = ConsoleReporter(reporter_config)
    elif report_format == "markdown":
        reporter = MarkdownReporter(reporter_config)
    elif report_format == "json":
        reporter = JSONReporter(reporter_config)
    elif report_format == "html":
        reporter = HTMLReporter(reporter_config)
    elif report_format == "sarif":
        reporter = SARIFReporter(reporter_config)
    else:
        reporter = ConsoleReporter(reporter_config)
    
    return reporter.generate(result)


def main(args: Optional[List[str]] = None) -> int:
    """主入口"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # 初始化配置文件
    if parsed_args.init:
        config_path = Config.init_config_file()
        print(f"✅ 配置文件已创建: {config_path}")
        print("请编辑配置文件，设置AI API密钥等选项")
        return 0
    
    # 加载配置
    config = Config.load(parsed_args.config)
    
    # 运行分析
    result = run_analysis(parsed_args, config)
    
    # 生成报告
    report = generate_report(result, parsed_args, config)
    
    # 输出报告
    if parsed_args.output:
        with open(parsed_args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n✅ 报告已保存: {parsed_args.output}")
    else:
        print()
        print(report)
    
    # 根据问题严重程度返回退出码
    counts = result.get_issue_counts()
    if counts["critical"] > 0:
        return 2
    elif counts["high"] > 0:
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
