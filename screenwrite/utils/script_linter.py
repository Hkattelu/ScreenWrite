"""
Script linting utilities for validating markdown script quality.

This module provides linting functions to help users write better video scripts
by identifying common formatting issues and suggestions for improvement.
"""

import re
from typing import List, Tuple


class ScriptLintIssue:
    """Represents a linting issue found in a script."""
    
    def __init__(self, line_number: int, severity: str, message: str):
        """
        Initialize a linting issue.
        
        Args:
            line_number: Line number where issue was found
            severity: Severity level ('info', 'warning', 'error')
            message: Description of the issue
        """
        self.line_number = line_number
        self.severity = severity
        self.message = message
    
    def __str__(self) -> str:
        """Return formatted issue string."""
        return f"Line {self.line_number} [{self.severity.upper()}]: {self.message}"


def lint_script(script_content: str) -> List[ScriptLintIssue]:
    """
    Lint a markdown script and return list of issues.
    
    Args:
        script_content: Full markdown script content
        
    Returns:
        List of ScriptLintIssue objects
    """
    issues = []
    lines = script_content.split('\n')
    
    # Track state
    has_headers = False
    body_line_count = 0
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        if not stripped:
            continue
        
        # Check for headers
        if stripped.startswith('#'):
            has_headers = True
            # Warn about inconsistent header spacing
            if stripped.startswith('##'):
                if not stripped.startswith('## '):
                    issues.append(ScriptLintIssue(
                        i, 'warning', 
                        "Use space after ## (e.g., '## Section Name')"
                    ))
        else:
            body_line_count += 1
            word_count = len(stripped.split())
            
            # Check for very long paragraphs
            if word_count > 40:
                issues.append(ScriptLintIssue(
                    i, 'warning',
                    f"Very long paragraph ({word_count} words). Consider breaking into 2-3 sentences."
                ))
            
            # Check for very short paragraphs (might be incomplete)
            if word_count < 5 and not stripped.startswith('-'):
                issues.append(ScriptLintIssue(
                    i, 'info',
                    f"Very short paragraph ({word_count} words). Might be incomplete."
                ))
            
            # Check for unclear pronouns without context
            if re.search(r'\b(it|that|this|them)\b', stripped, re.IGNORECASE):
                # If line is mostly pronouns without nouns, warn
                nouns = re.findall(r'\b[A-Z][a-z]+\b', stripped)
                if len(nouns) == 0 and word_count < 10:
                    issues.append(ScriptLintIssue(
                        i, 'info',
                        "Pronouns used without clear context. Consider adding specific terms."
                    ))
            
            # Warn about code blocks in voiceover (should be describe, not code)
            if '`' in stripped or '```' in stripped:
                issues.append(ScriptLintIssue(
                    i, 'warning',
                    "Avoid code snippets in voiceover. Describe what the code does instead."
                ))
    
    # Check overall script structure
    if not has_headers:
        issues.insert(0, ScriptLintIssue(
            1, 'warning',
            "No markdown headers found. Use # and ## to structure sections."
        ))
    
    if body_line_count == 0:
        issues.insert(0, ScriptLintIssue(
            1, 'error',
            "No body text found. Script only contains headers."
        ))
    
    return issues


def lint_script_file(file_path: str) -> List[ScriptLintIssue]:
    """
    Lint a markdown script file.
    
    Args:
        file_path: Path to markdown script file
        
    Returns:
        List of ScriptLintIssue objects
        
    Raises:
        IOError: If file cannot be read
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return lint_script(content)


def print_lint_issues(issues: List[ScriptLintIssue], verbose: bool = False) -> None:
    """
    Print linting issues in a user-friendly format.
    
    Args:
        issues: List of ScriptLintIssue objects
        verbose: Print all issues (warnings, info), else only errors
    """
    if not issues:
        print("No script issues found.")
        return
    
    # Filter by severity if not verbose
    if not verbose:
        issues = [i for i in issues if i.severity == 'error']
    
    if not issues:
        return
    
    print(f"\nScript Linting Results ({len(issues)} {'issue' if len(issues) == 1 else 'issues'}):")
    
    # Group by severity
    errors = [i for i in issues if i.severity == 'error']
    warnings = [i for i in issues if i.severity == 'warning']
    infos = [i for i in issues if i.severity == 'info']
    
    if errors:
        print(f"\n❌ Errors ({len(errors)}):")
        for issue in errors:
            print(f"  {issue}")
    
    if warnings:
        print(f"\n⚠️  Warnings ({len(warnings)}):")
        for issue in warnings:
            print(f"  {issue}")
    
    if infos and verbose:
        print(f"\nℹ️  Info ({len(infos)}):")
        for issue in infos:
            print(f"  {issue}")
