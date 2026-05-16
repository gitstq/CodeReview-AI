"""
Tests for reporters module
"""

import unittest
from src.codereview_ai.reporters import (
    ConsoleReporter, JSONReporter, MarkdownReporter, HTMLReporter
)
from src.codereview_ai.core import ReviewResult, CodeIssue, Severity, IssueType


class TestConsoleReporter(unittest.TestCase):
    """Test console reporter"""

    def setUp(self):
        self.reporter = ConsoleReporter(use_colors=False)

    def test_empty_report(self):
        results = []
        output = self.reporter.report(results)
        self.assertIn("CodeReview-AI Report", output)

    def test_report_with_issues(self):
        result = ReviewResult(file_path="test.py")
        issue = CodeIssue(
            file_path="test.py",
            line_number=10,
            column=5,
            severity=Severity.HIGH,
            issue_type=IssueType.BUG,
            message="Test issue",
            suggestion="Fix it",
            rule_id="TEST-001"
        )
        result.add_issue(issue)

        output = self.reporter.report([result])
        self.assertIn("test.py", output)
        self.assertIn("Test issue", output)


class TestJSONReporter(unittest.TestCase):
    """Test JSON reporter"""

    def setUp(self):
        self.reporter = JSONReporter()

    def test_json_output(self):
        result = ReviewResult(file_path="test.py")
        output = self.reporter.report([result])

        self.assertIn('"meta"', output)
        self.assertIn('"summary"', output)
        self.assertIn('"results"', output)


class TestMarkdownReporter(unittest.TestCase):
    """Test Markdown reporter"""

    def setUp(self):
        self.reporter = MarkdownReporter()

    def test_markdown_output(self):
        result = ReviewResult(file_path="test.py")
        output = self.reporter.report([result])

        self.assertIn("# CodeReview-AI Report", output)
        self.assertIn("## 📊 Summary", output)


class TestHTMLReporter(unittest.TestCase):
    """Test HTML reporter"""

    def setUp(self):
        self.reporter = HTMLReporter()

    def test_html_output(self):
        result = ReviewResult(file_path="test.py")
        output = self.reporter.report([result])

        self.assertIn("<!DOCTYPE html>", output)
        self.assertIn("CodeReview-AI Report", output)


if __name__ == '__main__':
    unittest.main()