"""AAP Migration Toolkit - Unified Single-Page Application

This is the main entry point for the web UI. It provides a unified tabbed interface
for dependency analysis, migration planning, risk assessment, and capacity sizing.
"""

import asyncio
import json
import sys
import time
from pathlib import Path

import pandas as pd
import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aap_migration_planner.database import DatabaseService
from aap_migration_planner.sizing import AAP26SizingCalculator
from web.components.metrics import render_resource_breakdown, render_risk_metrics
from web.components.phase_timeline import render_migration_timeline
from web.utils.data_loader import get_sample_data, run_analysis_async, save_to_file
from web.utils.session import get_connection_config, init_session_state, is_connected

# Initialize session
init_session_state()

# Configure page (can only be called once)
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
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 24px;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #EE0000;
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
            if not aap_url or not aap_token:
                st.error("Please provide URL and token")
            elif not aap_url.startswith("https://"):
                if aap_url.startswith("http://"):
                    suggested_url = aap_url.replace("http://", "https://", 1)
                    st.error(
                        f"🔒 **Security Error**: HTTP URLs are not allowed. "
                        f"API tokens must be transmitted over HTTPS only.\n\n"
                        f"Please use: `{suggested_url}`"
                    )
                else:
                    st.error("🔒 **Security Error**: URL must start with https://")
            else:
                st.session_state.aap_url = aap_url
                st.session_state.aap_token = aap_token
                st.session_state.verify_ssl = verify_ssl
                st.session_state.aap_connected = True
                st.success("✅ Connected securely via HTTPS")
                st.rerun()

    with col2:
        if st.button("🔓 Disconnect", use_container_width=True):
            st.session_state.aap_connected = False
            st.session_state.clear()
            st.rerun()

    # Connection status
    if st.session_state.aap_connected:
        st.success("✅ Connected (HTTPS)")
        st.caption(f"🔒 {st.session_state.aap_url}")
    else:
        st.warning("⚠️ Not connected")

    # Security notice
    with st.expander("🔒 Security Notice", expanded=False):
        st.caption(
            "**HTTPS Required**: This tool only accepts HTTPS URLs to protect your "
            "API tokens during transmission. HTTP connections are blocked for security."
        )

    st.markdown("---")
    st.caption("Version 0.1.0")


# Main page header
st.markdown('<div class="main-header">AAP Migration Toolkit</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Plan your AAP migrations with confidence</div>',
    unsafe_allow_html=True,
)

# Main tabbed interface
tab1, tab2, tab3, tab4 = st.tabs(
    ["🔍 Analysis", "📋 Migration Plan", "📊 Dashboard & Resources", "📏 Sizing Calculator"]
)

