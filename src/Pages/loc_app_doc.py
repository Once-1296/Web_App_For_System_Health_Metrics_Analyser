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

    # Sidebar Navigation
    st.sidebar.title("Documentation")
    titles = [s.title for s in sections]
    selected_title = st.sidebar.radio("Go to:", titles)

    # Find the selected Section object
    active_section = next(s for s in sections if s.title == selected_title)

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
        Welcome to the application documentation. This section provides a 
        high-level summary of the project goals and architecture.
        """)
        active.media.info("Visual aids or summary metrics can go here.")

    elif active.id == "usage":
        active.header.title("How to Use")
        active.body.markdown("1. Step one\n2. Step two\n3. Step three")
        # active.media.image("path/to/tutorial.png")

    elif active.id == "faq":
        active.header.title("Frequently Asked Questions")
        with active.body:
            st.expander("How do I update the data?").write("Update via the settings tab.")
            st.expander("Is this app secure?").write("Yes, it uses end-to-end encryption.")

    elif active.id == "references":
        active.header.title("References & Resources")
        active.body.markdown("- [Streamlit Docs](https://docs.streamlit.io)")
        active.body.markdown("- [Python Wiki](https://wiki.python.org)")

if __name__ == "__main__":
    render()