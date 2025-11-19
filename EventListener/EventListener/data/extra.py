import os, asyncio


from datetime import datetime, timezone
from dotenv import load_dotenv


import data.env_config as config


BASE_DIR = os.path.dirname(__file__)
EVENTS_FILE = os.path.join(BASE_DIR, "..", "events.txt")



config.API_KEY
config.GROUP_IDS
config.ENDPOINT_BASE_EVENT
config.ENDPOINT_BASE_GROUP


VALID_KEYS = {"api_key", "group_ids", "group_id", "endpoints"}


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


def reload_env(*items, verbose=True):
    if not items:
        print(f"{ts()} [System] Error: No reload targets provided. Valid: {VALID_KEYS}")
        return

    items = [i.lower() for i in items]

    invalid = [i for i in items if i not in VALID_KEYS]
    if invalid:
        print(f"{ts()} [System] Error: Invalid reload key(s): {invalid}. Valid: {VALID_KEYS}")
        return

    load_dotenv(override=True)
    reloaded_any = False

    if "api_key" in items or "all" in items:
        config.API_KEY = os.getenv("API_KEY", "")
        if verbose: print(f"{ts()} [System] Reloaded API_KEY")
        reloaded_any = True

    if "group_ids" in items or "group_id" in items or "all" in items:
        raw = os.getenv("GROUP_ID", "")
        config.GROUP_IDS = [gid.strip() for gid in raw.split(",") if gid.strip()]
        if verbose: print(f"{ts()} [System] Reloaded GROUP_IDS: {config.GROUP_IDS}")
        reloaded_any = True

    if "endpoints" in items or "endpoint" in items or "all" in items:
        config.ENDPOINT_BASE_EVENT = os.getenv("ENDPOINT_BASE_EVENT", "")
        config.ENDPOINT_BASE_GROUP = os.getenv("ENDPOINT_BASE_GROUP", "")
        if verbose:
            print(f"{ts()} [System] Reloaded ENDPOINTS:\n  EVENT: {config.ENDPOINT_BASE_EVENT}\n  GROUP: {config.ENDPOINT_BASE_GROUP}")
        reloaded_any = True

    if "vrchat" in items or "all" in items:
        config.VRC_USER = os.getenv("VRC_USER", "")
        config.VRC_PASS = os.getenv("VRC_PASS", "")
        config.USER_ID = os.getenv("USER_ID", "")
        if verbose:
            print(f"{ts()} [System] Reloaded VRChat credentials")
        reloaded_any = True

    if "contact" in items or "all" in items:
        config.CONTACT = os.getenv("CONTACT", "")
        if verbose:
            print(f"{ts()} [System] Reloaded CONTACT: {config.CONTACT}")
        reloaded_any = True

    if not reloaded_any:
        print(f"{ts()} [System] Nothing was reloaded")
    elif verbose:
        print(f"{ts()} [System] Reload complete")
