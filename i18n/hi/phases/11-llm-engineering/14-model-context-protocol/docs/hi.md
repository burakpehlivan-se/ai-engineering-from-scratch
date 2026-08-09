# मॉडल संदर्भ प्रोटोकॉल (एमसीपी)

> 2025 से पहले निर्मित हर एलएलएम ऐप ने अपना स्वयं का टूल स्कीमा आविष्कार किया। फिर एंथ्रोपिक ने एमसीपी भेजा, क्लाउड ने इसे अपनाया, ओपनएआई ने इसे अपनाया, और 2026 तक यह किसी भी एलएलएम को किसी भी टूल, डेटा स्रोत या एजेंट से जोड़ने के लिए डिफ़ॉल्ट वायर प्रारूप है। एक एमसीपी सर्वर लिखें और प्रत्येक मेजबान इसके लिए बात करता है।

**Type:** Build
**Languages:** Python
**Prerequisites:** Phase 11 · 09 (Function Calling), Phase 11 · 03 (Structured Outputs)
**Time:** ~75 minutes

## समस्या

आप एक चैटबॉट भेजते हैं जिसमें तीन उपकरण की आवश्यकता होती हैः एक डेटाबेस क्वेरी, एक कैलेंडर एपीआई और एक फ़ाइल रीडर। आप क्लाउड के लिए तीन जेएसओएन योजनाएं लिखते हैं। फिर बिक्री चैटजीपीटी में समान उपकरण चाहता है  आप उन्हें ओपनएआई के लिए फिर से लिखते हैं `tools`पैरामीटर. फिर आप Cursor, Zed, और Claude Code  तीन और rewrites जोड़ते हैं, प्रत्येक में सूक्ष्म रूप से अलग JSON सम्मेलनों के साथ. एक सप्ताह बाद, मानव एक नया क्षेत्र जोड़ता है; आप छह योजनाओं को अपडेट करते हैं।

यह 2025 से पहले की वास्तविकता थी। प्रत्येक होस्ट (एलएलएम चलाने वाली चीज) और प्रत्येक सर्वर (उपकरणों और डेटा को उजागर करने वाली चीज) ने कस्टम प्रोटोकॉल भेजे। स्केलिंग का मतलब था एक एनएक्सएम एकीकरण मैट्रिक्स।

मॉडल कॉन्टेक्स्ट प्रोटोकॉल उस मैट्रिक्स को ढक देता है। एक JSON-RPC आधारित विनिर्देश। एक सर्वर उपकरण, संसाधन और संकेतों को उजागर करता है। कोई भी संगत होस्ट  क्लाउड डेस्कटॉप, चैटजीपीटी, कर्सर, क्लाउड कोड, जेड, और एजेंट फ्रेमवर्क की एक लंबी पूंछ  कस्टम गोंद के बिना उन्हें खोज और कॉल कर सकता है।

2026 की शुरुआत से, एमसीपी प्रमुख तीनों (एंट्रोपिक, ओपनएआई, गूगल) और प्रत्येक प्रमुख एजेंट हर्न में डिफ़ॉल्ट टूल-एंड-सीओटी प्रोटोकॉल है।

## अवधारणा

![MCP: one host, one server, three capabilities](../assets/mcp-architecture.svg)

**The three primitives.**एक MCP सर्वर ठीक तीन चीजों को उजागर करता है।

1. **Tools** फ़ंक्शन जो मॉडल कॉल कर सकता है।`tools`या मानवतावादी `tool_use`. प्रत्येक का नाम, विवरण, JSON योजना इनपुट, और एक हैंडलर है.
2. **Resources** केवल-पढ़ने वाली सामग्री जो मॉडल या उपयोगकर्ता अनुरोध कर सकता है (फ़ाइल, डेटाबेस पंक्तियाँ, एपीआई प्रतिक्रियाएं) ।
3. **Prompts** पुनः प्रयोज्य टेम्पलेट किए गए संकेत जो उपयोगकर्ता शॉर्टकट के रूप में उपयोग कर सकता है।

**The wire format.**JSON-RPC 2.0 स्टूडियो, वेबसॉकेट, या स्ट्रीम करने योग्य HTTP पर। प्रत्येक संदेश है `{"jsonrpc": "2.0", "method": "...", "params": {...}, "id": N}`. खोज विधिएँ हैं`tools/list`,`resources/list`,`prompts/list`. उद्धरण विधि `tools/call`,`resources/read`,`prompts/get`. .

