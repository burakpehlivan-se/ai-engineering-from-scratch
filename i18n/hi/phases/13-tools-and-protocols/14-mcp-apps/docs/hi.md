# MCP Apps  इंटरैक्टिव UI संसाधनों के माध्यम से `ui://`

> केवल पाठ उपकरण आउटपुट एजेंटों को दिखा सकते हैं क्या कैप करता है। एमसीपी ऐप्स (एसईपी -1724, आधिकारिक 26 जनवरी 2026) एक उपकरण वापस करने के लिए अनुमति देते हैं सैंडबॉक्स इंटरैक्टिव एचटीएमएल क्लाउड डेस्कटॉप, चैटजीपीटी, कर्सर, हंस, और वीएस कोड में इनलाइन प्रस्तुत किया गया। डैशबोर्ड, फॉर्म, नक्शे, 3 डी दृश्य, सभी एक विस्तार के माध्यम से। यह सबक एक एक्सटेंशन के माध्यम से चलता है।`ui://`संसाधन योजना, `text/html;profile=mcp-app`MIME, iframe-sandbox postMessage प्रोटोकॉल, और सुरक्षा सतह जो सर्वर को HTML रेंडर करने के साथ आती है।

**Type:** Build
**Languages:** Python (stdlib, UI resource emitter), HTML (sample app)
**Prerequisites:** Phase 13 · 07 (MCP server), Phase 13 · 10 (resources)
**Time:** ~75 minutes

## सीखने के लक्ष्य

- एक वापस `ui://`एक उपकरण कॉल से संसाधन और सही MIME और मेटाडेटा सेट करें।
- किसी उपकरण के संबंधित UI को  के साथ घोषित करें`_meta.ui.resourceUri`,`_meta.ui.csp`और `_meta.ui.permissions`. .
- यूआई-टू-होस्ट संचार के लिए iframe sandbox postMessage JSON-RPC को लागू करें।
- सीएसपी और अनुमति नीति डिफ़ॉल्ट को लागू करें जो UI-उत्पत्ति वाले हमलों से बचाव करते हैं।

## समस्या

2025 का युग`visualize_timeline`उपकरण "यहां 14 नोट हैं जो समयक्रम में व्यवस्थित हैंः ..." लौट सकते हैं। यह एक पैराग्राफ है। उपयोगकर्ता वास्तव में इंटरैक्टिव टाइमलाइन चाहते हैं। एमसीपी ऐप्स से पहले, विकल्प थेः क्लाइंट-विशिष्ट विजेट एपीआई (क्लाउड आर्टिफैक्ट्स, ओपनएआई कस्टम जीपीटी एचटीएमएल), या कोई यूआई नहीं।

एमसीपी एप्लिकेशन (एसईपी-1724, 26 जनवरी, 2026 को भेजा गया) अनुबंध को मानकीकृत करते हैं। एक उपकरण परिणाम में एक `resource`जिसका यूआरआई है `ui://...`और किसकी MIME है `text/html;profile=mcp-app`. होस्ट इसे एक सैंडबॉक्स आईफ़्रेम में सीमित सीएसपी के साथ प्रस्तुत करता है और जब तक स्पष्ट रूप से अनुमत नहीं होता है तब तक नेटवर्क एक्सेस नहीं होता है। आईफ़्रेम के अंदर यूआई एक छोटे से पोस्टमेसेज जेएसओएन-आरपीसी बोली के माध्यम से मेसेज होस्ट को भेजता है।

प्रत्येक संगत क्लाइंट (क्लाउड डेस्कटॉप, चैटजीपीटी, हंस, वीएस कोड) एक ही प्रदर्शन करता है `ui://`एक सर्वर, एक HTML बंडल, सार्वभौमिक UI.

## अवधारणा

### `ui://`संसाधन योजना

एक उपकरण वापस करता हैः

```json
{
  "content": [
    {"type": "text", "text": "Here is your notes timeline:"},
    {"type": "ui_resource", "uri": "ui://notes/timeline"}
  ],
  "_meta": {
    "ui": {
      "resourceUri": "ui://notes/timeline",
      "csp": {
        "defaultSrc": "'self'",
        "scriptSrc": "'self' 'unsafe-inline'",
        "connectSrc": "'self'"
      },
      "permissions": []
    }
  }
}
```

तब मेजबान बुलाता है`resources/read`पर `ui://notes/timeline`यूआरआई और वापस आता हैः

```json
{
  "contents": [{
    "uri": "ui://notes/timeline",
    "mimeType": "text/html;profile=mcp-app",
    "text": "<!doctype html>..."
  }]
}
```

### आइफ़्रेम रेत बॉक्स

मेजबान एक सैंडबॉक्स के अंदर HTML प्रस्तुत करता है `<iframe>`साथः

- `sandbox="allow-scripts allow-same-origin"`(या प्रति सर्वर घोषणा के लिए सख्त)
- सर्वर द्वारा घोषित सीएसपी प्रतिक्रिया हेडर के माध्यम से लागू किया गया।
- कोई कुकीज़, कोई स्थानीय भंडारण मेजबान के मूल से नहीं।
- नेटवर्क तक पहुंच सीमित है `connectSrc`सीएसपी में।

### पोस्टमेसेज प्रोटोकॉल

iframe मेजबान के साथ संचार करता है `window.postMessage`. एक छोटी सी JSON-RPC 2.0 बोलीः

हमेशा पिन`targetOrigin`समकक्ष की सटीक उत्पत्ति के लिए, और प्राप्त पक्ष पर मान्य `event.origin`किसी भी उपयोगी लोड को संसाधित करने से पहले एक अनुमतिदाता के खिलाफ। कभी भी उपयोग न करें`"*"`इस चैनल के दोनों तरफ  शरीर उपकरण कॉल और संसाधन रीड करता है।

```js
// iframe to host  (pin to host origin)
window.parent.postMessage({
  jsonrpc: "2.0",
  id: 1,
  method: "host.callTool",
  params: { name: "notes_update", arguments: { id: "note-14", title: "..." } }
}, "https://host.example.com");

// host to iframe  (pin to iframe origin)
iframe.contentWindow.postMessage({
  jsonrpc: "2.0",
  id: 1,
  result: { content: [...] }
}, "https://iframe.example.com");

// receiver on both sides
window.addEventListener("message", (event) => {
  if (event.origin !== "https://expected-peer.example.com") return;
  // safe to process event.data
});
```

उपलब्ध होस्ट-साइड विधियों UI कॉल कर सकते हैंः

- `host.callTool(name, arguments)` सर्वर टूल को कॉल करता है।
- `host.readResource(uri)` एक MCP संसाधन पढ़ता है।
- `host.getPrompt(name, arguments)` एक शीघ्र टेम्पलेट लाता है।
- `host.close()` UI को खारिज करता है।

हर कॉल अभी भी MCP प्रोटोकॉल के माध्यम से जाता है और सर्वर की अनुमति विरासत में मिलता है।

### अनुमति

`_meta.ui.permissions`सूची अतिरिक्त क्षमताओं की मांग करता हैः

- `camera` उपयोगकर्ता के कैमरे तक पहुँच (स्कैन-ए-डॉक्यूमेंट यूआई के लिए उपयोग किया जाता है) ।
- `microphone` आवाज इनपुट।
- `geolocation` स्थान।
- `network:*` नेटवर्क तक पहुंच  से अधिक`connectSrc`केवल अनुमति देता है।

प्रत्येक अनुमति उपयोगकर्ता द्वारा UI प्रस्तुत करने से पहले देखे जाने वाले एक संकेत है।

### सुरक्षा जोखिम

एक iframe में HTML अभी भी HTML है. नया हमले सतहः

- **Prompt-injection via UI.**एक दुर्भावनापूर्ण सर्वर UI पाठ दिखा सकता है जो सिस्टम संदेश की तरह दिखता है और उपयोगकर्ता को धोखा देता है। होस्ट रेंडरिंग को सर्वर UI को होस्ट UI से स्पष्ट रूप से अलग करना चाहिए।
- **Exfiltration via `connectSrc`.**यदि सीएसपी अनुमति देता है `connect-src: *`डिफ़ॉल्ट रूप से सख्त होना चाहिए.
- **Clickjacking.**यूआई होस्ट क्रोम को ओवरलैप करता है। होस्टों को z-index हेरफेर को रोकने और अस्पष्टता नियमों को लागू करना चाहिए।
- **Steal focus.**यूआई कीबोर्ड फोकस लेता है और अगले संदेश को कैप्चर करता है. मेजबानों को इंटरसेप्ट करना चाहिए.

चरण 13 · 15 एमसीपी सुरक्षा के हिस्से के रूप में इन पर गहराई से चर्चा करता है; यह पाठ इनकी शुरूआत करता है।

### `ui/initialize`हाथ मिलाकर

iframe लोड होने के बाद, यह भेजता है `ui/initialize`पोस्ट संदेश परः

```json
{"jsonrpc": "2.0", "id": 0, "method": "ui/initialize",
 "params": {"theme": "dark", "locale": "en-US", "sessionId": "..."}}
```

होस्ट क्षमताओं और सत्र टोकन के साथ प्रतिक्रिया करता है। UI प्रत्येक बाद के होस्ट कॉल पर सत्र टोकन का उपयोग करता है।

### AppRenderer / AppFrame SDK आदिम

विस्तारित अनुप्रयोगों एसडीके दो सुविधा आदिम उजागर करता हैः

- `AppRenderer`(सर्वर पक्ष)  एक प्रतिक्रिया / दृश्य / ठोस घटक को लपेटता है और एक उत्सर्जन करता है `ui://`सही MIME और मेटाडेटा के साथ संसाधन।
- `AppFrame`(ग्राहक पक्ष)  संसाधन प्राप्त करता है, iframe माउंट करता है, और मेल मेल के माध्यम से.

आप इन का उपयोग कर सकते हैं या हाथ से HTML और JSON-RPC रोल कर सकते हैं.

### पारिस्थितिकी तंत्र की स्थिति

एमसीपी एप्लिकेशन 26 जनवरी 2026 को शिप किया गया। अप्रैल 2026 तक ग्राहक सहायताः

- **Claude Desktop.**जनवरी 2026 से पूर्ण समर्थन।
- **ChatGPT.**एप्लिकेशन एसडीके (समान अंतर्निहित एमसीपी एप्लिकेशन प्रोटोकॉल) के माध्यम से पूर्ण समर्थन।
- **Cursor.**बीटा; सेटिंग्स के माध्यम से सक्षम करें.
- **VS Code.**केवल इंसाइडर निर्माण करता है।
- **Goose.**पूर्ण समर्थन।
- **Zed, Windsurf.**रोडमैप किया गया।

उत्पादन में सर्वरः डैशबोर्ड, मानचित्र दृश्य, डेटा तालिका, चार्ट बिल्डर, सैंडबॉक्स आईडीई पूर्वावलोकन।

```figure
t3-ui-sandbox
```

## इसका प्रयोग करें

`code/main.py`एक  के साथ नोट्स सर्वर का विस्तार करता है`visualize_timeline`एक `ui://notes/timeline`संसाधन, और एक संभालकर्ता के लिए `resources/read`उस यूआरआई पर जो एक एसवीजी टाइमलाइन के साथ एक छोटा लेकिन पूरा एचटीएमएल बंडल लौटाता है। एचटीएमएल stdlib-templated है  कोई बिल्ड सिस्टम नहीं है। पोस्टमेसेज को जेएस टिप्पणियों में स्केच किया गया है क्योंकि stdlib ब्राउज़र नहीं चला सकता है।

