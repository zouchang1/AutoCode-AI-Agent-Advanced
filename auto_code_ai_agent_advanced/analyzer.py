"""
auto_code_ai_agent_advanced/analyzer.py
Multi-language source code analysis engine.

Scans project directories, categorises files by language, and collects:
  - lines of code (LOE) per language
  - comment lines and blank lines
  - TODO / FIXME / HACK / XXX markers
  - file-level and aggregate quality metrics
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Language definitions
# ---------------------------------------------------------------------------

LANGUAGE_MAP: Dict[str, Dict] = {
    ".py": {
        "name": "Python",
        "single_comment": re.compile(r"^\s*#"),
        "block_comment_start": re.compile(r'^\s*"""(?!")'),
        "block_comment_end": re.compile(r'"""(?!")'),
    },
    ".js": {
        "name": "JavaScript",
        "single_comment": re.compile(r"^\s*//"),
        "block_comment_start": re.compile(r"^\s*/\*"),
        "block_comment_end": re.compile(r"\*/"),
    },
    ".ts": {
        "name": "TypeScript",
        "single_comment": re.compile(r"^\s*//"),
        "block_comment_start": re.compile(r"^\s*/\*"),
        "block_comment_end": re.compile(r"\*/"),
    },
    ".jsx": {
        "name": "JSX",
        "single_comment": re.compile(r"^\s*//"),
        "block_comment_start": re.compile(r"^\s*/\*"),
        "block_comment_end": re.compile(r"\*/"),
    },
    ".tsx": {
        "name": "TSX",
        "single_comment": re.compile(r"^\s*//"),
        "block_comment_start": re.compile(r"^\s*/\*"),
        "block_comment_end": re.compile(r"\*/"),
    },
    ".go": {
        "name": "Go",
        "single_comment": re.compile(r"^\s*//"),
        "block_comment_start": re.compile(r"^\s*/\*"),
        "block_comment_end": re.compile(r"\*/"),
    },
    ".java": {
        "name": "Java",
        "single_comment": re.compile(r"^\s*//"),
        "block_comment_start": re.compile(r"^\s*/\*"),
        "block_comment_end": re.compile(r"\*/"),
    },
    ".cpp": {
        "name": "C++",
        "single_comment": re.compile(r"^\s*//"),
        "block_comment_start": re.compile(r"^\s*/\*"),
        "block_comment_end": re.compile(r"\*/"),
    },
    ".h": {
        "name": "C/C++ Header",
        "single_comment": re.compile(r"^\s*//"),
        "block_comment_start": re.compile(r"^\s*/\*"),
        "block_comment_end": re.compile(r"\*/"),
    },
    ".cs": {
        "name": "C#",
        "single_comment": re.compile(r"^\s*//"),
        "block_comment_start": re.compile(r"^\s*/\*"),
        "block_comment_end": re.compile(r"\*/"),
    },
    ".rs": {
        "name": "Rust",
        "single_comment": re.compile(r"^\s*//"),
        "block_comment_start": re.compile(r"^\s*/\*"),
        "block_comment_end": re.compile(r"\*/"),
    },
    ".rb": {
        "name": "Ruby",
        "single_comment": re.compile(r"^\s*#"),
        "block_comment_start": re.compile(r"^=begin"),
        "block_comment_end": re.compile(r"^=end"),
    },
    ".swift": {
        "name": "Swift",
        "single_comment": re.compile(r"^\s*//"),
        "block_comment_start": re.compile(r"^\s*/\*"),
        "block_comment_end": re.compile(r"\*/"),
    },
    ".kt": {
        "name": "Kotlin",
        "single_comment": re.compile(r"^\s*//"),
        "block_comment_start": re.compile(r"^\s*/\*"),
        "block_comment_end": re.compile(r"\*/"),
    },
    ".sh": {
        "name": "Shell",
        "single_comment": re.compile(r"^\s*#"),
        "block_comment_start": None,
        "block_comment_end": None,
    },
    ".yaml": {
        "name": "YAML",
        "single_comment": re.compile(r"^\s*#"),
        "block_comment_start": None,
        "block_comment_end": None,
    },
    ".yml": {
        "name": "YAML",
        "single_comment": re.compile(r"^\s*#"),
        "block_comment_start": None,
        "block_comment_end": None,
    },
    ".toml": {
        "name": "TOML",
        "single_comment": re.compile(r"^\s*#"),
        "block_comment_start": None,
        "block_comment_end": None,
    },
    ".json": {
        "name": "JSON",
        "single_comment": None,
        "block_comment_start": None,
        "block_comment_end": None,
    },
    ".md": {
        "name": "Markdown",
        "single_comment": None,
        "block_comment_start": None,
        "block_comment_end": None,
    },
}

MARKER_PATTERN = re.compile(r"\b(TODO|FIXME|HACK|XXX|BUG|WORKAROUND|OPTIMIZE)\b", re.IGNORECASE)

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class FileReport:
    """Per-file analysis snapshot."""

    path: str
    language: str
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    markers: Dict[str, List[int]] = field(default_factory=dict)  # marker -> [line numbers]


@dataclass
class LanguageSummary:
    """Aggregated stats for a single language."""

    language: str
    file_count: int
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    markers: Dict[str, int] = field(default_factory=dict)
    comment_ratio: float = 0.0  # comment / code


