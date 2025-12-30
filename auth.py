import streamlit as st

def render():
    with st.container(horizontal_alignment="center"):
        st.title("Welcome Back", text_alignment="center")
        with st.container(border=True, horizontal_alignment="center", width=400):
            user_name = st.text_input("Enter your name")
            user_email = st.text_input("Enter your email")
            user_password = st.text_input("Enter your password", type="password")
            if st.button("Login with Google"):
                st.login("google")