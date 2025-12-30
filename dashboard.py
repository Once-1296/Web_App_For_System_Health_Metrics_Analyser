import streamlit as st
import pandas as pd
import numpy as np

# --- 1. Mock Data Setup (For testing independently) ---
# In your actual app, this comes from your auth system.
# We ensure st.user exists so the code runs immediately.
if not hasattr(st, 'user'):
    st.user = {
        "given_name": "Alex",
        "family_name": "Dev",
        "email": "alex.dev@university.edu",
        "role": "Student",
        "verified_email": True,
        "picture": "https://api.dicebear.com/7.x/notionists/svg?seed=Alex"
    }
    
if "theme_state" not in st.session_state:
    st.session_state.theme_state = "light"

def change_theme():
            """Toggles the theme and re-runs the script."""
            if st.session_state.theme_state == "light":
                st.session_state.theme_state = "dark"
                st._config.set_option("theme.base", "dark")
            else:
                st.session_state.theme_state = "light"
                st._config.set_option("theme.base", "light")
            st.rerun()

def get_user_dataframe():
    df = pd.DataFrame.from_dict(st.user, orient='index', columns=['User Details'])
    return df

def get_mock_activity_data():
    """Generates mock data to simulate user activity logs."""
    dates = pd.date_range(end=pd.Timestamp.now(), periods=7).strftime("%Y-%m-%d")
    activity = np.random.randint(1, 10, size=7)
    return pd.DataFrame({"Date": dates, "Login Count": activity}).set_index("Date")

def render():

    # --- Main Content Area ---
    st.title(f"Welcome {st.user["given_name"]}")
    
    # Use Tabs to organize information
    tab1, tab2, tab3 = st.tabs(["👤 Profile Info", "📊 Activity Analytics", "⚙️ Settings"])

    with tab1:
        st.subheader("Personal Information")
        
        df_profile = get_user_dataframe()
        
        selected_parameters = ['name', 'email', 'hd']
        #df_few = df_profile[selected_parameters]
        summary_data = {k: st.user[k] for k in selected_parameters if k in st.user}
    
        summary_df = pd.DataFrame.from_dict(summary_data, orient='index', columns=['Value'])
        
        name = summary_data["name"]
        email = summary_data["email"]
        try:
            hd = summary_data["hd"]
        except:
            hd = "google.com"

        st.write("Username: " + name)
        st.write("Email: " + email)
        st.write("Workspace: " + hd)
        #st.table(df_profile)
        #st.table(df_few)
        
        # Feature: Download Data
        csv = df_profile.to_csv().encode('utf-8')
        st.download_button(
            label="Download Profile Report",
            data=csv,
            file_name='user_profile.csv',
            mime='text/csv',
        )

    with tab2:
        st.subheader("Weekly Activity")
        st.write("Here is a summary of your logins this week.")
        
        chart_data = get_mock_activity_data()
        
        # Interactive Bar Chart
        st.bar_chart(chart_data)
        
        # Metrics Row
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Logins", "24", "+2")
        col2.metric("Active Projects", "3", "1 New")
        col3.metric("System Status", "Healthy")

    with tab3:
        st.subheader("Raw Data View")
        with st.expander("View Raw JSON Payload"):
            st.json(st.user)
        
        # Display the toggle button in the sidebar or main body
        # button_label = ("🌜 Switch to Dark Mode" if st.session_state.theme_state == "light" else "🌞 Switch to Light Mode")
        # st.button(button_label, on_click=change_theme)


# --- 4. Execution ---
if __name__ == "__main__":
    render()