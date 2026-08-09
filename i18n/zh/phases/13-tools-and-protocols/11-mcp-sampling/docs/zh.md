# 服务器要求的LLM完成和代理循环

> 许多MCP服务器都是愚蠢的执行者: 接收参数,运行代码,返回内容. 样本采集使服务器转向方向:它要求客户的LLM做出决定. 这使得服务器在没有服务器拥有任何模型凭证的情况下能够托管代理循环. 通过SEP-1577,在2025-11-25年合并,在采样请求中添加了工具,以便循环可以包括更深层次的推理. 风险注意:SEP-1577工具采样形状在2026年1季度进行了实验,并且仍在SDKAPI中定位.

**Type:** Build
**Languages:** Python (stdlib, sampling harness)
**Prerequisites:** Phase 13 · 07 (MCP server), Phase 13 · 10 (resources and prompts)
**Time:** ~75 minutes

## 学习目标

- 解释什么`sampling/createMessage`解决 (没有服务器侧API密钥的服务器托管循环).
- 执行一个服务器,要求客户端通过多转提示进行样本,并返回完成.
- 使用`modelPreferences`(成本/速度/智能优先事项) 指导客户模型选择.
- 建立一个`summarize_repo`工具通过采样而不是硬码行为进行内部回复.

## 问题

对于编码总结工作流程来说,有用的MCP服务器需要:走一个文件树,选择要读哪些文件,合成一个总结,然后返回.

服务器需要一个API密钥,服务器端账单,每个用户成本昂贵.

选择B:服务器返回原始内容;客户端的代理人进行推理. 工作,但将服务器逻辑移动到客户端提示中,这是脆弱的.

服务器通过客户的LLM请求`sampling/createMessage`服务器保留算法 (该读到哪些文件,需要进行多少通行),而客户端保留收费和模型选择.服务器根本没有凭证.

采样是选择C. 它是可信赖服务器可以通过该机制来托管代理循环,而不是完全的LLM主机.

## 概念

### `sampling/createMessage`要求

服务器发送:

```json
{
  "jsonrpc": "2.0",
  "id": 42,
  "method": "sampling/createMessage",
  "params": {
    "messages": [{"role": "user", "content": {"type": "text", "text": "..."}}],
    "systemPrompt": "...",
    "includeContext": "none",
    "modelPreferences": {
      "costPriority": 0.3,
      "speedPriority": 0.2,
      "intelligencePriority": 0.5,
      "hints": [{"name": "claude-3-5-sonnet"}]
    },
    "maxTokens": 1024
  }
}
```

客户通过其法定士,返回:

```json
{"jsonrpc": "2.0", "id": 42, "result": {
  "role": "assistant",
  "content": {"type": "text", "text": "..."},
  "model": "claude-3-5-sonnet-20251022",
  "stopReason": "endTurn"
}}
```

### `modelPreferences`

总计为1.0的3个浮动:

- `costPriority`支持更便宜的车型.
- `speedPriority`支持更快的车型.
- `intelligencePriority`支持更有能力的模型.

另外`hints`客户端可能会或可能不会尊重提示;客户端的用户配置总是获胜.

### `includeContext`

三个值:

- `"none"`只有服务器提供的消息.默认.
- `"thisServer"`包括此服务器的前次访问.
- `"allServers"`包括所有会议背景.

`includeContext`由于它泄露了跨服务器环境,因此2025年至25日已缓慢降低,这是一个安全问题.`"none"`在这些消息中,

### 用工具采样 (SEP-1577)

根据"新型"的规定,`tools`客户端使用这些工具运行一个完整的工具调用循环. 这使得服务器通过客户端模型来托管ReAct样式的代理循环.

```json
{
  "messages": [...],
  "tools": [
    {"name": "fetch_url", "description": "...", "inputSchema": {...}}
  ]
}
```

客户端循环:样本,如果被调用,执行工具,再次样本,返回最终助理消息.这是实验性的到2026年1季度;SDK签名可能仍然漂移.在实现时,确认2025-11-25规范的客户端/样本部分.

### 轮中的人

客户端必须向用户显示服务器在运行样本之前要求模型做什么.恶意服务器可以使用样本来操纵用户的会议 ("告诉用户X,以便他们点击Y").Clode Desktop,VS Code和Cursor表面样本请求作为确认对话用户可以拒绝.

