# 基本知识 原始知识,生命周期,JSON-RPC基础

> 在MCP之前的每一次集成都是一次性的. 模型语境协议,首次由安特罗皮在2024年11月发行,现在由Linux基金会的Agentic AI基金会管理,标准化发现和调用,以便任何客户端可以与任何服务器交谈. 2025-11-25规范命名了六个原始 (三个服务器,三个客户端),一个三阶段的生命周期和一个JSON-RPC 2.0线程格式. 了解这些,这阶段的MCP章节的其他部分将成为阅读.

**Type:** Learn
**Languages:** Python (stdlib, JSON-RPC parser)
**Prerequisites:** Phase 13 · 01 through 05 (the tool interface and function calling)
**Time:** ~45 minutes

## 学习目标

- 列出所有六种MCP原始 (服务器上的工具,资源,提示;根,采样,客户端上的引发) 并给出每个使用案例.
- 通过三个阶段的生命周期 (启动,运行,关闭) 进行查询,并表示每个阶段谁会发送哪个信息.
- 解析和发射JSON-RPC 2.0请求,响应和通知封.
- 解释哪些能力谈判`initialize`没有它,什么会破裂.

## 问题

在MCP之前,每个工具使用代理都有自己的协议.Cursor有一个MCP形状但不兼容的工具系统.Claude Desktop运输了不同的工具系统.VS Code的Copilot扩展有一个第三个.构建了"Postgres查询"工具的团队三次写出相同的工具,每个工具都输入到不同的主机的API.重复使用需要复制代码.

结果是布里亚的一次一体化爆炸,

通过标准化电线格式来解决这一问题. 每个MCP客户端都有一个MCP服务器:Cloade Desktop,ChatGPT,Cursor,VS Code,Gemini,Goose,Zed,Windsurf,到2026年4月300多个客户端.每月的SDK下载量为110万次. 10,000多个公共服务器.Linux基金会于2025年12月在新的Agentic AI基金会下担任管理员.

在此阶段使用的规格修改是**2025-11-25**增加了异步任务 (SEP-1686),URL模式调用 (SEP-1036),工具采样 (SEP-1577),增量范围同意 (SEP-835),以及OAuth 2.1资源指标语义.

## 概念

### 服务器原始的3个

1. **Tools.**调用式行动.从13期起相同的四步循环.
2. **Resources.**仅可读的内容,可以由URI来处理: `file:///path`现在`db://query/...`通过"自定义"
3. **Prompts.**复用模板. 服务器提供模板,客户端填写参数.

### 三个客户端原始

4. **Roots.**服务器可以接触到URI的集合. 客户端声明它们;服务器尊重它们.
5. **Sampling.**服务器要求客户端的模型完成. 启用服务器托管的代理循环,而没有服务器侧 API 密钥.
6. **Elicitation.**服务器在飞行中要求客户端的用户进行结构化输入. 形式或URL (SEP-1036).

 MCP 的每一个能力都属于其中一个.

### 电缆格式:JSON-RPC 2.0

每个消息都是包含这些字段的JSON对象:

- 要求:`{jsonrpc: "2.0", id, method, params}`现在,我们要去.
- 答案:`{jsonrpc: "2.0", id, result | error}`现在,我们要去.
- 通知:`{jsonrpc: "2.0", method, params}`没有`id`没有预期的反应.

基本规格有15种方法,由原始组组组组.

- `initialize`现在,`initialized`现在,我们要去做什么?
- `tools/list`现在`tools/call`
- `resources/list`现在`resources/read`现在`resources/subscribe`
- `prompts/list`现在`prompts/get`
- `sampling/createMessage`服务器到客户端
- `notifications/tools/list_changed`现在`notifications/resources/updated`现在`notifications/progress`

### 三阶段生命周期

**Phase 1: initialize.**

客户发送`initialize`它们的`capabilities`其他`clientInfo`服务器用自己的方式响应`capabilities`现在`serverInfo`客户端发送了`notifications/initialized`双方可以根据谈判能力发送请求.

**Phase 2: operation.**

客户的电话`tools/list`为了发现,`tools/call`服务器可能会发送`sampling/createMessage`如果它声明了该功能.`notifications/tools/list_changed`客户端可以发送`notifications/roots/list_changed`当用户改变根范围时.

**Phase 3: shutdown.**

任何一方都关闭了运输.MCP中没有结构性关闭方法;运输 (studio或 Streamable HTTP,阶段13 · 09) 携带了终端连接信号.

### 能力谈判

`capabilities`在`initialize`交手是合同.

```json
{
  "tools": {"listChanged": true},
  "resources": {"subscribe": true, "listChanged": true},
  "prompts": {"listChanged": true}
}
```

服务器表示可以发射`tools/list_changed`通知和支持`resources/subscribe`客户同意,并声明:

