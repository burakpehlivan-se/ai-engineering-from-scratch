# المهارات والموظفين SDKs  المهارات الإنسانية, AGENTS.md, OpenAI Apps SDK

> المهارات تقول كيفية القيام بمهمة، و2026 ستقوم بتجميع كلتا الطائرات تمكن مهارات العميل في Anthropic (المعيار المفتوح ، ديسمبر 2025) من السفر باسم SKILL.md مع الكشف التدريجي. أجهزة OpenAI الخاصة بتطبيقات SDK هي MCP بالإضافة إلى بيانات الويجيت. AGENTS.md (الآن في 60،000 + repos) يقع في جذور repo كسياق وكيل على مستوى المشروع. هذه الدروس تعطي أسماء لكل منها وتبني مجموعة صغيرة من SKILL.md + AGENTS.md التي تتجول عبر العملاء.

**Type:** Learn
**Languages:** Python (stdlib, SKILL.md parser and loader)
**Prerequisites:** Phase 13 · 07 (MCP server)
**Time:** ~45 minutes

## أهداف التعلم

- تمييز بين الطبقات الثلاثة: AGENTS.md (سياق المشروع) ، SKILL.md (المعلومات التي يمكن إعادة استخدامها) ، MCP (الأدوات).
- اكتب SKILL.md مع المادة الاولى من YAML والكشف التدريجي.
- تحميل المهارات في نظام الملفات في وقت تشغيل العميل.
- قم بتكوين مهارة مع خادم MCP و AGENTS.md بحيث تعمل حزمة واحدة في كود كلود، كورسور، وكودكس.

## المشكلة

يقوم المهندس بتحويل سير العمل لتكليف الملاحظات إلى طلب متعدد الخطوات: "اقرأ أحدث رسائل العلاقات العامة المدمجة. مجموعة حسب المنطقة. قم بتجميع كل منها. اكتب مدخلًا من خلال النظام التغييري وفقًا لنمط الفريق. أرسل إلى مسودة Slack. " وضعوه في وثيقة Notion لفريقهم.

الآن يريدون استخدام هذه التدفقات من كود كود، كورسور، وكودكس كلي. كل وكيل لديه طريقة مختلفة لتحميل التعليمات: كود كود سلاش-أوامر، قواعد كورسور، كودكس `.codex.md`المهندس ينسخ سير العمل ثلاث مرات ويحافظ على ثلاث نسخ

وكلاء.مدي و سكيل.مدي معاً يصلحون هذا

- **AGENTS.md**يجلس على جذور البيانات. كل وكيل متوافق يقرأها عند بدء الجلسة. "كيف يعمل هذا المشروع؟ ما هي الاتفاقيات؟ أي أوامر تشغيل الاختبارات؟"
- **SKILL.md**هو مجموعة محمولة: YAML frontmatter (اسم وصف) + جسم التسجيل + موارد اختيارية. وكلاء يدعمون المهارات تحميلها باسم على الطلب.
- **MCP**(المرحلة 13 · 06-14) يتعامل مع الأدوات التي تحتاج المهارة إلى استدعاءها.

ثلاث طبقات، ومتفرد محمول واحد.

## المفهوم

### الوكلاء.md (الوكلاء.md)

تم إطلاقها في أواخر عام 2025 ، تم تبنيها من قبل 60،000 + repos بحلول أبريل 2026. ملف واحد في root repo.

```markdown
# Project: my-service

## Conventions
- TypeScript with strict mode.
- Use Pydantic for models on the Python side.
- Tests run with `pnpm test`.

## Build and run
- `pnpm dev` for local dev server.
- `pnpm build` for production bundle.
```

يقرأ الوكلاء هذا عند بدء الجلسة ويستخدمونه لتصفية سلوكهم لهذا المشروع. كل وكيل برمجة في عام 2026 يدعم AGENTS.md: كلود كود، كورسور، كودكس، كوبيلوتر وركس سبيس، اوبن كود، ويندسرف، زيد.

