"""AutoCode AI Agent Advanced — Intelligent Code Analysis & Automation Agent."""

__version__ = "1.0.0"
__author__ = "zouchang1"

from .analyzer import CodeAnalyzer, AnalysisResult
from .report import ReportGenerator
from .tester import TestRunner
from .pipeline import Pipeline

__all__ = [
    "CodeAnalyzer",
    "AnalysisResult",
    "ReportGenerator",
    "TestRunner",
    "Pipeline",
]