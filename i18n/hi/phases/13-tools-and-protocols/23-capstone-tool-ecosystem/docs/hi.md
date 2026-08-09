# कैपस्टोन  एक पूर्ण उपकरण पारिस्थितिकी तंत्र का निर्माण करें

> चरण 13 ने प्रत्येक टुकड़े को सिखाया। यह कैपस्टोन उन्हें एक उत्पादन-आकार के सिस्टम में तार करता हैः उपकरण + संसाधन + संकेत + कार्य + UI के साथ एक एमसीपी सर्वर, किनारे पर ओएथ 2.1, एक आरबीएसी गेटवे, एक मल्टी-सर्वर क्लाइंट, एक ए 2 ए उप-एजेंट कॉल, ओटेल को कलेक्टर में ट्रैक करना, सीआई में टूल-ट्राइकिंग का पता लगाना, और एक एजेंट्स.एमडी + स्किल.एमडी बंडल। अंत तक आप हर वास्तुकला विकल्प का बचाव कर सकते हैं।

**Type:** Build
**Languages:** Python (stdlib, end-to-end ecosystem harness)
**Prerequisites:** Phase 13 · 01 through 21
**Time:** ~120 minutes

## सीखने के लक्ष्य

- एक MCP सर्वर को लिखें जो उपकरण, संसाधन, संकेत और कार्य को एक `ui://`एप्लिकेशन।
- एक OAuth 2.1 गेटवे के साथ सर्वर के सामने जो RBAC और pinned हैश को लागू करता है।
- एक बहु-सर्वर क्लाइंट लिखें जो OTel GenAI गुणों के साथ अंत-से-अंत को ट्रैक करता है।
- कार्यभार का एक भाग A2A उप-एजेंट को सौंपें; सुनिश्चित करें कि अस्पष्टता बरकरार है।
- एजेंटों.md + कौशल.md के साथ पूरे स्टैक को पैक करें ताकि अन्य एजेंट इसे चला सकें।

## समस्या

"अनुसंधान और रिपोर्ट" प्रणाली को भेजेंः

- उपयोगकर्ता पूछता हैः "एजेंट प्रोटोकॉल पर सबसे ज्यादा उद्धृत 2026 arXiv कागजातों का सारांश दें। "
- प्रणालीः खोज MCP के माध्यम से arXiv; A2A के माध्यम से एक विशेषज्ञ लेखक एजेंट को कागज सारांश सौंपने; समग्र परिणाम; एक इंटरैक्टिव रिपोर्ट MCP Apps के रूप में प्रस्तुत करें `ui://`संसाधन; ओटीएल के लिए हर कदम लॉग.

चरण 13 के सभी आदिम दिखाई देते हैं। यह एक खिलौना नहीं है  उत्पादन अनुसंधान-सहायक प्रणाली 2026 में एंथ्रोपिक (क्लाउड रिसर्च उत्पाद), ओपनएआई (एप्स एसडीके के साथ जीपीटी), और तीसरे पक्ष द्वारा शिप किया गया है।

## अवधारणा

### वास्तुकला

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

### निशान पदानुक्रम

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

एक निशान आईडी. प्रत्येक स्पैन के पास अधिकार है`gen_ai.*`गुण।

### सुरक्षा की स्थिति

- OAuth 2.1 + PKCE संसाधन संकेतक दर्शकों को गेटवे पर चिपकाकर।
- गेटवे अपस्ट्रीम क्रेडेंशियल रखता है; उपयोगकर्ता उन्हें कभी नहीं देखता है।
- आरबीएसी: `alice`है`research:read`,`research:write`, सभी उपकरणों को बुला सकता है।`bob`है`research:read`, फोन नहीं कर सकते `generate_report`. .
- पिन किया गया विवरण घोषणापत्रः किसी भी सर्वर को छोड़ दिया गया जिसका टूल हैश बदल गया।
- दो नियम का लेखा-परीक्षणः कोई भी उपकरण अविश्वसनीय इनपुट, संवेदनशील डेटा और परिणामी कार्रवाई को जोड़ता नहीं है।

### प्रतिपादन