### تنسيق SKILL.md

مهارات العملاء في أنثروبيك (تم إصدارها كمعيار مفتوح في ديسمبر 2025):

```markdown
---
name: release-notes-writer
description: Write a changelog entry for the latest merged PRs following this project's style.
---

# Release notes writer

When invoked, run these steps:

1. List PRs merged since the last tag. Use `gh pr list --base main --state merged`.
2. Group by label: feature, fix, chore, docs.
3. For each PR in each group, write one line: `- <title> (#<num>)`.
4. Draft the release notes and stage them in CHANGELOG.md.

If the user says "ship", run `git tag vX.Y.Z` and `gh release create`.

## Notes

- Never include commits without a PR.
- Skip "chore" entries from the public changelog.
```

المادة الأمامية تعلن هوية المهارة. الجسم هو الإشارة التي تظهر للنموذج عندما تحملها المهارة.

### الإفصاح التدريجي

المهارات يمكن أن تشير إلى الموارد الفرعية التي يأخذها الوكيل فقط عند الحاجة.

```
skills/
  release-notes-writer/
    SKILL.md
    style-guide.md
    template.md
    scripts/
      generate.sh
```

يقول SKILL.md "انظر style-guide.md لقواعد النمط". يقوم العميل بسحب style-guide.md فقط عندما تكون المهارة تعمل بنشاط. هذا يتجنب إفخار المطلوب بالتفاصيل التي قد لا يحتاجها النمط.

### اكتشاف النظام الملفي

أوقات تشغيل العميل تقوم بفحص المجلات المعروفة لملفات SKILL.md:

- `~/.anthropic/skills/*/SKILL.md`
- المشروع`./skills/*/SKILL.md`
- `~/.claude/skills/*/SKILL.md`

تحميل حسب اسم المجلد والمواد الاولى `name`كلود كود، إنثروباتي كلود وكيل SDK، و SkillKit (منتقل وكيل) جميعًا تتبع هذا النمط.

### كود الوكيل الإنساني SDK

`@anthropic-ai/claude-agent-sdk`(تايب سكريبت) و `claude-agent-sdk`(بايتون) تحميل مهارات عند بدء الجلسة، كشف لهم ك"وكلاء" قابلة للدعوة داخل الوقت التشغيل. حلقة وكيل يرسل إلى مهارة عندما يستدعيها المستخدم.

### OpenAI Apps SDK

تم إطلاقه في أكتوبر 2025؛ تم بناؤه مباشرة على MCP. يوحد من أصل OpenAI السابق وأفعال GPT المخصصة تحت سطح واحد للمطور. تطبيق Apps SDK هو:

- خادم MCP (الأدوات والموارد والإشارات).
- بالإضافة إلى البيانات المعدنية للشاتجبت.
- بالإضافة إلى تطبيقات MCP اختيارية `ui://`الموارد للمساحات التفاعلية.

نفس البروتوكول، تجربة أكثر غنى.

### تحميل عبر العملاء عبر SkillKit

أدوات مثل SkillKit وطبقات التوزيع عبر الوكلاء مماثلة ترجمة SKILL.md واحد إلى النموذج الأصلي لكل من 32 + وكالة الذكاء الاصطناعي (كلود كود، كورسور، كودكس، جيميني CLI، OpenCode، إلخ). مصدر واحد من الحقيقة؛ العديد من المستهلكين.

### -كأس ثلاث طبقات

| Layer | File | Loaded when | Purpose |
|-------|------|-------------|---------|
| AGENTS.md | repo root | session start | project-level conventions |
| SKILL.md | skills directory | skill invoked | reusable workflow |
| MCP server | external process | tools needed | callable actions |

كل ثلاثة تتكون: العميل يقرأ AGENTS.md عند بدء الجلسة، ويدعو المستخدم إلى مهارة، وتشمل تعليمات المهارة مكالمات أداة MCP، ويرسل العميل عبر عميل MCP.

```figure
t3-skill-layers
```

## استخدمها

`code/main.py`يُرسل جهاز تحليل وملحوظة STDlib SKILL.md. يكتشف مهارات تحت`./skills/`، يُفحص المادة الأمامية YAML بالإضافة إلى جسم التسجيل، ويُنتج مقترحاً يُحدد باسم المهارة. ثم يحاكي حلقة العميل التي تدعو`release-notes-writer`باسمها

ما الذي يجب أن ننظر إليه:

- يامل المواد الأمامية تم تحليلها مع محلل القليل من القليل (لا `pyyaml`الإعتماد).
- تم تخزين جسم المهارات حرفياً، ويقوم العميل بتعديلها على نظام التسجيل عند الدعوة.
- الإفصاح التدريجي المثبت عن طريق `read_subresource`وظيفة تسحب الملفات المرجعية على الطلب.

## أرسله

هذا الدرس يُنتج`outputs/skill-agent-bundle.md`. في ضوء سير العمل، تنتج المهارة مجموعة SKILL.md + AGENTS.md + MCP-server-blueprint المشتركة، التي يمكن نقلها عبر العملاء.

## التمارين

1. أركض`code/main.py`إضافة مهارة ثانية تحت`skills/`و تأكد من أن الشاحنة ستلتقطها

2. اكتب AGENTS.md لهذا الدورة الإنتقالية. تضم أوامر الاختبار، اتفاقيات النمط، والنموذج العقلي المرحلة 13.

3. نقل تدفق عمل متعدد الخطوات من وثائق فريقك الداخلية إلى SKILL.md. التحقق من أن تحمله في كود كلود.

4. ترجمة المهارة إلى أشكال القواعد الأصلية لـ Cursor و Codex يدوياً. احتساب الفرق بين الأشكال  هذه هي سطح الترجمة SkillKit الآليات.

5. اقرأ مدونة المعلومات عن مهارات العميل الإنثروپي. حدد ميزة واحدة في SDK العميل كلود التي لا تغطي محمل هذا الدروس. (توصية: استدعاء العميل الفرعي)

## الشروط الرئيسية

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| SKILL.md | "The skill file" | YAML frontmatter plus markdown body, loaded by agent runtime |
| AGENTS.md | "Repo-root agent context" | Project-level conventions file read on session start |
| Progressive disclosure | "Lazy-load sub-resources" | Skill body references files pulled only when needed |
| Frontmatter | "YAML block at top" | Metadata (name, description) in `---` delimiters |
| Claude Agent SDK | "Anthropic's skill runtime" | `@anthropic-ai/claude-agent-sdk`, loads skills and routes |
| OpenAI Apps SDK | "MCP + widget meta" | OpenAI's dev surface built on MCP plus ChatGPT UI hooks |
| Skill discovery | "Filesystem scan" | Walk known dirs for SKILL.md, key by name |
| Cross-agent portability | "One skill many agents" | Translate one SKILL.md to 32+ agents via SkillKit-style tools |
| Agent Skill | "Portable know-how" | Reusable task template outside MCP's tool concept |
| Apps SDK | "MCP plus ChatGPT UI" | Connectors and Custom GPTs unified on MCP |

## المزيد من القراءة

- [Anthropic — Agent Skills announcement](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)إطلاقه في ديسمبر 2025
- [Anthropic — Agent Skills docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) إشارة إلى شكل SKILL.md
- [OpenAI — Apps SDK](https://developers.openai.com/apps-sdk) منصة تطوير على أساس MCP لـ ChatGPT
- [agents.md](https://agents.md/) تنسيق AGENTS.md و قائمة التبني
- [Anthropic — anthropics/skills GitHub](https://github.com/anthropics/skills) أمثلة على المهارات الرسمية