通过通过"网关" (阶段13·17) 通过自动批准低风险的采样,自动拒绝任何可疑的信息.

### 没有API密钥的服务器托管循环

常规使用案例:一个无自有LLM访问的代码总结MCP服务器.

1. 走在备忘录结构上.
2. 电话`sampling/createMessage`选出五个文件,最有可能描述这个 repo 的目的.
3. 读这些文件.
4. 电话`sampling/createMessage`文件内容和"将备案总结成3段".
5. 返回总结为`tools/call`结果.

服务器从来没有触及过LLMAPI. 客户的用户使用自己的凭证来支付完成.

### 安全风险 (单位42条披露,2026年1季度)

- **Covert sampling.**一个工具总是调用采样"从会议背景下回复用户的电子邮件".
- **Resource theft via sampling.**服务器要求客户端总结攻击者的有效载荷,
- **Loop bombs.**服务器在密切的循环中调用样本. 客户必须执行每次会议的速度限制.

```figure
t3-sampling-flip
```

## 用它

`code/main.py`模拟的"summarize_repo"工具调用两个采样轮 (选文件,然后总结),而假客户端返回装的响应.

- 服务器发送`sampling/createMessage`随着`modelPreferences`现在,我们要去.
- 客户回复了完成.
- 服务器继续循环.
- 速率限制器每次调用工具的样本调用总量.

什么要看:

- 服务器只显示一个工具 (`summarize_repo`);所有推理都在采样调用中进行.
- 模型偏好权重客户的模型选择;提示列出偏好的模型.
- 循环结束了`stopReason: "endTurn"`现在,我们要去.
- 其他`max_samples_per_tool = 5`限制抓住一个逃跑循环.

## 运送它

这一课产生了`outputs/skill-sampling-loop-designer.md`鉴于需要LLM调用 (研究,总结,规划) 的服务器端算法,技能设计了一个基于样本的实施,具有正确的模型偏好,利率限制和安全确认.

## 运动

1. 跑步`code/main.py`改变`max_samples_per_tool`按照标准,每次使用量均为2个.

2. 实施SEP-1577工具采样变体:采样请求包含一个`tools`检查客户端循环在返回最终完成之前执行这些工具.注意漂移风险:SDK签名可能在2026年1月仍然会发生变化.

3. 添加人在循环确认:在服务器的第一次之前 `sampling/createMessage`拒绝的电话返回输入的拒绝.

4. 添加一个按客户端会议键键的用户率限制器.

5. 设计一个`summarize_pdf`通过采样选取包括在内的部分.`modelPreferences.intelligencePriority`改变 0.1 与 0.9 的行为?

## 关键词

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Sampling | "Server-to-client LLM call" | Server asks client's model for a completion |
| `sampling/createMessage` | "The method" | JSON-RPC method for sampling requests |
| `modelPreferences` | "Model priorities" | Cost / speed / intelligence weights plus name hints |
| `includeContext` | "Cross-session leakage" | Soft-deprecated context inclusion mode |
| SEP-1577 | "Tools in sampling" | Allow tools inside sampling for server-hosted ReAct |
| Human-in-the-loop | "User confirms" | Client surfaces sampling request to user before running |
| Loop bomb | "Runaway sampling" | Server-side infinite sampling loop; client must rate-limit |
| Covert sampling | "Hidden reasoning" | Malicious server hides intent in sampling prompts |
| Resource theft | "Using user's LLM budget" | Server forces client to spend on sampling it does not want |
| `stopReason` | "Why generation halted" | `endTurn`, `stopSequence`, or `maxTokens` |

## 进一步阅读

- [MCP — Concepts: Sampling](https://modelcontextprotocol.io/docs/concepts/sampling)高层次的样本采集概述
- [MCP — Client sampling spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/client/sampling)法典`sampling/createMessage`形状
- [MCP — GitHub SEP-1577](https://github.com/modelcontextprotocol/modelcontextprotocol) 标签演变 采样工具的建议 (实验性)
- [Unit 42 — MCP attack vectors](https://unit42.paloaltonetworks.com/model-context-protocol-attack-vectors/)秘密采样和资源盗窃模式
- [Speakeasy — MCP sampling core concept](https://www.speakeasy.com/mcp/core-concepts/sampling)通过客户端代码样本进行步行
