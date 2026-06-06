# MCP Kaynakları ve İstemleri — Araçların Ötesinde Bağlam Sunma

> Araçlar MCP ilgisinin %90'ını alır. Diğer iki sunucu primitifi farklı sorunları çözer. Kaynaklar okuma için veri sunar; istemler yeniden kullanılabilir şablonları slash-komutları olarak sunar. Birçok sunucu, okumaları araçlara sarmak yerine kaynakları ve istemleri, istemci istemlerinde iş akışlarını kodlamak yerine kullanmalıdır. Bu ders karar verme kuralını isimlendirir ve `resources/*` ve `prompts/*` mesajlarını yürüyerek gösterir.

**Tür:** İnşa Et
**Diller:** Python (stdlib, kaynak + istem işleyicisi)
**Ön koşullar:** Faz 13 · 07 (MCP sunucusu)
**Süre:** ~45 dakika

## Öğrenme Hedefleri

- Belirli bir alan için bir yeteneği araç, kaynak veya istem olarak sunma arasında karar ver.
- `resources/list`, `resources/read`, `resources/subscribe`'ı uygula ve `notifications/resources/updated`'ı ele al.
- `prompts/list` ve `prompts/get`'i argüman şablonlarıyla uygula.
- Ana programların istemleri slash-komutları olarak ne zaman yüzey çıkardığını vs otomatik olarak enjekte edilen bağlam olarak ne zaman gösterdiğini tanı.

## Sorun

Bir notlar uygulaması için_naif bir MCP sunucusu her şeyi araç olarak sunar: `notes_read`, `notes_list`, `notes_search`. Bu, her veri erişimini model tarafından驱动an bir araç çağrısına sarar. Sonuçlar:

- Model, bağlamdan yararlanabilecek her sorgu için `notes_read`'i çağırmaya karar vermek zorundadır.
- Salt okunur içerik abone olunamaz veya yan panelde akışı yapılamaz.
- İstemci UI'ları (Claude Desktop'ın kaynak ekleme paneli, Cursor'ın "Include file" seçicisi) veriyi yüzey çıkaramaz.

Doğru bölünme: veriyi kaynak olarak sun, değiştiren veya hesaplanan eylemleri araç olarak sun, yeniden kullanılabilir çok adımlı iş akışlarını istem olarak sun. Her primitifin kendi UX kolaylığı ve erişim paterni vardır.

## Kavram

### Araç vs kaynak vs istem — karar kuralı

| Yetenek | Primitif |
|------------|-----------|
| Kullanıcı veriyi aramak, filtrelemek veya dönüştürmek istiyor | araç |
| Kullanıcı ana programının bu veriyi bağlam olarak eklemesini istiyor | kaynak |
| Kullanıcı yeniden çalıştırabilecekleri şablonlu bir iş akışı istiyor | istem |

Kılavuz: model bunu ilgili her sorguda çağırmaktan yararlanacaksa, bu bir araçtır. Kullanıcı bunu bir konuşmaya eklemekten yararlanacaksa, bu bir kaynaktır. Tüm bir çok adımlı iş akışı kullanıcının yeniden kullanmak istediği ünitesiyse, bu bir istemdir.

### Kaynaklar

`resources/list`, `{resources: [{uri, name, mimeType, description?}]}` döndürür. `resources/read`, `{uri}` alır ve `{contents: [{uri, mimeType, text | blob}]}` döndürür.

URI'ler herhangi bir adreslenebilir şey olabilir:

- `file:///Users/alice/notes/mcp.md`
- `postgres://my-db/query/SELECT ...`
- `notes://note-14` (özel şema)
- `memory://session-2026-04-22/recent` (sunucuya özgü)

`contents[]` hem metni hem de ikili veriyi destekler. İkili, bir base64 kodlanmış string olarak `blob` artı bir `mimeType` kullanır.

### Kaynak abonelikleri