# ==================== TAB 1: ANALYSIS ====================
with tab1:
    st.markdown("### 🔍 Dependency Analysis")
    st.caption("Discover cross-organization dependencies and visualize migration impact")
    st.markdown("---")

    # Check connection
    if not is_connected():
        st.warning("⚠️ Not connected to AAP. Please connect using the sidebar.")
        st.info("Enter your AAP credentials in the sidebar and click 'Connect'")
    else:
        # Cache Statistics
        try:
            db_service = DatabaseService(db_path="data/aap_analysis.db")
            stats = db_service.get_stats()

            if stats["total_orgs"] > 0:
                with st.expander("📊 Cache Statistics", expanded=False):
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Cached Organizations", stats["total_orgs"])

                    with col2:
                        st.metric("Cached Resources", f"{stats['total_resources']:,}")

                    with col3:
                        st.metric("Dependencies Tracked", stats["total_dependencies"])

                    with col4:
                        if stats["last_analysis"]:
                            st.metric(
                                "Last Analysis", stats["last_analysis"].strftime("%Y-%m-%d %H:%M")
                            )
                        else:
                            st.metric("Last Analysis", "Never")

                    col_a, col_b = st.columns([3, 1])

                    with col_a:
                        st.caption(
                            "✅ Using database cache for faster analysis. Fresh data fetched only for changed orgs."
                        )

                    with col_b:
                        if st.button("🗑️ Clear Cache", use_container_width=True):
                            for org in db_service.get_all_organizations():
                                db_service.clear_organization(org.name)
                            st.success("Cache cleared!")
                            st.rerun()
        except Exception:
            pass  # Database not initialized yet

        # Analysis controls
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            analysis_mode = st.radio(
                "Analysis Mode", ["All Organizations", "Specific Organization"], horizontal=True
            )

        with col2:
            if analysis_mode == "Specific Organization":
                org_name = st.text_input("Organization Name", placeholder="Engineering")
            else:
                org_name = None

        with col3:
            use_sample = st.checkbox("Use Sample Data", help="Use demo data instead of live AAP")

        # Advanced settings
        with st.expander("⚙️ Advanced Settings"):
            st.markdown("**Parallelism Configuration**")
            col1, col2 = st.columns(2)

            with col1:
                max_concurrent_orgs = st.slider(
                    "Max Concurrent Organizations",
                    min_value=1,
                    max_value=20,
                    value=5,
                    help="How many organizations to analyze in parallel",
                )

            with col2:
                max_concurrent_resources = st.slider(
                    "Max Concurrent Resource Fetches",
                    min_value=5,
                    max_value=50,
                    value=20,
                    help="How many resource types to fetch in parallel per org",
                )

        # Run analysis button
        if st.button("🔍 Run Analysis", type="primary", use_container_width=True):
            if use_sample:
                st.session_state.analysis_data = get_sample_data()
                st.success("✅ Sample data loaded!")
            else:
                # Progress tracking UI
                progress_container = st.container()
                with progress_container:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    eta_text = st.empty()

                start_time = time.time()
                progress_data = {"current": 0, "total": 1, "message": "Starting..."}

                def update_progress(current, total, message):
                    """Progress callback to update UI."""
                    progress_data["current"] = current
                    progress_data["total"] = total
                    progress_data["message"] = message

                    if total > 0:
                        progress = current / total
                        progress_bar.progress(progress)

                        elapsed = time.time() - start_time
                        if current > 0:
                            rate = elapsed / current
                            remaining = (total - current) * rate
                            eta_min = int(remaining / 60)
                            eta_sec = int(remaining % 60)
                            eta_text.caption(
                                f"⏱️ ETA: {eta_min}m {eta_sec}s | Speed: {current/elapsed:.1f} orgs/sec"
                            )

                    status_text.info(f"📊 {message} ({current}/{total})")

                config = get_connection_config()

                try:
                    result = asyncio.run(
                        run_analysis_async(
                            config["url"],
                            config["token"],
                            config["verify_ssl"],
                            org_name,
                            progress_callback=update_progress,
                            max_concurrent_orgs=max_concurrent_orgs,
                            max_concurrent_resources=max_concurrent_resources,
                        )
                    )

                    if result:
                        progress_bar.progress(1.0)
                        status_text.success("✅ Analysis complete!")

                        elapsed_total = time.time() - start_time
                        total_orgs = progress_data.get("total", 0)
                        eta_text.success(
                            f"✅ Completed in {int(elapsed_total/60)}m {int(elapsed_total%60)}s | Analyzed {total_orgs} organizations"
                        )

                        st.session_state.analysis_data = result
                        st.success("✅ Analysis complete!")
                        save_to_file(result, "data/latest_analysis.json")
                    else:
                        st.error("❌ Analysis failed")

                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    import traceback

                    with st.expander("Show error details"):
                        st.code(traceback.format_exc())

        # Display results
        if st.session_state.analysis_data:
            data = st.session_state.analysis_data

            # Summary metrics
            st.markdown("### 📊 Summary")

            if data.get("type") == "global":
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Organizations", data.get("total_organizations", 0))

                with col2:
                    st.metric(
                        "Independent",
                        len(data.get("independent_orgs", [])),
                        help="Organizations with no dependencies",
                    )

                with col3:
                    st.metric(
                        "Dependent",
                        len(data.get("dependent_orgs", [])),
                        help="Organizations with cross-org dependencies",
                    )

                with col4:
                    total_deps = sum(
                        len(report.get("dependencies", {}))
                        for report in data.get("org_reports", {}).values()
                    )
                    st.metric(
                        "Dependencies", total_deps, help="Total cross-org dependency relationships"
                    )

            st.markdown("---")

            # Resource Quality Warnings
            if data.get("type") == "global":
                total_duplicates = data.get("total_duplicates", 0)
                avg_quality = data.get("average_quality_score", 100.0)

                if total_duplicates > 0:
                    st.markdown("### ⚠️ Resource Quality Warnings")
                    st.caption("Duplicate resources detected that may cause migration issues")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        severity_color = (
                            "🔴"
                            if total_duplicates >= 10
                            else "🟡"
                            if total_duplicates >= 5
                            else "🟢"
                        )
                        st.metric(
                            f"{severity_color} Duplicate Resources",
                            total_duplicates,
                            help="Resources with identical names in the same organization",
                        )

                    with col2:
                        score_color = (
                            "🔴" if avg_quality < 60 else "🟡" if avg_quality < 80 else "🟢"
                        )
                        st.metric(
                            f"{score_color} Quality Score",
                            f"{avg_quality:.1f}%",
                            help="Average quality score across all organizations (100% = perfect)",
                        )

                    with col3:
                        # Count orgs with duplicates
                        orgs_with_dups = sum(
                            1
                            for report in data.get("org_reports", {}).values()
                            if report.get("quality_report")
                            and report["quality_report"]["duplicate_count"] > 0
                        )
                        st.metric(
                            "🏢 Organizations Affected",
                            orgs_with_dups,
                            help="Organizations containing duplicate resources",
                        )

                    # Show detailed duplicates by organization
                    with st.expander("🔍 View Duplicate Details", expanded=False):
                        org_reports = data.get("org_reports", {})

                        for org_name, report in sorted(org_reports.items()):
                            quality_report = report.get("quality_report")
                            if not quality_report or quality_report["duplicate_count"] == 0:
                                continue

                            st.markdown(f"#### 🏢 {org_name}")
                            st.caption(
                                f"Quality Score: {quality_report['quality_score']:.1f}% | {quality_report['duplicate_count']} duplicate(s)"
                            )

                            for dup in quality_report["duplicates"]:
                                severity_emoji = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(
                                    dup["severity"], "⚪"
                                )

                                with st.container():
                                    col_a, col_b = st.columns([3, 1])

                                    with col_a:
                                        st.markdown(
                                            f"{severity_emoji} **{dup['resource_type_display']}:** `{dup['name']}`"
                                        )
                                        st.caption(f"**Impact:** {dup['impact']}")

                                    with col_b:
                                        st.metric("Copies", dup["count"])

                                    st.info(f"💡 **Recommendation:** {dup['recommendation']}")
                                    st.caption(f"IDs: {', '.join(map(str, dup['ids']))}")
                                    st.markdown("---")

                    st.markdown("---")

            # Critical Path Analysis - Migration Blockers
            st.markdown("### 🚨 Migration Blockers & Critical Path")
            st.caption("Organizations that block the most migrations - must migrate these first")

            if data.get("type") == "global":
                org_reports = data.get("org_reports", {})

                # Calculate who blocks whom (reverse dependencies)
                blocking_count = {}
                for org_name, report in org_reports.items():
                    blocking_count[org_name] = 0

                # Count how many orgs each org blocks
                for org_name, report in org_reports.items():
                    deps = report.get("dependencies", {})
                    for dep_org in deps.keys():
                        if dep_org in blocking_count:
                            blocking_count[dep_org] += 1

                # Sort by blocking count (descending)
                blockers = sorted(blocking_count.items(), key=lambda x: x[1], reverse=True)

                # Show top blockers
                top_blockers = [b for b in blockers if b[1] > 0][:10]

                if top_blockers:
                    st.warning(
                        f"⚠️ Found {len([b for b in blockers if b[1] > 0])} organizations that block other migrations"
                    )

                    # Display in columns
                    cols = st.columns(2)
                    for idx, (org_name, count) in enumerate(top_blockers):
                        with cols[idx % 2]:
                            severity = "🔴" if count >= 5 else "🟡" if count >= 2 else "🟢"
                            st.metric(
                                f"{severity} {org_name}",
                                f"{count} org(s) blocked",
                                help=f"Must migrate {org_name} before {count} other organizations can migrate",
                            )

                    # Show migration order recommendation
                    migration_order = data.get("migration_order", [])
                    if migration_order:
                        with st.expander("📋 Recommended Migration Order"):
                            st.markdown(
                                "Migrate in this sequence to minimize dependency conflicts:"
                            )
                            order_text = ""
                            for idx, org in enumerate(migration_order[:20], 1):
                                blocker_count = blocking_count.get(org, 0)
                                if blocker_count > 0:
                                    order_text += f"{idx}. **{org}** 🚨 _({blocker_count} orgs depend on this)_\n"
                                else:
                                    order_text += f"{idx}. {org}\n"
                            st.markdown(order_text)
                            if len(migration_order) > 20:
                                st.caption(
                                    f"... and {len(migration_order) - 20} more. See Migration Plan tab for complete order."
                                )
                else:
                    st.success(
                        "✅ No blocking dependencies! All organizations can migrate independently."
                    )

            st.markdown("---")

            # Dependency Chain Explorer
            st.markdown("### 🔗 Dependency Chain Explorer")
            st.caption("Explore dependency relationships - shows what each organization depends on")

            if data.get("type") == "global":
                org_reports = data.get("org_reports", {})

                # Search/filter
                search_org = st.text_input(
                    "🔍 Search Organization",
                    placeholder="Type to filter organizations...",
                    key="dep_chain_search",
                )

                # Filter organizations based on search
                filtered_orgs = {}
                for org_name, report in org_reports.items():
                    if not search_org or search_org.lower() in org_name.lower():
                        filtered_orgs[org_name] = report

                if filtered_orgs:
                    # Show dependency chains
                    for org_name in sorted(filtered_orgs.keys()):
                        report = filtered_orgs[org_name]
                        deps = report.get("dependencies", {})
                        can_migrate_standalone = report.get("can_migrate_standalone", True)

                        # Build chain summary
                        if deps:
                            dep_summary = f"→ Depends on {len(deps)} org(s)"
                            icon = "🔴" if len(deps) >= 3 else "🟡"
                        else:
                            dep_summary = "✅ Independent"
                            icon = "🟢"

                        with st.expander(f"{icon} **{org_name}** {dep_summary}"):
                            if deps:
                                st.markdown("**Dependency Chain:**")

                                for dep_org, dep_resources in deps.items():
                                    resource_count = len(dep_resources)
                                    st.markdown(
                                        f"  └─ **{dep_org}** ({resource_count} resource(s))"
                                    )

                                    # Show resource breakdown
                                    resource_types = {}
                                    for res in dep_resources:
                                        rtype = res.get("resource_type", "unknown")
                                        if rtype not in resource_types:
                                            resource_types[rtype] = 0
                                        resource_types[rtype] += 1

                                    resource_list = ", ".join(
                                        [
                                            f"{count} {rtype.replace('_', ' ')}"
                                            for rtype, count in sorted(resource_types.items())
                                        ]
                                    )
                                    st.caption(f"     ↳ {resource_list}")

                                # Show migration requirement
                                req_before = report.get("required_migrations_before", [])
                                if req_before:
                                    st.info(f"⚠️ **Must migrate first:** {', '.join(req_before)}")
                            else:
                                st.success(
                                    "✅ This organization has no dependencies and can migrate at any time."
                                )
                else:
                    st.info(f"No organizations found matching '{search_org}'")

            st.markdown("---")

            # Organization Details with Cross-Org Dependencies
            st.markdown("### 📋 Detailed Organization Information")
            st.caption("Deep dive into resources and dependency details per organization")

            if data.get("type") == "global":
                org_reports = data.get("org_reports", {})

                # Filter options
                filter_option = st.radio(
                    "Show",
                    ["All", "Independent Only", "Dependent Only"],
                    horizontal=True,
                    key="org_filter",
                )

                for org_name, report in org_reports.items():
                    has_deps = report.get("has_cross_org_deps", False)

                    # Apply filter
                    if filter_option == "Independent Only" and has_deps:
                        continue
                    if filter_option == "Dependent Only" and not has_deps:
                        continue

                    with st.expander(
                        f"**{org_name}** - {report.get('resource_count', 0)} resources"
                    ):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"**Organization ID:** {report.get('org_id')}")
                            st.markdown(f"**Total Resources:** {report.get('resource_count', 0)}")
                            st.markdown(
                                f"**Can Migrate Standalone:** {'✅ Yes' if report.get('can_migrate_standalone') else '❌ No'}"
                            )

                        with col2:
                            deps = report.get("dependencies", {})
                            if deps:
                                st.markdown(f"**Dependencies ({len(deps)} org(s)):**")
                                for dep_org, dep_resources in deps.items():
                                    st.markdown(f"  - {dep_org}: {len(dep_resources)} resource(s)")
                            else:
                                st.markdown("**Dependencies:** None")

                        # Show required migrations before
                        req_before = report.get("required_migrations_before", [])
                        if req_before:
                            st.info(
                                f"⚠️ Must migrate these organizations first: {', '.join(req_before)}"
                            )

                        # Detailed dependency breakdown
                        deps = report.get("dependencies", {})
                        if deps:
                            st.markdown("---")
                            st.markdown("#### 🔍 Detailed Dependencies")

                            for dep_org, dep_resources in deps.items():
                                with st.expander(
                                    f"📦 Dependencies on **{dep_org}** ({len(dep_resources)} resources)"
                                ):
                                    # Group by resource type
                                    by_type = {}
                                    for dep in dep_resources:
                                        res_type = dep.get("resource_type", "unknown")
                                        if res_type not in by_type:
                                            by_type[res_type] = []
                                        by_type[res_type].append(dep)

                                    for res_type, resources in sorted(by_type.items()):
                                        st.markdown(
                                            f"**{res_type.replace('_', ' ').title()}** ({len(resources)})"
                                        )

                                        # Create table data
                                        table_data = []
                                        for dep in resources:
                                            required_by = dep.get("required_by", [])
                                            required_by_str = ", ".join(
                                                [
                                                    f"{r.get('name', 'unknown')} ({r.get('type', 'unknown')})"
                                                    for r in required_by[:3]
                                                ]
                                            )
                                            if len(required_by) > 3:
                                                required_by_str += (
                                                    f" ... +{len(required_by) - 3} more"
                                                )

                                            table_data.append(
                                                {
                                                    "Resource Name": dep.get(
                                                        "resource_name", "N/A"
                                                    ),
                                                    "ID": dep.get("resource_id", "N/A"),
                                                    "Used By": required_by_str
                                                    if required_by_str
                                                    else "N/A",
                                                }
                                            )

                                        if table_data:
                                            df = pd.DataFrame(table_data)
                                            st.dataframe(
                                                df, use_container_width=True, hide_index=True
                                            )
                                        st.markdown("")

            st.markdown("---")

            # Export options
            st.markdown("### 💾 Export")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("📄 Download JSON", use_container_width=True, key="analysis_json"):
                    json_str = json.dumps(data, indent=2, default=str)
                    st.download_button(
                        "⬇️ Download", json_str, file_name="analysis.json", mime="application/json"
                    )

            with col2:
                if st.button("🖼️ Download Graph", use_container_width=True, key="analysis_graph"):
                    st.info("Graph export coming soon!")

            with col3:
                if st.button("📊 Generate Report", use_container_width=True, key="analysis_report"):
                    st.info("Report generation coming soon!")

        else:
            st.info("👆 Click 'Run Analysis' to get started")


