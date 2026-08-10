# بناء خادم MCP  Python + TypScript SDKs

> معظم دروس المكالمات المكافحة تظهر فقط عالم التحية الاستثنائية خادم حقيقي يضع الأدوات بالإضافة إلى الموارد بالإضافة إلى الإشارات، ويعالج تفاوض القدرات، ويعرض أخطاء مهيكلة، ويعمل بنفس الطريقة عبر SDKs. هذه الدروس تبني خادم ملاحظات من نهاية إلى نهاية: نقل stdlib stdio، JSON-RPC إرسال، ثلاثة الخادم البدائية، ونمط وظيفة نقية التي تنزلق إما في FastMCP SDK Python أو SDK TypeScript عندما تخرج.

**Type:** Build
**Languages:** Python (stdlib, stdio MCP server)
**Prerequisites:** Phase 13 · 06 (MCP fundamentals)
**Time:** ~75 minutes

## أهداف التعلم

- تنفيذ`initialize`،`tools/list`،`tools/call`،`resources/list`،`resources/read`،`prompts/list`و`prompts/get`الأساليب
- اكتب حلقة إرسال تقرأ رسائل JSON-RPC من stdin وتكتب ردود فعل إلى stdout.
- إصدار استجابات الخطأ المهيكلة حسب مواصفات JSON-RPC 2.0 ورموز إضافية من MCP.
- تخرج تنفيذ stdlib إلى FastMCP (Python SDK) أو SDK TypeScript دون إعادة كتابة منطق الأداة.

## المشكلة

قبل أن تتمكن من استخدام النقل عن بعد (مرحلة 13 · 09) أو طبقة auth (مرحلة 13 · 16) ، تحتاج إلى خادم محلي نظيف. المحلي يعني stdio: يتم إنشاء الخادم من قبل العميل كعملية طفلية، وتدفق الرسائل عبر stdin/stdout newline-delimited.

تُقرر مواصفات 2025-11-25 أن رسائل الاستديو يتم ترميدها كموظف JSON مع صريح `\n`لا يوجد نظام SSE هنا ؛ كان SSE الوضع البعيد القديم ويتم إزاله في منتصف عام 2026 (خادم Rovo MCP في Atlassian قد أُساعد عليه في 30 يونيو 2026 ؛ Keboola في 1 أبريل 2026) . بالنسبة للستديو ، فإن جسم JSON واحد لكل سطر هو شكل الأسلاك بالكامل.

