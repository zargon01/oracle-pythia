from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import time

from HitApi import call_chat_api

app = FastAPI(title="Blueverse API Wrapper")

logging.basicConfig(level=logging.INFO)


# 📦 Request Schema
class ChatRequest(BaseModel):
    type: str
    query: str
    current_code: Optional[str] = None


# 📡 Health Check
@app.get("/")
def health():
    return {"status": "running"}


# 🤖 Chat Endpoint
@app.post("/chat")
def chat(req: ChatRequest):
    start_time = time.time()

    try:
        # 🔧 Build query (inject current_code if present)
        final_query = req.query
        if req.current_code:
            final_query += f"\n\nExisting Code:\n{req.current_code}"

        response = call_chat_api(req.type, final_query)

        if not response.ok:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )

        # 🧠 Parse response
        try:
            data = response.json()
        except Exception:
            data = response.text

        # 🔍 Extract code + explanation (depends on API format)
        code = None
        explanation = None
        try:
            data = response.json()
        except Exception:
            data = {}
        if isinstance(data, dict):
            # Adjust keys based on actual API response
            code = data.get("response","")
            # code = data.get("code") or data.get("output") or str(data)
            explanation = f"Generated using {data.get('responseSource', 'unknown model')}"
            # explanation = data.get("explanation") or data.get("message") or ""
            backend_time = data.get("execution_time", None)
        else:
            code = data
            explanation = ""

        response_time = round(time.time() - start_time, 3)

        
        return {
            "status": "success",
            "code": code,
            "explanation": explanation,
            "response_time": response_time,
            "backend_time": backend_time
        }

    except Exception as e:
        logging.error(f"❌ Internal Error: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )