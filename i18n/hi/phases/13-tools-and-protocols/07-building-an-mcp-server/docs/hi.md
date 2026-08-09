# एक MCP सर्वर  पायथन + टाइपस्क्रिप्ट एसडीके बनाना

> अधिकांश एमसीपी ट्यूटोरियल केवल स्टूडियो हैलो-वर्ल्ड्स दिखाते हैं। एक वास्तविक सर्वर उपकरण और संसाधन और संकेतों को उजागर करता है, क्षमता वार्ता को संभालता है, संरचित त्रुटियों को उत्सर्जित करता है, और एसडीके के माध्यम से समान काम करता है। यह पाठ एक नोट सर्वर अंत-से-अंत का निर्माण करता हैः stdlib स्टूडियो परिवहन, JSON-RPC डिस्पैच, तीन सर्वर आदिम, और एक शुद्ध-कार्य शैली जो या तो पायथन एसडीके के फास्टएमसीपी या टाइपस्क्रिप्ट एसडीके में गिर जाता है जब आप स्नातक करते हैं।

**Type:** Build
**Languages:** Python (stdlib, stdio MCP server)
**Prerequisites:** Phase 13 · 06 (MCP fundamentals)
**Time:** ~75 minutes

## सीखने के लक्ष्य

- कार्यान्वयन`initialize`,`tools/list`,`tools/call`,`resources/list`,`resources/read`,`prompts/list`और `prompts/get`विधि।
- एक डिस्पैच लूप लिखें जो stdin से JSON-RPC संदेशों को पढ़ता है और stdout के लिए प्रतिक्रिया लिखता है।
- JSON-RPC 2.0 विनिर्देश और MCP के अतिरिक्त कोड के अनुसार संरचित त्रुटि प्रतिक्रियाएं जारी करें।
- उपकरण तर्क को फिर से लिखने के बिना फास्टएमसीपी (पायथन एसडीके) या टाइपस्क्रिप्ट एसडीके में एक स्टडीलिब कार्यान्वयन को स्नातक करें।

## समस्या

इससे पहले कि आप एक रिमोट ट्रांसपोर्ट (चरण 13 · 09) या एक auth परत (चरण 13 · 16) का उपयोग कर सकें, आपको एक साफ स्थानीय सर्वर की आवश्यकता है। स्थानीय का अर्थ है stdio: सर्वर क्लाइंट द्वारा एक बच्चे की प्रक्रिया के रूप में उत्पन्न किया जाता है, संदेश stdin/stdout newline-delimited पर बहते हैं।

2025-11-25 विनिर्देशों को निर्धारित करता है कि स्टूडियो संदेशों को स्पष्ट रूप से के साथ JSON वस्तुओं के रूप में एन्कोड किया जाता है `\n`यहाँ कोई SSE नहीं है; SSE पुराना रिमोट मोड था और इसे 2026 के मध्य में हटा दिया जा रहा है (अटलसियन के रोवो एमसीपी सर्वर ने इसे 30 जून 2026 को अप्रचलित कर दिया; 1 अप्रैल 2026 को केबुला) । स्टूडियो के लिए, प्रति पंक्ति एक JSON ऑब्जेक्ट पूरे तार प्रारूप है।

नोट्स सर्वर एक अच्छा आकार है क्योंकि यह सभी तीन सर्वर आदिमताओं का अभ्यास करता है। उपकरण उत्परिवर्तन करते हैं (`notes_create`) संसाधन डेटा को उजागर करते हैं (`notes://{id}`) जहाज टेम्पलेट्स को सूचित करता है (`review_note`) इस पाठ का आकार किसी भी क्षेत्र में सामान्य है।

## अवधारणा

### डिस्पैच लूप

```
loop:
  line = stdin.readline()
  msg = json.loads(line)
  if has id:
    handle request -> write response
  else:
    handle notification -> no response
```

तीन नियम:

- किसी भी चीज़ को stdout पर प्रिंट न करें जो JSON-RPC लिफाफे नहीं है। डिबग लॉग stderr पर जाते हैं।
- प्रत्येक अनुरोध को एक ही प्रतिक्रिया के साथ मेल करना चाहिए `id`. .
- सूचनाओं का उत्तर नहीं दिया जाना चाहिए।

### कार्यान्वयन`initialize`

```python
def initialize(params):
    return {
        "protocolVersion": "2025-11-25",
        "capabilities": {
            "tools": {"listChanged": True},
            "resources": {"listChanged": True, "subscribe": False},
            "prompts": {"listChanged": False},
        },
        "serverInfo": {"name": "notes", "version": "1.0.0"},
    }
```

