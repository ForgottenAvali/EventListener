import os, asyncio, json, logging, http.cookiejar, requests, vrchatapi


from vrchatapi.api import authentication_api, groups_api, calendar_api, users_api
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode
from vrchatapi.exceptions import UnauthorizedException, ApiException


from datetime import datetime, timezone


from data.extra import ts, load_existing_events, save_new_events
from data.website.events import send_to_website
import data.env_config as config


config.VRC_USER
config.VRC_PASS
config.user_id
config.CONTACT
config.GROUP_IDS


configuration = vrchatapi.Configuration(username=config.VRC_USER, password=config.VRC_PASS)
client = vrchatapi.ApiClient(configuration)
client.user_agent = f"{config.CONTACT}"


auth_api = authentication_api.AuthenticationApi(client)
groups_api_instance = groups_api.GroupsApi(client)
calendar_api_instance = calendar_api.CalendarApi(client)
users_api_instance = users_api.UsersApi(client)


AUTH_TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "vrc_auth_token.json")


async def login_vrc():
    loop = asyncio.get_running_loop()

    if os.path.exists(AUTH_TOKEN_FILE):
        try:
            with open(AUTH_TOKEN_FILE, "r") as f:
                saved = json.load(f)
                token = saved.get("auth")
                if token:
                    client.rest_client.cookie_jar.set_cookie(
                        http.cookiejar.Cookie(
                            version=0,
                            name="auth",
                            value=token,
                            port=None,
                            port_specified=False,
                            domain="api.vrchat.cloud",
                            domain_specified=True,
                            domain_initial_dot=False,
                            path="/",
                            path_specified=True,
                            secure=True,
                            expires=None,
                            discard=False,
                            comment=None,
                            comment_url=None,
                            rest={},
                            rfc2109=False
                        )
                    )

                    user = await loop.run_in_executor(None, auth_api.get_current_user)
                    print(f"[VRChat] Reused existing auth token as {user.display_name}")
                    return user
        except Exception as e:
            logging.warning(f"[VRChat] Failed to use saved auth token: {e}")

    try:
        user = await loop.run_in_executor(None, auth_api.get_current_user)
        print(f"[VRChat] Logged in as {user.display_name} (no 2FA required)")

        for cookie in client.rest_client.cookie_jar:
            if cookie.name == "auth":
                with open(AUTH_TOKEN_FILE, "w") as f:
                    json.dump({"auth": cookie.value}, f)
                print("[VRChat] Saved new auth token")
                break

        return user

    except UnauthorizedException as e:
        body = getattr(e, "body", None)
        if body:
            try:
                body_json = json.loads(body)
                if "requiresTwoFactorAuth" in body_json:
                    factors = body_json["requiresTwoFactorAuth"]

                    if "emailOtp" in factors:
                        code = input("[VRChat] Enter your VRChat Email 2FA code: ")
                        await loop.run_in_executor(
                            None,
                            lambda: auth_api.verify2_fa_email_code(TwoFactorEmailCode(code=code))
                        )
                        user = await loop.run_in_executor(None, auth_api.get_current_user)
                    elif "totp" in factors:
                        code = input("[VRChat] Enter your VRChat Authenticator code: ")
                        await loop.run_in_executor(None, lambda: auth_api.verify2_fa({"code": code}))
                        user = await loop.run_in_executor(None, auth_api.get_current_user)

                    for cookie in client.rest_client.cookie_jar:
                        if cookie.name == "auth":
                            with open(AUTH_TOKEN_FILE, "w") as f:
                                json.dump({"auth": cookie.value}, f)
                            print("[VRChat] Saved new auth token")
                            break

                    return user

            except json.JSONDecodeError:
                logging.error(f"[VRChat] Could not parse error body: {body}")

        logging.error(f"[VRChat] Login failed: {e}")
        raise


async def ensure_connection():
    while True:
        try:
            await login_vrc()
        except Exception as ex:
            logging.error(f"{ts()} [VRChat-Auth] Reconnect failed: {ex}")
        await asyncio.sleep(300)


async def fetch_group_events(group_id: str):
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
    existing = load_existing_events()
    new_entries = []
    new_events = []

    for gid in config.GROUP_IDS:
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
    loop = asyncio.get_running_loop()
    try:
        group = await loop.run_in_executor(None, lambda: groups_api_instance.get_group(group_id))
        name = getattr(group, "name", None)

        if not name:
            print(f"{ts()} [VRChat-Group] No name found for {group_id}.")
            return None

        print(f"{ts()} [VRChat-Group] Found group '{name}' (ID: {group_id})")
        return {"id": group_id, "name": name}
    except Exception as e:
        print(f"{ts()} [VRChat-Group] Failed to fetch info for {group_id}: {e}")
        return None


async def is_in_group(group_id: str):
    loop = asyncio.get_running_loop()

    try:
        groups = await loop.run_in_executor(
            None,
            lambda: users_api_instance.get_user_groups(config.user_id)
        )

        for g in groups:
            if g.id == group_id:
                return True

        return False

    except Exception as e:
        print(f"{ts()} [VRChat-Group] Failed to check group membership: {e}")
        return False


async def join_group(group_id: str):
    loop = asyncio.get_running_loop()

    try:
        group = await loop.run_in_executor(
            None,
            lambda: groups_api_instance.join_group(group_id)
        )
        return group

    except Exception as e:
        print(f"[VRChat-Group] Failed to join group {group_id}: {e}")
        return None
