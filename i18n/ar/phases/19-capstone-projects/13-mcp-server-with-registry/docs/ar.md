# كابستون 13  خادم MCP مع السجل والحكم

> توقفت بروتوكول النموذجية من كونها المستقبل وأصبحت المواصفات الافتراضية لاستخدام الأدوات في عام 2026. أنثروبيك، OpenAI، جوجل، وجميع العملاء الكبار IDE شحن MCP. نشر Pinterest نظامه الإيكولوجي الداخلي لخادمات MCP. سجل AAIF رسمية القدرة البيانات المعدنية في `.well-known`أدرجت AWS ECS نشر نشر الاستشارة غير الحكومية. وضع وكيل البلوك نفس البروتوكول داخل مساعد مضيف. شكل الإنتاج 2026 هو: نقل StreamableHTTP ، نطاق OAuth 2.1 ، إطار سياسة OPA ، و سجل يسمح لفرق المنصة اكتشاف وتؤكيد وتمكين الخوادم. بناء ذلك من نهاية إلى نهاية.

**Type:** Capstone
**Languages:** Python (server, via FastMCP) or TypeScript (@modelcontextprotocol/sdk), Go (registry service)
**Prerequisites:** Phase 11 (LLM engineering), Phase 13 (tools and MCP), Phase 14 (agents), Phase 17 (infrastructure), Phase 18 (safety)
**Phases exercised:**P11 · P13 · P14 · P17 · P18
**Time:** 25 hours

## المشكلة

أصبحت MCP لغة اللغة الافريقية التي تستخدم الأدوات. كلود كود، كورسور 3، أمپ، اوبن كود، جيميني كلي، وكل وكيل مدير الآن استهلاك خادمات MCP. التحديات الإنتاجية ليست كتابة الخوادم (FastMCP يجعل ذلك سهلا) ولكن نشرها على نطاق مع متطلبات المؤسسة: نطاقات OAuth لكل مستأجر، سياسة OPA على الأدوات المدمرة، StreamableHTTP مقياسية بلا حالة، سجل للاكتشاف، سجلات المراجعة لكل مكالمة أداة. نظام MCP الداخلي لـ Pinterest ومواصفات سجل AAIF تحدد 2026 بار.

ستقوم ببناء خادم MCP يعرض 10 أدوات داخلية (Postgres القراءة فقط، إدراج S3، Jira، Linear، Datadog، إلخ) ، واجهة استخدام السجل للاكتشاف من منصة، وبوابة موافقة الإنسان للأدوات المدمرة. يظهر اختبار الحمل التوسع الأفقي StreamableHTTP. يلبي مسار المراجعة مراجعة أمن المؤسسة.

## المفهوم

تعتمد مراجعة MCP 2026 على StreamableHTTP كنقل افتراضي. على عكس شكل stdio-and-SSE السابق ، فإن StreamableHTTP غير متعلقة بالولاية افتراضيًا: نقطة نهاية HTTP واحدة تقبل طلبات JSON-RPC ، وتتدفق الاستجابات ، وتدعم الاتصالات طويلة الأمد للإشعارات. غير متعلقة بالولاية تعني قابلية للتوسع الأفقي خلف ميزان الحمل.

التأذن هو OAuth 2.1 مع نطاقات لكل أداة.`jira:read`،`s3:list`،`postgres:query:readonly`. يقوم خادم MCP بتحقق من المجال في وقت الدعوة من خلال الأداة، وليس فقط بدء الجلسة. بالنسبة للأدوات ذات المخاطر العالية، يرفض الخادم أي دعوة لا يتم رفع نطاقها إلى `approved:by:human`خلال آخر N دقائق  هذا الارتفاع يأتي من بطاقة مراجعة Slack.

السجل هو خدمة منفصلة. كل خادم MCP يعرض`.well-known/mcp-capabilities`المستند مع مذكرة الأدوات، عنوان URL النقل، متطلبات المؤلف. استطلاعات السجل، التحقق من التحقق، والإندكس. تستخدم فرق المنصة واجهة المستخدم للسجل لمعرفة ما هي الأدوات المتاحة، وما هي نطاقات الحاجة إليها، وما هي فرق تمتلكها.

