# الموارد والمطلوبات من MCP  التعرض السياقي خارج الأدوات

> تستخدم أدوات 90% من اهتمام MCP. يحلّ البدائيّة الأخرى الخادمين مشاكل مختلفة. الموارد تعرض البيانات للقراءة؛ وتعرض الأوامر الشكلات قابلة للاستخدام المتكرر كأوامر شظيفة. يجب على العديد من الخوادم استخدام الموارد بدلاً من إغلاق القراءة في الأدوات، والإلهام بدلاً من سيرات العمل القوية في طلبات العميل. يطلق هذا الدروس قاعدة القرار ويمشي على الوصول إلى القواعد.`resources/*`و`prompts/*`رسائل

**Type:** Build
**Languages:** Python (stdlib, resource + prompt handler)
**Prerequisites:** Phase 13 · 07 (MCP server)
**Time:** ~45 minutes

## أهداف التعلم

- قرر بين عرض القدرة كوسيلة أو مواردة أو طلب لنطاق معين.
- تنفيذ`resources/list`،`resources/read`،`resources/subscribe`و التعامل`notifications/resources/updated`. . .
- تنفيذ`prompts/list`و`prompts/get`مع نماذج الحجج.
- التعرف عندما يظهر المضيف الإشارات كإرشادات التقاط مقابل سياق حقن تلقائي.

## المشكلة

خادم MCP ساذج لتطبيق الملاحظات يضع كل شيء على غرار أدوات: `notes_read`،`notes_list`،`notes_search`هذا يحتوي على كل وصول إلى البيانات في دعوة أداة مدفوعة على النموذج.

- يجب على النموذج أن يقرر ما إذا كان سيتصل`notes_read`لكل استفسار قد يستفيد من السياق
- لا يمكن الاشتراك بالمحتوى القراءة فقط أو التدفق على لوحة الجانب المضيف.
- لا يمكن أن تظهر واجهات تعريف العميل (فؤر إصدار الموارد في Cloud Desktop ، ومختار "شمل الملف" في Cursor) البيانات.

الانقسام الأيمن: تعرض البيانات كمورد، تعرض الإجراءات المتحولة أو الحاسوبية كأدوات، تعرض تدفقات العمل متعددة الخطوات قابلة للاستعمال كإشارات. لكل شيء بدائي لديه إمكانية UX الخاصة به ونمط الوصول الخاص به.

## المفهوم

### أدوات مقابل الموارد مقابل الطلبات قاعدة القرار

| Capability | Primitive |
|------------|-----------|
| User wants to search, filter, or transform data | tool |
| User wants the host to include this data as context | resource |
| User wants a templated workflow they can re-run | prompt |

المبادئ التوجيهية: إذا كان النموذج يستفيد من استدعاءها في كل استفسار مرتبط، فهو أداة. إذا كان المستخدم يستفيد من ربطه إلى محادثة، فهو مصدر. إذا كان تدفق العمل متعدد الخطوات بأكمله هو الوحدة التي يريد المستخدم إعادة استخدامها، فهو طلب.

### الموارد

`resources/list`العائدات`{resources: [{uri, name, mimeType, description?}]}`. .`resources/read`يأخذ`{uri}`و العائدات`{contents: [{uri, mimeType, text | blob}]}`. . .

يمكن أن تكون الـ URI أي شيء يمكن إدراجه:

- `file:///Users/alice/notes/mcp.md`
- `postgres://my-db/query/SELECT ...`
- `notes://note-14`(نظام رسمي)
- `memory://session-2026-04-22/recent`(محدد للخادم)

`contents[]`يدعم كل من النص والبيناري.`blob`كسلسلة مقفورة بـ base64 + a `mimeType`. . .

### الاشتراك في الموارد

إعلان`{resources: {subscribe: true}}`في القدرات. مكالمات العميل`resources/subscribe {uri}`. الخادم يرسل`notifications/resources/updated {uri}`عندما يتغير المصدر العميل يقرأ مجدداً

حالة الاستخدام: خادم ملاحظات يحتوي على موارد على ملفات على القرص. مشرف ملف يطلق إشعارات تحديث. سحب Claude Desktop الملف مرة أخرى إلى السياق عند تحرير خارج المضيف.

### نماذج الموارد (2025-11-25 إضافة)

`resourceTemplates`دعك تعرض نمط URI المعلم: `notes://{id}`مع`id`يمكن للعميل إكمال هويات التعرف على الموارد بشكل تلقائي في اختيار الموارد.

### الإشارات

`prompts/list`العائدات`{prompts: [{name, description, arguments?}]}`. .`prompts/get`يأخذ`{name, arguments}`و العائدات`{description, messages: [{role, content}]}`. . .

الإشارة هي قالب يملأ قائمة من الرسائل التي يطعمها المضيف نموذجها. على سبيل المثال ، `code_review`الإستعارة تأخذ`file_path`الحجج وتعطي تسلسل ثلاث رسائل: رسالة النظام، رسالة المستخدم مع جسم الملف، ومساعد الابتداء مع نموذج التفكير.

### المضيفون والإشارات

كلود ديسكوب، VS Code، و Cursor تعرض الإشارات كإرشادات شقة في واجهة المحادثة. يكتب المستخدم `/code_review`ويحصل على الحجج من نموذج. استدعاء الخادم هو العقد بين "استخدم اختصار" و "استدعاء كامل المرسل إلى النموذج".

