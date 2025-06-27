import asyncio
import websockets

clients = {}

async def relay(websocket, path):
    try:
        client_type = await websocket.recv()
        if client_type.startswith("agent:"):
            code = client_type.split(":")[1]
            clients[code] = websocket
            print(f"✅ Agent [{code}] connected")
            try:
                while True:
                    await asyncio.sleep(10)
            except Exception as e:
                print(f"❌ Agent [{code}] 中断: {e}")
            finally:
                if clients.get(code) == websocket:
                    del clients[code]
                    print(f"🧹 Agent [{code}] 清理完成")
        elif client_type.startswith("controller:"):
            code = client_type.split(":")[1]
            agent_ws = clients.get(code)
            print(f"🎮 控制端请求连接 Agent [{code}]")
            if agent_ws:
                await websocket.send("CONNECTED")
                try:
                    while True:
                        cmd = await websocket.recv()
                        print(f"📤 控制命令: {cmd}")
                        await agent_ws.send(cmd)
                        resp = await agent_ws.recv()
                        await websocket.send(resp)
                except Exception as e:
                    print(f"❌ 控制端异常：{e}")
            else:
                await websocket.send("NO_AGENT")
    except Exception as e:
        print(f"🔥 服务器异常：{e}")

async def main():
    async with websockets.serve(relay, "0.0.0.0", 6789):
        print("🚀 WebSocket 服务器已启动，监听端口 6789")
        await asyncio.Future()

asyncio.run(main())
