# System Health Metric Analyser - Web Dashboard

**Version 2.0**

The cloud-native command center for the System Health AI platform. This application provides data visualization and an AI-powered diagnostic interface.

## 🧠 Key Features

1.  **RAG-Based Chatbot:** A "Virtual SysAdmin" that uses Retrieval Augmented Generation (RAG) to answer technical questions based on official documentation (Windows/Linux).
2.  **Report Visualization:** Uses **Plotly** to visualize historical telemetry data stored in Supabase.

> **Technical Architecture Note:** > The Chatbot strictly acts as a **User Interface**. It does *not* analyze the raw report data itself.
> * A **Supabase Edge Function** is responsible for processing raw `psutil` telemetry and generating the JSON summary.
> * The Desktop Agent (ML Engine) uploads the data.
> * This Streamlit app simply queries the pre-calculated results from Supabase and visualizes them.

## 🛠 Developer Guide

### 1. Installation
```bash
# Clone the Web App branch
git clone https://github.com/Once-1296/Web_App_For_System_Health_Metrics_Analyser.git

# Create Virtual Environment
python -m venv venv
# Activate: source venv/bin/activate (Mac/Linux) or .\venv\Scripts\activate (Windows)

# Install Dependencies
pip install -r requirements.txt

# Run the Application
streamlit run app.py
```

### 2. Configuration (secrets.toml)
Streamlit manages secrets differently than the desktop app. You must create a file at .streamlit/secrets.toml.

```File Structure:

.streamlit/
└── secrets.toml
app.py
Content of .streamlit/secrets.toml:

Ini, TOML
[supabase]
url = "[https://your-project.supabase.co](https://your-project.supabase.co)"
key = "your-anon-key"

[google_auth]
client_id = "your-google-client-id"
client_secret = "your-google-client-secret"
```
