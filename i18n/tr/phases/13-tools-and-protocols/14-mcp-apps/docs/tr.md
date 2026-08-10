# MCP Uygulamaları  Interaktif UI Kaynakları üzerinden `ui://`

> Tekestli araç çıkışları, ajanların gösterebileceği şeyleri kapsar. MCP Apps (SEP-1724, resmi 26 Ocak 2026) bir araçın Claude Desktop, ChatGPT, Cursor, Goose ve VS Code'da çevrimiçi olarak gösterilen kum kutulu etkileşimli HTML'i geri göndermesine izin verir.`ui://`kaynak düzenlemesi,`text/html;profile=mcp-app`MIME, iframe-sandbox postMessage protokolü ve bir sunucu HTML'i göstermesine izin vermekle birlikte gelen güvenlik yüzeyi.

**Type:** Build
**Languages:** Python (stdlib, UI resource emitter), HTML (sample app)
**Prerequisites:** Phase 13 · 07 (MCP server), Phase 13 · 10 (resources)
**Time:** ~75 minutes

## Öğrenme Hedefleri

- Birini geri getir .`ui://`Bir araç çağrısından kaynak oluşturun ve doğru MIME ve metadata ayarlayın.
- Bir araçla ilişkili kullanıcı kullanımı kullanışlılığını belirtin `_meta.ui.resourceUri`- Evet .`_meta.ui.csp`ve`_meta.ui.permissions`- Evet .
- Uygulamacı kullanıcı aracından misafirhaneye iletişimi için iframe sandbox postMessage JSON-RPC uygulaması.
- UI'den kaynaklanan saldırılara karşı korunan CSP ve izin politikaları varsayımlarını uygulayın.

## Sorun

2025 yılı.`visualize_timeline`Bu bir paragrafdır. Kullanıcılar aslında etkileşimli zaman çizelgesini istiyor. MCP Apps'ten önce seçenekler: istemci özel widget API'leri (Claude artefakları, OpenAI Custom GPT HTML), veya hiç UI değildi.

