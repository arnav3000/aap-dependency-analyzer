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

### 🔒 Security

- **HTTPS-Only Enforcement** - HTTP connections blocked at all layers
- **Token Masking** - API tokens never logged or displayed
- **SSL Verification** - Configurable certificate validation
- **Pre-commit Security Hooks** - Secret detection with gitleaks

---

## UI vs CLI: Which to Use?

| Feature | Web UI Mode | CLI Mode | Notes |
|---------|-------------|----------|-------|
| **Interactive Graphs** | ✅ Yes | ❌ No | Dependency visualization, Gantt charts |
| **Real-time Analysis** | ✅ Yes | ✅ Yes | Both support live AAP connections |
| **Automation** | ❌ No | ✅ Yes | CLI supports scripting, CI/CD pipelines |
| **Capacity Sizing** | ✅ Yes | ❌ No | UI includes sizing calculator |
| **Report Export** | ✅ Yes | ✅ Yes | Both support JSON, HTML, text |
| **Multi-user Access** | ✅ Yes | ❌ No | UI can be deployed as shared service |
| **Resource Usage** | Higher (2GB RAM) | Lower (200MB RAM) | Containers vs Python process |
| **Setup Complexity** | Medium | Low | Containers vs pip install |
| **Best For** | Planning meetings, demos | Scripts, automation, headless servers |

**Recommendation:**

- **Use UI Mode** for interactive analysis, presentations, and demos
- **Use CLI Mode** for automation, CI/CD pipelines, and enterprise terminals

---

## Installation

### Prerequisites

**For UI Mode (Containerized):**

- Podman 4.0+ or Docker 20.10+
- podman-compose or docker-compose
- 2GB free RAM
- Access to AAP 2.4+ instance with API credentials

**For CLI Mode:**

- Python 3.12 or higher
- pip package manager
- Virtual environment (recommended)
- Access to AAP 2.4+ instance with API credentials

**For Both:**

- AAP instance must be accessible via HTTPS (HTTP connections are blocked for security)
- Valid AAP API token with read permissions

---

## Setup Instructions

### UI Mode (Web Interface - Recommended)

#### Step 1: Clone Repository

```bash
git clone https://github.com/arnav3000/aap-migration-planner.git
cd aap-migration-planner
```

#### Step 2: Configure Environment

Create a `.env` file with your AAP credentials:

```bash
# Copy template
cp .env.example .env

# Edit .env file
nano .env
```

Add your AAP credentials (HTTPS required):

```bash
# SECURITY: Only HTTPS URLs are accepted. HTTP is blocked to protect API tokens.
AAP_URL=https://your-aap-controller.example.com
AAP_TOKEN=your_api_token_here
AAP_VERIFY_SSL=true  # Set to false for self-signed certificates

# Optional settings
AAP_TIMEOUT=30
LOG_LEVEL=INFO
```

#### Step 3: Build and Start Containers

**Using Podman (Recommended):**

```bash
# Using Makefile
make start

# Or manually with podman-compose
podman-compose -f podman-compose.yml build
podman-compose -f podman-compose.yml up -d

# Verify containers are running
podman ps
```

**Using Docker:**

```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# Verify containers are running
docker ps
```

#### Step 4: Access Web UI

Open your browser and navigate to:

- **Web UI**: http://localhost:8501
- **Sizing Guide API**: http://localhost:5002 (optional, used by UI internally)

#### Step 5: Connect to AAP

1. In the web UI sidebar, enter your AAP URL and token
2. Click **"Connect"** button
3. Once connected, you'll see organization list
4. Select organizations to analyze

#### Stopping the UI

```bash
# Using Makefile
make stop

# Or manually
podman-compose -f podman-compose.yml down

# To remove volumes and clean up completely
make clean
```

---

### CLI Mode (Terminal-Only)

#### Step 1: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

#### Step 2: Install Package

**Option A: From Source (Development)**

```bash
# Clone repository
git clone https://github.com/arnav3000/aap-migration-planner.git
cd aap-migration-planner

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (optional, for development)
pre-commit install
```

**Option B: From PyPI (When Published)**

```bash
# Install from PyPI
pip install aap-migration-planner

# Verify installation
aap-planner --version
```

#### Step 3: Configure Environment

Create a `.env` file in your working directory:

