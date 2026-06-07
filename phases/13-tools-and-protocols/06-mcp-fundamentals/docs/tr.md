# MCP Temelleri — Primitifler, Yaşam Döngüsü, JSON-RPC Temeli

> MCP öncesi her entegrasyon bir kereliğine yapılıyordu. Model Context Protocol (Model Bağlam Protokolü), ilk olarak Anthropic tarafından Kasım 2024'te yayınlandı ve artık Linux Foundation'ın Agentic AI Foundation tarafından yönetiliyor, keşfi ve çağırmayı standartlaştırıyor böylece her istemci her sunucuyla konuşabiliyor. 2025-11-25 teknik dokümanı altı primitif isimlendirir (üç sunucu, üç istemci), üç aşamalı bir yaşam döngüsü ve JSON-RPC 2.0 tel formatını belirtir. Bunları öğrenin, bu fazın MCP bölümünün geri kalanı okuma haline gelir.

**Tür:** Öğren
**Diller:** Python (stdlib, JSON-RPC ayrıştırıcı)
**Ön koşullar:** Faz 13 · 01 ila 05 (araç arayüzü ve function calling)
**Süre:** ~45 dakika

## Öğrenme Hedefleri

- Altı MCP primitifini adlandırın (sunucu tarafında araçlar, kaynaklar, istemler; istemci tarafında kökler, örnekleme, ricada bulunma) ve her biri için bir kullanım durumu verin.
- Üç aşamalı yaşam döngüsünü (başlat, işlet, kapat) yürüyün ve her aşamada kimin hangi mesajı gönderdiğini belirtin.
- JSON-RPC 2.0 istek, yanıt ve bildirim zarflarını ayrıştırın ve üretin.
- `initialize`'daki yetenek müzakeresinin (capability negotiation) ne olduğunu ve onsuz neyin bozulduğunu açıklayın.

## Sorun

MCP öncesi, her araç kullanan ajanın kendi protokolü vardı. Cursor, MCP benzeri ama uyumsuz bir araç sistemine sahipti. Claude Desktop farklı bir taneyle yayınlandı. VS Code'un Copilot eklentisi üçüncüydü. Bir "Postorg sorgusu" aracı yazan ekip, aynı aracı üç kez yazdı, her biri farklı bir ana programın API'sine. Yeniden kullanmak kod kopyalamayı gerektiriyordu.

Sonuç, bir kereliğine entegrasyonların Kambriyen patlamasıydı ve ekosistem hızının bir tavanı vardı.

Bunu düzeltmek için MCP tel formatını standartlaştırır. Tek bir MCP sunucusu her MCP istemcisinde çalışır: Claude Desktop, ChatGPT, Cursor, VS Code, Gemini, Goose, Zed, Windsurf, Nisan 2026 itibarıyla 300+ istemci. Aylık 110M SDK indirmesi. 10.000+ genel sunucu. Linux Foundation, Aralık 2025'te yeni Agentic AI Foundation altında yönetimi devraldı.

Bu fazda kullanılan teknik doküman revizyonu **2025-11-25**'tir. Asenkron Görevleri (SEP-1686), URL modu ricada bulunmayı (SEP-1036), araçlarla örnekleme (SEP-1577), kademeli kapsam onayını (SEP-835) ve OAuth 2.1 kaynak gösterge anlambilimini ekler. Faz 13 · 09 ila 16 bu eklentileri kapsar. Bu ders temelde durur.

## Kavram

### Üç sunucu primitifi

1. **Araçlar.** Çağrılabilir eylemler. Faz 13 · 01'deki aynı dört adımlı döngü.
2. **Kaynaklar.** Sunulan veriler. URI ile adreslenebilir salt okunur içerik: `file:///path`, `db://query/...`, özel şemalar.
3. **İstemler.** Yeniden kullanılabilir şablonlar. Ana program UI'ında slash-komutları; sunucu şablonu sağlar, istemci argümanları doldurur.

### Üç istemci primitifi

4. **Kökler (Roots).** Sunucunun dokunabileceği URI kümesi. İstemci onları beyan eder; sunucu onlara saygı gösterir.
5. **Örnekleme (Sampling).** Sunucu, istemcinin modelinden bir completion yapmasını ister. Sunucu tarafında API anahtarı olmadan sunucu barındıran ajan döngülerini etkinleştirir.
6. **Ricada bulunma (Elicitation).** Sunucu, istemcinin kullanıcısından orta uçuşta yapılandırılmış girdi ister. Formlar veya URL'ler (SEP-1036).

MCP'taki her yetenek tam olarak bu altıdan birine aittir. Faz 13 · 10 ila 14 her birini derinlemesine kapsar.

### Tel formatı: JSON-RPC 2.0

Her mesaj şu alanları içeren bir JSON nesnesidir:

