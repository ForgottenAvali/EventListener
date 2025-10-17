import asyncio


from data.vrchatapi import login_vrc, ensure_connection, fetch_vrc_events
from data.bot_function import command_listener


async def main():
    await login_vrc()
    asyncio.create_task(ensure_connection())

    async def fetch_loop():
        while True:
            await fetch_vrc_events()
            await asyncio.sleep(900)

    await asyncio.gather(
        fetch_loop(),
        command_listener()
    )

if __name__ == "__main__":
    asyncio.run(main())