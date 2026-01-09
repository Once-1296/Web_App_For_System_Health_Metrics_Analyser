import streamlit as st

def render():
    with st.container(horizontal_alignment="center"):
        st.title("Welcome Back", text_alignment="center")
        with st.container(border=True, horizontal_alignment="center", width=400):
            if st.button("Login with Google"):
                st.login("google")