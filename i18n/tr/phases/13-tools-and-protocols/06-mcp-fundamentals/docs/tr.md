# MCP Temellikleri  İlkeler, Yaşam Dönemi, JSON-RPC Üssü

> MCP'den önceki her entegrasyon bir kerelikti. İlk olarak Kasım 2024'te Anthropic tarafından gönderilen ve şimdi Linux Vakfı'nın Agentic AI Vakfı tarafından yönetilen Model Kontext Protokolü, keşif ve çağrıları standartlaştırır, böylece herhangi bir müşteri herhangi bir sunucuyla konuşabilir. 2025-11-25 spesifikasyonu altı primitif (üç sunucu, üç istemci), üç aşamalı bir yaşam döngüsü ve JSON-RPC 2.0 tel biçimi isimlendiriyor. Bunları öğrenin ve bu aşamada MCP bölümünün geri kalanı okuma haline gelir.

**Type:** Learn
**Languages:** Python (stdlib, JSON-RPC parser)
**Prerequisites:** Phase 13 · 01 through 05 (the tool interface and function calling)
**Time:** ~45 minutes

## Öğrenme Hedefleri

- Tüm altı MCP primitiflerini (söreleri, kaynakları, sunucuda istekler; kökler, örnekleme, istemci üzerinde çıkarma) isimlendirin ve her birine bir kullanım durumunu verin.
- Üç aşamalı yaşam döngüsünü geçin (başlat, çalıştır, kapat) ve her aşamada hangi mesajı gönderenleri belirtin.
- JSON-RPC 2.0 istek, yanıt ve bildirim zarflarını incelemek ve yayınlamak.
- Hangi kapasite müzakere edildiğini açıklayın .`initialize`Bu, bir şey ve bu olmadan ne kırılır.

## Sorun

MCP'den önce, her araç kullanan ajanın kendi protokolü vardı. Cursor, MCP şeklinde ancak uyumsuz bir araç sistemine sahipti. Claude Desktop farklı bir ile gönderildi. VS Code'un Copilot uzantısı üçüncüsü vardı. "Postgres sorgu" aracı oluşturan bir ekip aynı aracı üç kez yazdı, her biri farklı bir barındırma API'ye.

Sonuç, bir kereli entegrasyonların Kambriyan patlaması ve ekosistem hızının bir tavanı oldu.

MCP, bu durumu tel biçimini standartlaştırarak düzeltir. Her MCP istemcisinde tek bir MCP sunucusu çalışır: Claude Desktop, ChatGPT, Cursor, VS Code, Gemini, Goose, Zed, Windsurf, Nisan 2026'a kadar 300+ istemci. 110M aylık SDK indirme. 10,000+ kamu sunucuları. Linux Vakfı, yeni Agentic AI Vakfı altında Aralık 2025'te yönetim kurdu.

Bu aşamada kullanılan spesifikasyon reviziyonu **2025-11-25**. Async Tasks (SEP-1686), URL modunun oluşturulması (SEP-1036), araçlarla örnekleme (SEP-1577), artışlı kapsam onay (SEP-835), ve OAuth 2.1 kaynak göstergesi semantiklerini ekler.

## Anlaşım

### Üç sunucu ilkesi

1. **Tools.**Çıkanma eylemleri. 13. fazadan aynı 4 adımlı döngü.
2. **Resources.**Açıklanan veriler. URI tarafından adreslenebilen sadece okunur içeriği: `file:///path`- Evet .`db://query/...`, özel programlar.
3. **Prompts.**Tekrar kullanılabilir şablonlar. Host UI'de kesik komutlar; sunucu şablonu sağlar, istemci argümanları doldurur.

### Üç müşteri ilkesi

4. **Roots.**URI'lerin serveri dokunmasına izin verilir.
5. **Sampling.**Server, bir tamamlama yapmak için istemcinin modelini talep eder. Server tarafından barındırılan ajan döngüleri sunucu taraflı API anahtarları olmadan etkinleştirir.
6. **Elicitation.**Server, istemcinin kullanıcısını uçuş ortasında yapılandırılmış giriş için soruyor.

MCP'deki her yetenek bu altı yetenekten tam olarak birine aittir.

### Kablo biçimi: JSON-RPC 2.0

