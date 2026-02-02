import streamlit as st

st.set_page_config(
    layout="centered",
    initial_sidebar_state="auto",
)

def render():
    with st.container(horizontal_alignment="center"):
        st.title("Welcome Back", text_alignment="center")

        with st.container(border=True, width=400, height="content", horizontal_alignment="center", vertical_alignment="center"):
            st.image("assets/imgs/robot.png", width=350)
            if st.button("Login with Google", width="stretch", type="primary"):
                st.login("google")