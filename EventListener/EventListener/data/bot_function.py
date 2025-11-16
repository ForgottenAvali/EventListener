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


# Console Commands


# help
        if command == "help":
            print("Available commands:")
            print("  add_group <vrc_group_id>")
            print("  update_group <vrc_group_id>")
            print("  delete_group <vrc_group_id>")
            print()
            print("  add_event <group_id> <event_id> <name> <description> <starts_at> <ends_at> <category> <access_type> <platforms>")
            print("  update_event <event_id> <group_id> <event_id> <name> <description> <starts_at> <ends_at> <category> <access_type> <platforms> <image_url> <tags>")
            print("  delete_event <event_id>")
            print()
            print("  reload_env")
            print("  refetch")
            print("  exit / quit")
            continue

        elif command in ("exit", "quit"):
            print(f"{ts()} [System] Exiting...")
            os._exit(0)

        elif command == "reload_env":
            reload_env()
            continue


# Groups


# add_group
        elif command == "add_group" and len(parts) == 2:
            group_id = parts[1]
            info = await fetch_group_info(group_id)

            if info:
                await add_group_to_api(
                    info["id"],
                    info["name"]
                )
            else:
                print(f"{ts()} [System] Failed to get group info for {group_id}")
            continue


# update_group
        elif command == "update_group" and len(parts) == 2:
            group_id = parts[1]
            info = await fetch_group_info(group_id)

            if info:
                await update_group_on_api(
                    info["id"],
                    info["name"]
                )
            else:
                print(f"{ts()} [System] Failed to get group info for {group_id}")
            continue


# delete_group
        elif command == "delete_group" and len(parts) == 2:
            group_id = parts[1]
            await delete_group_on_api(group_id)
            continue


# Events


# refetch
        elif command == "refetch":
            await fetch_vrc_events()
            continue


# add_event
        elif command == "add_event":
            if len(parts) < 10:
                print(f"{ts()} [System] Usage:")
                print("  add_event <group_id> <event_id> <name> <description> <starts_at> <ends_at> <category> <access_type> <platforms>")
                print("  platforms = comma separated list")
                continue

            vrc_group_id = parts[1]
            vrc_event_id = parts[2]
            name = parts[3]
            description = parts[4]
            starts_at = parts[5]
            ends_at = parts[6]
            category = parts[7]
            access_type = parts[8]
            platforms = parts[9].split(",")

            await add_event_to_api(
                vrc_group_id,
                vrc_event_id,
                name,
                description,
                starts_at,
                ends_at,
                category,
                access_type,
                platforms
            )
            continue


# update_event
        elif command == "update_event":
            if len(parts) < 13:
                print(f"{ts()} [System] Usage:")
                print("  update_event <website_event_id> <group_id> <event_id> <name> <description> <starts_at> <ends_at> <category> <access_type> <platforms> <image_url> <tags>")
                print("  platforms = comma separated list")
                print("  tags = comma separated list")
                continue

            event_id_path = parts[1]
            vrc_group_id = parts[2]
            vrc_event_id = parts[3]
            name = parts[4]
            description = parts[5]
            starts_at = parts[6]
            ends_at = parts[7]
            category = parts[8]
            access_type = parts[9]
            platforms = parts[10].split(",")
            image_url = parts[11] if parts[11].lower() != "none" else None
            tags = parts[12].split(",") if parts[12].lower() != "none" else None

            await update_event_on_api(
                event_id_path,
                vrc_group_id,
                vrc_event_id,
                name,
                description,
                starts_at,
                ends_at,
                category,
                access_type,
                platforms,
                image_url,
                tags
            )
            continue


# delete_event
        elif command == "delete_event":
            if len(parts) < 2:
                print(f"{ts()} [System] Usage:")
                print("  delete_event <event_id>")
                continue

            event_id = parts[1]
            await delete_event_on_api(event_id)
            continue


        else:
            print(f"{ts()} [System] Unknown command. Type 'help' for options.")
