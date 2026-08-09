# कौशल और एजेंट एसडीके  मानव कौशल, एजेंट्स.एमडी, ओपनएआई ऐप्स एसडीके

> MCP कहता है "कौन से उपकरण मौजूद हैं।" कौशल कहते हैं "क्यों एक कार्य करने के लिए।" 2026 स्टैक दोनों परतों. मानव संसाधन एजेंट कौशल (खुला मानक, दिसंबर 2025) क्रमिक प्रकटीकरण के साथ SKILL.md के रूप में जहाज। OpenAI के Apps SDK में MCP प्लस विजेट मेटाडेटा है। एजेंट्स.एमडी (अब 60,000+ रिपो में) परियोजना स्तर के एजेंट संदर्भ के रूप में रिपो रूट पर बैठता है। यह सबक क्या कवर करता है, इसका नाम देता है और एक न्यूनतम SKILL.md + AGENTS.md बंडल बनाता है जो एजेंटों के बीच यात्रा करता है।

**Type:** Learn
**Languages:** Python (stdlib, SKILL.md parser and loader)
**Prerequisites:** Phase 13 · 07 (MCP server)
**Time:** ~45 minutes

## सीखने के लक्ष्य

- तीन परतों में अंतर करेंः एजेंट्स.एमडी (परियोजना संदर्भ), स्किल.एमडी (पुनर्उपयोग योग्य ज्ञान) और एमसीपी (उपकरण) ।
- यमल के सामने की सामग्री और प्रगतिशील प्रकटीकरण के साथ एक SKILL.md लिखें।
- एक एजेंट रनटाइम में फ़ाइल सिस्टम शैली कौशल लोड करें।
- एक एमसीपी सर्वर और एक एजेंट्स.एमडी के साथ एक कौशल को लिखें ताकि एक पैकेज क्लाउड कोड, कर्सर और कोडेक्स में काम करे।

## समस्या

एक इंजीनियर एक रिलीज़-नोट्स-लिखी कार्यप्रवाह को एक बहु-चरण प्रलोभन में हटा देता हैः "अंतिम विलयित पीआर पढ़ें। क्षेत्र द्वारा समूह। प्रत्येक का सारांश दें। टीम की शैली के अनुसार एक चेंजलॉग प्रविष्टि लिखें। स्लैक ड्राफ्ट में पोस्ट करें। " उन्होंने इसे अपनी टीम के लिए एक नोशन डॉक्यूमेंट में रखा।

अब वे क्लाउड कोड, कर्सर और कोडेक्स CLI से इस कार्यप्रवाह का उपयोग करना चाहते हैं। प्रत्येक एजेंट के पास निर्देशों को लोड करने का एक अलग तरीका हैः क्लाउड कोड स्लैश-कमांड, कर्सर नियम, कोडेक्स `.codex.md`इंजीनियर काम के प्रवाह को तीन बार कॉपी करता है और तीन प्रतियां रखता है।

एजेंट्स.एमडी और स्किल.एमडी मिलकर इसको ठीक करेंः

- **AGENTS.md**यह एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन एजेंट है जो एक अनुपालन है जो एक अनुपालन है कि एक अनुपालन एजेंट है जो एक अनुपालन है जो एक अनुपालन है कि एक अनुपालन है कि एक अनुपालन है कि एक अनुपालन है जो एक अनुपालन है कि एक अनुपालन है कि एक अनुपालन है कि एक अनुपालन है कि एक है जो एक है जो एक है कि एक है जो एक है कि एक है जो एक है कि एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है जो एक है
- **SKILL.md**एक पोर्टेबल बंडल हैः YAML फ्रंटमैटर (नाम, विवरण) + मार्कडाउन बॉडी + वैकल्पिक संसाधन। कौशल का समर्थन करने वाले एजेंट उन्हें नाम से लोड करते हैं।
- **MCP**(चरण 13 · 06-14) कौशल को जिन उपकरणों का उपयोग करने की आवश्यकता है, उन्हें संभालता है।