Her mesaj, bu alanlarla bir JSON nesnesi:

- İstekler: `{jsonrpc: "2.0", id, method, params}`- Evet .
- Cevaplar: `{jsonrpc: "2.0", id, result | error}`- Evet .
- İletişimler: `{jsonrpc: "2.0", method, params}`Hayır.`id`, hiç bir tepki beklenmiyor.

Temel özellikte ~15 yöntem vardır, ilkel olarak gruplandırılır.

- `initialize`- Ne ?`initialized`- Evet .
- `tools/list`- Evet .`tools/call`
- `resources/list`- Evet .`resources/read`- Evet .`resources/subscribe`
- `prompts/list`- Evet .`prompts/get`
- `sampling/createMessage`(server-klient)
- `notifications/tools/list_changed`- Evet .`notifications/resources/updated`- Evet .`notifications/progress`

### Üç aşamalı yaşam döngüsü

**Phase 1: initialize.**

Müşteri gönderir .`initialize`- ... ... ...`capabilities`ve `clientInfo`Sunucu kendi yanıtlarıyla cevap verir .`capabilities`- Evet .`serverInfo`- Ve konuşturduğu özellik versiyonu.`notifications/initialized`Bu durumda her iki taraf da müzakere edilen yeteneklere göre talep gönderebilir.

**Phase 2: operation.**

İki yönlü. Müşteri arıyor.`tools/list`O zaman keşfetmek için.`tools/call`Sunucu gönderebilir.`sampling/createMessage`Eğer bu yeteneği açıklarsa, sunucu gönderebilir.`notifications/tools/list_changed`Kullanıcı gönderebilir.`notifications/roots/list_changed`Kullanıcı kök kapsamını değiştirdiğinde.

**Phase 3: shutdown.**

Her iki taraf da nakliyeyi kapatır. MCP'de yapılandırılmış kapanış yöntemi yoktur; nakliye (studio veya Streamable HTTP, Fase 13 · 09) bağlantının son sinyalini taşıyor.

### Kapasite müzakere

`capabilities`- ... ...`initialize`El sıkışması sözleşme.

```json
{
  "tools": {"listChanged": true},
  "resources": {"subscribe": true, "listChanged": true},
  "prompts": {"listChanged": true}
}
```

Sunucu yayınlanabileceğini açıkladı .`tools/list_changed`bildirim ve destek `resources/subscribe`Müşteri , kendi hakkını açıklayarak:

```json
{
  "roots": {"listChanged": true},
  "sampling": {},
  "elicitation": {}
}
```

Müşteri bildirmezse`sampling`, sunucu aramasın .`sampling/createMessage`. Simetrik: eğer sunucu açıklamadı `resources.subscribe`Müşteri, imzalamaya çalışmamalı.

Bu, ekosistem sürüklenmesini önler. Örneklemeyi desteklemeyen bir istemci hala geçerli bir MCP istemcisi; arama yapmayan bir sunucu `sampling`Bu özellikleri birlikte kullanmıyorlar.

### Yapılandırılmış içerik ve hata şekilleri

