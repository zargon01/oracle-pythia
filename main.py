from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

from HitApi import call_chat_api

app = FastAPI(title="Blueverse API Wrapper")

logging.basicConfig(level=logging.INFO)


# Request schema
class ChatRequest(BaseModel):
    type: str
    query: str


# Health check
@app.get("/")
def health():
    return {"status": "running"}


# Chat endpoint
@app.post("/chat")
def chat(req: ChatRequest):
    try:
        response = call_chat_api(req.type, req.query)

        if not response.ok:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )

        # Handle JSON or text response
        try:
            data = response.json()
        except Exception:
            data = response.text

        return {
            "status": "success",
            "data": data
        }

    except Exception as e:
        logging.error(f"❌ Internal Error: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )