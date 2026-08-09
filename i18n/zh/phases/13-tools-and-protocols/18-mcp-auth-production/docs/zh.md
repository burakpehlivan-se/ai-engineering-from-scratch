# 制作中MCP作者 注册,JWKS更新,观众注册的代币

> 课16提升了OAuth2.1状态机在记忆中. 到2026年,每一个 MCP 服务器到一个真正的组织都会在生产后面:客户端注册,扩展到无限客户群 (客户端 ID 转载数据文件首先,动态客户端注册作为一个反向兼容的反弹),授权服务器转载数据 (RFC 8414 *或* OpenID 连接发现), 支持代币验证,以及拒绝跨资源重播的观众支代币. 这一课程将整个表面模型为三个角色:授权服务器,资源服务器 (MCP服务器) 和客户端,
其他
> **Spec note (2025-11-25):**2025年11月的MCP授权规范将动态客户注册从`SHOULD`为了`MAY`造**Client ID Metadata Documents (CIMD)**建议的默认注册机制. 这一课程教导了规格的优先顺序,并且将DCR保留在通行过程中,因为它完全自主化在一个过程中.

**Type:** Build
**Languages:** Python (stdlib)
**Prerequisites:** Phase 13 · 16 (OAuth 2.1 state machine), Phase 13 · 17 (gateways)
**Time:** ~90 minutes

## 学习目标

- 通过RFC 8414元数据发现授权服务器,并验证合同.
- 执行RFC 7591动态客户登记,以便MCP客户在没有管理人员干预的情况下注册.
- 按时间表存储和更新JWKS键,以便签名验证存活关键翻转.
- 通过RFC 8707资源指标将代币粘贴到单个MCP资源上,并拒绝混副本重复使用.
- 清洁地分开三个角色:授权服务器,资源服务器,客户端,
- 阅读IdP能力矩阵,拒绝部署,当IdP不能满足MCP的作者配置文件时.

## 问题

课16模拟器在内存中运行OAuth 2.1. 制作中有三个操作缺口,仅存储器模拟器无法看到.

