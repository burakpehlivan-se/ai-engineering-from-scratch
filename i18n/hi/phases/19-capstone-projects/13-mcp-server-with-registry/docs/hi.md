# कैपस्टोन 13  रजिस्ट्री और गवर्नेंस के साथ एमसीपी सर्वर

> मॉडल कॉन्टेक्स्ट प्रोटोकॉल भविष्य नहीं रहा और 2026 में डिफ़ॉल्ट टूल-यूज स्पेसिफिकेशन बन गया। एंथ्रोपिक, ओपनएआई, गूगल और हर प्रमुख आईडीई जहाज एमसीपी क्लाइंट। Pinterest ने एमसीपी सर्वर के अपने आंतरिक पारिस्थितिकी तंत्र को प्रकाशित किया। एएआईएफ रजिस्ट्री ने क्षमता मेटाडेटा को औपचारिक रूप दिया।`.well-known`. AWS ECS ने संदर्भ स्टेटलेस तैनाती प्रकाशित की। ब्लॉक के हंस-एजेंट ने होस्ट किए गए सहायक के अंदर एक ही प्रोटोकॉल रखा। 2026 उत्पादन आकार हैः StreamableHTTP परिवहन, OAuth 2.1 स्कोप, OPA नीति गेटिंग, और एक रजिस्ट्री जो प्लेटफॉर्म टीमों को सर्वर का पता लगाने, सत्यापित करने और सक्षम करने की अनुमति देता है। इसे अंत से अंत तक बनाएं।

**Type:** Capstone
**Languages:** Python (server, via FastMCP) or TypeScript (@modelcontextprotocol/sdk), Go (registry service)
**Prerequisites:** Phase 11 (LLM engineering), Phase 13 (tools and MCP), Phase 14 (agents), Phase 17 (infrastructure), Phase 18 (safety)
**Phases exercised:**P11 · P13 · P14 · P17 · P18
**Time:** 25 hours

## समस्या

एमसीपी उपकरण-उपयोग की भाषा बन गया। क्लाउड कोड, कर्सर 3, एम्प, ओपनकोड, जेमिनी सीएलआई, और हर प्रबंधित एजेंट अब एमसीपी सर्वर का उपभोग करते हैं। उत्पादन चुनौतियां सर्वरों को बनाने में नहीं हैं (फास्टएमसीपी इसे आसान बनाता है) लेकिन उद्यम आवश्यकताओं के साथ उन्हें पैमाने पर तैनात करनाः प्रति किरायेदार ओएथ स्कोप, विनाशकारी उपकरणों पर ओपीए नीति, स्ट्रीमएबलएचटीपी स्टेटलेस स्केलिंग, खोज के लिए एक रजिस्ट्री, ऑडिट लॉग प्रति उपकरण कॉल। Pinterest के आंतरिक MCP पारिस्थितिकी तंत्र और AAIF रजिस्ट्री विनिर्देश 2026 बार सेट करते हैं।

आप एक एमसीपी सर्वर बनाएंगे जो 10 आंतरिक उपकरणों (पोस्टग्रेस केवल पढ़ने के लिए, एस 3 लिस्टिंग, जिरा, रैखिक, डेटाडॉग, आदि) को उजागर करता है, प्लेटफॉर्म की खोज के लिए एक रजिस्ट्री यूआई, और विनाशकारी उपकरणों के लिए एक मानव-अनुमोदित गेट। लोड परीक्षण StreamableHTTP क्षैतिज स्केलिंग प्रदर्शित करता है। ऑडिट ट्रेल एक उद्यम सुरक्षा समीक्षा को संतुष्ट करता है।

## अवधारणा

MCP 2026 संशोधन स्ट्रीमबलएचटीपी को डिफ़ॉल्ट परिवहन के रूप में अनिवार्य करता है। पहले के स्टीडियो-और-एसएसई प्रारूप के विपरीत, स्ट्रीमबलएचटीपी डिफ़ॉल्ट रूप से स्टेटलेस हैः एक एकल एचटीटीपी एंडपॉइंट जेएसओएन-आरपीसी अनुरोधों को स्वीकार करता है, प्रतिक्रियाओं को स्ट्रीम करता है, और अधिसूचनाओं के लिए लंबे समय तक चलने वाले कनेक्शन का समर्थन करता है। स्टेटलेस का मतलब है कि लोड बैलेंसर के पीछे क्षैतिज रूप से स्केलेबल।

