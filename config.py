import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
MONGO_URI = os.environ.get("MONGO_URI", "")
DB_NAME = os.environ.get("DB_NAME", "autoforwardbot")

# Comma separated user IDs, e.g. "12345,67890"
_owner_raw = os.environ.get("OWNER_IDS", "")
OWNER_IDS = [int(x) for x in _owner_raw.split(",") if x.strip().isdigit()]

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env var is required")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI env var is required")
if not OWNER_IDS:
    raise RuntimeError("OWNER_IDS env var is required (comma separated telegram user ids)")
