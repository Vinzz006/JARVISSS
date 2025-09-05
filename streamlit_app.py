import os, secrets, datetime as dt
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from livekit import api as lk_api  # official Python API

load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")           # e.g. wss://YOUR_SUBDOMAIN.livekit.cloud
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

app = Flask(__name__)
CORS(app)  # allow your static site to call this server

def require_env(var):
    if not os.getenv(var):
        raise RuntimeError(f"Missing required env var: {var}")
    return os.getenv(var)

# Sanity checks (fail fast on missing secrets)
require_env("LIVEKIT_URL")
require_env("LIVEKIT_API_KEY")
require_env("LIVEKIT_API_SECRET")

@app.get("/token")
def get_token():
    """
    GET /token?room=jarvis&identity=alice&name=Alice
    Returns: { token, wsUrl }
    """
    room = request.args.get("room", "jarvis")
    identity = request.args.get("identity") or f"user-{secrets.token_hex(4)}"
    name = request.args.get("name", identity)

    # Build a token with video grants. TTL = 1 hour.
    at = lk_api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    grants = lk_api.VideoGrants(
        room=room,
        room_join=True,
        can_publish=True,
        can_subscribe=True,
        # set room_create=True if you want the first join to create the room
    )
    token = (
        at.with_identity(identity)
          .with_name(name)
          .with_grants(grants)
          .with_ttl(dt.timedelta(hours=1))
          .to_jwt()
    )

    return jsonify({"token": token, "wsUrl": LIVEKIT_URL, "room": room, "identity": identity})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5050")

import streamlit as st
import requests
import uuid
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Add backend folder to Python path
sys.path.append(os.path.join(os.getcwd(), "backend"))
import dispatch_agent  # import the function

# Constants
TOKEN_SERVER = "http://localhost:5050/token"
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
