import streamlit as st
import requests
import uuid
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend folder to path
sys.path.append(os.path.join(os.getcwd(), "backend"))
import dispatch_agent

# Constants
TOKEN_SERVER = os.getenv("TOKEN_SERVER", "http://localhost:5050/token")
ROOM = "jarvis"

st.set_page_config(page_title="JARVIS - Streamlit UI", layout="centered")

st.title("🤖 JARVIS Voice Assistant (Streamlit)")
st.markdown("Control and debug your JARVIS agent here.")

# Session state
if "logs" not in st.session_state:
    st.session_state["logs"] = ""
if "identity" not in st.session_state:
    st.session_state["identity"] = f"user-{uuid.uuid4().hex[:6]}"

def add_log(msg: str):
    st.session_state["logs"] += msg + "\n"
    st.text_area("Logs", st.session_state["logs"], height=250)

# 🔗 Connect button
if st.button("🔗 Connect to Room", key="connect_btn"):
    try:
        res = requests.get(TOKEN_SERVER, params={"room": ROOM, "identity": st.session_state["identity"]})
        if res.status_code == 200:
            data = res.json()
            add_log(f"✅ Connected to room {data['room']} as {data['identity']}")
            st.success("Token retrieved successfully.")
        else:
            add_log(f"❌ Token server error: {res.status_code}")
            st.error("Failed to get token.")
    except Exception as e:
        add_log(f"❌ Error connecting: {e}")
        st.error(f"Error: {e}")

# 📤 Dispatch Agent button
if st.button("📤 Dispatch Agent", key="dispatch_btn"):
    try:
        code, text = dispatch_agent.dispatch_agent()
        add_log(f"Agent dispatch response: {code} {text}")
        if code == 200:
            st.success("✅ Agent dispatched successfully")
        else:
            st.error("❌ Failed to dispatch agent")
    except Exception as e:
        add_log(f"❌ Dispatch error: {e}")
        st.error(f"Error: {e}")



