import streamlit as st
import pandas as pd
from supabase import create_client
from src.Utils.supabase_config import url, key
import plotly.express as px
import plotly.graph_objects as go
import statistics as stats
import extra_streamlit_components as stx
from streamlit_option_menu import option_menu   
import time
import io
from fpdf import FPDF
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') # Required for server environments
from datetime import datetime
import tempfile
import os

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


# --- PDF Generation Functions ---
def create_matplotlib_line_chart(y_values, timestamps, label, color, title=""):
    """Create a matplotlib line chart for PDF export"""
    fig, ax = plt.subplots(figsize=(9, 4))
    
    # Convert timestamps to strings for plotting
    x_labels = [ts.strftime('%H:%M:%S') if hasattr(ts, 'strftime') else str(ts) for ts in timestamps]
    x_positions = range(len(y_values))
    
    ax.plot(x_positions, y_values, color=color, linewidth=2, marker='o', markersize=3)
    ax.set_ylabel(label, fontsize=10)
    ax.set_xlabel('Time', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Set x-axis labels (show fewer labels if too many points)
    step = max(1, len(x_labels) // 10)
    ax.set_xticks(x_positions[::step])
    ax.set_xticklabels(x_labels[::step], rotation=45, ha='right', fontsize=8)
    
    # Set y-axis limits
    if y_values:
        max_val = max(y_values)
        y_limit = min(max_val + 10, 100) if not any(v > 100 for v in y_values) else max_val * 1.1
        ax.set_ylim([0, y_limit])
    
    plt.tight_layout()
    return fig


def create_matplotlib_area_chart(df, x_col, y_col, color_col, title=""):
    """Create a matplotlib area chart for network data"""
    fig, ax = plt.subplots(figsize=(9, 4))
    
    # Get unique categories
    categories = df[color_col].unique()
    colors = {'Sent': '#636EFA', 'Received': '#AB63FA', 
              'Upload (MB)': '#1f77b4', 'Download (MB)': '#ff7f0e'}
    
    for category in categories:
        data = df[df[color_col] == category]
        x_vals = range(len(data))
        y_vals = data[y_col].values
        ax.fill_between(x_vals, y_vals, alpha=0.6, label=category, 
                        color=colors.get(category, '#333'))
        ax.plot(x_vals, y_vals, linewidth=1.5, color=colors.get(category, '#333'))
    
    ax.set_xlabel('Time', fontsize=10)
    ax.set_ylabel(y_col, fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    return fig


def create_matplotlib_bar_chart(df, x_col, y_col, color_col, title=""):
    """Create a matplotlib bar chart for network delta data"""
    fig, ax = plt.subplots(figsize=(9, 4))
    
    categories = df[color_col].unique()
    colors = {'Upload (MB)': '#1f77b4', 'Download (MB)': '#ff7f0e'}
    
    x_positions = df[df[color_col] == categories[0]].index.values
    width = 0.35
    
    for i, category in enumerate(categories):
        data = df[df[color_col] == category]
        offset = width * (i - len(categories)/2 + 0.5)
        ax.bar([x + offset for x in range(len(data))], data[y_col].values, 
               width=width, label=category, color=colors.get(category, '#333'))
    
    ax.set_xlabel('Time Window', fontsize=10)
    ax.set_ylabel(y_col, fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    plt.tight_layout()
    return fig


def plotly_to_image(fig, width=800, height=400):
    """Convert Plotly figure to image bytes using kaleido (browser-independent)"""
    try:
        # Method 1: Try kaleido first
        import plotly.io as pio
        img_bytes = pio.to_image(fig, format="png", width=width, height=height, engine="kaleido")
        return img_bytes
    except Exception as e1:
        try:
            # Method 2: Try without specifying engine
            import plotly.io as pio
            img_bytes = pio.to_image(fig, format="png", width=width, height=height)
            return img_bytes
        except Exception as e2:
            try:
                # Method 3: Convert to matplotlib and render
                # Extract data from plotly figure
                data = fig.data[0]
                
                fig_mpl, ax = plt.subplots(figsize=(width/100, height/100))
                
                # Handle different plot types
                if hasattr(data, 'y') and hasattr(data, 'x'):
                    # Line chart
                    x_vals = data.x if hasattr(data.x, '__iter__') else range(len(data.y))
                    y_vals = data.y
                    color = data.line.color if hasattr(data, 'line') and hasattr(data.line, 'color') else 'blue'
                    ax.plot(x_vals, y_vals, color=color, linewidth=2)
                    ax.set_xlabel(fig.layout.xaxis.title.text if fig.layout.xaxis.title else 'X')
                    ax.set_ylabel(fig.layout.yaxis.title.text if fig.layout.yaxis.title else 'Y')
                    ax.grid(True, alpha=0.3)
                    
                    # Set y-axis limits if available
                    if fig.layout.yaxis.range:
                        ax.set_ylim(fig.layout.yaxis.range)
                else:
                    ax.text(0.5, 0.5, 'Chart data unavailable', ha='center', va='center')
                
                ax.set_title(fig.layout.title.text if fig.layout.title and fig.layout.title.text else '')
                plt.tight_layout()
                
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                plt.close(fig_mpl)
                buf.seek(0)
                return buf.read()
            except Exception as e3:
                # Final fallback: create a blank placeholder
                print(f"All conversion methods failed: {e1}, {e2}, {e3}")
                fig_mpl, ax = plt.subplots(figsize=(width/100, height/100))
                ax.text(0.5, 0.5, 'Chart conversion failed', ha='center', va='center', fontsize=12)
                ax.axis('off')
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close(fig_mpl)
                buf.seek(0)
                return buf.read()


def matplotlib_to_image(fig):
    """Convert matplotlib figure to image bytes"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.read()


class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'System Resource Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 5, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(52, 152, 219)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.set_text_color(0, 0, 0)
        self.ln(3)
    
    def add_image_from_bytes(self, img_bytes, w=180, h=None):
        """Add image to PDF from bytes"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(img_bytes)
            tmp_path = tmp_file.name
        
        try:
            if h:
                self.image(tmp_path, x=10, w=w, h=h)
            else:
                self.image(tmp_path, x=10, w=w)
            self.ln(5)
        finally:
            os.unlink(tmp_path)
    
    def add_table(self, df, title=None):
        """Add a pandas dataframe as a table"""
        if title:
            self.set_font('Arial', 'B', 11)
            self.cell(0, 8, title, 0, 1)
        
        self.set_font('Arial', 'B', 9)
        col_width = 190 / len(df.columns)
        
        # Header
        for col in df.columns:
            self.cell(col_width, 7, str(col), 1, 0, 'C')
        self.ln()
        
        # Data
        self.set_font('Arial', '', 8)
        for _, row in df.iterrows():
            for item in row:
                self.cell(col_width, 6, str(item)[:25], 1, 0, 'C')
            self.ln()
        self.ln(3)


def create_pdf(samples, aggregates, forecast_samples, peak_period):
    """Generate comprehensive PDF report using matplotlib charts"""
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Prepare data
    df_s = pd.DataFrame(samples)
    df_s['ts'] = pd.to_datetime(df_s['ts'])
    agg_ts = pd.to_datetime([e['window']['start'] for e in aggregates])
    
    # =====================
    # SECTION 1: RAW DATA ANALYSIS
    # =====================
    pdf.add_page()
    pdf.chapter_title('1. CPU & Memory Usage (Raw Data)')
    
    # CPU Chart - using matplotlib
    cpu_vals = [e['cpu']['usage'] for e in samples]
    fig_cpu = create_matplotlib_line_chart(cpu_vals, df_s['ts'], "CPU %", "#636EFA", "CPU Usage Over Time")
    img_cpu = matplotlib_to_image(fig_cpu)
    pdf.add_image_from_bytes(img_cpu, w=180)
    
    # Memory Chart - using matplotlib
    mem_vals = [e['memory']['ram']['percent'] for e in samples]
    fig_mem = create_matplotlib_line_chart(mem_vals, df_s['ts'], "Memory %", "#00CC96", "Memory Usage Over Time")
    img_mem = matplotlib_to_image(fig_mem)
    pdf.add_image_from_bytes(img_mem, w=180)
    
    # CPU & Memory Trends
    pdf.add_page()
    pdf.chapter_title('2. CPU & Memory Trends (Aggregated)')
    
    cpu_avg = [e['cpu']['avg'] for e in aggregates]
    fig_cpu_avg = create_matplotlib_line_chart(cpu_avg, agg_ts, "Avg CPU %", "#EF553B", "Average CPU Trend")
    img_cpu_avg = matplotlib_to_image(fig_cpu_avg)
    pdf.add_image_from_bytes(img_cpu_avg, w=180)
    
    mem_avg = [e['memory_avg_percent'] for e in aggregates]
    fig_mem_avg = create_matplotlib_line_chart(mem_avg, agg_ts, "Avg Memory %", "#AB63FA", "Average Memory Trend")
    img_mem_avg = matplotlib_to_image(fig_mem_avg)
    pdf.add_image_from_bytes(img_mem_avg, w=180)
    
    # Temperature Section
    try:
        temps = [e['temps']['avg_c'] for e in aggregates if 'avg_c' in e['temps']]
        if temps and len(temps) == len(aggregates):
            pdf.add_page()
            pdf.chapter_title('3. Hardware Temperature')
            
            fig_temp = create_matplotlib_line_chart(temps, agg_ts, "Temperature °C", "#FF4B4B", "Hardware Temperature Over Time")
            img_temp = matplotlib_to_image(fig_temp)
            pdf.add_image_from_bytes(img_temp, w=180)
            
            # Sensor data - using matplotlib
            sensor_d = {k: [stats.mean([x['current'] for x in d[k]]) for d in (e['temps']['sensors'] for e in samples) if k in d] for k in {k for e in samples for k in e['temps']['sensors']}}
            
            fig_sensors, ax = plt.subplots(figsize=(9, 4))
            for sensor_name, values in sensor_d.items():
                ax.plot(values, label=sensor_name, linewidth=2, marker='o', markersize=3)
            ax.set_xlabel('Sample', fontsize=10)
            ax.set_ylabel('Temperature °C', fontsize=10)
            ax.set_title('Individual Sensor Temperatures', fontsize=12, fontweight='bold')
            ax.legend(loc='best', fontsize=8)
            ax.grid(True, alpha=0.3, linestyle='--')
            plt.tight_layout()
            
            img_sensors = matplotlib_to_image(fig_sensors)
            pdf.add_image_from_bytes(img_sensors, w=180)
    except Exception:
        pass
    
    # Storage Analysis
    pdf.add_page()
    pdf.chapter_title('4. Storage Analysis')
    
    disk_used = [e['disk']['used_gb'] for e in samples]
    disk_total = [e['disk']['total_gb'] for e in samples]
    disk_free = [t-u for t, u in zip(disk_total, disk_used)]
    
    # Create matplotlib pie charts for storage snapshots
    fig_storage, axes = plt.subplots(1, 3, figsize=(12, 4))
    
    positions = [0, len(disk_used)//2, -1]
    titles = ['Start', 'Mid', 'Latest']
    
    for ax, pos, title in zip(axes, positions, titles):
        ax.pie([disk_used[pos], disk_free[pos]], labels=['Used', 'Free'], 
               autopct='%1.1f%%', colors=['#ef553b', '#00cc96'], startangle=90)
        ax.set_title(title, fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    img_storage = matplotlib_to_image(fig_storage)
    pdf.add_image_from_bytes(img_storage, w=180)
    
    # Disk trend - using matplotlib
    disk_avg = [e['disk_avg_percent'] for e in aggregates]
    fig_disk_agg = create_matplotlib_line_chart(disk_avg, agg_ts, "Disk %", "#FFA15A", "Disk Utilization Trend")
    img_disk_agg = matplotlib_to_image(fig_disk_agg)
    pdf.add_image_from_bytes(img_disk_agg, w=180)
    
    # Network Activity
    pdf.add_page()
    pdf.chapter_title('5. Network Activity')
    
    # Cumulative throughput - using matplotlib
    net_df = pd.DataFrame({
        'Time': df_s['ts'],
        'Sent': [e['network']['bytes_sent'] for e in samples],
        'Received': [e['network']['bytes_recv'] for e in samples]
    }).melt(id_vars=['Time'], var_name='Traffic', value_name='Bytes')
    
    fig_net_s = create_matplotlib_area_chart(net_df, 'Time', 'Bytes', 'Traffic', 'Cumulative Network Throughput')
    img_net_s = matplotlib_to_image(fig_net_s)
    pdf.add_image_from_bytes(img_net_s, w=180)
    
    # Transfer delta - using matplotlib
    upload_delta = [e['network_delta'].get('tx_bytes', e['network_delta']['rx_bytes']) for e in aggregates]
    download_delta = [e['network_delta']['rx_bytes'] for e in aggregates]
    
    agg_net_df = pd.DataFrame({
        'Time': agg_ts,
        'Upload (MB)': [b / (1024 * 1024) for b in upload_delta], 
        'Download (MB)': [b / (1024 * 1024) for b in download_delta]
    }).melt(id_vars=['Time'], var_name='Type', value_name='MB')
    
    fig_net_a = create_matplotlib_bar_chart(agg_net_df, 'Time', 'MB', 'Type', 'Data Transfer Delta per Window')
    img_net_a = matplotlib_to_image(fig_net_a)
    pdf.add_image_from_bytes(img_net_a, w=180)
    
    # =====================
    # SECTION 2: SUMMARY & FORECAST
    # =====================
    pdf.add_page()
    pdf.chapter_title('6. System Summary & Top Processes')
    
    # Top processes
    top_processes = pd.DataFrame(peak_period['top_processes'])
    pdf.add_table(top_processes, title="Top 5 Processes During Peak Period")
    
    # Storage summary
    top_aggregates = peak_period['top_aggregate']
    mem_percent = top_aggregates['memory_avg_percent']
    disk_percent = top_aggregates['disk_avg_percent']
    
    fig_summary, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    
    # Memory pie
    ax1.pie([mem_percent, 100 - mem_percent], labels=['Used', 'Free'], 
            autopct='%1.1f%%', colors=['#ef553b', '#00cc96'], startangle=90)
    ax1.set_title('Memory Usage', fontsize=11, fontweight='bold')
    
    # Disk pie
    ax2.pie([disk_percent, 100 - disk_percent], labels=['Used', 'Free'], 
            autopct='%1.1f%%', colors=['#ef553b', '#00cc96'], startangle=90)
    ax2.set_title('Disk Usage', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    img_summary_storage = matplotlib_to_image(fig_summary)
    pdf.add_image_from_bytes(img_summary_storage, w=180)
    
    # CPU and Network stats
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'CPU Statistics', 0, 1)
    cpu_stats = pd.DataFrame([top_aggregates['cpu']])
    pdf.add_table(cpu_stats)
    
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'Network Statistics', 0, 1)
    network_stats = pd.DataFrame([top_aggregates['network_delta']])
    pdf.add_table(network_stats)
    
    # Temperature stats (if available)
    if top_aggregates['temps']['available']:
        pdf.add_page()
        pdf.chapter_title('7. Temperature Statistics')
        temp_stats = pd.DataFrame(top_aggregates['temps']['per_sensor'])
        pdf.add_table(temp_stats)
        
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, f"Average Temperature: {top_aggregates['temps']['avg_c']}°C", 0, 1)
    
    # Forecast Section
    pdf.add_page()
    pdf.chapter_title('8. Forecast Projection')
    
    df_forecast = pd.DataFrame(forecast_samples)
    df_forecast['ts'] = pd.to_datetime(df_forecast['ts'])
    
    # CPU forecast - using matplotlib
    cpu_forecast_vals = [e['cpu']['usage'] for e in forecast_samples]
    fig_cpu_forecast = create_matplotlib_line_chart(cpu_forecast_vals, df_forecast['ts'], "CPU %", "#636EFA", "CPU Usage Forecast")
    img_cpu_forecast = matplotlib_to_image(fig_cpu_forecast)
    pdf.add_image_from_bytes(img_cpu_forecast, w=180)
    
    # Memory forecast - using matplotlib
    mem_forecast_vals = [e['memory']['ram']['percent'] for e in forecast_samples]
    fig_mem_forecast = create_matplotlib_line_chart(mem_forecast_vals, df_forecast['ts'], "Memory %", "#00CC96", "Memory Usage Forecast")
    img_mem_forecast = matplotlib_to_image(fig_mem_forecast)
    pdf.add_image_from_bytes(img_mem_forecast, w=180)
    
    # Storage forecast
    pdf.add_page()
    pdf.chapter_title('9. Forecast Storage Analysis')
    
    disk_used_f = [e['disk']['used_gb'] for e in forecast_samples]
    disk_total_f = [e['disk']['total_gb'] for e in forecast_samples]
    disk_free_f = [t-u for t, u in zip(disk_total_f, disk_used_f)]
    
    fig_storage_f, axes_f = plt.subplots(1, 3, figsize=(12, 4))
    positions_f = [0, len(disk_used_f)//2, -1]
    
    for ax, pos, title in zip(axes_f, positions_f, titles):
        ax.pie([disk_used_f[pos], disk_free_f[pos]], labels=['Used', 'Free'], 
               autopct='%1.1f%%', colors=['#ef553b', '#00cc96'], startangle=90)
        ax.set_title(f"Forecast {title}", fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    img_storage_f = matplotlib_to_image(fig_storage_f)
    pdf.add_image_from_bytes(img_storage_f, w=180)
    
    # Network forecast - using matplotlib
    net_forecast_df = pd.DataFrame({
        'Time': df_forecast['ts'],
        'Sent': [e['network']['bytes_sent'] for e in forecast_samples],
        'Received': [e['network']['bytes_recv'] for e in forecast_samples]
    }).melt(id_vars=['Time'], var_name='Traffic', value_name='Bytes')
    
    fig_net_forecast = create_matplotlib_area_chart(net_forecast_df, 'Time', 'Bytes', 'Traffic', 'Forecast Network Throughput')
    img_net_forecast = matplotlib_to_image(fig_net_forecast)
    pdf.add_image_from_bytes(img_net_forecast, w=180)
    
    # Generate PDF
    pdf_output = io.BytesIO()
    pdf_bytes = pdf.output(dest='S')
    if isinstance(pdf_bytes,str):
        pdf_bytes=pdf_bytes.encode('latin-1')
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)
    
    return pdf_output.getvalue()


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

    st.title("📊 System Forecast Report")
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
    

# --- Modified Render Function ---
def render():
    email = st.user.get("email","awwab.wadekar@gmail.com")
    samples, aggregates, forecast_samples, peak_period = fetch_report(email)
    
    if samples and aggregates and forecast_samples and peak_period:
        # --- SIDEBAR DOWNLOAD BUTTON ---
        with st.sidebar:
            st.divider()
            st.subheader("📥 Export")
            
            # Generate PDF in memory
            # We use a spinner because image conversion can take a few seconds
            if st.button("📄 Prepare PDF Report", use_container_width=True):
                with st.spinner("Generating PDF... This may take 30-60 seconds"):
                    try:
                        pdf_data = create_pdf(samples, aggregates, forecast_samples, peak_period)
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=pdf_data,
                            file_name=f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            type="primary",
                            use_container_width=True
                        )
                        st.success("✅ PDF ready for download!")
                    except Exception as e:
                        st.error(f"Error generating PDF: {e}")
                        st.info("💡 Make sure you have kaleido installed: `pip install kaleido`")
            
            st.divider()
            st.caption("📅 Select a different report:")
            if st.button("Select by Date", type="secondary", key="date_btn", use_container_width=True):
                get_reports(email)

        # --- EXISTING UI TABS ---
        chosen_id = stx.tab_bar(data=[
            stx.TabBarItemData(id=1, title="Raw Data", description="Reports"),
            stx.TabBarItemData(id=2, title="Summary", description="Reports Summary"),
        ], default=1)
            
        if chosen_id == "1":
            render_charts(samples, aggregates)
        if chosen_id == "2":
            render_charts_summary(forecast_samples, peak_period)
            
    else:
        st.image("assets/imgs/hand-drawn-no-data-concept_52683-127823.avif", width='stretch') 
        time.sleep(3)
        st.switch_page("src/Pages/dashboard.py")


if __name__ == "__main__":
    render()
