# مهام غير متزامنة (SEP-1686)  اتصل الآن، احضر لاحقاً للعمل الطويل المدى

> العمل الحقيقي للعملاء يستغرق دقائق إلى ساعات: عمليات إحصاءات، وتوليد البحوث العميقة، صادرات اللحوم. أداة متزامنة تدعو إيقاف الاتصالات، وقت، أو حظر واجهة المستخدم. يضيف SEP-1686 ، الذي تم دمجها في 2025-11-25 ، مسؤولية مسألة بدائية: يمكن تكبير أي طلب ليصبح مهمة ، ويمكن الحصول على النتيجة في وقت لاحق أو التدفق عبر إشعارات الدولة. ملاحظة المخاطر المتجمدة: المهام تجربية خلال فترة الـ1 من عام 2026؛ لا يزال يتم تصميم سطح SDK حول المواصفات.

**Type:** Build
**Languages:** Python (stdlib, async task state machine)
**Prerequisites:** Phase 13 · 07 (MCP server), Phase 13 · 09 (transports)
**Time:** ~75 minutes

## أهداف التعلم

- تحديد متى يجب تعزيز أداة من متزامنة إلى مهام مزيدة (> 30 ثانية من العمل على جانب الخادم).
- إمتحان دورة حياة المهمة: `working``input_required``completed`- لا ، لا`failed`- لا ، لا`cancelled`. . .
- حالة المهمة مستمرة حتى لا تفقد الحوادث العمل أثناء الرحلة
- استطلاع`tasks/status`و أحضر`tasks/result`صحيحاً

## المشكلة

أ`generate_report`أداة تشغيل خط أنابيب استخراج متعددة الدقائق. الخيارات تحت نموذج متزامن:

1. أبقوا الاتصال مفتوحاً لمدة ثلاث دقائق، وسوف يُسقط النقل عن بعد، ويقضي الزبائن وقتًا، ويتجمد المستخدمون.
2. عودوا فوراً مع مؤشر مكان، وطلبوا من العميل أن يستطلع نقطة نهاية مخصصة.
3. أطلق النار ونساها، لا نتيجة

