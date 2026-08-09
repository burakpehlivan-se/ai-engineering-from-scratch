# MCP संसाधन और संकेत  उपकरण से परे संदर्भ जोखिम

> उपकरण MCP का 90 प्रतिशत ध्यान प्राप्त करते हैं। अन्य दो सर्वर आदिम विभिन्न समस्याओं को हल करते हैं। संसाधन पढ़ने के लिए डेटा को उजागर करते हैं; प्रमाणीकरण स्लैश-कमांड के रूप में पुनः प्रयोज्य टेम्पलेट को उजागर करते हैं। कई सर्वरों को उपकरणों में पढ़ने के बजाय संसाधनों का उपयोग करना चाहिए, और क्लाइंट प्रमाणीकरण में हार्ड-कोडिंग वर्कफ़्लो के बजाय प्रमाणीकरण का उपयोग करना चाहिए। इस पाठ में निर्णय नियम का नाम दिया गया है और प्रमाणीकरण का मार्ग प्रशस्त किया गया है।`resources/*`और `prompts/*`संदेश।

**Type:** Build
**Languages:** Python (stdlib, resource + prompt handler)
**Prerequisites:** Phase 13 · 07 (MCP server)
**Time:** ~45 minutes

## सीखने के लक्ष्य

- किसी क्षमता को किसी दिए गए डोमेन के लिए एक उपकरण, संसाधन या प्रॉम्प्ट के रूप में उजागर करने के बीच निर्णय लें।
- कार्यान्वयन`resources/list`,`resources/read`,`resources/subscribe`और संभाल `notifications/resources/updated`. .
- कार्यान्वयन`prompts/list`और `prompts/get`तर्क टेम्पलेट्स के साथ।
- जब मेजबान स्लैश-कमांड बनाम ऑटो-इंजेक्शन संदर्भ के रूप में संकेतों को पहचानता है।

## समस्या

नोट्स ऐप के लिए एक भोले एमसीपी सर्वर सब कुछ उपकरण के रूप में उजागर करता हैः `notes_read`,`notes_list`,`notes_search`. यह मॉडल-चालित उपकरण कॉल में डेटा तक पहुँच के हर एक को लपेटता है. परिणामः

- मॉडल को तय करना होगा कि क्या वह फोन करेगा `notes_read`संदर्भ से लाभान्वित हो सकता है कि हर क्वेरी के लिए.
- केवल-पढ़ने वाली सामग्री को होस्ट के साइड पैनल में सदस्यता नहीं दी जा सकती है या स्ट्रीम नहीं किया जा सकता है।
- क्लाइंट यूआई (क्लाउड डेस्कटॉप के संसाधन संलग्नक पैनल, पाठ्यक्रम के "फ़ाइल शामिल करें" पिकर) डेटा को सतह पर नहीं ला सकते हैं।

दाएं विभाजनः संसाधन के रूप में डेटा को उजागर करें, उपकरण के रूप में उत्परिवर्तनशील या कंप्यूटेड कार्यों को उजागर करें, प्रमाणीकरण के रूप में पुनः प्रयोज्य बहु-चरण कार्यप्रवाहों को उजागर करें। प्रत्येक आदिम में अपनी यूएक्स उपलब्धता और अपना उपयोग पैटर्न है।

## अवधारणा

### उपकरण बनाम संसाधन बनाम संकेत  निर्णय नियम

| Capability | Primitive |
|------------|-----------|
| User wants to search, filter, or transform data | tool |
| User wants the host to include this data as context | resource |
| User wants a templated workflow they can re-run | prompt |

गाइडलाइनः यदि मॉडल को प्रत्येक संबंधित क्वेरी पर कॉल करने से लाभ होगा, तो यह एक उपकरण है। यदि उपयोगकर्ता इसे बातचीत में संलग्न करने से लाभान्वित होगा, तो यह एक संसाधन है। यदि एक संपूर्ण बहु-चरण कार्यप्रवाह इकाई है जिसे उपयोगकर्ता पुनः उपयोग करना चाहता है, तो यह एक प्रॉम्प्ट है।

### संसाधन

`resources/list`रिटर्न `{resources: [{uri, name, mimeType, description?}]}`. .`resources/read`लेता है`{uri}`और रिटर्न `{contents: [{uri, mimeType, text | blob}]}`. .

यूआरआई कुछ भी हो सकता है जिसे संबोधित किया जा सकता हैः

- `file:///Users/alice/notes/mcp.md`
- `postgres://my-db/query/SELECT ...`
- `notes://note-14`(आयात व्यवस्था)
- `memory://session-2026-04-22/recent`(सर्वर विशिष्ट)

`contents[]`पाठ और द्विआधारी दोनों का समर्थन करता है. द्विआधारी उपयोग `blob`एक आधार64-संकेतन स्ट्रिंग के रूप में प्लस एक `mimeType`. .