प्राधिकरण OAuth 2.1 है प्रति उपकरण स्कोप के साथ. एक टोकन स्कोप जैसे है`jira:read`,`s3:list`,`postgres:query:readonly`. एमसीपी सर्वर उपकरण कॉल के समय स्कोप की जांच करता है, न कि केवल सत्र की शुरुआत। उच्च जोखिम वाले उपकरणों के लिए, सर्वर किसी भी कॉल को अस्वीकार करता है जिसका स्कोप नहीं बढ़ाया गया है `approved:by:human`पिछले N मिनट के भीतर  कि ऊंचाई एक Slack समीक्षा कार्ड से आता है।

रजिस्ट्री एक अलग सेवा है. प्रत्येक MCP सर्वर एक`.well-known/mcp-capabilities`दस्तावेज़ अपने उपकरण मैनिफेस्ट, परिवहन URL, लेखक आवश्यकताओं के साथ। रजिस्ट्री सर्वेक्षण, सत्यापन और सूचकांक। प्लेटफॉर्म टीमों को यह देखने के लिए रजिस्ट्री UI का उपयोग किया जाता है कि कौन से उपकरण उपलब्ध हैं, उन्हें किस दायरे की आवश्यकता है, और कौन सी टीमें उन्हें मालिक हैं।

## वास्तुकला

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

## स्टैक

- सर्वर फ्रेमवर्क: फास्टएमसीपी (पाइटन) या `@modelcontextprotocol/sdk`(टाइपस्क्रिप्ट)
- परिवहनः HTTPS (अराजकता रहित) पर StreamableHTTP
- Auth: OAuth 2.1 के साथ कार्यभार पहचान SPIFFE / SPIRE के माध्यम से
- नीति: ओपीए/रेगो नियम प्रति उपकरण; नीति निर्णय सेवा अनुरोध पर
- रजिस्ट्रीः स्वयं-होस्ट, खपत `.well-known/mcp-capabilities`प्रपत्र
- मानव अनुमोदनः विनाशकारी उपकरणों के लिए स्लैक इंटरैक्टिव संदेश
- तैनातीः AWS ECS Fargate या Fly.io, प्रति किरायेदार एक सर्वर या किरायेदार स्कोपिंग के साथ साझा
- ऑडिटः प्रति कॉल वंशावली के साथ संरचित JSONL प्रति किरायेदार बाल्ट

```figure
cf-mcp-gate
```

## इसे बनाओ

1. **Tool surface.**10 आंतरिक उपकरण प्रदर्शित करेंः पोस्टग्रेस केवल पढ़ने के लिए क्वेरी, एस 3 सूची ऑब्जेक्ट्स, जिरा खोज / प्राप्त, रैखिक खोज / प्राप्त, डेटाडॉग मीट्रिक क्वेरी, पेजरड्यूटी ऑन-कॉल खोज, गिटहब केवल पढ़ने के लिए, संज्ञा खोज, स्लैक खोज, सेल्सफोर्स पढ़ने। प्रत्येक उपकरण में एक टाइप स्कीमा और एक स्कोप लेबल है।

2. **FastMCP server.**उपकरण स्थापित करें. StreamableHTTP परिवहन कॉन्फ़िगर करें. OAuth टोकन अंतर्दृष्टि और दायरा प्रवर्तन के लिए एक मध्यवेयर जोड़ें.

3. **OPA policy.**प्रति उपकरण नीतिः किस सीमाओं द्वारा कॉल की अनुमति दी जाती है, PII को संपादित करने के लिए क्या लागू होता है, उपयोगिता भार आकार के कैप क्या लागू होते हैं। निर्णय सेवा हर उपकरण कॉल पर बुलाया जाता है।

4. **Registry service.**मतगणना करने वाली अलग-अलग गो या टीएस सेवा `.well-known/mcp-capabilities`पंजीकृत सर्वर से, JSON योजना के साथ मान्य करता है, और एक सूची / खोज / सत्यापित / सक्षम करने योग्य UI उजागर करता है।

5. **Capability manifest.**प्रत्येक सर्वर उजागर करता है `.well-known/mcp-capabilities`के साथः उपकरण सूची, लेखक आवश्यकताओं, परिवहन URL, मालिक टीम, SLO.

6. **Destructive tool separation.**उत्परिवर्तन राज्य (जिरा बनाएँ, रैखिक बनाएँ, पोस्टग्रेस लिखें) के उपकरण एक और अधिक सख्त auth प्रवाह के साथ एक दूसरे MCP सर्वर पर रहते हैंः टोकन में एक होना चाहिए `approved:by:human`स्लैक कार्ड के माध्यम से 15 मिनट के भीतर दायरा बढ़ाया गया।

