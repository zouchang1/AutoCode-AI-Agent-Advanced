"""
auto_code_ai_agent_advanced/tester.py
Automated test runner with structured output parsing.

Wraps pytest execution and provides pass/fail breakdowns,
error summaries, and execution performance metrics.
"""

from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class TestResult:
    """Parsed test execution result."""

    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    duration_sec: float = 0.0
    exit_code: int = -1
    raw_output: str = ""
    failed_tests: List[str] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)


class TestRunner:
    """Discover and run tests in a project directory."""

    def __init__(self, project_path: str, test_path: Optional[str] = None):
        self.project_path = Path(project_path).resolve()
        self.test_path = Path(test_path).resolve() if test_path else self.project_path / "tests"
        self.log_path = self.project_path / "logs"

    def discover(self) -> List[str]:
        """List discovered test files."""
        if not self.test_path.is_dir():
            return []
        return sorted(str(p.relative_to(self.project_path)) for p in self.test_path.rglob("test_*.py"))

    def run(self, extra_args: Optional[List[str]] = None) -> TestResult:
        """Execute pytest and parse results."""
        start = time.time()

        self.log_path.mkdir(parents=True, exist_ok=True)

        cmd = [
            sys.executable or "python",
            "-m",
            "pytest",
            str(self.test_path),
            "-v",
            "--tb=short",
        ]
        if extra_args:
            cmd.extend(extra_args)

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=300,
            )
        except subprocess.TimeoutExpired:
            return TestResult(
                exit_code=-9,
                duration_sec=time.time() - start,
                raw_output="[TIMEOUT] Test execution exceeded 300 seconds.",
            )

        duration = time.time() - start
        output = proc.stdout + "\n" + proc.stderr

        # Parse output
        result = TestResult(
            exit_code=proc.returncode,
            duration_sec=round(duration, 2),
            raw_output=output,
        )

        # Parse short summary line: "= 12 passed, 3 failed in 4.52s ="
        for line in output.split("\n"):
            line = line.strip()
            if not line.startswith("="):
                continue
            if "passed" in line or "failed" in line or "error" in line:
                result.passed = self._extract_number(line, "passed")
                result.failed = self._extract_number(line, "failed")
                result.errors = self._extract_number(line, "errors")
                result.skipped = self._extract_number(line, "skipped")

            # Collect failed test names
            if "FAILED" in line:
                # "FAILED tests/test_x.py::test_func - AssertionError: ..."
                parts = line.split("FAILED", 1)
                if len(parts) > 1:
                    test_name = parts[1].strip().split(" - ")[0].strip()
                    result.failed_tests.append(test_name)
                    if " - " in parts[1]:
                        msg = parts[1].split(" - ", 1)[1].strip()
                        result.error_messages.append(msg)

        # Write log
        log_file = self.log_path / f"test_run_{int(time.time())}.log"
        log_file.write_text(output, encoding="utf-8")

        return result

    @staticmethod
    def _extract_number(text: str, label: str) -> int:
        import re

        m = re.search(rf"(\d+)\s+{label}", text)
        return int(m.group(1)) if m else 0

    @staticmethod
    def result_to_markdown(result: TestResult) -> str:
        """Format test result as markdown summary."""
        total = result.passed + result.failed + result.errors + result.skipped
        lines = [
            "## Test Execution Report\n",
            f"| Metric | Value |",
            "|--------|------:|",
            f"| Total Tests | {total} |",
            f"| Passed | {result.passed} |",
            f"| Failed | {result.failed} |",
            f"| Errors | {result.errors} |",
            f"| Skipped | {result.skipped} |",
            f"| Duration | {result.duration_sec}s |",
            f"| Exit Code | {result.exit_code} |",
        ]

        if result.failed_tests:
            lines.append("\n### Failed Tests\n")
            for i, name in enumerate(result.failed_tests, 1):
                lines.append(f"{i}. `{name}`")
                if i - 1 < len(result.error_messages):
                    lines.append(f"   > {result.error_messages[i-1]}")

        if result.exit_code == -9:
            lines.append("\n⚠️ **Test execution timed out**")

        return "\n".join(lines) + "\n"