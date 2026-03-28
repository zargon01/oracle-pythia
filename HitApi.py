import requests
import json
import logging

from utils.GetBearer import get_bearer_token, invalidate_token
from utils.config import CHAT_API, SPACE_NAME, FLOW_ID
from GetState import refresh_session

logging.basicConfig(level=logging.INFO)


def _make_request(token, query_type, query):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    query_payload = {
        "type": query_type,
        "content": query
    }

    payload = {
        "query": json.dumps(query_payload),
        "space_name": SPACE_NAME,
        "flowId": FLOW_ID
    }

    return requests.post(CHAT_API, headers=headers, json=payload, timeout=15)


def call_chat_api(query_type: str, query: str):
    
    try:
        token = get_bearer_token()
    except Exception as e:
        logging.warning(f"⚠️ Token fetch failed: {e}")
        refresh_session()
        token = get_bearer_token(force_refresh=True)

    response = _make_request(token, query_type, query)

    if response.status_code == 401:
        logging.warning("⚠️ Token expired. Refreshing...")

        invalidate_token()

        try:
            token = get_bearer_token(force_refresh=True)
        except Exception:
            logging.warning("⚠️ Token refresh failed. Regenerating session...")
            refresh_session()
            token = get_bearer_token(force_refresh=True)

        response = _make_request(token, query_type, query)

    if not response.ok:
        logging.error(f"❌ API Failed: {response.status_code} | {response.text}")

    return response