केवल वही घोषित करें जो आप समर्थन करते हैं। ग्राहक गेट सुविधाओं के लिए सेट क्षमता पर निर्भर करता है।

### कार्यान्वयन`tools/list`और `tools/call`

`tools/list`रिटर्न `{tools: [...]}`प्रत्येक प्रविष्टि के साथ `name`,`description`,`inputSchema`. .`tools/call`लेता है`{name, arguments}`और रिटर्न `{content: [blocks], isError: bool}`. .

सामग्री ब्लॉकों को टाइप किया जाता है. सबसे आमः

```json
{"type": "text", "text": "Found 2 notes"}
{"type": "resource", "resource": {"uri": "notes://14", "text": "..."}}
{"type": "image", "data": "<base64>", "mimeType": "image/png"}
```

उपकरण त्रुटियां दो रूपों में आती हैं। प्रोटोकॉल स्तर की त्रुटियां (अज्ञात विधि, खराब पैरामीटर) JSON-RPC त्रुटियां हैं। उपकरण स्तर की त्रुटियां (मान्य कॉल लेकिन उपकरण विफल) को वापस किया जाता है।`{content: [...], isError: true}`. . जो मॉडल को अपनी विफलता को संदर्भ में देखने देता है.

### कार्यान्वयन संसाधन

संसाधन केवल-पढ़ने के लिए डिज़ाइन किए गए हैं। `resources/list`एक घोषणापत्र लौटाता है; `resources/read`सामग्री वापस करता है. यूआरआई हो सकता है `file://...`,`http://...`, या एक कस्टम योजना जैसे `notes://`. .

जब आप डेटा को एक उपकरण के बजाय संसाधन के रूप में प्रकट करते हैंः

- मॉडल इसे "कॉल" नहीं करता है; ग्राहक उपयोगकर्ता के अनुरोध पर इसे संदर्भ में इंजेक्ट कर सकता है।
- सदस्यताएँ सर्वर को अपडेट करने देती हैं जब संसाधन बदलता है (चरण 13 · 10) ।
- चरण 13 · 14 यह विस्तारित करता है `ui://`परस्पर संसाधनों के लिए।

### कार्यान्वयन निर्देश

प्रॉम्प्ट नामित तर्क वाले टेम्पलेट हैं। होस्ट उन्हें स्लैश-कमांड के रूप में प्रदर्शित करता है।`review_note`शीघ्रता में एक समय लग सकता है `note_id`तर्क और एक बहु-संदेश प्रम्प्ट टेम्पलेट उत्पन्न करें जो क्लाइंट अपने मॉडल को फ़ीड करता है।

### स्टूडियो परिवहन की बारीकियों

- न्यूलाइन-सीमित JSON. कोई लंबाई-पूर्वनिर्धारित फ्रेमिंग नहीं.
- बफर न करें।`sys.stdout.flush()`हर लेख के बाद।
- ग्राहक जीवनकाल को नियंत्रित करता है जब stdin बंद हो जाता है, साफ बाहर निकलें।
- SIGPIPE को चुपचाप न संभालें; लॉग और आउट करें।

### संकेतक

प्रत्येक उपकरण ले जा सकता है `annotations`सुरक्षा गुणों का वर्णन करने वाले:

- `readOnlyHint: true` शुद्ध पढ़ना, पुनः प्रयास करने के लिए सुरक्षित।
- `destructiveHint: true` अपरिवर्तनीय दुष्प्रभाव; ग्राहक को पुष्टि करनी चाहिए।
- `idempotentHint: true` एक ही इनपुट से एक ही आउटपुट उत्पन्न होता है।
- `openWorldHint: true` बाहरी प्रणालियों के साथ बातचीत करता है।

ग्राहक इनका उपयोग यूएक्स (पुष्टि संवाद, स्थिति संकेतकों) और रूटिंग (चरण 13 · 17) तय करने के लिए करता है।

### स्नातक का मार्ग

stdlib सर्वर में `code/main.py`फास्टएमसीपी (पाइटन) उसी तर्क को सजावट शैली में ढहता हैः

```python
from fastmcp import FastMCP
app = FastMCP("notes")

@app.tool()
def notes_search(query: str, limit: int = 10) -> list[dict]:
    ...
```

टाइपस्क्रिप्ट एसडीके का एक समकक्ष आकार है। स्नातक पथ तैयार होने पर ड्रॉप-इन है; अवधारणाएं (सक्षमताएं, डिस्पैच, सामग्री ब्लॉक) समान हैं।

