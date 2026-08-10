# أساسيات MCP  البدائيات، دورة الحياة، قاعدة JSON-RPC

> كل إدماج قبل (م.ك.بي) كان لمرة واحدة بروتوكول النموذجية للسياق، الذي أرسله شركة أنثروبيك لأول مرة في نوفمبر 2024، ويقوم الآن بإدارة مؤسسة "أجنتيك إيه إيه" لـ"لينكس" ، بتوحيد الاكتشاف والادعاء بحيث يمكن لأي عميل التحدث إلى أي خادم. تُسمي مواصفات 2025-11-25 ستة أسباب (ثلاثة خادمات، ثلاثة عملاء) ، ودورة حياة ثلاث مراحل، ونموذج أسلاك JSON-RPC 2.0. تعلم هذه و بقية الفصل من MCP في هذه المرحلة يصبح القراءة.

**Type:** Learn
**Languages:** Python (stdlib, JSON-RPC parser)
**Prerequisites:** Phase 13 · 01 through 05 (the tool interface and function calling)
**Time:** ~45 minutes

## أهداف التعلم

- أسمائ جميع أدوات MCP الأساسية الستة (الأدوات والموارد والإشارات على الخادم ؛ الجذور ، أخذ العينات ، الإجراءات على العميل) وقدم حالة استخدام واحدة لكل منها.
- قم بمشي خلال دورة الحياة الثلاثة مراحل (إطلاق، تشغيل، إيقاف) وذكر من يرسل أي رسالة في كل مرحلة.
- تحليل وإصدار غلافات طلبات وردات وإخطارات JSON-RPC 2.0.
- شرح ما هو التفاوض في القدرة`initialize`هو و ما ينكسر بدونها

## المشكلة

قبل MCP ، كان لكل وكيل يستخدم الأدوات بروتوكول خاص به. كان لدى Cursor نظام أدوات على شكل MCP غير متوافق. شحن Claude Desktop مع واحد مختلف. امتداد VS Code Copilot كان لديه ثالث. قام فريق قام ببناء أداة " Postgres query " بكتابة نفس الأداة ثلاث مرات ، كل مرة إلى API مختلفة من المضيف. احتجت إعادة استخدامه إلى نسخ الكود.

وكانت النتيجة انفجار كامبري من التكاملات المفردة و السقف على سرعة النظام البيئي.

تقوم MCP بتصديق هذا الأمر من خلال قياس تنسيق الشبكة. يعمل خادم MCP واحد في كل عميل MCP: Claude Desktop ، ChatGPT ، Cursor ، VS Code ، Gemini ، Goose ، Zed ، Windsurf ، 300 + عميل بحلول أبريل 2026. يتم تنزيل SDK شهريًا بمقدار 110 مليون. 10,000 + خادم عام. تولت مؤسسة Linux الإدارة في ديسمبر 2025 تحت مؤسسة Agentic AI الجديدة.

المواصفات المستخدمة في هذه المرحلة هي **2025-11-25**. يضيف مهام التزامن (SEP-1686) ، وإجراءات إعادة استخدام وضع URL (SEP-1036) ، ومعينة مع الأدوات (SEP-1577) ، وموافقة النطاق المتزايدة (SEP-835) ، و OAuth 2.1 رمزية مؤشر الموارد. المرحلة 13 · 09 إلى 16 تغطي هذه التوسعات. هذه الدروس تتوقف في الأساس.

## المفهوم

### ثلاثة خادمات بدائية

1. **Tools.**الإجراءات القابلة للدعوة نفس الحلقة من المرحلة 13 · 01.
2. **Resources.**البيانات المكشوفة. محتوى القراءة فقط قابل للتعريف بواسطة URI: `file:///path`،`db://query/...`، مخططات مخصصة
3. **Prompts.**القوالب قابلة للاستعمال. أوامر شاش في واجهة المستخدم المضيف؛ الخادم يوفر القوالب، والعميل يملأ الحجج.

### ثلاثة عملاء بدائيين

4. **Roots.**مجموعة من أوراي السماح للخادم باللمس. العميل يعلن عنهم؛ والخادم يحترمها.
5. **Sampling.**يطلب الخادم نموذج العميل لإجراء إكمال. يسمح بتشغيل حلقات وكيل مضيفة على الخادم دون مفاتيح API من جانب الخادم.
6. **Elicitation.**يطلب الخادم من مستخدم العميل إدخال مهيكلي في منتصف الرحلة. النماذج أو عناوين URL (SEP-1036).