实际的组织运行数百个MCP服务器和数千个MCP客户端.运营商并没有手动注册每个Cursor用户作为OAuth客户端.2025-11-25规范给客户提供解决这一问题的优先顺序:使用预注册的服务器.`client_id`如果您有,则使用一个**Client ID Metadata Document**(客户端将自己识别成控制的HTTPSURL,授权服务器*拉*转移数据),否则会回到**RFC 7591 dynamic client registration**(客户*推*一个`POST /register`获得了`client_id`根据CIMD的建议,CIMD是默认的,因为它完全删除了每个服务器的注册,同时保持了DNS根基的信任模式;DCR保留了后退兼容性.`client_id_metadata_document_supported`对于CIMD,`registration_endpoint`对于DCR.

另一个缺口是关键旋转.  JWT验证取决于授权服务器的签字密钥, 作为 JSON Web Key Set (JWKS) 发布. 授权服务器按时间表旋转这些 (通常每小时,有时在事件响应下更快). 通过MCP服务器,一个接收JWKS的启动,直到转换窗口, 产品线程将 JWKS 作为缓存值,更新工作将在前键到期之前覆盖缓存,加上在一个新键签署的代币到达时,缓存错误的缓存.

课程16引入了RFC 8707资源指标.在生产中,该指标成为每一个请求的硬要求检查.`token.aud`根据其自己的规范资源URL,并拒绝与HTTP401的不匹配.这是唯一的防御,以防止上游MCP服务器 (或持有一个服务器的恶意客户端) 将该代币反射到同一信任网中的另一台服务器中.

这一课将每一个空隙映射到一个水面的混凝土块上. 转载数据的数据是HTTP终端.  JWKS缓存更新是一个计划工作加上一个关键值缓存. 资源服务器在发送任何工具之前运行的 JWT验证是例行程序. 保持三个角色分开,每个角色只执行其所有的检查:授权服务器发出和旋转密钥,资源服务器缓存和验证,客户端发现和注册.

## 概念

### 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签: 标签

文件`/.well-known/oauth-authorization-server`描述客户需要的一切:

```json
{
  "issuer": "https://auth.example.com",
  "authorization_endpoint": "https://auth.example.com/authorize",
  "token_endpoint": "https://auth.example.com/token",
  "jwks_uri": "https://auth.example.com/.well-known/jwks.json",
  "registration_endpoint": "https://auth.example.com/register",
  "response_types_supported": ["code"],
  "grant_types_supported": ["authorization_code", "refresh_token"],
  "code_challenge_methods_supported": ["S256"],
  "scopes_supported": ["mcp:tools.read", "mcp:tools.invoke"],
  "token_endpoint_auth_methods_supported": ["none", "private_key_jwt"]
}
```

给一个MCP资源URL链的客户端发现: `oauth-protected-resource`根据RFC 9728 (资源服务器文件) 命名发行者,然后`oauth-authorization-server`客户端从来没有硬码授权URL.

在信任MCP的IDP之前,你要验证的合同:

- `code_challenge_methods_supported`包括`S256`规格是明确的:如果这个字段是**absent**授权服务器不支持PKCE和客户端**MUST**拒绝继续.
- `grant_types_supported`包括`authorization_code`拒绝了`password`其他`implicit`现在,我们要去.
- 至少有一个招生路径被广告:`client_id_metadata_document_supported: true`其他国家**or** `registration_endpoint`您不再需要DCR.
- `response_types_supported`现在,我们在`["code"]`对于OAuth 2.1.

如果`S256`如果没有,MCP服务器拒绝部署这个IdP 没有降级模式的PKCE.如果 *没有*注册路径广告,你没有预注册`client_id`您也不能注册; 部署说明书是错误的,不是代码.

### 保护资源元数据

第16课涵盖RFC 9728的生产中.该文件是客户端寻找由*这个*MCP服务器所信任的授权服务器的唯一地方.单个MCP服务器可以接受多个IDP的代币 (一个为员工,一个为合作伙伴).RFC 9728声明该集合;RFC 8414记录每个IDP支持什么.

```json
{
  "resource": "https://notes.example.com",
  "authorization_servers": ["https://auth.example.com", "https://partners.example.com"],
  "scopes_supported": ["mcp:tools.invoke"],
  "bearer_methods_supported": ["header"],
  "resource_documentation": "https://notes.example.com/docs"
}
```

### 客户端ID元数据文件 (建议默认)

转换登记从*推*到*拉*.`client_id`客户端使用它控制的HTTPSURL**as**其他`client_id`. URL 归结为 JSON 转载数据文件;授权服务器在 OAuth 流量中按要求获取它.信任根植于 DNS:如果服务器运营商信任 `app.example.com`公司信任客户`https://app.example.com/client.json`没有登记回路,没有`client_id`没有每个服务器状态保持同步.

客户端主持的元数据文档:

```json
{
  "client_id": "https://app.example.com/oauth/client.json",
  "client_name": "Example MCP Client",
  "client_uri": "https://app.example.com",
  "redirect_uris": ["http://127.0.0.1:7333/callback", "http://localhost:7333/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none"
}
```

其他`client_id`文件中的值**MUST**授权服务器确认此情况,拒绝不匹配.`client_id_metadata_document_supported: true`在其RFC 8414元数据中.

两项安全事实,规范是直接的:

- **SSRF.**授权服务器获取攻击者提供的URL. 它必须防范服务器端请求伪造 (不获取内部/管理员终端点).
- **localhost impersonation.**单独CIMD不能阻止本地攻击者索取合法的客户端的元数据URL并绑定任何`localhost`转向权限服务器**MUST**在同意期间明确显示转向URI主机名称,**SHOULD**警告我们`localhost`- 只有转向.

由于CIMD不需要服务器端状态,因此没有登记器可以像DCR所要求的那样站立.客户端端只能读取:从静态HTTPS端点提供您的元数据文档,然后让授权服务器拉出它.

### 动态客户端注册 (倒退/倒退兼容性)

现在,DCR已经成为一个`MAY`没有它 (而且没有CIMD或预注),每个MCP客户端 (Cursor,Claude Desktop,一个定制代理) 需要与IDP管理员进行非带交换.

```json
POST /register
Content-Type: application/json

{
  "redirect_uris": ["http://127.0.0.1:7333/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none",
  "scope": "mcp:tools.invoke",
  "client_name": "Cursor",
  "software_id": "com.cursor.cursor",
  "software_version": "0.42.0"
}
```

服务器响应了`client_id`其他`registration_access_token`对于后续更新:

```json
{
  "client_id": "c_3e7f1a",
  "client_id_issued_at": 1769472000,
  "redirect_uris": ["http://127.0.0.1:7333/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "registration_access_token": "regt_b2...",
  "registration_client_uri": "https://auth.example.com/register/c_3e7f1a"
}
```

`token_endpoint_auth_method: none`对于使用者的设备上运行的MCP客户端来说,这是正确的默认.`client_id`只有没有`client_secret`公共客户需要的拥有证明.

生产的三大陷:

- 没有那么,一个敌对的演员将编写数百万个假注册,`client_id`在注册官处理请求之前,请检查利率限制.
- `software_statement`课程模拟跳过它;生产线一个验证步骤拒绝任何其他地方的未签名注册转向URI.
- 其他`registration_access_token`盗窃这个代币意味着攻击者可以重写客户端的转向URI.

### 资源指标 (RFC 8707 (重复) 

制作规则:每一个代币请求都包括`resource=<canonical-mcp-url>`并且MCP服务器验证`token.aud`常规的URI是服务器的*最具体*标识符:它使用小字母方案和主机,没有碎片,通常没有后续切片.路径组件是**not**规则 规格在需要识别一个单个MCP服务器时保留它. `https://mcp.example.com`现在`https://mcp.example.com/mcp`现在`https://mcp.example.com:8443`其他`https://mcp.example.com/server/mcp`选择一个每个服务器和`aud`现在,我们在学习时,`https://notes.example.com`简单的说法:一个部署在一个源头下共托几个MCP服务器,以路径来区分它们.

### 标准标准 (RFC 7636 (重复)  PKCE

在 OAuth 2.1 中,PKCE是强制性的.课程的授权代码流动始终带有`code_challenge`其他`code_verifier`服务器拒绝任何没有验证器或没有对存储挑战进行哈希的验证器的代币请求.

### 经过该报告的调查结果,该报告的内容均包括:

关于MCP服务器授权层必须做什么,MCP规范 (2025-11-25) 是精确的:

- 执行RFC 9728保护资源的元数据,并通过 `WWW-Authenticate: Bearer resource_metadata="..."`标题在401号**or**已知的URI`/.well-known/oauth-protected-resource`(SEP-985使头条可选,已知倒退).`authorization_servers`领域**MUST**提名至少一个服务器.
- 仅通过 `Authorization: Bearer ...`现在**every**从来没有在查询链中,从来没有仅在会议开始时验证.
- 验证`aud`现在`iss`现在`exp`服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器 服务器**MUST**确认该代币是专门发行给它 (观众); 缺失或不匹配`aud`没有被拒绝,从来没有被视为牌.
- 在401/403回来`WWW-Authenticate: Bearer`运输`error=...`其他`resource_metadata="<PRM-URL>"`参数 (元数据文档的URL, *不是*空格资源),以及`scope="..."`现在`insufficient_scope`(403). 注:参数是`resource_metadata`没有发现的指标`resource`挑战中的参数.
- 授权服务器发现接受**either**标签: 标签: 标签: 标签: 标签: 标签:**or**客户端必须以优先顺序尝试两个已知后尾.
- 客户端 (而不是服务器) 防御**mix-up attacks**报告预期的情况`issuer`在转向并验证`iss`通过 PKCE 系统,客户端将其 转换到 其他类型的数据库中.`code_verifier`无论它是什么标志性的目的地.

标题:OAuth 2.1草案是基板;RFC 8414/7591/8707/9728/9207 +RFC 7636 +CIMD是表面;MCP规格是配置文件.

### 产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品产品

不是每个IDP都支持完整的MCP配置文件.下面的矩阵记录了2025-11-25规范的实际能力声明.这是一个 *部署门户,而不是建议.

根据CIMD的2025-11-25规范,底层OAuth草案仅在2025年10月被采用,因此供应商支持仍在到达以下将"CIMD"作为"今天的位置,请在您的租户中验证",而不是永久声明.

| IdP category | AS metadata (8414/OIDC) | CIMD | RFC 7591 DCR | RFC 8707 resource | RFC 7636 S256 PKCE | Notes |
|---|---|---|---|---|---|---|
| Self-hosted (Keycloak) | yes | emerging | yes | yes (since 24.x) | yes | Reference IdP for the MCP profile in this lesson; full DCR path end-to-end, CIMD tracking the new spec. |
| Enterprise SSO (Microsoft Entra ID) | yes | emerging | yes (premium tiers) | yes | yes | DCR availability differs by tenant tier; verify in target tenant before deploying. |
| Enterprise SSO (Okta) | yes | emerging | yes (Okta CIC / Auth0) | yes | yes | DCR available on Auth0 (now Okta CIC); classic Okta orgs require admin pre-registration. |
| Social login IdPs (generic) | varies | no | rarely | rarely | yes | Most social IdPs treat clients as static partners; no self-service enrollment. Use as identity source only, layer your own MCP-aware authorization server on top. |
| Custom / homegrown | depends | depends | depends | depends | depends | If you ship your own, ship the full profile and prefer CIMD. Skipping PKCE or audience binding breaks the MCP auth contract. |

部署表的拒绝规则:如果选择的IdP没有列出`S256`在`code_challenge_methods_supported`登记是一个软门:你需要*一个*工作路径 (预注册的 程序)`client_id`现在`client_id_metadata_document_supported: true`其他`registration_endpoint`) 仅仅没有DCR就不再是拒绝触发因素,因为CIMD或预注册可以覆盖它.

