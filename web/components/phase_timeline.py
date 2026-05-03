"""Migration phase timeline visualization component."""

import streamlit as st


def render_migration_timeline(migration_phases: list, org_reports: dict):
    """Render migration phase timeline.

    Args:
        migration_phases: List of migration phases
        org_reports: Organization reports dictionary
    """
    try:
        from datetime import datetime, timedelta

        import pandas as pd
        import plotly.figure_factory as ff

        # Create Gantt chart data
        tasks = []
        start_date = datetime.now()

        for phase in migration_phases:
            phase_num = phase.get("phase")
            orgs = phase.get("orgs", [])

            # Each phase takes 1 week (adjustable)
            phase_start = start_date + timedelta(weeks=phase_num - 1)
            phase_end = phase_start + timedelta(weeks=1)

            # Add task for each org in this phase
            for org in orgs:
                org_data = org_reports.get(org, {})
                resource_count = org_data.get("resource_count", 0)

                tasks.append(
                    dict(
                        Task=org,
                        Start=phase_start,
                        Finish=phase_end,
                        Resource=f"Phase {phase_num}",
                        Description=f"{resource_count} resources",
                    )
                )

        if tasks:
            # Create figure
            fig = ff.create_gantt(
                tasks,
                colors=["#EE0000", "#00AA00", "#0066CC", "#FF9900", "#9900CC"],
                index_col="Resource",
                show_colorbar=True,
                group_tasks=True,
                showgrid_x=True,
                showgrid_y=True,
                title="Migration Timeline (Estimated)",
                height=400,
            )

            fig.update_layout(
                xaxis_title="Timeline", yaxis_title="Organizations", hovermode="closest"
            )

            st.plotly_chart(fig, use_container_width=True)

            # Timeline summary
            total_weeks = len(migration_phases)
            st.info(f"📅 Estimated timeline: {total_weeks} weeks (assuming 1 week per phase)")

        else:
            st.warning("No timeline data available")

    except ImportError:
        st.error("Missing dependencies for timeline visualization")
        st.info("Install required package: pip install plotly")

        # Fallback to simple table
        st.markdown("**Migration Timeline:**")

        import pandas as pd

        timeline_data = []
        for phase in migration_phases:
            phase_num = phase.get("phase")
            orgs = phase.get("orgs", [])

            for org in orgs:
                org_data = org_reports.get(org, {})
                timeline_data.append(
                    {
                        "Phase": phase_num,
                        "Organization": org,
                        "Resources": org_data.get("resource_count", 0),
                        "Week": f"Week {phase_num}",
                    }
                )

        df = pd.DataFrame(timeline_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
