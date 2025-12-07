import os
from dotenv import load_dotenv

load_dotenv(override=True)

VRC_USER = os.getenv("VRC_USER")
VRC_PASS = os.getenv("VRC_PASS")
user_id = os.getenv("USER_ID")

API_KEY = os.getenv("API_KEY")
ENDPOINT_BASE_EVENT = os.getenv("ENDPOINT_BASE_EVENT")
ENDPOINT_BASE_GROUP = os.getenv("ENDPOINT_BASE_GROUP")

CONTACT = os.getenv("CONTACT")

raw_ids = os.getenv("GROUP_ID", "")
GROUP_IDS = [gid.strip() for gid in raw_ids.split(",") if gid.strip()]