MCP Apps (SEP-1724, 26 Ocak 2026'da teslimat edildi) sözleşmeyi standartlaştırır.`resource`URI'si kim?`ui://...`ve kimin MIME'si `text/html;profile=mcp-app`. Host, açıkça izin verilmedikçe sınırlı bir CSP ve ağ erişimi olmayan kum kutulu bir iframe'de sunar. iframe içindeki kullanıcı arayüzü, küçük bir postMessage JSON-RPC diyalekti aracılığıyla sunucuya mesaj gönderir.

Her uyumlu istemci (Claude Desktop, ChatGPT, Goose, VS Code) aynı şekilde yapar `ui://`Bir sunucu, bir HTML paket, evrensel kullanıcı arazi.

## Anlaşım

### - Evet .`ui://`Kaynak düzenlemesi

Bir araç geri verir:

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

Ev sahibi arıyor .`resources/read`- ...`ui://notes/timeline`URI ve geri döner:

```json
{
  "contents": [{
    "uri": "ui://notes/timeline",
    "mimeType": "text/html;profile=mcp-app",
    "text": "<!doctype html>..."
  }]
}
```

### Iframe kum kutusu

Ev sahibi HTML ' i kum kutu içinde gösterir .`<iframe>`ile:

- `sandbox="allow-scripts allow-same-origin"`(veya her sunucu açıklaması için daha sıkı)
- Sunucu tarafından açıklanan CSP, cevap başlıkları ile uygulanır.
- - Ne kurabiye, ne de ev sahibi'nin kaynağı.
- Ağ erişimi sınırlı `connectSrc`CSP'de.

### Mesaj sonrası protokol

İframe , `window.postMessage`Küçük bir JSON-RPC 2.0 diyalekti:

Hep çakış .`targetOrigin`Eşlerin tam kökenine ve alıcı tarafta onaylama`event.origin`Bir yükü işlemeyince bir izin listesi karşısında kullanmayın.`"*"`Bu kanalın her iki tarafında  vücut araç çağrılarını ve kaynak okuyuşlarını taşıyor.

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

Kullanılabilir host tarafı yöntemleri kullanıcı aracının çağırabileceği:

- `host.callTool(name, arguments)` bir sunucu aracı çağırır.
- `host.readResource(uri)` bir MCP kaynağı okur.
- `host.getPrompt(name, arguments)` bir şablon getirir.
- `host.close()` kullanıcı ortamını reddeder.

Her arama hala MCP protokolü üzerinden geçer ve sunucu izinlerini miras alır.

### İzinler

- Evet .`_meta.ui.permissions`listesi, ek özellik talep ediyor:

- `camera` kullanıcı kamerasına erişmek (doküman taraması UI'leri için kullanılır).
- `microphone` Ses girişleri.
- `geolocation`- Yerleşim.
- `network:*`  daha geniş ağ erişim`connectSrc`Tek başına izin verir.

Her izin kullanıcı kullanıcı açısından gösterilmeden önce görülen bir istekdir.

### Güvenlik riskleri

Bir iframe'deki HTML hala HTML. Yeni saldırı yüzeyi:

- **Prompt-injection via UI.**Kötü bir sunucu kullanıcı arazi, bir sistem mesajına benzeyen metni gösterebilir ve kullanıcıyı kandırabilir.
- **Exfiltration via `connectSrc`.**CSP izin verirse `connect-src: *`- Öntanımlı olarak sıkı olmalıdır.
- **Clickjacking.**UI, host chrome üzerine örtülür. Hostler z-index manipülasyonunu önlemeli ve açıklık kurallarını uygulamalıdır.
- **Steal focus.**Kullanıcı kullanıcılığı, klavye odaklanmasını alır ve bir sonraki mesajı yakalar.

13 · 15 aşaması, MCP güvenliği çerçevesinde bunları derinlemesine kapsar; bu ders onları tanıtar.

### `ui/initialize`El sıkışması

İframe yüklenince, gönderir `ui/initialize`Mesaj sonrası:

```json
{"jsonrpc": "2.0", "id": 0, "method": "ui/initialize",
 "params": {"theme": "dark", "locale": "en-US", "sessionId": "..."}}
```

Host, özellikler ve bir seans jetonu ile yanıt verir. UI, sonraki her host çağrısında seans jetonu kullanır.

### AppRenderer / AppFrame SDK primitipleri

Ext-apps SDK iki kolaylık primitifinin ortaya çıkmasını sağlar:

- `AppRenderer`(server tarafı)  bir React / Vue / Solid bileşenini sarıp bir `ui://`Doğru MIME ve metadata ile kaynak.
- `AppFrame`(klient tarafı)  kaynakları alır, iframe'yi monte eder ve PostMessage aracılığıyla.

Bunları kullanabilir veya HTML ve JSON-RPC'yi elle kaydırabilirsiniz.

### Ekosistem durumu

MCP Apps 26 Ocak 2026'da teslim edildi.

- **Claude Desktop.**2026 Ocak'tan itibaren tam destek.
- **ChatGPT.**Apps SDK (MCP Apps protokolü) üzerinden tam destek.
- **Cursor.**Beta; ayarlar üzerinden etkinleştir.
- **VS Code.**İçeri girenler inşa eder.
- **Goose.**Tam destek.
- **Zed, Windsurf.**Yol haritası.

Üretimdeki sunucular: ara çubuğu, harita görselleştirmeleri, veri tabloları, tablo yapımcıları, kum kutu IDE ön izlemeleri.

```figure
t3-ui-sandbox
```

## Kullan

`code/main.py`Not sunucusu bir  ile uzatılır`visualize_timeline`bir `ui://notes/timeline`Kaynak, ek olarak bir yöneticisi `resources/read`Bu URI'de küçük ama SVG zaman çizgisi ile tamamlanmış bir HTML paketi gönderir. HTML stdlib-templated  build sistem yoktur. postMessage bir tarayıcı çalıştıramaz stdlib için JS yorumlarında çizilmiştir.

Neye bakılır:

- `_meta.ui`Bu araçta kaynakUri, CSP, izinler bulunmaktadır.
- HTML ağ erişimsiz rendere eder; tüm veriler içe aktarılır.
- JS arıyor .`host.callTool`-`window.parent.postMessage`(bu stdlib demo'da belgelenmiş ama inert).

## Gönder

Bu ders bize çok yararlı .`outputs/skill-mcp-apps-spec.md`. İnteraktif bir kullanıcı kullanımı kullanımından yararlanacak bir araç göz önüne alındığında, bu beceri MCP Apps'in tüm sözleşmesini oluşturur: `ui://`URI, CSP, izinler, mesaj gönderme giriş noktaları ve güvenlik kontrol listesi.

## Egzersizler

1. Çık .`code/main.py`ve gönderilen HTML'i inceleyin. HTML'i doğrudan bir tarayıcıda açın; SVG renderiyi doğrulayın.`host.callTool("notes_update", ...)`- Evet .

2. CSP' yi sıkılaştır: çıkar `'unsafe-inline'`HTML oluşturma kodunda ne değişiklikler var?

3. İkinci bir UI kaynağı ekle `ui://notes/editor`Notları düzenlemek için bir form var. Kullanıcı gönderdiğinde, iframe arar `host.callTool("notes_update", ...)`- Evet .

4. İNFRAEM sandbox neyin karşısına ve neyin karşısına savunur?

5. SEP-1724 özelliklerini okuyun ve bu oyuncak uygulamasından yararlanmadığı MCP Apps SDK'de bir özellik belirleyin.

## Anahtar Terimler

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

## Daha Fazla Okumak

- [MCP ext-apps — GitHub](https://github.com/modelcontextprotocol/ext-apps) Referans uygulanması ve SDK
- [MCP Apps specification 2026-01-26](https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx) Resmi bir belgesi
- [MCP — Apps extension overview](https://modelcontextprotocol.io/extensions/apps/overview) Yüksek düzeyde belgeler
- [MCP blog — MCP Apps launch](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/) 2026 Ocak'ta başlatma tarihi
- [MCP Apps API reference](https://apps.extensions.modelcontextprotocol.io/api/) JSDoc tarzında SDK referansı
