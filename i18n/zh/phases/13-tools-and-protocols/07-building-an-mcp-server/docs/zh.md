# 构建MCP服务器  Python + TypeScript SDK

> 许多MCP教程只显示了工作室的问候世界. 实际的服务器将工具加上资源加上提示,处理能力谈判,发出结构错误,并在SDK中工作相同. 这一课构建了一个笔记服务器端到端:stdlib stdio运输,JSON-RPC发送,三个服务器原始,以及纯函数式的风格,当你毕业时,它会落入Python SDK的FastMCP或TypeScript SDK.

**Type:** Build
**Languages:** Python (stdlib, stdio MCP server)
**Prerequisites:** Phase 13 · 06 (MCP fundamentals)
**Time:** ~75 minutes

## 学习目标

- 实施`initialize`现在`tools/list`现在`tools/call`现在`resources/list`现在`resources/read`现在`prompts/list`其他`prompts/get`方法.
- 写一个发送循环,读取来自stdin的JSON-RPC消息,并写出对stdout的回应.
- 根据JSON-RPC 2.0规范和MCP的额外代码发出结构错误响应.
- 通过将 stdlib 实现到 FastMCP (Python SDK) 或TypeScript SDK,而不需要重写工具逻辑.

## 问题

在使用远程传输 (阶段13·09) 或 auth layer (阶段13·16) 之前,您需要一个干净的本地服务器.本地意味着stdio:客户端生成的服务器是个子进程,消息通过stdin/stdout新线定义流.

根据2025-11-25规范,工作室消息将被编码为JSON对象,`\n`区分器.这里没有SSE;SSE是旧的远程模式,将于2026年中移除 (Atlassian的Rovo MCP服务器于2026年6月30日废除了它;Keboola于2026年4月1日).

