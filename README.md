# Remote Desktop Controller（远程桌面控制系统）

这是一个基于 WebSocket 的远程桌面控制系统，包括：

- agent.py：被控端，推送屏幕截图并接收控制指令
- controller.py：控制端，显示远程图像并发出控制命令
- server.js：Node.js WebSocket 中转服务器

## 项目结构

```
.
├── agent.py
├── controller.py
├── server.js
└── README.md
```

## 安装依赖

### Python（用于 agent 和 controller）

```bash
pip install PyQt5 qasync websockets mss pillow pyautogui
```

### Node.js（用于服务器）

```bash
npm install ws
```

## 启动方式

### 启动 WebSocket 服务器

```bash
node server.js
```

### 启动被控端（Agent）

```bash
python agent.py
```

- 会生成唯一 agent 编号（保存在 APPDATA）
- 会尝试添加开机启动项
- 每秒推送 base64 编码的屏幕截图
- 接收 click、move、key 指令进行控制

### 启动控制端（Controller）

```bash
python controller.py
```

- 弹窗选择在线 Agent
- 全屏展示桌面图像
- 鼠标点击位置同步
- 键盘输入远程执行

## 默认服务器地址

```python
ws://1.94.107.241:6789
```

可在 `agent.py` 和 `controller.py` 中自行修改。

## 注意事项

- 如果 PyQt 图像无法显示，请确保配置了正确的插件路径：

```python
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = r"你的路径"
```

- 如果你要生成 EXE，建议使用 `pyinstaller`：

```bash
pyinstaller agent.py --noconsole --onefile
pyinstaller controller.py --noconsole --onefile
```

## 开发建议

- 支持多客户端同时查看
- 添加远程文件管理功能
- 支持双向语音或聊天

