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
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5050")), debug=True)
