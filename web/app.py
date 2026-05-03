"""AAP Migration Toolkit - Main Streamlit Application

This is the main entry point for the web UI. It provides a unified interface
for dependency analysis, migration planning, and capacity sizing.
"""

import streamlit as st

# Configure page
st.set_page_config(
    page_title="AAP Migration Toolkit",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for professional look
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #EE0000;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .feature-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        border-left: 4px solid #EE0000;
        margin-bottom: 1rem;
    }
    .metric-card {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 0.5rem;
        color: white;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar - AAP Connection
with st.sidebar:
    st.markdown("### 🚀 AAP Migration Toolkit")
    st.markdown("---")

    # Connection configuration
    st.markdown("#### Connection")

    # Initialize session state for connection
    if "aap_url" not in st.session_state:
        st.session_state.aap_url = ""
    if "aap_connected" not in st.session_state:
        st.session_state.aap_connected = False

    aap_url = st.text_input(
        "AAP URL",
        value=st.session_state.aap_url,
        placeholder="https://aap.example.com",
        help="Enter your AAP Controller URL",
    )

    aap_token = st.text_input(
        "API Token", type="password", help="Your AAP API authentication token"
    )

    verify_ssl = st.checkbox("Verify SSL", value=False)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 Connect", use_container_width=True):
            if aap_url and aap_token:
                st.session_state.aap_url = aap_url
                st.session_state.aap_token = aap_token
                st.session_state.verify_ssl = verify_ssl
                st.session_state.aap_connected = True
                st.success("Connected!")
                st.rerun()
            else:
                st.error("Please provide URL and token")

    with col2:
        if st.button("🔓 Disconnect", use_container_width=True):
            st.session_state.aap_connected = False
            st.session_state.clear()
            st.rerun()

    # Connection status
    if st.session_state.aap_connected:
        st.success("✅ Connected")
        st.caption(f"URL: {st.session_state.aap_url}")
    else:
        st.warning("⚠️ Not connected")

    st.markdown("---")

    # Navigation info
    st.markdown("#### 📚 Tools")
    st.markdown("""
    - 🔍 **Analysis**: Dependency graphs
    - 📋 **Migration Plan**: Phase timeline
    - 📊 **Dashboard**: Risk metrics
    - 📏 **Sizing Guide**: Capacity planning
    """)

    st.markdown("---")
    st.caption("Version 0.1.0")

# Main page content
st.markdown('<div class="main-header">AAP Migration Toolkit</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Plan your AAP migrations with confidence</div>', unsafe_allow_html=True
)

# Welcome message
st.markdown("""
Welcome to the **AAP Migration Toolkit** - your comprehensive solution for planning
and executing Ansible Automation Platform migrations.
""")

# Feature cards
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
    <div class="feature-card">
        <h3>🔍 Dependency Analysis</h3>
        <p>Discover cross-organization dependencies and resource relationships.
        Visualize complex dependency graphs to understand migration impact.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div class="feature-card">
        <h3>📋 Migration Planning</h3>
        <p>Get recommended migration sequences with phase-by-phase breakdown.
        Identify which organizations can migrate in parallel.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
    <div class="feature-card">
        <h3>📊 Risk Assessment</h3>
        <p>Identify migration risks before execution. See metrics, complexity scores,
        and potential blockers across your AAP instance.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div class="feature-card">
        <h3>📏 Capacity Sizing</h3>
        <p>Calculate infrastructure requirements for your target AAP environment.
        Get sizing recommendations based on workload analysis.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# Quick stats if connected
if st.session_state.aap_connected:
    st.markdown("### 📊 Quick Stats")

    # Placeholder for actual stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Organizations", value="—", help="Total organizations analyzed")

    with col2:
        st.metric(label="Dependencies", value="—", help="Cross-org dependencies detected")

    with col3:
        st.metric(label="Resources", value="—", help="Total resources scanned")

    with col4:
        st.metric(label="Risk Score", value="—", help="Overall migration complexity")

    st.info("👈 Select a tool from the sidebar to get started")
else:
    st.markdown("### 🔌 Getting Started")
    st.info("""
    1. Enter your AAP credentials in the sidebar
    2. Click "Connect" to establish connection
    3. Choose a tool from the sidebar navigation
    4. Start analyzing your AAP environment
    """)

st.markdown("---")

# Footer
st.markdown(
    """
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>Made with ❤️ for the AAP community</p>
    <p><a href="https://github.com/arnav3000/aap-migration-planner" target="_blank">GitHub</a> |
    <a href="https://github.com/arnav3000/aap-migration-planner/issues" target="_blank">Report Issue</a></p>
</div>
""",
    unsafe_allow_html=True,
)
