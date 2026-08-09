#  MCP资源和提示  工具之外的文本曝光

> 工具获得90%的MCP关注.其他两个服务器原始程序解决不同的问题.资源暴露数据用于阅读;提示暴露可重复使用的模板作为剪切命令.许多服务器应该使用资源而不是包装阅读工具,提示而不是硬编码工作流在客户端提示.这个课程命名决策规则,并行走的.`resources/*`其他`prompts/*`关于这些信息.

**Type:** Build
**Languages:** Python (stdlib, resource + prompt handler)
**Prerequisites:** Phase 13 · 07 (MCP server)
**Time:** ~45 minutes

## 学习目标

- 选择将功能作为工具,资源或一个特定域名的提示.
- 实施`resources/list`现在`resources/read`现在`resources/subscribe`手`notifications/resources/updated`现在,我们要去.
- 实施`prompts/list`其他`prompts/get`它们使用了论证模板.
- 识别主机出现提示时,即切除命令与自动注入的语境.

## 问题

简单的MCP服务器,将所有内容都作为工具:`notes_read`现在`notes_list`现在`notes_search`结果是: 通过数据的数据,

- 模型必须决定是否打电话`notes_read`对于任何可能从文本中获益的查询.
- 仅可阅读的内容不能订阅或流向主机的侧面板.
- 客户端UI (Claude Desktop的资源附件面板,Cursor的"包含文件"选项) 不能显示数据.

右分:将数据作为资源,将突变或计算操作作为工具,将可重复使用的多步骤工作流作为提示暴露.每个原始具有其 UX 能力和访问模式.

## 概念

### 工具与资源与提示 决策规则

| Capability | Primitive |
|------------|-----------|
| User wants to search, filter, or transform data | tool |
| User wants the host to include this data as context | resource |
| User wants a templated workflow they can re-run | prompt |

导向:如果模型在每个相关查询中调用它,它将是工具.如果用户将它添加到对话中,它将是资源.如果整个多步骤工作流是用户想要重复使用的单元,它是提示.

### 资源

`resources/list`收益`{resources: [{uri, name, mimeType, description?}]}`现在,我们要去.`resources/read`需要`{uri}`利率`{contents: [{uri, mimeType, text | blob}]}`现在,我们要去.

任何可归址的URI都可以:

- `file:///Users/alice/notes/mcp.md`
- `postgres://my-db/query/SELECT ...`
- `notes://note-14`(关税制度)
- `memory://session-2026-04-22/recent`(服务器特定)

`contents[]`支持文本和二进制.`blob`作为一个64基编码字符串加上一个`mimeType`现在,我们要去.

### 资源订阅

声明`{resources: {subscribe: true}}`客户的电话`resources/subscribe {uri}`服务器发送`notifications/resources/updated {uri}`客户端重新阅读.

使用案例:一个备注服务器,其资源是磁盘上的文件;一个文件监视器触发更新通知;Claude Desktop在在主机之外编辑时将文件重新引入文本.

### 资源模板 (2025-11-25 添加)

`resourceTemplates`让你暴露一个参数化的URI模式: `notes://{id}`随着`id`客户端可以自动填写资源选民中的身份证.

### 提示

`prompts/list`收益`{prompts: [{name, description, arguments?}]}`现在,我们要去.`prompts/get`需要`{name, arguments}`利率`{description, messages: [{role, content}]}`现在,我们要去.

提示是填写一个主机给其模型的消息列表的模板.`code_review`快速需要一个`file_path`参数返回一个三个信息序列:系统消息,文件体的用户消息,以及一个推理模板的助理开启.

### 接待者和提示

克劳德桌面,VS代码和Cursor将提示作为聊天界面的切片命令.`/code_review`服务器的提示是"用户快捷方式"和"向模型发送的完整提示"之间的合同.

检查能力谈判.一个具有快速能力的服务器声明,但没有快速支持的客户端将不看到切片命令.

### "变更列表"通知

资源和提示都发射`notifications/list_changed`只有输入20个新笔记的笔记服务器发出了`notifications/resources/list_changed`客户重新调用`resources/list`为了收拾这些补充.