**Host vs client vs server.**होस्ट LLM एप्लिकेशन (क्लाउड डेस्कटॉप) है। क्लाइंट होस्ट का एक उप-घटक है जो ठीक एक सर्वर से बात करता है। सर्वर आपका कोड है। एक होस्ट कई सर्वर को एक साथ माउंट कर सकता है।

### हाथ मिलाकर

प्रत्येक सत्र के साथ शुरू होता है `initialize`. क्लाइंट प्रोटोकॉल संस्करण और इसकी क्षमताओं को भेजता है. सर्वर अपनी संस्करण, नाम और समर्थन क्षमता सेट के साथ प्रतिक्रिया करता है (`tools`,`resources`,`prompts`,`logging`,`roots`) इसके बाद की हर चीज उन क्षमताओं के खिलाफ बातचीत की जाती है।

### एमसीपी क्या नहीं है

- RAG (चरण 11 · 06) अभी भी तय करता है कि क्या खींचना है; MCP संसाधनों के रूप में निकासी परिणामों को उजागर करने के लिए परिवहन है।
- एमसीपी प्लंपिंग है; लैंगग्राफ, पायदानटिकएआई और ओपनएआई एजेंट्स एसडीके जैसे फ्रेमवर्क इसके ऊपर बैठे हैं।
- मानचित्र और संदर्भ कार्यान्वयन के तहत ओपन सोर्स हैं।`modelcontextprotocol`org.

```figure
mcp-nxm-collapse
```

## इसे बनाओ

### चरण 1: न्यूनतम MCP सर्वर

आधिकारिक पायथन एसडीके है `mcp`(पूर्व में `mcp-python`) उच्च स्तरीय `FastMCP`सहायक हाथों को सजाते हैं।

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

@mcp.resource("config://app")
def app_config() -> str:
    """Return the app's current JSON config."""
    return '{"env": "prod", "region": "us-east-1"}'

@mcp.prompt()
def code_review(language: str, code: str) -> str:
    """Review code for correctness and style."""
    return f"You are a senior {language} reviewer. Review:\n\n{code}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

तीन सजावटकर्ता तीन आदिमों को पंजीकृत करते हैं। टाइप संकेत जेएसओएन योजना हो जाता है जो होस्ट देखता है। इसे क्लाउड डेस्कटॉप या क्लाउड कोड के तहत चलाएं जिसमें सर्वर प्रविष्टि इस फ़ाइल की ओर इशारा करती है।

### चरण 2: एक मेजबान से एक MCP सर्वर को कॉल करना

आधिकारिक पायथन क्लाइंट JSON-RPC बोलता है. मानव SDK के साथ इसे जोड़ने के लिए एक दर्जन लाइनों की आवश्यकता होती है.

```python
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp import ClientSession

params = StdioServerParameters(command="python", args=["server.py"])

async def call_add(a: int, b: int) -> int:
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            result = await session.call_tool("add", {"a": a, "b": b})
            return int(result.content[0].text)
```

`session.list_tools()`उत्पादन मेजबानों इन योजनाओं को प्रत्येक मोड़ में इंजेक्ट ताकि मॉडल एक उत्सर्जन कर सकते हैं`tool_use`ब्लॉक जो क्लाइंट फिर सर्वर को अग्रेषित करता है।

### चरण 3: स्ट्रीम करने योग्य HTTP परिवहन

स्थानीय डेवलपर के लिए स्टीडियो ठीक है। दूरस्थ उपकरणों के लिए, स्ट्रीम करने योग्य HTTP  एक POST प्रति अनुरोध का उपयोग करें, प्रगति के लिए वैकल्पिक सर्वर-सेंड इवेंट्स, 2025-06-18 विनिर्देश संशोधन के बाद से समर्थित।

```python
# Inside the server entrypoint
mcp.run(transport="streamable-http", host="0.0.0.0", port=8765)
```

होस्ट कॉन्फ़िगरेशन (Claude Desktop `mcp.json`या क्लाउड कोड `~/.mcp.json`):