###  JWKS 更新模式 (在AS 旋转,在资源服务器更新)

两个动词分开,因为把它们混在一起是真正的生产错误:

- **Rotate**资源服务器没有参与,也不能这样做.它不保留IdP的私钥.
- **Refresh**资源服务器做什么:`GET`资源服务器所执行的唯一的JWKS操作.

产品故障模式是旧缓存. 通过计划更新工作加上关键值缓存来解决.资源服务器运行一个工作 (cron,计时器,无论运行时间提供什么) 在固定间隔上,检索`<issuer>/.well-known/jwks.json`子,子,子,子,子,子,子,子,子,子,子,子,子,子,子,子,子,子,子,子,子,子.`cache[issuer] = {keys, fetched_at}`验证器可以从缓存中读取.`kid`缓存触发器中没有找到**one**交代更新作为倒退,然后重新检查. 这一次处理两个情况:计划更新,和重叠键窗口,一个新钥匙签署的代币在下一个计划更新之前到达.

倒的情况**must be a re-fetch, never a rotate**如果把缓存错误路径转换到旋转和,两件事就会发生破裂: (1) 造一个新钥匙会产生一个`kid`并且 (2) 攻击者将随机喷代币`kid`值得一提的是,它需要一个无限的系列的关键创作.`kid`总的来说,这只钱最多是一个浪费的.

