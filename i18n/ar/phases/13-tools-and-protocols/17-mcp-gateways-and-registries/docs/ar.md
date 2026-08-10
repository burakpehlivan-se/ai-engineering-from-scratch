# بوابات و سجلات MCP  طائرات التحكم في المؤسسات

> لا يمكن للمؤسسات أن تسمح لكل مطور بتثبيت خادمات MCP عشوائية. يقوم بوابة مركزية على auth، RBAC، المراجعة، الحد من المعدلات، التخزين الآلي، وكشف التسمم الأداة، ثم يعرض سطح الأداة المدمجة كمركز نهاية واحد من MCP. سجل MCP الرسمي (Anthropic + GitHub + PulseMCP + Microsoft ، المساحة الاسمية المحققة) هو القنوية المتقدمة. هذه الدروس تعطي أسماءً حيث يتناسب بوابة، وتعمل على تنفيذ بسيط، وتحقيق منظومة البائعين في عام 2026.

**Type:** Learn
**Languages:** Python (stdlib, minimal gateway)
**Prerequisites:** Phase 13 · 15 (tool poisoning), Phase 13 · 16 (OAuth 2.1)
**Time:** ~45 minutes

## أهداف التعلم

- شرح مكان بوابة MCP (بين عملاء MCP وخادمات MCP متعددة الخلفية).
- تنفيذ مسؤوليات البوابة الخمسة: auth، RBAC، مراجعة، حد السعر، السياسة.
- قم بتطبيق إشارة أداة محجوزة على طبقة البوابة
- تمييز سجل MCP الرسمي عن سجلات المقاييس (Glama، MCPMarket، MCP.so، Smithery، LobeHub).

## المشكلة

مجموعة من 500 شركة في فورتشن لديها 30 خادم MCP المعتمدة، 5000 مطور، متطلبات الامتثال والتحقق، وفريق أمن يريد سياسة مركزية. السماح لكل مطور بتثبيت خادمات تعسفية في IDEs هو غير بدء.

نمط البوابة:

1. يعمل Gateway كمدمج واحد من نقاط نهاية HTTP المباشرة.
2. Gateway تحتوي على إثباتات لكل خادم MCP متأخر.
3. يتم تصديق كل طلب للمطور وتحقيق المدى من خلال OAuth الخاص بمركز البوابة.
4. بوابة توجيه المكالمة إلى الخادم الخلفي، تطبيق السياسة.
5. جميع المكالمات مسجلة للتدقيق

بوابات Cloudflare MCP ، Kong AI Gateway ، IBM ContextForge ، MintMCP ، TrueFoundry ، Envoy AI Gateway  جميع البوابات أو ميزات البوابات التي تم شحنها في 2025-2026.

في الوقت نفسه ، أطلق سجل MCP الرسمي على أنه السجل القديمي المتجه نحو الأمام: خادمات مرتبة ومؤكدة مساحة الأسماء ، والتي تحمل اسم DNS العكسي يمكن أن تنسحب من خلال البوابة. يمكن أن تقوم Metaregistries (Glama ، MCPMarket ، MCP.so ، Smithery ، LobeHub) بتجميع الخوادم عبر مصادر متعددة.

## المفهوم

### مسؤوليات البوابة الخمسة

1. **Auth.**OAuth 2.1 لتحديد المطور؛ خرائط لأدوار المستخدم.
2. **RBAC.**سياسة المستخدم الواحد: أي خوادم، أي أدوات، أي نطاقات.
3. **Audit.**كل مكالمة مسجلة مع من، ماذا، متى، النتيجة.
4. **Rate limit.**حدد لكل مستخدم / لكل أداة / لكل خادم لمنع الإساءة.
5. **Policy.**رفضوا الوصف المسموم، نفذوا القاعدة الثانية، وبدءوا بتحرير المعلومات

### البوابة كمركز نهائي واحد

بالنسبة للمطورين، تبدو البوابة كخادم MCP واحد. من الداخل يتوجه إلى N خلفيات. يتم إعادة كتابة هويات الدورة (المرحلة 13 · 09) في الحدود.

### إعادة التأمين

لا يرى المطورون رموز الخلفية أبداً. البوابة تحتفظ بها (أو تمثيل مزود هوية يفعل ذلك).`notes:read`على البوابة يمكن الوصول إلى خادم MCP الملاحظات بشكل انتقالي مع إثباتات الخلفية الخاصة بالبوابة  ولكن فقط بموجب سياسة تربط الوصول الانتقالي.

### إضافة أدوات في البوابة

تحتوي البوابة على مذكرة من وصف الأدوات المعتمدة (SHA256 hashes). في وقت اكتشافها ، فإنها تجلب كل خلفية `tools/list`، يُقارن الهيشيز مع المخطط، ويُزيل أي أداة تغيرت وصفها. هذا هو الدفاع عن سحب السجاد من المرحلة 13 · 15 المطبق مركزياً.

### السياسة كرمز

المواجهات المتقدمة تعبر عن السياسة في OPA/Rego، Kyverno، أو Styra. قواعد مثل "المستخدم `alice`قد تتصل`github.open_pr`فقط على الإستعلامات في الـ "أرجنتيا"`acme`" يتم تشفيرها بإعلانية. البوابات البسيطة تستخدم رمز يدوي Python. كلا الشكليين صالحين.

### التوجيهات المعرفة للجلسة

عندما تتضمن جلسة المستخدم مزيجًا من الخوادم ، فإن عدة بوابات: جلسة MCP واحدة للمطور تحتوي على جلسات N في الخلفية ، واحدة لكل خادم. الإشعارات من أي طريق backend عبر البوابة إلى جلسة المطور.

### دمج مساحة الأسماء

