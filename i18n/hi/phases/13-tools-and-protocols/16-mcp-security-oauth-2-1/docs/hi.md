# एमसीपी सुरक्षा II  OAuth 2.1, संसाधन संकेतकों, वृद्धिशील दायरे

> रिमोट MCP सर्वर को प्राधिकरण की आवश्यकता होती है, न कि केवल प्रमाणीकरण। 2025-11-25 विनिर्देश OAuth 2.1 + PKCE + संसाधन संकेतक (RFC 8707) + संरक्षित संसाधन मेटाडेटा (RFC 9728) के साथ संरेखित होता है। SEP-835 403 WWW-Authenticate पर step-up प्राधिकरण के साथ incremental scope consent जोड़ता है। यह पाठ step-up flow को एक राज्य मशीन के रूप में लागू करता है ताकि आप हर hop देख सकें।

**Type:** Build
**Languages:** Python (stdlib, OAuth state machine simulator)
**Prerequisites:** Phase 13 · 09 (transports), Phase 13 · 15 (security I)
**Time:** ~75 minutes

## सीखने के लक्ष्य

- संसाधन सर्वर को प्राधिकरण सर्वर जिम्मेदारियों से अलग करें।
- PKCE- संरक्षित OAuth 2.1 प्राधिकरण कोड प्रवाह पर जाएं।
- उपयोग करें`resource`(RFC 8707) और संरक्षित संसाधन मेटाडेटा (RFC 9728) भ्रमित-उपयोगियों के हमलों को रोकने के लिए।
- step-up authorization लागू करेंः सर्वर 403 का जवाब देता है WWW-Authenticate के साथ अधिक दायरा के लिए पूछता है; क्लाइंट उपयोगकर्ता सहमति और पुनः प्रयासों को फिर से पूछता है।

## समस्या

प्रारंभिक एमसीपी (पूर्व-2025) ने एड-होक एपीआई कुंजी या यहां तक कि कोई ऑथ के साथ रिमोट सर्वर भेजे। 2025-11-25 विनिर्देश एक पूर्ण ओएथ 2.1 प्रोफ़ाइल के साथ उस अंतर को बंद करता है।

वास्तविक दुनिया की तीन आवश्यकताएँ:

- **Ordinary remote servers.**उपयोगकर्ता एक रिमोट MCP सर्वर स्थापित करता है जो उनके Notion / GitHub / Gmail तक पहुँचता है। PKCE के साथ OAuth 2.1 सही आकार है।
- **Scope escalation.**एक नोट सर्वर प्रदान की गई`notes:read`बाद में आवश्यकता हो सकती है `notes:write`एक विशिष्ट कार्य के लिए। पूरे प्रवाह को फिर से करने के बजाय, step-up (SEP-835) अतिरिक्त दायरे के लिए कहता है।
- **Confused deputy prevention.**क्लाइंट सर्वर ए के लिए दर्शकों के लिए एक टोकन रखता है। सर्वर ए दुर्भावनापूर्ण है और सर्वर बी को टोकन प्रस्तुत करने की कोशिश करता है। संसाधन संकेतक (आरएफसी 8707) अपने इच्छित दर्शकों के लिए टोकन को पिन करें।

OAuth 2.1 नया नहीं है। नया MCP की प्रोफ़ाइल हैः विशिष्ट आवश्यक प्रवाह (केवल प्राधिकरण कोड + PKCE; कोई अप्रत्यक्ष, कोई डिफ़ॉल्ट रूप से ग्राहक क्रेडेंशियल नहीं), प्रत्येक टोकन अनुरोध पर संसाधन संकेतक अनिवार्य हैं, और संरक्षित संसाधन मेटाडेटा प्रकाशित किए गए हैं ताकि ग्राहक जानते हैं कि कहां जाना है।

## अवधारणा

### भूमिकाएँ

- **Client.**एमसीपी क्लाइंट (क्लाउड डेस्कटॉप, कर्सर, आदि) ।
- **Resource server.**एमसीपी सर्वर (नोट्स, गिटहब, पोस्टग्रेस, जो भी हो) ।
- **Authorization server.**समस्या टोकन. संसाधन सर्वर के समान सेवा या एक अलग आईडीपी (Auth0, Keycloak, Cognito) हो सकती है।

MCP के प्रोफ़ाइल में, संसाधन और प्राधिकरण सर्वर एक ही होस्ट हो सकते हैं लेकिन URL द्वारा अलग किया जाना चाहिए।

### प्राधिकरण कोड + PKCE

प्रवाहः