Yeteneklerde `{resources: {subscribe: true}}` beyan edin. İstemci `resources/subscribe {uri}` çağırır. Kaynak değiştiğinde sunucu `notifications/resources/updated {uri}` gönderir. İstemci yeniden okur.

Kullanım durumu: kaynakları diskteki dosyalar olan bir notlar sunucusu; bir dosya izleyici güncelleme bildirimleri tetikler; Claude Desktop, ana programın dışında düzenlendiğinde dosyayı bağlama yeniden çeker.

### Kaynak şablonları (2025-11-25 ekleme)

`resourceTemplates`, `id` bir tamamlama hedefi olarak `notes://{id}` ile parametreli bir URI kalıbı sunmanızı sağlar. İstemci, kaynak seçicide id'leri otomatik tamamlayabilir.

### İstemler

`prompts/list`, `{prompts: [{name, description, arguments?}]}` döndürür. `prompts/get`, `{name, arguments}` alır ve `{description, messages: [{role, content}]}` döndürür.

Bir istem, ana programın modeline beslediği bir mesaj listesine dönüşen bir şablondur. Örneğin, bir `code_review` istemi bir `file_path` argümanı alır ve üç mesajlık bir dizi döndürür: bir system mesajı, dosya gövdesini içeren bir user mesajı ve bir akım şablonuyla başlayan bir assistant mesajı.

### Ana programlar ve istemler

Claude Desktop, VS Code ve Cursor istemleri sohbet UI'ında slash-komutları olarak sunar. Kullanıcı `/code_review` yazar ve bir formdan argümanlar seçer. Sunucunun istemi "kullanıcı kısayolu" ile "modele gönderilen tam istem" arasındaki sözeleşmedir.

Her istemci henüz istemleri desteklemiyor — yetenek müzakeresini kontrol edin. İstem yeteneği beyan edilmiş ancak istem desteği olmayan bir istemci, slash komutlarını göremez.

### "Liste değişti" bildirimi

Hem kaynaklar hem de istemler, küme değiştiğinde `notifications/list_changed` üretir. 20 yeni not içeren bir notlar sunucusu `notifications/resources/list_changed` üretir; istemci eklemeleri almak için `resources/list`'i yeniden çağırır.

### İçerik türü kuralları

Metin için: `mimeType: "text/plain"`, `text/markdown`, `application/json`.
İkili için: `image/png`, `application/pdf`, artı `blob` alanı.
MCP Apps için (Ders 14): `ui://` URI'sinde `text/html;profile=mcp-app`.

### Dinamik kaynaklar

Bir kaynak URI'si statik bir dosyaya karşılık gelmek zorunda değildir. `notes://recent`, her okumada en son beş notu döndürebilir. `db://query/users/active` parametreli bir sorgu çalıştırabilir. Sunucu içeriği dinamik olarak hesaplamakta serbesttir.

Kural: istemci URI'ye göre önbellek yapabiliyorsa, URI kararlı olmalıdır. Hesaplama tek seferlikse, URI bir zaman damgası veya nonce içermelidir, böylece istemci önbelleği bozulmaz.

### Abonelik vs sorgulama (polling)

Abonelik yetenekli istemciler, `notifications/resources/updated` aracılığıyla sunucu itişini alır. Abonelik öncesi istemciler veya desteklemeyen ana programlar yeniden okuyarak sorgulama yapar. Her ikisi de teknik doküman uyumludur. Sunucu yetenek beyanı, istemcinin hangisini desteklediğini söyler.

Aboneliklerin maliyeti: sunucuda oturum başına durum (kim neye abone). Abone kümesini sınırlı tutun; bağlantısı kesilen istemciler zaman aşımına uğramalıdır.

### İstemler vs system promptlar

MCP'taki istemler system prompt değildir. Ana programın system prompt'u (kendi çalışma talimatları) ve MCP istemleri (kullanıcı tarafından çağrılan sunucu tarafından sağlanan şablonlar) yan yana yaşar. Davranışı düzgün bir istemci, asla bir sunucu isteminin kendi system prompt'unu override etmesine izin vermez; onları katmanlandırır.

