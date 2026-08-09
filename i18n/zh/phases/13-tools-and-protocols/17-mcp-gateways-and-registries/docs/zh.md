# 企业控制机

> 企业不能让每个开发人员安装随机MCP服务器. 网关集中 auth,RBAC,审计,速度限制,缓存和工具中毒检测,然后将合并的工具表面作为一个单一的MCP终端点. 官方MCP注册表 (Anthropic + GitHub + PulseMCP + Microsoft,名称空间验证) 是正规的上游. 这一课标明了一个门口适合哪里, 进行最小的实施,

**Type:** Learn
**Languages:** Python (stdlib, minimal gateway)
**Prerequisites:** Phase 13 · 15 (tool poisoning), Phase 13 · 16 (OAuth 2.1)
**Time:** ~45 minutes

## 学习目标

- 解释MCP门口位于哪里 (MCP客户端和多个后端MCP服务器之间).
- 执行五个关口责任:Auth,RBAC,审计,利率限制,政策.
- 强制在门口层上执行一个固定的工具-哈什宣言.
- 区分官方MCP注册表与元注册表 (Glama,MCPMarket,MCP.so,Smithery,LobeHub).

## 问题

财富500强公司拥有30个经批准的MCP服务器,5000个开发人员,合规和审计要求,以及一个想要集中政策的安全团队.

门口模式:

1. 网关运行时,一个流向HTTP终端开发人员连接到.
2. 网关为每个后端MCP服务器提供了凭证.
3. 通过网关的 OAuth,每个开发者请求都会得到认证和范围.
4. 网关将调用到后端服务器,
5. 所有的电话都记录在审计中.

云飞云MCP门户,康格AI门户,IBM ContextForge,MintMCP,TrueFoundry,发送AI门户所有门户或门户功能在2025-2026年发送.

与此同时,官方MCP注册表作为正规上游系统启动:由策划,命名空间验证,反向DNS命名的服务器,门户端可以从中获取.

## 概念

### 五个门户责任

1. **Auth.**开发人员的身份;用户角色的地图.
2. **RBAC.**用户政策:哪些服务器,哪些工具,哪些范围.
3. **Audit.**每次电话都记录了谁,什么,什么时候的结果.
4. **Rate limit.**防止滥用.
5. **Policy.**拒绝有毒描述,执行第二规则,编辑PII.

### 作为一个终点的门口

开发人员认为,网关看起来像一个MCP服务器.内部,它路由到N后端. 会议ID (阶段13 · 09) 在边界重写.

### 凭证的跳转

开发人员从来没有看到后端代币.网关保留它们 (或向身份提供商提供代理).`notes:read`在网关上可以通过网关自己的后端凭证过渡访问注释MCP服务器,但只在将过渡访问绑定的政策下.

### 工具在门口

网关包含批准的工具描述表 (SHA256哈希).在发现时,它将每个后端的数据传输到`tools/list`通过将哈希与表格进行比较,并删除任何描述发生突变的工具.这是从第13 · 15阶段中央应用的地毯拉防御.

### 政策作为代码

通过 OPA/Rego,Kyverno或Styra,先进的网关表达政策.`alice`可能会打电话`github.open_pr`只有在 org 里存放`acme`简单的网关使用手编码的Python.

### 会议意识的路由

当用户的会议包含服务器的混合,网关多重:开发者的单个MCP会议会举行N后端会议,每个服务器每次一次.通过网关到开发者的会议的任何后端路线的通知.

### 名称空间合并

网关将所有后端的工具名字空间合并,通常是使用前置在碰撞上. `github.open_pr`现在`notes.search`这使得路由无误.

### 登记

- **Official MCP Registry (`registry.modelcontextprotocol.io`).**根据人类,GitHub,PulseMCP,微软的管理启动.`io.github.user/server`) 预先过以达到基本质量.
- **Glama.**搜索中心的地表,汇集了许多来源.
- **MCPMarket.**商业化目录,有供应商的列表.
- **MCP.so.**公共目录;公开提交
- **Smithery.**包装管理器式安装流量
- **LobeHub.**在他们的LoboChat应用程序中,