مدخلات دمج مساحات أسماء الأدوات من جميع الخلفيات، عادة مع مقدمة على اصطدام. `github.open_pr`،`notes.search`هذا يجعل التوجيه غير واضح

### السجلات

- **Official MCP Registry (`registry.modelcontextprotocol.io`).**أطلقت تحت الإدارة Anthropic، GitHub، PulseMCP، Microsoft.`io.github.user/server`تم تصفية مسبقة لجودة أساسية
- **Glama.**البحث المركزية التسجيلات التي تجمع العديد من المصادر.
- **MCPMarket.**دليل تجاري مع قائمة البائعين
- **MCP.so.**دليل المجتمع؛ تقديمات مفتوحة
- **Smithery.**تدفق التثبيت على شكل مدير الحزمة
- **LobeHub.**سجل متكامل مع واجهة التواصل في تطبيق LobeChat.

وبالتعيين، تسحب بوابات الشركات من السجل الرسمي، وتسمح بإضافة إدارة من السجلات المعدنية، وترفض أي شيء غير مدعوم.

### اسم DNS العكس

السجل الرسمي يطلب أسماء النظام التجاري للخادمات العامة: `io.github.alice/notes`.المناطق الاسمية تمنع الإستحواذ وتجعل تفويض الثقة أكثر وضوحاً

### استطلاع الموردين، أبريل 2026

| Vendor | Strength |
|--------|----------|
| Cloudflare MCP Portals | Edge-hosted; OAuth integrated; free tier |
| Kong AI Gateway | K8s-native; fine-grained policy; logs to OpenTelemetry |
| IBM ContextForge | Enterprise IAM; compliance; audit export |
| TrueFoundry | DevOps-leaning; metrics-first |
| MintMCP | Developer-platform oriented |
| Envoy AI Gateway | Open-source; customizable filters |

المرحلة 17 (بنية التحتية الإنتاجية) تدعم عمليات البوابة.

```figure
t3-gateway-funnel
```

## استخدمها

`code/main.py`يرسل بوابة داخلية صغيرة في ~ 150 سطر: يصدّق المستخدمين بواسطة رمز Bearer مزيف، يحمل سياسة RBAC لكل مستخدم، يرسل الطلبات إلى خادمين MCP متخلفين، ويكتب كل مكالمة إلى سجل مراجعة، ويتم فرض حد معدل، ويرفض أي أداة متخلفة لا تتطابق وصفها الهاشش مع المخطط المثبت.

ما الذي يجب أن ننظر إليه:

- `RBAC`المفتاح المفتاح من قبل`user_id`مع المسموح به`server_tool`الإدخالات
- `AUDIT_LOG`هو قائمة إضافية فقط للأحداث.
- حد السعر يستخدم علبة رمزية لكل مستخدم
- المخطط المضمن هو إشارة`server::tool -> hash`. . .

## أرسله

هذا الدرس يُنتج`outputs/skill-gateway-bootstrap.md`في ظل خطة مؤسسة MCP (المستخدمين والخلفيات، الامتثال) ، فإن المهارة تنتج تحديدات تشكيل البوابة.

## التمارين

1. أركض`code/main.py`. إجراء مكالمة كمستخدم مسموح به ثم كمستخدم غير مسموح به ثم انفجار تجاوز حد السعر. تحقق من كل التدفقات الثلاثة.

2. إضافة سياسة تحرير PII من النتائج قبل العودة إلى العميل. استخدم مرسل regex بسيط للسلسلسلات ذات شكل SSN؛ لاحظ الفجوة (بريد الإلكتروني، أرقام الهاتف).

3. تمديد سجل المراجعة لإصدار OpenTelemetry GenAI. المرحلة 13 · 20 تغطي الصفات الدقيقة.

4. تصميم سياسة RBAC لفريق 50 مطور مع خمسة خلفيات (الملاحظات، github، postgres، jira، slack). من يحصل فقط على القراءة على كل واحد؟ من يحصل على الكتابة؟

5. اقرأ الموقع المشترك Cloudflare MCP من أعلى إلى أسفل. حدد ميزة واحدة Cloudflare سفن التي لا يقدم هذا gateway stdlib.

## الشروط الرئيسية

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Gateway | "MCP proxy" | Centralizing server between clients and backends |
| Credential vaulting | "Backend tokens stay server-side" | Developers never see upstream tokens |
| Session-aware routing | "Multi-backend session" | Gateway multiplexes N backend sessions per developer session |
| Tool-hash pinning | "Approved manifest" | SHA256 of every approved tool description; blocks rug-pulls centrally |
| RBAC | "Per-user policy" | Role-based access control for tools and servers |
| Policy-as-code | "Declarative rules" | OPA/Rego, Kyverno, Styra policies enforced at gateway |
| Audit log | "Who, what, when" | Append-only event log for compliance |
| Rate limit | "Per-user token bucket" | Per-minute caps to prevent abuse |
| Official MCP Registry | "Canonical upstream" | `registry.modelcontextprotocol.io`, namespace-verified |
| Reverse-DNS naming | "Registry namespace" | `io.github.user/server` convention |

## المزيد من القراءة

- [Official MCP Registry](https://registry.modelcontextprotocol.io/) القنوات المتقدمة، المحققة من مساحة الأسماء
- [Cloudflare — Enterprise MCP](https://blog.cloudflare.com/enterprise-mcp/) نمط البوابة مع OAuth والسياسة
- [agentic-community — MCP gateway registry](https://github.com/agentic-community/mcp-gateway-registry)بوابة مرجعية مفتوحة المصدر
- [TrueFoundry — What is an MCP gateway?](https://www.truefoundry.com/blog/what-is-mcp-gateway) مقالة مقارنة
- [IBM — MCP context forge](https://github.com/IBM/mcp-context-forge)بوابة المؤسسات من شركة IBM