## Kullan

`code/main.py`, Ders 07'deki notlar sunucusunu şunlarla genişletir:

- Not başına kaynaklar (`notes://note-1` vb.) `resources/subscribe` desteğiyle.
- Üç mesajlı bir şablona dönüştürülen bir `review_note` istemi.
- Bir not değiştirildiğinde `notifications/resources/updated` üreten bir dosya izleyici simülasyonu.
- Her zaman en son beş notu döndüren bir `notes://recent` dinamik kaynağı.

Demo'yu çalıştırarak tam akışı görün.

## Sun

Bu ders `outputs/skill-primitive-splitter.md` dosyasını üretir. Önerilen bir MCP sunucusu verildiğinde, beceri her yeteneği bir gerekçeyle araç / kaynak / istem olarak sınıflandırır.

## Alıştırmalar

1. `code/main.py`'i çalıştırın. Başlangıç kaynak listesini gözlemleyin, ardından bir not düzenlemesi tetikleyin ve `notifications/resources/updated` olayının ateşlendiğini doğrulayın.

2. Bir `resources/list_changed` üretici ekleyin: yeni bir not oluşturulduğunda, istemcilerin yeniden keşfetmesi için bildirimi gönderin.

3. Bir GitHub MCP sunucusu için üç istem tasarlayın: `summarize_pr`, `triage_issue`, `release_notes`. Her biri argüman şemalarıyla. İstem gövdesi ek düzenleme olmadan çalıştırılabilir olmalıdır.

4. Ders 07 sunucusundaki mevcut bir aracı alın ve bir araç olarak mı kalması gerektiğini yoksa bir kaynak artı araç çiftine mi bölünmesi gerektiğini sınıflandırın. Bir cümle ile gerekçelendirin.

5. Teknik dokümanın `server/resources` ve `server/prompts` bölümlerini okuyun. `resources/read`'deki nadiren doldurulan ancak teknik dokümanın desteklediği alanı belirleyin. İpucu: kaynak içeriğindeki `_meta`'ya bakın.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| Resource (Kaynak) | "Sunulan veri" | URI ile adreslenebilir, ana programın okuyabildiği içerik |
| Resource URI | "Veriye işaretçi" | Şema前三fixli tanımlayıcı (`file://`, `notes://` vb.) |
| `resources/subscribe` | "Değişiklikleri izle" | Belirli bir URI için istemci-katılımlı sunucu itişi |
| `notifications/resources/updated` | "Kaynak değişti" | Abone olunan kaynağın yeni içerik aldığını belirten sinyal |
| Resource template | "Parametreli URI" | Ana program seçicisi için tamamlama ipuçlarına sahip URI kalıbı |
| Prompt (İstem) | "Slash-komutu şablonu" | Argüman slotlarına sahip adlı çok mesajlı şablon |
| Prompt arguments | "Şablon girdileri" | Ana programın dönüştürmeden önce topladığı tipli parametreler |
| `prompts/get` | "Şablonu dönüştür" | Sunucu doldurulmuş mesaj listesini döndürür |
| Content block (İçerik bloğu) | "Tipli parça" | `{type: text \| image \| resource \| ui_resource}` |
| Slash-command UX | "Kullanıcı kısayolu" | Ana program istemleri `/` ile başlayan komutlar olarak sunar |

## İleri Okuma

- [MCP — Concepts: Resources](https://modelcontextprotocol.io/docs/concepts/resources) — kaynak URI'leri, abonelikler ve şablonlar
- [MCP — Concepts: Prompts](https://modelcontextprotocol.io/docs/concepts/prompts) — istem şablonları ve slash-komutu entegrasyonu
- [MCP — Server resources spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/resources) — eksiksiz `resources/*` mesaj referansı
- [MCP — Server prompts spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts) — eksiksiz `prompts/*` mesaj referansı
- [MCP — Protocol info site: resources](https://modelcontextprotocol.info/docs/concepts/resources/) — resmi belgeleri genişleten topluluk kılavuzu
