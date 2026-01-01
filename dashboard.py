import streamlit as st
import pandas as pd
import numpy as np
from supabase import create_client, Client
# Assuming supabase_config is a local file or module you have
try:
    from supabase_config import url, key
except ImportError:
    st.error("Could not import 'url' and 'key' from 'supabase_config'. Please ensure the file exists.")
    url = ""
    key = ""

# --- SUPABASE CONNECTION ---
@st.cache_resource
def init_supabase() -> Client:
    """Initialize Supabase client with error handling."""
    try:
        return create_client(url, key)
    except Exception as e:
        st.error(f"Failed to initialize Supabase client: {e}")
        return None

# --- REPORT FETCHING FUNCTIONS ---

def get_report_options(user_email, supabase):
    """Fetches UUIDs for the user and maps them to Report N labels."""
    try:
        # Fetch IDs for the specific user
        response = supabase.table("user_system_reports")\
            .select("id")\
            .eq("user_email", user_email)\
            .execute()
        
        data = response.data
        if not data:
            return {}

        # Create dictionary mapping "Report X" -> UUID
        report_map = {}
        for index, item in enumerate(data):
            label = f"Report {index + 1}"
            report_map[label] = item['id']
            
        return report_map

    except Exception as e:
        st.error(f"Error fetching report list: {e}")
        return {}

def fetch_report_content(report_id, supabase):
    """Fetches summary and conclusions for a specific report ID."""
    try:
        response = supabase.table("user_system_reports")\
            .select("summary, conclusions")\
            .eq("id", report_id)\
            .execute()
        
        if not response.data:
            return None, "Report not found."

        record = response.data[0]
        summary = record.get('summary', '') or ""
        conclusions = record.get('conclusions', '') or ""

        # Check if both are empty
        if not summary.strip() and not conclusions.strip():
            return None, "Both Summary and Conclusions are empty for this report."

        # Format the text file content
        file_content = f"summary:\n{summary}\n\nconclusions:\n{conclusions}\n"
        return file_content, None

    except Exception as e:
        return None, f"Database error: {e}"

# --- UI COMPONENT: MODAL ---

@st.dialog("Download System Reports")
def open_download_modal(user_email):
    supabase = init_supabase()
    
    if not supabase:
        st.error("Database connection failed.")
        if st.button("Close"):
            st.rerun()
        return

    # 1. Fetch Options
    with st.spinner("Fetching available reports..."):
        report_map = get_report_options(user_email, supabase)

    if not report_map:
        st.warning("No system reports found for this user.")
        if st.button("Close"):
            st.rerun()
        return

    # 2. Select Option
    selected_label = st.selectbox("Select a Report", list(report_map.keys()))
    selected_uuid = report_map[selected_label]

    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])

    # 3. Action Buttons
    with col1:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

    with col2:
        # We use a standard button to trigger the fetch logic
        # If fetch is successful, we show the download button
        if st.button("Prepare Download", type="primary", use_container_width=True):
            content, error = fetch_report_content(selected_uuid, supabase)
            
            if error:
                st.error(error)
            else:
                # Provide the actual download button now that content is ready
                st.download_button(
                    label="⬇️ Click to Download .txt",
                    data=content,
                    file_name=f"{selected_label.replace(' ', '_')}_System_Report.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                st.success("File ready for download!")


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
        # --- MAIN BUTTON IMPLEMENTATION ---

        # Place this snippet where you want the button in your code
        if st.button("Download System Reports"):
            # Mocking user email retrieval as per instruction (st.user isn't standard, usually st.experimental_user or custom auth)
            # Replace this line with your actual auth logic
            try:
                # Example for Streamlit Community Cloud auth, or replace with your custom auth variable
                user_email = st.user.get("email")
            except:
                user_email = "test@example.com" # Fallback for testing
            
            if user_email:
                open_download_modal(user_email)
            else:
                st.error("User email not found. Please log in.")

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