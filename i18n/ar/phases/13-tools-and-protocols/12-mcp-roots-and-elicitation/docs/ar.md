# الجذور والتحقيق  إدخال المستخدم في المجال ووسط الرحلة

> المسارات المقررة تعطل في اللحظة التي يفتح فيها المستخدم مشروعًا مختلفًا. تُفكّر حجج الأداة المملئة مسبقاً عندما يحدد المستخدم ما لا يُمكن. يطرح الجذر الخادم على مجموعة من URI التي يسيطر عليها المستخدم؛ توقف الإجراءات في منتصف المكالمة من أجل طلب المدخلات المهيكلة من المستخدم عبر نموذج أو عنوان URL. اثنين من العملاء البدائيين، اثنين من الإصلاحات لنظم فشل MCP الشائعة. SEP-1036 (تحقيق وضع URL، 2025-11-25) تجربي من خلال H1 2026  تحقق إصدارات SDK قبل الاعتماد عليه.

**Type:** Build
**Languages:** Python (stdlib, roots + elicitation demo)
**Prerequisites:** Phase 13 · 07 (MCP server)
**Time:** ~45 minutes

## أهداف التعلم

- إعلان`roots`و استجيب`notifications/roots/list_changed`. . .
- تقييد عمليات ملف الخادم إلى URI داخل مجموعة الجذر المعلنة.
- استخدام`elicitation/create`لطلب من المستخدم تأكيد أو إدخال مهيكلي في منتصف المكالمة.
- اختر بين وضع الشكل وإثارة وضع URL (الآخر تجربي؛ ملاحظة خطر التجول).

## المشكلة

هناك فشلتين ملموستين في إصدار الملاحظات التي يضربها خادم MCP في الإنتاج

**Broken path assumption.**الخادم مكتوب ضد`~/notes`. مستخدم على آلة مختلفة مع ملاحظات في `~/Documents/Notes`يحصل على مكالمة أداة تفشل بصمت (لا يوجد ملف) أو أسوأ من ذلك، كتبت إلى المكان الخطأ.

**Missing argument the user would know.**يطلب المستخدم "حذف مذكرة تقرير TPS القديمة".`notes_delete(title: "TPS report")`ولكن هناك ثلاث أوراق متطابقة من عام 2023 و 2024 و 2025 و لا يمكن أن تخمين أداة. فشل "مضطرب" أمر مزعج؛ ركوب على كل ثلاثة أمر كارثي.

الجذور تصحيح الأول: العميل يعلن على `initialize`مجموعة من URI التي يمكن أن يلمسها الخادم. إصلاح الإثارة يصلح الثاني: الخادم توقف مكالمة الأداة ويرسل `elicitation/create`لطلب من المستخدم أن يختار أي واحد.

## المفهوم

### الجذور

العميل يعلن قائمة جذرية على `initialize`:

```json
{
  "capabilities": {"roots": {"listChanged": true}}
}
```

يمكن للخادم أن يتصل بعد ذلك`roots/list`:

```json
{"roots": [{"uri": "file:///Users/alice/Documents/Notes", "name": "Notes"}]}
```

يجب على الخوادم التعامل مع الجذور على أنها الحدود: يتم رفض أي ملف يقرأ أو يكتب خارج مجموعة الجذور. لا يتم تطبيق هذا من قبل العميل (المستخدم لا يزال يثق في الشفرة) ، ولكن الخوادم المتوافقة مع المواصفات تكرمها.

عندما يضيف المستخدم أو يزيل الجذر، يقوم العميل بإرسال `notifications/roots/list_changed`. الخادم يعيد الاتصال`roots/list`ويحديث حدودها

### لماذا الجذور هي عميل بدائي

يتم إعلان الجذور من قبل العميل لأنها تمثل نموذج الموافقة للمستخدم. قال المستخدم لـ Claude Desktop "منح هذا الخادم ملاحظات الوصول إلى هذين الإداريين". لا يمكن للخادم توسيع نطاق ذلك.

### الإجراء: وضع النموذج الافتراضي

`elicitation/create`يأخذ مخطط النموذج بالإضافة إلى طلب لغة طبيعية:

```json
{
  "method": "elicitation/create",
  "params": {
    "message": "Delete 'TPS report'? Multiple notes match; pick one.",
    "requestedSchema": {
      "type": "object",
      "properties": {
        "note_id": {
          "type": "string",
          "enum": ["note-3", "note-7", "note-14"]
        },
        "confirm": {"type": "boolean"}
      },
      "required": ["note_id", "confirm"]
    }
  }
}
```

العميل يعطي النموذج، ويجمع إجابة المستخدم، ويرد:

```json
{
  "action": "accept",
  "content": {"note_id": "note-14", "confirm": true}
}
```

ثلاثة إجراءات محتملة:`accept`(المستخدم ملأها) ،`decline`(استخدم أغلقها) ،`cancel`(المستخدم ألغى كل مكالمة الأداة)

مخططات الشكل مسطحة  لا تدعم الأشياء المتعظمة في v1. عادة ما ترفض SDK أي شيء أكثر تعقيدا من طبقة واحدة.

### الإجراءات: وضع URL (SEP-1036، تجربي)

جديد في 2025-11-25. بدلاً من مخطط، سيرفر يرسل عنوان URL:

```json
{
  "method": "elicitation/create",
  "params": {
    "message": "Sign in to GitHub",
    "url": "https://github.com/login/oauth/authorize?client_id=..."
  }
}
```

