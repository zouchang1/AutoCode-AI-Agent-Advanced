"""
auto_code_ai_agent_advanced/pipeline.py
Agent orchestration pipeline.

Coordinates the full workflow:
  code_analysis → report_generation → test_execution → final_summary
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from .analyzer import CodeAnalyzer, AnalysisResult
from .report import ReportGenerator
from .tester import TestRunner, TestResult

logger = logging.getLogger("auto-agent")


class Pipeline:
    """Orchestrates the full multi-agent pipeline."""

    def __init__(self, target_path: str, output_dir: Optional[str] = None):
        self.target_path = Path(target_path).resolve()
        self.output_dir = (
            Path(output_dir).resolve() if output_dir else self.target_path / "logs"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.analyzer = CodeAnalyzer(str(self.target_path))
        self.reporter = ReportGenerator()
        self.tester = TestRunner(str(self.target_path))

    def run_full(self) -> dict:
        """Execute the complete pipeline: analyze → report → test → output."""
        logger.info("Starting full pipeline for %s", self.target_path)

        # Step 1: Analyze codebase
        analysis = self.analyzer.analyze()
        logger.info(
            "Analysis complete: %d files, %d code lines, %d markers",
            analysis.total_files,
            analysis.total_code_lines,
            analysis.total_markers,
        )

        # Step 2: Generate PR report
        report_md = self.reporter.generate(analysis)
        report_path = self.output_dir / "code_analysis_report.md"
        report_path.write_text(report_md, encoding="utf-8")
        logger.info("Report written to %s", report_path)

        # Step 3: Run tests
        test_result = self.tester.run()
        test_md = TestRunner.result_to_markdown(test_result)
        test_path = self.output_dir / "test_report.md"
        test_path.write_text(test_md, encoding="utf-8")
        logger.info("Test report written to %s", test_path)

        # Step 4: Combine
        combined = self._combine_reports(analysis, report_md, test_result, test_md)
        combined_path = self.output_dir / "full_pipeline_report.md"
        combined_path.write_text(combined, encoding="utf-8")
        logger.info("Combined report written to %s", combined_path)

        return {
            "analysis": {
                "total_files": analysis.total_files,
                "total_code_lines": analysis.total_code_lines,
                "total_markers": analysis.total_markers,
                "quality_score": analysis.quality_score,
                "languages": list(analysis.languages.keys()),
            },
            "report_path": str(report_path),
            "test": {
                "passed": test_result.passed,
                "failed": test_result.failed,
                "duration_sec": test_result.duration_sec,
            },
            "test_report_path": str(test_path),
            "combined_report_path": str(combined_path),
        }

    def run_analyze(self) -> AnalysisResult:
        """Run only the analysis step."""
        return self.analyzer.analyze()

    def run_report(self, analysis: AnalysisResult) -> str:
        """Generate report from analysis result."""
        return self.reporter.generate(analysis)

    def run_test(self) -> TestResult:
        """Run only the test step."""
        return self.tester.run()

    @staticmethod
    def _combine_reports(
        analysis: AnalysisResult,
        report_md: str,
        test_result: TestResult,
        test_md: str,
    ) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"# AutoCode AI Agent — Full Pipeline Report\n\n"
            f"> **Generated**: {now}  \n"
            f"> **Pipeline**: Analyze → Report → Test  \n"
            f"> **Project**: `{analysis.target_path}`  \n\n"
            "---\n\n"
            "## Summary\n\n"
            f"- **Files**: {analysis.total_files}  \n"
            f"- **Code Lines**: {analysis.total_code_lines:,}  \n"
            f"- **Quality Score**: {analysis.quality_score}/100  \n"
            f"- **Tests**: {test_result.passed} passed, {test_result.failed} failed "
            f"({test_result.duration_sec}s)  \n\n"
            "---\n\n"
            f"{report_md}\n\n"
            "---\n\n"
            f"{test_md}\n\n"
            "---\n\n"
            "*AutoCode AI Agent Advanced — Intelligent Code Analysis & PR Automation*\n"
        )