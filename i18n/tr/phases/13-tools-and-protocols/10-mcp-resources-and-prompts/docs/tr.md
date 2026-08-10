# MCP Kaynakları ve İpuçları  Araçlardan Öte Kontext Açıklaması

> Kullanım araçları MCP dikkatinin yüzde 90'ını alır. Diğer iki sunucu primitifin farklı sorunları çözür. Kaynaklar okuma için verileri ortaya çıkarır; istekler tekrar kullanılabilir şablonları kesme komutları olarak ortaya çıkarır. Birçok sunucu, araçlara okunuşları paketlemek yerine kaynakları kullanmalı ve istemci isteklerinde sert kodlama iş akışları yerine istekler kullanmalıdır. Bu ders karar kuralını isimlendirir ve yönlendirmeyi yürütür.`resources/*`ve `prompts/*`Mesajlar.

**Type:** Build
**Languages:** Python (stdlib, resource + prompt handler)
**Prerequisites:** Phase 13 · 07 (MCP server)
**Time:** ~45 minutes

## Öğrenme Hedefleri

- Bir yeteneği bir araç, kaynak veya belirli bir alan için bir istek olarak açığa çıkarmak arasında karar verin.
- Uygulama`resources/list`- Evet .`resources/read`- Evet .`resources/subscribe`ve elini tut .`notifications/resources/updated`- Evet .
- Uygulama`prompts/list`ve `prompts/get`Tartışma şablonları ile.
- Ev sahibi, talimatları otomatik olarak enjekte edilen bağlamla karşılaştırarak, talimatları gösterdiğinde fark et.

## Sorun

Notlar uygulaması için saf bir MCP sunucusu her şeyi araç olarak ortaya çıkarır: `notes_read`- Evet .`notes_list`- Evet .`notes_search`Bu, tüm veri erişimlerini model yönlendirilen bir araç çağrısı ile sarar.

- Model aramayacak mı karar vermeli.`notes_read`Bu konuya ait olan her soruyu sormak için.
- Sadece okunur içerik, sunucu yan paneline abone veya akışlanamaz.
- Müşteri UI'leri (Claude Desktop'un kaynak ekleme panelini, Cursor'un "Fayla dahil" seçicisi) verileri yüzeyde bırakamaz.

Sağ bölünme: verileri bir kaynak olarak ortaya çıkarmak, mutasyonlu veya hesaplanmış eylemleri araçlar olarak ortaya çıkarmak, tekrar kullanılabilir çok adımlı iş akışlarını istekler olarak ortaya çıkarmak. Her primitif'in UX erişimi ve erişim kalıbı vardır.

## Anlaşım

### Araçlar vs kaynaklar vs. istekler  karar kuralı

| Capability | Primitive |
|------------|-----------|
| User wants to search, filter, or transform data | tool |
| User wants the host to include this data as context | resource |
| User wants a templated workflow they can re-run | prompt |

Yönerge: eğer model, ilgili her sorguda çağrılmaktan yarar görürse, bir araçtır. Eğer kullanıcı, bir sohbete bağlanmaktan yarar görürse, bir kaynaktır. Eğer tüm bir çok adımlı iş akışı, kullanıcı'nın yeniden kullanmak istediği birimse, bir isteklendirme olur.

### Kaynaklar

`resources/list`Devamı`{resources: [{uri, name, mimeType, description?}]}`- Evet .`resources/read`Alıyor .`{uri}`ve geri dönüşleri`{contents: [{uri, mimeType, text | blob}]}`- Evet .

URI'ler adreslenebilir her şey olabilir:

- `file:///Users/alice/notes/mcp.md`
- `postgres://my-db/query/SELECT ...`
- `notes://note-14`(gümrük düzenlemesi)
- `memory://session-2026-04-22/recent`(server-sözlü)

`contents[]`Hem metni hem de ikili kullanımı destekler.`blob`base64 kodlanmış bir ip artı `mimeType`- Evet .

### Kaynak abonelikleri

İtiraf et .`{resources: {subscribe: true}}`- Müşteri çağrıları.`resources/subscribe {uri}`- Sunucu gönderir .`notifications/resources/updated {uri}`Kaynak değişince, müşteri tekrar okuyor.

Kullanım durumu: kaynakları disk üzerindeki dosyalar olan not sunucusu; dosya izleyicisi güncellemeler uyarısını tetikler; Claude Desktop dosyayı host dışında düzenlediğinde bağlamda yeniden çekir.

### Kaynak Şablonları (2025-11-25 eklenmesi)

`resourceTemplates`parametreli bir URI örneğini ortaya çıkarmak için: `notes://{id}`- Evet .`id`Müşteri kaynak seçicisinde kimliklerini otomatik olarak tamamlayabilir.

### İpuçlar

`prompts/list`Devamı`{prompts: [{name, description, arguments?}]}`- Evet .`prompts/get`Alıyor .`{name, arguments}`ve geri dönüşleri`{description, messages: [{role, content}]}`- Evet .

Bir istek, ev sahibi tarafından modeline beslenen mesajların bir listesini dolduran bir şablondur.`code_review`Hemen bir `file_path`argument ve üç mesajlı bir dizini gönderir: bir sistem mesajı, dosya vücudu ile bir kullanıcı mesajı ve bir mantık şablonu ile bir yardımcı atış.