@dataclass
class AnalysisResult:
    """Top-level analysis output."""

    target_path: str
    total_files: int
    total_lines: int
    total_code_lines: int
    total_comment_lines: int
    total_blank_lines: int
    total_markers: int
    languages: Dict[str, LanguageSummary]
    files: List[FileReport]

    @property
    def quality_score(self) -> int:
        """Heuristic 0-100 quality score."""
        if self.total_code_lines == 0:
            return 50

        score = 80  # baseline

        # Penalty: too many TODOs / FIXMEs per 1000 code lines
        marker_density = self.total_markers / max(self.total_code_lines / 1000, 1)
        if marker_density > 20:
            score -= 15
        elif marker_density > 10:
            score -= 8
        elif marker_density > 5:
            score -= 3

        # Bonus: healthy comment ratio (15-30% is good)
        cr = self.total_comment_lines / max(self.total_code_lines, 1)
        if 0.10 <= cr <= 0.40:
            score += 5
        elif cr < 0.05:
            score -= 5  # under-commented

        # Penalty: lots of tiny files suggest poor organization
        small_files = sum(1 for f in self.files if f.code_lines < 10)
        if small_files > len(self.files) * 0.3:
            score -= 5

        # Language diversity bonus
        if len(self.languages) >= 3:
            score += 5
        elif len(self.languages) >= 2:
            score += 2

        return max(0, min(100, score))


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------


class CodeAnalyzer:
    """Scans a directory tree and produces an AnalysisResult."""

    IGNORE_DIRS: set = {
        ".git",
        "__pycache__",
        "node_modules",
        "venv",
        ".venv",
        "env",
        ".idea",
        ".vscode",
        "dist",
        "build",
        ".egg-info",
        "logs",
    }

    IGNORE_EXTS: set = {
        ".pyc", ".pyo", ".so", ".dll", ".dylib",
        ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
        ".ttf", ".otf", ".woff", ".woff2",
        ".zip", ".tar", ".gz", ".bz2",
        ".exe", ".msi", ".bin",
    }

    def __init__(self, path: str, ignore_dirs: Optional[set] = None):
        self.root = Path(path).resolve()
        self.ignore_dirs = ignore_dirs or self.IGNORE_DIRS

    def analyze(self) -> AnalysisResult:
        """Run the full analysis."""
        if not self.root.is_dir():
            raise NotADirectoryError(f"{self.root} is not a directory")

        files: List[FileReport] = []
        lang_buckets: Dict[str, List[FileReport]] = {}

        for file_path in self.root.rglob("*"):
            if not file_path.is_file():
                continue
            if any(part.startswith(".") and part != "." for part in file_path.relative_to(self.root).parts):
                continue
            if self._is_ignored(file_path):
                continue

            report = self._analyze_file(file_path)
            if report is None:
                continue

            files.append(report)
            lang_buckets.setdefault(report.language, []).append(report)

        # Build language summaries
        language_summaries: Dict[str, LanguageSummary] = {}
        total_markers = 0
        for lang, lang_files in lang_buckets.items():
            total_code = sum(f.code_lines for f in lang_files)
            total_comment = sum(f.comment_lines for f in lang_files)
            total_blank = sum(f.blank_lines for f in lang_files)
            total_lines = sum(f.total_lines for f in lang_files)
            markers: Dict[str, int] = {}
            for f in lang_files:
                for marker, lines in f.markers.items():
                    markers[marker] = markers.get(marker, 0) + len(lines)
            lang_markers = sum(markers.values())
            total_markers += lang_markers

            language_summaries[lang] = LanguageSummary(
                language=lang,
                file_count=len(lang_files),
                total_lines=total_lines,
                code_lines=total_code,
                comment_lines=total_comment,
                blank_lines=total_blank,
                markers=markers,
                comment_ratio=round(total_comment / max(total_code, 1), 3),
            )

        total_code = sum(f.code_lines for f in files)
        total_comment = sum(f.comment_lines for f in files)
        total_blank = sum(f.blank_lines for f in files)
        total_lines_total = sum(f.total_lines for f in files)

        return AnalysisResult(
            target_path=str(self.root),
            total_files=len(files),
            total_lines=total_lines_total,
            total_code_lines=total_code,
            total_comment_lines=total_comment,
            total_blank_lines=total_blank,
            total_markers=total_markers,
            languages=language_summaries,
            files=sorted(files, key=lambda x: x.path),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _is_ignored(self, path: Path) -> bool:
        for part in path.parts:
            if part in self.ignore_dirs:
                return True
        ext = path.suffix.lower()
        if ext in self.IGNORE_EXTS:
            return True
        return False

    def _analyze_file(self, path: Path) -> Optional[FileReport]:
        ext = path.suffix.lower()
        lang_def = LANGUAGE_MAP.get(ext)
        if lang_def is None:
            return None

        try:
            text = path.read_text("utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            return None

        lines = text.split("\n")
        total_lines = len(lines)
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        markers: Dict[str, List[int]] = {}
        in_block_comment = False

        for lineno, raw_line in enumerate(lines, start=1):
            stripped = raw_line.strip()

            # Blank
            if not stripped:
                blank_lines += 1
                continue

            # Block comment detection
            bc_start = lang_def.get("block_comment_start")
            bc_end = lang_def.get("block_comment_end")

            if in_block_comment:
                comment_lines += 1
                if bc_end and bc_end.search(stripped):
                    in_block_comment = False
                continue

            if bc_start and bc_start.search(stripped):
                comment_lines += 1
                if bc_end and bc_end.search(stripped):
                    pass  # single-line block comment
                else:
                    in_block_comment = True
                continue

            # Single-line comment
            sc = lang_def.get("single_comment")
            if sc and sc.search(stripped):
                comment_lines += 1
                code_lines += 0
            else:
                code_lines += 1

            # Marker detection (even in comments)
            for m in MARKER_PATTERN.findall(stripped):
                markers.setdefault(m.upper(), []).append(lineno)

        return FileReport(
            path=str(path.relative_to(self.root)),
            language=lang_def["name"],
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            markers=markers,
        )