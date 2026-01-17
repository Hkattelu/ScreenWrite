"""
Unified test runner and linting script for vid-orchestrator.

Runs linting checks (flake8, pylint) and all test suites.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description, check=True):
    """Run a command and report results."""
    print(f"\n{'='*70}")
    print(f"{description}")
    print(f"{'='*70}")
    print(f"Running: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=False,
            text=True,
            check=check
        )
        
        if result.returncode == 0:
            print(f"\n✓ {description} - PASSED")
            return True
        else:
            print(f"\n✗ {description} - FAILED (exit code: {result.returncode})")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {description} - FAILED (exit code: {e.returncode})")
        return False
    except FileNotFoundError:
        print(f"\n✗ {description} - SKIPPED (command not found)")
        return None


def run_flake8(target_dirs):
    """Run flake8 linting."""
    cmd = ["flake8"] + target_dirs
    return run_command(cmd, "Flake8 Linting", check=False)


def run_pylint(target_dirs):
    """Run pylint linting."""
    cmd = ["pylint"] + target_dirs
    return run_command(cmd, "Pylint Analysis", check=False)


def run_tests(verbose=False):
    """Run all unit tests."""
    cmd = ["python", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, "Unit Tests", check=False)


def run_coverage():
    """Run tests with coverage reporting."""
    print(f"\n{'='*70}")
    print("Test Coverage Analysis")
    print(f"{'='*70}\n")
    
    # Check if coverage is installed
    try:
        subprocess.run(["coverage", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Coverage - SKIPPED (coverage not installed)")
        print("  Install with: pip install coverage")
        return None
    
    # Run tests with coverage
    print("Running tests with coverage...\n")
    result1 = subprocess.run(
        ["coverage", "run", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        capture_output=False
    )
    
    if result1.returncode != 0:
        print("\n✗ Coverage - FAILED (tests failed)")
        return False
    
    # Generate coverage report
    print("\nGenerating coverage report...\n")
    result2 = subprocess.run(
        ["coverage", "report", "-m"],
        capture_output=False
    )
    
    # Generate HTML coverage report
    print("\nGenerating HTML coverage report...")
    subprocess.run(
        ["coverage", "html"],
        capture_output=True
    )
    print("HTML coverage report generated in: htmlcov/index.html")
    
    if result2.returncode == 0:
        print("\n✓ Coverage - PASSED")
        return True
    else:
        print("\n✗ Coverage - FAILED")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run linting and tests for vid-orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_lint_and_tests.py                # Run everything
  python run_lint_and_tests.py --lint-only    # Run only linting
  python run_lint_and_tests.py --tests-only   # Run only tests
  python run_lint_and_tests.py --coverage     # Run tests with coverage
  python run_lint_and_tests.py --fast         # Quick checks only
        """
    )
    
    parser.add_argument(
        "--lint-only",
        action="store_true",
        help="Run only linting checks (skip tests)"
    )
    
    parser.add_argument(
        "--tests-only",
        action="store_true",
        help="Run only tests (skip linting)"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage reporting"
    )
    
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Run only flake8 and quick tests (skip pylint)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose test output"
    )
    
    args = parser.parse_args()
    
    # Determine project root
    project_root = Path(__file__).parent
    
    # Target directories for linting
    target_dirs = [
        str(project_root / "vid_orchestrator"),
        str(project_root / "tests")
    ]
    
    results = {
        "flake8": None,
        "pylint": None,
        "tests": None,
        "coverage": None
    }
    
    print(f"\nvid-orchestrator Quality Checks")
    print(f"Project root: {project_root}")
    
    # Run linting checks
    if not args.tests_only:
        results["flake8"] = run_flake8(target_dirs)
        
        if not args.fast:
            results["pylint"] = run_pylint(target_dirs)
    
    # Run tests
    if not args.lint_only:
        if args.coverage:
            results["coverage"] = run_coverage()
        else:
            results["tests"] = run_tests(verbose=args.verbose)
    
    # Print summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}\n")
    
    passed = 0
    failed = 0
    skipped = 0
    
    for name, result in results.items():
        if result is True:
            status = "✓ PASSED"
            passed += 1
        elif result is False:
            status = "✗ FAILED"
            failed += 1
        else:
            status = "- SKIPPED"
            skipped += 1
        
        print(f"{name:15} {status}")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    # Determine exit code
    if failed > 0:
        print("\n✗ Some checks failed")
        return 1
    elif passed > 0:
        print("\n✓ All checks passed!")
        return 0
    else:
        print("\n- No checks were run")
        return 0


if __name__ == "__main__":
    sys.exit(main())