```bash
cat > .env << 'EOF'
# AAP Connection (HTTPS REQUIRED)
AAP_URL=https://your-aap-controller.example.com
AAP_TOKEN=your_api_token_here
AAP_VERIFY_SSL=true

# Optional Settings
AAP_TIMEOUT=60
LOG_LEVEL=INFO
EOF

# Secure the file (Linux/macOS)
chmod 600 .env
```

**OR** set environment variables directly:

```bash
export AAP_URL=https://your-aap-controller.example.com
export AAP_TOKEN=your_api_token_here
export AAP_VERIFY_SSL=true
```

#### Step 4: Validate Connection

Test your AAP connection:

```bash
aap-planner validate
```

Expected output:

```
🔐 AAP Migration Planner - Configuration Validation

📋 Loading configuration...
   URL: https://your-aap.example.com/api/v2
   SSL Verify: true
   Timeout: 30s

🔌 Testing AAP connection...
   ✅ Connected successfully!
   AAP Version: 2.5.0

📊 Checking permissions...
   ✅ API credentials valid
   Organizations accessible: 15

✅ Validation successful! Ready to run analysis.
```

#### Step 5: Run Analysis

**Analyze single organization:**

```bash
aap-planner analyze --organization "Engineering"
```

**Analyze all organizations:**

```bash
aap-planner analyze --all --output analysis.json
```

**Generate reports:**

```bash
# HTML report
aap-planner report --input analysis.json --format html --output report.html

# Text report
aap-planner report --input analysis.json --format text --output report.txt

# JSON export
aap-planner report --input analysis.json --format json --output export.json
```

#### Step 6: View Results

```bash
# Open HTML report in browser
# Linux:
xdg-open report.html

# macOS:
open report.html

# Windows:
start report.html

# Or view text report
cat report.txt
```

---

## Container Architecture

The containerized deployment uses three services:

```
┌─────────────────────────────────────────┐
│  Web UI (aap-toolkit-web)              │
│  Port: 8501                             │
│  - Streamlit-based interface            │
│  - Interactive visualizations           │
│  - Migration planning dashboard         │
└────────────┬────────────────────────────┘
             │
             │ API Calls
             │
┌────────────▼────────────────────────────┐
│  Backend (aap-toolkit-backend)         │
│  - Analysis engine                      │
│  - AAP API client                       │
│  - CLI commands                         │
└────────────┬────────────────────────────┘
             │
             │ Uses
             │
┌────────────▼────────────────────────────┐
│  Sizing Guide (aap-sizing-guide)       │
│  Port: 5002                             │
│  - Capacity calculator                  │
│  - Infrastructure sizing                │
└─────────────────────────────────────────┘
```

### Makefile Commands

The project includes a Makefile that automatically detects whether you're using Podman or Docker:

```bash
# Show all available commands
make help

# Container Management
make build          # Build all container images
make start          # Start all services (creates .env from template if missing)
make stop           # Stop all services
make restart        # Restart all services
make status         # Show container status
make clean          # Stop and remove containers, images, and volumes

# Monitoring
make logs           # Show logs from all services (follow mode)
make logs-web       # Show web UI logs only

# Container Shell Access
make shell-backend  # Open bash shell in backend container
make shell-web      # Open bash shell in web container

# Development
make install        # Install package locally in editable mode
make dev            # Run development setup (install + build)
make test           # Run pytest test suite
make lint           # Run ruff linter
make format         # Format code with ruff

# CLI Commands (requires .env configuration)
make validate       # Validate AAP connection
make analyze        # Run dependency analysis (saves to data/analysis.json)
make report         # Generate HTML report (saves to data/report.html)
```

**Example Workflow:**

```bash
# Initial setup
make start          # Starts containers
# Edit .env when prompted
make start          # Start again after configuring

# Daily usage
make logs           # Monitor activity
make restart        # After code/config changes
make clean          # Full cleanup when done
```

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AAP_URL` | ✅ Yes | - | AAP Controller URL (**must use HTTPS**) |
| `AAP_TOKEN` | ✅ Yes | - | AAP API token for authentication |
| `AAP_VERIFY_SSL` | ❌ No | `true` | Verify SSL certificates (set to `false` for self-signed) |
| `AAP_TIMEOUT` | ❌ No | `30` | API request timeout in seconds |
| `LOG_LEVEL` | ❌ No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Example .env File

```bash
# AAP Connection (HTTPS REQUIRED)
AAP_URL=https://your-aap-controller.example.com
AAP_TOKEN=your_api_token_here
AAP_VERIFY_SSL=true  # Set to false for self-signed certificates

