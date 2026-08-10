# أمن المخططات المشتركة II  OAuth 2.1، مؤشرات الموارد، الأهداف الزائدة

> تحتاج خوادم MCP عن بعد إلى تصريح ، وليس مجرد تصديق. تتماشى مواصفات 2025-11-25 مع مؤشرات OAuth 2.1 + PKCE + الموارد (RFC 8707) + البيانات المعدنية المستخدمة في الموارد المحمية (RFC 9728). يضيف SEP-835 موافقة نطاق متزايدة مع تصريح تصويب على 403 WWW-Authenticate. هذه الدروس تنفيذ تدفق الصعود كجهاز حالة حتى تتمكن من رؤية كل قفزة.

**Type:** Build
**Languages:** Python (stdlib, OAuth state machine simulator)
**Prerequisites:** Phase 13 · 09 (transports), Phase 13 · 15 (security I)
**Time:** ~75 minutes

## أهداف التعلم

- تمييز خادم الموارد عن مسؤوليات خادم الموافقة.
- إشغال تدفق رمز تفويض OAuth 2.1 المحمية من PKCE.
- استخدام`resource`(RFC 8707) و البيانات المعدنية المستخدمة في الموارد المحمية (RFC 9728) لمنع الهجمات المرتبطة بالخلط.
- تنفيذ تصريحات التطوير: يستجيب الخادم 403 مع WWW-Authenticate بطلب نطاق أعلى؛ يقوم العميل بإعادة طلب موافقة المستخدم ومحاولات جديدة.

## المشكلة

أرسلت MCP المبكرة (قبل عام 2025) خوادم بعيدة مع مفاتيح API ad-hoc أو حتى بدون auth. تمكنت مواصفات 2025-11-25 من إغلاق الفجوة مع ملف OAuth 2.1 الكامل.

ثلاثة احتياجات في العالم الحقيقي:

- **Ordinary remote servers.**يقوم المستخدم بتثبيت خادم MCP عن بعد يسمح له بالوصول إلى Notion / GitHub / Gmail. OAuth 2.1 مع PKCE هو الشكل الصحيح.
- **Scope escalation.**خادم ملاحظات منح `notes:read`يمكن أن تحتاج لاحقاً`notes:write`بدلاً من إعادة القيام بالعمل بأكمله، يطلب التكثيف (SEP-835) نطاق إضافي.
- **Confused deputy prevention.**يحتفظ العميل برمز من أجل الجمهور من أجل الخادم A. الخادم A هو ضار ويحاول تقديم الرمز إلى الخادم B. مؤشرات الموارد (RFC 8707) وضع الرمز إلى الجمهور المقصود.

OAuth 2.1 ليست جديدة. ما هو جديد هو ملف تعريف MCP: تدفقات مطلوبة محددة (رمز الترخيص + PKCE فقط؛ لا ضمنية، لا توجد إئتمانات العميل حسب الافتراض) ، مؤشرات الموارد إلزامية على كل طلب رمزية، ومعلومات المعلومات المستخدمة في الموارد المحمية التي يتم نشرها حتى يعرف العملاء أين يذهبون.

## المفهوم

### الأدوار

- **Client.**عميل MCP (Claude Desktop، Cursor، إلخ).
- **Resource server.**خادم MCP (لاحظات ، GitHub ، Postgres ، أي شيء).
- **Authorization server.**إصدار رموز. قد تكون نفس الخدمة مثل خادم الموارد أو IDP منفصل (Auth0, Keycloak, Cognito).

في ملف تعريف MCP، يمكن أن تكون الخوادم الموارد والإذن نفس المضيف ولكن يجب أن يتم التمييز بينها بواسطة عناوين URL.

### رمز الترخيص + PKCE

التدفق:

1. العميل يخلق`code_verifier`(الصدفة) و `code_challenge`(SHA256)
2. العميل يُعيد المستخدم إلى `/authorize?response_type=code&client_id=...&redirect_uri=...&scope=notes:read&code_challenge=...&resource=https://notes.example.com`. . .
3. موافقة المستخدم . سيرفر الإذن يُعيد إلى `redirect_uri?code=...`. . .
4. رسائل العميل إلى `/token?grant_type=authorization_code&code=...&code_verifier=...&resource=...`. . .
5. يقوم خادم التأذن بتؤكيد hash المحقق ضد التحدي المخزن وإصدار رمز الوصول.
6. العميل يستخدم الرمز: `Authorization: Bearer ...`في كل طلب إلى خادم الموارد.

