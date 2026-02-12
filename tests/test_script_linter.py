"""
Unit tests for script_linter utility.
"""

import unittest
import io
import os
import tempfile
from unittest.mock import patch
from screenwrite.utils.script_linter import (
    lint_script,
    lint_script_file,
    print_lint_issues,
    ScriptLintIssue
)


class TestScriptLinter(unittest.TestCase):
    """Test cases for script linter functions."""

    def test_lint_script_valid(self):
        """Test linting a valid script with no issues."""
        content = "# Title\n\n## Section\nThis is a perfectly valid paragraph with enough words and clear context."
        issues = lint_script(content)
        # Should have 0 issues (or at least no errors/warnings if it's too short)
        # Actually "This is a perfectly valid paragraph with enough words and clear context." is 12 words.
        # Short paragraph is < 5 words. So it should be fine.
        # It has a header. It has body text.
        self.assertEqual(len([i for i in issues if i.severity in ('error', 'warning')]), 0)

    def test_lint_script_no_headers(self):
        """Test warning for script without headers."""
        content = "This is a script without any markdown headers."
        issues = lint_script(content)
        self.assertTrue(any(i.severity == 'warning' and "No markdown headers found" in i.message for i in issues))

    def test_lint_script_no_body(self):
        """Test error for script without body text."""
        content = "# Title\n## Section"
        issues = lint_script(content)
        self.assertTrue(any(i.severity == 'error' and "No body text found" in i.message for i in issues))

    def test_lint_script_inconsistent_header_spacing(self):
        """Test warning for inconsistent header spacing."""
        content = "# Title\n##Section\nBody text here."
        issues = lint_script(content)
        self.assertTrue(any(i.severity == 'warning' and "Use space after ##" in i.message for i in issues))

    def test_lint_script_long_paragraph(self):
        """Test warning for very long paragraphs."""
        content = "# Title\n\n" + "word " * 41 + "."
        issues = lint_script(content)
        self.assertTrue(any(i.severity == 'warning' and "Very long paragraph" in i.message for i in issues))

    def test_lint_script_short_paragraph(self):
        """Test info for very short paragraphs."""
        content = "# Title\n\nShort."
        issues = lint_script(content)
        self.assertTrue(any(i.severity == 'info' and "Very short paragraph" in i.message for i in issues))

    def test_lint_script_unclear_pronouns(self):
        """Test info for unclear pronouns without context."""
        content = "# Title\n\nit is that."
        issues = lint_script(content)
        self.assertTrue(any(i.severity == 'info' and "Pronouns used without clear context" in i.message for i in issues))

        # Should not warn if there are capitalized nouns
        content_with_noun = "# Title\n\nPython is great. It is that."
        issues = lint_script(content_with_noun)
        self.assertFalse(any("Pronouns used without clear context" in i.message for i in issues))

    def test_lint_script_code_snippets(self):
        """Test warning for code snippets in voiceover."""
        content = "# Title\n\nUse `print()` to see output."
        issues = lint_script(content)
        self.assertTrue(any(i.severity == 'warning' and "Avoid code snippets" in i.message for i in issues))

    def test_lint_script_file(self):
        """Test lint_script_file correctly reads and lints a file."""
        content = "# Title\n##Section" # Has inconsistent spacing and no body
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            issues = lint_script_file(tmp_path)
            self.assertGreater(len(issues), 0)
            self.assertTrue(any("Use space after ##" in i.message for i in issues))
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_print_lint_issues_no_issues(self):
        """Test print_lint_issues with no issues."""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            print_lint_issues([])
            self.assertEqual(fake_out.getvalue().strip(), "No script issues found.")

    def test_print_lint_issues_with_issues_non_verbose(self):
        """Test print_lint_issues shows only errors by default."""
        issues = [
            ScriptLintIssue(1, 'error', "Error message"),
            ScriptLintIssue(2, 'warning', "Warning message")
        ]
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            print_lint_issues(issues, verbose=False)
            output = fake_out.getvalue()
            self.assertIn("Errors (1)", output)
            self.assertIn("Error message", output)
            self.assertNotIn("Warnings", output)
            self.assertNotIn("Warning message", output)

    def test_print_lint_issues_with_issues_verbose(self):
        """Test print_lint_issues shows everything in verbose mode."""
        issues = [
            ScriptLintIssue(1, 'error', "Error message"),
            ScriptLintIssue(2, 'warning', "Warning message"),
            ScriptLintIssue(3, 'info', "Info message")
        ]
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            print_lint_issues(issues, verbose=True)
            output = fake_out.getvalue()
            self.assertIn("Errors (1)", output)
            self.assertIn("Warnings (1)", output)
            self.assertIn("Info (1)", output)
            self.assertIn("Error message", output)
            self.assertIn("Warning message", output)
            self.assertIn("Info message", output)


if __name__ == '__main__':
    unittest.main()