# Optional: Performance Tuning
AAP_TIMEOUT=60

# Optional: Logging
LOG_LEVEL=INFO
```

### Security Notes

**HTTPS-Only Enforcement:**

This tool enforces HTTPS connections at all layers to protect your API tokens. HTTP URLs are automatically rejected.

```bash
# ✅ Correct (HTTPS)
export AAP_URL=https://aap.example.com

# ❌ Incorrect (HTTP - will be blocked)
export AAP_URL=http://aap.example.com
# Error: HTTP URLs are not allowed for security reasons
```

**Self-Signed Certificates:**

If your AAP instance uses self-signed certificates:

```bash
# Option 1: Disable SSL verification (not recommended for production)
export AAP_VERIFY_SSL=false

# Option 2: Add certificate to system trust store (recommended)
sudo cp aap-cert.pem /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

**Token Security:**

- Never commit `.env` files to version control
- Use secrets managers (Vault, AWS Secrets Manager) in production
- Rotate tokens regularly
- Grant minimum required permissions (read-only access)

See [SECURITY.md](SECURITY.md) for comprehensive security documentation.

---

## Troubleshooting

### Common Issues

#### 1. HTTP URL Rejected

**Error:**

```
❌ Configuration Error: HTTP URLs are not allowed for security reasons
```

**Solution:**

```bash
# Change HTTP to HTTPS
export AAP_URL=https://aap.example.com  # Not http://
```

#### 2. SSL Certificate Verification Failed

**Error:**

```
❌ Connection failed: SSL: CERTIFICATE_VERIFY_FAILED
```

**Solution:**

```bash
# For self-signed certificates
export AAP_VERIFY_SSL=false

# Or add certificate to trust store (better)
sudo cp aap-cert.pem /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

#### 3. Connection Timeout

**Error:**

```
❌ Connection failed: Timeout
```

**Solution:**

```bash
# Increase timeout
export AAP_TIMEOUT=120

# Or check network connectivity
curl -k https://your-aap.example.com/api/v2/ping/
```

#### 4. Container Won't Start

**Error:**

```
Error: port already allocated
```

**Solution:**

```bash
# Check what's using port 8501
lsof -i :8501

# Stop conflicting service or change port
# Edit podman-compose.yml and change port mapping
```

#### 5. Missing Dependencies in CLI Mode

**Error:**

```
ModuleNotFoundError: No module named 'httpx'
```

**Solution:**

```bash
# Reinstall in virtual environment
pip install -e ".[dev]"

# Or install missing package directly
pip install httpx
```

#### 6. Token Expired or Invalid

**Error:**

```
❌ Connection failed: 401 Unauthorized
```

**Solution:**

```bash
# Generate new token in AAP UI:
# 1. Go to AAP UI → Users → <Your User>
# 2. Navigate to Tokens tab
# 3. Click "Add" to create new token
# 4. Copy token and update .env file

export AAP_TOKEN=new_token_here
aap-planner validate
```

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# CLI mode
export LOG_LEVEL=DEBUG
aap-planner validate

# Container mode (edit .env)
LOG_LEVEL=DEBUG
```

### Getting Help

If you encounter issues not covered here:

1. Check existing [GitHub Issues](https://github.com/arnav3000/aap-migration-planner/issues)
2. Review [SECURITY.md](SECURITY.md) for security-related questions
3. Review [ENTERPRISE_CLI_GUIDE.md](ENTERPRISE_CLI_GUIDE.md) for CLI usage patterns
4. Open a new issue with:
   - Error message (redact sensitive info)
   - Environment details (OS, Python version, container runtime)
   - Steps to reproduce

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
- [x] Core dependency analysis engine
- [x] HTML report generation
- [x] Risk scoring algorithm
- [x] CLI implementation
- [x] JSON export functionality
- [x] Interactive web UI with Streamlit
- [x] Container deployment (Podman/Docker)
- [x] SQLite database caching
- [x] AAP sizing calculator integration
- [x] HTTPS-only security enforcement
- [ ] Multi-AAP comparison mode
- [ ] PDF report export
- [ ] Authentication for web UI
- [ ] Scheduled analysis (cron integration)
- [ ] Email report delivery

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
