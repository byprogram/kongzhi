# pip install websockets
import asyncio
import websockets
import base64
from PIL import Image
import io

AGENT_CODE = "123456"

async def control():
    uri = "ws://your_server_ip:6789"
    async with websockets.connect(uri) as ws:
        await ws.send(f"controller:{AGENT_CODE}")
        status = await ws.recv()
        if status == "CONNECTED":
            await ws.send("screenshot")
            b64 = await ws.recv()
            image = Image.open(io.BytesIO(base64.b64decode(b64)))
            image.show()
        else:
            print("Agent not found")

asyncio.run(control())