### संसाधनों की सदस्यता

घोषणा `{resources: {subscribe: true}}`क्षमताओं में. ग्राहक कॉल`resources/subscribe {uri}`. सर्वर भेजता है `notifications/resources/updated {uri}`जब संसाधन बदलता है. ग्राहक फिर से पढ़ता है.

उपयोग के मामलेः एक नोट सर्वर जिसका संसाधन डिस्क पर फ़ाइलें हैं; एक फ़ाइल वॉचर अपडेट सूचनाओं को ट्रिगर करता है; क्लाउड डेस्कटॉप होस्ट के बाहर संपादित होने पर फ़ाइल को संदर्भ में वापस खींचता है।

### संसाधन टेम्पलेट्स (2025-11-25 जोड़ें)

`resourceTemplates`आप एक पैरामीटर URI पैटर्न को उजागर करने के लिए अनुमति देंः `notes://{id}`के साथ`id`ग्राहक संसाधन चयनकर्ता में स्वतः आईडी भर सकते हैं।

### संकेत

`prompts/list`रिटर्न `{prompts: [{name, description, arguments?}]}`. .`prompts/get`लेता है`{name, arguments}`और रिटर्न `{description, messages: [{role, content}]}`. .

एक प्रॉम्प्ट एक टेम्पलेट है जो मेजबान द्वारा अपने मॉडल को फ़ीड किए गए संदेशों की सूची को भरता है। उदाहरण के लिए, एक `code_review`शीघ्रता एक लेता है `file_path`तर्क और तीन संदेश अनुक्रम लौटाता हैः एक प्रणाली संदेश, फ़ाइल निकाय के साथ एक उपयोगकर्ता संदेश, और तर्क टेम्पलेट के साथ एक सहायक किकऑफ।

### मेजबान और सूचनाएँ

क्लाउड डेस्कटॉप, वीएस कोड, और cursor चैट UI में स्लैश-कमांड के रूप में संकेतों को उजागर करते हैं। उपयोगकर्ता टाइप `/code_review`सर्वर का प्रॉम्प्ट "उपयोगकर्ता शॉर्टकट" और "पूरा प्रॉम्प्ट मॉडल को भेजा" के बीच अनुबंध है।

सभी क्लाइंट प्रॉम्प्ट का समर्थन नहीं करते हैं अभी तक  चेक क्षमता बातचीत। शीघ्र क्षमता के साथ एक सर्वर घोषित किया गया है लेकिन त्वरित समर्थन के बिना एक क्लाइंट बस स्लैश कमांड नहीं देखेंगे।

### "सूची बदल गई" सूचना

संसाधन और संकेत दोनों ही उत्सर्जित करते हैं `notifications/list_changed`एक नोट सर्वर जो सिर्फ आयात किया 20 नए नोट्स जारी करता है`notifications/resources/list_changed`; ग्राहक पुनः कॉल करता है `resources/list`जोड़ों को लेने के लिए।

### सामग्री प्रकार की सम्मेलन

पाठ के लिएः `mimeType: "text/plain"`,`text/markdown`,`application/json`. .
द्विआधारी के लिएः `image/png`,`application/pdf`, प्लस `blob`क्षेत्र।
एमसीपी एप्लिकेशन के लिए (पाठ 14): `text/html;profile=mcp-app`एक में `ui://`यूआरआई

### गतिशील संसाधन

संसाधन यूआरआई को स्थैतिक फ़ाइल से मेल नहीं लेना चाहिए। `notes://recent`प्रत्येक पाठ पर नवीनतम पांच नोटों को वापस कर सकते हैं।`db://query/users/active`सर्वर गतिशील रूप से सामग्री की गणना करने के लिए स्वतंत्र है।

नियमः यदि क्लाइंट यूआरआई द्वारा कैश कर सकता है, तो यूआरआई स्थिर होना चाहिए। यदि गणना एक शॉट है, तो यूआरआई में एक टाइमस्टैम्प या नॉनस शामिल होना चाहिए ताकि क्लाइंट कैश आउट न हो।

### सदस्यता बनाम मतदान

सदस्यता के लिए सक्षम ग्राहकों सर्वर के माध्यम से पुश प्राप्त `notifications/resources/updated`. पूर्व सदस्यता क्लाइंट या होस्ट जो इसे समर्थन नहीं करते हैं फिर से पढ़कर सर्वेक्षण करें. दोनों विनिर्देशों के अनुरूप हैं. सर्वर की क्षमता घोषणा क्लाइंट को बताती है कि यह किसका समर्थन करता है।

सदस्यता की लागतः सर्वर पर प्रति सत्र स्थिति (किसे किस पर सदस्यता ली गई है) । सदस्यता सेट को सीमित रखें; डिस्कनेक्ट क्लाइंट्स को समय निकालना चाहिए।