# ==================== TAB 2: MIGRATION PLAN ====================
with tab2:
    st.markdown("### 📋 Migration Plan")
    st.caption("Phase-by-phase migration timeline with dependency ordering")
    st.markdown("---")

    # Check connection
    if not is_connected():
        st.warning("⚠️ Not connected to AAP. Please connect using the sidebar.")
    elif not st.session_state.analysis_data:
        st.warning("⚠️ No analysis data available. Please run analysis first.")
        st.info("👉 Go to **Analysis** tab and click 'Run Analysis'")
    else:
        data = st.session_state.analysis_data

        # Only show for global analysis
        if data.get("type") != "global":
            st.warning(
                "⚠️ Migration plan is only available for global (all organizations) analysis."
            )
            st.info("👉 Go to **Analysis** tab and run analysis with 'All Organizations' mode")
        else:
            # Migration summary
            st.markdown("### 📊 Migration Summary")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Phases", len(data.get("migration_phases", [])))

            with col2:
                st.metric("Total Organizations", data.get("total_organizations", 0))

            with col3:
                phases = len(data.get("migration_phases", []))
                estimated_days = phases * 7
                st.metric(
                    "Estimated Duration",
                    f"{estimated_days} days",
                    help="Estimated timeline assuming 1 week per phase",
                )

            st.markdown("---")

            # Phase details
            st.markdown("### 📅 Migration Phases")

            migration_phases = data.get("migration_phases", [])
            if migration_phases:
                # Render timeline visualization
                render_migration_timeline(migration_phases, data.get("org_reports", {}))

                # Phase breakdown
                for phase in migration_phases:
                    phase_num = phase.get("phase")
                    orgs = phase.get("orgs", [])
                    description = phase.get("description", "")

                    with st.expander(
                        f"**Phase {phase_num}** - {len(orgs)} organization(s)",
                        expanded=(phase_num == 1),
                    ):
                        st.markdown(f"**Description:** {description}")
                        st.markdown(f"**Organizations:** {', '.join(orgs)}")

                        org_reports = data.get("org_reports", {})
                        total_resources = sum(
                            org_reports.get(org, {}).get("resource_count", 0) for org in orgs
                        )
                        st.markdown(f"**Total Resources:** {total_resources}")

                        if len(orgs) > 1:
                            st.success(
                                f"✅ These {len(orgs)} organizations can migrate in parallel"
                            )
                        else:
                            st.info("ℹ️ Single organization in this phase")

            st.markdown("---")

            # Export migration plan
            st.markdown("### 💾 Export Migration Plan")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📄 Download Plan (JSON)", use_container_width=True, key="plan_json"):
                    plan_data = {
                        "migration_order": data.get("migration_order", []),
                        "migration_phases": migration_phases,
                        "independent_orgs": data.get("independent_orgs", []),
                        "dependent_orgs": data.get("dependent_orgs", []),
                        "total_organizations": data.get("total_organizations"),
                    }
                    json_str = json.dumps(plan_data, indent=2)
                    st.download_button(
                        "⬇️ Download",
                        json_str,
                        file_name="migration_plan.json",
                        mime="application/json",
                    )

            with col2:
                if st.button("📊 Download Plan (PDF)", use_container_width=True, key="plan_pdf"):
                    st.info("PDF export coming soon!")