7. **Audit log.**प्रति किरायेदार केवल जोड़ने के लिए JSONL: `{timestamp, user, tool, args_redacted, response_redacted, outcome}`. लिखने से पहले प्रेसिडियो के माध्यम से पीआईडी को संपादित करें.

8. **Load test.**StreamableHTTP पर 100 समवर्ती क्लाइंट। एक दूसरी प्रतिकृति जोड़कर क्षैतिज स्केलिंग प्रदर्शित करें; सत्र चिपचिपाहट के बिना लोड बैलेंसर को पुनः वितरित करें।

9. **Conformance tests.**दोनों सर्वरों के खिलाफ आधिकारिक MCP अनुरूपता सूट चलाएं. सभी अनिवार्य अनुभागों को पास करें.

## इसका प्रयोग करें

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

## इसे भेजें

`outputs/skill-mcp-server.md`OAuth 2.1 स्कोप और OPA गेटिंग के साथ आंतरिक उपकरणों के लिए एक उत्पादन-ग्रेड MCP सर्वर + रजिस्ट्री + ऑडिट परत।

| Weight | Criterion | How it is measured |
|:-:|---|---|
| 25 | Spec conformance | StreamableHTTP + capability manifest passes MCP conformance tests |
| 20 | Security | Scope enforcement, OPA coverage across every tool, secret hygiene |
| 20 | Observability | Per-tool-call audit log with PII redaction |
| 20 | Scale | 100-client load test horizontal scale demonstration |
| 15 | Registry UX | Discover / validate / enable-disable workflow |
| **100** | | |

## व्यायाम

1. एक नया उपकरण जोड़ें (संयोजन खोज) इसे कोर सर्वर को छूने के बिना रजिस्ट्री सत्यापन प्रवाह के माध्यम से भेजें।

2. एक OPA नीति लिखें जो Postgres क्वेरी के परिणामों को नामित स्तंभों से सम्पादित करता है `email`,`ssn`या `phone`. एक जांच प्रश्न के साथ अभ्यास.

3. स्थानीय विलंबता पर स्ट्रीम करने योग्य HTTP बनाम स्टिडियो बेंचमार्क करें। प्रति कॉल रिपोर्ट p50/p95.

4. प्रति किरायेदार कोटा लागू करेंः प्रति किरायेदार प्रति उपकरण प्रति मिनट अधिकतम N कॉल। दूसरे OPA नियम के माध्यम से लागू करें।

5. MCP अनुरूपता सूट को  से चलाएं[mcp-conformance-tests](https://github.com/modelcontextprotocol/conformance)और हर असफलता को ठीक करना।

## प्रमुख शर्तें

| Term | What people say | What it actually means |
|------|-----------------|------------------------|
| StreamableHTTP | "2026 MCP transport" | Stateless HTTP + streaming; replaces SSE + stdio for networked servers |
| Capability manifest | "Well-known doc" | `.well-known/mcp-capabilities` with tool list, auth, transport URL |
| OPA / Rego | "Policy engine" | Open Policy Agent for authorizing tool calls against external rules |
| Scope elevation | "Approved-by-human" | Short-lived scope granted via Slack approval, required for destructive tools |
| Registry | "Tool discovery" | Service that indexes MCP servers from their capability manifests |
| Workload identity | "SPIFFE / SPIRE" | Cryptographic service identity for OAuth token issuance |
| Conformance suite | "Spec tests" | Official MCP test battery for StreamableHTTP + tool manifest correctness |

## आगे पढ़ना

- [Model Context Protocol 2026 Roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) StreamableHTTP, क्षमता मेटाडेटा, रजिस्ट्री
- [AAIF MCP Registry spec](https://github.com/modelcontextprotocol/registry) 2026 रजिस्ट्री स्पेसिफिकेशन
- [AWS ECS reference deployment](https://aws.amazon.com/blogs/containers/deploying-model-context-protocol-mcp-servers-on-amazon-ecs/) संदर्भ उत्पादन की तैनाती
- [Pinterest internal MCP ecosystem](https://www.infoq.com/news/2026/04/pinterest-mcp-ecosystem/) संदर्भ आंतरिक तैनाती
- [Block `goose` MCP usage](https://block.github.io/goose/) संदर्भ एजेंट खपत पैटर्न
- [FastMCP](https://github.com/jlowin/fastmcp) पायथन सर्वर फ्रेमवर्क
- [Open Policy Agent](https://www.openpolicyagent.org/) नीति इंजन संदर्भ
- [SPIFFE / SPIRE](https://spiffe.io) कार्यभार पहचान संदर्भ
