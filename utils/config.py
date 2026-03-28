import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AUTH_STATE_PATH = os.path.join(BASE_DIR, "state", "auth.json")

BASE_URL = "https://blueverse-foundry.ltimindtree.com"
CHAT_API = f"{BASE_URL}/chatservice/chat"

SPACE_NAME = "Scripter_7c0c1e4b"
FLOW_ID = "69c4ca6b8bbe8031ba495dd9"

TOKEN_TTL = 1800  # 30 mins