तीन परतें, एक पोर्टेबल कलाकृतियों.

## अवधारणा

### एजेंट्स.एमडी (एजेंट्स.एमडी)

अप्रैल 2026 तक 60,000+ रिपो द्वारा अपनाया गया। रिपो रूट पर एक फ़ाइल। प्रारूपः

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

एजेंट यह सत्र शुरू में पढ़ते हैं और इसका उपयोग उस परियोजना के लिए अपने व्यवहार को मापने के लिए करते हैं। 2026 में हर कोडिंग एजेंट एजेंट्स.एमडी का समर्थन करता हैः क्लाउड कोड, कर्सर, कोडेक्स, कॉपिलाइट वर्कस्पेस, ओपनकोड, विंडसर्फ, जेड।

### SKILL.md प्रारूप

एंथ्रोपिक के एजेंट कौशल (डिसेम्बर 2025 में एक खुले मानक के रूप में जारी किया गया):

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

सामने की सामग्री कौशल की पहचान घोषित करती है। शरीर कौशल लोड होने पर मॉडल को दिखाया गया संकेत है।

### प्रगतिशील प्रकटीकरण

कौशल उप-स्रोतों का संदर्भ दे सकता है जो एजेंट केवल आवश्यकता के समय लाता है। उदाहरणः

```
skills/
  release-notes-writer/
    SKILL.md
    style-guide.md
    template.md
    scripts/
      generate.sh
```

SKILL.md कहते हैं "शैली-निर्देशक.md देखें शैली नियमों के लिए।" एजेंट केवल शैली-निर्देशक.md खींचता है जब कौशल सक्रिय रूप से चल रहा है। यह मॉडल की आवश्यकता नहीं हो सकती है के साथ प्रॉम्प्ट को फुलाव से बचता है।

### फ़ाइल प्रणाली खोज

एजेंट रनटाइम SKILL.md फ़ाइलों के लिए ज्ञात निर्देशिकाओं स्कैनः

- `~/.anthropic/skills/*/SKILL.md`
- परियोजना `./skills/*/SKILL.md`
- `~/.claude/skills/*/SKILL.md`

लोड फ़ोल्डर नाम और सामने की सामग्री के अनुसार होता है `name`. क्लाउड कोड, मानव क्लाउड एजेंट एसडीके, और कौशलकिट (क्रॉस एजेंट) सभी इस पैटर्न का पालन करते हैं।

### मानव क्लाउड एजेंट एसडीके

`@anthropic-ai/claude-agent-sdk`(टाइपस्क्रिप्ट) और `claude-agent-sdk`सत्र शुरू करने पर लोड कौशल, उन्हें रनटाइम के भीतर बुलाए जाने वाले "एजेंट" के रूप में उजागर करें। एजेंट लूप एक कौशल को भेजता है जब उपयोगकर्ता इसे बुलाता है।

### OpenAI Apps SDK

अक्टूबर 2025 में लॉन्च किया गया; सीधे एमसीपी पर बनाया गया। एक एकल डेवलपर सतह के तहत ओपनएआई के पूर्व कनेक्टर्स और कस्टम जीपीटी कार्यों को एकीकृत करता है। एक ऐप्स एसडीके ऐप हैः

- एक MCP सर्वर (उपकरण, संसाधन, संकेत)
- और चैटजीपीटी के UI के लिए विजेट मेटाडेटा.
- प्लस एक वैकल्पिक MCP Apps `ui://`इंटरैक्टिव सतहों के लिए संसाधन।

एक ही प्रोटोकॉल, अधिक समृद्ध अनुभव.

### SkillKit के माध्यम से क्रॉस एजेंट पोर्टेबिलिटी

SkillKit जैसे उपकरण और इसी तरह के क्रॉस-एजेंट वितरण परतें एक SKILL.md को 32+ AI एजेंटों (क्लाउड कोड, कर्सर, कोडेक्स, जेमिनी CLI, ओपनकोड, आदि) के प्रत्येक के मूल स्वरूप में अनुवाद करती हैं। एक सत्य स्रोत; कई उपभोक्ता।