备注服务器是个好形状的,因为它运行了所有三个服务器原始性.`notes_create`资源暴露数据 (`notes://{id}`提示船舶模板 (`review_note`课程的形状将被普遍化到任何领域.

## 概念

### 发送循环

```
loop:
  line = stdin.readline()
  msg = json.loads(line)
  if has id:
    handle request -> write response
  else:
    handle notification -> no response
```

三个规则:

- 打印任何不是JSON-RPC封筒的东西,请不要打印到 stdout.
- 每个请求都必须与一个相同的回应相匹配`id`现在,我们要去.
- 通知不得被回复.

### 执行`initialize`

```python
def initialize(params):
    return {
        "protocolVersion": "2025-11-25",
        "capabilities": {
            "tools": {"listChanged": True},
            "resources": {"listChanged": True, "subscribe": False},
            "prompts": {"listChanged": False},
        },
        "serverInfo": {"name": "notes", "version": "1.0.0"},
    }
```

客户端依赖于设置的功能.

### 执行`tools/list`其他`tools/call`

`tools/list`收益`{tools: [...]}`每条条目都包含`name`现在`description`现在`inputSchema`现在,我们要去.`tools/call`需要`{name, arguments}`利率`{content: [blocks], isError: bool}`现在,我们要去.

内容块是输入的.最常见的:

```json
{"type": "text", "text": "Found 2 notes"}
{"type": "resource", "resource": {"uri": "notes://14", "text": "..."}}
{"type": "image", "data": "<base64>", "mimeType": "image/png"}
```

工具级错误有两种形式.协议级错误 (未知方法,坏参数) 是JSON-RPC错误.工具级错误 (有效调用,但工具失败) 被返回为`{content: [...], isError: true}`这让模型在本文中看到失败.

### 实施资源

资源的设计仅可读.`resources/list`返回明示表;`resources/read`返回内容.`file://...`现在`http://...`像是""这样的定制方案.`notes://`现在,我们要去.

当你将数据作为资源而不是工具时:

- 模型不会"调用",客户端可以根据用户的要求将其注入文本中.
- 订阅允许服务器在资源变化时推送更新 (阶段13 · 10).
- 阶段13 · 14延长了这一阶段`ui://`互动资源.

### 执行提示

提示是包含命名参数的模板.主机将它们作为切断命令显示.`review_note`快速可能需要一个`note_id`文件的文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,文件,

### 工作室运输细节

- 没有长度预定框.
- 没有缓冲.`sys.stdout.flush()`在每一封信之后.
- 客户控制了生命周期. 当STDIN关闭时,清洁地离开.
- 不要默默处理SIGPIPE;登录和退出.

### 标记

每个工具都能携带`annotations`描述安全性:

- `readOnlyHint: true`纯读,可以再试一次.
- `destructiveHint: true`不可逆的副作用; 患者应确认.
- `idempotentHint: true`相同的输入产生相同的输出.
- `openWorldHint: true`与外部系统相互作用.

客户端使用这些信息来决定UX (确认对话框,状态指标) 和路由 (阶段13 · 17).

### 毕业的路径

现在,我们在`code/main.py`快MCP (Python) 则将相同的逻辑推向装饰师式:

```python
from fastmcp import FastMCP
app = FastMCP("notes")

@app.tool()
def notes_search(query: str, limit: int = 10) -> list[dict]:
    ...
```

类型Script SDK具有相等的形状. 毕业途径是随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随时随之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之之

```figure
t3-dispatch-loop
```

## 用它

`code/main.py`只有在工作室,它处理`initialize`现在`tools/list`现在`tools/call`对于三种工具 (`notes_list`现在`notes_search`现在`notes_create`), `resources/list`其他`resources/read`对于每一张笔记,`review_note`通过输入JSON-RPC消息来驱动它:

```
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python main.py
```

什么要看:

- 发送器是一个`dict[str, Callable]`按方法名称键入.
- 每个工具执行器都会返回内容块列表,而不是一个空文字列.
- `isError: true`执行者提起时设置.

## 运送它

这一课产生了`outputs/skill-mcp-server-scaffolder.md`由于一个域名 (笔记,门票,文件,数据库),技能将提供合适的工具/资源/提示分类和SDK毕业途径.

## 运动

1. 跑步`code/main.py`通过手工编写的JSON-RPC消息来驱动它.`notes_create`现在`resources/read`为了回收新笔记.

2. 添加一个`notes_delete`工具`annotations: {destructiveHint: true}`验证客户端将出现确认对话框 (这需要一个真正的主机; Claude Desktop 工作).

3. 实施`resources/subscribe`所以服务器推了`notifications/resources/updated`每当一个笔记被修改时,添加一个保持任务.

4. 移植服务器到FastMCP.Python文件应该缩小到80行以下.电线行为必须是一样的;用同一个JSON-RPC测试带验证.

5. 阅读规格`server/tools`标识一个工具定义的领域,没有在本课程的服务器中实现. (提示:有几个;选择一个,然后添加它.)

## 关键词

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| MCP server | "The thing that exposes tools" | Process that speaks MCP JSON-RPC over stdio or HTTP |
| stdio transport | "Child process model" | Server is spawned by client; communicates via stdin/stdout |
| Dispatcher | "Method router" | Map of JSON-RPC method name to handler function |
| Content block | "Tool result chunk" | Typed element in the `content` array of a tool response |
| `isError` | "Tool-level failure" | Signals the tool failed; distinguishes from JSON-RPC error |
| Annotations | "Safety hints" | readOnly / destructive / idempotent / openWorld flags |
| FastMCP | "Python SDK" | Decorator-based higher-level framework on top of the MCP protocol |
| Resource URI | "Addressable data" | `file://`, `db://`, or custom scheme identifying a resource |
| Prompt template | "Slash-command brief" | Server-supplied template with argument slots for host UIs |
| Capability declaration | "Feature toggle" | Per-primitive flags declared in `initialize` |

## 进一步阅读

- [Model Context Protocol — Python SDK](https://github.com/modelcontextprotocol/python-sdk)参考Python实现
- [Model Context Protocol — TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)并行TS实施
- [FastMCP — server framework](https://gofastmcp.com/)MCP服务器的PythonAPI
- [MCP — Quickstart server guide](https://modelcontextprotocol.io/quickstart/server)使用 SDK 的端到端教程
- [MCP — Server tools spec](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)工具/*信息的完整参考
