# AAP Dependency Analyzer & Migration Planner

> Automated dependency analysis and migration planning for Ansible Automation Platform

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![License: Commercial](https://img.shields.io/badge/License-Commercial-orange.svg)](LICENSE-COMMERCIAL.md)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

## 📜 Dual Licensing

This software is available under **two license options**:

### 🆓 Open Source (GPL v3) - **FREE**

Perfect for personal use, academic research, and open-source projects.  
[View GPL v3 License →](LICENSE)

### 💼 Commercial License - **Paid**

Required for proprietary software, SaaS offerings, and commercial products.  
Includes support, warranty, and no GPL copyleft obligations.  
[View Commercial License →](LICENSE-COMMERCIAL.md) | [Pricing →](PRICING.md)

**Need help choosing?** Email: arnav3000@gmail.com

---

## What Does It Do?

**🔍 Analyzer:** Understand your AAP environment

- Map cross-organization dependencies automatically
- Detect duplicate resources and naming violations
- Generate quality scores and governance reports
- Visualize interactive dependency graphs

**📋 Planner:** Execute safe migrations

- Calculate migration order based on dependencies
- Generate phase-by-phase migration timeline
- Identify blockers and critical paths
- Size infrastructure for AAP 2.6

**💡 Why?** Most AAP migration failures happen because of hidden dependencies. A job template in Org A references a credential in Org B → migrate in wrong order → production outage. This tool prevents that.

**🎮 Try it now:** No AAP instance needed! Includes demo data to explore all features instantly.

---

## 🚀 Quick Start (2 Minutes)

**Just want to try it? No AAP instance needed!**

```bash
# 1. Clone and start
git clone https://github.com/arnav3000/aap-migration-planner.git
cd aap-migration-planner
podman-compose up -d    # or: docker-compose up -d

# 2. Open browser
open http://localhost:8501

# 3. Click "🎲 Use Sample Data" button in the sidebar

# 4. Explore all features with demo data!
```

**That's it!** You can now:

- ✅ See dependency graphs
- ✅ View quality reports with duplicates
- ✅ Check migration phases
- ✅ Try the sizing calculator
- ✅ Export reports

---

### Connect to Your AAP Instance (Optional)

Once you're ready to analyze your real AAP environment:

1. **Create configuration file:**

   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials:**

   ```bash
   AAP_URL=https://your-aap-controller.example.com
   AAP_TOKEN=your_api_token_here
   AAP_VERIFY_SSL=false
   ```

3. **Restart containers:**

   ```bash
   podman-compose restart   # or: docker-compose restart
   ```

4. **In the UI:** Enter your AAP URL and token in sidebar, click "Connect"

---

### Option 2: CLI Installation

```bash
# Install from PyPI (when published)
pip install aap-migration-planner

# Or install from source
git clone https://github.com/arnav3000/aap-migration-planner.git
cd aap-migration-planner
pip install -e .

# Configure
export AAP_URL=https://your-aap.example.com
export AAP_TOKEN=your_api_token_here
export AAP_VERIFY_SSL=false

# Run analysis
aap-planner analyze --all
aap-planner report --format html --output report.html
```

---

## Configuration (Optional - for Real AAP Analysis)

**Note:** You can use sample data without any configuration. Only needed for connecting to your AAP instance.

Create a `.env` file with your AAP credentials:

```bash
# AAP Connection (HTTPS REQUIRED - HTTP is blocked for security)
AAP_URL=https://your-aap-controller.example.com
AAP_TOKEN=your_api_token_here
AAP_VERIFY_SSL=false  # Set to true for production with valid SSL

# Optional
AAP_TIMEOUT=60
LOG_LEVEL=INFO
```

**Security Note:** This tool only accepts HTTPS URLs to protect your API tokens. HTTP connections are automatically rejected.

---

## Features

### 🔍 Dependency Analysis

- Automatic discovery of cross-org references (credentials, inventories, projects, execution environments)
- Interactive dependency graph visualization
- Critical path identification

### ⚠️ Quality & Governance

- Duplicate resource detection (same name, same org)
- Naming convention analysis and violations
- Quality scoring with actionable recommendations
- Prefix usage patterns (environment, team, region)

### 📋 Migration Planning

- Topological sort for safe migration order
- Phase-by-phase grouping (parallel migrations where possible)
- Risk assessment and blocker identification
- Migration timeline visualization

### 📏 Infrastructure Sizing

- AAP 2.6 capacity calculator
- Execution node + control plane requirements
- Based on Red Hat official formulas

### 💾 Export & Reports

- HTML reports with graphs
- JSON export for automation
- Quality report downloads

---

## Web UI

The web interface provides 5 main tabs:

**1. 🔍 Analysis**

- Summary metrics (organizations, dependencies)
- Interactive dependency graph
- Critical path analysis
- Organization details

**2. ⚠️ Quality Report**

- Duplicate resource detection with severity levels
- Naming convention analysis and consistency scores
- Violations breakdown by organization
- Export quality reports

**3. 📋 Migration Plan**

- Phase-by-phase migration timeline
- Gantt chart visualization
- Dependency ordering

**4. 📊 Dashboard & Resources**

- Executive KPIs
- Resource breakdown by type
- Risk metrics

**5. 📏 Sizing Calculator**

- AAP 2.6 infrastructure sizing
- Calculate execution nodes and control plane needs

---

## CLI Commands

```bash
# Validate AAP connection
aap-planner validate

# Analyze single organization
aap-planner analyze --organization "Engineering"

# Analyze all organizations
aap-planner analyze --all --output analysis.json

# Generate HTML report
aap-planner report --format html --output plan.html

# Generate text report
aap-planner report --format text

# Generate JSON export
aap-planner report --format json --output export.json
```

---

## Container Management

**Start containers:**

```bash
podman-compose up -d    # or docker-compose up -d
```

**Stop containers:**

```bash
podman-compose down     # or docker-compose down
```

**View logs:**

```bash
podman-compose logs -f  # or docker-compose logs -f
```

**Rebuild after code changes:**

```bash
podman-compose up -d --build
```

**Clean up everything:**

```bash
podman-compose down -v
podman rmi aap-toolkit-web aap-toolkit-backend
```

---

## Use Cases

**1. Pre-Migration Risk Assessment**

- Identify all cross-org dependencies before migration
- Generate executive summary for stakeholders
- Estimate migration complexity

**2. Multi-Org Migration Sequencing**

- Discover which orgs can migrate independently
- Get recommended migration order
- Identify "foundation" orgs that must go first

**3. Continuous Governance**

- Monitor for duplicate resources
- Enforce naming conventions
- Track quality scores over time

**4. Infrastructure Planning**

- Size target AAP 2.6 environment
- Calculate execution node requirements
- Plan control plane capacity

---

## Requirements

**For Container Deployment:**

- Podman 4.0+ or Docker 20.10+
- podman-compose or docker-compose
- 2GB RAM
- HTTPS access to AAP 2.4+ instance

**For CLI:**

- Python 3.12+
- pip
- HTTPS access to AAP 2.4+ instance

**AAP Permissions:**

- Read access to organizations, job templates, workflows, credentials, inventories, projects

---

## Troubleshooting

**Port already in use:**

```bash
# Check what's using port 8501
lsof -i :8501
# Kill the process or change port in docker-compose.yml/podman-compose.yml
```

**SSL certificate errors:**

```bash
# For self-signed certificates, set in .env:
AAP_VERIFY_SSL=false
```

**Connection timeout:**

```bash
# Increase timeout in .env:
AAP_TIMEOUT=120
```

**HTTP URL rejected:**

```bash
# Change to HTTPS (HTTP is blocked for security):
AAP_URL=https://aap.example.com  # Not http://
```

---

## Architecture

```
┌─────────────────────────────────┐
│  Web UI (Streamlit)            │
│  Port: 8501                     │
│  - Interactive dashboard        │
│  - Dependency graphs            │
│  - Quality reports              │
└────────────┬────────────────────┘
             │
             │ Uses
             ▼
┌─────────────────────────────────┐
│  Backend Engine                │
│  - AAP API client              │
│  - Dependency analyzer         │
│  - Quality scanner             │
│  - Migration planner           │
└────────────┬────────────────────┘
             │
             │ Integrates
             ▼
┌─────────────────────────────────┐
│  Sizing Calculator             │
│  Port: 5002                     │
│  - AAP 2.6 capacity formulas   │
└─────────────────────────────────┘
```

**Tech Stack:**

- Python 3.12
- Streamlit (Web UI)
- Plotly (Visualizations)
- NetworkX (Graph algorithms)
- SQLite (Caching)
- httpx (Async HTTP)

---

## Security

✅ **HTTPS-Only:** HTTP connections blocked to protect API tokens  
✅ **Secret Detection:** Pre-commit hooks with Gitleaks  
✅ **SAST Scanning:** Bandit + Semgrep security analysis  
✅ **Container Scanning:** Trivy vulnerability detection  
✅ **Dependency Audits:** Weekly pip-audit scans  
✅ **SBOM Generation:** Software Bill of Materials for compliance  

See [SECURITY.md](SECURITY.md) for details.

---

## Related Projects

- **[aap-bridge](https://github.com/arnav3000/aap-bridge-fork)** - AAP migration execution tool (this tool analyzes, aap-bridge migrates)
- **[ansible-lint](https://github.com/ansible/ansible-lint)** - Ansible playbook linting
- **[Red Hat CoP](https://github.com/redhat-cop)** - Red Hat Communities of Practice

---

## Roadmap

- [x] Dependency analysis engine
- [x] Web UI with interactive graphs
- [x] Quality & governance scanning
- [x] Migration phase calculator
- [x] AAP 2.6 sizing integration
- [x] Container deployment
- [ ] Multi-AAP comparison mode
- [ ] PDF report export
- [ ] Email notifications
- [ ] Historical trending
- [ ] Integration with aap-bridge for automated migration

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

This software is **dual-licensed**:

### Open Source License (GPL v3)

Free for personal, academic, and GPL-compatible projects.  
📄 [View GPL v3 License](LICENSE)

### Commercial License

Required for proprietary/closed-source software, SaaS offerings, and commercial use cases that cannot comply with GPL v3 copyleft requirements.

**Benefits:**

- ✅ Proprietary use without GPL obligations
- ✅ SaaS and managed service deployment
- ✅ Warranty and indemnification
- ✅ Priority support (email, phone, 24/7 available)
- ✅ Custom development options

📄 [View Commercial License](LICENSE-COMMERCIAL.md)  
💰 [View Pricing](PRICING.md)

**Questions about licensing?** Email: arnav3000@gmail.com

---

## Support

### Community Support (GPL v3)

- **Issues:** [GitHub Issues](https://github.com/arnav3000/aap-migration-planner/issues)
- **Questions:** Open an issue with the "question" label
- **Response Time:** Best effort

### Commercial Support

- **Email Support:** Included with all commercial licenses (48h response)
- **Priority Support:** Available with Enterprise license (4h response)
- **Premium Support:** 24/7/365 with 1h response (add-on)
- **Professional Services:** Custom development, training, migration services

📧 **Contact:** arnav3000@gmail.com

---

**Made with ❤️ for the AAP community**