- İstekler: `{jsonrpc: "2.0", id, method, params}`.
- Yanıtlar: `{jsonrpc: "2.0", id, result | error}`.
- Bildirimler: `{jsonrpc: "2.0", method, params}` — `id` yok, yanıt beklenmez.

Temel teknik doküman ~15 method içerir, primitiflere göre gruplandırılmış. Önemli olanlar:

- `initialize` / `initialized` (el sıkışma)
- `tools/list`, `tools/call`
- `resources/list`, `resources/read`, `resources/subscribe`
- `prompts/list`, `prompts/get`
- `sampling/createMessage` (sunucudan istemciye)
- `notifications/tools/list_changed`, `notifications/resources/updated`, `notifications/progress`

### Üç aşamalı yaşam döngüsü

**Aşama 1: başlat.**

İstemci `yetenekleri` (capabilities) ve `clientInfo` ile `initialize` gönderir. Sunucu kendi `yetenekleri`, `serverInfo` ve konuştuğu teknik doküman sürümüyle yanıt verir. Yanıtı sindirdiğinde istemci `notifications/initialized` gönderir. Buradan itibaren, her iki taraf da müzakere edilen yeteneklere göre istek gönderebilir.

**Aşama 2: işletme.**

İkili yönlü. İstemci keşfetmek için `tools/list`, çağırmak için `tools/call` çağırır. Sunucu bu yeteneği beyan ettiyse `sampling/createMessage` gönderebilir. Araç kümesi değiştiğinde sunucu `notifications/tools/list_changed` gönderebilir. Kullanıcı kök kapsamını değiştirdiğinde istemci `notifications/roots/list_changed` gönderebilir.

**Aşama 3: kapatma.**

Her iki taraf taşımayı kapatır. MCP'ta yapılandırılmış bir kapatma methodu yok; taşıma (stdio veya Streamable HTTP, Faz 13 · 09) bağlantı sonu sinyalini taşır.

### Yetenek müzakeresi

`initialize` el sıkışmasındaki `yetenekler` (capabilities) sözleşmedir. Bir sunucudan örnek:

```json
{
 "tools": {"listChanged": true},
 "resources": {"subscribe": true, "listChanged": true},
 "prompts": {"listChanged": true}
}
#### Açıklama
Sunucu, tools/list_changed bildirimleri üretebileceğini ve resources/subscribe'ı desteklediğini beyan eder.
```

Sunucu `tools/list_changed` bildirimleri üretebileceğini ve `resources/subscribe`'ı desteklediğini beyan eder. İstemci kendi beyanıyla onaylar:

```json
{
 "roots": {"listChanged": true},
 "sampling": {},
 "elicitation": {}
}
#### Açıklama
İstemci, kök listesi değişikliği, örnekleme ve ricada bulunma yeteneklerini beyan eder.
```

İstemci `sampling`'i beyan etmezse, sunucu `sampling/createMessage` çağırmamalıdır. Simetrik: sunucu `resources.subscribe`'ı beyan etmezse, istemci abone olmaya çalışmamalıdır.

Bu, ekosistem kaymasını önleyen şeydir. Örnekleme desteklemeyen bir istemci hala geçerli bir MCP istemcidir; `sampling` çağırmayan bir sunucu hala geçerli bir MCP sunucusudur. Sadece o özelliği birlikte kullanmazlar.

### Yapılandırılmış içerik ve hata şekilleri

`tools/call`, tipli bloklardan oluşan bir `content` dizisi döndürür: `text`, `image`, `resource`. Faz 13 · 14, MCP Apps (`ui://` etkileşimli UI) ile bunu genişletir.

Hatalar JSON-RPC hata kodları kullanır. Teknik dokümanın tanımladığı eklemeler: `-32002` "Kaynak bulunamadı", `-32603` "Dahili hata", artı MCP'e özgü hata verisi `error.data` olarak.

### İstemci yetenekleri vs araç çağrısı detayları

Yaygın bir karışıklık: `capabilities.tools`, istemcinin araç listesi değişikliği bildirimlerini destekleyip desteklemediğidir. İstemcinin belirli araçları ÇAĞIRIP ÇAĞIRMAYACAĞı, model tarafından驱动an bir çalışma zamanı seçimidir, bir yetenek bayrağı değil. Yetenek bayrağı teknik doküman düzeyindeki sözlleşmedir. Modelin seçimi orthogonal'dır.

### Neden JSON-RPC, REST değil?

JSON-RPC 2.0 (2010), hafif ikili yönlü bir protokoldür. REST istemci başlatmalıdır. MCP, sunucu başlatmalı mesajlara (örnekleme, bildirimler) ihtiyaç duyuyordu, bu yüzden simetrik istek/yanıt şekline sahip JSON-RPC doğal bir uyum sağladı. JSON-RPC ayrıca stdio ve WebSocket/Streamable HTTP üzerinden temiz şekilde birleşir, HTTP'nin istek şeklini yeniden icat etmeden.

