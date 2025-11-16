import os, json, requests, asyncio
from dotenv import load_dotenv

from data.extra import ts, fmt_date

load_dotenv()
CONTACT = os.getenv("CONTACT")
ENDPOINT_BASE_EVENT = os.getenv("ENDPOINT_BASE_EVENT")
API_KEY = os.getenv("API_KEY")


async def send_to_website(events):
    if not ENDPOINT_BASE_EVENT or not API_KEY:
        print(f"{ts()} [Website] Skipping website sending (no endpoint/API key).")
        return

    headers = {
        "content-type": "application/json",
        "x-api-key": API_KEY,
        "user-agent": str(CONTACT),
    }

    sent_count = 0

    for e in events:
        payload = {
            "vrc_group_id": str(e["group_id"]),
            "vrc_event_id": str(e["event_id"]),
            "name": str(e["title"]),
            "description": str(e["description"]),
            "starts_at": fmt_date(e["start"]),
            "ends_at": fmt_date(e["end"]),
            "category": str(e["category"]),
            "access_type": str(e["access_type"]),
            "platforms": [str(p) for p in e.get("platforms", [])],
            "image_url": str(e["image"]) if e.get("image") else None,
            "tags": [str(t) for t in e.get("tags", [])] if e.get("tags") else None,
        }

        print(f"{ts()} [Website] Sending event: {e['event_id']} from {e['group_id']}")

        try:
            response = requests.post(ENDPOINT_BASE_EVENT, headers=headers, json=payload, timeout=90)

            try:
                response_text = json.dumps(response.json(), indent=2)
            except Exception:
                response_text = response.text or "<no response body>"

            if response.status_code in (200, 201):
                sent_count += 1
                print(f"{ts()} [Website] Sent event {e['event_id']}.\n[Website Response] {response_text}")
            else:
                print(f"{ts()} [Website] Failed ({response.status_code}): {response_text}")

        except Exception as ex:
            print(f"{ts()} [Website] Error sending {e['event_id']}: {ex}")

        await asyncio.sleep(2)

    print(f"{ts()} [Website] Finished sending {sent_count}/{len(events)} events.")


async def add_event_to_api(group_id, vrc_event_id, name, description, starts_at, ends_at, category, access_type, platforms, image_url=None, tags=None):
    if not ENDPOINT_BASE_EVENT or not API_KEY:
        print(f"{ts()} [Website] Skipping event creation (no endpoint/API key).")
        return

    payload = {
        "vrc_group_id": group_id,
        "vrc_event_id": vrc_event_id,
        "name": name,
        "description": description,
        "starts_at": fmt_date(starts_at),
        "ends_at": fmt_date(ends_at),
        "category": category,
        "access_type": access_type,
        "platforms": platforms,
        "image_url": image_url,
        "tags": tags,
    }

    headers = {
        "content-type": "application/json",
        "x-api-key": API_KEY,
        "user-agent": str(CONTACT),
    }

    print(f"{ts()} [Website] Creating event '{name}' ({vrc_event_id})...")

    try:
        response = requests.post(ENDPOINT_BASE_EVENT, headers=headers, json=payload, timeout=90)
        try:
            response_text = json.dumps(response.json(), indent=2)
        except Exception:
            response_text = response.text or "<no response body>"

        if response.status_code in (200, 201):
            print(f"{ts()} [Website] Successfully created event.\n[Website Response] {response_text}")
        else:
            print(f"{ts()} [Website] Failed ({response.status_code}): {response_text}")

    except Exception as ex:
        print(f"{ts()} [Website] Error creating event: {ex}")


async def update_event_on_api(website_id, group_id, vrc_event_id, name, description, starts_at, ends_at, category, access_type, platforms, image_url=None, tags=None):
    if not ENDPOINT_BASE_EVENT or not API_KEY:
        print(f"{ts()} [Website] Skipping event update (no endpoint/API key).")
        return

    endpoint = f"{ENDPOINT_BASE_EVENT}/{website_id}"

    payload = {
        "vrc_group_id": group_id,
        "vrc_event_id": vrc_event_id,
        "name": name,
        "description": description,
        "starts_at": fmt_date(starts_at),
        "ends_at": fmt_date(ends_at),
        "category": category,
        "access_type": access_type,
        "platforms": platforms,
        "image_url": image_url,
        "tags": tags,
    }

    headers = {
        "content-type": "application/json",
        "x-api-key": API_KEY,
        "user-agent": str(CONTACT),
    }

    print(f"{ts()} [Website] Updating event '{name}' ({vrc_event_id}) at {endpoint}...")

    try:
        response = requests.put(endpoint, headers=headers, json=payload, timeout=90)

        try:
            response_text = json.dumps(response.json(), indent=2)
        except Exception:
            response_text = response.text or "<no response body>"

        if response.status_code in (200, 201):
            print(f"{ts()} [Website] Successfully updated event.\n[Website Response] {response_text}")
        else:
            print(f"{ts()} [Website] Failed ({response.status_code}): {response_text}")

    except Exception as ex:
        print(f"{ts()} [Website] Error updating event: {ex}")


async def delete_event_on_api(website_id):
    if not ENDPOINT_BASE_EVENT or not API_KEY:
        print(f"{ts()} [Website] Skipping event deletion (no endpoint/API key).")
        return

    endpoint = f"{ENDPOINT_BASE_EVENT}/{website_id}"

    headers = {
        "x-api-key": API_KEY,
        "user-agent": str(CONTACT),
    }

    print(f"{ts()} [Website] Deleting event {website_id}...")

    try:
        response = requests.delete(endpoint, headers=headers, timeout=90)

        try:
            response_text = json.dumps(response.json(), indent=2)
        except Exception:
            response_text = response.text or "<no response body>"

        if response.status_code in (200, 201):
            print(f"{ts()} [Website] Successfully deleted.\n[Website Response] {response_text}")
        else:
            print(f"{ts()} [Website] Failed ({response.status_code}): {response_text}")

    except Exception as ex:
        print(f"{ts()} [Website] Error deleting event: {ex}")