```json
{
  "roots": {"listChanged": true},
  "sampling": {},
  "elicitation": {}
}
```

如果客户不申报`sampling`服务器不得打电话`sampling/createMessage`交对称:如果服务器不声明`resources.subscribe`客户不得尝试签订.

没有支持采样的客户端仍然是有效的MCP客户端;一个不调用服务器`sampling`它们只是不使用这个功能在一起.

### 结构化内容和错误形状

`tools/call`返回一个`content`类型类块的数组: `text`现在`image`现在`resource`阶段13 · 14增加了MCP应用程序 (`ui://`互动UI) 加入该列表.

错误使用JSON-RPC错误代码. 规格定义的添加: `-32002`没有找到资源`-32603`内部错误,加上MCP特定错误数据`error.data`现在,我们要去.

### 客户端功能与工具呼叫详情

常见的混:`capabilities.tools`客户端是否支持工具列表变更通知.客户端是否会调用特定工具是运行时间选择,由其模型驱动,而不是能力旗.能力旗是规范级别合同.模型的选择是直角.

### 为什么要使用JSON-RPC而不是REST?

JSON-RPC 2.0 (2010) 是一个轻量级的双向协议.REST是客户端启动的.MCP需要服务器启动的消息 (样本,通知),因此JSON-RPC与其对称请求/响应形状是自然合适的.JSON-RPC也清洁地构建了studio和WebSocket/Streamable HTTP,而不重新发明HTTP的请求形状.

```figure
mcp-tool-call
```

## 用它

`code/main.py`通过JSON-RPC 2.0解析器和发射器,然后使用`initialize`其他`tools/list`其他`tools/call`其他`shutdown`通过手动测序,打印每一个信息. 没有真正的运输,只是信息的形状.

什么要看:

- `initialize`声明能力两方面;`serverInfo`其他`protocolVersion: "2025-11-25"`现在,我们要去.
- `tools/list`返回一个`tools`列;每个条目都有`name`现在`description`现在`inputSchema`现在,我们要去.
- `tools/call`使用`params.name`其他`params.arguments`现在,我们要去.
- 答案`content`是一个数组`{type, text}`子,子,子.

## 运送它

这一课产生了`outputs/skill-mcp-handshake-tracer.md`鉴于MCP客户端服务器互动的pcap式转录,技能注释每个消息,使用哪个原始,哪个生命周期阶段,以及它取决于哪个功能.

## 运动

1. 跑步`code/main.py`确定能力谈判发生的线程,并描述如果服务器不声明会发生什么变化`tools.listChanged`现在,我们要去.

2. 扩展解析器处理`notifications/progress`信息的形状:`{method: "notifications/progress", params: {progressToken, progress, total}}`放出它,而长时间`tools/call`确认客户端处理器会显示一个进展.

3. 阅读MCP 2025-11-25规格从上到下面. 整个文档大约80页. 确定大多数服务器都不需要的功能标志. 提示:它与资源订阅有关.

4. 草图在纸上原始的假设"cron工作"功能将属于. (提示:服务器希望客户端在预定的时间调用它.今天六个原始的任何一个都不适合.) MCP的2026路线图有一个SEP草案.

5. 从 GitHub 开放的 MCP 服务器解析一个会议日志. 计算请求与响应与通知消息. 计算流量的多少分量是生命周期与操作.

## 关键词

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| MCP | "Model Context Protocol" | Open protocol for model-to-tool discovery and invocation |
| Server primitive | "What a server exposes" | tools (actions), resources (data), prompts (templates) |
| Client primitive | "What a client lets servers use" | roots (scope), sampling (LLM callbacks), elicitation (user input) |
| JSON-RPC 2.0 | "The wire format" | Symmetric request/response/notification envelopes |
| `initialize` handshake | "Capability negotiation" | First message pair; servers and clients declare features they support |
| `tools/list` | "Discovery" | Client asks server for its current tool set |
| `tools/call` | "Invocation" | Client asks server to execute a tool with arguments |
| `notifications/*_changed` | "Mutation events" | Server tells client that its primitive list has changed |
| Content block | "Typed result" | `{type: "text" \| "image" \| "resource" \| "ui_resource"}` in tool result |
| SEP | "Spec Evolution Proposal" | Named draft proposal (e.g. SEP-1686 for async Tasks) |

## 进一步阅读

- [Model Context Protocol — Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25)法典规范文件
- [Model Context Protocol — Architecture concepts](https://modelcontextprotocol.io/docs/concepts/architecture)六原始的心理模型
- [Anthropic — Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol)2024年11月发射时间
- [MCP blog — First MCP anniversary](https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/)一年后期和2025年至25年间规格变化
- [WorkOS — MCP 2025-11-25 spec update](https://workos.com/blog/mcp-2025-11-25-spec-update)SEP-1686,1036,1577,835和1724的总结
