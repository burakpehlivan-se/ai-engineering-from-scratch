#  构建一个完整的工具生态系统

> 阶段13教了每一个部分.这个结尾石将它们连接到一个生产形状的系统:一个具有工具+资源+提示+任务+UI的MCP服务器,边缘的OAuth 2.1,一个RBAC门户端,一个多服务器客户端,一个A2A子代理调用,OTel追踪到收藏器,CI中工具中毒检测,以及一个 AGENTS.md + SKILL.md捆绑.到最后,你可以捍卫每个建筑选择.

**Type:** Build
**Languages:** Python (stdlib, end-to-end ecosystem harness)
**Prerequisites:** Phase 13 · 01 through 21
**Time:** ~120 minutes

## 学习目标

- 编写一个MCP服务器,用一个 `ui://`应用程序.
- 通过OAuth 2.1网关,执行RBAC和嵌哈希.
- 写一个多服务器客户端,它可以跟踪OTel GenAI属性端到端.
- 转移部分工作负载到A2A子代理;检查不透明度保持.
- 包装整个堆用 AGENTS.md + SKILL.md,以便其他代理人可以驾驶它.

## 问题

运输"研究和报告"系统:

- 用户问:"要概括2026年最受引用的三篇关于代理协议的 arXiv 论文.
- 系统:通过MCP搜索 arXiv;通过A2A向专业的作家代理委托论文总结;汇总结果;作为MCP应用程序呈现互动报告`ui://`资源;记录每一步到OTel.

这不是一个玩具生产研究辅助系统,在2026年由安тропо (Claude Research产品),OpenAI (GPTs with Apps SDK) 发送,第三方拥有这种形状.

## 概念

### 建筑

```
[user] -> [client] -> [gateway (OAuth 2.1 + RBAC)] -> [research MCP server]
                                                      |
                                                      +- MCP tool: arxiv_search (pure)
                                                      +- MCP resource: notes://recent
                                                      +- MCP prompt: /research_topic
                                                      +- MCP task: generate_report (long)
                                                      +- MCP Apps UI: ui://report/current
                                                      +- A2A call: writer-agent (tasks/send)
                                                      |
                                                      +- OTel GenAI spans
```

### 痕迹等级

```
agent.invoke_agent
 ├── llm.chat (kick off)
 ├── mcp.call -> tools/call arxiv_search
 ├── mcp.call -> resources/read notes://recent
 ├── mcp.call -> prompts/get research_topic
 ├── a2a.tasks/send -> writer-agent
 │    └── task transitions (opaque internals)
 ├── mcp.call -> tools/call generate_report (task-augmented)
 │    └── tasks/status polling
 │    └── tasks/result (completed, returns ui:// resource)
 └── llm.chat (final synthesis)
```

每个跨度都有权利`gen_ai.*`它们的属性.

### 安全姿势

- 通过 OAuth 2.1 + PKCE,将资源指标将观众固定在网关上.
- 网关保留上游的凭证;用户从来没有看到它们.
-  `alice`没有`research:read`现在`research:write`能调用所有的工具.`bob`没有`research:read`没有电话.`generate_report`现在,我们要去.
- 嵌描述表:任何工具哈希变化的服务器都丢弃了.
- 审计第二规则:没有工具结合不值得信赖的输入,敏感数据和后续行动.

### 染

最后一个`generate_report`任务返回内容块加上一个`ui://report/current`资源.客户端的主机 (Claude Desktop等) 在沙盒iframe中将互动仪表板呈现出来.仪表板包含一个排序的纸质列表,引用数量和调用按.`host.callTool('summarize_paper', {arxiv_id})`对于用户点击的任何文件.

### 包装

整个东西是这样的:

```
research-system/
  AGENTS.md                     # project conventions
  skills/
    run-research/
      SKILL.md                  # the top-level workflow
  servers/
    research-mcp/               # the MCP server
      pyproject.toml
      src/
  agents/
    writer/                     # the A2A agent
  gateway/
    config.yaml                 # RBAC + pinned manifest
```