```figure
t3-dispatch-loop
```

## इसका प्रयोग करें

`code/main.py`यह केवल स्टूडियो पर एक पूर्ण नोट्स MCP सर्वर है, stdlib. यह संभालता है `initialize`,`tools/list`,`tools/call`तीन उपकरण के लिए (`notes_list`,`notes_search`,`notes_create`), `resources/list`और `resources/read`प्रत्येक नोट के लिए, और `review_note`आप इसे JSON-RPC संदेश पाइपिंग द्वारा चला सकते हैंः

```
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python main.py
```

क्या देखना हैः

- डिस्पेंचर एक है `dict[str, Callable]`विधि नाम द्वारा कुंजीकृत।
- प्रत्येक उपकरण निष्पादक सामग्री ब्लॉक की सूची देता है, न कि एक नग्न स्ट्रिंग।
- `isError: true`जब निष्पादक उठता है तो सेट किया जाता है।

## इसे भेजें

यह सबक हमें फल देता है`outputs/skill-mcp-server-scaffolder.md`. एक डोमेन (नोट, टिकट, फाइल, डेटाबेस) को देखते हुए, कौशल एक एमसीपी सर्वर को सही उपकरण / संसाधन / प्रमाणीकरण विभाजन और एसडीके स्नातक पथ के साथ खड़ा करता है।

## व्यायाम

1. दौड़ें`code/main.py`और इसे हाथ से निर्मित JSON-RPC संदेशों के साथ ड्राइव करें। अभ्यास `notes_create`, तो `resources/read`नए नोट को प्राप्त करने के लिए.

2. एक जोड़ें `notes_delete` के साथ उपकरण`annotations: {destructiveHint: true}`. सत्यापित करें क्लाइंट एक पुष्टि संवाद के साथ दिखाई देगा (इसके लिए एक वास्तविक होस्ट की आवश्यकता है; क्लाउड डेस्कटॉप काम करता है).

3. कार्यान्वयन`resources/subscribe`तो सर्वर धक्का देता है `notifications/resources/updated`जब भी एक नोट को संशोधित किया जाता है. एक रखरखाव कार्य जोड़ें.

4. सर्वर को फास्टएमसीपी पर पोर्ट करें। पायथन फ़ाइल को 80 लाइनों से कम तक छोटा करना चाहिए। तार व्यवहार समान होना चाहिए; उसी JSON-RPC परीक्षण हर्नल के साथ सत्यापित करें।

5. विवरण पढ़ें `server/tools`अनुभाग और इस पाठ के सर्वर में लागू नहीं किए गए उपकरण परिभाषा के एक क्षेत्र की पहचान करें। (संकेतः कई हैं; एक चुनें और इसे जोड़ें) ।

## प्रमुख शर्तें

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| MCP server | "The thing that exposes tools" | Process that speaks MCP JSON-RPC over stdio or HTTP |
| stdio transport | "Child process model" | Server is spawned by client; communicates via stdin/stdout |
| Dispatcher | "Method router" | Map of JSON-RPC method name to handler function |
| Content block | "Tool result chunk" | Typed element in the `content` array of a tool response |
| `isError` | "Tool-level failure" | Signals the tool failed; distinguishes from JSON-RPC error |
| Annotations | "Safety hints" | readOnly / destructive / idempotent / openWorld flags |
| FastMCP | "Python SDK" | Decorator-based higher-level framework on top of the MCP protocol |
| Resource URI | "Addressable data" | `file://`, `db://`, or custom scheme identifying a resource |
| Prompt template | "Slash-command brief" | Server-supplied template with argument slots for host UIs |
| Capability declaration | "Feature toggle" | Per-primitive flags declared in `initialize` |

## आगे पढ़ना

- [Model Context Protocol — Python SDK](https://github.com/modelcontextprotocol/python-sdk) संदर्भ पायथन कार्यान्वयन
- [Model Context Protocol — TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) समानांतर टीएस कार्यान्वयन
- [FastMCP — server framework](https://gofastmcp.com/) एमसीपी सर्वर के लिए डेकोरेटर शैली पायथन एपीआई
- [MCP — Quickstart server guide](https://modelcontextprotocol.io/quickstart/server) किसी भी SDK का उपयोग करके अंत-से-अंत ट्यूटोरियल
- [MCP — Server tools spec](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) उपकरण/* संदेशों के लिए पूर्ण संदर्भ
