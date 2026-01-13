import streamlit as st

def render():
    with st.container(horizontal_alignment="center"):
        st.title("Welcome Back", text_alignment="center")

        with st.container(border=True, width=400, height="content", horizontal_alignment="center", vertical_alignment="center"):
            user_name = st.text_input("Name")
            user_email = st.text_input("Email")
            user_password = st.text_input("Password", type="password")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Login", use_container_width=True):
                    if user_email and user_password:
                        st.session_state.is_logged_in = True
                        # handle_login({
                        #     "email": user_email,
                        #     "given_name": user_name
                        # })
                        st.rerun()
                    else:
                        st.error("Email and password required")

            with col2:
                if st.button("Login with Google", use_container_width=True, type="primary"):
                    st.login("google")