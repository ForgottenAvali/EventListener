import os, json, requests, asyncio
from dotenv import load_dotenv


from data.extra import ts, fmt_date


load_dotenv()
CONTACT = os.getenv("CONTACT")
ENDPOINT_BASE_GROUP = os.getenv("ENDPOINT_BASE_GROUP")
ENDPOINT_GROUP = os.getenv("ENDPOINT_GROUP")
API_KEY = os.getenv("API_KEY")


async def add_group_to_api(group_id: str, name: str, description: str = ""):
    if not ENDPOINT_GROUP or not API_KEY:
        print(f"{ts()} [Website] Skipping group creation (no endpoint/API key).")
        return

    headers = {
        "x-api-key": API_KEY,
        "user-agent": f"{CONTACT}",
    }

    payload = {
        "group_id": str(group_id),
        "name": str(name),
        "description": str(description or ""),
    }

    print(f"{ts()} [Website] Creating group '{name}' ({group_id})")

    try:
        response = requests.post(ENDPOINT_GROUP, headers=headers, json=payload, timeout=90)
        try:
            response_text = json.dumps(response.json(), indent=2)
        except Exception:
            response_text = response.text or "<no response body>"

        if response.status_code in (200, 201):
            print(f"{ts()} [Website] Group '{name}' created successfully.\n[Website Response - {group_id}] {response_text}")
        else:
            print(f"{ts()} [Website] Failed to create group '{name}' ({response.status_code}): {response_text}")

    except Exception as ex:
        print(f"{ts()} [Website] Error creating group '{name}': {ex}")


async def update_group_on_api(group_id: str, name: str, description: str = ""):
    if not ENDPOINT_BASE_GROUP or not API_KEY:
        print(f"{ts()} [Website] Skipping group creation (no endpoint/API key).")
        return
    
    endpoint = f"{ENDPOINT_BASE_GROUP}/{group_id}/update"
    
    headers = {
        "x-api-key": API_KEY,
        "user-agent": f"{CONTACT}"
    }

    payload = {
        "group_id": str(group_id),
        "name": str(name),
        "description": str(description or ""),
    }

    print(f"{ts()} [Website] Updating group '{name}' ({group_id})")

    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=90)

        try:
            response_text = json.dumps(response.json(), indent=2)
        except Exception:
            response_text = response.text or "<no response body>"

        if response.status_code in (200, 201):
            print(f"{ts()} [Website] Successfully updated group '{name}'.\n[Website Response] {response_text}")
        else:
            print(f"{ts()} [Website] Failed to update group '{name}' ({response.status_code}): {response_text}")

    except Exception as ex:
        print(f"{ts()} [Website] Error updating group '{name}': {ex}")


async def delete_group_on_api(group_id):
    if not ENDPOINT_BASE_GROUP or not API_KEY:
        print(f"{ts()} [Website] Skipping event update (no endpoint/API key).")
        return

    endpoint = f"{ENDPOINT_BASE_GROUP}/{group_id}/delete"

    headers = {
        "x-api-key": API_KEY,
        "user-agent": f"{CONTACT}",
    }

    print(f"{ts()} [Website] Deleting group {group_id}")

    try:
        response = requests.post(endpoint, headers=headers, timeout=90)

        try:
            response_text = json.dumps(response.json(), indent=2)
        except Exception:
            response_text = response.text or "<no response body>"

        if response.status_code in (200, 201):
            print(f"{ts()} [Website] Successfully deleted group '{group_id}'.\n[Website Response] {response_text}")
        else:
            print(f"{ts()} [Website] Failed to delete group '{group_id}' ({response.status_code}): {response_text}")

    except Exception as ex:
        print(f"{ts()} [Website] Error updating event '{group_id}': {ex}")