PKCE يمنع هجمات إيقاف رمز التأليف. مؤشرات الموارد تمنع رمز العملة من أن تكون صالحة في أماكن أخرى.

### البيانات المعدنية الموارد المحمية (RFC 9728)

سرفير الموارد ينشر `.well-known/oauth-protected-resource`الوثيقة:

```json
{
  "resource": "https://notes.example.com",
  "authorization_servers": ["https://auth.example.com"],
  "scopes_supported": ["notes:read", "notes:write", "notes:delete"]
}
```

يكتشف العميل خادم الإذن من خادم الموارد. يقلل من التكوين  لا يحتاج العميل إلا إلى عنوان URL للموارد.

### مؤشرات الموارد (RFC 8707)

`resource`المعلم في طلب الشكلة يضع الرأي المقصود للشكلة. الشكلة المصدرة تحتوي على `aud: "https://notes.example.com"`خادم آخر من (م سي بي) يتلقى هذه الشيكات`aud`ورفضها.

### نموذج النطاق

المرافق هي سلسلة منفصلة عن الفضاء.

- `notes:read`،`notes:write`،`notes:delete`
- `admin:*`لقدرات الإدارة (استخدام محدود)
- `profile:read`لتحديد الهوية

يجب أن يكون اختيار النطاق أقل امتيازاً: اطلب ما تحتاجه الآن، وتقدم قدمًا عندما تحتاج إلى المزيد.

### تصريح التطوير (SEP-835)

منح المستخدمين `notes:read`يطلبون من العميل حذف ملاحظة، ويقول الخادم:

```
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer error="insufficient_scope",
    scope="notes:delete", resource="https://notes.example.com"
```

يرى العميل خطأ insufficient_scope، ويقوم بإجراء حوار الموافقة على النطاق الإضافي، ويقوم بتدفق OAuth الصغير له، ويعيد محاولة الطلب مع رمز جديد.

### التحقق من صحة الجمهور

كل طلب: عمليات التحقق من الخادم`token.aud == self.resource_url`هذا يمنع إعادة استخدام الرمز عبر الخادم

### الرموز القصيرة الأجل والدورة

يجب أن تكون رموز الوصول قصيرة الأمد (بالمعتاد 1 ساعة). يتم تدوير رموز التجديد في كل عملية تجديد. يقوم العميل بتعامل التجديد الصامت في الخلفية.

### لا يوجد رمز عبر

خادمات العينات (مرحلة 13 · 11) لا يجب أن تمرّر رمز العميل إلى خدمات أخرى. طلب العينات هو الحد.

### الوقاية المرتبطة بالخلط

الـ " " " الـ " " " الـ " " الـ " " الـ " " الـ " " الـ " " الـ " " الـ " الـ " الـ " الـ " الـ " الـ " الـ " الـ " الـ " الـ " الـ " الـ " الـ " الـ " الـ " الـ " الـ " الـ " الـ " الـ " الـ "`aud`. العميل يلتزم بـ`client_id`كل طلب معتمد ضد كل منهما، ويقضي المواصفات صراحة نمط "موافقة الـ"التوين" القديم الذي كان شائعًا في النظم الإيكولوجية الأدوات البعيدة قبل نظام "م سي بي".

### اكتشاف هوية العميل

ينشر كل عميل MCP بياناته المعدنية في عنوان URL ثابت. يمكن لخوادم التأذن الحصول على وثيقة بيانات المعدنية العميل لاكتشاف إعادة توجيه URIs ومعلومات الاتصال. هذا يزيل تسجيل العميل اليدوي.

### البوابات و OAuth

