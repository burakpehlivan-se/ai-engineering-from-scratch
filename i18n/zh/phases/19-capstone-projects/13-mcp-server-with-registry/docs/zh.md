#                   

> 模拟语境协议不再是未来,并成为2026年默认的工具使用规范.安тропо,OpenAI,谷歌以及每个主要的IDE运输MCP客户端.Pinterest发布了其内部MCP服务器生态系统.AAIF注册表正式化了功能元数据在`.well-known`. AWS ECS 发布了参考无状态部署.Block的代理将相同的协议放入一个托管助理中.2026年生产形式是: StreamableHTTP 运输,OAuth 2.1 范围,OPA 政策门户和一个登记库,允许平台团队发现,验证和启用服务器.

**Type:** Capstone
**Languages:** Python (server, via FastMCP) or TypeScript (@modelcontextprotocol/sdk), Go (registry service)
**Prerequisites:** Phase 11 (LLM engineering), Phase 13 (tools and MCP), Phase 14 (agents), Phase 17 (infrastructure), Phase 18 (safety)
**Phases exercised:**子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子子
**Time:** 25 hours

## 问题

工会成为工具使用的语言. 克劳德代码,Cursor 3,Amp,OpenCode,双胞胎CLI,以及所有管理代理现在都使用MCP服务器. 生产挑战不是创建服务器 (FastMCP使得很容易),而是根据企业要求进行规模部署:每个租户的OAuth范围,破坏性工具的OPA政策, StreamableHTTP无状态扩展,发现的注册表,每个工具调用的审计日志. 讯内部的MCP生态系统和AAIF注册表规格设定了2026年.

您将构建一个MCP服务器,将暴露10个内部工具 (仅读后格雷斯,S3列表,Jira,线性,数据库等),一个平台发现的注册表UI,以及破坏性工具的人类批准门.负载测试显示了 StreamableHTTP水平扩展.审计轨道满足了企业安全审查.

## 概念

MCP 2026 修订要求 StreamableHTTP 作为默认运输.与之前的 stdio-and-SSE 形式不同, StreamableHTTP 默认无状态:单个 HTTP 终端点接受JSON-RPC 请求,流回应,并支持长期的通讯连接.无状态意味着负载平衡器背后可水平扩展.

授权是OAuth 2.1 每个工具的范围.`jira:read`现在`s3:list`现在`postgres:query:readonly`对于高风险工具,服务器拒绝任何未提高到 范围的电话.`approved:by:human`在最后N分钟内, 这个升高来自 Slack 审查卡.

每个MCP服务器都会暴露一个`.well-known/mcp-capabilities`文件包含工具表,运输URL,作者要求. 注册表调查,验证和索引.平台团队使用注册表UI来查看有哪些工具,需要哪些范围,以及哪些团队拥有它们.

## 建筑

```
MCP client (Claude Code, Cursor 3, ...)
          |
          v
StreamableHTTP over HTTPS (JSON-RPC + streaming)
          |
          v
MCP server (FastMCP) behind load balancer
          |
   +------+------+---------+----------+------------+
   v             v         v          v            v
Postgres    S3 listing  Jira       Linear     Datadog
(read-only) (paged)     (read)     (read)     (query)
          |
   +------+-------------+
   v                    v
 OPA policy gate   destructive tool MCP (separate server)
                        |
                        v
                   human approval via Slack
                        |
                        v
                   audit log (append-only, per-tenant)

  registry service
     |
     v  GET /.well-known/mcp-capabilities from each server
     v
     UI: search / validate / enable-disable / ownership
```

## 堆

- 服务器框架:FastMCP (Python) 或 `@modelcontextprotocol/sdk`现在,我们要做什么?
- 运输:通过HTTPS (无状态) 流通HTTP
- 通过SPIFFE/SPIRE提供工作负载身份的OAuth 2.1
- 政策:每工具的OPPA/RegO规则;每请求的政策决策服务
- 登记:自主托管,消费`.well-known/mcp-capabilities`标签
- 人类批准:用于破坏性工具的交互式信息
- 部署:AWS ECS Fargate或 Fly.io,每租户一个服务器或共享租户范围
- 审计:每次调用时的结构化JSONL单租户桶

```figure
cf-mcp-gate
```

## 建立它

1. **Tool surface.**展示10个内部工具:Postgres仅阅读查询,S3列表对象,Jira搜索/搜索,线性搜索/搜索,Datadog测量查询,PagerDuty在调用查询,GitHub仅阅读,Notion搜索,Slack搜索,Salesforce阅读.每个工具都有打字式方案和范围标签.

2. **FastMCP server.**装备工具,配置流通HTTP运输,添加中级软件用于OAuth代币内检查和范围执行.

