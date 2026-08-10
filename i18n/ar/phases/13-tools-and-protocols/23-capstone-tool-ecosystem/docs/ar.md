# الحجر الرئيسي  بناء نظام بيئي كامل للأدوات

> المرحلة 13 علمت كل قطعة. هذا الحجر النهائي يضمها إلى نظام واحد على شكل إنتاج: خادم MCP مع الأدوات + الموارد + الإشعار + المهام + UI ، OAuth 2.1 على الحافة ، بوابة RBAC ، عميل متعدد الخادمات ، مكالمة A2A وكيل فرعي ، تتبع OTel إلى مجمع ، اكتشاف التسمم الأدوات في CI ، و مجموعة AGENTS.md + SKILL.md. في النهاية يمكنك الدفاع عن كل خيار معماري.

**Type:** Build
**Languages:** Python (stdlib, end-to-end ecosystem harness)
**Prerequisites:** Phase 13 · 01 through 21
**Time:** ~120 minutes

## أهداف التعلم

- إعداد خادم MCP يضع الأدوات والموارد والإشارات والمهام مع `ui://`التطبيق
- تقدم الخادم بمركز OAuth 2.1 الذي يفرض RBAC والحشيشات المثبتة.
- اكتب عميل متعدد الخادم الذي يتتبع مع OTel GenAI خصائص من نهاية إلى نهاية.
- تمنح جزء من عبء العمل إلى وكيل فرعي A2A؛ التحقق من الحفاظ على الضموضة.
- إغلف كل كومة مع AGENTS.md + SKILL.md حتى يمكن للوكلاء الآخرين قيادتها.

## المشكلة

إرسال نظام "البحث والتقرير":

- يطلب المستخدم: "الجمع بين ثلاثة أوراق arXiv الأكثر إقتباساً في عام 2026 حول بروتوكولات الوكيل".
- النظام: البحث عن arXiv عبر MCP؛ تفويض ملخص ورقة إلى وكيل الكتاب المتخصص عبر A2A؛ إجمالي النتائج؛ تقديم تقرير تفاعلي كطبقات MCP `ui://`الموارد، تسجيل كل خطوة إلى OTel.

جميع البدائيات من المرحلة 13 تظهر. هذه ليست لعبة  إنتاج أنظمة مساعد البحث التي تم شحنها في عام 2026 من قبل Anthropic (المنتج Claude Research) ، OpenAI (GPTs مع التطبيقات SDK) ، والأطراف الثالثة لديها هذا الشكل بالضبط.

## المفهوم

### الهندسة المعمارية

```
[user] -> [client] -> [gateway (OAuth 2.1 + RBAC)] -> [research MCP server]
                                                      |
                                                      +- MCP tool: arxiv_search (pure)
                                                      +- MCP resource: notes://recent
                                                      +- MCP prompt: /research_topic
                                                      +- MCP task: generate_report (long)
                                                      +- MCP Apps UI: ui://report/current
                                                      +- A2A call: writer-agent (tasks/send)
                                                      |
                                                      +- OTel GenAI spans
```

### تسلسل التسلسل التسلسل

```
agent.invoke_agent
 ├── llm.chat (kick off)
 ├── mcp.call -> tools/call arxiv_search
 ├── mcp.call -> resources/read notes://recent
 ├── mcp.call -> prompts/get research_topic
 ├── a2a.tasks/send -> writer-agent
 │    └── task transitions (opaque internals)
 ├── mcp.call -> tools/call generate_report (task-augmented)
 │    └── tasks/status polling
 │    └── tasks/result (completed, returns ui:// resource)
 └── llm.chat (final synthesis)
```

هوية واحدة لكل فترة الحق`gen_ai.*`الصفات

### وضعية الأمن

- OAuth 2.1 + PKCE مع مؤشر الموارد يربط الجمهور بمركز البوابة.
- Gateway تحتفظ بالوثائق فوق التيار؛ لا يراها المستخدم أبدا.
- (ريكو)`alice`- نعم`research:read`،`research:write`، يمكن أن تدعو جميع الأدوات.`bob`- نعم`research:read`لا أستطيع الاتصال`generate_report`. . .
- بيان منشور: أسقطت أي خادم تغيرت أدواتها.
- قاعدة المراجعة الثانية: لا توجد أداة تجمع بين إدخال غير موثوق به، والبيانات الحساسة، والإجراءات التالية.

### التعبير

النهائي`generate_report`المهمة تعيد كتلة المحتوى بالإضافة إلى `ui://report/current`الموارد. مضيف العميل (كلود ديسكوب، إلخ) يعطي لوحة التحكم التفاعلية في إطار أشرطة غطاء الرمال. تحتوي لوحة التحكم على قائمة ورقة مرتبة، ومعدلات الاقتباسات، وزرقة تطلب `host.callTool('summarize_paper', {arxiv_id})`لأي ورقة يضغط عليها المستخدم

### التعبئة

كل شيء يُرسل ك:

```
research-system/
  AGENTS.md                     # project conventions
  skills/
    run-research/
      SKILL.md                  # the top-level workflow
  servers/
    research-mcp/               # the MCP server
      pyproject.toml
      src/
  agents/
    writer/                     # the A2A agent
  gateway/
    config.yaml                 # RBAC + pinned manifest
```

المستخدمين ينشرون مع `docker compose up`. يمكن للمستخدمين كود كود، كورسور، كودكس، و opencode تشغيل النظام عن طريق استدعاء`run-research`المهارة

### ما ساهمت به كل دروس المرحلة 13

| Lesson | What the capstone uses |
|--------|------------------------|
| 01-05 | Tool interface, provider-portability, parallel calls, schemas, linting |
| 06-10 | MCP primitives, server, client, transports, resources + prompts |
| 11-14 | Sampling, roots + elicitation, async tasks, `ui://` apps |
| 15-17 | Tool poisoning, OAuth 2.1, gateway + registry |
| 18 | A2A sub-agent delegation |
| 19 | OTel GenAI tracing |
| 20 | Routing gateway for the LLM layer |
| 21 | SKILL.md + AGENTS.md packaging |

```figure
t3-capstone-chain
```

## استخدمها

`code/main.py`يخلط نمط الدروس السابقة في عرض عرض واحد قابل للتشغيل. جميع stdlib ، جميعها في العملية حتى تتمكن من قراءتها من النهاية. فإنه يعمل في التدفق الكامل للسيناريو البحث والتقرير: ضغط اليد مع بوابة ، OAuth 2.1 محاكاة ، أدوات / قائمة دمج ، توليد_التقرير كمهمة ، مكالمة A2A إلى الكاتب ، ui:// الموارد أعادت ، OTel امتدادات إرسال.

ما الذي يجب أن ننظر إليه:

- هوية واحدة على كل قفزة
- سياسة البوابة تمنع المستخدم الثاني من الكتابة.
- دورة حياة المهمة تعمل → اكتمل وتعيد كل من النص والحتوى ui://.
- حالة الدعوة الداخلية A2A غير واضحة للموسيقي.
- الملفات Agents.md و SKILL.md هي الملفات الوحيدة التي يحتاجها وكيل آخر لإعادة إنتاج سير العمل.

## أرسله

هذا الدرس يُنتج`outputs/skill-ecosystem-blueprint.md`. بالنظر إلى حاجة إلى المنتج (البحث، الموجّهة، التلقائيّة) ، فإن المهارة تنتج الهندسة الكاملة: أيّة أدوات MCP البدائيّة، أيّة بوابات التحكم، أيّة A2A تدعو، أيّة telemetry، أيّة التعبئة.

## التمارين

1. أركض`code/main.py`لاحظوا هوية البحث الواحد وكيف تتراوح العش واعتبروا عدد البدائيين من المرحلة 13

2. تمديد عرض التجربة: إضافة خادم MCP ثانوي (مثل `bibliography`) و تأكيد أن البوابة تجمع أدواته في نفس مساحة الأسماء.

3. استبدل وكيل الكتاب المزيف A2A بمكلفة حقيقية تعمل على عملية فرعية.

4. إضافة خطوة تحرير المعلومات الشخصية في بوابة التوجيه بين الموسيقي والشركة القانونية. يتم مسح رسائل البريد الإلكتروني التأكيد في استفسار المستخدم.

5. اكتب "AGENTS.md" لزميل فريق من شأنه أن يحافظ على هذا النظام، يجب أن يستغرق أقل من خمس دقائق لقراءة وتعطيه كل ما يحتاجه لتشغيل الحجر الرئيسي في "كورسور" أو "كودكس".

## الشروط الرئيسية

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Capstone | "Phase-13 integration demo" | End-to-end system using every primitive |
| Research and report | "The scenario" | Search, summarize, render pattern |
| Ecosystem | "All the pieces together" | Server + client + gateway + sub-agent + telemetry + package |
| Trace hierarchy | "Single trace id" | Every hop's span shares the trace; parent-child via span ids |
| Gateway-issued token | "Transitive auth" | Client sees only gateway's token; gateway holds upstream creds |
| Merged namespace | "All tools in one flat list" | Multi-server merge at the gateway, prefix-on-collision |
| Opacity boundary | "A2A call hides internals" | Sub-agent's reasoning invisible to orchestrator |
| Three-layer stack | "AGENTS.md + SKILL.md + MCP" | Project context + workflow + tools |
| Defense-in-depth | "Multiple security layers" | Pinned hashes, OAuth, RBAC, Rule of Two, audit log |
| Spec compliance matrix | "What we ship that the spec requires" | Checklist mapping deliverables to 2025-11-25 requirements |

## المزيد من القراءة

- [MCP — Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) الإشارة الموحدة
- [MCP blog — 2026 roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) حيث يتوجه البروتوكول
- [a2a-protocol.org](https://a2a-protocol.org/latest/) إشارة A2A v1.0
- [OpenTelemetry — GenAI semconv](https://opentelemetry.io/docs/specs/semconv/gen-ai/) اتفاقيات التتبع القنوني
- [Anthropic — Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) أنماط وقت تشغيل وكيل الإنتاج
