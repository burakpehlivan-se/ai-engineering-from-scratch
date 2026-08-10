# عينة المملكة المتحدة للبرامج  استكمالات الـ LLM التي يطلبها الخادم وخطوط العميل

> معظم خوادم MCP هي مُنفذات غبية: تأخذ الحجج، تشغيل الشفرة، تعيد المحتوى. يسمح الاختبار بالخادم بتغيير الاتجاه: يطلب من ماجستير العلوم العميل اتخاذ قرار. هذا يسمح لـ خادم المضيف حلقات وكيل دون الخادم تمتلك أي أوراق اعتماد نموذج. إضافة SEP-1577، التي دمجت في 2025-11-25، أدوات داخل طلبات أخذ العينات حتى يمكن أن يتضمن الحلقة التفكير العميق. ملاحظة المخاطر المتجمدة: أداة SEP-1577 في شكل العينات كانت تجربية حتى الربع الأول من عام 2026 وما زالت تستقر في APIs SDK.

**Type:** Build
**Languages:** Python (stdlib, sampling harness)
**Prerequisites:** Phase 13 · 07 (MCP server), Phase 13 · 10 (resources and prompts)
**Time:** ~75 minutes

## أهداف التعلم

- اشرح ما الذي`sampling/createMessage`يحل (حلقات تستضيف الخادم دون مفاتيح API على جانب الخادم).
- تنفيذ خادم يطلب من العميل أن يختار عبر طلب متعدد التحولات ويرد الإكمال.
- استخدام`modelPreferences`(التكلفة / السرعة / الأولويات الاستخباراتية) لتوجيه اختيار نموذج العميل.
- بناء `summarize_repo`أداة تتكرر داخلياً عن طريق أخذ العينات بدلاً من سلوك التشفير الصلب.

## المشكلة

يجب على خادم MCP مفيد لتدفق عمل لجمع الكود: المشي شجرة الملفات، اختيار الملفات التي تقرأها، وتجميع ملخص، والعودة. أين يحدث التفكير LLM؟

الخيار الأول: الخادم يدعو لجامعة الشراكة الخاصة به. يحتاج مفتاح API، فاتورة جانب الخادم، هو مكلف لكل مستخدم.

الخيار ب: يعيد الخادم المحتوى الخام، وكيل العميل يقوم بالبرأى. يعمل ولكن ينقل منطق الخادم إلى طلب العميل، وهو هش.

الخيار ج: يطلب الخادم ماجستير الشراكة للعميل عبر `sampling/createMessage`يحتفظ الخادم بالخوارزمية (أي ملفات يجب قراءتها، كم مرسلات يجب إجراؤها) بينما يحتفظ العميل بالفواتير واختيار النموذج. لا يوجد لدى الخادم أي إثباتات على الإطلاق.

الخيار C هو العينات. إنه الآلية التي يمكن من خلالها أن يستضيف الخادم الموثوق به حلقة الوكيل دون أن يكون مستضيفًا كاملًا لـ LLM نفسه.

## المفهوم

### `sampling/createMessage`الطلب

الخادم يرسل:

```json
{
  "jsonrpc": "2.0",
  "id": 42,
  "method": "sampling/createMessage",
  "params": {
    "messages": [{"role": "user", "content": {"type": "text", "text": "..."}}],
    "systemPrompt": "...",
    "includeContext": "none",
    "modelPreferences": {
      "costPriority": 0.3,
      "speedPriority": 0.2,
      "intelligencePriority": 0.5,
      "hints": [{"name": "claude-3-5-sonnet"}]
    },
    "maxTokens": 1024
  }
}
```

العميل يدير ماجستير القانون، يعود:

```json
{"jsonrpc": "2.0", "id": 42, "result": {
  "role": "assistant",
  "content": {"type": "text", "text": "..."},
  "model": "claude-3-5-sonnet-20251022",
  "stopReason": "endTurn"
}}
```

### `modelPreferences`

ثلاثة طائرات تصل إلى 1.0:

- `costPriority`: يفضلون النماذج الرخيصة
- `speedPriority`: تفضل النماذج الأسرع.
- `intelligencePriority`: يفضلون النماذج الأكثر قدرة

بالإضافة إلى ذلك`hints`: أساليب المستخدم المفضل. قد يحترم العميل أو لا يحترم الإشارات؛ إعداد المستخدم للعميل يفوز دائمًا.

### `includeContext`

ثلاثة قيم:

- `"none"`فقط الرسائل المقدمة من الخادم.
- `"thisServer"` تشمل الرسائل السابقة من جلسة هذا الخادم.
- `"allServers"` تشمل جميع سياقات الجلسة.

`includeContext`يُعتبر هذا النظام منخفضًا بشكل ملحوظ اعتبارًا من 2025-11-25 لأنه يسرق السياق عبر الخادم، وهو ما يشكل مخاوف أمنية.`"none"`و إرسال السياق المبرر في الرسائل

### أخذ العينات بالأدوات (SEP-1577)

جديد في 2025-11-25: طلب أخذ العينات يمكن أن يتضمن`tools`المستخدم يدير حلقة كاملة للدعوة باستخدام هذه الأدوات. وهذا يسمح للخادم استضافة حلقة وكيل في نمط ReAct من خلال نموذج العميل.

```json
{
  "messages": [...],
  "tools": [
    {"name": "fetch_url", "description": "...", "inputSchema": {...}}
  ]
}
```

حلقات العميل: عينة، أداة تنفيذ إذا تم الاتصال، عينة مرة أخرى، عودة رسالة المساعد النهائي. هذا تجربي حتى Q1 2026; قد لا تزال توقيعات SDK تتحرك. تأكد من قسم العميل / العينة الخاصة بتفصيل 2025-11-25 عند تنفيذ.

### البشر في الحلقة

يجب على العميل أن يظهر للمستخدم ما يطلب منه الخادم من النموذج قبل تشغيل العينة. يمكن لخادم ضار استخدام العينة للتلاعب بمجلسة المستخدم ("قل X للمستخدم حتى ينقر على Y"). طلبات عينة سطح كلود ديسكوب و VS Code و Cursor كحوار تحديد يمكن للمستخدم رفض.

الإجماع عام 2026: أخذ العينات دون تأكيد بشري هو علامة حمراء. يمكن لبرامج البوابة (المرحلة 13 · 17) أن تمتلك الموافقة التلقائية على أخذ العينات منخفضة المخاطر وتنفيذ أي شيء مشبوه.

### حلقات استضافة الخادم بدون مفاتيح API

حالة الاستخدام القنوني: خادم MCP لجمع الرمز بدون وصول LLM الخاص به.

1. إمشي على هيكل الإستعراض
2. اتصل`sampling/createMessage`مع "اختر خمسة ملفات على الأرجح لتصف الغرض من هذا الاستعلام".
3. اقرأ تلك الملفات
4. اتصل`sampling/createMessage`مع محتوى الملفات و "الجمع في 3 فقرات".
5. أعد الموجب كـ `tools/call`النتيجة

الخادم لا يلمس أبداً API LLM. مستخدم العميل يدفع مقابل الإكمال باستخدام إثباتاتهم الخاصة.

### مخاطر السلامة (كشف الوحدة 42، فصل 2026)

- **Covert sampling.**أداة تدعو دائماً إلى أخذ العينات "استجيب بريد إلكتروني المستخدم من سياق الجلسة". المرحلة 13 · 15 تغطي متجهات الهجوم.
- **Resource theft via sampling.**الخادم يطلب من العميل أن يجمع حمولة المهاجم، ويفرض الفواتير للمستخدم.
- **Loop bombs.**الخادم يدعو للاستعراض في حلقة ضيقة العملاء يجب أن يفرضوا حدود معدل الجلسة الواحدة

```figure
t3-sampling-flip
```

## استخدمها

`code/main.py`يرسل خادم مزيف إلى العميل خيط أخذ العينات. أداة محاكاة "summarize_repo" تستدعي جولتين من أخذ العينات (ملفات اختيار، ثم التجميع) ، ويعود العميل المزيف إلى استجابات محتفظة. يظهر الخيط:

- الخادم يرسل`sampling/createMessage`مع`modelPreferences`. . .
- العميل يعيد الإكمال
- الخادم يستمر في حلقة.
- حدد الحد من التكلفة يحدد إجمالي دعوات العينات لكل دعوة لأداة.

ما الذي يجب أن ننظر إليه:

- الخادم يعرض أداة واحدة فقط (`summarize_repo`كل التفكير يحدث في دعوات أخذ العينات.
- تفضيلات النموذج تعزز اختيار النموذج للعميل؛ وتقوم الإشارات بإدراج النماذج المفضلة.
- الحلقة تنتهي`stopReason: "endTurn"`. . .
- - نعم`max_samples_per_tool = 5`الحد يلتقط حلقة هرب

## أرسله

هذا الدرس يُنتج`outputs/skill-sampling-loop-designer.md`. بالنظر إلى خوارزمية جانب الخادم التي تحتاج إلى دعوات LLM (البحث والإجمالة والتخطيط) ، تصمم المهارة تنفيذًا قائمًا على العينات مع النموذج المناسب.

## التمارين

1. أركض`code/main.py`تغيير`max_samples_per_tool`إلى 2 ولاحق حد حد حد السعر.

2. تنفيذ نوع أداة "SEP-1577" في أخذ العينات: طلب أخذ العينات يحمل`tools`المجموعة. التحقق من أن حلقة جانب العميل تنفذ هذه الأدوات قبل إعادة الانتهاء النهائي. لاحظ خطر التنقل: قد تتغير توقيعات SDK حتى H1 2026.

3. إضافة تأكيد البشر في الحلقة: قبل أول خادم `sampling/createMessage`، توقف وانتظر موافقة المستخدم. مكالمات رفض تعيد رفض منخفض.

4. إضافة حدّة معدلات لكل مستخدم معدة حسب جلسة العميل. يجب أن تشارك حلقات نفس الخادم من قبل نفس المستخدم ميزانية.

5. تصميم`summarize_pdf`أداة تستخدم العينات لتحديد قطع لتشمل. رسم الرسائل المرسلة. كيف يتم`modelPreferences.intelligencePriority`تغيير السلوك عند 0.1 مقابل 0.9؟

## الشروط الرئيسية

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Sampling | "Server-to-client LLM call" | Server asks client's model for a completion |
| `sampling/createMessage` | "The method" | JSON-RPC method for sampling requests |
| `modelPreferences` | "Model priorities" | Cost / speed / intelligence weights plus name hints |
| `includeContext` | "Cross-session leakage" | Soft-deprecated context inclusion mode |
| SEP-1577 | "Tools in sampling" | Allow tools inside sampling for server-hosted ReAct |
| Human-in-the-loop | "User confirms" | Client surfaces sampling request to user before running |
| Loop bomb | "Runaway sampling" | Server-side infinite sampling loop; client must rate-limit |
| Covert sampling | "Hidden reasoning" | Malicious server hides intent in sampling prompts |
| Resource theft | "Using user's LLM budget" | Server forces client to spend on sampling it does not want |
| `stopReason` | "Why generation halted" | `endTurn`, `stopSequence`, or `maxTokens` |

## المزيد من القراءة

- [MCP — Concepts: Sampling](https://modelcontextprotocol.io/docs/concepts/sampling) نظرة عامة على مستوى عال عن أخذ العينات
- [MCP — Client sampling spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/client/sampling) القنوني `sampling/createMessage`الشكل
- [MCP — GitHub SEP-1577](https://github.com/modelcontextprotocol/modelcontextprotocol) تطور المواصفات اقتراح لأدوات في أخذ العينات (تجريبية)
- [Unit 42 — MCP attack vectors](https://unit42.paloaltonetworks.com/model-context-protocol-attack-vectors/) أنماط أخذ العينات السرية وسرقة الموارد
- [Speakeasy — MCP sampling core concept](https://www.speakeasy.com/mcp/core-concepts/sampling) التدقيق مع عينات رمزية من جانب العميل