### सिस्टम संकेतों के विरुद्ध संकेत

MCP में प्रमांड सिस्टम प्रमांड नहीं हैं। होस्ट का सिस्टम प्रमांड (उसके अपने ऑपरेटिंग निर्देश) और MCP प्रमांड (उपयोगकर्ता द्वारा इल्यूटेड सर्वर-सप्लाई किए गए टेम्पलेट) एक साथ रहते हैं। एक अच्छी तरह से व्यवहार करने वाला क्लाइंट कभी भी सर्वर प्रमांड को अपने स्वयं के सिस्टम प्रमांड को ओवरराइड नहीं करने देता है; यह उन्हें परत करता है।

```figure
t3-primitive-sort
```

## इसका प्रयोग करें

`code/main.py`पाठ 07 से नोट सर्वर का विस्तार करता हैः

- प्रति नोट संसाधन (`notes://note-1`आदि) के साथ `resources/subscribe`समर्थन।
- ए `review_note`एक तीन संदेश टेम्पलेट के लिए प्रस्तुत करता है कि संकेत.
- एक फ़ाइल-वॉचर सिमुलेशन जो उत्सर्जन करता है `notifications/resources/updated`जब एक नोट में संशोधन किया जाता है।
- ए `notes://recent`गतिशील संसाधन जो हमेशा नवीनतम पांच नोटों को वापस करता है।

पूर्ण प्रवाह देखने के लिए डेमो चलाएं।

## इसे भेजें

यह सबक हमें फल देता है`outputs/skill-primitive-splitter.md`. प्रस्तावित एमसीपी सर्वर को देखते हुए, कौशल प्रत्येक क्षमता को तर्कसंगत रूप से उपकरण / संसाधन / प्रॉम्प्ट के रूप में वर्गीकृत करता है।

## व्यायाम

1. दौड़ें`code/main.py`. प्रारंभिक संसाधन सूची का निरीक्षण करें, फिर एक नोट संपादन को सक्रिय करें और `notifications/resources/updated`घटना आग.

2. एक जोड़ें `resources/list_changed`emitter: जब एक नया नोट बनाया जाता है, तो ग्राहक को फिर से खोजने के लिए अधिसूचना भेजें।

3. GitHub MCP सर्वर के लिए तीन प्रम्प्ट डिजाइन करेंः `summarize_pr`,`triage_issue`,`release_notes`प्रत्येक में तर्क योजनाएं होती हैं. शीघ्र निकाय को आगे संपादन किए बिना चलाया जा सकता है।

4. पाठ 07 सर्वर में मौजूद किसी उपकरण को ले लो और वर्गीकृत करें कि क्या उसे एक उपकरण बने रहना चाहिए या संसाधन प्लस उपकरण जोड़े में विभाजित किया जाना चाहिए। एक वाक्य में सही ठहराना।

5. विवरण पढ़ें `server/resources`और `server/prompts`अनुभागों में एक क्षेत्र की पहचान करें `resources/read`यह शायद ही कभी आबादी है लेकिन विनिर्देशों के साथ समर्थित है.`_meta`संसाधनों की सामग्री पर।

## प्रमुख शर्तें

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Resource | "Exposed data" | URI-addressable content the host can read |
| Resource URI | "Pointer to data" | Scheme-prefixed identifier (`file://`, `notes://`, etc.) |
| `resources/subscribe` | "Watch for changes" | Client-opt-in server-push updates for a specific URI |
| `notifications/resources/updated` | "Resource changed" | Signal to client that a subscribed resource has new content |
| Resource template | "Parameterized URI" | URI pattern with completion hints for the host picker |
| Prompt | "Slash-command template" | Named multi-message template with argument slots |
| Prompt arguments | "Template inputs" | Typed parameters the host collects before rendering |
| `prompts/get` | "Render template" | Server returns the filled-in message list |
| Content block | "Typed chunk" | `{type: text \| image \| resource \| ui_resource}` |
| Slash-command UX | "User shortcut" | Host surfaces prompts as commands starting with `/` |

## आगे पढ़ना

- [MCP — Concepts: Resources](https://modelcontextprotocol.io/docs/concepts/resources) संसाधन यूआरआई, सदस्यता और टेम्पलेट
- [MCP — Concepts: Prompts](https://modelcontextprotocol.io/docs/concepts/prompts) शीघ्र टेम्पलेट और स्लैश कमांड इंटीग्रेशन
- [MCP — Server resources spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/resources) पूर्ण `resources/*`संदेश संदर्भ
- [MCP — Server prompts spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts) पूर्ण `prompts/*`संदेश संदर्भ
- [MCP — Protocol info site: resources](https://modelcontextprotocol.info/docs/concepts/resources/) आधिकारिक दस्तावेजों पर समुदाय मार्गदर्शिका का विस्तार