अंतिम `generate_report`कार्य सामग्री ब्लॉकों प्लस एक लौटाता है `ui://report/current`संसाधन. क्लाइंट का होस्ट (क्लाउड डेस्कटॉप, आदि) एक सैंडबॉक्स iframe में इंटरैक्टिव डैशबोर्ड को प्रस्तुत करता है। डैशबोर्ड में एक सॉर्ट पेपर सूची, उद्धरण गिनती और एक बटन होता है जो कॉल करता है `host.callTool('summarize_paper', {arxiv_id})`किसी भी कागज के लिए उपयोगकर्ता क्लिक करता है।

### पैकेजिंग

पूरी बात जहाजों के रूप मेंः

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

 के साथ उपयोगकर्ता तैनात`docker compose up`. क्लाउड कोड, cursor, codex और opencode उपयोगकर्ता सिस्टम को चला सकते हैं`run-research`कौशल।

### चरण 13 के प्रत्येक पाठ का क्या योगदान था

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

## इसका प्रयोग करें

`code/main.py`यह अनुसंधान और रिपोर्ट परिदृश्य के लिए पूर्ण प्रवाह चलाता हैः गेटवे के साथ हाथ मिलाएं, OAuth 2.1 का अनुकरण करें, उपकरण / सूची को मिलाएं, एक कार्य के रूप में उत्पन्न करें_रिपोर्ट करें, लेखक को A2A कॉल करें, ui:// संसाधन लौटाएं, OTel स्पैन जारी करें।

क्या देखना हैः

- प्रत्येक कूद पर एक निशान आईडी.
- गेटवे नीति दूसरे उपयोगकर्ता को लिखने से रोकती है।
- कार्य जीवन चक्र काम करने के लिए चला जाता है → पूरा और पाठ और ui:// सामग्री दोनों को वापस करता है.
- A2A कॉल की आंतरिक स्थिति ऑर्केस्ट्रेटर के लिए अस्पष्ट है।
- एजेंट्स.एमडी और स्किल.एमडी एकमात्र फाइलें हैं जिनकी किसी अन्य एजेंट को वर्कफ़्लो को पुनः पेश करने की आवश्यकता होती है।

## इसे भेजें

यह सबक हमें फल देता है`outputs/skill-ecosystem-blueprint.md`. उत्पाद की आवश्यकता (अनुसंधान, संक्षेप, स्वचालन) को देखते हुए, कौशल पूर्ण वास्तुकला का उत्पादन करता हैः कौन सी एमसीपी आदिम, कौन सी गेटवे नियंत्रण करती है, कौन सी ए 2 ए कॉल करती है, कौन सी टेलीमेट्री, कौन सा पैकेजिंग।

## व्यायाम

1. दौड़ें`code/main.py`. एकल निशान आईडी और कैसे विस्तार घोंसला ध्यान दें. चरण 13 से कितने आदिमों की संख्या डेमो स्पर्श करता है.

2. डेमो का विस्तार करेंः एक दूसरा बैक-एंड एमसीपी सर्वर जोड़ें (जैसे `bibliography`) और पुष्टि करें कि गेटवे अपने उपकरणों को एक ही नाम स्थान में मिलाता है।

3. एक उपप्रक्रिया पर चल रहे एक असली एक के साथ नकली ए 2 ए लेखक एजेंट की जगह. पाठ 19 हर्नर का उपयोग करें.

4. ऑर्केस्ट्रेटर और एलएलएम के बीच रूटिंग गेटवे में पीआईआई संपादन चरण जोड़ें। उपयोगकर्ता क्वेरी में पुष्टि ईमेल को स्क्रब किया जाता है।

5. एक टीम के साथी के लिए एक एजेंट्स.एमडी लिखें जो इस प्रणाली को बनाए रखेगा। इसे पढ़ने में पांच मिनट से कम समय लगना चाहिए और उन्हें सब कुछ देना चाहिए जो उन्हें कर्सर या कोडेक्स में मुख्य पत्थर को चलाने के लिए आवश्यक है।

## प्रमुख शर्तें

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

## आगे पढ़ना

- [MCP — Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) समेकित संदर्भ
- [MCP blog — 2026 roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) जहां प्रोटोकॉल का दिशा है
- [a2a-protocol.org](https://a2a-protocol.org/latest/) A2A v1.0 संदर्भ
- [OpenTelemetry — GenAI semconv](https://opentelemetry.io/docs/specs/semconv/gen-ai/) कैनोनिक ट्रैकिंग कन्वेंशन
- [Anthropic — Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) उत्पादन एजेंट रनटाइम पैटर्न
