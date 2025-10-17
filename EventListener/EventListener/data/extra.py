import os, asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(__file__)
EVENTS_FILE = os.path.join(BASE_DIR, "..", "events.txt")


def load_existing_events():
    """Load existing event IDs from the text file."""
    if not os.path.exists(EVENTS_FILE):
        return set()
    
    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
        return {line.strip() for line in lines if line.strip()}


def save_new_events(new_events):
    """Save new events to the file."""
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        for entry in new_events:
            f.write(entry + "\n")


def ts():
    """Return timestamp as [MM/DD/YY HH:MM:SS]."""
    return datetime.now().strftime("[%m/%d/%y %H:%M:%S]")


def fmt_date(dt):
    if isinstance(dt, datetime):
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        parsed = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return str(dt)