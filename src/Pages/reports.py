import streamlit as st
import pandas as pd
from supabase import create_client
from src.Utils.supabase_config import url, key
import plotly.express as px
import plotly.graph_objects as go
import statistics as stats
import extra_streamlit_components as stx
from streamlit_option_menu import option_menu   

st.set_page_config(
    layout="wide",
    initial_sidebar_state="auto",
)

if "report_id" not in st.session_state:
    st.session_state.report_id = -1

# -- Data Fetching and Processing Functions --
@st.dialog("User Reports", width="large")
def get_reports(email):
    sb = create_client(url, key)
    try:
        resp = (
            sb.table("user_system_reports")
            .select("id", "created_at")
            .eq("user_email", email)
            .order("created_at", desc=True)
            .execute()
        )

        if not resp.data:
            st.warning(f"No reports found for {email}.")
            return

        options = [
            f"Report {i+1}: ID {r['id']} ({r['created_at'][:10]})" 
            for i, r in enumerate(resp.data)
        ]

        selected_label = option_menu(
            menu_title="Select a Report",
            options=options,
            icons=["file-earmark-text"] * len(options),
            default_index=0,
            styles={
                "container": {"background-color": "#111"},
                "nav-link": {"font-size": "14px", "text-align": "left"},
            }
        )

        selected_index = options.index(selected_label)
        
        if st.button("Load Selected Report", width='content', type="primary"):
            # Update the persisted session state
            st.session_state.report_id = selected_index
            st.rerun()

    except Exception as e:
        st.error(f"Error fetching reports: {e}")

def fetch_report(email):
    sb = create_client(url, key)
    try:
        resp = (
            sb.table("user_system_reports")
            .select("raw_data", "summary", "created_at")
            .eq("user_email", email)
            .order("created_at", desc=True)
            .execute()
        )
        
        if not resp.data or st.session_state.report_id >= len(resp.data):
            return None, None, None, None

        record = resp.data[st.session_state.report_id]
        
        # Extraction logic
        raw_data = record.get("raw_data", {})
        data_content = raw_data.get("data", {}) if raw_data else {}
        recent_samples = data_content.get("recent_samples", [])
        aggregates = data_content.get("aggregates", [])

        summary = record.get("summary", {})
        forecast_samples = summary.get('forecast_projection') if summary else None
        peak_period = summary.get('peak_active_period') if summary else None

        return recent_samples, aggregates, forecast_samples, peak_period

    except Exception as e:
        st.error(f"Error fetching/parsing report: {e}")
        return None, None, None, None


# Graph-Making Functions
def create_line_chart(y_values, timestamps, label, color, is_aggregate=False):
    """Generates a styled line chart for samples or aggregates."""
    max_val = max(y_values) if len(y_values) > 0 else 100
    # Use 100% cap for usage metrics, otherwise dynamic cap
    y_limit = min(max_val + 10, 100) if not any(v > 100 for v in y_values) else max_val * 1.1
    
    fig = px.line(x=timestamps, y=y_values, labels={'x': 'Time', 'y': label})
    
    # Styling
    line_shape = 'spline' if is_aggregate else 'linear' # Smoother lines for aggregates
    fig.update_traces(line_color=color, line_shape=line_shape, line_width=2 if not is_aggregate else 3)
    
    fig.update_layout(
        yaxis_range=[0, y_limit],
        xaxis_range=[min(timestamps), max(timestamps)],
        margin=dict(l=20, r=20, t=30, b=20),
        height=300,
        template="plotly_white",
        hovermode="x unified"
    )
    return fig


def create_disk_pie(used, free, title):
    fig = px.pie(names=["Used", "Free"], values=[used, free], title=title, color_discrete_map={"Used": "#ef553b", "Free": "#00cc96"}, hole=0.4)
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=40, b=10), height=220)
    return fig