1. ग्राहक उत्पन्न करता है `code_verifier`(संदिग्ध) और `code_challenge`(SHA256) ।
2. ग्राहक उपयोगकर्ता को  पर पुनर्निर्देशित करता है`/authorize?response_type=code&client_id=...&redirect_uri=...&scope=notes:read&code_challenge=...&resource=https://notes.example.com`. .
3. उपयोगकर्ता सहमति देता है. प्राधिकरण सर्वर रीडायरेक्ट करता है `redirect_uri?code=...`. .
4. ग्राहक को पोस्ट करता है `/token?grant_type=authorization_code&code=...&code_verifier=...&resource=...`. .
5. प्राधिकरण सर्वर संग्रहीत चुनौती के खिलाफ सत्यापक के हैश को मान्य करता है और एक एक्सेस टोकन जारी करता है।
6. ग्राहक टोकन का उपयोग करता हैः `Authorization: Bearer ...`संसाधन सर्वर के लिए प्रत्येक अनुरोध पर।

PKCE प्राधिकरण कोड के इंटरसेप्शन हमलों को रोकता है। संसाधन संकेतकों टोकन को अन्य जगहों पर मान्य होने से रोकता है।

### संरक्षित संसाधनों के मेटाडेटा (RFC 9728)

संसाधन सर्वर एक `.well-known/oauth-protected-resource`दस्तावेजः

```json
{
  "resource": "https://notes.example.com",
  "authorization_servers": ["https://auth.example.com"],
  "scopes_supported": ["notes:read", "notes:write", "notes:delete"]
}
```

क्लाइंट संसाधन सर्वर से प्राधिकरण सर्वर का पता लगाता है। विन्यास को कम करता है  क्लाइंट को केवल संसाधन URL की आवश्यकता होती है।

### संसाधन संकेतकों (RFC 8707)

`resource`टोकन अनुरोध पिन में पैरामीटर टोकन के इच्छित दर्शक है. जारी टोकन में शामिल है `aud: "https://notes.example.com"`. एक और MCP सर्वर इस टोकन चेक प्राप्त .`aud`और उसे झुठलाता है

### दायरा मॉडल

स्कोप अंतरिक्ष से अलग स्ट्रिंग्स हैं। आम एमसीपी सम्मेलनः

- `notes:read`,`notes:write`,`notes:delete`
- `admin:*`प्रशासन क्षमताओं के लिए (छोटे उपयोग)
- `profile:read`पहचान के लिए

दायरा चयन न्यूनतम विशेषाधिकार होना चाहिएः अब आपको जो चाहिए वह मांगें, जब आपको अधिक चाहिए तो कदम उठाएं।

### वृद्धि प्राधिकरण (SEP-835)

उपयोगकर्ता अनुदान `notes:read`बाद में वे एजेंट से एक नोट हटाने के लिए कहते हैं. सर्वर जवाब देता हैः

```
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer error="insufficient_scope",
    scope="notes:delete", resource="https://notes.example.com"
```

ग्राहक insufficient_scope त्रुटि देखता है, उपयोगकर्ता को अतिरिक्त दायरे के लिए सहमति संवाद के साथ पूछता है, इसके लिए एक मिनी OAuth प्रवाह करता है, नए टोकन के साथ अनुरोध को पुनः प्रयास करता है।

### टोकन दर्शकों की सत्यापन

प्रत्येक अनुरोधः सर्वर जांच `token.aud == self.resource_url`. असंगत = 401. यह क्रॉस-सर्वर टोकन पुनः उपयोग को रोकता है.

### अल्पकालिक टोकन और रोटेशन

एक्सेस टोकन अल्पकालिक होना चाहिए (1 घंटे डिफ़ॉल्ट) । रिफ्रेश टोकन हर रिफ्रेश पर घूमते हैं। क्लाइंट पृष्ठभूमि में चुपचाप रिफ्रेश को संभालता है।

### कोई प्रतीकात्मक पास नहीं

नमूना लेने वाले सर्वर (चरण 13 · 11) को ग्राहक के टोकन को अन्य सेवाओं को पारित नहीं करना चाहिए। नमूना लेने का अनुरोध सीमा है।

### भ्रमित उप-रोधी

टोकन  से बंधता है`aud`. ग्राहक को बाध्य करता है`client_id`प्रत्येक अनुरोध दोनों के खिलाफ मान्य है। विनिर्देश स्पष्ट रूप से पुराने "पास-द-टोकन" पैटर्न को प्रतिबंधित करता है जो कि पूर्व-एमसीपी रिमोट टूल पारिस्थितिकी तंत्र में आम था।

### ग्राहक आईडी का पता लगाना

प्रत्येक MCP क्लाइंट एक निश्चित URL पर अपना मेटाडेटा प्रकाशित करता है। प्राधिकरण सर्वर रीडायरेक्ट यूआरआई और संपर्क जानकारी खोजने के लिए क्लाइंट के मेटाडेटा दस्तावेज़ को प्राप्त कर सकते हैं। यह मैनुअल क्लाइंट पंजीकरण को हटा देता है।

### गेटवे और ओएथ

