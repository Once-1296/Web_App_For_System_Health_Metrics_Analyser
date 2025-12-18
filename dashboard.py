import streamlit as st

def render():
    st.write(st.user)

    if st.button("🚪 Logout"):
        st.logout()