يفتح العميل عنوان URL في متصفح ، وينتظر الانتهاء ، ويرد عندما يعود المستخدم. مفيد لتدفقات OAuth ، وافق على الدفع ، وقيع وثيقة عندما يكون النموذج غير كاف.

ملاحظة المخاطر المتجمدة: لا يزال شكل استجابة SEP-1036 مستقرًا؛ بعض SDKs تعيد عنوان URL للرد ، والبعض الآخر يعيد رمز الإكمال. اقرأ ملاحظات إطلاق SDK قبل استخدام وضع URL في الإنتاج.

### عندما يكون الإستفادة من ذلك هو الأداة الصحيحة

- تأكيد المستخدم قبل إجراءات مدمرة (لمحة مدمرة + إثارة).
- التشابه (اختر واحد من N مطابقات).
- إعداد التشغيل الأول (مفاتيح API، الإداريات، التفضيلات).
- تدفقات في نمط OAuth (وضع URL).

### عندما يكون الإستفادة خاطئة

- ملء الحجج المطلوبة من الأداة التي يمكن أن يكون النموذج طلبها في النص. استخدام إعادة الإشعار العادي، وليس حوار الإثارة.
- مكالمات عالية التردد. الإثارة تعيق المحادثة؛ لا تطلقها داخل حلقة.
- أي شيء يمكن أن يؤكد عليه الخادم بعد الحقيقة.

### جسر البشر في الحلقة

الإجراءات بالإضافة إلى أخذ العينات معاً تمكن من نموذج "الإنسان في الحلقة" في MCP. يمكن أن يتوقف حلقة العميل في خادم إما لدخل المستخدم (الإجراءات) أو التفكير في النموذج (الإجراءات). تغطي المرحلة 13 · 11 أخذ العينات. يغطي هذا الدروس الإجراءات. ضعها معاً للحكم الكامل في منتصف الحلقة.

```figure
t3-roots-boundary
```

## استخدمها

`code/main.py`يمتد خادم الملاحظات مع:

- `roots/list`ردّ الخادم الذي يستجوب بعد إشعارات تغيير قائمة الجذر.
- أ`notes_delete`أداة تستخدم`elicitation/create`لتحديد المناقضات عندما تتطابق ملاحظات متعددة.
- أ`notes_setup`أداة تستخدم إثارة وضع URL لفتح صفحة تشكيل أول تشغيل (مثبتة).
- التحقق من الحدود الذي يرفض العمليات على URI خارج الجذور المعلنة.

يقدم التجربة ثلاثة سيناريوهات: مسار سعيد (واحد مباراة) ، والتحليل (ثلاث مباريات ، وحرائق إثارة) ، والكتابة خارج الجذر (منفذ).

## أرسله

هذا الدرس يُنتج`outputs/skill-elicitation-form-designer.md`. بالنظر إلى أداة قد تحتاج إلى تأكيد المستخدم أو عدم التوضيح ، تصمم المهارة مخطط نموذج الطلب وتمثال الرسالة.

## التمارين

1. أركض`code/main.py`. تنشئ مسار التشكيكات ؛ تأكد من استرداد المستخدم المثالي إلى الأداة.

2. إضافة أداة جديدة `notes_archive`هذا يتطلب تأكيد الإثارة في كل مرة (ملاحظة مدمرة). تحقق من UX: كيف يُقارن هذا مع نموذج إعادة السؤال في النص؟

3. تنفيذ إثارة وضع URL لتدفق OAuth الأول. لاحظ خطر التجرف وإضافة حارس نسخة SDK.

4. التمديد`roots/list`التعامل: عند وصول الإخطار، يجب على الخادم إعادة قراءة وإعادة مسح الملفات المفتوحة التي قد تكون خارج نطاق الانتظار.

5. اقرأ موضوع بحث SEP-1036 على GitHub. حدد سؤال مفتوح يؤثر على كيفية التعامل مع استدعاءات الوسائط URL.

## الشروط الرئيسية

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Root | "Consent boundary" | URI the client has allowed the server to touch |
| `roots/list` | "Server asks for scope" | Client returns the current root set |
| `notifications/roots/list_changed` | "User changed scope" | Client signals the root set has mutated |
| Elicitation | "Ask the user mid-call" | Server-initiated request for structured user input |
| `elicitation/create` | "The method" | JSON-RPC method for elicitation requests |
| Form mode | "Schema-driven form" | Flat JSON Schema rendered as a form in the client UI |
| URL mode | "Browser redirect" | SEP-1036 experimental; opens a URL and waits |
| `accept` / `decline` / `cancel` | "User response outcomes" | Three branches the server handles |
| Disambiguation | "Pick one" | Common elicitation use case when a tool has N candidates |
| Flat form | "Top-level properties only" | Elicitation schemas cannot nest |

## المزيد من القراءة

- [MCP — Client roots spec](https://modelcontextprotocol.io/specification/draft/client/roots) إشارة الجذور القنونية
- [MCP — Client elicitation spec](https://modelcontextprotocol.io/specification/draft/client/elicitation) إشارة إثبات القنوني
- [Cisco — What's new in MCP elicitation, structured content, OAuth enhancements](https://blogs.cisco.com/developer/whats-new-in-mcp-elicitation-structured-content-and-oauth-enhancements) إضافة 2025-11-25
- [MCP — GitHub SEP-1036](https://github.com/modelcontextprotocol/modelcontextprotocol) اقتراح إثارة في وضع URL (تجريبية، مخاطر التجول)
- [The New Stack — How elicitation brings human-in-the-loop to AI tools](https://thenewstack.io/how-elicitation-in-mcp-brings-human-in-the-loop-to-ai-tools/) UX المشي