لا يدعم كل عميل الإشارات بعد  التفاوض على القدرة التحقق. يتم الإعلان عن خادم لديه القدرة السريعة ولكن العميل دون دعم سريع ببساطة لن يرى أوامر السلاش.

### إشعار "تغيير القائمة"

كل من الموارد والإشارات الإرسال`notifications/list_changed`عندما يتغير المجموعة، خادم الملاحظات الذي استورد 20 ملاحظة جديدة يصدر`notifications/resources/list_changed`العميل يستدعي`resources/list`لجمع الإضافات

### اتفاقيات نوع المحتوى

النص: `mimeType: "text/plain"`،`text/markdown`،`application/json`. . .
للثنائي: `image/png`،`application/pdf`، بالإضافة إلى`blob`المجال
للتطبيقات MCP (الدرس 14): `text/html;profile=mcp-app`في`ui://`(URI)

### الموارد الديناميكية

لا يجب أن تتوافق URI الموارد مع ملف ثابت. `notes://recent`يمكن أن تعيد أحدث خمسة ملاحظات في كل قراءة.`db://query/users/active`يمكن تنفيذ استفسار معين. الخادم حر في حساب المحتوى بشكل ديناميكي.

قاعدة: إذا كان العميل يمكن التخزين بواسطة URI، يجب أن يكون URI مستقرا. إذا كان الحسابات واحدة، يجب أن تتضمن URI طابع زمني أو غيره حتى لا يتبقى التخزين العميل.

### الاشتراك مقابل الاستطلاع

العملاء الذين يمكنهم الاشتراك يحصلون على دعم الخادم عبر `notifications/resources/updated`. العملاء أو المضيفين الذين لا يدعمونها استبيان عن طريق إعادة القراءة. كلاهما متوافق مع المواصفات. إعلان قدرة الخادم يخبر العميل الذي يدعم.

تكلفة الاشتراك: حالة كل جلسة على الخادم (من الذي يتم الاشتراك به ما). الحفاظ على مجموعة الاشتراك محدودة؛ يجب أن يقطع العملاء من الاتصال.

### الإشارات مقابل الإشارات النظامية

لا تكون الإشعارات في MCP إشعارات نظامية. إشعارات نظام المضيف (تعليمات تشغيل خاصة بها) وإشعارات MCP (القوالب المقدمة من الخادم التي يستدعيها المستخدم) تعيش جنبا إلى جنب. لا يسمح عميل جيد بالسيطرة على الخادم بإشعارات نظامية خاصة به؛ بل يضعها.

```figure
t3-primitive-sort
```

## استخدمها

`code/main.py`يطول خادم الملاحظات من الدروس 07 مع:

- الموارد لكل ملاحظة (`notes://note-1`، إلخ) مع `resources/subscribe`دعم
- أ`review_note`الإشارة التي تعطي نموذج ثلاث رسائل.
- محاكاة مراقب الملفات التي تنبعث`notifications/resources/updated`عندما يتم تعديل الملاحظة.
- أ`notes://recent`مصدر ديناميكي يعيد دائماً آخر خمسة أرقام

أطلقي الظهور لترى التدفق الكامل

## أرسله

هذا الدرس يُنتج`outputs/skill-primitive-splitter.md`نظراً لخادم MCP المقترح ، فإن المهارة تصنف كل قدرة كأداة / موارد / استشارة مع منطق.

## التمارين

1. أركض`code/main.py`. لاحظ قائمة الموارد الأولية ، ثم قم بتحرير الملاحظة والتحقق من `notifications/resources/updated`حوادث الحرائق

2. إضافة`resources/list_changed`المُصدِّر: عندما يتم إنشاء مذكرة جديدة، أرسل الإخطار حتى يجد العملاء مرة أخرى.

3. صمم ثلاث إشارات لخادم GitHub MCP: `summarize_pr`،`triage_issue`،`release_notes`كل منهما مع مخططات الحوارات يجب أن يكون الجسم السريع قابلاً للتشغيل دون إصدار آخر

4. خذ أداة موجودة في خادم الدروس 07 وتصنيف ما إذا كان يجب أن يبقى أداة أو يتم تقسيمها إلى زوج من الأدوات بالإضافة إلى الموارد. توجيه في جملة واحدة.

5. اقرأوا المواصفات`server/resources`و`server/prompts`أجزاء. حدد الحقل الواحد في `resources/read`هذا نادرًا ما يُعيش فيه الناس ولكن معتمدًا على المواصفات`_meta`على محتوى الموارد.

## الشروط الرئيسية

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

## المزيد من القراءة

- [MCP — Concepts: Resources](https://modelcontextprotocol.io/docs/concepts/resources) الموردات و URIs، الاشتراكات، والعلامات التشريعية
- [MCP — Concepts: Prompts](https://modelcontextprotocol.io/docs/concepts/prompts) نماذج سريعة ودمج القيادة
- [MCP — Server resources spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/resources) كامل `resources/*`إشارة الرسالة
- [MCP — Server prompts spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts) كامل `prompts/*`إشارة الرسالة
- [MCP — Protocol info site: resources](https://modelcontextprotocol.info/docs/concepts/resources/) دليل المجتمع في توسيع الوثائق الرسمية
