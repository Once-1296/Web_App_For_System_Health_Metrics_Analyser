import streamlit as st
from typing import Dict, List, Optional


"""Local app documentation scaffold.

This module provides a lightweight, extensible structure for hosting
local documentation pages inside Streamlit. It intentionally does not
include any textual content or images; instead it exposes functions and
container placeholders so you can add text, images and code later.

Usage (example):
  from loc_app_doc import render_documentation, Section

  sections = [
      Section(id="intro", title="Introduction"),
      Section(id="arch", title="Architecture"),
  ]

  render_documentation(sections)

All rendering is performed inside Streamlit containers so you can later
call section.body.markdown("...") or section.image.image("path") to
inject content.
"""


class Section:
    """Represents a documentation section with empty Streamlit containers.

    After calling `render_documentation`, each Section will have the
    following attributes populated with Streamlit container objects:
      - header: container for the section header (left empty by default)
      - body: container for markdown or rich text
      - media: a placeholder (st.empty) where images, diagrams or widgets
               can be rendered later

    The Section object itself does not emit any text until you call write
    methods on those containers.
    """

    def __init__(self, id: str, title: str = ""):
        self.id = id
        self.title = title
        # These will be set by the renderer
        self.header = None
        self.body = None
        self.media = None

    def set_containers(self, header, body, media):
        self.header = header
        self.body = body
        self.media = media


def _build_default_sections() -> List[Section]:
    """Return a sensible default list of sections for app documentation.

    These are empty placeholders (no text). You can replace or extend
    this list when calling `render_documentation`.
    """

    ids_and_titles = [
        ("overview", "Overview"),
        ("architecture", "Architecture"),
        ("data_flow", "Data flow"),
        ("components", "Components"),
        ("deployment", "Deployment"),
        ("usage", "How to use"),
        ("faq", "FAQ"),
        ("references", "References"),
    ]
    return [Section(id=i, title=t) for i, t in ids_and_titles]


def render_documentation(sections: Optional[List[Section]] = None):
    """Render the documentation UI and attach empty containers to sections.

    - sections: list of Section objects. If None, a default set is used.

    This function will create a sidebar navigator (section titles) and
    allocate three containers per section (header, body, media). It will
    not write any text or images — those must be added later by calling
    methods on the section's containers (for example: section.body.markdown(...)).
    """

    if sections is None:
        sections = _build_default_sections()

    st.set_page_config(page_title="App Documentation", layout="wide")

    # Sidebar navigation (shows section titles). Selecting a section
    # does not populate content automatically; it only switches the view.
    titles = [s.title or s.id for s in sections]
    selected = st.sidebar.radio("Sections", titles, index=0)

    # Find selected Section object
    sel_section = next((s for s in sections if (s.title or s.id) == selected), sections[0])

    # Create three-column layout: header (left), body (middle), media (right)
    left, middle, right = st.columns([2, 6, 3])

    # Allocate containers but do not write any content into them.
    header_container = left.container()
    body_container = middle.container()
    media_placeholder = right.empty()

    # Attach containers to the Section so user can populate them later.
    sel_section.set_containers(header=header_container, body=body_container, media=media_placeholder)

    # Intentionally leave containers empty. Provide a tiny hint in the
    # Python docstring / code comments so you know where to inject content.

    # Return the active section object so the caller can fill it.
    return sel_section


def render():
    """Compatibility wrapper used when running this module directly.

    It will create the default section list and return the active Section
    object. No visible explanatory text or images are written by default.
    """

    sections = _build_default_sections()
    active = render_documentation(sections)
    # Example (commented) — when you're ready to add content, uncomment
    # and populate containers. Do not uncomment now, to keep the page empty.
    #
    # active.header.title("")
    # active.body.markdown("")
    # active.media.image("")

    return active


if __name__ == "__main__":
    render()