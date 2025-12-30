import streamlit as st
from streamlit_option_menu import option_menu
import auth
import dashboard
import chat2

# auth checkup
if not st.user.is_logged_in:
    auth.render()
    st.stop()

# Here will be a new navigation sidebar 
#     1. Dashboard, 
#     2. Chat, 
#     3. History
#     4. Logout
# 
with st.sidebar:
    col1, col2 = st.columns([1, 3], gap="small")
    
    with col1:
        if "picture" in st.user:
            st.image(st.user["picture"], width=50)
        else:
            st.write("👤")
            
    with col2:
        user_name = st.user.get("given_name", "User")
        user_email = st.user.get("email", "")
        
        # Using HTML allows precise control over line-height (spacing between lines)
        st.markdown(f"""
            <div style="margin-top: 5px;">
                <h3 style="margin: 0; font-size: 18px;">{user_name}</h3>
                <p style="margin: 0; font-size: 12px; color: grey;">{user_email}</p>
            </div>
        """, unsafe_allow_html=True)

    # Use markdown '---' to trigger your custom CSS <hr> style
    st.markdown("---")

    # --- 3. Menu ---
    selected = option_menu(
        None,
        ["Dashboard", "Chat", "History"],
        icons=["speedometer2", "chat-dots", "clock-history"], # Removed extra icon to match list length
        orientation="vertical",
        default_index=0,
        styles={
            "container": {
                "padding": "0!important", 
                "background-color": "transparent"
            },
            "icon": {
                "font-size": "16px" # Slightly smaller to match compact look
            }, 
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "5px", # Small margin between items
                "--hover-color": "#e66c38"
            },
            "nav-link-selected": {
                "background-color": "#e66c38", # Added background color for clearer selection
                "color": "white"
            },
        }
    )

# Page Routing
if selected == "Dashboard":
    # Ensure dashboard module is imported
    # import dashboard 
    dashboard.render()

elif selected == "Chat":
    # Ensure chat2 module is imported
    # import chat2
    chat2.render()
