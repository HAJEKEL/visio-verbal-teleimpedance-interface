import aiohttp
import asyncio

async def test_initialize():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8080/control",
            data="initialize",
            headers={"Content-Type": "text/plain"}
        ) as resp:
            print(f"Status: {resp.status}")
            text = await resp.text()
            print(f"Response: {text}")

asyncio.run(test_initialize())
