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
