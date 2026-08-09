# 转移: 转移: 转移: 转移:

> 工作室在本地工作,而不是其他地方.流式HTTP (2025-03-26) 是远程标准.旧的HTTP+SSE运输已过时,并将在2026年中移除.选择错误的运输成本是迁移;选择正确的购买远程托管的MCP服务器,具有会议连续性和DNS重复保护.

**Type:** Learn
**Languages:** Python (stdlib, Streamable HTTP endpoint skeleton)
**Prerequisites:** Phase 13 · 07, 08 (MCP server and client)
**Time:** ~45 minutes

## 学习目标

- 根据部署形状 (本地与远程,单进程与舰队) 选择studio和 Streamable HTTP.
- 实现流式HTTP单端点模式:请求的POST,会议流的GET.
- 执行`Origin`通过验证和会议识别语义来击败DNS重新检索.
- 在2026年中期删除截止日期之前将旧的HTTP+SSE服务器迁移到流式HTTP.

## 问题

首个MCP远程运输 (2024-11) 是HTTP+SSE:两个终端点,一个为客户端的POST和一个服务器-传输事件频道.它工作.它也很不:每次会议的两个终端点,一些CDN前面的破解缓存,以及对长期的SSE连接的严重依赖,一些WAF攻击性地终止.

通过流式HTTP取代了2025-03-26规范:一个终端点,客户端请求的POST,设置会议流的GET,两个共享一个`Mcp-Session-Id`截至2026年底,大多数企业服务器都将被移除. 截至2026年6月30日,亚特拉斯人罗沃移除了它.

工作室仍然对本地服务器很重要. 克劳德桌面,VS代码,以及每个IDE型客户端都通过工作室生成服务器. 正确的心理模型:工作室为"这个机器",流式HTTP为"网络上".没有交叉.

## 概念

### 工作室

- 客户端产生的服务器,通过STDIN/STDOUT通信.
- 每行一个JSON对象,每行一个新线.
- 没有会议身份,进程身份是会议.
- 没有需要的授权 (孩子继承了父母的信任界限).
- 永远不要使用远程服务器,你需要SSH或socat道,在此时使用流式HTTP.

### 流式 HTTP

单一的终点`/mcp`支持三个HTTP方法:

- **POST /mcp.**客户端发送一个JSON-RPC消息.服务器以单个JSON响应或一个或多个响应的SSE流 (用于批量响应和与该请求相关的通知) 响应.
- **GET /mcp.**客户端打开长期存在的SSE频道.服务器使用它来对服务器对客户端的请求 (样本,通知,调用).
- **DELETE /mcp.**客户端明确终止会议.

会议由 `Mcp-Session-Id`服务器设置首个响应,客户端在每次请求上回响. 会议ID必须是加密式随机 (128+位);客户端选择的ID被拒绝以确保安全性.

### 单个终点对两个

旧规格中的两端点模式仍然可调用2026年. 规格宣布它是"遗留兼容".但所有新服务器都应该是单端点.官方SDK发射单端点;使用遗留模式只有与未迁移的遥控器交谈时.

### `Origin`验证和DNS检测

浏览器不是MCP客户端 (今天),但攻击者可以创建一个 Web 页面,`localhost:1234/mcp`用户本地MCP服务器在哪里收听. 如果服务器不检查`Origin`浏览器的原始版本将无法保存,因为`Origin: http://evil.com`是有效的交叉起源.

根据2025-11-25规范,服务器必须拒绝其请求.`Origin`允许列表通常包含MCP客户端主机 (`https://claude.ai`现在`vscode-webview://*`) 和本地UI的本地主机变体.

### 会议ID生命周期

1. 客户在没有 发送首次请求`Mcp-Session-Id`现在,我们要去.
2. 服务器将随机的ID,集 `Mcp-Session-Id`在响应标题上.
3. 客户端在所有随后的请求上回响了该标题`GET /mcp`为了流动.
4. 服务器可以取消会议; 客户端在随后的请求中看到404并且必须重新启动.
5. 客户端可以明确删除此次会议,

### 保持和重新连接

客户端通过重新GET,重新建立相同的连接.`Mcp-Session-Id`服务器必须在停机期间排队错过的事件 (直到合理的窗口) 并通过 `last-event-id`标题,客户端回声.

第13期包括任务,使得长期的工作即使连接完整的会议也能存活下来.

### 逆向兼容性探测器

客户端希望支持旧和新服务器:

1. 给我一个`/mcp`现在,我们要去.
2. 如果答案是`200 OK`通过JSON或SSE,这是流式HTTP.
3. 如果答案是`200 OK`随着`Content-Type: text/event-stream`并且`Location`标题指向次要终端点,这是传统的HTTP+SSE; 按照 `Location`现在,我们要去.

### 云,ngrok,和托管