`tools/call`bir `content`Tiplenen bloklar dizisi: `text`- Evet .`image`- Evet .`resource`. 13 · 14 aşamada MCP Apps eklenir (`ui://`Bu listeye eklenir.

Hatalar JSON-RPC hata kodlarını kullanır.`-32002`"Kaynak bulunamadı",`-32603`"İçki hata", ek olarak MCP spesifik hata verileri`error.data`- Evet .

### Müşteri yetenekleri vs araç çağrıları detayları

Genel bir karışıklık:`capabilities.tools`Bu seçenekler, bir uygulama veya uygulama için kullanılabilir bir araç olarak kullanılır. Bu seçenekler, bir uygulama veya uygulama için kullanılabilir bir araç olarak kullanılır.

### Neden REST değil JSON-RPC?

JSON-RPC 2.0 (2010) hafif bir iki yönlü protokoldür. REST istemci tarafından başlatılır. MCP'ye sunucu tarafından başlatılan mesajlar (sampling, bildirimler) gerekirdi, bu nedenle JSON-RPC simetrik talep / yanıt şekliyle doğal bir uyumluydu. JSON-RPC ayrıca HTTP'nin talep şeklini yeniden icat etmeden stdio ve WebSocket / Streamable HTTP üzerinde temiz bir şekilde oluşturur.

```figure
mcp-tool-call
```

## Kullan

`code/main.py`en az bir JSON-RPC 2.0 analizörü ve emiten gönderir, sonra `initialize`→ `tools/list`→ `tools/call`→ `shutdown`Her zarfı doğrulamak için, daha fazla okuma bölümünde bağlantılı özelliklere karşılaştırın.

Neye bakılır:

- `initialize`İkisi de yeteneklerini açıklıyor; cevap `serverInfo`ve `protocolVersion: "2025-11-25"`- Evet .
- `tools/list`bir `tools`Array; her giriş `name`- Evet .`description`- Evet .`inputSchema`- Evet .
- `tools/call`kullanımı `params.name`ve `params.arguments`- Evet .
- Cevap`content`bir dizi `{type, text}`- Bloklar.

## Gönder

Bu ders bize çok yararlı .`outputs/skill-mcp-handshake-tracer.md`. MCP istemci-sörver etkileşiminin pcap tarzında bir transkripti verildiğinde, becerin her mesajın hangi primitif, hangi yaşam döngüsü aşamasını ve hangi yeteneğe bağlı olduğunu not eder.

## Egzersizler

1. Çık .`code/main.py`. Yetenek müzakerelerinin gerçekleşeceği çizgiyi belirleyin ve sunucu açıklamamasaydı ne değişeceğini açıklayın `tools.listChanged`- Evet .

2. Parser ' i kaldır .`notifications/progress`Mesaj şekli:`{method: "notifications/progress", params: {progressToken, progress, total}}`Uzun süreli bir süreliğine yayın .`tools/call`devam ediyor ve müşteri yöneticisinin bir ilerleme çubuğunu görüntüleyeceğini onaylayın.

3. MCP 2025-11-25 özelliklerini yukarıdan aşağıya okuyun. Tüm belge yaklaşık 80 sayfadır. Çoğu sunucuya ihtiyaç duyulmayan bir yetenek bayrağını belirleyin. İpucu: kaynak aboneliği ile ilgilidir.

4. MCP'nin 2026 yol haritasında bunun için bir SEP taslağı vardır.

5. GitHub'daki açık bir MCP sunucusu üzerinden bir seans günlüğünü analiz edin. İstediği karşı karşı cevap karşı bildirim mesajlarını sayın. Trafikin yaşam döngüsü karşı operasyonun ne kadar bölümü olduğunu hesaplayın.

## Anahtar Terimler

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| MCP | "Model Context Protocol" | Open protocol for model-to-tool discovery and invocation |
| Server primitive | "What a server exposes" | tools (actions), resources (data), prompts (templates) |
| Client primitive | "What a client lets servers use" | roots (scope), sampling (LLM callbacks), elicitation (user input) |
| JSON-RPC 2.0 | "The wire format" | Symmetric request/response/notification envelopes |
| `initialize` handshake | "Capability negotiation" | First message pair; servers and clients declare features they support |
| `tools/list` | "Discovery" | Client asks server for its current tool set |
| `tools/call` | "Invocation" | Client asks server to execute a tool with arguments |
| `notifications/*_changed` | "Mutation events" | Server tells client that its primitive list has changed |
| Content block | "Typed result" | `{type: "text" \| "image" \| "resource" \| "ui_resource"}` in tool result |
| SEP | "Spec Evolution Proposal" | Named draft proposal (e.g. SEP-1686 for async Tasks) |

## Daha Fazla Okumak

- [Model Context Protocol — Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) Kanonik özellik belgesi
- [Model Context Protocol — Architecture concepts](https://modelcontextprotocol.io/docs/concepts/architecture) altı primitif zihinsel model
- [Anthropic — Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) Kasım 2024'te başlatma tarihi
- [MCP blog — First MCP anniversary](https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/) Bir yıllık geriye bakış ve 2025-11-25 tarihleri değişikliği
- [WorkOS — MCP 2025-11-25 spec update](https://workos.com/blog/mcp-2025-11-25-spec-update) SEP-1686, 1036, 1577, 835 ve 1724 özetleri