لا يوجد أي منها جيد. SEP-1686 يضيف رابعًا: زيادة المهام. أي طلب (عادةً`tools/call`يمكن وضع علامة على المهام. يقوم الخادم بإرجاع هوية المهام على الفور. يقوم العميل بإجراء استطلاعات `tasks/status`و التقطات`tasks/result`عندما يتم، حالة جانب الخادم تنجو من إعادة تشغيل

## المفهوم

### زيادة المهام

تصبح الطلب مهمة عن طريق تحديد`params._meta.task.required: true`(أو `optional: true`الجهاز يستجيب على الفور:

```json
{
  "jsonrpc": "2.0", "id": 1,
  "result": {
    "_meta": {
      "task": {
        "id": "tsk_9f7b...",
        "state": "working",
        "ttl": 900000
      }
    }
  }
}
```

`ttl`هو وعد الخادم بالحفاظ على حالة؛ بعد ttl يتم التخلص من نتيجة المهمة.

### اختيار لكل أداة

يمكن أن تعلن إشارات الأدوات دعم المهام:

- `taskSupport: "forbidden"` هذه الأداة تعمل دائماً بالتزامن. آمنة للأدوات السريعة.
- `taskSupport: "optional"` يمكن للعميل طلب زيادة المهام.
- `taskSupport: "required"` العميل يجب أن يستخدم تكبير المهام.

أ`generate_report`أداة سيكون`required`.`notes_search`أداة سيكون`forbidden`. . .

### الدول

```
working  -> input_required -> working  (loop via elicitation)
working  -> completed
working  -> failed
working  -> cancelled
```

آلة الدولة هي إضافة فقط: مرة واحدة `completed`،`failed`أو`cancelled`المهمة هي نهائية

### الأساليب

- `tasks/status {taskId}`يعيد الحالة الحالية و إشارة إلى التقدم.
- `tasks/result {taskId}` يمنع أو يعيد 404 إذا لم يتم ذلك بعد.
- `tasks/cancel {taskId}` غير قادر؛ ولايات نهائية تجاهل.
- `tasks/list` اختياري؛ يُدرج المهام النشطة والتي تم إنجازها مؤخراً.

### تغييرات حالة التدفق

عندما يدعم الخادم ذلك، يمكن للعميل الاشتراك في الإخطارات الحكومية:

```
server -> notifications/tasks/updated {taskId, state, progress?}
```

العملاء الذين يُشغلون البث بدلاً من إجراءات الاستطلاع يحصلون على تجربة أفضل. يتم دعم الاستطلاع دائمًا كمنطقة أقل.

### حالة دائمة

يتطلب المواصفات الخوادم التي تعلن دعم المهام للحفاظ على حالة. لا ينبغي أن يفقد حادث النتائج المكتملة داخل ttl. التخزينات تتراوح من SQLite إلى Redis إلى نظام الملفات. تستخدم نظام الملفات دراسة 13.

### تعبيرات الإلغاء

`tasks/cancel`إذا كانت المهمة في منتصف الإجراء، يحاول الخادم التوقف (تحقق من إلغاء التعاون مع المنفذ). إذا كانت بالفعل محطة، فإن الطلب غير عملي.

### التعافي من الحوادث

عند إعادة تشغيل عملية الخادم:

1. تحميل جميع حالات المهمة المستمرة.
2. - قم بتسجيل أيّة`working`المهام التي ماتت عمليةها`failed`مع خطأ`CRASH_RECOVERY`. . .
3. الحفاظ على`completed`- لا ، لا`failed`- لا ، لا`cancelled`لأجل أفعالهم

### مهام التزامن بالإضافة إلى أخذ العينات

المهمة يمكن أن تطلب نفسها`sampling/createMessage`. هكذا تعمل مهام البحث طويلة الأمد: خيط المهام في الخادم يظهر نموذج العميل حسب الحاجة، بينما يظهر واجهة المستخدم العميل على النحو `working`مع تحديثات دورية للتقدم.

### لماذا هذا تجربي

تم إرسال SEP-1686 في 2025-11-25 ولكن الخريطة الوسيعة تدعو إلى ثلاثة قضايا مفتوحة: البدائيات الاستعانة الدائمة ، والمهام الفرعية (علاقات مهام الوالدين والطفل) ، وتوحيد نتائج TTL. تتوقع أن يتطور المواصفات حتى عام 2026. يجب أن يعامل رمز الإنتاج المهام باعتبارها مستقرة فقط للقضية المشتركة والحماية من تغييرات SDK المستقبلية للمهام الفرعية.

```figure
tp-task-lifecycle
```

## استخدمها

`code/main.py`ينفذ مخزن مهمة قوي (دعم من قبل النظام الملفي) و `generate_report`أداة تعمل في خيط خلفي العملاء يطلبون الأداة، يحصلون على معرف المهمة على الفور، استطلاع `tasks/status`بينما يعمل العامل يقوم بتحديث التقدم، والحصول على`tasks/result`عندما يتم إبطال العمل، يتم محاكاة استرداد الحادث عن طريق إيقاف خيط العامل وإعادة تحميل الحالة.

ما الذي يجب أن ننظر إليه:

- حالة المهمة JSON استمرت إلى `/tmp/lesson-13-tasks/<id>.json`. . .
- تحديثات حلقة العمال`progress`في مجال التنمية، الاستطلاع يظهر أنها تتقدم.
- الإلغاء من جانب العميل يحدد حدثاً، العامل يبحث و يغادر مبكراً.
- إعادة تحميل الدولة على "الصدمة" تمثل مهمة الطيران`failed`مع`CRASH_RECOVERY`. . .

## أرسله

هذا الدرس يُنتج`outputs/skill-task-store-designer.md`. بالنظر إلى أداة طويلة الأمد (البحث، البناء، التصدير) ، تصميم المهارة مخزن المهام (شكل الحالة، التلفزيون، الاستدامة) ، واختيار المهمة الصحيحةدعم العلم، وخطوط إخطارات التقدم.

## التمارين

1. أركض`code/main.py`أطلقوا`generate_report`المهمة، حالة الاستطلاع، ثم الحصول على النتيجة.

2. إضافة`tasks/cancel`اتصلوا بالمركز المتوسط للتأكد من أن العامل يحترمها والولاية تصبح`cancelled`. . .

3. محاكاة استعادة الحوادث: إيقاف خيط العامل، إعادة تشغيل الشحن، ومراقبة `CRASH_RECOVERY`وضع الفشل

4. تمديد المخزن إلى SQLite. انتصارات الاستمرارية هي نفسها؛ تختلف خيارات الاستفسار (قائمة جميع المهام من الجلسة X).

5. اقرأ رسالة خريطة الطريق لمؤسسة المشاريع المشتركة لعام 2026، حدد المشكلة المفتوحة ذات الصلة بالمهام التي من المرجح أن تؤثر على تصميم API SDK في العام المقبل.

## الشروط الرئيسية

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Task | "Long-running tool call" | Request augmented with `_meta.task` for async execution |
| SEP-1686 | "Tasks spec" | Spec Evolution Proposal that added Tasks in 2025-11-25 |
| `_meta.task` | "Task envelope" | Per-request metadata containing id, state, ttl |
| taskSupport | "Tool flag" | `forbidden` / `optional` / `required` per tool |
| `tasks/status` | "Poll method" | Fetch current state and optional progress hint |
| `tasks/result` | "Fetch result" | Returns the completed payload or 404 if not yet done |
| `tasks/cancel` | "Stop it" | Idempotent cancellation request |
| ttl | "Retention budget" | Milliseconds the server promises to keep the task state |
| `notifications/tasks/updated` | "State push" | Server-initiated state-change event |
| Durable store | "Crash-safe state" | Filesystem / SQLite / Redis persistence layer |

## المزيد من القراءة

- [MCP — GitHub SEP-1686 issue](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1686) الاقتراح الأصلي والمناقشة الكاملة
- [WorkOS — MCP async tasks for AI agent workflows](https://workos.com/blog/mcp-async-tasks-ai-agent-workflows) تصميم المشي مع المنطق
- [DeepWiki — MCP task system and async operations](https://deepwiki.com/modelcontextprotocol/modelcontextprotocol/2.7-task-system-and-async-operations)الميكانيكا و آلة الدولة
- [FastMCP — Tasks](https://gofastmcp.com/servers/tasks) أنماط تنفيذ المهام على مستوى SDK
- [MCP blog — 2026 roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) القضايا المفتوحة والأولويات لعام 2026 بما في ذلك المهام الفرعية
