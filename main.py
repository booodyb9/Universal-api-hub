import os
import secrets
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Universal API Hub", version="1.0.0", description="Shared API gateway for multiple projects")

class EchoRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": "universal-api-hub"}

def check_key(authorization: str | None):
    expected = os.getenv("API_HUB_KEY")
    if not expected:
        raise HTTPException(status_code=503, detail="API authentication is not configured")
    if not authorization or not authorization.startswith("Bearer ") or not secrets.compare_digest(authorization[7:], expected):
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/v1/echo", tags=["Utilities"])
def echo(payload: EchoRequest, authorization: str | None = Header(default=None)):
    check_key(authorization)
    return {"message": payload.message}
