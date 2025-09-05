import os, datetime as dt, jwt, requests
from dotenv import load_dotenv

load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL").replace("wss://", "https://")
API_KEY = os.getenv("LIVEKIT_API_KEY")
API_SECRET = os.getenv("LIVEKIT_API_SECRET")
ROOM = "jarvis"

def dispatch_agent():
    now = dt.datetime.utcnow()
    exp = now + dt.timedelta(minutes=10)

    token = jwt.encode(
        {
            "iss": API_KEY,
            "sub": API_KEY,
            "exp": exp,
            "nbf": now,
            "video": {"room": ROOM, "roomCreate": True},
        },
        API_SECRET,
        algorithm="HS256",
    )

    url = f"{LIVEKIT_URL}/api/agent/dispatch"
    resp = requests.post(
        url,
        json={"room": ROOM},
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )

    return resp.status_code, resp.text


if __name__ == "__main__":
    code, text = dispatch_agent()
    print("Response:", code, text)
