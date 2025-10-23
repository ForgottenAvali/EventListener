import os, asyncio, json, logging


import vrchatapi
from vrchatapi.api import authentication_api, groups_api, calendar_api
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode
from vrchatapi.exceptions import UnauthorizedException, ApiException


from dotenv import load_dotenv
from datetime import datetime, timezone


from data.extra import ts, load_existing_events, save_new_events
from data.website.events import send_to_website


load_dotenv()
VRC_USER = os.getenv("VRC_USER")
VRC_PASS = os.getenv("VRC_PASS")
CONTACT = os.getenv("CONTACT")
GROUP_ID = os.getenv("GROUP_ID", "")

GROUP_IDS = [gid.strip() for gid in GROUP_ID.split(",") if gid.strip()]


if not VRC_USER or not VRC_PASS:
    raise ValueError("Missing VRChat login credentials in .env")
if not CONTACT:
    raise ValueError("Missing CONTACT in .env")
if not GROUP_ID:
    raise ValueError("Missing GROUP_ID in .env")


config = vrchatapi.Configuration(username=VRC_USER, password=VRC_PASS)
client = vrchatapi.ApiClient(config)
client.user_agent = f"{CONTACT}"


auth_api = authentication_api.AuthenticationApi(client)
groups_api_instance = groups_api.GroupsApi(client)
calendar_api_instance = calendar_api.CalendarApi(client)


async def login_vrc():
    """Login to VRChat and handle 2FA if needed"""
    loop = asyncio.get_running_loop()
    try:
        user = await loop.run_in_executor(None, auth_api.get_current_user)
        print(f"{ts()} [VRChat-Auth] Logged in as {user.display_name}")
        return user

    except UnauthorizedException as ex:
        body = getattr(ex, "body", None)
        if body:
            try:
                body_json = json.loads(body)
                if "requiresTwoFactorAuth" in body_json:
                    factors = body_json["requiresTwoFactorAuth"]

                    if "emailOtp" in factors:
                        code = input(f"{ts()} [VRChat-Auth] Enter your VRChat Email 2FA code: ")
                        await loop.run_in_executor(
                            None,
                            lambda: auth_api.verify2_fa_email_code(
                                TwoFactorEmailCode(code=code)
                            ),
                        )
                        return await loop.run_in_executor(None, auth_api.get_current_user)

                    if "totp" in factors:
                        code = input(f"{ts()} [VRChat-Auth] Enter your VRChat Authenticator code: ")
                        await loop.run_in_executor(
                            None,
                            lambda: auth_api.verify2_fa(
                                {"code": code}
                            )
                        )
                        return await loop.run_in_executor(None, auth_api.get_current_user)

            except json.JSONDecodeError:
                logging.error(f"{ts()} [VRChat-Auth] Could not parse error body: {body}")
        logging.error(f"{ts()} [VRChat-Auth] Login failed: {ex}")
        raise


async def ensure_connection():
    """Re-login every 5 minutes to keep the session alive"""
    while True:
        try:
            await login_vrc()
        except Exception as ex:
            logging.error(f"{ts()} [VRChat-Auth] Reconnect failed: {ex}")
        await asyncio.sleep(300)


def reload_env(verbose=True):
    """Reload .env and update registered groups"""
    load_dotenv(override=True)
    global GROUP_ID, GROUP_IDS

    GROUP_ID = os.getenv("GROUP_ID", "")
    GROUP_IDS = [gid.strip() for gid in GROUP_ID.split(",") if gid.strip()]

    if verbose:
        print(f"{ts()} [System] Reloaded .env file. Active groups: {GROUP_IDS}")


async def fetch_group_events(group_id: str):
    """Fetch all calendar events for a specific group, including ongoing ones"""
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(
            None, lambda: calendar_api_instance.get_group_calendar_events(group_id)
        )

        events = getattr(result, "data", getattr(result, "results", []))
        now = datetime.now(timezone.utc)
        event_list = []

        for e in events:
            try:
                start = datetime.fromisoformat(e.starts_at.replace("Z", "+00:00"))
                end = datetime.fromisoformat(e.ends_at.replace("Z", "+00:00"))
            except Exception:
                start, end = e.starts_at, e.ends_at

            if end >= now:
                try:
                    full_event = await loop.run_in_executor(
                        None, lambda: calendar_api_instance.get_group_calendar_event(group_id, e.id)
                    )
                    platforms = getattr(full_event, "platforms", [])
                    image = getattr(full_event, "image_url", None)
                    tags = getattr(full_event, "tags", [])
                except ApiException:
                    platforms = []

                event_list.append(
                    {
                        "group_id": group_id,
                        "event_id": e.id,
                        "title": e.title,
                        "description": e.description,
                        "start": e.starts_at,
                        "end": e.ends_at,
                        "category": e.category,
                        "access_type": e.access_type,
                        "platforms": platforms,
                        "image": image,
                        "tags": tags,
                    }
                )

        print(f"{ts()} [VRChat-Calendar] Found {len(event_list)} events for {group_id}.")
        return event_list

    except Exception as ex:
        logging.error(f"{ts()} [VRChat-Calendar] Failed to fetch events for {group_id}: {ex}")
        return []


async def fetch_vrc_events():
    """Fetch all group events and save only new ones to file"""
    existing = load_existing_events()
    new_entries = []
    new_events = []

    for gid in GROUP_IDS:
        print(f"{ts()} [VRChat-Calendar] Fetching events for group {gid}...")
        events = await fetch_group_events(gid)
        await asyncio.sleep(1)

        for e in events:
            entry = f"{e['event_id']} from {e['group_id']}"
            if entry not in existing:
                new_entries.append(entry)
                new_events.append(e)

    if new_entries:
        save_new_events(new_entries)
        print(f"{ts()} [VRChat-Calendar] Added {len(new_entries)} new events.")
        await send_to_website(new_events)
    else:
        print(f"{ts()} [VRChat-Calendar] No new events found")


async def fetch_group_info(group_id: str):
    """Fetch a VRChat group's name and description by ID"""
    loop = asyncio.get_running_loop()
    try:
        group = await loop.run_in_executor(None, lambda: groups_api_instance.get_group(group_id))
        name = getattr(group, "name", None)
        description = getattr(group, "description", None)

        if not name:
            print(f"{ts()} [VRChat-Group] No name found for {group_id}.")
            return None

        print(f"{ts()} [VRChat-Group] Found group '{name}' (ID: {group_id})")
        return {"id": group_id, "name": name, "description": description or ""}
    except Exception as e:
        print(f"{ts()} [VRChat-Group] Failed to fetch info for {group_id}: {e}")
        return None

