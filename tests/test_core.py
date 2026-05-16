"""
Tests for core module
"""

import unittest
import tempfile
import os
from src.codereview_ai.core import (
    CodeReviewer, CodeIssue, ReviewResult,
    Severity, IssueType
)


class TestCodeIssue(unittest.TestCase):
    """Test CodeIssue dataclass"""

    def test_issue_creation(self):
        issue = CodeIssue(
            file_path="test.py",
            line_number=10,
            column=5,
            severity=Severity.HIGH,
            issue_type=IssueType.BUG,
            message="Test message",
            suggestion="Test suggestion",
            rule_id="TEST-001"
        )

        self.assertEqual(issue.file_path, "test.py")
        self.assertEqual(issue.line_number, 10)
        self.assertEqual(issue.severity, Severity.HIGH)

    def test_issue_to_dict(self):
        issue = CodeIssue(
            file_path="test.py",
            line_number=1,
            column=0,
            severity=Severity.LOW,
            issue_type=IssueType.STYLE,
            message="Test",
            suggestion="Fix it",
            rule_id="TEST-001"
        )

        d = issue.to_dict()
        self.assertEqual(d["file_path"], "test.py")
        self.assertEqual(d["severity"], "low")


class TestReviewResult(unittest.TestCase):
    """Test ReviewResult class"""

    def test_result_creation(self):
        result = ReviewResult(file_path="test.py")
        self.assertEqual(result.file_path, "test.py")
        self.assertEqual(len(result.issues), 0)

    def test_add_issue(self):
        result = ReviewResult(file_path="test.py")
        issue = CodeIssue(
            file_path="test.py",
            line_number=1,
            column=0,
            severity=Severity.INFO,
            issue_type=IssueType.DOCUMENTATION,
            message="Test",
            rule_id="TEST-001"
        )
        result.add_issue(issue)

        self.assertEqual(len(result.issues), 1)


class TestCodeReviewer(unittest.TestCase):
    """Test CodeReviewer class"""

    def setUp(self):
        self.reviewer = CodeReviewer(use_static_analysis=True, use_llm=False)

    def test_review_python_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("password = 'secret'\n")
            f.write("eval('1+1')\n")
            temp_path = f.name

        try:
            result = self.reviewer.review_file(temp_path)
            self.assertIsInstance(result, ReviewResult)
            self.assertEqual(result.file_path, temp_path)
        finally:
            os.unlink(temp_path)

    def test_review_nonexistent_file(self):
        result = self.reviewer.review_file("/nonexistent/file.py")
        self.assertIn("error", result.summary)

    def test_review_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            with open(os.path.join(tmpdir, "test.py"), 'w') as f:
                f.write("x = 1\n")

            results = self.reviewer.review_directory(tmpdir)
            self.assertIsInstance(results, list)

    def test_supported_extensions(self):
        self.assertIn('.py', CodeReviewer.SUPPORTED_EXTENSIONS)
        self.assertIn('.js', CodeReviewer.SUPPORTED_EXTENSIONS)


if __name__ == '__main__':
    unittest.main()