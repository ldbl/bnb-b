#!/usr/bin/env python3
"""
Golden 21/21 Regression Test - MUST PASS

This test protects the perfect 21/21 LONG accuracy system.
Any change that breaks this test breaks the core system and must be reverted.

Usage:
    python3 tests/test_golden_regression.py

Expected output:
    ✅ 21/21 signals maintained

If this fails, the system is broken and needs immediate attention.
"""

import os
import re
import subprocess
import sys
from pathlib import Path


def test_21_signals_regression() -> None:
    """
    CRITICAL: Verify system maintains 21/21 LONG signals with 100% accuracy

    This is the most important test in the entire system.
    """
    print("🛡️ Running Golden 21/21 Regression Test...")

    try:
        # Run backtest from project root
        project_root = Path(__file__).parent.parent

        # Ensure data directory exists for backtest output files
        project_root.joinpath("data").mkdir(parents=True, exist_ok=True)

        # Set up environment with absolute src path prepended to PYTHONPATH
        env = os.environ.copy()
        src_path = os.path.abspath(project_root / "src")
        existing_pythonpath = env.get("PYTHONPATH", "")
        if existing_pythonpath:
            env["PYTHONPATH"] = f"{src_path}{os.pathsep}{existing_pythonpath}"
        else:
            env["PYTHONPATH"] = src_path

        result = subprocess.run(
            [sys.executable, str(project_root / "run_enhanced_backtest.py")],
            check=False,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            env=env,  # Pass environment with proper PYTHONPATH
        )

        if result.returncode != 0:
            print("❌ REGRESSION: Backtest failed with error")
            print("STDERR:", result.stderr)
            print("STDOUT:", result.stdout)
            raise AssertionError("Backtest failed with errors")

        output = result.stdout

        # Extract signal count
        signal_match = re.search(r"LONG Signals:\s*(\d+)", output)
        if not signal_match:
            print("❌ REGRESSION: Could not find LONG Signals count in output")
            print("Output:", output[-500:])  # Last 500 chars
            raise AssertionError("Could not find LONG Signals count in output")

        signals = int(signal_match.group(1))
        if signals != 21:
            print(f"❌ REGRESSION: Only {signals} signals (expected 21)")
            print("This breaks the perfect system!")
            raise AssertionError(f"Only {signals} signals (expected 21)")

        # Extract accuracy
        accuracy_match = re.search(r"Accuracy:\s*([\d.]+)%", output)
        if not accuracy_match:
            print("❌ REGRESSION: Could not find accuracy in output")
            print("Output:", output[-500:])  # Last 500 chars
            raise AssertionError("Could not find accuracy in output")

        accuracy = float(accuracy_match.group(1))
        if accuracy < 100.0:
            print(f"❌ REGRESSION: Only {accuracy}% accuracy (expected 100%)")
            print("This breaks the perfect system!")
            raise AssertionError(f"Only {accuracy}% accuracy (expected 100%)")

        print("✅ 21/21 signals maintained")
        print("✅ 100% accuracy preserved")

    except subprocess.TimeoutExpired:
        print("❌ REGRESSION: Backtest timed out (>5 minutes)")
        print("This suggests the system is broken or hanging")
        raise AssertionError("Backtest timed out (>5 minutes)") from None

    except Exception as e:
        print(f"❌ REGRESSION: Test failed with exception: {e}")
        raise AssertionError(f"Test failed with exception: {e}") from e


def main() -> None:
    """Run regression test and exit with proper code"""
    try:
        test_21_signals_regression()
        print("\n🏆 REGRESSION TEST PASSED")
        print("The perfect 21/21 LONG accuracy system is preserved!")
        sys.exit(0)
    except AssertionError as e:
        print("\n🚨 REGRESSION TEST FAILED")
        print("The perfect system is broken - immediate attention required!")
        print("Revert recent changes and investigate!")
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print("\n🚨 REGRESSION TEST FAILED")
        print("The perfect system is broken - immediate attention required!")
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
