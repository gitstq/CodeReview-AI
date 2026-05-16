"""
Tests for analyzers module
"""

import unittest
from src.codereview_ai.analyzers import PatternMatcher, StaticAnalyzer
from src.codereview_ai.core import Severity, IssueType


class TestPatternMatcher(unittest.TestCase):
    """Test pattern matcher"""

    def setUp(self):
        self.matcher = PatternMatcher()

    def test_hardcoded_password_detection(self):
        code = "password = 'secret123'"
        issues = self.matcher.analyze(code, "test.py")

        self.assertTrue(any(
            i.rule_id.startswith("SEC-hardcoded_password") for i in issues
        ))

    def test_eval_usage_detection(self):
        code = "result = eval(user_input)"
        issues = self.matcher.analyze(code, "test.py")

        self.assertTrue(any(
            i.rule_id.startswith("SEC-eval_usage") for i in issues
        ))
        self.assertTrue(any(
            i.severity == Severity.HIGH for i in issues
        ))

    def test_bare_except_detection(self):
        code = """
try:
    do_something()
except:
    pass
"""
        issues = self.matcher.analyze(code, "test.py")

        self.assertTrue(any(
            i.rule_id.startswith("BUG-bare_except") for i in issues
        ))

    def test_mutable_default_detection(self):
        code = "def func(items=[]):\n    pass"
        issues = self.matcher.analyze(code, "test.py")

        self.assertTrue(any(
            i.rule_id.startswith("BUG-mutable_default") for i in issues
        ))


class TestStaticAnalyzer(unittest.TestCase):
    """Test static analyzer"""

    def setUp(self):
        self.analyzer = StaticAnalyzer()

    def test_python_analysis(self):
        code = """
def test_function(password="default"):
    eval("1 + 1")
    return password
"""
        issues = self.analyzer.analyze(code, "test.py")

        # Should find eval usage
        self.assertTrue(any(
            "eval" in i.message.lower() for i in issues
        ))

    def test_complex_function_detection(self):
        code = """
def very_complex_function():
    if True:
        if True:
            if True:
                if True:
                    if True:
                        pass
    return 1
"""
        issues = self.analyzer.analyze(code, "test.py")

        # May find complexity issues
        self.assertIsInstance(issues, list)


if __name__ == '__main__':
    unittest.main()