3. **OPA policy.**工具的规则:哪些范围允许调用,哪些 PII 编辑适用,哪些有效载荷尺寸限制适用.

4. **Registry service.**单独的Go或TS服务,`.well-known/mcp-capabilities`通过JSON Schema验证,并显示一个清单/搜索/验证/禁用UI.

5. **Capability manifest.**每个服务器都会暴露`.well-known/mcp-capabilities`包含:工具列表,作者要求,运输URL,所有者团队,SLO.

6. **Destructive tool separation.**转变状态的工具 (Jira create, Linear create, Postgres write) 在第二个MCP服务器上使用更严格的 auth流:代币必须具有一个`approved:by:human`通过Slack卡在15分钟内提高范围.

7. **Audit log.**仅添加JSONL每租户: `{timestamp, user, tool, args_redacted, response_redacted, outcome}`报纸前通过普雷西迪奥编辑.

8. **Load test.**在 StreamableHTTP 上,可同时使用100个客户端.通过添加第二个复制品来展示水平扩展;显示负载平衡器在没有会议粘性的情况下重新分配.

9. **Conformance tests.**运行官方MCP合规套件对两个服务器进行运行.

## 用它

```
$ curl -H "Authorization: Bearer eyJhbGc..." \
       -X POST https://mcp.internal.example.com/ \
       -d '{"jsonrpc":"2.0","method":"tools/call",
            "params":{"name":"postgres.readonly","arguments":{"sql":"SELECT 1"}}}'
[registry]   capability validated: postgres.readonly v1.2
[policy]    scope postgres:query:readonly present; allowed
[audit]     logged: user=u42 tool=postgres.readonly outcome=ok
response:    { "result": { "rows": [[1]] } }
```

## 运送它

`outputs/skill-mcp-server.md`描述产品. 具有OAuth 2.1 范围和OPA 门户的内部工具的生产级MCP服务器+注册表+审计层.

| Weight | Criterion | How it is measured |
|:-:|---|---|
| 25 | Spec conformance | StreamableHTTP + capability manifest passes MCP conformance tests |
| 20 | Security | Scope enforcement, OPA coverage across every tool, secret hygiene |
| 20 | Observability | Per-tool-call audit log with PII redaction |
| 20 | Scale | 100-client load test horizontal scale demonstration |
| 15 | Registry UX | Discover / validate / enable-disable workflow |
| **100** | | |

## 运动

1. 添加一个新工具 (Confluence搜索). 通过注册表验证流,而不需要触摸核心服务器.

2. 编写一个OPA政策,编辑包含命名列的Postgres查询结果`email`现在`ssn`其他`phone`练习探测器查询.

3. 根据本地延迟的标准, 流动HTTP与studio. 每次通话报告 p50/p95.

4. 实施每租户配额:每租户每工具每分钟最多的N通话.通过第二个OPA规则执行.

5. 从 运行MCP 合规套件[mcp-conformance-tests](https://github.com/modelcontextprotocol/conformance)修复每一个失败.

## 关键词

| Term | What people say | What it actually means |
|------|-----------------|------------------------|
| StreamableHTTP | "2026 MCP transport" | Stateless HTTP + streaming; replaces SSE + stdio for networked servers |
| Capability manifest | "Well-known doc" | `.well-known/mcp-capabilities` with tool list, auth, transport URL |
| OPA / Rego | "Policy engine" | Open Policy Agent for authorizing tool calls against external rules |
| Scope elevation | "Approved-by-human" | Short-lived scope granted via Slack approval, required for destructive tools |
| Registry | "Tool discovery" | Service that indexes MCP servers from their capability manifests |
| Workload identity | "SPIFFE / SPIRE" | Cryptographic service identity for OAuth token issuance |
| Conformance suite | "Spec tests" | Official MCP test battery for StreamableHTTP + tool manifest correctness |

## 进一步阅读

- [Model Context Protocol 2026 Roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)流式HTTP,功能元数据,注册表
- [AAIF MCP Registry spec](https://github.com/modelcontextprotocol/registry)2026年登记规范
- [AWS ECS reference deployment](https://aws.amazon.com/blogs/containers/deploying-model-context-protocol-mcp-servers-on-amazon-ecs/)参考生产部署
- [Pinterest internal MCP ecosystem](https://www.infoq.com/news/2026/04/pinterest-mcp-ecosystem/)参考内部部署
- [Block `goose` MCP usage](https://block.github.io/goose/)参考药物消费模式
- [FastMCP](https://github.com/jlowin/fastmcp) Python 服务器框架
- [Open Policy Agent](https://www.openpolicyagent.org/)政策引擎参考
- [SPIFFE / SPIRE](https://spiffe.io)工作负载身份参考
