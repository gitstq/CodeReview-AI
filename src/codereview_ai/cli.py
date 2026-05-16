"""
Command-line interface for CodeReview-AI
命令行接口模块
"""

import argparse
import sys
import os
from typing import Optional, List

from .core import CodeReviewer
from .reporters import ConsoleReporter, JSONReporter, MarkdownReporter, HTMLReporter


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog='codereview-ai',
        description='🔍 CodeReview-AI: Lightweight AI Code Review Assistant',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Review a single file
  codereview-ai review file.py

  # Review entire directory
  codereview-ai review ./src --format markdown -o report.md

  # Review git changes
  codereview-ai diff HEAD~1

  # Use LLM for enhanced analysis
  codereview-ai review ./src --llm openai --api-key $OPENAI_API_KEY

  # Generate HTML report
  codereview-ai review ./src --format html -o report.html

For more information: https://github.com/gitstq/codereview-ai
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Review command
    review_parser = subparsers.add_parser(
        'review',
        help='Review code files or directories',
        description='Review code for issues, bugs, and improvements'
    )
    review_parser.add_argument(
        'path',
        help='File or directory path to review'
    )
    review_parser.add_argument(
        '-f', '--format',
        choices=['console', 'json', 'markdown', 'html'],
        default='console',
        help='Output format (default: console)'
    )
    review_parser.add_argument(
        '-o', '--output',
        help='Output file path (default: stdout)'
    )
    review_parser.add_argument(
        '--llm',
        choices=['openai', 'anthropic', 'claude', 'deepseek'],
        help='LLM backend for enhanced analysis'
    )
    review_parser.add_argument(
        '--api-key',
        help='API key for LLM backend (or set env var)'
    )
    review_parser.add_argument(
        '--model',
        help='Model name for LLM backend'
    )
    review_parser.add_argument(
        '--no-static',
        action='store_true',
        help='Disable static analysis'
    )
    review_parser.add_argument(
        '--exclude',
        nargs='+',
        default=['.git', '__pycache__', 'node_modules', 'venv', '.venv', 'dist', 'build'],
        help='Directories to exclude from analysis'
    )
    review_parser.add_argument(
        '--max-file-size',
        type=int,
        default=500000,
        help='Maximum file size in bytes (default: 500000)'
    )

    # Diff command
    diff_parser = subparsers.add_parser(
        'diff',
        help='Review git diff changes',
        description='Review files changed in git commits'
    )
    diff_parser.add_argument(
        'base_ref',
        nargs='?',
        default='HEAD~1',
        help='Base git reference (default: HEAD~1)'
    )
    diff_parser.add_argument(
        '-r', '--repo',
        default='.',
        help='Repository path (default: current directory)'
    )
    diff_parser.add_argument(
        '-f', '--format',
        choices=['console', 'json', 'markdown', 'html'],
        default='console',
        help='Output format'
    )
    diff_parser.add_argument(
        '-o', '--output',
        help='Output file path'
    )
    diff_parser.add_argument(
        '--llm',
        choices=['openai', 'anthropic', 'claude', 'deepseek'],
        help='LLM backend'
    )
    diff_parser.add_argument(
        '--api-key',
        help='API key'
    )

    # Config command
    config_parser = subparsers.add_parser(
        'config',
        help='Show configuration information',
        description='Display configuration and environment info'
    )

    return parser


def get_api_key(backend: str, provided_key: Optional[str]) -> Optional[str]:
    """Get API key from argument or environment"""
    if provided_key:
        return provided_key

    env_vars = {
        'openai': 'OPENAI_API_KEY',
        'anthropic': 'ANTHROPIC_API_KEY',
        'claude': 'ANTHROPIC_API_KEY',
        'deepseek': 'DEEPSEEK_API_KEY',
    }

    env_var = env_vars.get(backend.lower())
    if env_var:
        return os.getenv(env_var)

    return None


def handle_review(args) -> int:
    """Handle review command"""
    path = args.path

    if not os.path.exists(path):
        print(f"Error: Path not found: {path}", file=sys.stderr)
        return 1

    # Initialize reviewer
    llm_backend = args.llm
    api_key = get_api_key(llm_backend, args.api_key) if llm_backend else None

    reviewer = CodeReviewer(
        llm_backend=llm_backend,
        api_key=api_key,
        model=args.model,
        use_static_analysis=not args.no_static,
        use_llm=bool(llm_backend),
        max_file_size=args.max_file_size,
    )

    # Perform review
    if os.path.isfile(path):
        results = [reviewer.review_file(path)]
    else:
        results = reviewer.review_directory(path, exclude_patterns=args.exclude)

    # Generate report
    output = generate_report(results, args.format)

    # Output results
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Report saved to: {args.output}")
        except IOError as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            return 1
    else:
        print(output)

    # Return exit code based on issues found
    total_issues = sum(len(r.issues) for r in results)
    return 1 if total_issues > 0 else 0


def handle_diff(args) -> int:
    """Handle diff command"""
    llm_backend = args.llm
    api_key = get_api_key(llm_backend, args.api_key) if llm_backend else None

    reviewer = CodeReviewer(
        llm_backend=llm_backend,
        api_key=api_key,
        use_static_analysis=True,
        use_llm=bool(llm_backend),
    )

    results = reviewer.review_git_diff(args.repo, args.base_ref)

    if not results:
        print("No supported files found in git diff.")
        return 0

    output = generate_report(results, args.format)

    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Report saved to: {args.output}")
        except IOError as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            return 1
    else:
        print(output)

    total_issues = sum(len(r.issues) for r in results)
    return 1 if total_issues > 0 else 0


def handle_config(args) -> int:
    """Handle config command"""
    print("🔧 CodeReview-AI Configuration")
    print("=" * 50)
    print()

    # Check environment variables
    env_vars = [
        ('OPENAI_API_KEY', 'OpenAI API Key'),
        ('ANTHROPIC_API_KEY', 'Anthropic API Key'),
        ('DEEPSEEK_API_KEY', 'DeepSeek API Key'),
    ]

    print("Environment Variables:")
    for var, description in env_vars:
        value = os.getenv(var, '')
        status = '✅ Set' if value else '❌ Not set'
        masked = f"{value[:8]}..." if value and len(value) > 8 else value
        print(f"  {var}: {status} ({masked if value else 'N/A'})")

    print()
    print("Supported File Types:")
    extensions = CodeReviewer.SUPPORTED_EXTENSIONS
    ext_list = sorted(extensions)
    for i in range(0, len(ext_list), 8):
        print("  " + ", ".join(ext_list[i:i+8]))

    print()
    print("Supported LLM Backends:")
    print("  - openai (gpt-4o-mini, gpt-4o)")
    print("  - anthropic/claude (claude-3-haiku, claude-3-sonnet)")
    print("  - deepseek (deepseek-chat)")

    return 0


def generate_report(results, format_type: str) -> str:
    """Generate report in specified format"""
    if format_type == 'json':
        reporter = JSONReporter()
    elif format_type == 'markdown':
        reporter = MarkdownReporter()
    elif format_type == 'html':
        reporter = HTMLReporter()
    else:
        reporter = ConsoleReporter(use_colors=sys.stdout.isatty())

    return reporter.report(results)


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 1

    if parsed_args.command == 'review':
        return handle_review(parsed_args)
    elif parsed_args.command == 'diff':
        return handle_diff(parsed_args)
    elif parsed_args.command == 'config':
        return handle_config(parsed_args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())