# ==================== TAB 3: DASHBOARD & RESOURCES ====================
with tab3:
    st.markdown("### 📊 Dashboard & Resources")
    st.caption("Risk metrics, resource distribution, and resource browser")
    st.markdown("---")

    # Check connection
    if not is_connected():
        st.warning("⚠️ Not connected to AAP. Please connect using the sidebar.")
    elif not st.session_state.analysis_data:
        st.warning("⚠️ No analysis data available. Please run analysis first.")
        st.info("👉 Go to **Analysis** tab and click 'Run Analysis'")
    else:
        data = st.session_state.analysis_data

        # Only show for global analysis
        if data.get("type") != "global":
            st.warning(
                "⚠️ Dashboard and resources are only available for global (all organizations) analysis."
            )
            st.info("👉 Go to **Analysis** tab and run analysis with 'All Organizations' mode")
        else:
            # Sub-tabs for Dashboard and Resources
            dashboard_tab, resources_tab = st.tabs(["📊 Dashboard", "📦 Resources"])

            with dashboard_tab:
                # Key metrics
                st.markdown("### 📈 Key Metrics")

                col1, col2, col3, col4, col5 = st.columns(5)

                org_reports = data.get("org_reports", {})
                total_orgs = data.get("total_organizations", 0)
                independent_count = len(data.get("independent_orgs", []))
                dependent_count = len(data.get("dependent_orgs", []))

                total_resources = sum(
                    report.get("resource_count", 0) for report in org_reports.values()
                )
                total_dependencies = sum(
                    len(report.get("dependencies", {})) for report in org_reports.values()
                )

                with col1:
                    st.metric("Total Organizations", total_orgs)

                with col2:
                    st.metric(
                        "Independent",
                        independent_count,
                        delta=f"{round(independent_count/total_orgs*100) if total_orgs else 0}%",
                        delta_color="normal",
                    )

                with col3:
                    st.metric(
                        "Dependent",
                        dependent_count,
                        delta=f"{round(dependent_count/total_orgs*100) if total_orgs else 0}%",
                        delta_color="inverse",
                    )

                with col4:
                    st.metric("Total Resources", total_resources)

                with col5:
                    st.metric("Cross-Org Dependencies", total_dependencies)

                st.markdown("---")

                # Risk scoring
                st.markdown("### ⚠️ Risk Analysis")
                render_risk_metrics(org_reports)

                st.markdown("---")

                # Resource breakdown
                st.markdown("### 📦 Resource Distribution")
                render_resource_breakdown(org_reports)

                st.markdown("---")

                # Organization comparison
                st.markdown("### 🏢 Organization Comparison")

                comparison_data = []
                for org_name, report in org_reports.items():
                    comparison_data.append(
                        {
                            "Organization": org_name,
                            "Resources": report.get("resource_count", 0),
                            "Dependencies": len(report.get("dependencies", {})),
                            "Can Migrate Standalone": "✅ Yes"
                            if report.get("can_migrate_standalone")
                            else "❌ No",
                            "Required Before": ", ".join(
                                report.get("required_migrations_before", [])
                            )
                            or "None",
                        }
                    )

                df = pd.DataFrame(comparison_data)
                df = df.sort_values("Resources", ascending=False)
                st.dataframe(df, use_container_width=True, hide_index=True)

            with resources_tab:
                st.markdown("### 📦 Resource Browser")
                st.caption("Browse all resources in AAP")

                # Resource scope selector
                resource_scope = st.radio(
                    "Resource Scope",
                    ["🌐 Global Resources", "🏢 Organization Resources"],
                    key="resource_scope",
                    horizontal=True,
                )

                if resource_scope == "🌐 Global Resources":
                    # Display global resources
                    global_resources = data.get("global_resources", {})

                    if not global_resources:
                        st.info("No global resources found in this AAP instance")
                    else:
                        # Summary metrics
                        st.markdown("#### 🌐 Global Resources")
                        st.caption("Resources not tied to any specific organization")

                        col1, col2 = st.columns(2)

                        with col1:
                            total_global = sum(len(items) for items in global_resources.values())
                            st.metric("Total Global Resources", total_global)
                        with col2:
                            resource_types = len(
                                [rt for rt, items in global_resources.items() if items]
                            )
                            st.metric("Resource Types", resource_types)

                        st.markdown("---")

                        # Resource type selector
                        available_types = sorted(
                            [rt for rt, items in global_resources.items() if items]
                        )

                        if available_types:
                            selected_type = st.selectbox(
                                "Select Resource Type",
                                available_types,
                                format_func=lambda x: f"{x.replace('_', ' ').title()} ({len(global_resources.get(x, []))})",
                                key="global_type_selector",
                            )

                            if selected_type:
                                items = global_resources.get(selected_type, [])

                                st.markdown(f"#### {selected_type.replace('_', ' ').title()}")
                                st.caption(f"{len(items)} resources")

                                # Build dataframe
                                table_data = []
                                for item in items:
                                    row = {
                                        "ID": item.get("id", "N/A"),
                                        "Name": item.get("name", "N/A"),
                                        "Description": (item.get("description", "")[:80] + "...")
                                        if len(item.get("description", "")) > 80
                                        else item.get("description", ""),
                                        "Modified": item.get("modified", "N/A")[:19]
                                        if item.get("modified")
                                        else "N/A",
                                    }
                                    table_data.append(row)

                                if table_data:
                                    df = pd.DataFrame(table_data)
                                    st.dataframe(df, use_container_width=True, hide_index=True)
                        else:
                            st.info("No global resources available")

                else:
                    # Organization-specific resources
                    org_names = sorted(org_reports.keys())
                    selected_org = st.selectbox(
                        "Select Organization", org_names, key="org_selector"
                    )

                    if selected_org:
                        report = org_reports[selected_org]
                        resources = report.get("resources", {})

                        # Summary metrics
                        st.markdown(f"#### {selected_org}")
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Organization ID", report.get("org_id"))
                        with col2:
                            total_resources = sum(
                                len(items) for items in resources.values() if items
                            )
                            st.metric("Total Resources", total_resources)
                        with col3:
                            resource_types = len([rt for rt, items in resources.items() if items])
                            st.metric("Resource Types", resource_types)

                        st.markdown("---")

                        # Resource type selector
                        available_types = sorted([rt for rt, items in resources.items() if items])

                        if not available_types:
                            st.info("No resources found in this organization")
                        else:
                            selected_type = st.selectbox(
                                "Select Resource Type",
                                available_types,
                                format_func=lambda x: f"{x.replace('_', ' ').title()} ({len(resources.get(x, []))})",
                                key="type_selector",
                            )

                            if selected_type:
                                items = resources.get(selected_type, [])

                                st.markdown(f"#### {selected_type.replace('_', ' ').title()}")
                                st.caption(f"{len(items)} resources")

                                # Build dataframe
                                table_data = []
                                for item in items:
                                    row = {
                                        "ID": item.get("id", "N/A"),
                                        "Name": item.get("name", "N/A"),
                                        "Description": (item.get("description", "")[:80] + "...")
                                        if len(item.get("description", "")) > 80
                                        else item.get("description", ""),
                                        "Modified": item.get("modified", "N/A")[:19],
                                    }
                                    table_data.append(row)

                                if table_data:
                                    df = pd.DataFrame(table_data)
                                    st.dataframe(df, use_container_width=True, hide_index=True)


