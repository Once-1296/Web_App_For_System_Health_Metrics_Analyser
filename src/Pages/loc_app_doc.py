import streamlit as st
from typing import List, Optional
import extra_streamlit_components as stx

class Section:
    """Represents a documentation section with empty Streamlit containers."""

    def __init__(self, id: str, title: str = ""):
        self.id = id
        self.title = title
        # Container placeholders to be populated by the caller
        self.header = None
        self.body = None
        self.media = None

    def set_containers(self, header, body, media):
        """Attaches actual Streamlit containers to this section object."""
        self.header = header
        self.body = body
        self.media = media


def _build_default_sections() -> List[Section]:
    """Returns the four specific sections requested."""
    ids_and_titles = [
        ("overview", "Overview"),
        ("usage", "How to use"),
        ("faq", "FAQ"),
        ("references", "References"),
    ]
    return [Section(id=i, title=t) for i, t in ids_and_titles]


def render_documentation(sections: Optional[List[Section]] = None) -> Section:
    """
    Renders the sidebar navigation and prepares the layout columns.
    Returns the currently active Section object.
    """
    if sections is None:
        sections = _build_default_sections()

    if "active_section_index" not in st.session_state:
        st.session_state.active_section_index = 0

    # Sidebar Navigation
    st.sidebar.title("Documentation")
    
    for i, section in enumerate(sections):
        if st.sidebar.button(section.title, key=f"nav_{section.id}", use_container_width=True):
            st.session_state.active_section_index = i

    # Find the selected Section object
    active_section = sections[st.session_state.active_section_index]

    # UI Layout: Header (Top), then Body and Media (Side-by-Side)
    # This layout is cleaner for documentation than three narrow columns
    header_area = st.container()
    col_body, col_media = st.columns([3, 2], gap="large")

    # Assign containers to the active section
    active_section.set_containers(
        header=header_area,
        body=col_body,
        media=col_media
    )

    return active_section


def render():
    """Execution entry point."""
    # 1. Setup page config
    st.set_page_config(page_title="App Documentation", layout="wide")

    # 2. Render the scaffold and get the active section
    active = render_documentation()

    # 3. Example of how to populate the content (Clean Implementation)
    if active.id == "overview":
        active.header.title("Project Overview")
        active.body.markdown("""
        The application is a comprehensive System Performance Monitor built with Python, designed to provide deep technical insights into hardware health and resource allocation. By utilizing the Psutil library, the app retrieves high-fidelity data from the CPU, memory, disks, and network interfaces. This data is then rendered through a professional-grade interface powered by PyQt, featuring dynamic tables and real-time updating graphs that visualize system fluctuations as they happen.

        To ensure security and data integrity, the application currently employs Google OAuth 2.0 as the primary authorization method. While the dashboard provides immediate visual feedback through its live graphing system, the core analytical engine requires a 25-minute data collection window. This duration allows the application to aggregate enough telemetry to generate a statistically significant performance report, moving beyond simple real-time viewing to provide actionable, long-term system diagnostics.

        ---
        **Quick Links:**
        * 📥 [Releases page to install app](https://github.com/MohdHedayati/Local-app---system-health-metric-analyzer/releases/tag/v2.0)
        * 📺 [View Demo Video Here](https://drive.google.com/file/d/1VBxCqLG-cHM9lLjSFF6cGrrf4kFEBD8W/view?usp=sharing)
        * 📄 [In Depth Docs](https://mohdhedayati.github.io/System-Health-Metric-Analyser/)
        """)

    elif active.id == "usage":
        active.header.title("How to Use")
        active.body.markdown("Step 1: Launch the exe, Open the application via your terminal or desktop shortcut.")
        active.body.markdown("\nStep 2: Monitor the system, View live CPU, RAM, and Disk usage in the primary dashboard.")
        active.body.markdown("\nStep 3: After 25 minutes Click on the 'Generate Report' button to receive an AI-powered analysis of your current system state.")
        # active.media.image("path/to/tutorial.png")

    elif active.id == "faq":
        active.header.title("Frequently Asked Questions")
        with active.body:
            st.expander("How do I update the data?").write("Update via the settings tab.")
            st.expander("Is this app secure?").write("Yes, it uses end-to-end encryption.")
            st.expander("Why is the temporary directory functionality unavailable on Windows?").write("Current architectural constraints within the Windows environment limit certain filesystem operations. We are evaluating future updates to address these compatibility issues.")

        st.expander("What is the reason for the 25-minute observation period?").write("To provide an accurate and meaningful report, the application requires a sufficient window of data. This duration ensures that the system can collect a diverse set of metrics to identify patterns rather than just momentary spikes.")

        st.expander("Why does the file upload process take several minutes?").write("This delay is primarily due to the initialization requirements of the ONNX Runtime on Windows systems. Please allow 2-3 minutes for the environment to stabilize and complete the upload successfully.")

        st.expander("Are there any external dependencies to download?").write("No. The application is designed to be self-contained. All necessary libraries and runtimes are included in the standard installation package.")

        st.expander("Is a Google Account mandatory for use?").write("Yes. To maintain the integrity of the diagnostic reports and ensure they are attributed to verified users, a Google Account is required for authentication.")

        st.expander("What was the inspiration behind this tool?").write("The project was heavily inspired by the efficiency and aesthetic of Btop and Htop, the renowned resource monitors for Linux-based systems.")

        st.expander("Is my data stored permanently on the cloud?").write("Metrics are processed to generate your report; however, we prioritize user privacy. System logs are used solely for the generation of the requested analysis.")

    elif active.id == "references":
        active.header.title("References & Resources")
        active.body.markdown("- [Streamlit Docs](https://docs.streamlit.io)")
        active.body.markdown("- [Python Wiki](https://wiki.python.org)")
        active.body.markdown("- [PyQt6 Docs](https://www.riverbankcomputing.com/static/docs/pyqt6/)")
        active.body.markdown("- [Psutil Docs](https://psutil.readthedocs.io/en/latest/)")
        active.body.markdown("- [ONNX Runtime Docs](https://onnxruntime.ai/docs/)")
        active.body.markdown("- [PyTorch Documentation](https://docs.pytorch.org/docs/stable/index.html)")
        active.body.markdown("- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)")

if __name__ == "__main__":
    render()
