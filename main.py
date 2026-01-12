import streamlit as st
# from streamlit_option_menu import option_menu
import auth
# import chat_frontend as chat
# import chat_history as history
from chat_backend import load_past_chats
import loc_app_doc

# auth checkup
if not st.user.is_logged_in:
    auth.render()
    st.stop()



# Load past chats if new session
if not "current_chat_id" in st.session_state:
    load_past_chats(st.user.get("email", ""))
# print(st.session_state.current_chat_id)

# Here will be a new navigation sidebar 
#     1. Dashboard, 
#     2. Chat, 
#     3. History
#     4. Logout


# Show user logo at the start
# st.sidebar.image("https://example.com/logo.png", width=100)
picture = st.user.get("picture", None)
if picture:
    st.logo(picture)



# with st.sidebar:
#     col1, col2 = st.columns([1, 3], gap="small")
    
#     with col1:
#         if "picture" in st.user:
#             st.image(st.user["picture"], width=50)
#         else:
#             st.write("👤")
            
#     with col2:
#         user_name = st.user.get("given_name", "User")
#         user_email = st.user.get("email", "")
        
#         # Using HTML allows precise control over line-height (spacing between lines)
#         st.markdown(f"""
#             <div style="margin-top: 5px;">
#                 <h3 style="margin: 0; font-size: 18px;">{user_name}</h3>
#                 <p style="margin: 0; font-size: 12px; color: grey;">{user_email}</p>
#             </div>
#         """, unsafe_allow_html=True)

#     # Use markdown '---' to trigger your custom CSS <hr> style
#     st.markdown("---")

    # --- 3. Menu ---
#     selected = option_menu(
#         None,
#         ["Dashboard", "Chat", "History","Local App Guide"],
#         icons=["speedometer2", "chat-dots", "clock-history","download"], # Removed extra icon to match list length
#         orientation="vertical",
#         default_index=0,
#         styles={
#             "container": {
#                 "padding": "0!important", 
#                 "background-color": "transparent"
#             },
#             "icon": {
#                 "font-size": "16px" # Slightly smaller to match compact look
#             }, 
#             "nav-link": {
#                 "font-size": "15px",
#                 "text-align": "left",
#                 "margin": "5px", # Small margin between items
#                 "--hover-color": "#e66c38"
#             },
#             "nav-link-selected": {
#                 "background-color": "#e66c38", # Added background color for clearer selection
#                 "color": "white"
#             },
#         }
#     )
#     st.divider()
#     # Logout Button (Visual only, logic depends on your auth provider)
#     if 'confirm_logout' not in st.session_state:
#         st.session_state.confirm_logout = False

#     # 2. The Main Logout Button
#     if st.button("Logout", use_container_width=True):
#         st.session_state.confirm_logout = True

#     # 3. If they clicked logout, show the confirmation UI
#     if st.session_state.confirm_logout:
#         st.warning("Are you sure you want to logout?")
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             if st.button("Yes", use_container_width=True):
#                 st.session_state.confirm_logout = False # Reset state
#                 st.success("Logging out...")
#                 st.logout() # Note: st.logout is usually for Streamlit Auth
#                 st.rerun()
                
#         with col2:
#             if st.button("No", use_container_width=True):
#                 st.session_state.confirm_logout = False
#                 st.rerun() # Refresh to hide the warning

# # Page Routing
# if selected == "Dashboard":
#     # Ensure dashboard module is imported
#     # import dashboard 
#     dashboard.render()

# elif selected == "Chat":
#     # Ensure chat2 module is imported
#     # import chat2
#     chat.render()

# elif selected == "History":
#     # Show past chats
#     history.render()

# elif selected == "Local App Guide":
#     loc_app_doc.render()


dashboard_page = st.Page(
    "dashboard.py",
    title="Dashboard",
    icon=":material/dashboard:",
    default=True,
)

chat_page = st.Page(
    "chat_frontend.py",
    title="Chat",
    icon=":material/chat:",
)

history_page = st.Page(
    "chat_history.py",
    title="History",
    icon=":material/history:",
)

loc_app_doc_page = st.Page(
    "loc_app_doc.py",
    title="Local App Guide",
    icon=":material/download:",
)

pg = st.navigation([dashboard_page, chat_page, history_page, loc_app_doc_page])

pg.run()