企业网关默认地从官方注册表中拉出,允许管理员从地表注册表中进行添加,并拒绝任何未支持的东西.

### 逆向DNS命名

官方登记处要求公共服务器的反向DNS名称: `io.github.alice/notes`名称空间防止着,使信任委托更清楚.

### 供应商调查,2026年4月

| Vendor | Strength |
|--------|----------|
| Cloudflare MCP Portals | Edge-hosted; OAuth integrated; free tier |
| Kong AI Gateway | K8s-native; fine-grained policy; logs to OpenTelemetry |
| IBM ContextForge | Enterprise IAM; compliance; audit export |
| TrueFoundry | DevOps-leaning; metrics-first |
| MintMCP | Developer-platform oriented |
| Envoy AI Gateway | Open-source; customizable filters |

第17阶段 (生产基础设施) 进一步深入研究门户运营.

```figure
t3-gateway-funnel
```

## 用它

`code/main.py`通过假的 Bearer 代币验证用户,按用户的 RBAC 政策进行验证,向两个后端 MCP 服务器传输请求,将每次调用写入审计日志,执行一个利率限制,并拒绝任何后端工具,其描述哈希不匹配的嵌表.

什么要看:

- `RBAC`按键键编写`user_id`允许的`server_tool`其他信息
- `AUDIT_LOG`只是一个附加事件列表.
- 利率限制使用每用户的代币桶.
- 印的表格是说法`server::tool -> hash`现在,我们要去.

## 运送它

这一课产生了`outputs/skill-gateway-bootstrap.md`鉴于企业MCP计划 (用户,后端,合规性),技能产生了网关配置规格.

## 运动

1. 跑步`code/main.py`作为一个被允许用户,然后作为一个被禁止用户,然后超过利率限制的爆发.

2. 添加一个从结果中删除 PII 的政策,然后返回客户端.使用简单的 regex 通过SSN 形状的字符串;注意差距 (电子邮件,电话号码).

3. 扩展审计日志以发射OpenTelemetry GenAI范围. 13 · 20阶段涵盖了精确的属性.

4. 设计一个50个开发团队的RBAC政策,有五个后端 (笔记,吉图,后台,吉拉,slack).谁只能阅读每个?谁能写?

5. 查看Cloudflare企业MCP帖子上到下. 确定一个功能Cloudflare船只,这个Stdlib门口没有.

## 关键词

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Gateway | "MCP proxy" | Centralizing server between clients and backends |
| Credential vaulting | "Backend tokens stay server-side" | Developers never see upstream tokens |
| Session-aware routing | "Multi-backend session" | Gateway multiplexes N backend sessions per developer session |
| Tool-hash pinning | "Approved manifest" | SHA256 of every approved tool description; blocks rug-pulls centrally |
| RBAC | "Per-user policy" | Role-based access control for tools and servers |
| Policy-as-code | "Declarative rules" | OPA/Rego, Kyverno, Styra policies enforced at gateway |
| Audit log | "Who, what, when" | Append-only event log for compliance |
| Rate limit | "Per-user token bucket" | Per-minute caps to prevent abuse |
| Official MCP Registry | "Canonical upstream" | `registry.modelcontextprotocol.io`, namespace-verified |
| Reverse-DNS naming | "Registry namespace" | `io.github.user/server` convention |

## 进一步阅读

- [Official MCP Registry](https://registry.modelcontextprotocol.io/)法典上游,名称空间验证
- [Cloudflare — Enterprise MCP](https://blog.cloudflare.com/enterprise-mcp/) 通过 OAuth 和政策的网关模式
- [agentic-community — MCP gateway registry](https://github.com/agentic-community/mcp-gateway-registry)开源参考网关
- [TrueFoundry — What is an MCP gateway?](https://www.truefoundry.com/blog/what-is-mcp-gateway)功能比较文章
- [IBM — MCP context forge](https://github.com/IBM/mcp-context-forge)IBM的企业门户