### तीन परतों का ढेर

| Layer | File | Loaded when | Purpose |
|-------|------|-------------|---------|
| AGENTS.md | repo root | session start | project-level conventions |
| SKILL.md | skills directory | skill invoked | reusable workflow |
| MCP server | external process | tools needed | callable actions |

तीनों ही रचनाएँः एजेंट सत्र की शुरुआत में AGENTS.md पढ़ता है, उपयोगकर्ता एक कौशल का आह्वान करता है, कौशल के निर्देशों में MCP उपकरण कॉल शामिल हैं, एजेंट एक MCP क्लाइंट के माध्यम से भेजता है।

```figure
t3-skill-layers
```

## इसका प्रयोग करें

`code/main.py`यह एक stdlib SKILL.md पार्सर और लोडर भेजता है। यह कौशल के तहत खोजता है`./skills/`, YAML फ्रंटमैटर और मार्कडाउन बॉडी को पार्स करता है, और कौशल नाम से कुंजीबद्ध एक डिक्टेट उत्पन्न करता है। यह फिर एक एजेंट लूप का अनुकरण करता है जो कॉल करता है`release-notes-writer`नाम से।

क्या देखना हैः

- YAML फ्रंटमैटर को न्यूनतम stdlib पार्सर (नहीं `pyyaml`निर्भरता) ।
- कौशल शरीर शब्दशः संग्रहीत; एजेंट इसे कॉल पर सिस्टम के संकेत पर प्रीपेन्ड करता है।
- एक `read_subresource`फ़ंक्शन जो अनुरोध पर संदर्भित फ़ाइलों को खींचता है।

## इसे भेजें

यह सबक हमें फल देता है`outputs/skill-agent-bundle.md`. एक कार्यप्रवाह को देखते हुए, कौशल एक संयुक्त SKILL.md + AGENTS.md + MCP-server-blueprint bundle का उत्पादन करता है, जो एजेंटों के बीच पोर्टेबल है।

## व्यायाम

1. दौड़ें`code/main.py`. नीचे एक दूसरा कौशल जोड़ें `skills/`और लोडर इसे उठाता है पुष्टि.

2. इस पाठ्यक्रम रेपो के लिए एक एजेंट्स.एमडी लिखें. परीक्षण कमांड, शैली सम्मेलन, और चरण 13 मानसिक मॉडल शामिल करें।

3. अपनी टीम के आंतरिक दस्तावेजों से एक बहु-चरण कार्यप्रवाह को एक SKILL.md में पोर्ट करें। इसे क्लाउड कोड में लोड करें।

4. कौशल को पाठ्यक्रम और कोडेक्स के मूल नियम प्रारूपों में हाथ से अनुवाद करें। प्रारूपों के बीच अंतर गिनें  यह अनुवाद सतह SkillKit स्वचालित है।

5. मानव एजेंट कौशल ब्लॉग पोस्ट पढ़ें। क्लाउड एजेंट एसडीके में एक विशेषता की पहचान करें जिसे इस पाठ के लोडर में शामिल नहीं किया गया है। (संकेतः एजेंट उप-उल्लेखना)

## प्रमुख शर्तें

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

## आगे पढ़ना

- [Anthropic — Agent Skills announcement](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) दिसंबर 2025 में लॉन्च
- [Anthropic — Agent Skills docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) SKILL.md प्रारूप संदर्भ
- [OpenAI — Apps SDK](https://developers.openai.com/apps-sdk) ChatGPT के लिए MCP आधारित डेवलपर प्लेटफॉर्म
- [agents.md](https://agents.md/) AGENTS.md प्रारूप और अपनाए जाने की सूची
- [Anthropic — anthropics/skills GitHub](https://github.com/anthropics/skills) आधिकारिक कौशल के उदाहरण
