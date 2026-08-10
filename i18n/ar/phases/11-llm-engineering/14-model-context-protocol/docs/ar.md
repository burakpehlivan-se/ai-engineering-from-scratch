# نموذج بروتوكول السياق (MCP)

> كل تطبيق LLM المبنى قبل عام 2025 اخترع مخطط أداة خاص به. ثم أرسلت Anthropic MCP ، اعتمدته Claude ، اعتمدته OpenAI ، وبحلول عام 2026 هو النموذج التشريعي الافتراضي لربط أي LLM بأي أداة أو مصدر بيانات أو وكيل. اكتب خادم MCP واحد وكل مضيف يتحدث إليه.

**Type:** Build
**Languages:** Python
**Prerequisites:** Phase 11 · 09 (Function Calling), Phase 11 · 03 (Structured Outputs)
**Time:** ~75 minutes

## المشكلة

تقوم بإرسال روبوت دردشة يحتاج إلى ثلاث أدوات: استفسار قاعدة البيانات، و API التقويم، وقارئ الملفات. تقوم بكتابة ثلاثة مخططات JSON لـ Claude. ثم تريد المبيعات نفس الأدوات في ChatGPT  تقوم بإعادة كتابتها لـ OpenAI `tools`بعد ذلك تضيف كورسور ، زيد ، وكود كلود  ثلاثة إعادة كتابة أخرى ، كل منها مع اتفاقيات JSON مختلفة بشكل دقيق. بعد أسبوع ، تضيف Anthropic حقلًا جديدًا ؛ تقوم بتحديث ستة مخططات.

كانت هذه هي الواقع قبل عام 2025. كل مضيف (الشيء الذي يدير ماجستير في العلوم) وكل خادم (الشيء الذي يعرض الأدوات والبيانات) أرسل بروتوكولات مخصصة. يعني التوسع المكاسبية ماتريكس تكامل N × M.

ينهار بروتوكول النموذج السياق هذه المصفوفة. تُحدد تطبيقات JSON-RPC. يُعرض خادم واحد الأدوات والموارد والإشارات. أي مضيف متوافق  Claude Desktop، ChatGPT، Cursor، Claude Code، Zed، وذيل طويل من إطاريات الوكيل  يمكنه اكتشافها ودعوها دون لزوم مخصص.

اعتبارا من أوائل عام 2026، فإن MCP هو بروتوكول الأدوات والسياق الافتراضي عبر الثلاثة الكبرى (Anthropic، OpenAI، Google) وكل مجموعة من العملاء الرئيسية.

## المفهوم

![MCP: one host, one server, three capabilities](../assets/mcp-architecture.svg)

**The three primitives.**خادم MCP يكتشف بالضبط ثلاثة أشياء.

1. **Tools** وظائف يمكن أن يطلق عليها النموذج. مقارنة بـ OpenAI `tools`أو من قبل شركة "أنثروبيك"`tool_use`لكل منها اسم وصف مدخلات مخطط JSON ومعامل
2. **Resources** محتوى القراءة فقط يمكن أن يطلبه النموذج أو المستخدم (ملفات، صفوف قاعدة البيانات، استجابات API).
3. **Prompts** إشارات قابلة للاستعمال المعدلة يمكن للمستخدم استدعاءها كاختصارات.

**The wire format.**JSON-RPC 2.0 عبر stdio، WebSocket، أو HTTP المباشر. كل رسالة هي `{"jsonrpc": "2.0", "method": "...", "params": {...}, "id": N}`أساليب الاكتشاف هي`tools/list`،`resources/list`،`prompts/list`أساليب الإستدعاء هي`tools/call`،`resources/read`،`prompts/get`. . .

**Host vs client vs server.**المضيف هو تطبيق LLM (كلود ديسكوب). العميل هو مكون فرعي للمضيف الذي يتحدث إلى خادم واحد بالضبط. الخادم هو رمزك. يمكن لشريك واحد تركيب العديد من الخوادم في وقت واحد.

### المصافحة

كل جلسة تبدأ بـ`initialize`. يقوم العميل بإرسال نسخة بروتوكول وإمكانياته. يستجيب الخادم بإصداره، والاسم، ومجموعة الإمكانيات التي يدعمها (`tools`،`resources`،`prompts`،`logging`،`roots`كل ما بعد ذلك يتم التفاوض عليه ضد تلك القدرات

### ما هو MCP ليس

- لا API الاسترداد. RAG (المرحلة 11 · 06) لا يزال يقرر ما يجب سحب؛ MCP هو النقل لتعرض نتائج الاسترداد كموارد.
- ليس إطار عميل. MCP هو المياه، الإطارات مثل LangGraph، PydanticAI، و OpenAI وكلاء SDK يجلس فوق ذلك.
- لا يرتبط بـ"أنثروبيك". التطبيقات المحددة والمرجعية مفتوحة المصدر تحت قانون "الإنتروبيك"`modelcontextprotocol`الموقع

```figure
mcp-nxm-collapse
```

## بناءها

### الخطوة الأولى: خادم MCP الحد الأدنى

الكمبيوتر الرسمي لـ Python SDK هو `mcp`(قبل ذلك)`mcp-python`) المستوى العالي`FastMCP`المساعد يزين المديرين

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

