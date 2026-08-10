# تطبيقات MCP  الموارد التفاعلية من خلال UI `ui://`

> تُغطي أداة النتائج التي يتم عرضها من خلال الوكلاء فقط. تسمح تطبيقات MCP (SEP-1724, رسميًا 26 يناير 2026) بأداة بإرجاع HTML التفاعلي المعدن بالرمل المعدن في شكل إضافي في كود ستوب ، تشات جي بي تي ، كورسور ، غوز ، ووس كود. لوحات التحكم والأنماط والخرائط والمشاهد الثلاثية الأبعاد ، كلها من خلال امتداد واحد. هذه الدروس تمشي على `ui://`نظام الموارد،`text/html;profile=mcp-app`MIME، بروتوكول iframe-sandbox postMessage، والسطح الأمني الذي يأتي مع السماح لخادم عرض HTML.

**Type:** Build
**Languages:** Python (stdlib, UI resource emitter), HTML (sample app)
**Prerequisites:** Phase 13 · 07 (MCP server), Phase 13 · 10 (resources)
**Time:** ~75 minutes

## أهداف التعلم

- أعد`ui://`المورد من مكالمة أداة وتعيين MIME الصحيحة والبيانات المعدنية.
- إعلن واجهة تعريف المستخدم المرتبطة بالأداة مع `_meta.ui.resourceUri`،`_meta.ui.csp`و`_meta.ui.permissions`. . .
- تنفيذ صندوق الرمل iframe postMessage JSON-RPC للاتصال من واجهة الوصول إلى المضيف.
- تطبيق قواعد CSP والسياسة الإذن القابلة للتصدي للسياسة التي تحمي نفسها من الهجمات التي نشأت من UI.

## المشكلة

عصر 2025`visualize_timeline`يمكن أن يعيد أداة "هنا 14 ملاحظة منظمة بالتسلسل الزمني: ...". هذا فقرة. المستخدمون يريدون بالفعل جدول زمني تفاعلي. قبل تطبيقات MCP ، كانت الخيارات: API الويجيتات المحددة للعميل (ملفات كلود ، OpenAI Custom GPT HTML) ، أو لا UI على الإطلاق.

تطبيقات MCP (SEP-1724, تم شحنها في 26 يناير 2026) توفر معيار للعقد.`resource`التي هي URI `ui://...`و من هو`text/html;profile=mcp-app`. يقوم المضيف بتقديمها في إطار رمادي مع إطار CSP محدود ولا توفر إمكانية وصول إلى الشبكة إلا إذا تم منحها صراحة. يرسل واجهة الفور داخل إطار الإضافة رسائل إلى المضيف عبر لهجة JSON-RPC من خلال رسالة البريد الصغيرة.

كل عميل متوافق (كلود ديسكوب، تشات جي بي تي، غوز، VS Code) يعطي نفس `ui://`الموردة بنفس الطريقة. خادم واحد، حزمة HTML واحدة، واجهة المستخدم العالمية.

## المفهوم

### - نعم`ui://`نظام الموارد

أداة تعود:

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

المضيف ثم يُدعو`resources/read`على`ui://notes/timeline`و يُرجع:

```json
{
  "contents": [{
    "uri": "ui://notes/timeline",
    "mimeType": "text/html;profile=mcp-app",
    "text": "<!doctype html>..."
  }]
}
```

### صندوق الرمال

المضيف يعطي HTML داخل مربع رمال`<iframe>`مع:

- `sandbox="allow-scripts allow-same-origin"`(أو أكثر صرامة لكل إعلان خادم)
- يتم تطبيق CSP المعلن عن الخادم عبر عناوين الاستجابة.
- لا يوجد كعك ولا مخزن محلي من أصل المضيف
- الوصول إلى الشبكة محدودة`connectSrc`في مركز التجميع.

### البروتوكول بعد الرسالة

يتواصل iframe مع المضيف عبر `window.postMessage`. لغة صغيرة JSON-RPC 2.0:

دائماً أبرز`targetOrigin`إلى أصل النظير الدقيق، والجانب المقبل يصدق`event.origin`ضد المُسَمِح قبل معالجة أيّ حمولة مفيدة.`"*"`على أي جانب من هذه القناة  يحمل الجسم مكالمات الأدوات وقراءة الموارد.

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

أساليب الجانب المضيف المتاحة يمكن للمستخدم أن يدعو إليها:

- `host.callTool(name, arguments)`يستخدم أداة الخادم
- `host.readResource(uri)`يقرأ مصدر MCP.
- `host.getPrompt(name, arguments)` يحضر نموذج سريع.
- `host.close()`يرفض UI

كل مكالمة ما زالت تمر عبر بروتوكول MCP وتتراث بإذن الخادم.

### الإذن

- نعم`_meta.ui.permissions`طلبات القائمة إضافية:

- `camera` الوصول إلى كاميرا المستخدم (المستخدمة لمتصفحات البيانات المستخدمة في الوثائق).
- `microphone` إدخال الصوت
- `geolocation` موقع
- `network:*` وصول شبكة أوسع من `connectSrc`فقط يسمح.

كل إذن هو طلب يراه المستخدم قبل أن يعطي واجهة المستخدم.

### مخاطر الأمن

HTML في iframe ما زال HTML. سطح هجوم جديد:

