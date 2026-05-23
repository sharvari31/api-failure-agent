import streamlit as st
import asyncio
import threading
import time
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitor.agent import run_monitoring, get_alerts, get_logs, get_stats

# Start monitoring in background thread
def start_monitoring():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_monitoring())

if "monitoring_started" not in st.session_state:
    st.session_state.monitoring_started = True
    thread = threading.Thread(target=start_monitoring, daemon=True)
    thread.start()

# Page config
st.set_page_config(
    page_title="API Failure Detection Agent",
    page_icon="🔍",
    layout="wide"
)

# Header
st.title("🔍 API Failure Detection & Debugging Agent")
st.markdown("*AI-powered real-time API monitoring with automatic anomaly detection*")
st.divider()

# Auto refresh
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 5, 30, 10)
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown("This agent monitors APIs in real-time, detects anomalies using **Isolation Forest ML**, and generates debugging recommendations using **Groq LLaMA3**.")

# Main metrics
stats = get_stats()
logs = get_logs()
alerts = get_alerts()

# Top metrics row
col1, col2, col3, col4 = st.columns(4)

total_checks = sum(s.get("total_checks", 0) for s in stats.values())
total_errors = sum(s.get("error_count", 0) for s in stats.values())
total_alerts = len(alerts)
apis_monitored = len(stats)

with col1:
    st.metric("APIs Monitored", apis_monitored)
with col2:
    st.metric("Total Checks", total_checks)
with col3:
    st.metric("Errors Detected", total_errors)
with col4:
    st.metric("Anomaly Alerts", total_alerts, delta=f"{total_alerts} total" if total_alerts > 0 else None, delta_color="inverse")

st.divider()

# API Health Status
st.subheader("📊 API Health Status")

for api_name, api_stats in stats.items():
    if not api_stats:
        continue

    avg_time = api_stats.get("avg_response_time", 0)
    errors = api_stats.get("error_count", 0)
    checks = api_stats.get("total_checks", 0)

    if avg_time < 500 and errors == 0:
        status = "🟢 Healthy"
        color = "normal"
    elif avg_time < 2000 or errors < 3:
        status = "🟡 Warning"
        color = "off"
    else:
        status = "🔴 Critical"
        color = "inverse"

    with st.expander(f"{api_name} — {status}"):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Avg Response Time", f"{avg_time}ms")
        with c2:
            st.metric("Total Checks", checks)
        with c3:
            st.metric("Errors", errors)

        # Response time chart
        api_log = logs.get(api_name, [])
        if len(api_log) > 1:
            times = [entry["response_time"] for entry in api_log]
            timestamps = [entry["timestamp"][-8:] for entry in api_log]
            anomalies = [entry["is_anomaly"] for entry in api_log]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=times,
                mode="lines+markers",
                name="Response Time",
                line=dict(color="royalblue", width=2),
                marker=dict(
                    color=["red" if a else "royalblue" for a in anomalies],
                    size=[10 if a else 6 for a in anomalies]
                )
            ))
            fig.update_layout(
                title="Response Time History (red = anomaly)",
                xaxis_title="Time",
                yaxis_title="Response Time (ms)",
                height=250,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)

st.divider()

# Alerts Section
st.subheader("🚨 AI-Generated Debugging Recommendations")

if not alerts:
    st.info("No anomalies detected yet. Monitoring is running — alerts will appear here when anomalies are found.")
else:
    for alert in reversed(alerts[-10:]):
        with st.container():
            st.error(f"**{alert['api_name']}** — {alert['timestamp'][:19]}")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Response Time", f"{alert['response_time']}ms")
            with col2:
                st.metric("Status Code", alert['status_code'])
            st.markdown(f"**🤖 AI Analysis:** {alert['explanation']}")
            st.divider()

# Auto refresh
time.sleep(refresh_rate)
st.rerun()