### Ev sahibi ve haberleri

Claude Desktop, VS Code ve Cursor, sohbet kullanıcı aracında slash-komutlar olarak istekleri ortaya çıkarır. Kullanıcılar `/code_review`Bir sunucu'nun istekleri "kullanıcı kısayolu" ve "model'e gönderilen tam istek" arasındaki sözleşmedir.

Her istemci istekleri desteklemiyor.  Kontrol yetenekleri müzakere.

### "List değiştirildi" bildirimi

Hem kaynaklar hem de istekler yayımlanıyor .`notifications/list_changed`Yeni 20 not içeri aldığı not sunucusu yayıyor.`notifications/resources/list_changed`Müşteri tekrar arar.`resources/list`Ekleri almak için.

### İçerik tipi konvansiyonları

Metin için: `mimeType: "text/plain"`- Evet .`text/markdown`- Evet .`application/json`- Evet .
İkili için: `image/png`- Evet .`application/pdf`, artı `blob`- Alan.
MCP Uygulamaları için (Deneyim 14): `text/html;profile=mcp-app`bir `ui://`URI.

### Dinamik kaynaklar

Bir kaynak URI'nin statik bir dosya ile karşılık gelmesi gerekmez. `notes://recent`Her okuma için son beş notu geri verebilirim.`db://query/users/active`Sunucu, içeriği dinamik olarak hesaplamakta özgürdür.

Kural: eğer istemci URI tarafından önbelleğe koyabilirse, URI istikrarlı olmalıdır. Hesaplama tek çekim ise, URI bir zaman damgasını veya nonce içermelidir, böylece istemci önbelleği eskileşmez.

### Abonelikler ile oylamalar

Abonelik yeteneği olan müşteriler sunucuyu kullanıyor `notifications/resources/updated`. Ön abonelik müşterileri veya desteklemeyen sunucuları yeniden okuyarak anket. Her ikisi de spesifikasyonlara uygun.

Abonelik maliyeti: Sessiyon başına sunucu durumunda (kim neye abone oldu). Aboneli set sınırlı tutun; bağlantı kesilen müşteriler zaman kesmelidir.

### İstekler vs. Sistem İstekleri

MCP'deki istekler sistem istekleri değildir. Host'ın sistem istekleri (özünün işletim talimatları) ve MCP istekleri (kullanıcı tarafından çağrılan sunucu sağlanan şablonlar) yan yana yaşar. İyi davranan bir istemci asla bir sunucu istekini kendi sistem isteklerini ön plana bırakmaz; onları katlar.

```figure
t3-primitive-sort
```

## Kullan

`code/main.py`Not sunucusu ders 07'den sonra:

- Not başına kaynaklar (`notes://note-1`(v.b.) ile`resources/subscribe`Destek.
- A.`review_note`3 mesaj şablonu ile gönderilen bir prompt.
- Dosya izleyicisi simülasyonu , `notifications/resources/updated`Not değiştirildiğinde.
- A.`notes://recent`En son beş notu geri veren dinamik kaynak.

Tam akışını görmek için demo çalıştır.

## Gönder

Bu ders bize çok yararlı .`outputs/skill-primitive-splitter.md`Önerilen bir MCP sunucusu göz önüne alındığında, beceriler her yeteneği bir mantıklılık ile araç / kaynak / istek olarak sınıflandırır.

## Egzersizler

1. Çık .`code/main.py`. İlk kaynak listesine bak, sonra not düzenlemeyi başlat ve `notifications/resources/updated`- Yangın olayı.

2. Bir ekle`resources/list_changed`yayıcı: Yeni bir not oluşturulduğunda, müşterilerin yeniden keşfetmesi için bildirimi gönderin.

3. GitHub MCP sunucu için üç istek tasarlayın: `summarize_pr`- Evet .`triage_issue`- Evet .`release_notes`Bu nedenle, bu sistemin kullanılabilirliği için gerekli düzenlemeler yapılmalıdır.

4. Ders 07 sunucusunda mevcut bir aracı alın ve bir araç olarak kalıp kalmayacağını veya bir kaynak artı araç çiftine bölülüp bölülmeyeceğini sınıflandırın.

5. Spec'in yazısını oku.`server/resources`ve `server/prompts`Bölümler. `resources/read`Bu çok nadiren kalabalık bir yer ama spesifikasyon desteklenir.`_meta`Kaynak içeriği hakkında.

## Anahtar Terimler

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

## Daha Fazla Okumak

- [MCP — Concepts: Resources](https://modelcontextprotocol.io/docs/concepts/resources) kaynak URI'leri, abonelikleri ve şablonları
- [MCP — Concepts: Prompts](https://modelcontextprotocol.io/docs/concepts/prompts) prompt şablonları ve slash komut entegrasyonu
- [MCP — Server resources spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/resources) Tam `resources/*`mesaj referansı
- [MCP — Server prompts spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts) Tam `prompts/*`mesaj referansı
- [MCP — Protocol info site: resources](https://modelcontextprotocol.info/docs/concepts/resources/) Resmi belgeleri genişletmek için topluluk kılavuzu