# ==================== TAB 4: SIZING CALCULATOR ====================
with tab4:
    st.markdown("### 📏 AAP Capacity Sizing Calculator")
    st.caption("Calculate infrastructure requirements for AAP 2.6 based on AAP 2.4 metrics")
    st.markdown("---")

    # Initialize calculator
    calculator = AAP26SizingCalculator()

    # Input form
    st.markdown("### 📝 Current AAP 2.4 Metrics")

    # Controller metrics
    st.markdown("#### Control Plane")
    col1, col2 = st.columns(2)

    with col1:
        num_controllers = st.number_input(
            "Number of Controllers",
            min_value=1,
            value=3,
            step=1,
            help="Current number of controller nodes in AAP 2.4",
        )

        controller_cpu_avg = st.slider(
            "Controller CPU Usage - Average (%)",
            min_value=0,
            max_value=100,
            value=35,
            help="Average CPU utilization across controllers",
        )

        controller_cpu_peak = st.slider(
            "Controller CPU Usage - Peak (%)",
            min_value=0,
            max_value=100,
            value=50,
            help="Peak CPU utilization during busy periods",
        )

    with col2:
        controller_memory = st.slider(
            "Controller Memory Usage (%)",
            min_value=0,
            max_value=100,
            value=20,
            help="Memory utilization on controller nodes",
        )

        num_hub_nodes = st.number_input(
            "Number of Hub Nodes", min_value=0, value=2, step=1, help="Automation Hub nodes"
        )

        hub_cpu = st.slider(
            "Hub CPU Usage (%)", min_value=0, max_value=100, value=25, help="Hub CPU utilization"
        )

    # Execution plane metrics
    st.markdown("---")
    st.markdown("#### Execution Plane")

    col1, col2 = st.columns(2)

    with col1:
        num_execution = st.number_input(
            "Number of Execution Nodes",
            min_value=1,
            value=10,
            step=1,
            help="Current execution nodes",
        )

        execution_cpu = st.slider(
            "Execution Node CPU Usage (%)",
            min_value=0,
            max_value=100,
            value=70,
            help="Average CPU on execution nodes",
        )

    with col2:
        execution_memory = st.slider(
            "Execution Node Memory Usage (%)",
            min_value=0,
            max_value=100,
            value=50,
            help="Memory utilization on execution nodes",
        )

        forks_observed = st.number_input(
            "Observed Forks", min_value=1, value=5, help="Typical fork count in jobs"
        )

    # Database metrics
    st.markdown("---")
    st.markdown("#### Database")

    col1, col2 = st.columns(2)

    with col1:
        db_vcpu = st.number_input(
            "Database vCPU", min_value=1, value=8, step=1, help="Database vCPU allocation"
        )

        db_memory_gb = st.number_input(
            "Database Memory (GB)", min_value=1, value=64, step=8, help="Database RAM in GB"
        )

        db_cpu_percent = st.slider(
            "Database CPU Usage (%)",
            min_value=0,
            max_value=100,
            value=60,
            help="Database CPU utilization",
        )

    with col2:
        db_memory_percent = st.slider(
            "Database Memory Usage (%)",
            min_value=0,
            max_value=100,
            value=35,
            help="Database memory utilization",
        )

        db_requests_peak = st.number_input(
            "Concurrent DB Requests (Peak)",
            min_value=1,
            value=300,
            help="Peak concurrent database connections",
        )

        db_growth_gb = st.number_input(
            "DB Growth Per Day (GB)", min_value=0, value=50, help="Daily database growth"
        )

    # Workload metrics
    st.markdown("---")
    st.markdown("#### Workload Characteristics")

    col1, col2 = st.columns(2)

    with col1:
        playbooks_per_day = st.number_input(
            "Playbooks Per Day (Peak)",
            min_value=1,
            value=10000,
            step=1000,
            help="Peak daily job executions",
        )

        concurrent_jobs = st.number_input(
            "Concurrent Jobs (Peak)",
            min_value=1,
            value=100,
            step=10,
            help="Maximum concurrent jobs",
        )

        concurrent_pending = st.number_input(
            "Concurrent Jobs Pending", min_value=0, value=20, help="Jobs waiting in queue"
        )

    with col2:
        managed_hosts = st.number_input(
            "Managed Hosts",
            min_value=1,
            value=5000,
            step=100,
            help="Total hosts under management",
        )

        tasks_per_job = st.number_input(
            "Tasks Per Job (Avg)", min_value=1, value=50, help="Average tasks per playbook"
        )

        job_duration_hours = st.number_input(
            "Job Duration (Hours)",
            min_value=0.1,
            max_value=24.0,
            value=0.25,
            step=0.25,
            help="Average job execution time",
        )

    # Advanced settings
    with st.expander("⚙️ Advanced Settings"):
        col1, col2 = st.columns(2)

        with col1:
            retention_hours = st.number_input(
                "Job Retention (Hours)", min_value=1, value=48, help="How long to keep job history"
            )

            allowed_hours = st.number_input(
                "Allowed Hours Per Day",
                min_value=1,
                max_value=24,
                value=24,
                help="Hours available for job execution",
            )

            verbosity = st.selectbox(
                "Verbosity Level",
                options=[0, 1, 2, 3, 4],
                index=1,
                format_func=lambda x: {
                    0: "Minimal (0)",
                    1: "Normal (1) - Recommended",
                    2: "Verbose (2)",
                    3: "Debug (3)",
                    4: "Connection Debug (4)",
                }[x],
                help="Ansible verbosity level affects event processing load",
            )

        with col2:
            peak_pattern = st.selectbox(
                "Peak Concurrency Pattern",
                options=["distributed_24x7", "business_hours", "batch_window", "mixed"],
                index=0,
                format_func=lambda x: {
                    "distributed_24x7": "Distributed 24/7 (1.0x)",
                    "business_hours": "Business Hours (2.5x)",
                    "batch_window": "Batch Window (10.0x)",
                    "mixed": "Mixed Pattern (1.5x)",
                }[x],
                help="How jobs are distributed throughout the day",
            )

            hub_memory = st.slider(
                "Hub Memory Usage (%)", min_value=0, max_value=100, value=30, help="Hub memory %"
            )

    # Calculate sizing
    st.markdown("---")

    if st.button("🔬 Calculate AAP 2.6 Sizing", type="primary", use_container_width=True):
        with st.spinner("Calculating infrastructure requirements..."):
            try:
                # Prepare metrics dictionary
                metrics = {
                    "num_controllers": num_controllers,
                    "controller_cpu_percent_avg": controller_cpu_avg,
                    "controller_cpu_percent_peak": controller_cpu_peak,
                    "controller_memory_percent": controller_memory,
                    "num_hub_nodes": num_hub_nodes,
                    "hub_cpu_percent": hub_cpu,
                    "hub_memory_percent": hub_memory,
                    "num_execution_nodes": num_execution,
                    "execution_cpu_percent": execution_cpu,
                    "execution_memory_percent": execution_memory,
                    "forks_observed": forks_observed,
                    "database_vcpu": db_vcpu,
                    "database_memory_gb": db_memory_gb,
                    "database_cpu_percent": db_cpu_percent,
                    "database_memory_percent": db_memory_percent,
                    "concurrent_db_requests_peak": db_requests_peak,
                    "db_growth_per_day_gb": db_growth_gb,
                    "playbooks_per_day_peak": playbooks_per_day,
                    "concurrent_jobs_peak": concurrent_jobs,
                    "concurrent_jobs_pending": concurrent_pending,
                    "job_retention_hours": retention_hours,
                    "managed_hosts": managed_hosts,
                    "tasks_per_job": tasks_per_job,
                    "job_duration_hours": job_duration_hours,
                    "allowed_hours_per_day": allowed_hours,
                    "verbosity_level": verbosity,
                    "peak_pattern": peak_pattern,
                }

                # Calculate sizing
                results = calculator.generate_sizing_recommendation(metrics)

                st.success("✅ Sizing calculation complete!")

                # Display warnings if any
                if results.get("warnings"):
                    st.warning("⚠️ **Warnings:**")
                    for warning in results["warnings"]:
                        st.warning(f"- {warning}")

                # Display results
                st.markdown("### 🖥️ AAP 2.6 Infrastructure Requirements")

                components = results.get("components", {})

                # Gateway
                st.markdown("#### Gateway (API/UI)")
                gateway = components.get("platform_gateway", {})

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Pods", gateway.get("gateway_pods", "N/A"))
                with col2:
                    st.metric("CPU per Pod", f"{gateway.get('cpu_per_pod', 'N/A')}")
                with col3:
                    st.metric("Memory per Pod (GB)", f"{gateway.get('memory_per_pod_gb', 'N/A')}")
                with col4:
                    st.metric("Total CPU", f"{gateway.get('total_cpu', 'N/A')}")

                if gateway.get("note"):
                    st.caption(f"ℹ️ {gateway['note']}")

                st.markdown("---")

                # Controller (Event Processing)
                st.markdown("#### Controller (Event Processing)")
                controller = components.get("automation_controller_control_plane", {})

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Pods", controller.get("control_plane_pods", "N/A"))
                with col2:
                    st.metric("CPU per Pod", f"{controller.get('cpu_per_pod', 'N/A')}")
                with col3:
                    st.metric(
                        "Memory per Pod (GB)", f"{controller.get('memory_per_pod_gb', 'N/A')}"
                    )
                with col4:
                    st.metric("Total CPU", f"{controller.get('total_cpu', 'N/A')}")

                if controller.get("note"):
                    st.caption(f"ℹ️ {controller['note']}")

                # Show event processing details
                with st.expander("📊 Event Processing Details"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Event Forks", f"{controller.get('event_forks', 0):,.0f}")
                        st.metric("Verbosity Level", controller.get("verbosity_level", "N/A"))
                    with col2:
                        st.metric("Forks for Jobs", f"{controller.get('forks_for_jobs', 0):,.2f}")
                        st.metric("Events per Task", controller.get("events_per_task", "N/A"))

                st.markdown("---")

                # Execution Plane
                st.markdown("#### Execution Plane (Task Runner)")
                execution = components.get("automation_controller_execution_plane", {})

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Pods", execution.get("execution_pods", "N/A"))
                with col2:
                    st.metric("CPU per Pod", f"{execution.get('cpu_per_pod', 'N/A')}")
                with col3:
                    st.metric("Memory per Pod (GB)", f"{execution.get('memory_per_pod_gb', 'N/A')}")
                with col4:
                    st.metric("Total CPU", f"{execution.get('total_cpu', 'N/A')}")

                if execution.get("note"):
                    st.caption(f"ℹ️ {execution['note']}")

                # Show execution details
                with st.expander("⚙️ Execution Details"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Forks Needed", f"{execution.get('forks_needed', 0):,.2f}")
                        st.metric(
                            "Jobs per Host per Day",
                            f"{execution.get('jobs_per_host_per_day', 0):.1f}",
                        )
                    with col2:
                        st.metric("Peak Pattern", execution.get("peak_pattern", "N/A"))
                        st.metric("Peak Multiplier", f"{execution.get('peak_multiplier', 1.0)}x")

                st.markdown("---")

                # Database
                st.markdown("#### Database (PostgreSQL)")
                database = components.get("database", {})

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("CPU", f"{database.get('cpu', 'N/A')}")
                with col2:
                    st.metric("Memory (GB)", f"{database.get('memory_gb', 'N/A')}")
                with col3:
                    st.metric("Storage (GB)", f"{database.get('storage_gb', 'N/A')}")
                with col4:
                    st.metric("IOPS", f"{database.get('iops', 'N/A'):,}")

                # Show storage breakdown
                storage_breakdown = database.get("storage_breakdown", {})
                if storage_breakdown:
                    with st.expander("💾 Storage Breakdown"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Facts", f"{storage_breakdown.get('facts_mb', 0):.1f} MB")
                        with col2:
                            st.metric(
                                "Inventory", f"{storage_breakdown.get('inventory_mb', 0):.1f} MB"
                            )
                        with col3:
                            st.metric("Jobs", f"{storage_breakdown.get('jobs_mb', 0):.1f} MB")

                st.markdown("---")

                # Automation Hub
                st.markdown("#### Automation Hub")
                hub = components.get("automation_hub", {})

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Pods", hub.get("hub_pods", "N/A"))
                with col2:
                    st.metric("CPU per Pod", f"{hub.get('cpu_per_pod', 'N/A')}")
                with col3:
                    st.metric("Memory per Pod (GB)", f"{hub.get('memory_per_pod_gb', 'N/A')}")

                if hub.get("note"):
                    st.caption(f"ℹ️ {hub['note']}")

                st.markdown("---")

                # Summary
                st.markdown("### 📊 Total Requirements")

                summary = results.get("summary", {})

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(
                        "Total Pods", summary.get("estimated_pods", 0), help="All container pods"
                    )
                with col2:
                    st.metric(
                        "Total CPU", f"{summary.get('total_cpu', 0)}", help="Sum of all CPU cores"
                    )
                with col3:
                    st.metric(
                        "Total Memory (GB)",
                        f"{summary.get('total_memory_gb', 0)}",
                        help="Sum of all RAM",
                    )
                with col4:
                    st.metric(
                        "Total Storage (GB)",
                        f"{summary.get('total_storage_gb', 0)}",
                        help="Database storage",
                    )

                # Save results to session
                st.session_state.sizing_results = results

            except Exception as e:
                st.error(f"❌ Error calculating sizing: {str(e)}")
                import traceback

                with st.expander("Show error details"):
                    st.code(traceback.format_exc())

    # Export sizing results
    if st.session_state.get("sizing_results"):
        st.markdown("---")
        st.markdown("### 💾 Export Sizing")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📄 Download Results (JSON)", use_container_width=True, key="sizing_json"):
                json_str = json.dumps(st.session_state.sizing_results, indent=2, default=str)
                st.download_button(
                    "⬇️ Download", json_str, file_name="aap26_sizing.json", mime="application/json"
                )

        with col2:
            if st.button("📊 Generate Report", use_container_width=True, key="sizing_report"):
                st.info("Sizing report generation coming soon!")

    # Documentation
    st.markdown("---")
    st.markdown("### 📚 Resources")

    st.markdown(
        """
**Using Official Red Hat Formulas:**
- Based on Red Hat's AAP 2.4 to 2.6 migration sizing guide
- Includes event processing overhead calculations
- Accounts for verbosity levels and peak patterns
- Validates against recommended minimums

**Need Help?**
- [Red Hat AAP Documentation](https://access.redhat.com/documentation/en-us/red_hat_ansible_automation_platform/)
- [AAP Sizing Guide](https://access.redhat.com/articles/AAP_sizing)
"""
    )


# Footer
st.markdown("---")
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