خادم الملاحظات هو شكل جيد لأنه يمارس كل ثلاثة أسباب الخادم.`notes_create`الموارد تعرض البيانات (`notes://{id}`) تُطلب من قوالب السفن (`review_note`صيغة هذا الدروس تعاملت إلى أي مجال.

## المفهوم

### حلقة الإرسال

```
loop:
  line = stdin.readline()
  msg = json.loads(line)
  if has id:
    handle request -> write response
  else:
    handle notification -> no response
```

ثلاثة قواعد:

- لا تطبع أي شيء إلى stdout ليس لفافة JSON-RPC. سجلات إزالة التشغيل تذهب إلى stderr.
- كل طلب يجب أن يطابق مع رد يحمل نفس`id`. . .
- لا يجوز الرد على الإخطارات

### تنفيذ`initialize`

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

أعلن فقط ما تدعمه العميل يعتمد على القدرة المحددة لميزات البوابة

### تنفيذ`tools/list`و`tools/call`

`tools/list`العائدات`{tools: [...]}`مع كل مدخل ذو `name`،`description`،`inputSchema`. .`tools/call`يأخذ`{name, arguments}`و العائدات`{content: [blocks], isError: bool}`. . .

يتم كتابة كتب كتب المحتوى. الأكثر شيوعاً:

```json
{"type": "text", "text": "Found 2 notes"}
{"type": "resource", "resource": {"uri": "notes://14", "text": "..."}}
{"type": "image", "data": "<base64>", "mimeType": "image/png"}
```

تظهر أخطاء أداة في شكلين. يتم إرجاع أخطاء مستوى البروتوكول (الوسيلة غير المعروفة ، والفوارم السيئة) على أنها أخطاء JSON-RPC. يتم إرجاع أخطاء مستوى الأداة (الدعوة الصالحة ولكن فشل الأداة) على النحو:`{content: [...], isError: true}`هذا يسمح للنموذج أن يرى الفشل في سياقه

### الموارد التنفيذية

الموارد القراءة فقط من خلال التصميم.`resources/list`يعيد بياناً`resources/read`يعيد المحتوى. يمكن أن تكون`file://...`،`http://...`أو مخططات مخصصة مثل`notes://`. . .

عندما تعرض البيانات كمورد بدلاً من أداة:

- النموذج لا "يطلب" ذلك، يمكن للعميل حقنها في السياق بناء على طلب المستخدم.
- الإشتراكات تسمح للخادم بإعادة تحديثات عندما يتغير الموارد (المرحلة 13 · 10).
- المرحلة 13 · 14 تمتد هذا مع `ui://`للموارد التفاعلية.

### الإشارات التنفيذية

الإشارات هي نماذج مع حجج مسموح بها. يظهرها المضيف كأوامر شقة.`review_note`الإستعارة قد تستغرق`note_id`الحجة ووضع نموذج استشارة متعددة الرسائل يطعم العميل نموذجها.

### أخفاف النقل

- لا يوجد إطار معتمد على الطول
- لا تُضغط.`sys.stdout.flush()`بعد كل كتابة
- العميل يتحكم في مدة الحياة عندما يغلق (إيهف) ، اخرج نظيفاً
- لا تتعامل مع SIGPIPE بصمت، إدخال وتخروج.

### الملاحظات

كل أداة يمكن أن تحمل`annotations`تصف خصائص السلامة:

- `readOnlyHint: true`قراءة نقية آمنة للمحاولة مرة أخرى
- `destructiveHint: true` آثار جانبية لا رجعة فيها، يجب أن يؤكد العميل.
- `idempotentHint: true` نفس المدخلات تنتج نفس المخرجات.
- `openWorldHint: true`يتفاعل مع الأنظمة الخارجية.

يستخدم العميل هذه لتحديد UX (حوارات التأكيد ومؤشرات الحالة) والتوجه (المرحلة 13 · 17).

### طريق التخرج

خادم ستديلب في`code/main.py`و هو حوالي 180 خطا. FastMCP (Python) ينهار نفس المنطق إلى نمط الديكور:

```python
from fastmcp import FastMCP
app = FastMCP("notes")

@app.tool()
def notes_search(query: str, limit: int = 10) -> list[dict]:
    ...
```

يحتوي SDK TypeScript على شكل مماثل. مسار التخرج هو التسجيل عندما تكون جاهزًا. المفاهيم (القدرات، الرسائل، كتلة المحتوى) هي نفسها.

```figure
t3-dispatch-loop
```

## استخدمها

`code/main.py`هو خادم الملاحظات المكملة على الاستديو فقط`initialize`،`tools/list`،`tools/call`لثلاث أدوات (`notes_list`،`notes_search`،`notes_create`()`resources/list`و`resources/read`لكل ملاحظة و`review_note`يمكنك تشغيله عن طريق توجيه رسائل JSON-RPC:

```
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python main.py
```

ما الذي يجب أن ننظر إليه:

- المُرسل هو`dict[str, Callable]`المفتاح باسم الطريقة.
- كل أداة تنفيذية يعود قائمة من حظر المحتوى، وليس سلسلة عريضة.
- `isError: true`يتم تحديدها عندما يرفع المفعول.

## أرسله

هذا الدرس يُنتج`outputs/skill-mcp-server-scaffolder.md`. وبالنظر إلى نطاق (الملاحظات والبطاقات والملفات، قاعدة البيانات) ، فإن المهارات تقوم بتوفير خادم MCP مع الأدوات / الموارد / الطلبات المناسبة تقسيم ومرحلة التخرج من SDK.

## التمارين

1. أركض`code/main.py`ويقودها مع رسائل JSON-RPC التي بنيت يدويا.`notes_create`، ثم`resources/read`لاسترداد الرسالة الجديدة

2. إضافة`notes_delete`أداة مع `annotations: {destructiveHint: true}`. التحقق من أن العميل سوف يظهر حوار التأكيد (هذا يتطلب مضيف حقيقي؛ كلود مكتب يعمل).

3. تنفيذ`resources/subscribe`لذا الخادم يدفع`notifications/resources/updated`كلما تم تعديل ملاحظة إضافة مهمة حافظة

4. نقل الخادم إلى FastMCP. يجب أن تقلص ملف Python إلى أقل من 80 سطر. يجب أن يكون سلوك الأسلاك متطابقًا. التحقق من نفس القائمة الاختبارية JSON-RPC.

5. اقرأوا المواصفات`server/tools`القسم وتحديد حقل واحد من تعريف الأداة غير تنفيذ في خادم هذا الدروس. (تلميح: هناك العديد؛ اختيار واحد وإضافة ذلك.)

## الشروط الرئيسية

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

## المزيد من القراءة

- [Model Context Protocol — Python SDK](https://github.com/modelcontextprotocol/python-sdk) تنفيذ Python المرجعي
- [Model Context Protocol — TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) تنفيذ نظام التشغيل المتوازي
- [FastMCP — server framework](https://gofastmcp.com/) API Python على طراز المزيج لخادمات MCP
- [MCP — Quickstart server guide](https://modelcontextprotocol.io/quickstart/server) دراسة نهاية إلى نهاية باستخدام أي من SDK
- [MCP — Server tools spec](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) إشارة كاملة للأدوات/* الرسائل