缓存形状:

```json
{
  "https://auth.example.com": {
    "keys": [
      {"kid": "k_2026_03", "kty": "RSA", "n": "...", "e": "AQAB", "alg": "RS256", "use": "sig"},
      {"kid": "k_2026_04", "kty": "RSA", "n": "...", "e": "AQAB", "alg": "RS256", "use": "sig"}
    ],
    "fetched_at": 1772668800
  }
}
```

权限服务器通过输入下一个键 (`k_2026_04`) 在退休之前 (`k_2026_03`),因此在旧密钥下发行的代币仍然有效,直到它们到期.缓存存储存储会保持联盟;验证器选择通过`kid`现在,我们要去.

### 验证程序

在发送任何工具之前,MCP服务器执行验证.`code/main.py`使用:

```python
result = server.validate(bearer_token, required_scope="mcp:tools.invoke")
if not result["valid"]:
    return {"status": result["status"], "WWW-Authenticate": result["www_authenticate"]}
```

`validate`解码JWT,从JWKS缓存中解决签名密钥 (一次更新一次错误),验证签名,然后检查`iss`针对允许清单,`aud`对于这个服务器的可信资源,`exp`返回一个 `WWW-Authenticate`资源服务器上保持一个常规的程序意味着每个入口点 (每个工具调用,每个运输) 都会经历相同的检查;没有通路可以先验证到一个工具.