كل قدرة في MCP تنتمي إلى واحدة من هذه الأجزاء السادسة بالضبط. المرحلة 13 · 10 إلى 14 تغطي كل واحدة عميقة.

### تنسيق الأسلاك: JSON-RPC 2.0

كل رسالة هي جسم JSON مع هذه الحقول:

- الطلبات:`{jsonrpc: "2.0", id, method, params}`. . .
- الإجابات: `{jsonrpc: "2.0", id, result | error}`. . .
- الإخطارات: `{jsonrpc: "2.0", method, params}`لا`id`لا يوجد رد متوقع

المواصفات الأساسية لديها 15 طريقة ، المجموعة من قبل البدائية.

- `initialize`- لا ، لا`initialized`(تصافيح يد)
- `tools/list`،`tools/call`
- `resources/list`،`resources/read`،`resources/subscribe`
- `prompts/list`،`prompts/get`
- `sampling/createMessage`(خادم إلى عميل)
- `notifications/tools/list_changed`،`notifications/resources/updated`،`notifications/progress`

### دورة حياة ثلاث مراحل

**Phase 1: initialize.**

العميل يرسل`initialize`مع`capabilities`و`clientInfo`الخادم يستجيب بمفرده`capabilities`،`serverInfo`و النسخة المحددة التي تتحدث بها العميل يرسل`notifications/initialized`من هنا فصاعداً، يمكن لأي طرف إرسال طلبات حسب القدرات المتفاوضة.

**Phase 2: operation.**

اتصالات العميل`tools/list`لاكتشافها، ثم `tools/call`الخادم قد يرسل`sampling/createMessage`إذا أعلنت هذه القدرة . قد يرسل الخادم`notifications/tools/list_changed`عندما يتغير مجموعة الأدوات العميل قد يرسل`notifications/roots/list_changed`عندما يغير المستخدم نطاق الجذر.

**Phase 3: shutdown.**

كل جانب يغلق النقل. لا توجد طريقة إيقاف مهيكلة في MCP؛ النقل (ستديو أو HTTP المباشر، المرحلة 13 · 09) يحمل إشارة نهاية الاتصال.

### التفاوض حول القدرة

`capabilities`في`initialize`اليدوية هو العقد. مثال من خادم:

```json
{
  "tools": {"listChanged": true},
  "resources": {"subscribe": true, "listChanged": true},
  "prompts": {"listChanged": true}
}
```

الخادم يعلن أنه يمكن أن يُبعث`tools/list_changed`الإخطارات والدعم `resources/subscribe`. العميل يوافق بإعلان نفسه:

```json
{
  "roots": {"listChanged": true},
  "sampling": {},
  "elicitation": {}
}
```

إذا لم يعلن العميل`sampling`، لا يجوز للخادم الاتصال`sampling/createMessage`التناظر: إذا لم يعلن الخادم`resources.subscribe`لا يجب على العميل أن يحاول الاشتراك

هذا ما يمنع الانحراف في النظام الإيكولوجي. العميل الذي لا يدعم أخذ العينات لا يزال عميل MCP صالحاً.`sampling`لا يزال خادم MCP صالحة.

### المحتوى المهيكلي وشكل الخطأ