# --- Main Rendering Logic ---
def render_charts(samples, aggregates):
    # Data Prep: Samples
    df_s = pd.DataFrame(samples)
    df_s['ts'] = pd.to_datetime(df_s['ts'])
    
    # Data Prep: Aggregates
    agg_ts = pd.to_datetime([e['window']['start'] for e in aggregates])

    # 1. CPU & Memory Section
    st.title("🖥️ System Resource Report")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("CPU Usage (Raw)")
            cpu_vals = [e['cpu']['usage'] for e in samples]
            st.plotly_chart(create_line_chart(cpu_vals, df_s['ts'], "CPU %", "#636EFA"), width='stretch', key ="3")
        with col2:
            st.subheader("Memory Usage (Raw)")
            mem_vals = [e['memory']['ram']['percent'] for e in samples]
            st.plotly_chart(create_line_chart(mem_vals, df_s['ts'], "Mem %", "#00CC96"), width='stretch', key ="4")

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Average CPU Trend")
            cpu_avg = [e['cpu']['avg'] for e in aggregates]
            st.plotly_chart(create_line_chart(cpu_avg, agg_ts, "Avg CPU %", "#EF553B", True), width='stretch', key ="5")
        with col2:
            st.subheader("Average Memory Trend")
            mem_avg = [e['memory_avg_percent'] for e in aggregates]
            st.plotly_chart(create_line_chart(mem_avg, agg_ts, "Avg Mem %", "#AB63FA", True), width='stretch', key ="6")

    # 2. Hardware Temperature Section 
    try:
        temps = [e['temps']['avg_c'] for e in aggregates if 'avg_c' in e['temps']]
        if temps and len(temps) == len(aggregates):
            with st.container(border=True):
                # First Graph
                st.subheader("🌡️ Hardware Temperature")
                # Using a custom color (Orange/Red) for temperature
                fig_temp = create_line_chart(temps, agg_ts, "Temp °C", "#FF4B4B", True)
                # Update Y-axis specifically for Celsius logic
                fig_temp.update_layout(yaxis_range=[min(temps)-5, max(temps)+5]) 
                st.plotly_chart(fig_temp, width='stretch', key ="7")
                
                st.divider()
                
                # Second Graph
                sensor_d = {k: [stats.mean([x['current'] for x in d[k]]) for d in (e['temps']['sensors'] for e in samples) if k in d] for k in {k for e in samples for k in e['temps']['sensors']}}
                fig = go.Figure()
                # Loop through the dynamic dictionary
                for sensor_name, values in sensor_d.items():
                    fig.add_trace(go.Scatter(
                        y=values,
                        mode='lines',
                        name=sensor_name
                    ))

                fig.update_layout(
                    margin=dict(l=20, r=20, t=40, b=20),
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, width='stretch', key ="8")
            
    except Exception:
        pass

    # 3. Disk Snapshots & Aggregates
    with st.container(border=True):
        st.subheader("💾 Storage Analysis")
        c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
        
        disk_used = [e['disk']['used_gb'] for e in samples]
        disk_total = [e['disk']['total_gb'] for e in samples]
        disk_free = [t-u for t, u in zip(disk_total, disk_used)]

        with c1: st.plotly_chart(create_disk_pie(disk_used[0], disk_free[0], "Start"), width='stretch', key ="9")
        with c2: st.plotly_chart(create_disk_pie(disk_used[len(disk_used)//2], disk_free[len(disk_used)//2], "Mid"), width='stretch', key ="10")
        with c3: st.plotly_chart(create_disk_pie(disk_used[-1], disk_free[-1], "Latest"), width='stretch', key ="11")
        with c4:
            st.markdown("**Disk Utilization Trend**")
            disk_avg = [e['disk_avg_percent'] for e in aggregates]
            fig_disk_agg = create_line_chart(disk_avg, agg_ts, "Disk %", "#FFA15A", True)
            st.plotly_chart(fig_disk_agg, width='stretch', key ="12")

    # 4. Network Activity
    with st.container(border=True):
        st.subheader("🌐 Network Activity")
        nc1, nc2 = st.columns(2)
        
        with nc1:
            st.caption("Cumulative Throughput")
            net_df = pd.DataFrame({
                'Time': df_s['ts'],
                'Sent': [e['network']['bytes_sent'] for e in samples],
                'Received': [e['network']['bytes_recv'] for e in samples]
            }).melt(id_vars=['Time'], var_name='Traffic', value_name='Bytes')
            
            fig_net_s = px.area(net_df, x='Time', y='Bytes', color='Traffic',
                               color_discrete_map={'Sent': '#636EFA', 'Received': '#AB63FA'})
            fig_net_s.update_layout(height=350, margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_net_s, width='stretch', key ="13")

        with nc2:
            st.caption("Data Transfer Delta per Window")
            upload_delta = [e['network_delta'].get('tx_bytes', e['network_delta']['rx_bytes']) for e in aggregates]
            download_delta = [e['network_delta']['rx_bytes'] for e in aggregates]
            
            agg_net_df = pd.DataFrame({
                'Time': agg_ts,
                'Upload (MB)': [b / (1024 * 1024) for b in upload_delta], 
                'Download (MB)': [b / (1024 * 1024) for b in download_delta]
            }).melt(id_vars=['Time'], var_name='Type', value_name='MB')
            
            fig_net_a = px.bar(agg_net_df, x='Time', y='MB', color='Type', barmode='group',
                               color_discrete_map={'Upload (MB)': '#1f77b4', 'Download (MB)': '#ff7f0e'})
            
            fig_net_a.update_layout(height=350, margin=dict(l=10, r=10, t=20, b=10),
                                   legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_net_a, width='stretch', key ="14")
            
    # Optional: Aggregation Metadata
    with st.expander("Window Details"):
        durations = [e['window']['duration_sec'] for e in aggregates]
        st.markdown(f"**Report covers {len(aggregates)} aggregation windows. Average window duration: {sum(durations)/len(durations):.2f}s**")
    

def render_charts_summary(forecast_samples, peak_period):
    # Top processes in summary.
    with st.container(border=True):
        st.subheader("Top 5 Processes")
        top_processes = peak_period['top_processes'] # Table
        st.dataframe(top_processes, hide_index=True, selection_mode="multi-row")
    
    # Top Aggregates in Summary.
    top_aggregates = peak_period['top_aggregate']
    
    with st.container(border=True):
        st.subheader("Storage Report")
        mem_percent = top_aggregates['memory_avg_percent'] # pie
        disk_percent = top_aggregates['disk_avg_percent'] # pie
        col1, col2 = st.columns(2)
        
        def create_disk_pie(used, free, title):
            fig = px.pie(names=["Used", "Free"], values=[used, free], title=title,
                            color_discrete_map={"Used": "#ef553b", "Free": "#00cc96"}, hole=0.4)
            fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=40, b=10), height=220)
            return fig

        with col1: st.plotly_chart(create_disk_pie(mem_percent, 100 - mem_percent, "Memory"), width='stretch', key ="1")
        with col2: st.plotly_chart(create_disk_pie(disk_percent, 100 - disk_percent, "Disk"), width='stretch', key ="2")
        
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("CPU Stats")
            cpu_stats = top_aggregates['cpu'] # Table
            st.dataframe(cpu_stats)
        
        with col2:
            st.subheader("Network Stats")
            network_stats = top_aggregates['network_delta']
            st.dataframe(network_stats)

    if top_aggregates['temps']['available']:
        with st.container(border=True):
            st.subheader("Temperature Stats")
            temp_stats = top_aggregates['temps']['per_sensor'] # bar chart
            temp_percent = top_aggregates['temps']['avg_c']  # BOX
            st.dataframe(temp_stats)
            st.code(f"Average Temperature is {temp_percent}") 
            
    # Forecasted Samples
    df_s = pd.DataFrame(forecast_samples)
    df_s['ts'] = pd.to_datetime(df_s['ts'])
    # 1. CPU & Memory Section
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("CPU Usage (Raw)")
            cpu_vals = [e['cpu']['usage'] for e in forecast_samples]
            st.plotly_chart(create_line_chart(cpu_vals, df_s['ts'], "CPU %", "#636EFA"), width='stretch', key ="15")
        with col2:
            st.subheader("Memory Usage (Raw)")
            mem_vals = [e['memory']['ram']['percent'] for e in forecast_samples]
            st.plotly_chart(create_line_chart(mem_vals, df_s['ts'], "Mem %", "#00CC96"), width='stretch', key ="16")

    # 2. Disk Snapshots & Aggregates
    with st.container(border=True):
        st.subheader("Storage Summary")
        c1, c2, c3 = st.columns(3)
        
        disk_used = [e['disk']['used_gb'] for e in forecast_samples]
        disk_total = [e['disk']['total_gb'] for e in forecast_samples]
        disk_free = [t-u for t, u in zip(disk_total, disk_used)]  

        with c1: st.plotly_chart(create_disk_pie(disk_used[0], disk_free[0], "Start"), width='stretch', key ="18")
        with c2: st.plotly_chart(create_disk_pie(disk_used[len(disk_used)//2], disk_free[len(disk_used)//2], "Mid"), width='stretch', key ="19")
        with c3: st.plotly_chart(create_disk_pie(disk_used[-1], disk_free[-1], "Latest"), width='stretch', key ="20")
        

    # 3. Network Activity
    with st.container(border=True):
        st.subheader("Network Summary")
        st.caption("Cumulative Throughput")
        net_df = pd.DataFrame({
            'Time': df_s['ts'],
            'Sent': [e['network']['bytes_sent'] for e in forecast_samples],
            'Received': [e['network']['bytes_recv'] for e in forecast_samples]
        }).melt(id_vars=['Time'], var_name='Traffic', value_name='Bytes')
        
        fig_net_s = px.area(net_df, x='Time', y='Bytes', color='Traffic',
                            color_discrete_map={'Sent': '#636EFA', 'Received': '#AB63FA'})
        fig_net_s.update_layout(height=350, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_net_s, width='stretch', key ="21")
    

def render():
    email = "awwab.wadekar@gmail.com"
    # email = st.user.get("email", "")
    samples, aggregates, forecast_samples, peak_period = fetch_report(email)
    if samples and aggregates and forecast_samples and peak_period:
        chosen_id = stx.tab_bar(data=[
            stx.TabBarItemData(id=1, title="Raw Data", description="Reports"),
            stx.TabBarItemData(id=2, title="Summary", description="Reports Summary"),
        ], default=1)
            
        if chosen_id == "1":
            render_charts(samples, aggregates)
        if chosen_id == "2":
            render_charts_summary(forecast_samples, peak_period)
            
        with st.sidebar:
            st.caption("Select a different report:")
            if st.button("Date", type="secondary", key="date_btn", width='stretch'):
                get_reports(email)
            
    else:
        st.warning("No Data found.")    


if __name__ == "__main__":
    render()