### 观众重播通行 (访问符号权限限制)

服务器A (`notes.example.com`) 和服务器B (`tasks.example.com`) 两者都会登录在同一授权服务器上.服务器A被破坏.攻击者取取用户的笔记符号并将其反弹到服务器B.

服务器B的验证器:

1. 解码JWT,通过JWKS来获取`kid`检查签名.
2. 查看`iss`对于其保护资源的元数据`authorization_servers`通过同一名人.
3. 查看`aud == "https://tasks.example.com"`没有成功的代币.`aud`是`https://notes.example.com`)
4. 返回401号`WWW-Authenticate: Bearer error="invalid_token", error_description="audience mismatch", resource_metadata="https://tasks.example.com/.well-known/oauth-protected-resource"`现在,我们要去.

观众声称是协议层的唯一防御措施. 为了性能而跳过它是最常见的生产错误;验证器必须在每个请求上运行,而不仅仅是会议开始. 规格称这是**access-token privilege restriction**:一个MCP服务器`MUST`拒绝任何在观众中不提名的标志.

> **Naming note.**规格保留了"混副"这个词,用于一个相关但明显的问题:一个作为OAuth的MCP服务器**proxy**通过使用静态客户端ID,将代币转发到第三方API上,而不会获得每个客户端用户同意.观众绑定修复了上述重播;混副级修复是每个客户端同意.**plus**没有通过输入代币到上游API (MCP服务器)`MUST`获得自己的独立上游代币).

### 混合攻击 (服务器无法提供客户端防御)

客户端可以在其一生中与许多授权服务器交谈.恶意AS可以试图让客户端在攻击者的代币终端点赎回诚实的AS授权代码.观众绑定在这里并没有帮助.

