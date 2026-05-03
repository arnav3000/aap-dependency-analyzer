## AAP Migration Toolkit - Web UI

Interactive web interface for AAP migration planning and capacity sizing.

### Features

- **🔍 Dependency Analysis** - Interactive graph visualization of cross-org dependencies
- **📋 Migration Planning** - Phase-by-phase timeline with recommended migration order
- **📊 Risk Dashboard** - Executive-level metrics and complexity scoring
- **📏 Capacity Sizing** - Infrastructure sizing calculator for AAP 2.6

### Quick Start

#### Using Containers (Recommended)

```bash
# Build and start all services
make start

# Access web UI
open http://localhost:8501
```

#### Local Development

```bash
# Install dependencies
pip install -e ".[dev]"
pip install streamlit plotly pandas networkx

# Run web UI
streamlit run web/app.py
```

### Architecture

```
web/
├── app.py                      # Main application entry point
├── pages/                      # Multi-page app sections
│   ├── 1_🔍_Analysis.py       # Dependency graph & analysis
│   ├── 2_📋_Migration_Plan.py # Migration phases & timeline
│   ├── 3_📊_Dashboard.py      # Risk metrics & dashboard
│   └── 4_📏_Sizing_Guide.py   # Capacity sizing integration
├── components/                 # Reusable UI components
│   ├── graph.py               # Dependency graph visualization
│   ├── phase_timeline.py      # Migration timeline charts
│   └── metrics.py             # Dashboard metrics widgets
└── utils/                      # Utility modules
    ├── session.py             # Streamlit session management
    └── data_loader.py         # AAP data loading & analysis
```

### Usage

#### 1. Connect to AAP

Enter your AAP credentials in the sidebar:

- **AAP URL**: `https://your-aap-instance.com`
- **API Token**: Your authentication token
- **Verify SSL**: Enable for production

Click "Connect" to establish connection.

#### 2. Run Analysis

Go to **Analysis** page:

- Select "All Organizations" or specific org
- Click "Run Analysis"
- View dependency graph and details
- Export results as JSON

#### 3. Review Migration Plan

Go to **Migration Plan** page:

- See recommended migration order
- Review phase breakdown
- Check risk assessment
- Export migration plan

#### 4. View Dashboard

Go to **Dashboard** page:

- Key metrics and KPIs
- Risk scoring by organization
- Resource distribution charts
- Complexity analysis

#### 5. Calculate Sizing

Go to **Sizing Guide** page:

- Enter workload parameters
- Click "Calculate Sizing"
- Review infrastructure requirements
- Export sizing results

### Sample Data Mode

For demos or testing without live AAP:

1. Check "Use Sample Data" on Analysis page
2. Click "Run Analysis"
3. Explore all features with realistic sample data

Generate custom samples:

```bash
python3 scripts/generate_sample_data.py
```

### Configuration

#### Environment Variables

Create `.env` file:

```bash
AAP_URL=https://aap.example.com
AAP_TOKEN=your_token_here
AAP_VERIFY_SSL=false
SIZING_GUIDE_URL=http://localhost:5002
```

#### Streamlit Configuration

Custom config in `.streamlit/config.toml`:

```toml
[server]
port = 8501
address = "0.0.0.0"

[theme]
primaryColor = "#EE0000"  # Red Hat red
backgroundColor = "#FFFFFF"
```

### Dependencies

**Required:**

- `streamlit>=1.30.0` - Web framework
- `plotly>=5.18.0` - Interactive charts
- `pandas>=2.1.0` - Data manipulation
- `networkx>=3.2` - Graph algorithms

**Optional:**

- `kaleido>=0.2.1` - Static image export

Install all:

```bash
pip install streamlit plotly pandas networkx kaleido
```

### Deployment

#### Container Deployment

```bash
# Build web UI container
podman build -t aap-toolkit-web:latest -f Containerfile.web .

# Run standalone
podman run -d \
  -p 8501:8501 \
  -e AAP_URL=https://aap.example.com \
  -e AAP_TOKEN=your_token \
  -v ./data:/app/data:Z \
  aap-toolkit-web:latest

# Or use compose
podman-compose -f podman-compose.yml up -d
```

#### Kubernetes Deployment

```bash
# Generate Kubernetes manifests
podman kube generate aap-toolkit-pod > k8s-deployment.yaml

# Deploy
kubectl apply -f k8s-deployment.yaml
```

### Troubleshooting

#### Web UI Won't Load

```bash
# Check if port is available
lsof -i :8501

# Check container logs
podman logs aap-toolkit-web

# Restart service
make restart
```

#### Analysis Fails

- **Check AAP credentials** in .env file
- **Verify network connectivity** to AAP instance
- **Check SSL settings** if using self-signed certs
- **View logs** for detailed error messages

#### Sizing Guide Unavailable

```bash
# Check if sizing guide is running
curl http://localhost:5002/health

# Start sizing guide
podman start aap-sizing-guide

# Or restart all services
make start
```

#### Graph Visualization Missing

Install missing dependencies:

```bash
pip install plotly networkx
```

### Development

#### Running Locally

```bash
# Install in editable mode
pip install -e ".[dev]"

# Install web dependencies
pip install streamlit plotly pandas networkx

# Run with hot reload
streamlit run web/app.py
```

#### Adding New Pages

1. Create file: `web/pages/N_Icon_Name.py`
2. Add page content
3. Import utilities: `from web.utils.session import init_session_state`
4. Streamlit auto-detects new pages

#### Adding New Components

1. Create file: `web/components/component_name.py`
2. Define render functions
3. Import in pages: `from web.components.component_name import render_function`

### Performance

#### Caching

Analysis results are cached in session state. To clear:

```python
st.session_state.analysis_data = None
```

#### Large Datasets

For 50+ organizations:

- Use filters on Analysis page
- Limit graph to top N orgs
- Export to JSON for external analysis

### Security

#### Best Practices

- **Never commit `.env`** files with real credentials
- **Use SSL verification** in production
- **Run containers rootless** (Podman default)
- **Limit network exposure** (firewall port 8501)

#### Data Handling

- Credentials used only for API calls
- No persistent storage of tokens
- Analysis results saved locally only
- No external data transmission

### Support

- **Issues**: https://github.com/arnav3000/aap-migration-planner/issues
- **Documentation**: See CLAUDE.md for architecture
- **Demo Script**: See docs/demo_script.md

### License

GPL-3.0 - See LICENSE file
