# 经验证 II  OAuth 2.1,资源指标,增长目标

> 远程MCP服务器需要授权,而不仅仅是身份验证. 2025-11-25规范与OAuth 2.1 + PKCE +资源指标 (RFC 8707) +保护资源元数据 (RFC 9728) 保持一致.SEP-835在403 WWW-Authenticate上增加范围同意,并增加授权.本课将 step-up流作为状态机实现,以便您可以看到每次跳跃.

**Type:** Build
**Languages:** Python (stdlib, OAuth state machine simulator)
**Prerequisites:** Phase 13 · 09 (transports), Phase 13 · 15 (security I)
**Time:** ~75 minutes

## 学习目标

- 区分资源服务器和授权服务器责任.
- 通过PKCE保护的 OAuth 2.1授权代码流.
- 使用`resource`保护资源的数据 (RFC 9728) 防止混副攻击.
- 执行加级授权:服务器用WWW-Authenticate响应403请求更大的范围;客户端再次要求用户同意并重新尝试.

## 问题

早期的MCP (前-2025) 运送了具有ad-hoc API密钥甚至没有Auth的远程服务器. 2025-11-25规范通过完整的OAuth 2.1配置文件缩小了这一差距.

现实世界需要的三个:

- **Ordinary remote servers.**用户安装一个远程MCP服务器,可访问他们的Notion / GitHub / Gmail. PKCE的 OAuth 2.1 是正确的形状.
- **Scope escalation.**已授予的备份服务器`notes:read`后面可能需要`notes:write`增强 (SEP-835) 要求增加范围.
- **Confused deputy prevention.**客户端持有为服务器A的观众量化的代币.服务器A是恶意的,并试图将代币呈现给服务器B.资源指标 (RFC 8707) 将代币 Pin给其预期的观众.

官方授权 2.1 不是新鲜的.新鲜的是MCP的配置文件:具体的要求流 (仅授权代码+PKCE;没有隐含,默认的客户端凭证),每个代币请求都必须使用资源指标,以及公布的保护资源元数据,以便客户知道要去哪里.

## 概念

### 角色

- **Client.**对于MCP客户端 (Claude Desktop,Cursor等).
- **Resource server.**任何其他服务器,
- **Authorization server.**问题代币.可能与资源服务器相同的服务或独立的IdP (Auth0, Keycloak,Cognito).

在MCP的个人资料中,资源和授权服务器可以是相同的主机,但应该通过URL来区分.

### 授权代码+PKCE

流量:

1. 客户端生成`code_verifier`,,,,,,,,,,,,,,,,,,,,,.`code_challenge`其他类型的产品
2. 客户端将用户转向到`/authorize?response_type=code&client_id=...&redirect_uri=...&scope=notes:read&code_challenge=...&resource=https://notes.example.com`现在,我们要去.
3. 使用者同意. 授权服务器将转向到`redirect_uri?code=...`现在,我们要去.
4. 客户端发送到`/token?grant_type=authorization_code&code=...&code_verifier=...&resource=...`现在,我们要去.
5. 授权服务器验证验证器的哈希与存储的挑战,并发出访问令牌.
6. 客户端使用代币:`Authorization: Bearer ...`在资源服务器的每一个请求上.

资源指标阻止代币在其他地方有效.

### 保护资源的元数据 (RFC 9728)

资源服务器发布一个`.well-known/oauth-protected-resource`文件:

```json
{
  "resource": "https://notes.example.com",
  "authorization_servers": ["https://auth.example.com"],
  "scopes_supported": ["notes:read", "notes:write", "notes:delete"]
}
```

客户端从资源服务器中发现授权服务器. 减少配置客户端只需要资源URL.

### 资源指标 (RFC 8707)

`resource`发行的代币包含了 代币的目标观众.`aud: "https://notes.example.com"`另一个MCP服务器接收了这些代币检查`aud`他否认它.

### 范围模型

范围是空间分离的字符串.

- `notes:read`现在`notes:write`现在`notes:delete`
- `admin:*`管理功能 (使用量少)
- `profile:read`为了身份

选择范围应是最不重要的:现在要求你需要的东西,当你需要更多的时候,就采取行动.

### 增长许可 (SEP-835)

用户补贴`notes:read`后来他们要求代理删除一张笔记.