## الهندسة المعمارية

```
MCP client (Claude Code, Cursor 3, ...)
          |
          v
StreamableHTTP over HTTPS (JSON-RPC + streaming)
          |
          v
MCP server (FastMCP) behind load balancer
          |
   +------+------+---------+----------+------------+
   v             v         v          v            v
Postgres    S3 listing  Jira       Linear     Datadog
(read-only) (paged)     (read)     (read)     (query)
          |
   +------+-------------+
   v                    v
 OPA policy gate   destructive tool MCP (separate server)
                        |
                        v
                   human approval via Slack
                        |
                        v
                   audit log (append-only, per-tenant)

  registry service
     |
     v  GET /.well-known/mcp-capabilities from each server
     v
     UI: search / validate / enable-disable / ownership
```

## الـ"كثيرة"

- إطار الخادم: FastMCP (Python) أو `@modelcontextprotocol/sdk`(تايب سكريبت)
- النقل: StreamableHTTP عبر HTTPS (غير حكومي)
- الموافقة: الموافقة 2.1 مع هوية عبء العمل عبر SPIFFE / SPIRE
- السياسة: قواعد OPA / Rego لكل أداة ؛ خدمة اتخاذ القرارات السياسية حسب الطلب
- السجل: المضيف الذاتي، الاستهلاك `.well-known/mcp-capabilities`المخططات
- الموافقة البشرية: إرسال رسالة تفاعلية للاستخدام في أدوات تدمير
- التنفيذ: AWS ECS Fargate أو Fly.io، خادم واحد لكل مستأجر أو مشترك مع استهداف المستأجر
- مراجعة: مدخل JSONL مهيكل لكل مستأجر مع سلسلة كل مكالمة

```figure
cf-mcp-gate
```

## بناءها

1. **Tool surface.**عرض 10 أدوات داخلية: استفسار Postgres القراءة فقط، أشياء القائمة S3، بحث Jira / fetch، بحث خطي / fetch، استفسار متري Datadog، بحث PagerDuty على المكالمة، GitHub القراءة فقط، بحث Notion، بحث Slack، قراءة Salesforce. كل أداة لديها مخطط منخفض وصففة نطاق.

2. **FastMCP server.**قم بتجميع الأدوات، قم بتشغيل نقل StreamableHTTP، أضف برامج وسطية لتحقيق إشارات OAuth وتطبيق النطاق.

3. **OPA policy.**سياسة Rego لكل أداة: ما هي النطاقات التي تسمح بالادعاء، ما هي إصدارات المعلومات الشخصية التي تطبق، ما هي القيود الحجمية للمحمل المفيد. خدمة القرار تدعو في كل مكالمة أداة.

4. **Registry service.**خدمة Go أو TS منفصلة التي تقوم بالاجراءات`.well-known/mcp-capabilities`من الخوادم المسجلة، والتي تؤكد مع نظام JSON، وتكشف قائمة / البحث / التحقق / تعطيل واجهة المستخدم.

5. **Capability manifest.**كل خادم يكتشف`.well-known/mcp-capabilities`مع: قائمة الأدوات، متطلبات المؤلف، عنوان نقل، فريق المالك، SLO.

6. **Destructive tool separation.**أدوات تتحول إلى حالة (Jira create، Linear create، Postgres write) تعيش على خادم MCP ثاني مع تدفق auth أكثر صرامة: يجب أن يكون لدى الوهمات `approved:by:human`يُرتفع نطاق المجال عبر بطاقة Slack خلال 15 دقيقة.

7. **Audit log.**إضافة فقط JSONL لكل مستأجر: `{timestamp, user, tool, args_redacted, response_redacted, outcome}`. إصدار المعلومات من خلال بريسيديو قبل الكتابة

8. **Load test.**100 عميل متزامن على StreamableHTTP. إظهار التوسع الأفقي عن طريق إضافة نسخة ثانية؛ عرض موازنة الحمل إعادة توزيع دون لزجة الجلسة.

