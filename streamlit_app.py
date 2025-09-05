import streamlit as st
import subprocess
import os
import sys
import requests
import uuid
from dotenv import load_dotenv

load_dotenv()

# Constants
TOKEN_SERVER = os.getenv("TOKEN_SERVER", "http://localhost:5050/token")
ROOM = "jarvis"

st.set_page_config(page_title="JARVIS Control Panel", layout="centered")

st.title("🤖 JARVIS Control Panel")
st.markdown("Start backend services and control your JARVIS agent from here.")

# --- Session State ---
if "logs" not in st.session_state:
    st.session_state["logs"] = ""
if "identity" not in st.session_state:
    st.session_state["identity"] = f"user-{uuid.uuid4().hex[:6]}"

def add_log(msg: str):
    st.session_state["logs"] += msg + "\n"
    st.text_area("Logs", st.session_state["logs"], height=250)

# --- Start Token Server ---
if st.button("🚀 Start Token Server", key="server_btn"):
    try:
        subprocess.Popen([sys.executable, os.path.join("backend", "server.py")])
        add_log("✅ Token server started on http://localhost:5050")
    except Exception as e:
        add_log(f"❌ Error starting token server: {e}")

# --- Start Agent ---
if st.button("🤖 Start JARVIS Agent", key="agent_btn"):
    try:
        subprocess.Popen([sys.executable, os.path.join("backend", "agent.py")])
        add_log("✅ Agent started")
    except Exception as e:
        add_log(f"❌ Error starting agent: {e}")

# --- Connect to Room ---
if st.button("🔗 Connect to Room", key="connect_btn"):
    try:
        res = requests.get(TOKEN_SERVER, params={"room": ROOM, "identity": st.session_state["identity"]})
        if res.status_code == 200:
            data = res.json()
            add_log(f"✅ Connected to room {data['room']} as {data['identity']}")
            st.success("Token retrieved successfully.")
        else:
            add_log(f"❌ Token server error: {res.status_code}")
    except Exception as e:
        add_log(f"❌ Error connecting: {e}")

# --- Dispatch Agent ---
if st.button("📤 Dispatch Agent", key="dispatch_btn"):
    try:
        sys.path.append(os.path.join(os.getcwd(), "backend"))
        import dispatch_agent
        code, text = dispatch_agent.dispatch_agent()
        add_log(f"Agent dispatch response: {code} {text}")
        if code == 200:
            st.success("✅ Agent dispatched successfully")
        else:
            st.error("❌ Failed to dispatch agent")
    except Exception as e:
        add_log(f"❌ Dispatch error: {e}")
