from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/token")
def get_token(room: str, identity: str):
    return {"token": f"dummy-token-for-{identity}-in-{room}"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5051)