9. **Conformance tests.**إشغال مجموعة الموافقة الرسمية من MCP ضد كلا الخوادم. اجتياز جميع القسمات الإلزامية.

## استخدمها

```
$ curl -H "Authorization: Bearer eyJhbGc..." \
       -X POST https://mcp.internal.example.com/ \
       -d '{"jsonrpc":"2.0","method":"tools/call",
            "params":{"name":"postgres.readonly","arguments":{"sql":"SELECT 1"}}}'
[registry]   capability validated: postgres.readonly v1.2
[policy]    scope postgres:query:readonly present; allowed
[audit]     logged: user=u42 tool=postgres.readonly outcome=ok
response:    { "result": { "rows": [[1]] } }
```

## أرسله

`outputs/skill-mcp-server.md`يصف المنتج. خادم MCP من مستوى الإنتاج + طبقة التسجيل + مراجعة للأدوات الداخلية مع نطاق OAuth 2.1 و OPA Gateing.

| Weight | Criterion | How it is measured |
|:-:|---|---|
| 25 | Spec conformance | StreamableHTTP + capability manifest passes MCP conformance tests |
| 20 | Security | Scope enforcement, OPA coverage across every tool, secret hygiene |
| 20 | Observability | Per-tool-call audit log with PII redaction |
| 20 | Scale | 100-client load test horizontal scale demonstration |
| 15 | Registry UX | Discover / validate / enable-disable workflow |
| **100** | | |

## التمارين

1. إضافة أداة جديدة (بحث التوافق) إرساله عبر تدفق التحقق من السجل دون لمس الخادم الأساسي.

2. اكتب سياسة OPA التي تحرير نتائج استفسار Postgres التي تحتوي على أعمدة تحمل أسماء `email`،`ssn`أو`phone`تمرين مع استفسار الصوت

3. مقياس التدفقات المتداولة HTTP مقابل stdio على التأخير المحلي. تقرير لكل مكالمة p50/p95.

4. تنفيذ حصة المستأجر: أقصى عدد من المكالمات في الدقيقة لكل أداة لكل مستأجر. تنفيذها من خلال قاعدة OPA الثانية.

5. تشغيل مجموعة التوافقات MCP من [mcp-conformance-tests](https://github.com/modelcontextprotocol/conformance)و إصلاح كل فشل

## الشروط الرئيسية

| Term | What people say | What it actually means |
|------|-----------------|------------------------|
| StreamableHTTP | "2026 MCP transport" | Stateless HTTP + streaming; replaces SSE + stdio for networked servers |
| Capability manifest | "Well-known doc" | `.well-known/mcp-capabilities` with tool list, auth, transport URL |
| OPA / Rego | "Policy engine" | Open Policy Agent for authorizing tool calls against external rules |
| Scope elevation | "Approved-by-human" | Short-lived scope granted via Slack approval, required for destructive tools |
| Registry | "Tool discovery" | Service that indexes MCP servers from their capability manifests |
| Workload identity | "SPIFFE / SPIRE" | Cryptographic service identity for OAuth token issuance |
| Conformance suite | "Spec tests" | Official MCP test battery for StreamableHTTP + tool manifest correctness |

## المزيد من القراءة

- [Model Context Protocol 2026 Roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) StreamableHTTP، البيانات المعدنية للقدرة، السجل
- [AAIF MCP Registry spec](https://github.com/modelcontextprotocol/registry) مواصفات السجل لعام 2026
- [AWS ECS reference deployment](https://aws.amazon.com/blogs/containers/deploying-model-context-protocol-mcp-servers-on-amazon-ecs/) تنفيذ الإنتاج المرجعي
- [Pinterest internal MCP ecosystem](https://www.infoq.com/news/2026/04/pinterest-mcp-ecosystem/) النشر الداخلي المرجعي
- [Block `goose` MCP usage](https://block.github.io/goose/)نمط استهلاك العوامل المرجعية
- [FastMCP](https://github.com/jlowin/fastmcp)إطار الخادم Python
- [Open Policy Agent](https://www.openpolicyagent.org/) إشارة محرك السياسة
- [SPIFFE / SPIRE](https://spiffe.io) إشارة إلى هوية الحملة