- **Prompt-injection via UI.**يمكن للمستخدم أن يظهر واجهة تعريف الخادم الخبيثة نصاً يشبه رسالة النظام ويخدع المستخدم. يجب أن يتميز تعريف المضيف بشكل مرئي بين واجهة تعريف الخادم من واجهة تعريف المضيف.
- **Exfiltration via `connectSrc`.**إذا سمح لشركة التعاون المركزي`connect-src: *`يمكن للمستخدمين إرسال البيانات إلى أي مكان يجب أن تكون الإعدادات القاسية
- **Clickjacking.**تتداخل واجهة المستخدم مع الكروم المضيف. يجب على المضيفين منع التلاعب بنشر z وتطبيق قواعد الضموضة.
- **Steal focus.**يُستعمل واجهة المستخدم تركيز لوحة المفاتيح ويُلتقط الرسالة التالية. يجب على المضيفين إيقافها.

المرحلة 13 · 15 تغطي هذه بشكل متعمق كجزء من أمن MCP؛ هذا الدروس يقدمها.

### `ui/initialize`صلصة اليد

بعد تحميل الإطار، فإنه يرسل `ui/initialize`على البريد

```json
{"jsonrpc": "2.0", "id": 0, "method": "ui/initialize",
 "params": {"theme": "dark", "locale": "en-US", "sessionId": "..."}}
```

يستجيب المضيف مع القدرات و رمز جلسة. يستخدم واجهة البحث رمز جلسة في كل مكالمة مضيف لاحقة.

### أسباب أسبريندر / أسبفريم SDK

يظهر SDK التطبيقات الموسعة اثنين من أسباب الراحة:

- `AppRenderer`(جانب الخادم)  يلف جزء React / Vue / Solid ويطلق `ui://`الموارد مع MIME والبيانات المعدنية الصحيحة.
- `AppFrame`(جانب العميل)  يتلقى الموارد، يضم iframe، ويتوسط بعدMessage.

يمكنك استخدام هذه أو تحويل HTML و JSON-RPC يدويا.

### حالة النظام البيئي

أرسلت تطبيقات MCP في 26 يناير 2026. دعم العملاء اعتبارا من أبريل 2026:

- **Claude Desktop.**الدعم الكامل منذ يناير 2026.
- **ChatGPT.**الدعم الكامل عبر بروتوكول التطبيقات SDK (المسألة الأساسية نفسها MCP Apps).
- **Cursor.**التطبيق التجريبي؛ تمكين عبر الإعدادات.
- **VS Code.**إنسانسيدبني فقط
- **Goose.**دعم كامل
- **Zed, Windsurf.**خريطة الطريق

الخوادم في الإنتاج: لوحة التحكم، وتصور الخرائط، جداول البيانات، صانعي الرسوم البيانية، عرضات أجهزة إدارة التشغيل.

```figure
t3-ui-sandbox
```

## استخدمها

`code/main.py`يمتد خادم الملاحظات مع `visualize_timeline`الوسيلة التي تعيد `ui://notes/timeline`الموارد، بالإضافة إلى مدير للمعلومات`resources/read`على تلك الرسائل البيانية التي تعيد مجموعة HTML صغيرة ولكنها كاملة مع خط زمني SVG. HTML هي stdlib-نموذج  لا نظام بناء. يتم رسم postMessage في تعليقات JS لأن stdlib لا يمكن تشغيل متصفح.

ما الذي يجب أن ننظر إليه:

- `_meta.ui`على الرد على الأداة يحمل المواردUri، CSP، الإذن.
- HTML يعطي دون وصول إلى الشبكة؛ جميع البيانات مدرجة.
- مكالمات جي إس`host.callTool`عبر`window.parent.postMessage`(موثقة ولكن غير فعالة في هذا التجربة المثيرة).

## أرسله

هذا الدرس يُنتج`outputs/skill-mcp-apps-spec.md`. بالنظر إلى أداة ستستفيد من واجهة المستخدم التفاعلية ، فإن المهارة تنتج عقد MCP Apps الكامل: `ui://`أوريتشال، CSP، الإذن، نقاط دخول البريد، وقائمة تفتيش أمنية.

## التمارين

1. أركض`code/main.py`و تحقق من HTML المنبعث. افتح HTML مباشرة في متصفح؛ التحقق من SVG تمثيل. ثم رسم العقد بعد الرسالة التي ستستخدمها UI للاتصال `host.callTool("notes_update", ...)`. . .

2. ضيق الحاجز المركزي: إزالة`'unsafe-inline'`و استخدم سياسة النص غير القائمة على النص. ما هي التغييرات في رمز توليد HTML؟

3. إضافة مصدر UI ثاني `ui://notes/editor`مع نموذج لتحرير ملاحظة في مكانها. عندما يقوم المستخدم بإرسالها، يطلق الإطار الإلكتروني`host.callTool("notes_update", ...)`. . .

4. أودي على سطح الهجوم من واجهة المستخدم. أين يمكن لخادم ضار أن يُحقق محتوى؟ ما الذي يدافع عليه صندوق الرمل من iframe وما الذي لا يفعل؟

5. اقرأ مواصفات SEP-1724 وتحدد قدرة واحدة في SDK MCP Apps لا تستخدمها تنفيذ اللعبة.

## الشروط الرئيسية

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

## المزيد من القراءة

- [MCP ext-apps — GitHub](https://github.com/modelcontextprotocol/ext-apps) تنفيذ مرجعي و SDK
- [MCP Apps specification 2026-01-26](https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx) وثيقة تحديد رسمية
- [MCP — Apps extension overview](https://modelcontextprotocol.io/extensions/apps/overview) توثيق رفيع المستوى
- [MCP blog — MCP Apps launch](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/) يناير 2026 نقطة الإطلاق
- [MCP Apps API reference](https://apps.extensions.modelcontextprotocol.io/api/) إشارة SDK على النمط JSDoc