क्या देखना हैः

- `_meta.ui`उपकरण प्रतिक्रिया संसाधनUri, सीएसपी, अनुमति है।
- HTML नेटवर्क एक्सेस के बिना प्रस्तुत करता है; सभी डेटा इनलाइन हैं।
- जेएस कॉल `host.callTool`द्वारा `window.parent.postMessage`(लेखित लेकिन इस स्टडीलिब डेमो में निष्क्रिय) ।

## इसे भेजें

यह सबक हमें फल देता है`outputs/skill-mcp-apps-spec.md`. एक उपकरण को देखते हुए जो एक इंटरैक्टिव UI से लाभान्वित होगा, कौशल पूरे MCP Apps अनुबंध का उत्पादन करता हैः `ui://`यूआरआई, सीएसपी, अनुमति, पोस्टमेसेज प्रवेश बिंदुओं, और सुरक्षा चेकलिस्ट।

## व्यायाम

1. दौड़ें`code/main.py`और बाहर भेजा गया HTML की जांच. सीधे एक ब्राउज़र में HTML खोलें; SVG रेंडर की पुष्टि. फिर पोस्ट संदेश अनुबंध की स्केच UI कॉल करने के लिए उपयोग करेगा `host.callTool("notes_update", ...)`. .

2. सीएसपी को कसेंः हटाएं `'unsafe-inline'`HTML पीढ़ी कोड में क्या बदलाव हैं?

3. दूसरा UI संसाधन जोड़ें `ui://notes/editor`एक नोट को संपादित करने के लिए एक फॉर्म के साथ जगह में। जब उपयोगकर्ता प्रस्तुत करता है, iframe कॉल करता है `host.callTool("notes_update", ...)`. .

4. यूआई के हमले की सतह का ऑडिट करें. एक दुर्भावनापूर्ण सर्वर सामग्री को कहां इंजेक्ट कर सकता है? iframe sandbox क्या से बचाता है और क्या नहीं करता है?

5. SEP-1724 विनिर्देश पढ़ें और MCP Apps SDK में एक क्षमता की पहचान करें जिसका उपयोग यह खिलौना कार्यान्वयन नहीं करता है।

## प्रमुख शर्तें

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| MCP Apps | "Interactive UI resources" | SEP-1724 extension shipped 2026-01-26 |
| `ui://` | "App URI scheme" | Resource scheme for UI bundles |
| `text/html;profile=mcp-app` | "The MIME" | Content-type for MCP App HTML |
| Iframe sandbox | "Render container" | Browser sandboxing of the UI with CSP and permissions |
| postMessage JSON-RPC | "UI-to-host wire" | Tiny JSON-RPC-over-postMessage dialect for host calls |
| `_meta.ui` | "Tool-UI binding" | Metadata linking a tool result to a UI resource |
| CSP | "Content-Security-Policy" | Declares allowed sources for scripts, network, styles |
| AppRenderer | "Server SDK primitive" | Converts a framework component into a `ui://` resource |
| AppFrame | "Client SDK primitive" | Iframe mount helper that mediates postMessage |
| `ui/initialize` | "Handshake" | First postMessage from UI to host |

## आगे पढ़ना

- [MCP ext-apps — GitHub](https://github.com/modelcontextprotocol/ext-apps) संदर्भ कार्यान्वयन और SDK
- [MCP Apps specification 2026-01-26](https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx) औपचारिक विनिर्देश दस्तावेज
- [MCP — Apps extension overview](https://modelcontextprotocol.io/extensions/apps/overview) उच्च स्तरीय दस्तावेज
- [MCP blog — MCP Apps launch](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/) जनवरी 2026 लॉन्च की तारीख
- [MCP Apps API reference](https://apps.extensions.modelcontextprotocol.io/api/) JSDoc शैली के SDK संदर्भ
