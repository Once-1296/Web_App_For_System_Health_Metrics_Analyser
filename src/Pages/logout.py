import streamlit as st

st.set_page_config(
    layout="centered",
    initial_sidebar_state="auto",
)

@st.dialog("Logout")
def render():
    st.warning("Are you sure you want to logout?")
    col1, col2 = st.columns(2, gap="small")
    with col1:
        if st.button("Yes", width='stretch'):
            st.logout()
    with col2:
        if st.button("Cancel", width='stretch'):
            st.session_state.confirm_logout = False
            st.switch_page("src/Pages/dashboard.py")
                    
if __name__ == "__main__":
    render()