`tools/call`يعود الـ`content`مجموعة من الكتل المخطوطة: `text`،`image`،`resource`. المرحلة 13 · 14 تضيف MCP Apps (`ui://`(UI) للتفاعل إلى تلك القائمة.

الخطأ يستخدم رموز الخطأ JSON-RPC. الإضافات المحددة حسب المواصفات: `-32002`"المورد لم يجد"`-32603`"خطأ داخلي"، بالإضافة إلى بيانات الخطأ الخاصة بمكسب`error.data`. . .

### قدرات العميل مقابل تفاصيل المكالمة في الأداة

خيبة أمل شائعة:`capabilities.tools`ما إذا كان العميل يدعم الإخطارات المتغيرة في قائمة الأدوات. ما إذا كان العميل سيستدع الأدوات المحددة هو خيار في الوقت التشغيلي الذي يقوده نموذجها ، وليس علامة قدرة. علامة قدرة هي عقد مستوى التفاصيل. اختيار النموذج هو محاكم.

### لماذا JSON-RPC وليس REST؟

JSON-RPC 2.0 (2010) هو بروتوكول خفيف ثنائي الاتجاه. REST هو المستهلك المبدع. MCP بحاجة إلى رسائل الخادم المبدع (مثالية، إشعارات) ، لذلك كان JSON-RPC مع شكله التوافقية طلب / رد مناسب طبيعي. JSON-RPC أيضا يكوّن نظيفا على ستديو و WebSocket / Streamable HTTP دون إعادة اختراع شكل طلب HTTP.

```figure
mcp-tool-call
```

## استخدمها

`code/main.py`يرسل قناة JSON-RPC 2.0 الحد الأدنى والمبعث ، ثم يذهب `initialize``tools/list``tools/call``shutdown`التسلسل باليد، طباعة كل رسالة. لا نقل حقيقي، فقط أشكال الرسالة. مقارنة مع المواصفات المرتبطة في القراءة المتقدمة للتحقق من كل غلاف.

ما الذي يجب أن ننظر إليه:

- `initialize`يعلن القدرات في كلا الطرقين ؛ الرد على ذلك`serverInfo`و`protocolVersion: "2025-11-25"`. . .
- `tools/list`يعود الـ`tools`صف: كل مدخل لديه`name`،`description`،`inputSchema`. . .
- `tools/call`استخدامات`params.name`و`params.arguments`. . .
- ردّها`content`هو مجموعة من`{type, text}`الكتل.

## أرسله

هذا الدرس يُنتج`outputs/skill-mcp-handshake-tracer.md`. بالنظر إلى نسخة على شكل pcap للتفاعل بين العميل والخادم MCP ، فإن المهارة تعليقاً لكل رسالة مع أي مرحلة بدائية ، ومرحلة دورة الحياة ، والقدرة التي تعتمد عليها.

## التمارين

1. أركض`code/main.py`تحديد الخط الذي يحدث فيه تفاوض القدرات ووصف ما الذي سيتغير إذا لم يعلن الخادم `tools.listChanged`. . .

2. تمديد المصفح للتعامل معه`notifications/progress`. شكل الرسالة:`{method: "notifications/progress", params: {progressToken, progress, total}}`إصدرها أثناء التشغيل الطويل`tools/call`و تأكد من أن المدير العميل سيظهر شريط تقدم

3. اقرأ المواصفات المحددة من أعلى إلى أسفل MCP 2025-11-25  المستند بأكمله حوالي 80 صفحة. حدد علامة القدرة الوحيدة التي لا تحتاجها معظم الخوادم. النصيحة: إنها تتعلق بتأمين الموارد.

4. رسم على الورق البدائية ميزة افتراضية "عمل cron" من شأنها أن تنتمي إلى. (لمحة: يريد الخادم من العميل استدعائه في وقت محدد. لا أحد من البدائيات الستة يناسب اليوم.) خريطة الطريق 2026 من MCP لديها مشروع SEP لهذا.

5. تحليل سجل جلسة واحدة من خادم MCP مفتوح على GitHub. احتساب طلب مقابل رد مقابل رسائل الإخطار. حساب ما هو جزء من حركة المرور مقابل العملية.

## الشروط الرئيسية

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| MCP | "Model Context Protocol" | Open protocol for model-to-tool discovery and invocation |
| Server primitive | "What a server exposes" | tools (actions), resources (data), prompts (templates) |
| Client primitive | "What a client lets servers use" | roots (scope), sampling (LLM callbacks), elicitation (user input) |
| JSON-RPC 2.0 | "The wire format" | Symmetric request/response/notification envelopes |
| `initialize` handshake | "Capability negotiation" | First message pair; servers and clients declare features they support |
| `tools/list` | "Discovery" | Client asks server for its current tool set |
| `tools/call` | "Invocation" | Client asks server to execute a tool with arguments |
| `notifications/*_changed` | "Mutation events" | Server tells client that its primitive list has changed |
| Content block | "Typed result" | `{type: "text" \| "image" \| "resource" \| "ui_resource"}` in tool result |
| SEP | "Spec Evolution Proposal" | Named draft proposal (e.g. SEP-1686 for async Tasks) |

## المزيد من القراءة

- [Model Context Protocol — Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) الوثيقة المحددة القنوية
- [Model Context Protocol — Architecture concepts](https://modelcontextprotocol.io/docs/concepts/architecture) النموذج العقلي الستة البدائية
- [Anthropic — Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) نوفمبر 2024 نقطة الإطلاق
- [MCP blog — First MCP anniversary](https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/) التراجع لمدة عام وتغييرات المواصفات 2025-11-25
- [WorkOS — MCP 2025-11-25 spec update](https://workos.com/blog/mcp-2025-11-25-spec-update) ملخص للـ SEP-1686 و 1036 و 1577 و 835 و 1724
