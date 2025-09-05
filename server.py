import os
import datetime as dt
import jwt
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

app = Flask(__name__)
CORS(app)

@app.get("/token")
def get_token():
    """Generate and return a LiveKit access token"""
    room = request.args.get("room", "jarvis")
    identity = request.args.get("identity", "user-123")

    now = dt.datetime.utcnow()
    exp = now + dt.timedelta(minutes=10)

    token = jwt.encode(
        {
            "iss": LIVEKIT_API_KEY,
            "sub": LIVEKIT_API_KEY,
            "exp": exp,
            "nbf": now,
            "video": {"room": room, "roomCreate": True},
        },
        LIVEKIT_API_SECRET,
        algorithm="HS256",
    )

    return jsonify({
        "token": token,
        "wsUrl": LIVEKIT_URL,
        "room": room,
        "identity": identity
    })

if __name__ == "__main__":
    # Changed port to 5051
    app.run(host="0.0.0.0", port=5051, debug=True)
