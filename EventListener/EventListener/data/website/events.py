import os, json, requests, asyncio
from dotenv import load_dotenv


from data.extra import ts, fmt_date


load_dotenv()
CONTACT = os.getenv("CONTACT")
ENDPOINT_BASE_EVENT = os.getenv("ENDPOINT_BASE_EVENT")
ENDPOINT_EVENT = os.getenv("ENDPOINT_EVENT")
API_KEY = os.getenv("API_KEY")


async def send_to_website(events):
    if not ENDPOINT_EVENT or not API_KEY:
        print(f"{ts()} [Website] Skipping website sending (no webhook/API key).")
        return

    headers = {
        "content-type": "application/json",
        "x-api-key": API_KEY,
        "user-agent": f"{CONTACT}",
    }

    sent_count = 0

    for e in events:
        payload = {
            "group_id": str(e["group_id"]),
            "event_id": str(e["event_id"]),
            "title": str(e["title"]),
            "description": str(e["description"]),
            "starts_at": fmt_date(e["start"]),
            "ends_at": fmt_date(e["end"]),
            "category": str(e["category"]),
            "access_type": str(e["access_type"]),
            "platforms": [str(p) for p in e.get("platforms", [])],
        }

        print(f"{ts()} [Website] Sending event: {e['event_id']} from {e['group_id']}")

        try:
            response = requests.post(ENDPOINT_EVENT, headers=headers, json=payload, timeout=90)
            try:
                response_text = json.dumps(response.json(), indent=2)
            except Exception:
                response_text = response.text or "<no response body>"

            if response.status_code in (200, 201):
                sent_count += 1
                print(f"{ts()} [Website] Sent event {e['event_id']} from {e['group_id']}.\n[Website Response - {e['event_id']}] {response_text}")
            else:
                print(f"{ts()} [Website] Failed to send {e['event_id']} ({response.status_code}): {response_text}")

        except Exception as ex:
            print(f"{ts()} [Website] Error sending {e['event_id']}: {ex}")

        await asyncio.sleep(2)

    print(f"{ts()} [Website] Finished sending {sent_count}/{len(events)} events.")


async def add_event_to_api(group_id, event_id, title, description, starts_at, ends_at, category, access_type, platforms):
    """Sends an event to the website API directly."""
    if not ENDPOINT_EVENT or not API_KEY:
        print(f"{ts()} [Website] Skipping event creation (no endpoint/API key).")
        return

    payload = {
        "group_id": group_id,
        "event_id": event_id,
        "title": title,
        "description": description,
        "starts_at": fmt_date(starts_at),
        "ends_at": fmt_date(ends_at),
        "category": category,
        "access_type": access_type,
        "platforms": platforms,
    }

    headers = {
        "content-type": "application/json",
        "x-api-key": API_KEY,
        "user-agent": f"{CONTACT}",
    }

    print(f"{ts()} [Website] Creating event '{title}' ({event_id})...")

    try:
        response = requests.post(ENDPOINT_EVENT, headers=headers, json=payload, timeout=90)
        try:
            response_text = json.dumps(response.json(), indent=2)
        except Exception:
            response_text = response.text or "<no response body>"

        if response.status_code in (200, 201):
            print(f"{ts()} [Website] Successfully created event '{title}'.\n[Website Response] {response_text}")
        else:
            print(f"{ts()} [Website] Failed to create event '{title}' ({response.status_code}): {response_text}")
    except Exception as ex:
        print(f"{ts()} [Website] Error creating event '{title}': {ex}")


async def update_event_on_api(website_id, group_id, event_id, title, description, starts_at, ends_at, category, access_type, platforms):
    if not ENDPOINT_BASE_EVENT or not API_KEY:
        print(f"{ts()} [Website] Skipping event update (no endpoint/API key).")
        return

    endpoint = f"{ENDPOINT_BASE_EVENT}/{website_id}/update"

    payload = {
        "group_id": group_id,
        "event_id": event_id,
        "title": title,
        "description": description,
        "starts_at": fmt_date(starts_at),
        "ends_at": fmt_date(ends_at),
        "category": category,
        "access_type": access_type,
        "platforms": platforms,
    }

    headers = {
        "content-type": "application/json",
        "x-api-key": API_KEY,
        "user-agent": f"{CONTACT}",
    }

    print(f"{ts()} [Website] Updating event '{title}' ({event_id}) at {endpoint}...")

    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=90)

        try:
            response_text = json.dumps(response.json(), indent=2)
        except Exception:
            response_text = response.text or "<no response body>"

        if response.status_code in (200, 201):
            print(f"{ts()} [Website] Successfully updated event '{title}'.\n[Website Response] {response_text}")
        else:
            print(f"{ts()} [Website] Failed to update event '{title}' ({response.status_code}): {response_text}")

    except Exception as ex:
        print(f"{ts()} [Website] Error updating event '{title}': {ex}")


async def delete_event_on_api(website_id):
    if not ENDPOINT_BASE_EVENT or not API_KEY:
        print(f"{ts()} [Website] Skipping event update (no endpoint/API key).")
        return

    endpoint = f"{ENDPOINT_BASE_EVENT}/{website_id}/delete"

    headers = {
        "x-api-key": API_KEY,
        "user-agent": f"{CONTACT}",
    }

    print(f"{ts()} [Website] Deleting event id {website_id}")

    try:
        response = requests.post(endpoint, headers=headers, timeout=90)

        try:
            response_text = json.dumps(response.json(), indent=2)
        except Exception:
            response_text = response.text or "<no response body>"

        if response.status_code in (200, 201):
            print(f"{ts()} [Website] Successfully deleted event '{website_id}'.\n[Website Response] {response_text}")
        else:
            print(f"{ts()} [Website] Failed to update event '{website_id}' ({response.status_code}): {response_text}")

    except Exception as ex:
        print(f"{ts()} [Website] Error updating event '{website_id}': {ex}")