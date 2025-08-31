#!/usr/bin/env python3
"""
Test runner for MarkItDown
Provides easy commands to run different types of tests
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run MarkItDown tests")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "performance", "all"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Run with coverage reporting"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Run with verbose output"
    )
    
    args = parser.parse_args()
    
    # Get the test directory
    test_dir = Path(__file__).parent
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        cmd.append("-v")
    
    if args.coverage:
        cmd.extend([
            "--cov=packages/markitdown/src/markitdown",
            "--cov-report=html",
            "--cov-report=term"
        ])
    
    # Add test path based on type
    if args.type == "all":
        cmd.append(str(test_dir))
    else:
        cmd.append(str(test_dir / args.type))
    
    # Run the tests
    success = run_command(cmd, f"{args.type.title()} tests")
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