### 内容类型公约

文本:`mimeType: "text/plain"`现在`text/markdown`现在`application/json`现在,我们要去.
对于二进制:`image/png`现在`application/pdf`另外一个`blob`其他地方
对于MCP应用程序 (14课): `text/html;profile=mcp-app`在一个`ui://`子.

### 动态资源

资源URI不必与静态文件相匹配. `notes://recent`能在每次阅读中返回最后五张笔记.`db://query/users/active`服务器可以动态计算内容.

规则:如果客户端可以通过URI缓存,URI必须稳定.如果计算是单次,URI应该包含一个时间或非,以便客户端缓存不会变老.

### 订阅与投票

订阅客户端通过服务器推送`notifications/resources/updated`预订客户端或不支持它的主机通过重新阅读. 两个都符合规范. 服务器的功能声明告诉客户端它支持哪些.

订阅成本:服务器上每次会议状态 (谁订阅什么). 保持订阅的集合有限;断开客户端应停机时间.

### 提示与系统提示

服务器提示 (MCP) 并不是系统提示.主机系统提示 (其自己的操作说明) 和MCP提示 (用户所调用的服务器提供的模板) 并肩.一个好行为的客户端从来不让服务器提示取代其自己的系统提示;它将它们放在层次上.

```figure
t3-primitive-sort
```

## 用它

`code/main.py`从07课程开始,将笔记服务器扩展到:

- 每笔笔记的资源 (`notes://note-1`其他类型`resources/subscribe`支持.
- `review_note`提示将其转换为3条消息模板.
- 发射的文件监视器模拟`notifications/resources/updated`当修改说明时.
- `notes://recent`动态资源,总是返回最新的五个音符.

运行演示,看看全部流量.

## 运送它

这一课产生了`outputs/skill-primitive-splitter.md`鉴于拟议的MCP服务器,技能将每个功能归类为工具/资源/提示,并有理由.

## 运动

1. 跑步`code/main.py`观察最初的资源列表,然后启动编辑注释,并验证`notifications/resources/updated`事件发生火灾.

2. 添加一个`resources/list_changed`发射者:当创建新的说明时,发送通知,以便客户重新发现.

3. 设计GitHub MCP服务器的三个提示: `summarize_pr`现在`triage_issue`现在`release_notes`任何一个有论点方案. 提示器应该可以在没有进一步的编辑的情况下运行.

4. 取一个现有工具在课07服务器中,并分类它是否应该保持为工具,或者分为资源加工具对. 用一个句子证明理由.

5. 阅读规格`server/resources`其他`server/prompts`确定一个字段`resources/read`,看看,我们有很多人.`_meta`资源内容.

## 关键词

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Resource | "Exposed data" | URI-addressable content the host can read |
| Resource URI | "Pointer to data" | Scheme-prefixed identifier (`file://`, `notes://`, etc.) |
| `resources/subscribe` | "Watch for changes" | Client-opt-in server-push updates for a specific URI |
| `notifications/resources/updated` | "Resource changed" | Signal to client that a subscribed resource has new content |
| Resource template | "Parameterized URI" | URI pattern with completion hints for the host picker |
| Prompt | "Slash-command template" | Named multi-message template with argument slots |
| Prompt arguments | "Template inputs" | Typed parameters the host collects before rendering |
| `prompts/get` | "Render template" | Server returns the filled-in message list |
| Content block | "Typed chunk" | `{type: text \| image \| resource \| ui_resource}` |
| Slash-command UX | "User shortcut" | Host surfaces prompts as commands starting with `/` |

## 进一步阅读

- [MCP — Concepts: Resources](https://modelcontextprotocol.io/docs/concepts/resources)资源URI,订阅和模板
- [MCP — Concepts: Prompts](https://modelcontextprotocol.io/docs/concepts/prompts)快速模板和切除命令集成
- [MCP — Server resources spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/resources) 满`resources/*`信息参考
- [MCP — Server prompts spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts) 满`prompts/*`信息参考
- [MCP — Protocol info site: resources](https://modelcontextprotocol.info/docs/concepts/resources/) 社区指南扩展官方文件
