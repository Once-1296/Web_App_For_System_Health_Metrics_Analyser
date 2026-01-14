import streamlit as st
import extra_streamlit_components as stx
from streamlit_option_menu import option_menu
from src.Utils.chat_backend import delete_chat

def load_past_chats():
    details = []
    for chat_id, chat in st.session_state.chat_id.items():
        if len(chat["title"]) == 0:
            chat["title"] = "New Chat"
        details.append((chat_id, chat["title"]))
    
    details = details[::-1]
    default_index = next(
        i for i, (cid, _) in enumerate(details)
        if cid == st.session_state.current_chat_id
    )
    
    titles = [title for _, title in details]
    labels = []
    for i, (_, title) in enumerate(details):
        if i == 0:
            labels.append(f"➕ {title}")
        else:
            labels.append(f"{i}. {title}")
            
    selected_label = option_menu(
        None,
        labels,
        menu_icon=len(titles)*["chat-dots"],
        orientation="vertical",
        default_index=default_index,
        styles={
            "container": {
                "padding": "0!important", 
                "background-color": "transparent"
            },
            "icon": {
                "font-size": "16px"
            }, 
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "5px", # Small margin between items
                "--hover-color": "#00d4ff"
            },
            "nav-link-selected": {
                "background-color": "#00d4ff", # Added background color for clearer selection
                "color": "white"
            },
        }
    )
    selected_index = labels.index(selected_label)
    selected_chat_id = details[selected_index][0]
    # Only switch if a different chat is selected
    if st.session_state.current_chat_id != selected_chat_id:
        st.session_state.current_chat_id = selected_chat_id
        st.session_state.switch_page_from_history = True

    if st.session_state.switch_page_from_history == True:
        st.session_state.switch_page_from_history = False
        st.switch_page("src/Pages/chat_frontend.py")
    

# For deleting the chats.
def delete_chat():
    details = []
    for chat_id, chat in st.session_state.chat_id.items():
        if chat["title"]:
            details.append((chat_id, chat["title"]))

    details = details[::-1]
    remaining_chats = details[1:]

    st.write("### Manage Chats")

    # 2. Master checkbox
    delete_all = st.checkbox("Select All for Deletion", key="delete_all")

    # 3. Sync child checkboxes when master changes
    if "prev_delete_all" not in st.session_state:
        st.session_state.prev_delete_all = delete_all

    if delete_all != st.session_state.prev_delete_all:
        for cid, _ in remaining_chats:
            st.session_state[f"delete_{cid}"] = delete_all
        st.session_state.prev_delete_all = delete_all

    selected_chat_ids = []

    # 4. Render child checkboxes
    for i, (cid, title) in enumerate(remaining_chats):
        checked = st.checkbox(
            f"{i+1}. {title}",
            key=f"delete_{cid}"
        )
        if checked:
            selected_chat_ids.append(cid)

    # 5. Action button
    if selected_chat_ids:
        if st.button(f"Delete {len(selected_chat_ids)} Selected Chats", type="primary"):
            delete_chat()
            st.success(f"Deleted IDs: {selected_chat_ids}")


def render():
    chosen_id = stx.tab_bar(data=[
            stx.TabBarItemData(id=1, title="History", description="Chat History"),
            stx.TabBarItemData(id=2, title="Delete", description="Delete Chat History")
        ], default=1)
    
    with st.container(border=True):
        if chosen_id == "1":
            load_past_chats()
            
        elif chosen_id == "2":
            delete_chat()

if __name__ == "__main__":
    render()