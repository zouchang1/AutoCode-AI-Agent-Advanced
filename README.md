<<<<<<< HEAD
# AutoCode-AI-Agent-Advanced

## AutoCode AI Agent 进阶版

**基于 MiMo V2.5 推理模型的智能代码审查与自动修复系统**

---

### 🚀 核心功能

| 功能 | 描述 |
|------|------|
| **智能代码审查** | 调用 MiMo V2.5 API 进行深度代码质量分析 |
| **自动 PR 生成** | 基于审查结果自动生成改进建议 |
| **单元测试生成** | 利用 MiMo 语义理解能力生成测试用例 |
| **多语言支持** | Python / Java / Go |

---

### 📦 安装

```bash
pip install -r requirements.txt
export MIMO_API_KEY="your_key"
```

---

### ▶️ 使用

```bash
python main.py --api-key your_key demo_code/
=======
# AutoCode AI Agent Advanced

> An intelligent multi-agent code analysis, PR generation, and automated testing orchestration system.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code Quality](https://img.shields.io/badge/quality-pipeline--enabled-success)](#)

---

## Overview

**AutoCode AI Agent Advanced** is a modular, extensible agent-based automation framework for software projects. It orchestrates three core agents in a pipeline:

| Agent | Module | Responsibility |
|-------|--------|----------------|
| **Code Analyzer** | `analyzer.py` | Scans source code across 15+ languages, collects LOC metrics, detects TODO/FIXME markers, computes quality heuristics. |
| **Report Generator** | `report.py` | Transforms analysis data into structured PR-style markdown reports with quality scoring and actionable recommendations. |
| **Test Runner** | `tester.py` | Discovers, executes, and reports on pytest test suites with structured pass/fail/error breakdowns. |

The **Pipeline Orchestrator** (`pipeline.py`) chains these agents into a single `analyze → report → test` workflow, producing a combined deliverable suitable for CI/CD integration, code review, or developer dashboards.

---

## Features

- **Multi-Language Support** — Python, JavaScript, TypeScript, Go, Java, C++, C#, Rust, Ruby, Swift, Kotlin, Shell, YAML, TOML, JSON, Markdown.
- **Line Counting** — Code, comment, and blank line breakdowns per file and per language.
- **Marker Detection** — Automatically finds `TODO`, `FIXME`, `HACK`, `XXX`, `BUG`, `WORKAROUND`, `OPTIMIZE` markers.
- **Heuristic Quality Scoring** — 0-100 score based on marker density, comment coverage, file organization, and language diversity.
- **Structured PR Reports** — Markdown output formatted as a pull request summary, with sections for overview, language breakdown, file breakdown, and recommendations.
- **Automated Test Execution** — Integrates with pytest, parses output, logs results, and highlights failures.
- **Pipeline Mode** — Single command runs the full workflow, saving all artifacts to disk.
- **Agent-Oriented Architecture** — Each module is independently usable and individually replaceable, making the system extensible for additional agent types (linting, security scanning, dependency audit).

---

## Quick Start

### Installation

```bash
pip install -r requirements.txt
# or
pip install -e .    # editable install with CLI entry point
```

### Usage

```bash
# Full pipeline: analyze → report → test
python -m auto_code_ai_agent_advanced.cli all /path/to/project

# Or install and use the CLI directly:
auto-agent all /path/to/project

# Individual stages:
auto-agent analyze /path/to/project
auto-agent report /path/to/project
auto-agent test  /path/to/project
```

### Options

```bash
auto-agent all /path/to/project -o ./reports   # output directory
auto-agent test /path/to/project --coverage     # run with pytest-cov
auto-agent --verbose analyze /path/to/project   # debug logging
```

### Output

All reports are written to the `logs/` directory by default:

```
logs/
├── code_analysis_report.md       # Code quality & PR report
├── test_report.md                # Test execution results
├── full_pipeline_report.md       # Combined report
└── test_run_<timestamp>.log      # Raw pytest output
>>>>>>> 91142c2 (refactor: full rewrite v1.0.0 — modular agent architecture)
```

---

<<<<<<< HEAD
### 📈 性能指标

- 日均处理：~20 万行代码
- 日均 Token 消耗：~500 万
- 审查准确率：~92%

---

*AutoCode AI Agent Team*
=======
## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Pipeline Orchestrator                  │
│                     (pipeline.py)                          │
│                                                          │
│   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐│
│   │  Code        │   │  Report      │   │  Test        ││
│   │  Analyzer    │──▶│  Generator   │   │  Runner      ││
│   │ (analyzer.py)│   │ (report.py)  │   │ (tester.py)  ││
│   └──────────────┘   └──────────────┘   └──────────────┘│
│          │                   │                   │         │
│          ▼                   ▼                   ▼         │
│   AnalysisResult    report.md              TestResult     │
│                                                          │
│   ┌────────────────────────────────────────────────────┐  │
│   │           Combined Pipeline Report                  │  │
│   └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

The architecture is intentionally modular — each agent can be run independently, replaced, or extended without affecting the others. The `Pipeline` class simply chains them together and aggregates outputs.

### Extending

To add a new agent (e.g. `LinterAgent`, `SecurityScanner`):

1. Create a new module (e.g. `linter.py`) with an interface compatible with the pipeline.
2. Add the agent to `Pipeline` in `pipeline.py`.
3. Add a new subcommand in `cli.py`.

---

## Demo

Included `demo_code/` directory for testing:

```bash
auto-agent all .
```

This runs the full pipeline on the AutoCode project itself — meta-analysis included.

---

## Requirements

- Python 3.10+
- click >= 8.0
- pytest >= 7.0

---

## License

MIT

---

## Author

**zouchang1** — [GitHub](https://github.com/zouchang1/AutoCode-AI-Agent-Advanced)
>>>>>>> 91142c2 (refactor: full rewrite v1.0.0 — modular agent architecture)
