import streamlit as st
import pandas as pd
import numpy as np
from supabase import create_client, Client
import src.Pages.logout as logout
import extra_streamlit_components as stx

st.set_page_config(
    layout="centered",
    initial_sidebar_state="auto",
)

# Assuming supabase_config is a local file or module you have
try:
    from src.Utils.supabase_config import url, key
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
            .select("conclusions")\
            .eq("id", report_id)\
            .execute()
        
        if not response.data:
            return None, "Report not found."

        record = response.data[0]
        conclusions = record.get('conclusions', '') or ""

        # Check if both are empty
        if not conclusions.strip():
            return None, "Conclusions are empty for this report."

        # Format the text file content
        file_content = f"conclusions:\n{conclusions}\n"
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
        if st.button("Cancel", width='stretch'):
            st.rerun()

    with col2:
        # We use a standard button to trigger the fetch logic
        # If fetch is successful, we show the download button
        if st.button("Prepare Download", type="primary", width='stretch'):
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
                    width='stretch'
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
    """Converts st.user dictionary into a pandas DataFrame for display."""
    dict_of_user = {}
    dict_of_user.update({
        "email": st.user["email"],
        "name": st.user["name"],
        "given_name": st.user["given_name"],
        "family_name": st.user["family_name"],
        "picture": st.user["picture"]
    })
    try:
        dict_of_user["no_of_chats"] = len(st.session_state.chat_id)
        if len(st.session_state.chat_id[len(st.session_state.chat_id)]["user_messages"])==0:
            dict_of_user["no_of_chats"]-=1
    except Exception as e:
        dict_of_user["no_of_chats"] = 0
    try:
        dict_of_user["no_of_reports"] = len(st.session_state.report_times)
    except Exception as e:
        dict_of_user["no_of_reports"] = 0
    df = pd.DataFrame.from_dict(dict_of_user, orient='index', columns=['User Details'])
    return df

def get_mock_activity_data():
    """Generates mock data to simulate user activity logs for plotting.

    Expects st.session_state.report_times to be a list/iterable of ISO timestamps like:
    "2026-01-01T11:49:59.016415+00:00"

    Returns a pandas.DataFrame indexed by dates (last 7 days) with a single column 'logins'
    suitable for st.bar_chart.
    """
    try:
        user_report_times = st.session_state.report_times
        # print(user_report_times)
    except Exception as e:
        # print(e)
        user_report_times = []

    # If no timestamps available, return a 7-day zero/ random sample so chart shows something
    if not user_report_times:
        # print("No report times found in session state.")
        # dates = pd.date_range(end=pd.Timestamp.utcnow().normalize(), periods=7)
        # counts = np.random.randint(0, 6, size=len(dates))
        # df = pd.DataFrame({"reports": counts}, index=dates)
        # df.index.name = "date"
        return {}

    try:
        # Parse timestamps robustly into UTC datetimes
        ts = pd.to_datetime(pd.Series(list(user_report_times)), utc=True, errors="coerce")
        ts = ts.dropna()
        if ts.empty:
            raise ValueError("No valid timestamps after parsing.")

        # Aggregate counts per calendar day (UTC)
        day_counts = ts.dt.date.value_counts().sort_index()

        # Convert date index back to datetime index for plotting and align to last 7 days
        day_index = pd.to_datetime(day_counts.index)
        df = pd.DataFrame({"reports": day_counts.values}, index=day_index)

        # Ensure last 7 days are present (fill missing days with 0)
        # last_7 = pd.date_range(end=pd.Timestamp.utcnow().normalize(), periods=7)
        # df = df.reindex(last_7, fill_value=0)
        # df.index.name = "date"
        # print(df)
        return df

    except Exception as e:
        st.warning(f"Could not parse activity timestamps: {e}")
        dates = pd.date_range(end=pd.Timestamp.utcnow().normalize(), periods=7)
        df = pd.DataFrame({"reports": np.zeros(len(dates), dtype=int)}, index=dates)
        df.index.name = "date"
        return df


def render():

    # --- Main Content Area ---
    st.title(f"Welcome {st.user['given_name']}! 👋")
    
    # with stx
    chosen_id = stx.tab_bar(data=[
            stx.TabBarItemData(id=1, title="Profile", description="User Profile Info"),
            stx.TabBarItemData(id=2, title="Activity", description="User Activity Analysis"),
            stx.TabBarItemData(id=3, title="Settings", description="System Settings"),
        ], default=1)

    with st.container(
        border=True
    ):
        if chosen_id == "1":
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

        if chosen_id == "2":
            st.subheader("App Activity")
            st.write("Here is a summary of your activity this week.")
            
            chart_data = get_mock_activity_data()
            
            # Interactive Bar Chart
            st.bar_chart(chart_data)
            
            # Metrics Row
            col1, col2, col3 = st.columns(3)
            try:
                num_of_chats = len(st.session_state.chat_id) 
                last_id = max(st.session_state.chat_id) if len(st.session_state.chat_id) else -1
                sign = "+1" if last_id != -1 and len(st.session_state.chat_id[num_of_chats]["user_messages"])==0 else "+0"
                # print(len(st.session_state.chat_id[num_of_chats]["user_messages"]))
                col1.metric("Total chats", num_of_chats,sign)
                num_of_reports = len(st.session_state.report_times)
                # count all reports whose time is within the last 7 days
                try:
                    rpt_times = pd.to_datetime(
                        pd.Series(list(st.session_state.report_times)),
                        utc=True,
                        errors="coerce"
                    ).dropna()
                    one_week_ago = pd.Timestamp.utcnow().tz_convert("UTC") - pd.Timedelta(days=7)
                    count_new = int((rpt_times >= one_week_ago).sum())
                except Exception as e:
                    # print(e)
                    count_new = 0
                col2.metric("Active Reports", num_of_reports, f"{count_new} Last 7 Days")

            except Exception as e:
                col1.metric("Total chats", "0", "+0")
                col2.metric("Active Reports", "0", "0 New")
            col3.metric("System Status", "Healthy")

        if chosen_id == "3":
            st.subheader("Raw Data View")
            with st.expander("View Raw JSON Payload"):
                st.json(st.user)
                
            st.subheader("Logout")
            if st.button("Logout"):
                logout.render()

            # Display the toggle button in the sidebar or main body
            # button_label = ("🌜 Switch to Dark Mode" if st.session_state.theme_state == "light" else "🌞 Switch to Light Mode")
            # st.button(button_label, on_click=change_theme)


# --- 4. Execution ---
if __name__ == "__main__":
    render()