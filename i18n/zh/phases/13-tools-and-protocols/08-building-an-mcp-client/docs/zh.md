# 建立一个MCP客户端 发现,调用,会议管理

> 许多MCP内容都会提供服务器教程, 客户端代码是硬管的所在:过程产,能力谈判,多个服务器中的工具列表合并,采样回调,重连接和命名空间碰撞解决方案. 这一课程建立了一个多服务器客户端,将三个不同的MCP服务器升级到一个模型的平坦工具名字空间.

**Type:** Build
**Languages:** Python (stdlib, multi-server MCP client)
**Prerequisites:** Phase 13 · 07 (building an MCP server)
**Time:** ~75 minutes

## 学习目标

- 作为一个子程序,完成一个MCP服务器.`initialize`发送一个`notifications/initialized`现在,我们要去.
- 保持每个服务器的会议状态 (功能,工具列表,最后一次见到的通知ID).
- 通过碰撞处理将多个服务器的工具列表合并到一个名字空间中.
- 调用工具调用到拥有它的服务器,并重新组装响应.

## 问题

一个真正的代理主机 (Claude Desktop,Cursor,Goose,Gemini CLI) 一次加载多个MCP服务器.用户可能同时运行文件系统服务器,Postgres服务器和GitHub服务器.客户端的工作:

1. 起每个服务器.
2. 握手,独立地握手.
3. 电话`tools/list`它们每次都会平.
4. 当模型发射时`notes_search`在合并的名称空间中查看,然后向正确的服务器.
5. 处理任何服务器的通知 (`tools/list_changed`) 没有阻.
6. 运输故障时重新连接.

官方 SDK 包装了这,但心理模型必须是你的.

## 概念

### 婴儿过程的繁殖

`subprocess.Popen`随着`stdin=PIPE, stdout=PIPE, stderr=PIPE`设置`bufsize=1`通过使用文字模式进行线条阅读.每个服务器是一个进程;客户端拥有一个进程.`Popen`按服务器处理.

### 服务器每次会议状态

`Session`每个服务器的对象包含:

- `process`  的手柄.
- `capabilities`服务器在什么时候宣布`initialize`现在,我们要去.
- `tools`最后一个`tools/list`结果.
- `pending` 要求ID的地图到一个答复的承诺/未来等待.

要求本质上是非同步的;`tools/call`服务器B在调用中时不能阻止.要么使用配列或无同步的线程.

### 合并名称空间

当客户端看到集成工具列表时,名称可能会碰撞.两个服务器可能都会暴露`search`客户有三个选择:

1. **Prefix by server name.** `notes/search`现在`files/search`清晰但丑.
2. **Silent first-come.**后来的服务器`search`危险,隐藏碰撞.
3. **Collision rejection.**拒绝加载第二个服务器,请通知用户.

克劳德桌面使用前按服务器. 客使用明显错误的碰撞拒绝. VS Code MCP也采用前按服务器.

### 路由

合并后,一个发送表图`tool_name -> session`模型以名字发出电话;客户找到会议并写出一个`tools/call`传递给服务器的SDDIN,然后等待响应.

### 采样回调

如果服务器声明了`sampling`能力`initialize`它们可能会发送`sampling/createMessage`要求客户运营其法定律师事务所.

1. 阻止对该服务器的进一步请求,直到样本解决,或如果其实现支持同步,则将其运输.
2. 打电话给其法学执法机构.
3. 发送回应到服务器.

课程11涉及到端到端采样.

### 通知处理

`notifications/tools/list_changed`意思是重新调用`tools/list`现在,我们要去.`notifications/resources/updated`通知不得产生回应 不要试图对资源进行回复.

常见客户端错误: 封锁读取循环`tools/call`通过一个背景读者线程将每个消息推到排队中; 主线程将排队和发送.

### 连接