```json
{
  "mcpServers": {
    "demo": {
      "type": "http",
      "url": "https://tools.example.com/mcp"
    }
  }
}
```

सर्वर एक ही सजावट रखता है; केवल परिवहन बदलता है।

### चरण 4: स्कोपिंग और सुरक्षा

एक MCP उपकरण किसी और के विश्वास सीमा पर चल रहा है मनमानी कोड है. तीन अनिवार्य पैटर्न.

- **Capability allowlists.**मेजबान एक `roots`उपकरण हैंडलर में लागू करें; मॉडल द्वारा प्रदान किए गए पथों पर भरोसा न करें।
- **Human-in-the-loop for mutation.**केवल-पढ़ने वाले उपकरण स्वचालित रूप से निष्पादित कर सकते हैं। लिखने/हटाने के लिए उपकरण पुष्टि की आवश्यकता होगी  सर्वर सेट होने पर मेजबान एक स्वीकृति UI सतह पर आते हैं `destructiveHint: true`उपकरण मेटाडेटा पर।
- **Tool poisoning defense.**एक दुर्भावनापूर्ण संसाधन में छिपे हुए शीघ्र इंजेक्शन निर्देश हो सकते हैं ("संक्षेप में, भी कॉल करें `exfil`) संसाधन सामग्री को अविश्वसनीय डेटा के रूप में व्यवहार करें; इसे सिस्टम संदेश क्षेत्र में कभी भी प्रवेश नहीं करने दें। चरण 11 · 12 (गार्ड्रेल) देखें।

देखो`code/main.py`एक चलाने योग्य सर्वर + क्लाइंट जोड़ी के लिए यह सब प्रदर्शित करता है।

## 2026 में भी फंसे हुए जाल

- **Schema drift.**मॉडल ने देखा `tools/list`मोड 1 में टूल सेट बदलता है 5 में टूल सेट बदलता है। मॉडल एक गायब उपकरण को बुलाता है। मेजबानों को फिर से सूचीबद्ध करना चाहिए।`notifications/tools/list_changed`. .
- **Large resource blobs.**संसाधन अपशिष्ट संदर्भ के रूप में 2MB फ़ाइल को छोड़ना. पृष्ठ या सर्वर-साइड सारांशित करें.
- **Too many servers.**50 एमसीपी सर्वर स्थापित करने से उपकरण बजट (चरण 11 · 05) उड़ा जाता है। अधिकांश सीमा मॉडल ~ 40 उपकरणों से परे गिरावट करते हैं।
- **Version skew.**विनिर्देश संशोधन (2024-11, 2025-03, 2025-06, 2025-12) में टूटने वाले फ़ील्ड पेश किए गए हैं।
- **Stdio deadlocks.**सर्वर जो stdout में लॉग करते हैं JSON-RPC धारा को भ्रष्ट करते हैं. केवल stderr में लॉग करें।

## इसका प्रयोग करें

2026 MCP स्टैकः

| Situation | Pick |
|-----------|------|
| Local dev, single-user tools | Python `FastMCP`, stdio transport |
| Remote team tools / SaaS integration | Streamable HTTP, OAuth 2.1 auth |
| TypeScript host (VS Code extension, web app) | `@modelcontextprotocol/sdk` |
| High-throughput server, typed access | Official Rust SDK (`modelcontextprotocol/rust-sdk`) |
| Exploring ecosystem servers | `modelcontextprotocol/servers` monorepo (Filesystem, GitHub, Postgres, Slack, Puppeteer) |

अंगूठे का नियमः यदि कोई उपकरण केवल-पढ़ने योग्य, कैश करने योग्य और दो या दो से अधिक मेजबानों से बुलाया जाता है, तो इसे MCP सर्वर के रूप में भेजें। यदि यह एक बार का इनलाइन तर्क है, तो इसे स्थानीय फ़ंक्शन के रूप में रखें (चरण 11 · 09) ।

## इसे भेजें

सहेजें`outputs/skill-mcp-server-designer.md`:

```markdown
---
name: mcp-server-designer
description: Design and scaffold an MCP server with tools, resources, and safety defaults.
version: 1.0.0
phase: 11
lesson: 14
tags: [llm-engineering, mcp, tool-use]
---

Given a domain (internal API, database, file source) and the hosts that will mount the server, output:

1. Primitive map. Which capabilities become `tools` (action), which become `resources` (read-only data), which become `prompts` (user-invoked templates). One line per primitive.
2. Auth plan. Stdio (trusted local), streamable HTTP with API key, or OAuth 2.1 with PKCE. Pick and justify.
3. Schema draft. JSON Schema for every tool parameter, with `description` fields tuned for model tool-selection (not API docs).
4. Destructive-action list. Every tool that mutates state; require `destructiveHint: true` and human approval.
5. Test plan. Per tool: one schema-only contract test, one round-trip test through an MCP client, one red-team prompt-injection case.

Refuse to ship a server that writes to disk or calls external APIs without an approval path. Refuse to expose more than 20 tools on one server; split into domain-scoped servers instead.
```

## व्यायाम

1. **Easy.**`demo-server`एक के साथ `subtract`उपकरण. इसे क्लाउड डेस्कटॉप से कनेक्ट करें. पुष्टि करें होस्ट एक रिस्टार्ट के बिना नया उपकरण उठाता है द्वारा जारी एक `tools/list_changed`अधिसूचना।
2. **Medium.**एक जोड़ें `resource`जो  के अंतिम 100 पंक्तियों को उजागर करता है`/var/log/app.log`. एक जड़ अनुमति सूची लागू करें तो`../etc/passwd`मॉडल द्वारा मांगी गई है, भले ही यह अवरुद्ध हो।
3. **Hard.**एक एमसीपी प्रॉक्सी बनाएं जो तीन अपस्ट्रीम सर्वर (फाइल सिस्टम, गिटहब, पोस्टग्रेस) को एक समग्र सतह में बहुविध बनाता है। नाम टकरावों को संभालें और आगे बढ़ें `notifications/tools/list_changed`साफ.

## प्रमुख शर्तें

| Term | What people say | What it actually means |
|------|-----------------|-----------------------|
| MCP | "Tool protocol for LLMs" | JSON-RPC 2.0 spec for exposing tools, resources, and prompts to any LLM host. |
| Host | "Claude Desktop" | The LLM application — owns the model and user UI, mounts one or more clients. |
| Client | "Connection" | A per-server connection inside the host that speaks JSON-RPC to exactly one server. |
| Server | "The thing with the tools" | Your code; advertises tools/resources/prompts and handles their invocation. |
| Tool | "Function call" | Model-invokable action with a JSON Schema input and a text/JSON result. |
| Resource | "Read-only data" | URI-addressed content (file, row, API response) the host can request. |
| Prompt | "Saved prompt" | User-invokable template (often with arguments) surfaced as a slash-command. |
| Stdio transport | "Local dev mode" | Parent host spawns the server as a child process; JSON-RPC over stdin/stdout. |
| Streamable HTTP | "The 2025-06 remote transport" | POST for requests, optional SSE for server-initiated messages; replaces the older SSE-only transport. |

## आगे पढ़ना

- [Model Context Protocol specification](https://modelcontextprotocol.io/specification) कैनोनिक संदर्भ, तारीख के अनुसार संस्करण।
- [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) फाइल सिस्टम, गिटहब, पोस्टग्रेस, स्लैक, पप्पीटर संदर्भ सर्वर।
- [Anthropic — Introducing MCP (Nov 2024)](https://www.anthropic.com/news/model-context-protocol) डिजाइन तर्क के साथ लॉन्च पोस्ट।
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk) इस पाठ में इस्तेमाल किया गया आधिकारिक एसडीके।
- [Security considerations for MCP](https://modelcontextprotocol.io/docs/concepts/security) जड़ें, विनाशकारी संकेत, उपकरण विषाक्तता।
- [Google A2A specification](https://a2a-protocol.org/latest/) एजेंट2एजेंट प्रोटोकॉल; एजेंट-से-एजेंट संचार के लिए भाई-बहन मानक जो एमसीपी के एजेंट-टू-टूल दायरे को पूरक करता है।
- [Anthropic — Building effective agents (Dec 2024)](https://www.anthropic.com/research/building-effective-agents) जहां एमसीपी एजेंट डिजाइन के लिए व्यापक पैटर्न लाइब्रेरी में स्थित है (अगस्त LLM, वर्कफ़्लो, स्वायत्त एजेंट) ।