مرحلة 13 · 17 تظهر كيفية تعامل بوابة المؤسسات مع OAuth: بوابة تحتفظ بإثباتات للخادمات المتقدمة ، يتم إصدار رموز للعميل من بوابة ، ولا تغادر رموز المتقدمة البوابة أبدًا. هذا يقلل نموذج الثقة  يقوم المستخدمون بالتوثيق مع البوابة مرة واحدة ؛ بوابة معالجة تصريحات الخادم N.

```figure
t3-scope-stepup
```

## استخدمها

`code/main.py`يحاكي تدفق OAuth 2.1 الكامل كآلة حالة.

- مُحقق رمز PKCE / توليد التحديات.
- تدفق رمز التأذن مع مؤشر الموارد.
- نقطة نهاية للبيانات المعدنية المستخدمة في الموارد المحمية
- التحقق من الوهم مع التحقق من الجمهور.
- - إضافة خطوة`insufficient_scope`. . .

لا يوجد خادم HTTP في هذه الدروس، الآلة الحكومية تعمل في الذاكرة حتى تتمكن من تتبع كل قفزة. دروس البوابة في المرحلة 13 · 17 تشبيه إلى نقل فعلي.

## أرسله

هذا الدرس يُنتج`outputs/skill-oauth-scope-planner.md`. بالنظر إلى خادم MCP عن بعد مع الأدوات، تصميم المهارة مجموعة النطاق، وضع القواعد، وسياسة التطوير.

## التمارين

1. أركض`code/main.py`تتبع تدفق الزيادة من المجالين لاحظ أي من القفزات تتكرر عند الزيادة

2. إضافة دوران رمز التجديد: كل إعادة إصدار رمز تجديد جديد ويجعل القديم غير صالح. محاكاة رمز تجديد مسروق يستخدم بعد التجديد وتأكيد فشله.

3. تنفيذ نقطة نهاية البيانات المعدنية المستخدمة في الموارد المحمية كرد HTTP حقيقي باستخدام stdlib http.server. مرآة نقطة نهاية /mcp من الدروس 09.

4. تصميم تسلسل تسلسل نطاق لمخادم GitHub MCP: قراءة repo، كتابة PR، الموافقة على PR، دمج PR، الإدارة. استخدام تصعيد بين كل مستوى.

5. اقرأ RFC 8707 و RFC 9728. حدد الحقل الواحد في 9728 الذي يستخدمه MCP بشكل مختلف عن مثال RFC.`scopes_supported`().

## الشروط الرئيسية

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| OAuth 2.1 | "Modern OAuth" | Consolidated RFC that mandates PKCE and forbids implicit flow |
| PKCE | "Proof-of-possession" | Code verifier + challenge defeating authorization-code interception |
| Resource indicator | "Token audience" | RFC 8707 `resource` parameter pinning token to one server |
| Protected-resource metadata | "Discovery doc" | RFC 9728 `.well-known/oauth-protected-resource` |
| Step-up authorization | "Incremental consent" | SEP-835 flow for adding scopes on demand |
| `insufficient_scope` | "403 with WWW-Authenticate" | Server signal to re-consent for a larger scope |
| Confused deputy | "Token reuse across services" | Attack where a trusted holder forwards a token inappropriately |
| Short-lived token | "Access token TTL" | Bearer that expires quickly; refresh token renews |
| Scope hierarchy | "Least privilege stack" | Graduated scope set with step-up between levels |
| Client ID metadata | "Client discovery doc" | URL at which the client publishes its own OAuth metadata |

## المزيد من القراءة

- [MCP — Authorization spec](https://modelcontextprotocol.io/specification/draft/basic/authorization) ملف المعلومات المختلفة المختلفة
- [den.dev — MCP November authorization spec](https://den.dev/blog/mcp-november-authorization-spec/) إنجاز التغييرات التي ستحدث في الفترة من 2025 إلى 21-25
- [RFC 8707 — Resource indicators for OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8707) RFC المضمنة للجمهور
- [RFC 9728 — OAuth 2.0 protected resource metadata](https://datatracker.ietf.org/doc/html/rfc9728) RFC وثيقة الاكتشاف
- [Aembit — MCP OAuth 2.1, PKCE and the future of AI authorization](https://aembit.io/blog/mcp-oauth-2-1-pkce-and-the-future-of-ai-authorization/) عملية تدريجية - تدفقات - تدريجية
