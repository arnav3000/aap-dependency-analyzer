# AAP Migration Planner

> Migration planning and dependency analysis tool for Ansible Automation Platform

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

## What is AAP Migration Planner?

AAP Migration Planner helps you **plan and de-risk** migrations from Ansible Automation Platform 2.x to newer versions by analyzing dependencies, detecting risks, and recommending migration sequences.

**Use it to:**

- 🔍 Discover cross-organization dependencies
- 📊 Generate visual dependency graphs and risk reports
- 🗺️ Get recommended migration order for multi-org environments
- ⚠️ Identify potential blockers before migration starts

**NOT a migration execution tool** - For actual migration, see [aap-bridge](https://github.com/arnav3000/aap-bridge-fork)

---

## Quick Start

### Option 1: Web UI (Recommended)

```bash
# Clone repository
git clone https://github.com/arnav3000/aap-migration-planner.git
cd aap-migration-planner

# Build and start containers
make start

# Access web UI
open http://localhost:8501
```

### Option 2: CLI

```bash
# Install
pip install aap-migration-planner

# Configure (create .env file)
cat > .env << EOF
AAP_URL=https://aap-controller.example.com
AAP_TOKEN=your_api_token_here
AAP_VERIFY_SSL=false
EOF

# Analyze single organization
aap-planner analyze --organization "Engineering"

# Analyze all organizations
aap-planner analyze --all

# Generate HTML report
aap-planner report --format html --output migration-plan.html
```

---

## Features

### 🌐 Web UI

- **Interactive Dependency Graph** - Visualize org-to-org dependencies
- **Migration Timeline** - Phase-by-phase migration plan with Gantt charts
- **Risk Dashboard** - Executive metrics and complexity scoring
- **Capacity Sizing** - Infrastructure sizing calculator for AAP 2.6
- **Export Reports** - JSON, CSV, PDF (coming soon)

### 💻 CLI

- **Dependency Analysis** - Discover cross-org dependencies programmatically
- **Report Generation** - HTML, text, and JSON formats
- **Validation** - Test AAP connectivity and credentials
- **Automation-Ready** - CI/CD integration support

### 🐳 Container-First

- **Podman & Docker Support** - Rootless containers for security
- **Microservices Architecture** - Modular, scalable design
- **One-Command Deployment** - `make start` and you're running

---

## Installation

### Using Containers (Recommended)

```bash
# Clone repository
git clone https://github.com/arnav3000/aap-migration-planner.git
cd aap-migration-planner

# Copy environment template
cp .env.example .env

# Edit .env with your AAP credentials
# AAP_URL=https://your-aap.example.com
# AAP_TOKEN=your_token_here

# Build and start all services
make start

# Access:
# - Web UI: http://localhost:8501
# - Sizing Guide: http://localhost:5002
```

### From PyPI (CLI Only)

```bash
pip install aap-migration-planner
```

### From Source

```bash
git clone https://github.com/arnav3000/aap-migration-planner.git
cd aap-migration-planner
pip install -e ".[dev]"
```

### Prerequisites

- **For Containers**: Podman or Docker
- **For CLI**: Python 3.12 or higher
- **For Both**: Access to AAP instance (API credentials)

---

## Configuration

Create a `.env` file in your working directory:

```bash
# AAP Connection
AAP_URL=https://your-aap-controller.example.com
AAP_TOKEN=your_api_token_here
AAP_VERIFY_SSL=false  # Set to true in production

# Optional: Logging
LOG_LEVEL=INFO
```

---

## Use Cases

### 1. Pre-Migration Planning

Analyze your AAP instance before starting migration to identify:

- Cross-org dependencies that require coordinated migration
- Resource risks (missing credentials, broken references)
- Optimal migration sequence

**Example:**

```bash
aap-planner analyze --all --output pre-migration-analysis.json
aap-planner report --format html --output pre-migration-report.html
```

### 2. Multi-Org Migration Sequencing

For AAP instances with multiple organizations:

- Discover which orgs can be migrated independently
- Get recommended migration order based on dependencies
- Identify "foundation" orgs that must migrate first

**Example:**

```bash
# Analyze all orgs
aap-planner analyze --all

# Generate migration order report
aap-planner report --format html
```

### 3. Risk Assessment

Before executing migration:

- Detect broken references and missing dependencies
- Estimate migration complexity per organization
- Generate executive summary for stakeholders

**Example:**

```bash
# Analyze specific orgs you're concerned about
aap-planner analyze --organization "Production" --organization "Staging"
```

---

## Commands

### `analyze`

Analyze AAP instance for dependencies and risks.

```bash
# Analyze single organization
aap-planner analyze --organization "Engineering"

# Analyze multiple organizations
aap-planner analyze --organization "Eng" --organization "Ops"

# Analyze all organizations
aap-planner analyze --all

# Save analysis results
aap-planner analyze --all --output analysis.json
```

### `report`

Generate migration planning reports.

```bash
# HTML report (default)
aap-planner report --format html --output plan.html

# Text report
aap-planner report --format text

# JSON export
aap-planner report --format json --output plan.json
```

### `validate`

Validate AAP connection and credentials.

```bash
aap-planner validate
```

---

## Documentation

- [Installation Guide](docs/installation.md) *(coming soon)*
- [Quick Start Guide](docs/quickstart.md) *(coming soon)*
- [Use Cases](docs/use-cases.md) *(coming soon)*
- [Examples](docs/examples/) *(coming soon)*

---

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

```bash
# Clone repository
git clone https://github.com/arnav3000/aap-migration-planner.git
cd aap-migration-planner

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (editable mode)
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src/
```

---

## Roadmap

- [x] Project structure and extraction from aap-bridge
- [ ] Core dependency analysis engine
- [ ] HTML report generation
- [ ] Risk scoring algorithm
- [ ] CLI implementation
- [ ] JSON export functionality
- [ ] Interactive web UI
- [ ] Multi-AAP comparison mode

---

## Related Projects

- [aap-bridge](https://github.com/arnav3000/aap-bridge-fork) - AAP migration execution tool
- [ansible-lint](https://github.com/ansible/ansible-lint) - Ansible playbook linting
- [Red Hat CoP](https://github.com/redhat-cop) - Red Hat Communities of Practice

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

GPL-3.0 - See [LICENSE](LICENSE) for details.

---

## Authors

- **Arnav Bhati** ([@arnav3000](https://github.com/arnav3000))

---

## Support

- **Issues**: [GitHub Issues](https://github.com/arnav3000/aap-migration-planner/issues)
- **Questions**: Open an issue with the "question" label
- **Discussions**: [GitHub Discussions](https://github.com/arnav3000/aap-migration-planner/discussions) *(coming soon)*

---

## Acknowledgments

This project was extracted from [aap-bridge](https://github.com/arnav3000/aap-bridge-fork) to provide a focused, standalone migration planning tool.

---

**Made with ❤️ for the AAP community**