2026年生产远程MCP服务器运行在Cloudflare Workers (附其MCP Agents SDK),Vercel Functions或容器化 Node/Python上.关键:您的托管必须支持SSE GET的长期HTTP连接.Vercel的免费层次限制在10秒,不适合.Cloudflare Workers支持无限流.

### 门口组成

当你将多个MCP服务器带入门口 (阶段13·17),门口是一个单个流式HTTP终端点,它会重写会议ID和多个文件.工具在门口层合并;客户端看到一个逻辑服务器.

### 交通故障模式

- **stdio SIGPIPE.**儿童过程死亡中文升级SIGPIPE;服务器应该清洁地退出. 客户应检测EOF并标记会议死亡.
- **HTTP 502 / 504.**云飞, nginx 和其他代理在上游失败时发射这些. 流向HTTP客户端应该在短暂的备份后再次尝试一次.
- **SSE connection drop.**TCP RST,代理时间停止或客户端网络变化关闭流.客户端重新连接到 `Mcp-Session-Id`且可选`last-event-id`继续.
- **Session revocation.**服务器无效的会议ID;客户端看到404下一个请求.客户端必须再次握手.
- **Clock skew.**客户端的资源-TTL计算与服务器不同.客户端应将服务器时间表作为权威的.

### 什么时候绕过流式HTTP

一些企业在自己的网络内部署了gRPC或消息队列运输后的MCP服务器.这是非标准的.MCP的规范没有正式定义这些.Gateways可以在内部使用gRPC时向MCP客户端暴露流通 HTTP表面.保持外部表面规范一致;Gateway拥有翻译.

```figure
tp-transport-handshake
```

## 用它

`code/main.py`通过使用 `http.server`它处理了POST,GET和Delete.`/mcp`集成`Mcp-Session-Id`在第一反应时,验证`Origin`处理器重复使用07课时记录服务器的发送逻辑.

什么要看:

- POST处理器阅读JSON-RPC体,发送,并写出JSON响应 (单响应变体;SSE变体结构相似).
- 其他`Origin`检查拒绝默认的`http://evil.example`探测器,但接受了`http://localhost`现在,我们要去.
- 会议ID是随机的128位六字符串;服务器在内存中保留每次会议状态.

## 运送它

这一课产生了`outputs/skill-mcp-transport-migrator.md`由于HTTP+SSE (遗产) MCP服务器,该技能生成了一个向 Streamable HTTP 迁移计划,具有会议身份连续性,原始检查和后退兼容的探测支持.

## 运动

1. 跑步`code/main.py`给我一个`initialize`其他`curl`观察到`Mcp-Session-Id`后面,请查看一个回应标题.

2. 添加一个开启SSE流的GET处理器.`notifications/progress`通过重新使用相同的会议ID连接并确认服务器接受.

3. 执行`last-event-id`在重连接时,重播自那个ID以来生成的任何事件.

4. 延长时间`Origin`验证支持一个野生卡模式 (`https://*.example.com`) 并确认它接受`https://app.example.com`但拒绝了`https://evil.example.com.attacker.net`现在,我们要去.

5. 取出官方注册表中的旧HTTP+SSE服务器 (有几个) 并绘制迁移:终端点处理,会议识别生成和标题语义方面的变化.

## 关键词

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| stdio transport | "Local child process" | JSON-RPC over stdin/stdout, newline-delimited |
| Streamable HTTP | "The remote transport" | Single-endpoint POST + GET + optional SSE, 2025-03-26 spec |
| HTTP+SSE | "Legacy" | Two-endpoint model being removed in mid-2026 |
| `Mcp-Session-Id` | "Session header" | Server-assigned random id echoed on every subsequent request |
| `Origin` allowlist | "DNS-rebinding defense" | Reject requests whose Origin is not approved |
| Single endpoint | "One URL" | `/mcp` handles POST / GET / DELETE for all session operations |
| `last-event-id` | "SSE replay" | Header used to resume a dropped stream without missing events |
| Backwards-compat probe | "Old vs new detection" | Client response-shape check that auto-selects transport |
| Long-lived HTTP | "SSE streaming" | Server pushes events for minutes or hours on one TCP connection |
| Session revocation | "Force re-init" | Server invalidates a session id; client must handshake again |

## 进一步阅读

- [MCP — Basic transports spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)用于stdio和流媒体HTTP的可信引用
- [MCP — Basic transports spec 2025-03-26](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports)引入了流式HTTP的修改
- [Cloudflare — MCP transport](https://developers.cloudflare.com/agents/model-context-protocol/transport/) 工作者托管的流向HTTP模式
- [AWS — MCP transport mechanisms](https://builder.aws.com/content/35A0IphCeLvYzly9Sw40G1dVNzc/mcp-transport-mechanisms-stdio-vs-streamable-http)不同部署形状的比较
- [Atlassian — HTTP+SSE deprecation notice](https://community.atlassian.com/forums/Atlassian-Remote-MCP-Server/HTTP-SSE-Deprecation-Notice/ba-p/3205484)具体的移民截止日期例