चरण 13 · 17 दिखाता है कि एक उद्यम गेटवे OAuth को कैसे संभालता हैः गेटवे अपस्ट्रीम सर्वर के लिए क्रेडेंशियल रखता है, क्लाइंट के लिए टोकन गेटवे द्वारा जारी किए जाते हैं, और अपस्ट्रीम टोकन कभी भी गेटवे को नहीं छोड़ते हैं। यह ट्रस्ट मॉडल को फ्लिप करता है  उपयोगकर्ता गेटवे के साथ एक बार सत्यापित करते हैं; गेटवे N सर्वर प्राधिकरणों को संभालता है।

```figure
t3-scope-stepup
```

## इसका प्रयोग करें

`code/main.py`यह एक राज्य मशीन के रूप में पूर्ण OAuth 2.1 step-up प्रवाह का अनुकरण करता है। यह लागू करता हैः

- PKCE कोड-वेरिफायर/चैलेंज जनरेशन।
- संसाधन संकेतक के साथ प्राधिकरण कोड प्रवाह।
- संरक्षित संसाधन मेटाडेटा अंत बिंदु।
- दर्शकों की जांच के साथ टोकन सत्यापन.
- आगे बढ़ें `insufficient_scope`. .

इस पाठ में कोई HTTP सर्वर नहीं है; राज्य मशीन मेमोरी में चलती है ताकि आप हर कूद को ट्रैक कर सकें। चरण 13 · 17 के गेटवे पाठ इसे वास्तविक परिवहन के लिए तार करता है।

## इसे भेजें

यह सबक हमें फल देता है`outputs/skill-oauth-scope-planner.md`. उपकरण के साथ एक दूरस्थ MCP सर्वर को देखते हुए, कौशल दायरा सेट, नियमन नियमन और step-up नीति डिजाइन करता है।

## व्यायाम

1. दौड़ें`code/main.py`दो-स्कॉप अप स्ट्रेप-अप प्रवाह का पता लगाएं। ध्यान दें कि किस कूदने पर दोहराएं।

2. रिफ्रेश-टोकन रोटेशन जोड़ेंः प्रत्येक रिफ्रेश एक नया रिफ्रेश टोकन जारी करता है और पुराना अमान्य करता है। रोटेशन के बाद उपयोग किए जा रहे एक चुराए गए रिफ्रेश टोकन का अनुकरण करें और इसकी विफलता की पुष्टि करें।

3. stdlib http.server का उपयोग करके संरक्षित संसाधन मेटाडेटा एंडपॉइंट को वास्तविक HTTP प्रतिक्रिया के रूप में लागू करें। पाठ 09 से /mcp एंडपॉइंट को दर्पण करें।

4. GitHub MCP सर्वर के लिए एक दायरा पदानुक्रम डिजाइन करेंः रीपो पढ़ें, पीआर लिखें, पीआर को मंजूरी दें, पीआर को मिलाएं, व्यवस्थापक। प्रत्येक स्तर के बीच step-up का उपयोग करें।

5. आरएफसी 8707 और आरएफसी 9728 पढ़ें। 9728 में एक क्षेत्र की पहचान करें जो एमसीपी आरएफसी के उदाहरण से अलग तरीके से उपयोग करता है। (संकेतः यह संबंधित है `scopes_supported`.)

## प्रमुख शर्तें

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| OAuth 2.1 | "Modern OAuth" | Consolidated RFC that mandates PKCE and forbids implicit flow |
| PKCE | "Proof-of-possession" | Code verifier + challenge defeating authorization-code interception |
| Resource indicator | "Token audience" | RFC 8707 `resource` parameter pinning token to one server |
| Protected-resource metadata | "Discovery doc" | RFC 9728 `.well-known/oauth-protected-resource` |
| Step-up authorization | "Incremental consent" | SEP-835 flow for adding scopes on demand |
| `insufficient_scope` | "403 with WWW-Authenticate" | Server signal to re-consent for a larger scope |
| Confused deputy | "Token reuse across services" | Attack where a trusted holder forwards a token inappropriately |
| Short-lived token | "Access token TTL" | Bearer that expires quickly; refresh token renews |
| Scope hierarchy | "Least privilege stack" | Graduated scope set with step-up between levels |
| Client ID metadata | "Client discovery doc" | URL at which the client publishes its own OAuth metadata |

## आगे पढ़ना

- [MCP — Authorization spec](https://modelcontextprotocol.io/specification/draft/basic/authorization) कैनोनिक एमसीपी ओएथ प्रोफ़ाइल
- [den.dev — MCP November authorization spec](https://den.dev/blog/mcp-november-authorization-spec/) 2025-11-25 के परिवर्तनों का पारगमन
- [RFC 8707 — Resource indicators for OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8707) दर्शकों के लिए आरएफसी
- [RFC 9728 — OAuth 2.0 protected resource metadata](https://datatracker.ietf.org/doc/html/rfc9728) खोज-प्रमाण आरएफसी
- [Aembit — MCP OAuth 2.1, PKCE and the future of AI authorization](https://aembit.io/blog/mcp-oauth-2-1-pkce-and-the-future-of-ai-authorization/) व्यावहारिक कदम-अप प्रवाह-चलाव-दर-पार
