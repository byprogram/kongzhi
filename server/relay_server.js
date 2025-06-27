const WebSocket = require("ws");

const wss = new WebSocket.Server({ port: 6789 });
const agents = new Map();

console.log("🚀 WebSocket 服务器已启动，监听端口 6789");

wss.on("connection", (ws) => {
  ws.once("message", (message) => {
    const msg = message.toString();

    // ✅ 控制端请求在线设备列表
    if (msg === "controller:list") {
      const onlineAgents = Array.from(agents.keys());
      if (onlineAgents.length === 0) {
        ws.send("NO_AGENT");
      } else {
        ws.send(onlineAgents.join(","));
      }
      ws.close(); // 关闭连接，因为这个只用于获取列表
      return;
    }

    // ✅ 被控端连接
    if (msg.startsWith("agent:")) {
      const code = msg.split(":")[1];
      agents.set(code, ws);
      console.log(`✅ Agent [${code}] connected`);

      ws.on("close", () => {
        agents.delete(code);
        console.log(`🧹 Agent [${code}] disconnected`);
      });
    }

    // ✅ 控制端连接并指定控制某个 agent
    else if (msg.startsWith("controller:")) {
      const code = msg.split(":")[1];
      const agentWs = agents.get(code);
      console.log(`🎮 Controller requests access to Agent [${code}]`);

      if (!agentWs || agentWs.readyState !== WebSocket.OPEN) {
        ws.send("NO_AGENT");
        ws.close();
        return;
      }

      ws.send("CONNECTED");

      ws.on("message", (cmd) => {
        try {
          agentWs.send(cmd.toString());
          agentWs.once("message", (data) => {
            ws.send(data.toString());
          });
        } catch (err) {
          ws.send("ERROR");
        }
      });
    }
  });
});
