"""
auto_code_ai_agent_advanced/cli.py
Click-based CLI entry point for the AutoCode AI Agent.

Usage:
    auto-agent analyze <path>
    auto-agent report <path>
    auto-agent test <path>
    auto-agent all <path>
"""

from __future__ import annotations

import logging
import sys

import click

from . import __version__
from .pipeline import Pipeline


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


# ---------------------------------------------------------------------------
# Shared option
# ---------------------------------------------------------------------------

_path_arg = click.argument(
    "path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
)


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------


@click.group()
@click.version_option(version=__version__, prog_name="auto-agent")
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging")
def cli(verbose: bool) -> None:
    """AutoCode AI Agent — Intelligent code analysis & automation."""
    _setup_logging(verbose)


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------


@cli.command()
@_path_arg
@click.option("-o", "--output", type=click.Path(), help="Output directory for reports")
def analyze(path: str, output: str | None) -> None:
    """Analyze a codebase and print summary."""
    pipe = Pipeline(path, output_dir=output)
    result = pipe.run_analyze()

    click.echo(f"\n{'='*50}")
    click.echo(f"  AutoCode AI Agent — Analysis Results")
    click.echo(f"{'='*50}")
    click.echo(f"  Path:         {result.target_path}")
    click.echo(f"  Files:        {result.total_files}")
    click.echo(f"  Code Lines:   {result.total_code_lines:,}")
    click.echo(f"  Comment:      {result.total_comment_lines:,}")
    click.echo(f"  Blank:        {result.total_blank_lines:,}")
    click.echo(f"  Markers:      {result.total_markers}")
    click.echo(f"  Languages:    {len(result.languages)}")
    click.echo(f"  Quality:      {result.quality_score}/100")
    click.echo(f"{'='*50}\n")

    for lang in sorted(result.languages.values(), key=lambda l: l.code_lines, reverse=True):
        click.echo(f"  {lang.language:15s}  {lang.file_count:3d} files  {lang.code_lines:>6,} lines")


@cli.command()
@_path_arg
@click.option("-o", "--output", type=click.Path(), help="Output directory for reports")
def report(path: str, output: str | None) -> None:
    """Generate a PR-style analysis report."""
    pipe = Pipeline(path, output_dir=output)
    result = pipe.run_analyze()
    report_md = pipe.run_report(result)

    report_path = pipe.output_dir / "code_analysis_report.md"
    click.echo(f"\nReport written to: {report_path}")
    click.echo("─" * 50)
    click.echo(report_md[:2000] + "\n..." if len(report_md) > 2000 else report_md)


@cli.command()
@_path_arg
@click.option("-o", "--output", type=click.Path(), help="Output directory for logs")
@click.option("--coverage", is_flag=True, help="Run tests with coverage")
def test(path: str, output: str | None, coverage: bool) -> None:
    """Discover and run tests."""
    pipe = Pipeline(path, output_dir=output)

    discovered = pipe.tester.discover()
    if not discovered:
        click.echo("No test files found under tests/")
        return

    click.echo(f"Discovered {len(discovered)} test file(s):")
    for f in discovered:
        click.echo(f"  • {f}")

    extra = ["--cov=."] if coverage else None
    result = pipe.tester.run(extra_args=extra)

    click.echo(f"\n{'='*50}")
    click.echo(f"  Tests: {result.passed} passed  {result.failed} failed  "
               f"{result.errors} errors  {result.skipped} skipped")
    click.echo(f"  Duration: {result.duration_sec}s  Exit code: {result.exit_code}")
    click.echo(f"{'='*50}")

    if result.failed_tests:
        click.echo("\nFailed tests:")
        for name in result.failed_tests:
            click.echo(f"  ✗ {name}")


@cli.command()
@_path_arg
@click.option("-o", "--output", type=click.Path(), help="Output directory for reports")
def all(path: str, output: str | None) -> None:
    """Run the full pipeline: analyze → report → test."""
    pipe = Pipeline(path, output_dir=output)
    summary = pipe.run_full()

    click.echo(f"\n{'='*50}")
    click.echo(f"  AutoCode AI Agent — Full Pipeline Complete")
    click.echo(f"{'='*50}")
    click.echo(f"  Files analyzed:  {summary['analysis']['total_files']}")
    click.echo(f"  Code lines:     {summary['analysis']['total_code_lines']:,}")
    click.echo(f"  Quality score:  {summary['analysis']['quality_score']}/100")
    click.echo(f"  Languages:      {', '.join(summary['analysis']['languages'])}")
    t = summary["test"]
    click.echo(f"  Tests:          {t['passed']} passed / {t['failed']} failed ({t['duration_sec']}s)")
    click.echo(f"{'='*50}")
    click.echo(f"\nOutputs:")
    click.echo(f"  • {summary['report_path']}")
    click.echo(f"  • {summary['test_report_path']}")
    click.echo(f"  • {summary['combined_report_path']}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cli()