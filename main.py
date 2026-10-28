import json
import os
import secrets
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Universal API Hub", version="1.1.0")

class EchoRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": "universal-api-hub"}

def authenticate(
    authorization: Annotated[str | None, Header()] = None,
    x_project_id: Annotated[str | None, Header()] = None,
) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    supplied = authorization[7:]
    if not supplied:
        raise HTTPException(status_code=401, detail="Unauthorized")

    raw = os.getenv("PROJECT_API_KEYS")
    if raw:
        try:
            keys = json.loads(raw)
            if not isinstance(keys, dict) or not all(isinstance(k, str) and isinstance(v, str) and v for k, v in keys.items()):
                raise ValueError("Invalid mapping")
        except (ValueError, TypeError):
            raise HTTPException(status_code=503, detail="Project authentication misconfigured")
        if not x_project_id or x_project_id not in keys:
            raise HTTPException(status_code=401, detail="Unauthorized")
        if not secrets.compare_digest(supplied, keys[x_project_id]):
            raise HTTPException(status_code=401, detail="Unauthorized")
        return x_project_id

    legacy = os.getenv("API_HUB_KEY")
    if not legacy:
        raise HTTPException(status_code=503, detail="API authentication is not configured")
    if not secrets.compare_digest(supplied, legacy):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return "legacy"

@app.post("/v1/echo", tags=["Utilities"])
def echo(payload: EchoRequest, project: Annotated[str, Depends(authenticate)]):
    return {"message": payload.message, "project": project}