```
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer error="insufficient_scope",
    scope="notes:delete", resource="https://notes.example.com"
```

客户端看到 insufficient_scope 错误,要求用户对额外的范围进行同意对话,执行一个小的 OAuth 流,再尝试使用新的代币请求.

### 标志观众验证

每个请求:服务器检查`token.aud == self.resource_url`这会阻止跨服务器代币重复使用.

### 短暂的代币和转换

访问令牌应该短暂 (1小时默认).更新令牌每次更新都会旋转.客户端在背景中处理默默更新.

### 没有标志性通行

采样服务器 (阶段13 · 11) 绝不能将客户的代币传递给其他服务.

### 混的副预防

标志绑定到`aud`客户端的联系方式`client_id`规范明确禁止了在MCP前远程工具生态系统中常见的"通过代码"模式.

### 发现客户身份

每个MCP客户端都将其元数据发布到固定URL.授权服务器可以获取客户端的元数据文档,发现转向URI和联系信息. 这取消了手动客户端注册.

### 网关和OAuth

阶段13 · 17显示了企业门户如何处理OAuth:门户保留上游服务器的凭证,客户端的代币由门户发行,上游代币从来不离开门户.这将翻转信任模式用户一次认证通过门户;门户处理N服务器授权.

```figure
t3-scope-stepup
```

## 用它

`code/main.py`模拟OAuth 2.1的全级加速度流程作为状态机器.

-  PKCE代码验证器/挑战生成.
- 权限代码流动与资源指标.
- 保护资源的元数据终端点.
- 标签验证与观众检查.
- 进步`insufficient_scope`现在,我们要去.

在此课程中没有HTTP服务器;状态机运行在内存中,所以你可以追踪每次跳跃.

## 运送它

这一课产生了`outputs/skill-oauth-scope-planner.md`由于有工具的远程MCP服务器,技能设计范围设置,定规则和升级政策.

## 运动

1. 跑步`code/main.py`追踪两范围的增速流量,注意哪些跳跃重复在增速.

2. 添加更新代币转换:每次更新都会发出新的更新代币,并无效了旧代币. 模拟转换后使用被盗的更新代币,并确认它失败.

3. 通过 stdlib http.server 实现保护资源的元数据终端作为一个真正的HTTP响应. 从09课中镜像 /mcp终端.

4. 设计一个GitHub MCP服务器的范围层次结构:阅读 repo,写 PR,批准 PR,并并 PR,管理.

5. 阅读RFC 8707和RFC 9728. 确定MCP在9728中使用的不同于RFC的例子中的一个字段. (提示:它涉及`scopes_supported`)

## 关键词

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| OAuth 2.1 | "Modern OAuth" | Consolidated RFC that mandates PKCE and forbids implicit flow |
| PKCE | "Proof-of-possession" | Code verifier + challenge defeating authorization-code interception |
| Resource indicator | "Token audience" | RFC 8707 `resource` parameter pinning token to one server |
| Protected-resource metadata | "Discovery doc" | RFC 9728 `.well-known/oauth-protected-resource` |
| Step-up authorization | "Incremental consent" | SEP-835 flow for adding scopes on demand |
| `insufficient_scope` | "403 with WWW-Authenticate" | Server signal to re-consent for a larger scope |
| Confused deputy | "Token reuse across services" | Attack where a trusted holder forwards a token inappropriately |
| Short-lived token | "Access token TTL" | Bearer that expires quickly; refresh token renews |
| Scope hierarchy | "Least privilege stack" | Graduated scope set with step-up between levels |
| Client ID metadata | "Client discovery doc" | URL at which the client publishes its own OAuth metadata |

## 进一步阅读

- [MCP — Authorization spec](https://modelcontextprotocol.io/specification/draft/basic/authorization)可行 MCP OAuth 资料
- [den.dev — MCP November authorization spec](https://den.dev/blog/mcp-november-authorization-spec/) 通过2025年至21月25日的变化
- [RFC 8707 — Resource indicators for OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8707)观众接的RFC
- [RFC 9728 — OAuth 2.0 protected resource metadata](https://datatracker.ietf.org/doc/html/rfc9728)发现文件的RFC
- [Aembit — MCP OAuth 2.1, PKCE and the future of AI authorization](https://aembit.io/blog/mcp-oauth-2-1-pkce-and-the-future-of-ai-authorization/)实用步骤上流通行
