import asyncio, os
from dotenv import load_dotenv


from data.extra import ts
from data.website.groups import add_group_to_api, update_group_on_api, delete_group_on_api
from data.website.events import add_event_to_api, update_event_on_api, delete_event_on_api
from data.vrchatapi import reload_env, fetch_group_info, fetch_vrc_events


async def command_listener():
    while True:
        command_line = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
        parts = command_line.strip().split(" ")
        if not parts:
            continue

        command = parts[0].lower()

# Console

        # Help
        if command == "help":
            print("Available commands:")
            print("  add_group <group_id>")
            print("  update_group <group_id>")
            print("  delete_group <group_id>")
            print("  add_event <group_id> <event_id> <title> <description> <start_time> <end_time> <category> <access_type> <platforms>")
            print("  update_event <website_event_id> <group_id> <event_id> <title> <description> <start_time> <end_time> <category> <access_type> <platforms>")
            print("  delete_event <website_event_id>")
            print("  reload_env")
            print("  refetch")
            print("  exit / quit")
            continue

        # Exit bot
        elif command in ("exit", "quit"):
            print(f"{ts()} [System] Exiting...")
            os._exit(0)

        # Reload .env
        elif command == "reload_env":
            reload_env()
            continue

# Groups

        # Add a group to the website
        elif command == "add_group" and len(parts) == 2:
            group_id = parts[1]
            info = await fetch_group_info(group_id)
            if info:
                await add_group_to_api(info["id"], info["name"], info["description"])
            else:
                print(f"{ts()} [System] Failed to get group info for {group_id}")
            continue

        # Update a group on the website
        elif command == "update_group" and len(parts) == 2:
            group_id = parts[1]
            info = await fetch_group_info(group_id)
            if info:
                await update_group_on_api(info["id"], info["name"], info["description"])
            else:
                print(f"{ts()} [System] Failed to get group info for {group_id}")
            continue

        # Delete a group on the website
        elif command == "delete_group" and len(parts) == 2:
            group_id = parts[1]

            await delete_group_on_api(group_id)
            continue

# Events

        # Refetch events
        elif command == "refetch":
            await fetch_vrc_events()
            continue

        # Add a event to the website manually
        elif command == "add_event":
            if len(parts) < 10:
                print(f"{ts()} [System] Usage:")
                print("  add_event <group_id> <event_id> <title> <description> <start_time> <end_time> <category> <access_type> <platforms>")
                print("  Example:")
                print('  add_event grp_123 cal_123 title description 2025-10-15T20:00:00Z 2025-10-15T21:00:00Z category public standalonewindows,android')
                continue

            group_id = parts[1]
            event_id = parts[2]
            title = parts[3]
            description = parts[4]
            starts_at = parts[5]
            ends_at = parts[6]
            category = parts[7]
            access_type = parts[8]
            platforms = parts[9].split(",")

            await add_event_to_api(group_id, event_id, title, description, starts_at, ends_at, category, access_type, platforms)
            continue

        # Update a event on the website
        elif command == "update_event":
            if len(parts) < 13:
                print(f"{ts()} [System] Usage:")
                print("  update_event <website_event_id> <group_id> <event_id> <title> <description> <start_time> <end_time> <category> <access_type> <platforms> <image_url> <tags>")
                print("  Example:")
                print('  update_event 123 grp_123 cal_123 title description 2025-10-15T20:00:00Z 2025-10-15T21:00:00Z category public standalonewindows,android https://api.vrchat.cloud/api/1/file/file_123/1/file tag,tag1,tag2')
                continue

            website_id = parts[1]
            group_id = parts[2]
            event_id = parts[3]
            title = parts[4]
            description = parts[5]
            starts_at = parts[6]
            ends_at = parts[7]
            category = parts[8]
            access_type = parts[9]
            platforms = parts[10].split(",")
            image = parts[11]
            tags = parts[12].split(",")

            await update_event_on_api(website_id, group_id, event_id, title, description, starts_at, ends_at, category, access_type, platforms, image, tags)
            continue

        # Delete a event on the website
        elif command == "delete_event":
            if len(parts) < 2:
                print(f"{ts()} [System] Usage:")
                print("  delete_event <website_event_id>")
                print("  Example:")
                print('  delete_event 123')
                continue

            website_id = parts[1]

            await delete_event_on_api(website_id)
            continue

        else:
            print(f"{ts()} [System] Unknown command. Type 'help' for options.")
