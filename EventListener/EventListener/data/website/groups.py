import os, json, requests, asyncio


from data.extra import ts
import data.env_config as config


config.CONTACT
config.ENDPOINT_BASE_GROUP
config.API_KEY


async def add_group_to_api(vrc_group_id: str, name: str):
    if not config.ENDPOINT_BASE_GROUP or not config.API_KEY:
        print(f"{ts()} [Website] Skipping group creation (no endpoint/API key).")
        return

    headers = {
        "content-type": "application/json",
        "x-api-key": config.API_KEY,
        "user-agent": str(config.CONTACT),
    }

    payload = {
        "vrc_group_id": str(vrc_group_id),
        "name": str(name),
    }

    print(f"{ts()} [Website] Creating group '{name}' ({vrc_group_id})...")

    try:
        response = requests.post(config.ENDPOINT_BASE_GROUP, headers=headers, json=payload, timeout=90)

        try:
            response_text = json.dumps(response.json(), indent=2)
        except Exception:
            response_text = response.text or "<no response body>"

        if response.status_code in (200, 201):
            print(f"{ts()} [Website] Group created.\n[Website Response] {response_text}")
        else:
            print(f"{ts()} [Website] Failed ({response.status_code}): {response_text}")

    except Exception as ex:
        print(f"{ts()} [Website] Error creating group: {ex}")


async def update_group_on_api(vrc_group_id: str, name: str):
    if not config.ENDPOINT_BASE_GROUP or not config.API_KEY:
        print(f"{ts()} [Website] Skipping group update (no endpoint/API key).")
        return

    endpoint = f"{config.ENDPOINT_BASE_GROUP}/{vrc_group_id}"

    headers = {
        "content-type": "application/json",
        "x-api-key": config.API_KEY,
        "user-agent": str(config.CONTACT),
    }

    payload = {
        "vrc_group_id": str(vrc_group_id),
        "name": str(name),
    }

    print(f"{ts()} [Website] Updating group '{name}' ({vrc_group_id})...")

    try:
        response = requests.put(
            endpoint,
            headers=headers,
            json=payload,
            timeout=90
        )

        try:
            response_text = json.dumps(response.json(), indent=2)
        except Exception:
            response_text = response.text or "<no response body>"

        if response.status_code in (200, 201):
            print(f"{ts()} [Website] Group updated.\n[Website Response] {response_text}")
        else:
            print(f"{ts()} [Website] Failed ({response.status_code}): {response_text}")

    except Exception as ex:
        print(f"{ts()} [Website] Error updating group: {ex}")


async def delete_group_on_api(vrc_group_id: str):
    if not config.ENDPOINT_BASE_GROUP or not config.API_KEY:
        print(f"{ts()} [Website] Skipping group deletion (no endpoint/API key).")
        return

    endpoint = f"{config.ENDPOINT_BASE_GROUP}/{vrc_group_id}"

    headers = {
        "x-api-key": config.API_KEY,
        "user-agent": str(config.CONTACT),
    }

    print(f"{ts()} [Website] Deleting group {vrc_group_id}...")

    try:
        response = requests.delete(endpoint, headers=headers, timeout=90)

        try:
            response_text = json.dumps(response.json(), indent=2)
        except Exception:
            response_text = response.text or "<no response body>"

        if response.status_code in (200, 201):
            print(f"{ts()} [Website] Group deleted.\n[Website Response] {response_text}")
        else:
            print(f"{ts()} [Website] Failed ({response.status_code}): {response_text}")

    except Exception as ex:
        print(f"{ts()} [Website] Error deleting group: {ex}")