用户使用`docker compose up`克劳德代码,Cursor,Codex和OpenCode用户可以使用使用Code 系统.`run-research`能做到.

### 每个13期课程都为什么贡献

| Lesson | What the capstone uses |
|--------|------------------------|
| 01-05 | Tool interface, provider-portability, parallel calls, schemas, linting |
| 06-10 | MCP primitives, server, client, transports, resources + prompts |
| 11-14 | Sampling, roots + elicitation, async tasks, `ui://` apps |
| 15-17 | Tool poisoning, OAuth 2.1, gateway + registry |
| 18 | A2A sub-agent delegation |
| 19 | OTel GenAI tracing |
| 20 | Routing gateway for the LLM layer |
| 21 | SKILL.md + AGENTS.md packaging |

```figure
t3-capstone-chain
```

## 用它

`code/main.py`通过使用此方法,它将前课程的模式成一个可运行的演示.所有stdlib,所有在流程中,以便您可以读到它端到端.它运行研究和报告场景的全部流量:握手与网关,OAuth 2.1模拟,工具/列表合并,生成_报告作为任务,A2A调用作者, ui://资源返回,OTel范围发射.

什么要看:

- 每次跳跃都会有一个追踪身份证.
- 通过网关的政策阻止第二个用户写作.
- 任务生命周期继续工作 →完成,并返回文本和 ui://内容.
- 对于管家来说,A2A电话的内部状态是不透明的.
- 其他代理人需要复制工作流程的唯一文件是 AGENTS.md 和 SKILL.md.

## 运送它

这一课产生了`outputs/skill-ecosystem-blueprint.md`鉴于产品需求 (研究,总结,自动化),技能产生了完整的架构:哪些MCP原始,哪些门户控制,哪些A2A调用,哪些远程测量,哪些包装.

## 运动

1. 跑步`code/main.py`记住单个痕迹的标识和如何扩展巢. 计算在第13阶段的原始人触摸多少.

2. 扩展演示:添加第二个后端MCP服务器 (例如 `bibliography`) 并确认网关将其工具融入同一名字空间.

3. 换一个真实的A2A编写代理,用一个副过程.

4. 在调整器和LLM之间的路由门口中添加 PII编辑步骤.

5. 写一个AGENTS.md给一个队友来维护这个系统. 这应该花不到五分钟阅读,

## 关键词

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Capstone | "Phase-13 integration demo" | End-to-end system using every primitive |
| Research and report | "The scenario" | Search, summarize, render pattern |
| Ecosystem | "All the pieces together" | Server + client + gateway + sub-agent + telemetry + package |
| Trace hierarchy | "Single trace id" | Every hop's span shares the trace; parent-child via span ids |
| Gateway-issued token | "Transitive auth" | Client sees only gateway's token; gateway holds upstream creds |
| Merged namespace | "All tools in one flat list" | Multi-server merge at the gateway, prefix-on-collision |
| Opacity boundary | "A2A call hides internals" | Sub-agent's reasoning invisible to orchestrator |
| Three-layer stack | "AGENTS.md + SKILL.md + MCP" | Project context + workflow + tools |
| Defense-in-depth | "Multiple security layers" | Pinned hashes, OAuth, RBAC, Rule of Two, audit log |
| Spec compliance matrix | "What we ship that the spec requires" | Checklist mapping deliverables to 2025-11-25 requirements |

## 进一步阅读

- [MCP — Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) 集成参考
- [MCP blog — 2026 roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)协议的方向
- [a2a-protocol.org](https://a2a-protocol.org/latest/) A2A v1.0 参考
- [OpenTelemetry — GenAI semconv](https://opentelemetry.io/docs/specs/semconv/gen-ai/)可信追踪公约
- [Anthropic — Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)生产代理运行时间模式