运输可能失败:服务器故障,操作系统失效,工作室管道破裂. 客户端在工作室停机时检测到EOF,并将会话处理为已关闭.

- 默默重新启动服务器,再握手.
- 对于可见用户的状态服务器,可以.

第13期 · 09期涵盖了流式HTTP连接语义;stdio更简单.

### 保持者和会议身份证

流式 HTTP 使用一个`Mcp-Session-Id`工作室没有会议 ID 过程身份是会议.保持是可选的;工作室管道不会在无活动下断裂.

```figure
tp-client-merge
```

## 用它

`code/main.py`通过使用MCP服务器,它将三个模拟MCP服务器作为子进程,每个服务器都握手,并将其工具列表合并,并将工具调用到右边. "服务器"实际上是其他 Python 进程运行玩具响应器 (没有真正的LLM).运行它来看:

- 首先,我们要做一个小程序.
- 三个`tools/list`结果将其合并成一个7工具名称空间.
- 根据工具名称进行路由决定.
- 由于名称空间的前置,被防止碰撞.

什么要看:

- 其他`Session`数据类保持每服务器状态清洁.
- 背景读者线程在不阻断主线程的情况下,将每条线程排列出来.
- 发送表是简单的`dict[str, Session]`现在,我们要去.
- 碰撞处理是明确的:当两个服务器宣布相同的名字时,后者将以前命名.

## 运送它

这一课产生了`outputs/skill-mcp-client-harness.md`由于MCP服务器 (名称,命令,args) 的声明列表,技能产生了一个带,产生它们,并合并工具列表,并发送具有碰撞分辨率的路由功能.

## 运动

1. 跑步`code/main.py`通过SIGTERM杀死一个模拟的服务器进程,观察客户端如何检测到EOF,

2. 执行名字空间前置. 当两个服务器暴露`search`改名第二个为`<server>/search`更新发送表,并正确验证工具调用路线.

3. 连接池式备份将服务器重启:在连续故障时,按指数重复,限30秒,在三次故障后发送通知给用户.

4. 绘制一个支持100个同时MCP服务器的客户端. 什么数据结构取代了简单的发送命令? (提示:为前名区间的试用,加上为工具数量为服务器的指标).

5. 导航客户端到官方的MCP Python SDK.`stdio_client`其他`ClientSession`代码应该从200行缩小到40行,同时保持多服务器路由.

## 关键词

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| MCP client | "The agent host" | Process that spawns servers and orchestrates tool calls |
| Session | "Per-server state" | Capabilities, tool list, and pending-request bookkeeping |
| Merged namespace | "One tool list" | Flat set of tool names across all active servers |
| Namespace collision | "Two servers same tool" | Client must prefix, reject, or first-come the duplicate |
| Routing | "Who gets this call?" | Dispatch from tool name to owning server |
| Background reader | "Non-blocking stdout" | Thread or task that drains server stdout into a queue |
| Sampling callback | "LLM-as-a-service" | Client handler for `sampling/createMessage` from server |
| `notifications/*_changed` | "Primitive mutated" | Signal the client must re-discover or re-read |
| Reconnection policy | "When server dies" | Restart semantics when transport fails |
| Stdio session | "Process = session" | No session id; child process lifetime is the session |

## 进一步阅读

- [Model Context Protocol — Client spec](https://modelcontextprotocol.io/specification/2025-11-25/client) 客户行为
- [MCP — Quickstart client guide](https://modelcontextprotocol.io/quickstart/client)使用Python SDK的好世界客户端教程
- [MCP Python SDK — client module](https://github.com/modelcontextprotocol/python-sdk)参考`ClientSession`其他`stdio_client`
- [MCP TypeScript SDK — Client](https://github.com/modelcontextprotocol/typescript-sdk) TS平行
- [VS Code — MCP in extensions](https://code.visualstudio.com/api/extension-guides/ai/mcp)如何VS Code在一个编辑器主机中多个MCP服务器