1. 在转向之前,客户记录预期的`issuer`根据验证的AS元数据.
2. 在授权回复上,客户将返回的回复进行比较.`iss`在任何地方发送代码之前,对记录发行者进行参数 (简单的字符串比较,没有正常化).
3. 失匹配 (或 `iss`在AS广告时缺席`authorization_response_iss_parameter_supported`拒绝,甚至不显示`error`其他地方

客户提供了其 `code_verifier`由于此,规格每次要求记录发行者与PKCE验证器一起,`state`现在,我们要去.

### 失败模式

- **Stale JWKS.**验证器在AS旋转键后拒绝有效代币. 修正是 cron-refresh + cache-miss-refetch 模式. 永远不要在更新工作的情况下缓存 JWKS.
- **Rotate-as-fall-back.**转换缓存错误路径到转换的路径,`kid`攻击者控制了它`kid`值值在关键创建DoS. 倒退必须是无权的`refresh-jwks`现在,我们要去.
- **Missing `aud` claim.**一些IDP默认省略`aud`除非`resource`验证者必须拒绝缺失的代币.`aud`没有人会把缺席视为一个狂欢的卡片.
- **Mix-up via missing `iss` check.**没有验证RFC 9207的客户端`iss`权限响应参数对发行者进行转向之前记录的权限响应参数可以被引导到攻击者的代币终端点中赎回诚实的AS代码.这是客户端故障;资源服务器无法补偿它.
- **Scope upgrade race.**两个同时进行的加大流程可以成功并产生两个具有不同范围的访问令牌.验证器必须使用在请求中呈现的令牌,而不是搜索"用户的当前范围",从而创建一个TOCTOU窗口.
- **Registration token theft.**一个泄露的`registration_access_token`让攻击者重新写转向URI. 按住这些,要求客户端在每次更新中呈现清晰文本; 根据怀疑旋转.
- **`iss` not pinned.**验证器可以接受任何`iss`攻击者可以建立自己的授权服务器,注册客户端,并发行代币.`authorization_servers`允许的列表是允许的列表;

```figure
t3-jwks-rotate
```

## 用它

`code/main.py`通过 Python 和三个角色进行了全过程的制作.`AuthorizationServer`现在`ResourceServer`其他`Client`流量:

1. 授权服务器将RFC 8414的元数据发布在 `/.well-known/oauth-authorization-server`现在,我们要去.
2.  MCP 客户端调用元数据终端点并检查其注册选项 (`client_id_metadata_document_supported`对于CIMD,`registration_endpoint`对于DCR) 和`S256`支持PKCE.
3. 通过DCR倒退路径:客户端发送到`/register`收到的数据`client_id`(CIMD客户端将其自己的HTTPS提供.`client_id`通过URL,跳过这个步骤.)
4. 通过 PKCE 保护的授权代码流 (RFC 7636) 运行MCP客户端`resource`标志 (RFC 8707).
5.  MCP 客户端调用一个工具在 MCP 服务器上`Authorization: Bearer ...`现在,我们要去.
6.  MCP服务器运行`validate`通过JWKS缓存的签字密钥来解决问题.
7.  IdP 旋转一个键; 计划更新将JWKS重新拉入缓存中.
8. 下一次调用会根据更新的键进行验证,而之前的代币仍然在重叠窗口中进行验证.
9. 试图反弹观众的 MCP 资源得到了 401 的`audience mismatch`其他`resource_metadata`标志.

在此,JWT使用HS256与共享秘密 (因此课程仅运行在stdlib上).制作使用RS256或EdDSA与上述JWKS模式;验证逻辑是相同的.因为IdP和资源服务器生活在一个过程中,`refresh_jwks`直接阅读授权服务器的关键列表;通过线程,它是一个HTTP `GET`为了`jwks_uri`现在,我们要去.

## 运送它

这一课产生了`outputs/skill-mcp-auth.md`鉴于MCP服务器配置和IdP能力组件,该技能会发射出站立的Auth表面保护资源的元数据,使用的注册路径 (CIMD,预注册或DCR倒退),JWKS更新时间表,范围映射和拒绝适用的规则,当IdP不支持完整的RFC配置文件.

## 运动

1. 跑步`code/main.py`观察如何在第6步中旋转键,`refresh_jwks`重新拉出已发布的集,既旧的代币 (重叠窗口),又新的代币都在重新启动的情况下验证.

2. 添加一个新的IDP到保护资源的元数据`authorization_servers`发行一个签署的代币,并确认验证者接受它.发行一个签署的代币,并确认验证者拒绝.`WWW-Authenticate: Bearer error="invalid_token", error_description="iss not allowed"`现在,我们要去.

3. 添加一个利率限制检查`register_client`使用一个每个源 IP 存储在一个小键键键的IP.

4. 阅读RFC 7591并确定课程的两个领域`/register`处理器不验证. 添加验证.`software_statement`其他`redirect_uris`美国的"URI"计划

5. 添加客户端ID的数据元数据文件路径.`client.json`哪个`client_id`允许服务器检查 (拒绝如果`client_id`≠ URL) 确认CIMD客户没有注册`register_client`给我打电话.

6. 证明了DoS的修正,向验证器发送一个随机的代币.`kid`确认`refresh_jwks`之后,故意将下跌回转换为旋转和,然后看看按假代币的重复回收.

7. 执行客户端RFC 9207 `iss`根据混合部分进行检查:在授权请求之前记录预期发行商,然后拒绝授权答复,该答案`iss`没有相应.

## 关键词

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| ASM | "OAuth metadata document" | RFC 8414 `/.well-known/oauth-authorization-server` JSON |
| CIMD | "Client metadata URL" | Client ID Metadata Document — an HTTPS URL used as the `client_id`; the AS pulls the JSON. Recommended default since 2025-11-25 |
| DCR | "Self-service client registration" | RFC 7591 `POST /register` flow; demoted to a `MAY` fallback in 2025-11-25 |
| JWKS | "Public keys for JWT validation" | JSON Web Key Set, fetched from `jwks_uri`, indexed by `kid` |
| Rotate vs refresh | "Updating the keys" | *Rotate* = AS mints/retires signing keys; *refresh* = resource server re-fetches the published set. Resource servers only ever refresh |
| Resource indicator | "Audience parameter" | RFC 8707 `resource` parameter pinning the token to one server |
| `aud` claim | "Audience" | JWT claim the validator compares against the canonical resource URL |
| Audience replay | "Token replay" | Token issued for Server A presented to Server B; defended by audience validation (spec: access-token privilege restriction) |
| Confused deputy | "Proxy token misuse" | An MCP proxy with a static client ID forwarding a token without per-client consent; distinct from audience replay |
| Mix-up attack | "Wrong token endpoint" | Client steered to redeem an honest AS's code at an attacker's endpoint; defended client-side via RFC 9207 `iss` |
| `iss` allow-list | "Trusted authorization servers" | The set named in protected-resource metadata's `authorization_servers` |
| `resource_metadata` | "Where to find the PRM doc" | `WWW-Authenticate` parameter naming the RFC 9728 metadata URL on a 401/403 |
| Public client | "Native or browser client" | OAuth client with no `client_secret`; PKCE compensates |
| `WWW-Authenticate` | "401/403 response header" | Carries `Bearer error=...` directives that drive client recovery |

## 进一步阅读

- [MCP — Authorization spec (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)本课程实现了MCP的作者资料
- [MCP blog — One Year of MCP: November 2025 Spec Release](https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/)2025年至25年发生了什么变化 (CIMD,XAA,DCR降级)
- [Aaron Parecki — Client Registration in the November 2025 MCP Authorization Spec](https://aaronparecki.com/2025/11/25/1/mcp-authorization-spec-update)CIMD-over-DCR的理由
- [OAuth Client ID Metadata Document (draft-ietf-oauth-client-id-metadata-document-00)](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-client-id-metadata-document-00)    
- [RFC 8414 — OAuth 2.0 Authorization Server Metadata](https://datatracker.ietf.org/doc/html/rfc8414) 发现合同
- [RFC 7591 — OAuth 2.0 Dynamic Client Registration Protocol](https://datatracker.ietf.org/doc/html/rfc7591) DCR (倒退路径)
- [RFC 7636 — Proof Key for Code Exchange (PKCE)](https://datatracker.ietf.org/doc/html/rfc7636)公众客户拥有证据
- [RFC 8707 — Resource Indicators for OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8707)观众的
- [RFC 9728 — OAuth 2.0 Protected Resource Metadata](https://datatracker.ietf.org/doc/html/rfc9728)资源服务器发现
- [RFC 9207 — OAuth 2.0 Authorization Server Issuer Identification](https://datatracker.ietf.org/doc/html/rfc9207) `iss`防范混合攻击的参数
- [OAuth 2.1 draft](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1)集成OAuth基板
