# MCP Uygulamaları — `ui://` Aracılığıyla Etkileşimli UI Kaynakları

> Yalnızca metin içeren araç çıkışı, ajanların gösterebileceği şeyi sınırlar. MCP Apps (SEP-1724, 26 Ocak 2026'da resmi), bir aracın Claude Desktop, ChatGPT, Cursor, Goose ve VS Code'da satır içi olarak oluşturulmuş kum sandboxlu etkileşimli HTML dönüştürmesine olanak tanır. Panolar, formlar, haritalar, 3D sahneler, hepsi tek bir uzantı aracılığıyla. Bu ders `ui://` kaynak şemasını, `text/html;profile=mcp-app` MIME'ını, iframe-sandbox postMessage protokolünü ve bir sunucuya HTML oluşturma izni vermenin getirdiği güvenlik yüzeyini işler.

**Tür:** İnşa Et
**Diller:** Python (stdlib, UI kaynak üreteci), HTML (örnek uygulama)
**Ön koşullar:** Faz 13 · 07 (MCP sunucusu), Faz 13 · 10 (kaynaklar)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Bir araç çağrısından `ui://` kaynağı döndür ve doğru MIME ve meta veriyi ayarla.
- Bir aracın ilişkili UI'ını `_meta.ui.resourceUri`, `_meta.ui.csp` ve `_meta.ui.permissions` ile beyan et.
- UI'dan ana programa iletişim için iframe sandbox postMessage JSON-RPC'sini uygula.
- UI kaynaklı saldırılara karşı savunan varsayılan CSP ve permissions-policy uygula.

## Sorun

2025 dönemi bir `visualize_timeline` aracı "İşte kronolojik olarak düzenlenmiş 14 not: ..." döndürebilir. Bu bir paragraftır. Kullanıcılar aslında etkileşimli zaman çizelgesini ister. MCP Apps öncesi seçenekler: istemciye özgü widget API'leri (Claude artifacts, OpenAI Custom GPT HTML) veya hiç UI olmamasıydı.

MCP Apps (SEP-1724, 26 Ocak 2026'da yayınlandı) sözleşmeyi standartlaştırır. Bir araç sonucu, URI'si `ui://...` ve MIME'ı `text/html;profile=mcp-app` olan bir `resource` içerir. Ana program bunu sınırlı bir CSP ile sandboxlanmış bir iframe'de ve açıkça verilmedikçe ağ erişimi olmadan oluşturur. iframe içindeki UI, küçük bir postMessage JSON-RPC diyalekti aracılığıyla ana programa mesajlar gönderir.

Uyumlu her istemci (Claude Desktop, ChatGPT, Goose, VS Code) aynı `ui://` kaynağını aynı şekilde oluşturur. Tek bir sunucu, tek bir HTML paketi, evrensel UI.

## Kavram

### `ui://` kaynak şeması

Bir araç döndürür:

```json
{
  "content": [
    {"type": "text", "text": "İşte notlarınızın zaman çizelgesi:"},
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

Ardından ana program `ui://notes/timeline` URI'si üzerinde `resources/read` çağırır ve şunu alır:

```json
{
  "contents": [{
    "uri": "ui://notes/timeline",
    "mimeType": "text/html;profile=mcp-app",
    "text": "<!doctype html>..."
  }]
}
```

### Iframe sandbox

Ana program HTML'i sınırlı bir `<iframe>` içinde oluşturur:

- `sandbox="allow-scripts allow-same-origin"` (veya sunucu beyanına göre daha katı)
- Sunucu tarafından beyan edilen CSP yanıt başlıkları aracılığıyla uygulanır.
- Ana programın kaynagından çerez, localStorage yok.
- Ağ erişimi CSP'deki `connectSrc` ile sınırlı.

### postMessage protokolü

iframe, `window.postMessage` aracılığıyla ana programla iletişim kurar. Küçük bir JSON-RPC 2.0 diyalekti:

`targetOrigin`'u her zaman partnerin kesin kaynağına sabitleyin ve alan tarafta, herhangi bir yükü işlemeden önce `event.origin`'i bir izin listesine göre doğrulayın. Bu kanalın her iki tarafında da asla `"*"` kullanmayın — gövde araç çağrısı ve kaynak okumaları taşır.

```js
// iframe'den ana programa  (ana program kaynağına sabitle)
window.parent.postMessage({
  jsonrpc: "2.0",
  id: 1,
  method: "host.callTool",
  params: { name: "notes_update", arguments: { id: "note-14", title: "..." } }
}, "https://host.example.com");

// ana programdan iframe'e  (iframe kaynağına sabitle)
iframe.contentWindow.postMessage({
  jsonrpc: "2.0",
  id: 1,
  result: { content: [...] }
}, "https://iframe.example.com");

// her iki taraftaki alıcı
window.addEventListener("message", (event) => {
  if (event.origin !== "https://expected-peer.example.com") return;
  // event.data'yı işlemek güvenli
});
```

UI'ın çağırabileceği kullanılabilir ana program tarafı metodları:

- `host.callTool(name, arguments)` — bir sunucu aracını çağırır.
- `host.readResource(uri)` — bir MCP kaynağı okur.
- `host.getPrompt(name, arguments)` — bir istem şablonu getirir.
- `host.close()` — UI'ı kapatır.

Her çağrı hala MCP protokolünden geçer ve sunucunun izinlerini miras alır.

### İzinler

`_meta.ui.permissions` listesi ek yetenekler ister:

- `camera` — kullanıcının kamerasına erişim (belge tarama UI'ları için kullanılır).
- `microphone` — ses girdisi.
- `geolocation` — konum.
- `network:*` — `connectSrc`'in tek başına izin verdiğinden daha geniş ağ erişimi.

Her izin, UI oluşturulmadan önce kullanıcının gördüğü bir istemdir.

### Güvenlik riskleri

iframe'deki HTML hala HTML'dir. Yeni saldırı yüzeyi:

- **UI aracılığıyla prompt enjeksiyonu.** Kötü niyetli bir sunucu UI'ı, system mesajı gibi görünen ve kullanıcıyı kandıran metin gösterebilir. Ana program oluşturma, sunucu UI'ını ana program UI'ından belirgin şekilde ayırt etmelidir.
- **`connectSrc` aracılığıyla sızıntı.** CSP `connect-src: *`'e izin verirse, UI her yere veri gönderebilir. Varsayılan katı olmalıdır.
- **Clickjacking.** UI, ana program kromunu (chrome) kaplar. Ana programlar z-index manipülasyonunu önlemeli ve opaklık kurallarını zorlamalıdır.
- **Odağı çalma.** UI klavye odağını alır ve bir sonraki mesajı yakalar. Ana programlar bunu kesintiye uğratmalıdır.

Faz 13 · 15, MCP güvenliğinin bir parçası olarak bunları derinlemesine kapsar; bu ders bunları tanıtır.

### `ui/initialize` el sıkışması

iframe yüklendikten sonra postMessage aracılığıyla `ui/initialize` gönderir:

```json
{"jsonrpc": "2.0", "id": 0, "method": "ui/initialize",
 "params": {"theme": "dark", "locale": "en-US", "sessionId": "..."}}
```

Ana program yeteneklerle ve bir oturum jetonuyla yanıt verir. UI, sonraki her ana program çağrısında oturum jetonunu kullanır.

### AppRenderer / AppFrame SDK primitifleri

ext-apps SDK iki kolaylık primitifi sunar:

- `AppRenderer` (sunucu tarafı) — bir React / Vue / Solid bileşenini sarar ve doğru MIME ve meta veriyle bir `ui://` kaynağı üretir.
- `AppFrame` (istemci tarafı) — kaynağı alır, iframe'i monte eder ve postMessage'ı aracılık yapar.

Bunları kullanabilir veya HTML ve JSON-RPC'yi elle yapabilirsiniz.

### Ekosistem durumu

MCP Apps 26 Ocak 2026'da yayınlandı. Nisan 2026 itibarıyla istemci desteği:

- **Claude Desktop.** Ocak 2026'dan beri tam destek.
- **ChatGPT.** Apps SDK aracılığıyla tam destek (aynı temel MCP Apps protokolü).
- **Cursor.** Beta; ayarlardan etkinleştirin.
- **VS Code.** Yalnızca Insider sürümleri.
- **Goose.** Tam destek.
- **Zed, Windsurf.** Yol haritasında.

Üretimdeki sunucular: panolar, harita görselleştirmeleri, veri tabloları, grafik oluşturucular, sandbox IDE önizlemeleri.

## Kullan

`code/main.py`, notlar sunucusunu bir SVG zaman çizelgesi içeren küçük ama eksiksiz bir HTML paketi döndüren `visualize_timeline` aracıyla genişletir; ayrıca bu URI üzerindeki `resources/read` için bir işleyici ekler. HTML stdlib-şablonlu — derleme sistemi yok. postMessage, stdlib bir tarayıcı süremeyeceği için JS yorumlarında çizilmiştir.

Neye bakılmalı:

- Araç yanıtındaki `_meta.ui`, resourceUri, CSP, izinleri taşır.
- HTML ağ erişimi olmadan oluşturulur; tüm veri satır içi.
- JS, `window.parent.postMessage` aracılığıyla `host.callTool` çağırır (belgelenmiş ancak bu stdlib demosunda etkisiz).

## Sun

Bu ders `outputs/skill-mcp-apps-spec.md` dosyasını üretir. Etkileşimli UI'dan yararlanacak bir araç verildiğinde, beci MCP Apps sözleşme paketini üretir: `ui://` URI, CSP, izinler, postMessage giriş noktaları ve bir güvenlik kontrol listesi.

## Alıştırmalar

1. `code/main.py`'i çalıştırın ve üretilen HTML'i inceleyin. HTML'i doğrudan tarayıcıda açın; SVG'nin oluşturulduğunu doğrulayın. Ardından UI'ın `host.callTool("notes_update", ...)` çağırmak için kullanacağı postMessage sözleşmesini çizin.

2. CSP'yi sıkılaştırın: `'unsafe-inline'`'ı kaldırın ve nonce tabanlı bir script politikası kullanın. HTML üretim kodunda ne değişir?

3. Bir notu yerinde düzenlemek için form içeren ikinci bir UI kaynağı `ui://notes/editor` ekleyin. Kullanıcı gönderdiğinde iframe `host.callTool("notes_update", ...)` çağırır.

4. UI'nın saldırı yüzeyini denetleyin. Kötü niyetli bir sunucu nerede içerik enjekte edebilir? Iframe sandbox neye karşı savunur ve neye karşı savunmaz?

5. SEP-1724 teknik dokümanını okuyun ve bu oyuncak uygulamanın kullanmadığı MCP Apps SDK'daki bir yeteneği belirleyin. (İpucu: bileşen düzeyinde senkronizasyon.)

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| MCP Apps | "Etkileşimli UI kaynakları" | 26-01-2026'da yayınlanan SEP-1724 eklentisi |
| `ui://` | "Uygulama URI şeması" | UI paketleri için kaynak şeması |
| `text/html;profile=mcp-app` | "MIME" | MCP App HTML için içerik türü |
| Iframe sandbox | "Oluşturma konteyneri" | CSP ve izinlerle tarayıcı sandbox'u |
| postMessage JSON-RPC | "UI'dan ana programa tel" | Ana program çağrıları için küçük JSON-RPC-over-postMessage diyalekti |
| `_meta.ui` | "Araç-UI bağlama" | Bir araç sonucunu bir UI kaynağına bağlayan meta veri |
| CSP | "Content-Security-Policy" | Script, ağ, stil için izin verilen kaynakları beyan eder |
| AppRenderer | "Sunucu SDK primitifi" | Bir çerçeve bileşenini `ui://` kaynağına dönüştürür |
| AppFrame | "İstemci SDK primitifi" | postMessage'ı aracılık yapan iframe montaj yardımcısı |
| `ui/initialize` | "El sıkışma" | UI'dan ana programana ilk postMessage |

## İleri Okuma

- [MCP ext-apps — GitHub](https://github.com/modelcontextprotocol/ext-apps) — referans uygulama ve SDK
- [MCP Apps specification 2026-01-26](https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx) — resmi teknik doküman
- [MCP — Apps extension overview](https://modelcontextprotocol.io/extensions/apps/overview) — üst düzey belgeleme
- [MCP blog — MCP Apps launch](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/) — Ocak 2026 lansman yazısı
- [MCP Apps API reference](https://apps.extensions.modelcontextprotocol.io/api/) — JSDoc tarzı SDK referansı
