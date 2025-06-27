import sys
import asyncio
import websockets
import base64
from PIL import Image
from io import BytesIO
import os

if sys.platform.startswith("win") and sys.version_info >= (3, 8):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = r"C:\\Users\\维尼熊\\AppData\\Local\\Packages\\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\\LocalCache\\local-packages\\Python310\\site-packages\\PyQt5\\Qt5\\plugins\\platforms"

from PyQt5.QtWidgets import (
    QApplication, QLabel, QWidget, QVBoxLayout,
    QInputDialog, QMessageBox, QMainWindow, QAction
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from qasync import QEventLoop

SERVER_URL = "ws://1.94.107.241:6789"

def fix_base64_padding(b64_string):
    b64_string = b64_string.strip().replace("\n", "").replace("\r", "")
    return b64_string + "=" * (-len(b64_string) % 4)

class RemoteViewer(QMainWindow):
    def __init__(self, agent_code):
        super().__init__()
        self.agent_code = agent_code
        self.setWindowTitle(f"控制端 - Agent {agent_code}")
        self.showFullScreen()  # 直接全屏显示

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.label = QLabel("连接中...", self.central_widget)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(True)  # 让图像填满 QLabel 区域

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # 去掉边距
        layout.addWidget(self.label)
        self.central_widget.setLayout(layout)

        self.websocket = None
        self.ws_lock = asyncio.Lock()
        self.label.mousePressEvent = self.on_click

        menubar = self.menuBar()
        device_menu = menubar.addMenu("设备")
        switch_action = QAction("连接其他设备", self)
        switch_action.triggered.connect(self.reconnect)
        device_menu.addAction(switch_action)

    def showEvent(self, event):
        super().showEvent(event)
        if not hasattr(self, "_started"):
            self._started = True
            asyncio.ensure_future(self.connect_server())

    def keyPressEvent(self, event):
        key = event.text()
        if key:
            asyncio.ensure_future(self.send_ws(f"key:{key}"))

    async def connect_server(self):
        try:
            self.websocket = await websockets.connect(SERVER_URL, max_size=None)
            await self.websocket.send(f"controller:{self.agent_code}")
            self.label.setText("已连接，开始接收图像流")
            asyncio.ensure_future(self.receive_stream())
        except Exception as e:
            self.label.setText(f"连接失败: {e}")

    async def send_ws(self, msg):
        if self.websocket:
            async with self.ws_lock:
                try:
                    await self.websocket.send(msg)
                except Exception as e:
                    self.label.setText(f"发送失败：{e}")

    async def receive_stream(self):
        try:
            async for b64 in self.websocket:
                try:
                    if not b64 or len(b64) < 100:
                        continue
                    b64_clean = fix_base64_padding(b64)
                    image = Image.open(BytesIO(base64.b64decode(b64_clean)))
                    data = image.convert("RGB").tobytes("raw", "RGB")
                    qimage = QImage(data, image.width, image.height, QImage.Format_RGB888)
                    self.label.setPixmap(QPixmap.fromImage(qimage))
                except Exception as e:
                    print("图像解码失败:", e)
                    continue
        except Exception as e:
            self.label.setText(f"连接中断：{e}")

    def on_click(self, event):
        if not self.label.pixmap():
            return
        x = event.pos().x()
        y = event.pos().y()
        asyncio.ensure_future(self.send_ws(f"click:{x},{y}"))

    def reconnect(self):
        if self.websocket:
            asyncio.ensure_future(self.websocket.close())
        self.hide()
        asyncio.ensure_future(self.launch_new_viewer())

    async def launch_new_viewer(self):
        new_viewer = await launch()
        if new_viewer:
            new_viewer.showFullScreen()

async def select_agent():
    try:
        async with websockets.connect(SERVER_URL) as ws:
            await ws.send("controller:list")
            data = await ws.recv()
            if data == "NO_AGENT":
                return None
            return data.split(",")
    except Exception:
        return []

async def launch():
    agents = await select_agent()
    if not agents:
        QMessageBox.critical(None, "错误", "没有在线设备")
        return

    selected, ok = QInputDialog.getItem(None, "选择设备", "选择 Agent 编号：", agents, 0, False)
    if ok:
        viewer = RemoteViewer(selected)
        return viewer
    else:
        return None

def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        viewer = loop.run_until_complete(launch())
        if viewer:
            loop.run_forever()

if __name__ == "__main__":
    main()
