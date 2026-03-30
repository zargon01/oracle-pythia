from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import time
import json

from HitApi import call_chat_api

app = FastAPI(title="Blueverse API Wrapper")

logging.basicConfig(level=logging.INFO)


class ChatRequest(BaseModel):
    type: str
    query: str
    current_code: Optional[str] = None


@app.get("/")
def health():
    return {"status": "running"}


@app.post("/chat")
def chat(req: ChatRequest):
    start_time = time.time()

    try:
        # 🔧 Build query
        final_query = req.query

        if req.current_code:
            final_query += f"\n\nExisting Code:\n{req.current_code}"

        # 🔥 Force structured response
        final_query += """
        
STRICTLY return valid JSON:
{
  "code": "...",
  "explanation": "..."
}
"""

        response = call_chat_api(req.type, final_query)

        if not response.ok:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )

        try:
            data = response.json()
        except Exception:
            data = {}

        # ✅ Extract model + backend timing
        model = data.get("responseSource", "unknown")
        backend_time = data.get("execution_time", None)

        raw_output = data.get("response", "")

        code = raw_output
        explanation = ""  # ✅ ALWAYS present

        # 🔍 Try parsing model JSON
        try:
            parsed = json.loads(raw_output)
            code = parsed.get("code", raw_output)
            explanation = parsed.get("explanation", "")
        except Exception:
            # fallback: keep raw output as code, explanation stays ""
            pass

        response_time = round(time.time() - start_time, 3)

        return {
            "status": "success",
            "code": code,
            "explanation": explanation,  # ✅ ALWAYS present
            "model": model,
            "response_time": response_time,
            "backend_time": backend_time
        }

    except Exception as e:
        logging.error(f"❌ Internal Error: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )