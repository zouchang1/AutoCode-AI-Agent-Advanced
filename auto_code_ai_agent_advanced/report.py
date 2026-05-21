"""
auto_code_ai_agent_advanced/report.py
AI-powered PR report generator.

Transforms a code analysis result into a structured, human-readable
pull request summary with file-level breakdowns, quality scoring,
and actionable recommendations.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from .analyzer import AnalysisResult, LanguageSummary


class ReportGenerator:
    """Generates structured PR reports from analysis results."""

    def __init__(self):
        pass

    def generate(self, result: AnalysisResult, title: Optional[str] = None) -> str:
        """Build a complete PR report in Markdown."""
        sections: List[str] = []

        # Header
        sections.append(self._header(title or "AutoCode AI Agent — Code Analysis Report"))

        # Summary stats
        sections.append(self._summary_table(result))

        # Quality score
        sections.append(self._quality_badge(result.quality_score))

        # Language breakdown
        sections.append(self._language_breakdown(result))

        # Marker hotspots
        if result.total_markers > 0:
            sections.append(self._marker_report(result))

        # File-level breakdown (top N)
        sections.append(self._file_breakdown(result))

        # Recommendations
        sections.append(self._recommendations(result))

        # Footer
        sections.append(self._footer())

        return "\n\n".join(sections)

    # ------------------------------------------------------------------
    # Section builders
    # ------------------------------------------------------------------

    @staticmethod
    def _header(title: str) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"# {title}\n\n"
            f"> **Generated**: {now}  \n"
            f"> **Engine**: AutoCode AI Agent v1.0.0  \n"
            f"> **Scope**: Full project analysis"
        )

    @staticmethod
    def _summary_table(result: AnalysisResult) -> str:
        return (
            "## Project Overview\n\n"
            "| Metric | Value |\n"
            "|--------|------:|\n"
            f"| Target Directory | `{result.target_path}` |\n"
            f"| Total Files | {result.total_files} |\n"
            f"| Total Lines | {result.total_lines:,} |\n"
            f"| Code Lines | {result.total_code_lines:,} |\n"
            f"| Comment Lines | {result.total_comment_lines:,} |\n"
            f"| Blank Lines | {result.total_blank_lines:,} |\n"
            f"| Languages Detected | {len(result.languages)} |\n"
            f"| TODO / FIXME / HACK Markers | {result.total_markers} |\n"
            f"| Comment Ratio | {result.total_comment_lines / max(result.total_code_lines, 1):.1%} |\n"
        )

    @staticmethod
    def _quality_badge(score: int) -> str:
        if score >= 85:
            emoji = "A+"
            label = "Excellent"
        elif score >= 70:
            emoji = "A"
            label = "Good"
        elif score >= 50:
            emoji = "B"
            label = "Fair"
        elif score >= 30:
            emoji = "C"
            label = "Needs Improvement"
        else:
            emoji = "D"
            label = "Poor"

        return (
            "## Code Quality Score\n\n"
            f"**{score}/100 — {emoji} ({label})**\n\n"
            "This heuristic score is based on marker density, comment coverage, "
            "file organization, and language diversity.\n"
        )

    @staticmethod
    def _language_breakdown(result: AnalysisResult) -> str:
        lines = ["## Language Breakdown\n\n"]
        lines.append("| Language | Files | Code Lines | Comments | Blanks | Comment Ratio | Markers |\n")
        lines.append("|----------|------:|-----------:|--------:|-------:|--------------:|--------:|\n")

        # Sort by code_lines descending
        sorted_langs = sorted(
            result.languages.values(), key=lambda l: l.code_lines, reverse=True
        )
        for lang in sorted_langs:
            cr = f"{lang.comment_ratio:.1%}" if lang.comment_ratio > 0 else "-"
            markers_total = sum(lang.markers.values()) or "-"
            lines.append(
                f"| {lang.language} | {lang.file_count} | {lang.code_lines:,} | "
                f"{lang.comment_lines:,} | {lang.blank_lines:,} | {cr} | {markers_total} |\n"
            )

        return "".join(lines)

    @staticmethod
    def _marker_report(result: AnalysisResult) -> str:
        lines = ["## Code Markers\n\n"]
        lines.append("| Marker | Count |\n|--------|------:|\n")

        marker_agg: dict = {}
        for lang in result.languages.values():
            for marker, count in lang.markers.items():
                marker_agg[marker] = marker_agg.get(marker, 0) + count

        for marker in ["TODO", "FIXME", "HACK", "XXX", "BUG", "WORKAROUND", "OPTIMIZE"]:
            count = marker_agg.get(marker, 0)
            if count:
                lines.append(f"| {marker} | {count} |\n")

        return "".join(lines)

    @staticmethod
    def _file_breakdown(result: AnalysisResult) -> str:
        lines = ["## Top Files by Size\n\n"]
        lines.append("| File | Language | Code Lines | Markers |\n")
        lines.append("|------|----------|-----------:|--------:|\n")

        sorted_files = sorted(result.files, key=lambda f: f.code_lines, reverse=True)[:15]
        for f in sorted_files:
            marker_count = sum(len(v) for v in f.markers.values())
            marker_str = str(marker_count) if marker_count > 0 else "-"
            lines.append(f"| `{f.path}` | {f.language} | {f.code_lines:,} | {marker_str} |\n")

        if len(result.files) > 15:
            lines.append(f"\n*+{len(result.files) - 15} more files*\n")

        return "".join(lines)

    @staticmethod
    def _recommendations(result: AnalysisResult) -> str:
        recs: List[str] = []

        if result.total_markers > 10:
            recs.append(
                f"- **Reduce technical debt**: {result.total_markers} TODO/FIXME/HACK markers found. "
                "Consider scheduling a cleanup sprint to address outstanding issues."
            )

        cr = result.total_comment_lines / max(result.total_code_lines, 1)
        if cr < 0.05 and result.total_code_lines > 500:
            recs.append(
                f"- **Improve documentation**: Comment ratio is only {cr:.1%}. "
                "Add docstrings and inline comments for complex logic to improve maintainability."
            )
        elif cr > 0.50:
            recs.append(
                f"- **Review comment density**: Comment ratio is {cr:.1%}, which is high. "
                "Ensure comments add value rather than restating what the code does."
            )

        non_py_files = sum(1 for f in result.files if f.language != "Python")
        if non_py_files > 10:
            recs.append(
                f"- **Consider unified tooling**: {non_py_files} non-Python files detected. "
                "Ensure cross-language build and test tooling is consistent."
            )

        if len(result.files) > 50:
            recs.append(
                f"- **Modularise project**: {len(result.files)} files in the root may indicate "
                "a flat structure. Consider organising into sub-packages/modules."
            )

        if not recs:
            recs.append("- No critical issues detected. The codebase is in good shape!")

        return "## Recommendations\n\n" + "\n".join(recs)

    @staticmethod
    def _footer() -> str:
        return (
            "---\n"
            "*Report generated by AutoCode AI Agent Advanced – Intelligent Code Analysis & PR Automation*\n"
            "*[auto-code-ai-agent-advanced](https://github.com/zouchang1/AutoCode-AI-Agent-Advanced)*"
        )