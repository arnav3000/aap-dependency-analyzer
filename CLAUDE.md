# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AAP Migration Planner is a **containerized migration planning toolkit** for Ansible Automation Platform (AAP) 2.x. It provides both a **web UI** and **CLI** for analyzing cross-organization dependencies, generating migration plans, assessing risks, and sizing target infrastructure.

**Current Status**: Beta - Core features implemented:

- ✅ Dependency analysis engine
- ✅ Web UI with 4 modules (Analysis, Migration Plan, Dashboard, Sizing)
- ✅ CLI with analyze, report, validate commands
- ✅ Container deployment (Podman/Docker)
- ✅ Integration with aap-sizing-guide microservice

## Commands

### Development Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Testing

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_analyzer.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_analyzer.py::test_function_name
```

### Linting and Formatting

```bash
# Check code with ruff
ruff check src/

# Auto-fix issues
ruff check --fix src/

# Format code
ruff format src/

# Type checking
mypy src/ --ignore-missing-imports

# Run all pre-commit hooks manually
pre-commit run --all-files
```

### Running the CLI

```bash
# Install in editable mode first, then:
aap-planner --help
aap-planner analyze --organization "Engineering"
aap-planner analyze --all
aap-planner report --format html --output plan.html
aap-planner validate
```

## Architecture

### High-Level Structure

The toolkit uses a **microservices architecture** with containerization:

```
┌──────────────────────────────────────────────────┐
│         Streamlit Web UI (Port 8501)            │
│  ┌─────────────┬─────────────┬──────────────┐   │
│  │  Analysis   │  Migration  │  Dashboard   │   │
│  │   (Graph)   │   (Phases)  │  (Metrics)   │   │
│  └─────────────┴─────────────┴──────────────┘   │
│  ┌─────────────────────────────────────────┐    │
│  │      Sizing Guide Integration           │    │
│  └─────────────────────────────────────────┘    │
└───────────┬──────────────────────┬───────────────┘
            │                      │
            │                      │
┌───────────▼────────┐    ┌────────▼──────────────┐
│   Backend Engine   │    │  Sizing Guide (5002)  │
│  - CLI Commands    │    │  Flask Microservice   │
│  - Analysis Core   │    │  Capacity Calculator  │
│  - AAP Client      │    │  Red Hat Formulas     │
└────────────────────┘    └───────────────────────┘
            │
            │
┌───────────▼────────┐
│   AAP Instance     │
│  API v2 (HTTPS)    │
└────────────────────┘
```

**Container Stack:**

- `aap-toolkit-web` - Streamlit web UI
- `aap-toolkit-backend` - Analysis engine (CLI)
- `aap-sizing-guide` - Capacity sizing service
- All connected via shared network

### Key Components

**`client/aap_client.py`** - AAPClient class

- Async HTTP client extending BaseAPIClient (not yet implemented)
- Handles AAP 2.4+ API with pagination (`get_paginated()`)
- Parallel page fetching (`get_all_resources_parallel()`)
- Resource-specific methods: `get_organizations()`, `get_job_templates()`, `get_workflow_job_templates()`, etc.
- Rate limiting and retry logic

**`analysis/analyzer.py`** - CrossOrgDependencyAnalyzer class

- Core analysis engine for cross-organization dependencies
- `analyze_organization(org_name)` - Analyze single org
- `analyze_all_organizations()` - Global analysis across all orgs
- Uses `RESOURCE_DEPENDENCIES` mapping to define FK relationships (job_templates → projects, inventories, credentials, etc.)
- Produces `OrgDependencyReport` and `GlobalDependencyReport` dataclasses

**`analysis/graph.py`** - Graph algorithms

- `topological_sort(graph)` - Kahn's algorithm for migration ordering
- `group_into_phases(graph, order)` - Groups orgs that can migrate in parallel
- Detects circular dependencies

**`reporting/`** - Report generators

- `html_report.py` - HTML reports with dependency graphs and risk assessments (47K lines - large file)
- `text_report.py` - Console-friendly text reports

**`cli/main.py`** - Click CLI

- Commands: `analyze`, `report`, `validate`
- Loads `.env` for configuration
- Most commands currently stubbed with "coming soon" messages

### Data Flow

```
1. User runs CLI command
   ↓
