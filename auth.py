import streamlit as st

def render():
    st.title("Authentication")

    if st.button("Login"):
        st.login("google")