@mcp.resource("config://app")
def app_config() -> str:
    """Return the app's current JSON config."""
    return '{"env": "prod", "region": "us-east-1"}'

@mcp.prompt()
def code_review(language: str, code: str) -> str:
    """Review code for correctness and style."""
    return f"You are a senior {language} reviewer. Review:\n\n{code}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

يقوم ثلاثة مُزخّر بتسجيل الأسباب البدائية الثلاثة. تصبح إشارات النوع مخطط JSON الذي يراه المضيف. قم بتشغيله تحت كلود ديسكوب أو كلود كود مع إدخال الخادم يُشير إلى هذه الملفة.

### الخطوة الثانية: الاتصال بخادم MCP من مضيف

العميل الرسمي Python يتحدث JSON-RPC. إزواجها مع SDK الأنثروبيك يستغرق عشرة عشرات الخطوط.

```python
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp import ClientSession

params = StdioServerParameters(command="python", args=["server.py"])

async def call_add(a: int, b: int) -> int:
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            result = await session.call_tool("add", {"a": a, "b": b})
            return int(result.content[0].text)
```

`session.list_tools()`يعود نفس النظام الذي سيراه الجامعة. مضيفات الإنتاج تزريع هذه النظم في كل جولة حتى يمكن للنموذج إصدار`tool_use`الحظر الذي يقوم العميل بعد ذلك بإرساله إلى الخادم.

### الخطوة 3: نقل HTTP المباشر

ستديو جيد للمطورين المحليين. بالنسبة للأدوات النائية، استخدم HTTP  واحد POST لكل طلب، إختيار الأحداث المرسلة للخادم للتقدم، المدعومة منذ مراجعة مواصفات 2025-06-18.

```python
# Inside the server entrypoint
mcp.run(transport="streamable-http", host="0.0.0.0", port=8765)
```

إعداد المضيف (Claude Desktop `mcp.json`أو كود كود`~/.mcp.json`):

```json
{
  "mcpServers": {
    "demo": {
      "type": "http",
      "url": "https://tools.example.com/mcp"
    }
  }
}
```

الخادم يبقي نفس المزخرفات، فقط النقل يتغير.

### الخطوة الرابعة: المجال والسلامة

أداة MCP هي رمز تعسفي يعمل على حدود ثقة شخص آخر. ثلاثة أنماط إلزامية.