## Kullan

`code/main.py`, minimal bir JSON-RPC 2.0 ayrıştırıcısı ve üreteci sunar, ardından `initialize` → `tools/list` → `tools/call` → `kapatma` dizisini elle yürüterek her mesajı yazdırır. Gerçek taşıma yok; yalnızca mesaj şekilleri. Her zarfı doğrulamak için İleri Okuma'da bağlantılı teknik dokümanla karşılaştırın.

Neye bakılmalı:

- `initialize` her iki yönde yetenekleri beyan eder; yanıtta `serverInfo` ve `protocolVersion: "2025-11-25"` vardır.
- `tools/list` bir `tools` dizisi döndürür; her giriş `name`, `description`, `inputSchema` içerir.
- `tools/call` `params.name` ve `params.arguments` kullanır.
- Yanıt `content`, `{type, text}` bloklarından oluşan bir dizidir.

## Sun

Bu ders `outputs/skill-mcp-handshake-tracer.md` dosyasını üretir. Bir MCP istemci-sunucu etkileşiminin pcap benzeri bir dökümü verildiğinde, beceri her mesajı hangi primitife, hangi yaşam döngüsü aşamasına ve hangi yeteneğe bağımlı olduğunu not eder.

## Alıştırmalar

1. `code/main.py`'i çalıştırın. Yetenek müzakeresinin gerçekleştiği satırı belirleyin ve sunucu `tools.listChanged`'ı beyan etmemiş olsaydı neyin değişeceğini açıklayın.

2. Ayrıştırıcıyı `notifications/progress`'i ele alacak şekilde genişletin. Mesaj şekli: `{method: "notifications/progress", params: {progressToken, progress, total}}`. Uzun süren bir `tools/call` sırasında bunu üretin ve istemci işleyicisinin bir ilerleme çubuğu göstereceğini doğrulayın.

3. MCP 2025-11-25 teknik dokümanını baştan sona okuyun — tüm belge yaklaşık 80 sayfadır. Çoğu sunucunun GEREK DUYMADIĞı tek yetenek bayrağını belirleyin. İpucu: kaynak aboneliğiyle ilgili.

4. Kağıda, hayali bir "zamanlanmış görev" (cron job) özelliğinin hangi primitife ait olacağını çizin. (İpucu: sunucu istemciden bunu zamanlanmış bir zamanda çalıştırmasını istiyor. Altı primitifin hiçbiri bugüne uymuyor.) MCP'ın 2026 yol haritasında bunun için bir SEP taslağı var.

5. GitHub'da açık bir MCP sunucusundan bir oturum günlüğü ayrıştırın. İstek vs yanıt vs bildirim mesajlarını sayın. Trafikte yaşam döngüsü vs işletme oranının ne olduğunu hesaplayın.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| MCP | "Model Context Protocol" | Modelden araca keşif ve çağırma için açık protokol |
| Server primitive (Sunucu primitifi) | "Sunucunun sunduğu" | araçlar (eylemler), kaynaklar (veriler), istemler (şablonlar) |
| Client primitive (İstemci primitifi) | "İstemcinin sunuculara izin verdiği" | kökler (kapsam), örnekleme (LLM geri çağırmaları), ricada bulunma (kullanıcı girdisi) |
| JSON-RPC 2.0 | "Tel formatı" | Simetrik istek/yanıt/bildirim zarfları |
| `initialize` el sıkışması | "Yetenek müzakeresi" | İlk mesaj çifti; sunucular ve istemciler destekledikleri özellikleri beyan eder |
| `tools/list` | "Keşif" | İstemci sunucudan mevcut araç kümesini ister |
| `tools/call` | "Çağırrma" | İstemci sunucudan bir aracı argümanlarla çalıştırmasını ister |
| `notifications/*_changed` | "Değişiklik olayları" | Sunucu, primitif listesinin değiştiğini istemciye bildirir |
| Content block (İçerik bloğu) | "Tipli sonuç" | Araç sonucunda `{type: "text" \| "image" \| "resource" \| "ui_resource"}` |
| SEP | "Teknik Doküman Geliştirme Önerisi" | Adlı taslak önerisi (ör. asenkron Görevler için SEP-1686) |

## İleri Okuma

- [Model Context Protocol — Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) — kanonik teknik doküman
- [Model Context Protocol — Architecture concepts](https://modelcontextprotocol.io/docs/concepts/architecture) — altı primitif zihinsel model
- [Anthropic — Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) — Kasım 2024 lansman yazısı
- [MCP blog — First MCP anniversary](https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/) — bir yıllık geriye dönük bakış ve 2025-11-25 teknik doküman değişiklikleri
- [WorkOS — MCP 2025-11-25 spec update](https://workos.com/blog/mcp-2025-11-25-spec-update) — SEP-1686, 1036, 1577, 835 ve 1724 özeti