2. CLI loads .env config (AAP_URL, AAP_TOKEN, AAP_VERIFY_SSL)
   ↓
3. AAPClient connects to AAP instance
   ↓
4. CrossOrgDependencyAnalyzer fetches resources per org
   ↓
5. Analyzer detects cross-org FK references (e.g., job_template.project → different org)
   ↓
6. Graph algorithms calculate migration order via topological sort
   ↓
7. Report generators create HTML/text/JSON output
```

### Web UI Architecture (New)

```
web/
├── app.py                      # Main entry point
├── pages/                      # Multi-page Streamlit app
│   ├── 1_🔍_Analysis.py       # Dependency graph visualization
│   ├── 2_📋_Migration_Plan.py # Phase timeline & order
│   ├── 3_📊_Dashboard.py      # Risk metrics & KPIs
│   └── 4_📏_Sizing_Guide.py   # Capacity sizing integration
├── components/                 # Reusable UI widgets
│   ├── graph.py               # Network graph (Plotly + NetworkX)
│   ├── phase_timeline.py      # Gantt chart timeline
│   └── metrics.py             # Dashboard charts
└── utils/                      # Web utilities
    ├── session.py             # Session state management
    └── data_loader.py         # Async analysis runner
```

**Key Technologies:**

- **Streamlit** - Web framework
- **Plotly** - Interactive charts
- **NetworkX** - Graph algorithms and layout
- **Pandas** - Data manipulation

## Code Standards

### Style

- **PEP 8** compliant
- **Max line length**: 100 characters
- **Type hints required** for all function signatures
- **Google-style docstrings** for public functions/classes
- **Ruff** for linting and formatting (configured in pyproject.toml)

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:

```
feat: add risk scoring for organizations
fix: correct dependency graph for workflow templates
docs: update installation instructions
```

### Testing

- Use **pytest** with async support (`pytest-asyncio`)
- Target **>80% coverage** (`pytest --cov=src`)
- Test both success and error cases
- Tests go in `tests/` directory (create if needed)

## Important Patterns

### Async/Await

All AAP API calls are async. Use `async`/`await` consistently:

```python
# Correct
orgs = await client.get_organizations()

# Wrong - will not work
orgs = client.get_organizations()  # Missing await
```

### Logging

Use structured logging via `structlog`:

```python
from aap_migration_planner.utils.logging import get_logger

logger = get_logger(__name__)
logger.info("event_name", key1=value1, key2=value2, message="Human readable")
```

### Resource Dependencies

When adding new resource types with cross-org dependencies, update `RESOURCE_DEPENDENCIES` in `analysis/analyzer.py`:

```python
RESOURCE_DEPENDENCIES = {
    "job_templates": [
        ("project", "projects"),          # FK field -> target resource type
        ("inventory", "inventories"),
    ],
}
```

### CLI Environment Variables

Configuration comes from `.env` file (loaded via `python-dotenv`):

```bash
AAP_URL=https://aap-controller.example.com
AAP_TOKEN=your_api_token_here
AAP_VERIFY_SSL=false
LOG_LEVEL=INFO
```

## Development Notes

### Pre-commit Hooks

The project uses pre-commit hooks (`.pre-commit-config.yaml`):

- `ruff` - Linting with auto-fix
- `ruff-format` - Code formatting
- `mypy` - Type checking
- `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`
- `detect-private-key` - Security check

If a hook fails, fix the issue before committing. Don't skip hooks with `--no-verify`.

### Working with Large Files

`reporting/html_report.py` is 47K lines - be careful when reading/editing. Use targeted searches and edits rather than full file reads when possible.

### AAP API Specifics

- Maximum page size: 200 items
- Pagination format: `?page=1&page_size=200`
- FK fields often end in `_id` but may just be the field name (e.g., `project`, `inventory`)
- Encrypted credential fields show as `$encrypted$` and cannot be extracted

## Related Files

- `README.md` - User-facing documentation, installation, use cases
- `CONTRIBUTING.md` - Development workflow, branching strategy, PR guidelines
- `pyproject.toml` - Dependencies, build config, tool settings (ruff, pytest, mypy)
- `.pre-commit-config.yaml` - Pre-commit hook configuration
