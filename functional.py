import asyncio
from pyrogram.errors import BadRequest, FloodWait


async def join(urls: list[str], app):
    for url in urls:
        try:
            print(url)
            await app.join_chat(url)
        except BadRequest as e:
            pass
        except FloodWait as e:
            print(f'I wait {e.value}')
            await asyncio.sleep(e.value)

