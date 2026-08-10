# مؤلف MCP في الإنتاج  التسجيل ، JWKS Refresh ، رموز المشاهد

> الدروس 16 أوقفت آلة حالة OAuth 2.1 في الذاكرة. بحلول عام 2026، كل خادم MCP الذي ترسل إليه إلى منظمة حقيقية يقع خلف إنتاج مؤلف: تسجيل العملاء الذي يتراوح إلى عدد لا حدود له من العملاء (وثائق المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم المستخدم التحقق من التحقق من الوهم، والوهم المضمنة للجمهور التي ترفض إعادة عرض الموارد المتعددة. هذه الدروس نموذج السطح الكامل مع ثلاثة أدوار خادم التصريح، خادم الموارد (خادم MCP) ، و عميل  بحيث يمكنك تتبع كل قفزة من اكتشاف إلى مكالمة أداة معتمدة.
>
> **Spec note (2025-11-25):**تم تخفيض مواصفات تصريحات المجموعة الممتدة في نوفمبر 2025 لتسجيل العملاء الديناميكي من `SHOULD`إلى`MAY`و صنع**Client ID Metadata Documents (CIMD)**الآلية الافتراضية الموصى بها للتسجيل. هذه الدروس تعلم كل من، في ترتيب الأولوية الخاصة، والرقم يحافظ على DCR للمشي من خلال لأنه يتمتع بنفسه بالكامل في عملية واحدة.

**Type:** Build
**Languages:** Python (stdlib)
**Prerequisites:** Phase 13 · 16 (OAuth 2.1 state machine), Phase 13 · 17 (gateways)
**Time:** ~90 minutes

## أهداف التعلم

- اكتشف خادم التصريح من خلال RFC 8414 البيانات المعدنية وتحقق من العقد.
- تنفيذ تسجيل العملاء الديناميكي RFC 7591 بحيث يتم تسجيل العملاء من MCP دون تدخل الإداري.
- حفظ وتجديد مفاتيح JWKS على جدول زمني بحيث يتم التحقق من التوقيع على ما يصل إلى إعادة المفتاح.
- إضافة الرموز إلى مصدر واحد من MCP باستخدام مؤشرات مصدر RFC 8707 ورفض إعادة استخدام النائب المرتبط.
- فصل الأدوار الثلاثة نظيفة  خادم الإذن، خادم الموارد، العميل  بحيث كل تنفذ فقط التحققات التي تنتمي إليها.
- اقرأ ماتريكس قدرات IDP ورفض نشر عندما لا يمكن أن يرضي IDP ملف المستخدم من MCP.

## المشكلة

يدير محاكي الدروس 16 OAuth 2.1 في الذاكرة. إنتاج لديه ثلاث ثغرات تشغيلية لا يراها محاكي الذاكرة فقط.

الفجوة الأولى هي التسجيل. يقوم منظمة حقيقية بتشغيل مئات خوادم MCP وآلاف عملاء MCP. لا يسجل المشغلون يدويا كل مستخدم Cursor كعميل OAuth. يمنح المواصفات 2025-11-25 العملاء أمرًا أولويًا لحل هذا: استخدام مستخدم مسجل مسبقًا `client_id`إذا كان لديك واحد، وإلا استخدم**Client ID Metadata Document**(العميل يحدد نفسه بـ عنوان HTTPS يسيطر عليه و خادم الإذن * يسحب* البيانات المعدنية) ، وإلا تعود إلى **RFC 7591 dynamic client registration**(العميل * يدفع * a `POST /register`و تتلقى`client_id`في الموقع) ، وإلا يطلب من المستخدم. CIMD هو الافتراض الموصى به لأنه يزيل التسجيل لكل خادم بالكامل مع الحفاظ على نموذج الثقة المتجذر في DNS. يتم الاحتفاظ بـ DCR للتوافق العكسي. كلاهما يكتشف نقاط دخولها من بيانات الميتامية لخادم الترخيص:`client_id_metadata_document_supported`لـ CIMD`registration_endpoint`لـ DCR

الفجوة الثانية هي دوران المفتاح يعتمد التحقق من JWT على مفاتيح توقيع خادم الائتمان، والتي يتم نشرها على أنها مجموعة مفاتيح ويب JSON (JWKS). يقوم خادم الإذن بتدوير هذه في جدول زمني (غالباً ما في الساعة، وأحياناً أسرع في حالة استجابة الحوادث). خادم MCP الذي يحصل على JWKS مرة واحدة في بدء يصدق بشكل جيد حتى نافذة الدوران  ثم كل طلب يفشل حتى إعادة تشغيل. سلك الإنتاج JWKS كمقيمة مخفية مع عمل التجديد الذي يغطي الاحتفاظ قبل انتهاء الفترة السابقة من المفاتيح، بالإضافة إلى إرجاع التقطيع على الاحتفاظ الفاشل للحالة التي يتم فيها توقيع رمز من قبل مفتاح أحدث من الاحتفاظ.

الفجوة الثالثة هي الالتزام بالجمهور. قدم الدروس 16 مؤشرات الموارد RFC 8707. في الإنتاج، يصبح هذا المؤشر تحقيقاً صعباً للمطالبة على كل طلب. يقوم خادم MCP بالمقارنة `token.aud`ضد عنوان URL الموارد القنوني الخاص به ورفض عدم الموافقة مع HTTP 401. هذا هو الدفاع الوحيد ضد خادم MCP متجهة إلى الأمام (أو عميل ضار يحمل رمزًا مصممة لمخادم واحد) يعيد تشغيل هذا الشك ضد خادم آخر في شبكة الثقة نفسها.

هذه الدروس ترسم كل فجوة على قطعة خرسانية من السطح. وثيقة البيانات المعدنية هي نقطة نهاية HTTP. تحديث التخزين التخزيني JWKS هو عمل مُجدد بالإضافة إلى التخزين التخزيني القيم المفتاحية. التحقق من JWT هو روتين يعمل عليه خادم الموارد قبل إرسال أي أداة. حافظ على الأدوار الثلاث منفصلة و كل واحد ينفذ فقط التحققات التي يملكها: خادم الإذن يصدر ويتناول المفاتيح، خادم الموارد تخزين وتؤكد، ويكشف العميل ويتسجل.

## المفهوم

### RFC 8414  أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت أوت

وثيقة في `/.well-known/oauth-authorization-server`يصف كل ما يحتاجه العميل:

```json
{
  "issuer": "https://auth.example.com",
  "authorization_endpoint": "https://auth.example.com/authorize",
  "token_endpoint": "https://auth.example.com/token",
  "jwks_uri": "https://auth.example.com/.well-known/jwks.json",
  "registration_endpoint": "https://auth.example.com/register",
  "response_types_supported": ["code"],
  "grant_types_supported": ["authorization_code", "refresh_token"],
  "code_challenge_methods_supported": ["S256"],
  "scopes_supported": ["mcp:tools.read", "mcp:tools.invoke"],
  "token_endpoint_auth_methods_supported": ["none", "private_key_jwt"]
}
```

العميل الذي تم إعطائه سلسلة URL للموارد MCP اكتشاف: `oauth-protected-resource`من RFC 9728 (وثيقة خادم الموارد) اسم المصدر ، ثم `oauth-authorization-server`(هذه المعلومات) تسمي كل نقطة نهاية العميل لا يرمز أبداً عنوان URL الموافقة

العقد الذي تفحصه قبل أن تثق في شركة " إيد ب " لـ " م سي بي

- `code_challenge_methods_supported`يشمل `S256`(PKCE لكل RFC 7636). التفاصيل واضحة: إذا كان هذا الحقل**absent**، لا يدعم خادم الإذن PKCE والعميل **MUST**رفضوا المضي قدماً
- `grant_types_supported`يشمل `authorization_code`ورفض`password`و`implicit`. . .
- يتم الإعلان عن مسار واحد على الأقل للتسجيل: `client_id_metadata_document_supported: true`(CIMD، تفضيل) **or** `registration_endpoint`إما يفي بالعقد، لم تعد بحاجة إلى الاحتفاظ بالبيانات.
- `response_types_supported`هو بالضبط`["code"]`لـ OAuth 2.1.

إذا`S256`إذا غيب، يرفض خادم MCP نشر ضد هذا IdP  لا يوجد وضع مهدّد ل PKCE. إذا *لا * طريق التسجيل يتم الإعلان عنه ولم يكن لديك تسجيل مسبق `client_id`لا يمكنك التسجيل أيضاً، إنّ مذكرة التنفيذ خاطئة، وليس الرمز.

### RFC 9728 (إعادة التأهيل)  بيانات الموردة المحمية

غطت الدروس 16 RFC 9728. الدلتا في الإنتاج: هذا الوثيقة هو المكان الوحيد الذي يبحث فيه العميل للعثور على خوادم الإذن الموثوق بها من قبل * هذا * خادم MCP. يمكن لمخادم MCP واحد قبول رموز من العديد من IdP (واحد للموظفين ، واحد للشركاء). يعلن RFC 9728 ذلك المجموعة ؛ RFC 8414 يستند إلى ما يدعمه كل IdP.

```json
{
  "resource": "https://notes.example.com",
  "authorization_servers": ["https://auth.example.com", "https://partners.example.com"],
  "scopes_supported": ["mcp:tools.invoke"],
  "bearer_methods_supported": ["header"],
  "resource_documentation": "https://notes.example.com/docs"
}
```

### وثائق بيانات المستخدم (المتميزة الموصى بها)

يعكس CIMD التسجيل من * push* إلى * pull*. بدلاً من طلب خادم الإذن لخسارة `client_id`، يستخدم العميل عنوان HTTPS الذي يسيطر عليه **as**- نعم`client_id`. يتم تحديد عنوان URL إلى وثيقة بيانات JSON ؛ يحصل خادم الإذن عليه عند الطلب أثناء تدفق OAuth. يتم ترشيح الثقة في DNS: إذا كان مشغل الخادم يثق `app.example.com`، انها تثق العميل خدمة من`https://app.example.com/client.json`لا تسجيل ذهاب وإياب، لا`client_id`مساحة الأسماء إلى التفريغ، لا حالة لكل خادم للحفاظ على التزام المزامنة.

الوثيقة المعدنية التي يستضيفها العميل:

```json
{
  "client_id": "https://app.example.com/oauth/client.json",
  "client_name": "Example MCP Client",
  "client_uri": "https://app.example.com",
  "redirect_uris": ["http://127.0.0.1:7333/callback", "http://localhost:7333/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none"
}
```

- نعم`client_id`القيمة في الوثيقة **MUST**يُساوي عنوان URL الذي يتم خدمته منه (يؤكد خادم الإذن هذا ، يتم رفض عدم المطابقة). يعلن خادم الإذن عن الدعم مع `client_id_metadata_document_supported: true`في بياناتها المعدنية RFC 8414

هناك حقائق أمنية واضحة حولها:

- **SSRF.**يقوم خادم الإذن بتحويل عنوان URL المقدم من المهاجم. يجب أن يتحمي ضد مزيف طلبات جانب الخادم (لا توجد تحويلات إلى نقاط نهاية داخلية / إدارية).
- **localhost impersonation.**لا يمكن لـ CIMD وحدها منع المهاجم المحلي من المطالبة بمدفوعات البيانات المعدنية لعميل شرعي والربط بأي `localhost`إعادة توجيه خادم الإذن**MUST**إظهار اسم المضيف لإعادة توجيه URI بوضوح أثناء الإذن و **SHOULD**تحذير`localhost`-إعادة توجيهات فقط

لأن CIMD لا تحتاج إلى حالة جانب الخادم ، لا يوجد مسجل للوقوف على الطريقة التي تتطلبها DCR. الجانب العميل يقرأ فقط: خدمة وثيقة البيانات المعدنية من نقطة نهاية HTTPS ثابتة ودع خادم الإذن يسحبها.

### RFC 7591  تسجيل العميل الديناميكي (التوافق مع الخلف / الخلف)

د.سي. آر الآن`MAY`ويحتفظ المستخدمون مع المستخدمين المستخدمين في الموقع، من أجل التوافق الخلفي مع عمليات تنفيذ ما قبل عام 2025-11-25 و IDPs التي لا تدعم CIMD بعد. بدونها (وبلا CIMD أو التسجيل المسبق) ، يحتاج كل عميل MCP (Cursor، Claude Desktop، وكيل مخصص) إلى تبادل خارج النطاق مع إداري IdP. مع DCR، يقوم العميل بنشر:

```json
POST /register
Content-Type: application/json

{
  "redirect_uris": ["http://127.0.0.1:7333/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none",
  "scope": "mcp:tools.invoke",
  "client_name": "Cursor",
  "software_id": "com.cursor.cursor",
  "software_version": "0.42.0"
}
```

الجهاز يستجيب بـ `client_id`و (أ)`registration_access_token`للتحديثات اللاحقة:

```json
{
  "client_id": "c_3e7f1a",
  "client_id_issued_at": 1769472000,
  "redirect_uris": ["http://127.0.0.1:7333/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "registration_access_token": "regt_b2...",
  "registration_client_uri": "https://auth.example.com/register/c_3e7f1a"
}
```

`token_endpoint_auth_method: none`هو الاختيار الافتراضي الصحيح لعملاء MCP التي تعمل على جهاز المستخدم.`client_id`فقط لا`client_secret`PKCE توفر دليل الممتلكات الذي يحتاجه العملاء العامون.

ثلاثة مشاكل في الإنتاج:

- يجب أن يحدد نقطة التسجيل المحددة حسب عنوان المصدره بدون ذلك، يقوم الفاعل العدائي بتسجيل ملايين التسجيلات المزيفة ويستنفد`client_id`إجراء فحص الحد الأدنى قبل أن يتعامل المسجل مع الطلب
- `software_statement`(التأكيد على JWT الموقع للعميل) مطلوب من قبل بعض IDPs المؤسسة. تخطي مزيفة الدروس ذلك؛ تشغيل الإنتاج خطوة التحقق التي ترفض التسجيلات غير الموقعة من أي شيء آخر غير localhost إعادة توجيه URIs.
- - نعم`registration_access_token`يجب أن يتم تخزينها كـ "هاش" وليس كـ "نص" عادي. سرقة هذه الرمزية تعني أن المهاجم يمكنه إعادة كتابة إعادة توجيهات العميل

### RFC 8707 (إعادة التأهيل)  مؤشرات الموارد

الدروس 16 وضعت الشكل قاعدة الإنتاج: كل طلب رمزية يتضمن`resource=<canonical-mcp-url>`، و خادم MCP يُحقق`token.aud`يطابق عنوان URL الموارد الخاص به في كل مكالمة. يعد URI القنوني هو * أكثر المعرفات محددة * للخادم: يستخدم مخططًا صغيرًا ومضيفًا ، لا يوجد قطعة ، ولا يوجد شرائح متأخرة تقليديًا.**not**يتم تجاهلها بالقاعدة  يحتفظ المفرد بها عندما تكون ضرورية لتحديد خادم MCP فردي. `https://mcp.example.com`،`https://mcp.example.com/mcp`،`https://mcp.example.com:8443`و`https://mcp.example.com/server/mcp`كل هذه المعلومات هي ملفات إلكترونية رسمية صالحة. اختر واحدة لكل خادم و محط`aud`(تلك الدرجة تستخدم الجمهور العاري مثل`https://notes.example.com`للوقت القصير: تنشر يستضيف العديد من خادمات MCP تحت أصل واحد يفرز بينها من خلال المسار.)

### RFC 7636 (إعادة التأهيل)  PKCE

PKCE إلزامية في OAuth 2.1. تدفق رمز الترخيص للدرس دائما يحمل `code_challenge`و`code_verifier`. يرفض الخادم أي طلب رمزية دون مؤكد أو مع مؤكد لا يختلف عن التحدي المخزن.

### ميكب Spec 2025-11-25 ملف مؤلف

تُحدد مواصفات MCP (2025-11-25) ما يجب أن تفعله طبقة تفويضات خادم MCP:

- تنفيذ RFC 9728 المعلومات المتحفظة، وتوفير موقعها إما من خلال `WWW-Authenticate: Bearer resource_metadata="..."`الرأس على 401 **or**المعلومات المشهورة`/.well-known/oauth-protected-resource`(SEP-985 جعلت الرأس اختياريًا مع تعليق معروف) البيانات المعدنية `authorization_servers`الحقل**MUST**اسم خادم واحد على الأقل
- تقبل الرموز فقط عبر `Authorization: Bearer ...`على**every**طلب  أبدا في سلسلة استفسارات، أبدا معتمدة فقط في بداية الجلسة.
- تأكيدي`aud`،`iss`،`exp`و المجال المطلوب لكل طلب . الخادم**MUST**يؤكد أن الرمز تم إصداره خصيصاً له (الجمهور) ؛ اختفاء أو عدم مطابقة`aud`يتم رفضه، لا يعامل أبداً كخريطة.
- في 401/403، العودة `WWW-Authenticate: Bearer`الحمل`error=...`،`resource_metadata="<PRM-URL>"`المعلم (URL الوثيقة البيانات المعدنية ، *ليس *المصدر العادي) ، و `scope="..."`على`insufficient_scope`(403) ملاحظة: المعلم هو `resource_metadata`، مؤشر اكتشاف  لا يوجد `resource`المعلم في التحدي.
- الوصول إلى خادم الموافقة يقبل **either**RFC 8414 المعلومات المتحركة**or**OpenID Connect Discovery 1.0، يجب على العملاء تجربة كل من الإضافات المعروفة بالتالي في الترتيب الأولوي.
- العميل (وليس الخادم) يدافع عن**mix-up attacks**: تسجل المتوقع `issuer`قبل إعادة توجيه وتؤكيد`iss`المعلم المسموح به-رد (RFC 9207) قبل استرداد الرمز. PKCE وحدها لا تتوقف عن الاختلط، لأن العميل يقدم `code_verifier`إلى أيّ نقطةٍ كانت تُوجّه إليها

مسودة OAuth 2.1 هي الأساس؛ RFC 8414/7591/8707/9728/9207 + RFC 7636 + CIMD هي السطح؛ وتحديد MCP هو الملف.

### ماتريكس قدرات IDP

لا تدعم كل IDP ملف MCP الكامل. توثيق المصفوفة أدناه بيانات القدرة الفعلية اعتبارًا من مواصفات 2025-11-25. إنها * بوابة الانتشار * ، وليس توصية.

تم شحن CIMD في مواصفات 2025-11-25 وتم اعتماد مسودة OAuth الأساسية فقط في أكتوبر 2025 ، لذلك لا يزال دعم البائعين قادما  تعامل "CIMD" أدناه ك"أين تقف اليوم ، تحقق في مستأجرك ،" وليس بيان دائم.

| IdP category | AS metadata (8414/OIDC) | CIMD | RFC 7591 DCR | RFC 8707 resource | RFC 7636 S256 PKCE | Notes |
|---|---|---|---|---|---|---|
| Self-hosted (Keycloak) | yes | emerging | yes | yes (since 24.x) | yes | Reference IdP for the MCP profile in this lesson; full DCR path end-to-end, CIMD tracking the new spec. |
| Enterprise SSO (Microsoft Entra ID) | yes | emerging | yes (premium tiers) | yes | yes | DCR availability differs by tenant tier; verify in target tenant before deploying. |
| Enterprise SSO (Okta) | yes | emerging | yes (Okta CIC / Auth0) | yes | yes | DCR available on Auth0 (now Okta CIC); classic Okta orgs require admin pre-registration. |
| Social login IdPs (generic) | varies | no | rarely | rarely | yes | Most social IdPs treat clients as static partners; no self-service enrollment. Use as identity source only, layer your own MCP-aware authorization server on top. |
| Custom / homegrown | depends | depends | depends | depends | depends | If you ship your own, ship the full profile and prefer CIMD. Skipping PKCE or audience binding breaks the MCP auth contract. |

قاعدة رفض لخطوط التنفيذ: إذا لم يذكر IDP المختار `S256`في`code_challenge_methods_supported`، يرفض خادم MCP تشغيل  PKCE ليس لديه وضع متدهور. التسجيل هو بوابة أكثر لينة: تحتاج إلى * واحد * مسار عمل (موقع مسبقًا مسجل `client_id`،`client_id_metadata_document_supported: true`أو`registration_endpoint`غياب DCR وحده لم يعد سبب لرفض العمل، لأن CIMD أو التسجيل المسبق يمكن أن يغطي ذلك.

### نمط إعادة التأهيل JWKS (التناوب في AS، التأهيل في خادم الموارد)

أبقَ اللفظين منفصلين، لأنّ إصطحابهم يُعدّ خطأً حقيقيّاً في الإنتاج:

- **Rotate**ما يفعله * خادم الإذن *: وضع مفتاح توقيع جديد ، ونشره في JWKS ، وإلغاء القديم في وقت لاحق. لا تشارك خادم الموارد في هذا ولا يمكنه القيام بذلك  لا يحمل مفتاح IDP الخاص.
- **Refresh**هو ما يفعله * خادم الموارد *:`GET`هذا هو الإجراء الوحيد الذي يقوم به خادم الموارد

وضع فشل الإنتاج هو مخزن سلفي. حلله مع وظيفة تحديث محددة بالإضافة إلى مخزن ذا قيمة مفتاحية. يقوم خادم الموارد بتشغيل وظيفة (cron، timer، أيا كان وقت تشغيلك يقدم) التي ، على فترة محددة ، تجلب `<issuer>/.well-known/jwks.json`و التداول`cache[issuer] = {keys, fetched_at}`.المؤكد يقرأ من هذا الجهاز التخزيني .وهو رمز`kid`غائب من محفزات التخزين**one**التجديد المزامن كإرجاع، ثم التحقق من جديد. هذا يتعامل مع الحالتين في وقت واحد: التجديد المخطط، ونوافذ التداخل المفتاحي حيث يتم وصول رمز موقّع بمفتاح جديد تماما قبل التجديد المخطط التالي.

الظهور الخلفي**must be a re-fetch, never a rotate**إذا قمت بتوصيل مسار التخفيض إلى مسار التداول، ستنتهي أمرين: (1) إن تم وضع مفتاح جديد ينتج`kid`لا يطابق الـ "Token" ، لذا فإن البحث يفشل على أي حال. و (2) مهاجم يفرش الـ "tokens" بالصدفة`kid`القيم تجبر سلسلة لا حدود لها من الإبداع الرئيسي`kid`تكلفة واحدة في المقام الأول

شكل الجهاز التخفيضي:

```json
{
  "https://auth.example.com": {
    "keys": [
      {"kid": "k_2026_03", "kty": "RSA", "n": "...", "e": "AQAB", "alg": "RS256", "use": "sig"},
      {"kid": "k_2026_04", "kty": "RSA", "n": "...", "e": "AQAB", "alg": "RS256", "use": "sig"}
    ],
    "fetched_at": 1772668800
  }
}
```

مفتاحان في وقت واحد هو حالة ثابتة. يقوم خادمات الإذن بالدوار عن طريق إدخال مفتاح التالي (`k_2026_04`قبل التقاعد (`k_2026_03`), لذلك تظل الرموز المصدرة تحت المفتاح القديم صالحة حتى تنتهي صلاحيتها. الاحتفاظ بالخزنة يحتوي على الاتحاد.`kid`. . .

### روتين التحقق من التحقق

خادم MCP يدير التحقق قبل إرسال أي أداة.`code/main.py`استخدامات:

```python
result = server.validate(bearer_token, required_scope="mcp:tools.invoke")
if not result["valid"]:
    return {"status": result["status"], "WWW-Authenticate": result["www_authenticate"]}
```

`validate`يفكّر JWT، يحل مفتاح التوقيع من ذاكرة التخزين JWKS (تتجديد مرة واحدة في غياب) ، يصدق التوقيع، ثم يُحقق `iss`ضد قائمة الإذن`aud`ضد الموارد القنونية لهذا الخادم`exp`، والطاق المطلوب  إرجاع`WWW-Authenticate`التحدي في الفشل الأول. الحفاظ على روتين واحد على خادم الموارد يعني أن كل نقطة دخول (كل مكالمة أداة، كل نقل) تمر بنفس التحققات. لا توجد مسار يصل إلى أداة دون التحقق أولاً.

### التشغيل المتكرر للجمهور (قيود على امتيازات الوصول إلى رموز الوصول)

الخادم (`notes.example.com`) و الخادم ب (`tasks.example.com`) كلا التسجيل ضد نفس خادم الموافقة. الخادم A هو المخترق. المهاجم يأخذ رمز ملاحظات المستخدم ويعيد تشغيله ضد الخادم B.

مؤكدة الخادم ب:

1. فك رموز JWT، احضر JWKS من خلال `kid`، تأكيد التوقيع
2. تحقق`iss`ضد بياناتها المتحمية`authorization_servers`(مُجريّة نفس الـ"آي دي بي"
3. تحقق`aud == "https://tasks.example.com"`(فشل رمز)`aud`هو`https://notes.example.com`().
4. أعد 401 مع `WWW-Authenticate: Bearer error="invalid_token", error_description="audience mismatch", resource_metadata="https://tasks.example.com/.well-known/oauth-protected-resource"`. . .

دعوى الجمهور هو الدفاع الوحيد ضد هذا الهجوم في طبقة البروتوكول. تخطي ذلك لأداء هو الخطأ الإنتاج الأكثر شيوعا؛ يجب أن يعمل المؤكد على كل طلب، وليس فقط في بداية الجلسة.**access-token privilege restriction**: خادم MCP `MUST`رفض أي رمز لا يسميه في الجمهور

> **Naming note.**يحتفظ المفرد بالصيغة * نائب مخبط * لمشكلة ذات صلة ولكنها واضحة: خادم MCP يعمل كموظف**proxy**إلى API طرف ثالث ، باستخدام معرف العميل ثابت ، الذي ينقل رمزًا دون الحصول على موافقة المستخدم لكل العميل. تحلّل ربط الجمهور التشغيل أعلاه. تحلّل حلّ النائب الخلط موافقة كل العميل **plus**لا تمرّر الرمز المُدخل أبداً إلى مُصدرات إدارة التكنولوجيا (MCP server `MUST`الحصول على رمز منفصل صعودا).

### هجمات مختلطة (دفاع من جانب العميل لا يمكن أن يوفر الخادم)

يتحدث العميل مع العديد من خادمات التأليف على مدى حياته. يمكن أن يحاول AS الخبيث أن يجعل العميل يسترد رمز التأليف الصادق من AS في نقطة نهاية رمزية للمهاجم. لا يساعد ربط الجمهور هنا  يحدث الهجوم قبل وجود أي رمز. يعيش الدفاع في العميل (RFC 9207):

1. قبل إعادة توجيه، يقوم العميل بتسجيل المتوقع `issuer`من البيانات المعدنية المعتمدة للطريقة المعمول بها.
2. على رد الموافقة، يُقارن العميل المرجع `iss`المعلمة ضد المصدر المسجل (مقارنة بسيطة من السلاسل، لا توجد طبيعة) قبل إرسال الرمز إلى أي مكان.
3. عدم الانسجام (أو `iss`غياب عندما أعلنت النظام التجاري `authorization_response_iss_parameter_supported`) → رفض، ولا حتى يعرض`error`الحقول

PKCE وحدها لا تتوقف عن الارتباك، لأن العميل يقدم`code_verifier`إلى أي نقطة نهاية رمزية تم توجيهها إليها لهذا السبب يقوم المواصفات بتسجيل المصدر على الطلب جنبا إلى جنب مع مؤكد PKCE و`state`. . .

### أساليب الفشل

- **Stale JWKS.**يرفض المؤكد رموز صالحة بعد أن يقوم AS بتدوير مفتاح. التحديد هو نمط cron-refresh + cache-miss-refetch أعلاه. لا تخزن JWKS أبدا دون عمل التجديد.
- **Rotate-as-fall-back.**إن توصيل مسار التخفيض إلى مسار التداول بدلاً من إعادة التوصيل هو خطأ حقيقي: لا ينتج أبداً المفقودين`kid`، و يصبح المهاجم يسيطر عليه`kid`القيم في إدارة الإدارة التركيزية. يجب أن يكون الخلفية هي المتميزة`refresh-jwks`. . .
- **Missing `aud` claim.**بعض المعلومات الإلكترونية تُغيب عن الإغلاق`aud`إلا إذا`resource`يحتوي على طلب الرمز. يجب على المؤكد رفض الرمز مع غياب`aud`لا تعامل مع غيابك كطرد
- **Mix-up via missing `iss` check.**العميل الذي لا يؤكد RFC 9207 `iss`يمكن توجيه مبرمير الامتحان والرد على المصدر الذي سجله قبل إعادة التوجيه إلى استرداد رمز AS الصادق في نقطة نهاية رمزية للمهاجم. هذا فشل من جانب العميل؛ لا يمكن لمخادم الموارد تعويض ذلك.
- **Scope upgrade race.**يمكن أن تنجح تدفقات تصعيد متزامنين لنفس المستخدم وتنتج رمزين وصولين ذوي نطاق مختلف. يجب على المؤكد استخدام الرمز المقدم على الطلب ، وليس البحث عن "نطاق المستخدم الحالي"  الذي يخلق نافذة TOCTOU.
- **Registration token theft.**- تسريب`registration_access_token`يسمح للمهاجم بإعادة كتابة إعادة توجيه URIs. حدد هذه في حالة راحة؛ تطلب من العميل تقديم النص الصريح في كل تحديث؛ تدوير على الشك.
- **`iss` not pinned.**مؤكد يقبل أي`iss`يسمح للمهاجمين بتقديم خادم تفويضهم الخاص، وتسجيل عميل للجمهور المستهدف، وإصدار رموز.`authorization_servers`القائمة هي القائمة المسموح بها، قم بتنفيذها.

```figure
t3-jwks-rotate
```

## استخدمها

`code/main.py`يمر في كامل تدفق الإنتاج مع stdlib Python وثلاث أدوار  `AuthorizationServer`،`ResourceServer`و`Client`التدفق:

1. خادم الإذن ينشر RFC 8414 البيانات الأساسية في `/.well-known/oauth-authorization-server`. . .
2. العميل MCP يدعو نقطة نهاية البيانات المعدنية ويتحقق من خيارات التسجيل (`client_id_metadata_document_supported`لـ CIMD`registration_endpoint`لـ (DCR) و`S256`دعم PKCE
3. المشي من خلال يأخذ طريق الرد من DCR: العميل يرسل إلى `/register`(RFC 7591) ويتلقّى`client_id`(مستهلك CIMD سيقدم بدلاً من ذلك HTTPS الخاص به `client_id`URL و تخطي هذه الخطوة.)
4. يقوم عميل MCP بتشغيل تدفق رموز الترخيص المحمية من PKCE (RFC 7636) مع `resource`مؤشر (RFC 8707).
5. العميل MCP يدعو أداة على خادم MCP مع `Authorization: Bearer ...`. . .
6. يعمل خادم MCP `validate`، حل مفتاح التوقيع من ذاكرة التخزين JWKS.
7. يدور IDP مفتاحاً؛ والإعادة المخطط لها تجذب JWKS مرة أخرى إلى التخزين الآلي.
8. المكالمة التالية تؤكد ضد المفاتيح المتجددة دون إعادة تشغيل، والرمز السابق لا يزال يؤكد خلال نافذة التداخل.
9. محاولة إعادة عرض الجمهور ضد مصدر مختلف من المملكة المتحدة تحصل على 401 مع`audience mismatch`و (أ)`resource_metadata`المؤشر

يستخدم JWT هنا HS256 مع سر مشترك (لذلك الدروس تعمل على stdlib فقط). إنتاج يستخدم RS256 أو EdDSA مع نمط JWKS أعلاه. منطق التحقق هو نفسه في غير ذلك. لأن IDP وخادم الموارد يعيش في عملية واحدة ، `refresh_jwks`يقرأ قائمة المفاتيح الخاصة بخادم الإذن مباشرة؛ عبر الأسلاك هو HTTP `GET`إلى`jwks_uri`. . .

## أرسله

هذا الدرس يُنتج`outputs/skill-mcp-auth.md`. بالنظر إلى تكوين خادم MCP ومجموعة قدرات IdP ، فإن المهارة تنبعث من سطح auth للاستقرار  البيانات المحتفظة الموارد، وسيلة التسجيل للاستخدام (CIMD، التسجيل المسبق، أو DCR fallback) ، وتوقيت إعادة التشغيل JWKS، خريطة النطاق، وقواعد الرفض للتطبيق عندما لا يدعم IdP الملف RFC الكامل.

## التمارين

1. أركض`code/main.py`. تتبع التدفق. لاحظ كيف يدور IDP مفتاح في الخطوة 6 ، المخطط `refresh_jwks`يُسحب مرة أخرى المجموعة المنشورة، ويتم تأكيد كل من الرمز القديم (فوترة التداخل) و الرمز الجديد دون إعادة تشغيل.

2. إضافة IDP جديد إلى البيانات المعدنية المستخدمة في الموارد المحمية `authorization_servers`إصدار رمز وقعه IDP الجديد وتأكيد المحقق يقبل به إصدار رمز وقعه IDP غير المدرجة وتأكيد الرفض المحقق مع `WWW-Authenticate: Bearer error="invalid_token", error_description="iss not allowed"`. . .

3. إضافة إحصاء على الحد من المعدلات إلى `register_client`تستخدم رموز-بوكيت لكل مصدر IP التي تمتلكها في إشارة صغيرة مع مفتاح IP.

4. اقرأ RFC 7591 وتحدد مجالات الدروس`/register`المدير لا يؤكد. إضافة التحقق.`software_statement`و`redirect_uris`نظام URI)

5. إضافة طريق بيانات المستخدم المستخدم.`client.json`الذي`client_id`يساوي عنوان URL الخاص به ، ويحصل على خادم الإذن على الحصول عليه والتحقق منه (رفض إذا `client_id`≠ URL) تأكيد أن عميل CIMD يسجل بدون أي `register_client`اتصل

6. إثبت إصلاح الدولية إرسال مؤكداً رمزياً مع إصدار عشوائي`kid`و تأكيد`refresh_jwks`يبدأ في التشغيل مرة واحدة على الأكثر وعدد المفاتيح في خادم الترخيص لا ينمو ثم أعيد إعادة تشغيل الركود إلى دورة وذرة ومشاهدة ارتفاع عدد المفاتيح لكل رمز مزيف

7. تنفيذ RFC 9207 من جانب العميل `iss`التحقق من قسم الخلط: تسجيل المصدر المتوقع قبل طلب الترخيص ، ثم رفض رد الترخيص الذي `iss`لا يطابق

## الشروط الرئيسية

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| ASM | "OAuth metadata document" | RFC 8414 `/.well-known/oauth-authorization-server` JSON |
| CIMD | "Client metadata URL" | Client ID Metadata Document — an HTTPS URL used as the `client_id`; the AS pulls the JSON. Recommended default since 2025-11-25 |
| DCR | "Self-service client registration" | RFC 7591 `POST /register` flow; demoted to a `MAY` fallback in 2025-11-25 |
| JWKS | "Public keys for JWT validation" | JSON Web Key Set, fetched from `jwks_uri`, indexed by `kid` |
| Rotate vs refresh | "Updating the keys" | *Rotate* = AS mints/retires signing keys; *refresh* = resource server re-fetches the published set. Resource servers only ever refresh |
| Resource indicator | "Audience parameter" | RFC 8707 `resource` parameter pinning the token to one server |
| `aud` claim | "Audience" | JWT claim the validator compares against the canonical resource URL |
| Audience replay | "Token replay" | Token issued for Server A presented to Server B; defended by audience validation (spec: access-token privilege restriction) |
| Confused deputy | "Proxy token misuse" | An MCP proxy with a static client ID forwarding a token without per-client consent; distinct from audience replay |
| Mix-up attack | "Wrong token endpoint" | Client steered to redeem an honest AS's code at an attacker's endpoint; defended client-side via RFC 9207 `iss` |
| `iss` allow-list | "Trusted authorization servers" | The set named in protected-resource metadata's `authorization_servers` |
| `resource_metadata` | "Where to find the PRM doc" | `WWW-Authenticate` parameter naming the RFC 9728 metadata URL on a 401/403 |
| Public client | "Native or browser client" | OAuth client with no `client_secret`; PKCE compensates |
| `WWW-Authenticate` | "401/403 response header" | Carries `Bearer error=...` directives that drive client recovery |

## المزيد من القراءة

- [MCP — Authorization spec (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) ملف المشاريع المختلفة هذا الدروس تنفيذ
- [MCP blog — One Year of MCP: November 2025 Spec Release](https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/) ما تغير في 2025-11-25 (CIMD، XAA، تخفيض DCR)
- [Aaron Parecki — Client Registration in the November 2025 MCP Authorization Spec](https://aaronparecki.com/2025/11/25/1/mcp-authorization-spec-update) منطقية CIMD-over-DCR
- [OAuth Client ID Metadata Document (draft-ietf-oauth-client-id-metadata-document-00)](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-client-id-metadata-document-00) CIMD
- [RFC 8414 — OAuth 2.0 Authorization Server Metadata](https://datatracker.ietf.org/doc/html/rfc8414)عقد اكتشاف
- [RFC 7591 — OAuth 2.0 Dynamic Client Registration Protocol](https://datatracker.ietf.org/doc/html/rfc7591) DCR (مسار العودة)
- [RFC 7636 — Proof Key for Code Exchange (PKCE)](https://datatracker.ietf.org/doc/html/rfc7636) دليل على امتلاك العميل العام
- [RFC 8707 — Resource Indicators for OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8707) إضافة الجمهور
- [RFC 9728 — OAuth 2.0 Protected Resource Metadata](https://datatracker.ietf.org/doc/html/rfc9728) اكتشاف الخادم الموارد
- [RFC 9207 — OAuth 2.0 Authorization Server Issuer Identification](https://datatracker.ietf.org/doc/html/rfc9207) الموقع `iss`المعلم الذي يحمي ضد الهجمات المختلطة
- [OAuth 2.1 draft](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1) الأساسية الموحدة لـ OAuth
