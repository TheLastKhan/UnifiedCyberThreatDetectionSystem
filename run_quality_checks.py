"""
Code Quality and Coverage Analysis Script for FAZ 2
"""

import subprocess
import sys
import json
from pathlib import Path

def run_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("RUNNING TESTS")
    print("="*70)
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=False
    )
    
    return result.returncode == 0

def run_flake8():
    """Run flake8 code style check."""
    print("\n" + "="*70)
    print("CODE STYLE CHECK (flake8)")
    print("="*70)
    
    result = subprocess.run(
        [sys.executable, "-m", "flake8", "src/", "tests/", "--max-line-length=100"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("No style issues found!")
    else:
        print("Style issues found:")
        print(result.stdout)
    
    return result.returncode == 0

def run_pylint():
    """Run pylint for code quality."""
    print("\n" + "="*70)
    print("CODE QUALITY CHECK (pylint)")
    print("="*70)
    
    files_to_check = [
        "src/email_detector/detector.py",
        "src/web_analyzer/analyzer.py",
        "src/unified_platform/platform.py"
    ]
    
    for file in files_to_check:
        print(f"\nChecking {file}...")
        result = subprocess.run(
            [sys.executable, "-m", "pylint", file, "--disable=C0111,C0103,R0913"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"  No issues")
        else:
            # Extract score from pylint output
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Your code has been rated' in line:
                    print(f"  {line.strip()}")

def count_tests():
    """Count test statistics."""
    print("\n" + "="*70)
    print("TEST STATISTICS")
    print("="*70)
    
    test_dir = Path("tests")
    test_files = list(test_dir.glob("test_*.py"))
    
    total_tests = 0
    test_info = []
    
    for test_file in test_files:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            num_tests = content.count("def test_")
            total_tests += num_tests
            test_info.append((test_file.name, num_tests))
    
    for filename, count in test_info:
        print(f"  {filename:<40} {count:>3} tests")
    
    print(f"\n  {'TOTAL':<40} {total_tests:>3} tests")

def count_lines():
    """Count lines of code."""
    print("\n" + "="*70)
    print("CODE STATISTICS")
    print("="*70)
    
    src_dir = Path("src")
    py_files = list(src_dir.rglob("*.py"))
    
    total_lines = 0
    
    for py_file in py_files:
        with open(py_file, 'r', encoding='utf-8') as f:
            lines = len(f.readlines())
            total_lines += lines
            relative_path = str(py_file.relative_to('.'))
            print(f"  {relative_path:<50} {lines:>5} lines")
    
    print(f"\n  {'TOTAL':<50} {total_lines:>5} lines")

def main():
    """Run all checks."""
    print("\n")
    print("=" * 70)
    print("FAZ 2 - TEST & KALITE KONTROL RAPORU".center(70))
    print("=" * 70)
    
    # Run checks
    tests_passed = run_tests()
    flake8_passed = run_flake8()
    run_pylint()
    
    # Count statistics
    count_tests()
    count_lines()
    
    # Summary
    print("\n" + "="*70)
    print("OZET")
    print("="*70)
    
    tests_status = "PASSED" if tests_passed else "FAILED"
    flake8_status = "PASSED" if flake8_passed else "HAS ISSUES"
    
    print(f"Tests:           {tests_status}")
    print(f"Code Style:      {flake8_status}")
    print(f"Code Quality:    (See pylint output above)")
    
    print("\n" + "="*70)
    print("FAZ 2 KONTROL TAMAMLANDI")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
