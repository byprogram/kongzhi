# 🖥️ Remote Desktop Controller

基于 Python + Node.js 实现的远程桌面控制系统。

## 📁 项目结构

```
.
├── agent.py         # 被控端
├── controller.py    # 控制端
├── server.js        # WebSocket 中转服务器
└── README.md
```

## 🔧 安装依赖

### Python（用于 agent 和 controller）

```bash
pip install PyQt5 qasync websockets mss pillow pyautogui
```

### Node.js（用于 server.js）

```bash
npm install ws
```

## 🚀 启动方式

### 启动 WebSocket 服务端

```bash
node server.js
```

### 启动被控端（agent.py）

```bash
python agent.py
```

> 会生成唯一 agent 编号（保存在 APPDATA），并推送屏幕截图

### 启动控制端（controller.py）

```bash
python controller.py
```

> 可选择设备并全屏查看远程桌面，支持鼠标点击与键盘控制

## 🌐 默认 WebSocket 地址

```python
ws://1.94.107.241:6789
```

> 如需更换，请修改 `agent.py` 和 `controller.py` 的 `SERVER_URI`

## 💡 打包 EXE（可选）

推荐使用 PyInstaller 打包：

```bash
pyinstaller agent.py --noconsole --onefile
pyinstaller controller.py --noconsole --onefile
```

## 📝 功能说明

- agent.py：每秒推送屏幕截图，响应 click/move/keyboard 指令
- controller.py：接收图像流并发送交互指令
- server.js：中转图像和控制命令，支持多设备选择

## ⚠️ 注意事项

- Windows 平台需配置 QT 插件路径（若遇图像无法显示）：

```python
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = r"你的插件路径"
```

## ✅ 待扩展功能

- 文件传输
- 多控制端支持
- 支持双向音视频通话
- 更稳定的心跳机制和断线重连

---

📌 欢迎 star 或提交 issue 改进本项目！
