from supabase import create_client
import json

SECRETS_PATH = ".streamlit/supabase_secrets.json"
try:
    with open(SECRETS_PATH, 'r') as file:
        secrets = json.load(file)
    
    # print("Data successfully loaded into a Python object (likely a dictionary or list):")
    # print(data)
    # print(f"Type of data: {type(data)}")

except FileNotFoundError:
    print("Error: The file 'data.json' was not found.")
except json.JSONDecodeError:
    print("Error: Could not decode JSON from the file. Check for invalid JSON syntax.")

url = secrets["PROJECT_URL"]
key = secrets["service_role_key"]

sb = create_client(url, key)
email = "awwab.wadekar@gmail.com"
resp = (
    sb.table("user_chat_nums").select("chat_id").eq("email",email).execute()
)
# st.session_state.setdefault("chat_id",{})
try:
    chat_ids = [entry["chat_id"] for entry in resp.data]
except Exception as e:
    chat_ids = []
for chat_id in chat_ids:
    chat_resp = (sb.table("all_chats").select("*").eq("email",email).eq("chat_id",chat_id).execute())
    data,count = chat_resp.data,chat_resp.count
    # st.session_state.chat_id.update({
    #     chat_id : 
    # })
    print(data)
    print(type(data[0]))
    