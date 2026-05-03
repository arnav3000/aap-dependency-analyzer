"""Dependency graph visualization component."""

import streamlit as st


def render_dependency_graph(data: dict):
    """Render interactive dependency graph.

    Args:
        data: Global analysis data
    """
    try:
        import networkx as nx
        import plotly.graph_objects as go

        # Build networkx graph
        G = nx.DiGraph()

        org_reports = data.get("org_reports", {})

        # Add nodes
        for org_name, report in org_reports.items():
            resource_count = report.get("resource_count", 0)
            has_deps = report.get("has_cross_org_deps", False)

            G.add_node(org_name, size=resource_count, has_deps=has_deps)

        # Add edges (dependencies)
        for org_name, report in org_reports.items():
            deps = report.get("dependencies", {})
            for dep_org in deps:
                # Edge from dependent org to required org
                G.add_edge(org_name, dep_org, weight=len(deps[dep_org]))

        # Layout
        pos = nx.spring_layout(G, k=2, iterations=50)

        # Create edge traces
        edge_traces = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]

            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode="lines",
                line=dict(width=2, color="#888"),
                hoverinfo="none",
                showlegend=False,
            )
            edge_traces.append(edge_trace)

        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        node_color = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            node_data = G.nodes[node]
            resource_count = node_data.get("size", 0)
            has_deps = node_data.get("has_deps", False)

            # Size based on resources (with scaling)
            size = 20 + (resource_count / 10)
            node_size.append(min(size, 80))  # Cap at 80

            # Color based on dependencies
            if has_deps:
                node_color.append("#EE0000")  # Red for dependent
            else:
                node_color.append("#00AA00")  # Green for independent

            # Hover text
            in_degree = G.in_degree(node)
            out_degree = G.out_degree(node)
            hover_text = (
                f"<b>{node}</b><br>"
                f"Resources: {resource_count}<br>"
                f"Depends on: {out_degree} org(s)<br>"
                f"Required by: {in_degree} org(s)"
            )
            node_text.append(hover_text)

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            hoverinfo="text",
            text=[node for node in G.nodes()],
            hovertext=node_text,
            textposition="top center",
            marker=dict(size=node_size, color=node_color, line=dict(width=2, color="white")),
            textfont=dict(size=10),
        )

        # Create figure
        fig = go.Figure(
            data=edge_traces + [node_trace],
            layout=go.Layout(
                title=dict(text="Organization Dependency Graph", font=dict(size=16)),
                showlegend=False,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=600,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

        # Legend
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("🟢 **Independent** - No dependencies")
        with col2:
            st.markdown("🔴 **Dependent** - Has cross-org dependencies")

        # Graph stats
        with st.expander("📊 Graph Statistics"):
            st.markdown(f"**Nodes:** {G.number_of_nodes()}")
            st.markdown(f"**Edges:** {G.number_of_edges()}")

            # Find most connected
            if G.number_of_nodes() > 0:
                in_degrees = dict(G.in_degree())
                out_degrees = dict(G.out_degree())

                most_required = max(in_degrees.items(), key=lambda x: x[1])
                most_dependent = max(out_degrees.items(), key=lambda x: x[1])

                st.markdown(
                    f"**Most Required:** {most_required[0]} ({most_required[1]} dependents)"
                )
                st.markdown(
                    f"**Most Dependencies:** {most_dependent[0]} ({most_dependent[1]} dependencies)"
                )

    except ImportError:
        st.error("Missing dependencies for graph visualization")
        st.info("Install required packages: pip install plotly networkx")

        # Fallback to text representation
        st.markdown("**Dependency List:**")
        for org_name, report in data.get("org_reports", {}).items():
            deps = report.get("dependencies", {})
            if deps:
                st.markdown(f"- **{org_name}** depends on: {', '.join(deps.keys())}")