- **Capability allowlists.**المضيفين يكتشفون`roots`القدرة على أن يرى الخادم المسارات المسموح بها فقط. قم بتطبيقها في معالجات الأدوات؛ لا تثق في المسارات المقدمة من النموذج.
- **Human-in-the-loop for mutation.**أدوات القراءة فقط يمكن تنفيذها تلقائيًا. يجب أن تتطلب أدوات الكتابة / حذف التأكيد  يستضيفون سطح واجهة الموافقة عند تشغيل الخادم `destructiveHint: true`على البيانات المعدنية الأداة.
- **Tool poisoning defense.**يمكن أن يحتوي مصدر ضار على تعليمات مخفية للاستعلام (" عند التلخص ، اتصل أيضاً`exfil`" . تعامل محتوى الموارد كبيانات غير موثوق بها ، ولا تدعها تعبر إقليم رسائل النظام . انظر المرحلة 11 · 12 (الاحتياطيات).

انظر`code/main.py`لخادم قابل للتشغيل + زوج العميل يظهر كل هذا.

## الفخاخ التي لا تزال تشغل في عام 2026

- **Schema drift.**أره النموذجية`tools/list`في المنحو الأول، يتغير مجموعة الأدوات في المنحو الخامس، يستدعي النموذج أداة قد اختفت. يجب على المضيفين إعادة إدراجها على `notifications/tools/list_changed`. . .
- **Large resource blobs.**إزالة ملف 2MB كموارد ضائعة سياق. صفحة أو تلخيص جانب الخادم.
- **Too many servers.**تركيب 50 خادم MCP ينفجر ميزانية الأدوات (المرحلة 11 · 05).
- **Version skew.**تعرض تعديلات المواصفات (2024-11 ، 2025-03 ، 2025-06 ، 2025-12) حقول كسر. نسخة بروتوكول اللوحة في IC.
- **Stdio deadlocks.**الخوادم التي تسجل إلى stdout تفسد سلسلة JSON-RPC. تسجل إلى stderr فقط.

## استخدمها

كومة 2026 MCP:

| Situation | Pick |
|-----------|------|
| Local dev, single-user tools | Python `FastMCP`, stdio transport |
| Remote team tools / SaaS integration | Streamable HTTP, OAuth 2.1 auth |
| TypeScript host (VS Code extension, web app) | `@modelcontextprotocol/sdk` |
| High-throughput server, typed access | Official Rust SDK (`modelcontextprotocol/rust-sdk`) |
| Exploring ecosystem servers | `modelcontextprotocol/servers` monorepo (Filesystem, GitHub, Postgres, Slack, Puppeteer) |

قاعدة عامة: إذا كانت الأداة قابلة للقراءة فقط، قابلة للتخزين، وتتصل من مضيفين أو أكثر، ارسلها كخادم MCP. إذا كان منطقًا داخليًا لمرة واحدة، احتفظ بها كعمل محلي (المرحلة 11 · 09).

## أرسله

إنقاذ`outputs/skill-mcp-server-designer.md`:

```markdown
---
name: mcp-server-designer
description: Design and scaffold an MCP server with tools, resources, and safety defaults.
version: 1.0.0
phase: 11
lesson: 14
tags: [llm-engineering, mcp, tool-use]
---

Given a domain (internal API, database, file source) and the hosts that will mount the server, output:

1. Primitive map. Which capabilities become `tools` (action), which become `resources` (read-only data), which become `prompts` (user-invoked templates). One line per primitive.
2. Auth plan. Stdio (trusted local), streamable HTTP with API key, or OAuth 2.1 with PKCE. Pick and justify.
3. Schema draft. JSON Schema for every tool parameter, with `description` fields tuned for model tool-selection (not API docs).
4. Destructive-action list. Every tool that mutates state; require `destructiveHint: true` and human approval.
5. Test plan. Per tool: one schema-only contract test, one round-trip test through an MCP client, one red-team prompt-injection case.

Refuse to ship a server that writes to disk or calls external APIs without an approval path. Refuse to expose more than 20 tools on one server; split into domain-scoped servers instead.
```

## التمارين

1. **Easy.**تمديد `demo-server`مع`subtract`أداة. قم بتوصيلها من لوحة المكتب كلود. تأكد من استلام المضيف الأداة الجديدة دون إعادة تشغيل بإصدار إشعار `tools/list_changed`الإخطار
2. **Medium.**إضافة`resource`الذي يعرض آخر 100 سطر من `/var/log/app.log`. تطبيق قائمة السماح الجذور حتى`../etc/passwd`يتم حجبها حتى لو طلبها النموذج
3. **Hard.**قم ببناء وكيل MCP يعدل ثلاثة خوادم فوقية (File System ، GitHub ، Postgres) إلى سطح واحد مجتمع. التعامل مع اصطدامات الأسماء والإتجاه المباشر `notifications/tools/list_changed`نظيفاً

## الشروط الرئيسية

| Term | What people say | What it actually means |
|------|-----------------|-----------------------|
| MCP | "Tool protocol for LLMs" | JSON-RPC 2.0 spec for exposing tools, resources, and prompts to any LLM host. |
| Host | "Claude Desktop" | The LLM application — owns the model and user UI, mounts one or more clients. |
| Client | "Connection" | A per-server connection inside the host that speaks JSON-RPC to exactly one server. |
| Server | "The thing with the tools" | Your code; advertises tools/resources/prompts and handles their invocation. |
| Tool | "Function call" | Model-invokable action with a JSON Schema input and a text/JSON result. |
| Resource | "Read-only data" | URI-addressed content (file, row, API response) the host can request. |
| Prompt | "Saved prompt" | User-invokable template (often with arguments) surfaced as a slash-command. |
| Stdio transport | "Local dev mode" | Parent host spawns the server as a child process; JSON-RPC over stdin/stdout. |
| Streamable HTTP | "The 2025-06 remote transport" | POST for requests, optional SSE for server-initiated messages; replaces the older SSE-only transport. |

## المزيد من القراءة

- [Model Context Protocol specification](https://modelcontextprotocol.io/specification) إشارة طائفية، نسخة حسب التاريخ.
- [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) نظام الملفات، GitHub، Postgres، Slack، Puppeteer خادم مرجعية.
- [Anthropic — Introducing MCP (Nov 2024)](https://www.anthropic.com/news/model-context-protocol) نقطة الإطلاق مع منطق التصميم.
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk) SDK الرسمي المستخدم في هذا الدروس.
- [Security considerations for MCP](https://modelcontextprotocol.io/docs/concepts/security)الجذور، الإشارات المدمرة، التسمم بالأدوات
- [Google A2A specification](https://a2a-protocol.org/latest/) بروتوكول Agent2Agent؛ معيار الأخوة للاتصال بين العملاء والوكلاء الذي يكمّل نطاق MCP من العميل إلى الأداة.
- [Anthropic — Building effective agents (Dec 2024)](https://www.anthropic.com/research/building-effective-agents) حيث يقع MCP في مكتبة النماذج الأوسع لتصميم الوكلاء (التربية القانونية المرتفعة، وتدفقات العمل، والوكلاء المستقلين).
