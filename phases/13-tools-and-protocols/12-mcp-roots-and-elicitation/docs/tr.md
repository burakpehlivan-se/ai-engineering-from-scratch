# Kökler ve Ricada Bulunma — Kapsam Belirleme ve Ortal Uçuşta Kullanıcı Girdisi

> Kodlanmış yollar, bir kullanıcı farklı bir proje açtığında kırılır. Önceden doldurulmuş araç argümanları, kullanıcı eksik bilgi verdiğinde kırılır. Kökler (roots), sunucuyu kullanıcı tarafından kontrol edilen bir URI kümesine kısıtlar; ricada bulunma (elicitation), orta araç çağrısında kullanıcıya bir form veya URL aracılığıyla yapılandırılmış girdi sormak için duraklar. İki istemci primitifi, yaygın MCP hata modları için iki düzeltme. SEP-1036 (URL modu ricada bulunma, 2025-11-25) 2026'nın ilk yarısına kadar deneyseldir — bunun üzerine inşa etmeden önce SDK sürümlerini kontrol edin.

**Tür:** İnşa Et
**Diller:** Python (stdlib, kökler + ricada bulunma demosu)
**Ön koşullar:** Faz 13 · 07 (MCP sunucusu)
**Süre:** ~45 dakika

## Öğrenme Hedefleri

- `roots`'u beyan et ve `notifications/roots/list_changed`'a yanıt ver.
- Sunucu dosya işlemlerini beyan edilen kök kümesinin içindeki URI'lerle kısıtla.
- Bir araç çağrısında kullanıcıdan onay veya yapılandırılmış girdi sormak için `elicitation/create`'i kullan.
- Form modu ile URL modu ricada bulunma arasında seçim yap (sonuncu deneyseldir; kayma riski not edilmiş).

## Sorun

Bir notlar MCP sunucusunun üretimde karşılaştığı iki somut hata.

**Bozulan yol varsayımı.** Sunucu `~/notes`'e karşı yazılmış. `~/Documents/Notes`'de notları olan farklı bir makinedeki kullanıcı, sessizce başarısız olan (dosya bulunamadı) veya daha da kötüsü yanlış yere yazan bir araç çağrısı alır.

**Kullanıcının bileceği eksik argüman.** Kullanıcı "eski TPS raporu notunu sil" diyor. Model `notes_delete(title: "TPS report")` çağırıyor ancak 2023, 2024 ve 2025'ten üç eşleşen not var. Araç tahmin edemez. "Belirsiz" hatası sinir bozucu; üçü üzerinde çalışmak ise felaket.

Köklere ilkini düzeltir: istemci `initialize`'da sunucunun dokunabileceği URI kümesini beyan eder. Ricada bulunma ikincini düzeltir: sunucu araç çağrısını duraklatır ve kullanıcının hangisini seçeceğini sormak için `elicitation/create` gönderir.

## Kavram

### Kökler

İstemci `initialize`'da bir kök listesi beyan eder:

```json
{
 "capabilities": {"roots": {"listChanged": true}}
}
```

Sunucu ardından `roots/list` çağırabilir:

```json
{"roots": [{"uri": "file:///Users/alice/Documents/Notes", "name": "Notes"}]}
```

Sunucular kökleri SINIR olarak ele almalıdır: kök kümesinin dışındaki herhangi bir dosya okuması veya yazması reddedilir. Bu istemci tarafından zorlanmaz (sunucu hala kullanıcının güvendiği koddur) ancak teknik doküman uyumlu sunucular buna saygı gösterir.

Kullanıcı bir kök eklediğinde veya kaldırdığında, istemci `notifications/roots/list_changed` gönderir. Sunucu `roots/list`'i yeniden çağırır ve sınırını günceller.

### Kökler neden bir istemci primitifi

Köller, kullanıcı rızası modelini temsil ettikleri için istemci tarafından beyan edilir. Kullanıcı Claude Desktop'a "bu notlar sunucusuna bu iki dizine erişim ver" dedi. Sunucu bu kapsamı genişletemez.

### Ricada bulunma: form modu varsayılanı

`elicitation/create`, bir form şeması artı doğal dil istemi alır:

```json
{
 "method": "elicitation/create",
 "params": {
 "message": "'TPS raporu' silinsin mi? Birden fazla not eşleşiyor; birini seçin.",
 "requestedSchema": {
 "type": "object",
 "properties": {
 "note_id": {
 "type": "string",
 "enum": ["note-3", "note-7", "note-14"]
 },
 "confirm": {"type": "boolean"}
 },
 "required": ["note_id", "confirm"]
 }
 }
}
```

İstemci bir form oluşturur, kullanıcının yanıtını toplar, döndürür:

```json
{
 "action": "accept",
 "content": {"note_id": "note-14", "confirm": true}
}
```

Üç olası eylem: `accept` (kullanıcı doldurdu), `decline` (kullanıcı kapattı), `cancel` (kullanıcı tüm araç çağrısını iptal etti).

Form şemaları düzdür — v1'de iç içe nesneler desteklenmez. SDK'lar genellikle tek katmandan daha karmaşık her şeyi reddeder.

### Ricada bulunma: URL modu (SEP-1036, deneysel)

2025-11-25'te yeni. Şema yerine sunucu bir URL gönderir:

```json
{
 "method": "elicitation/create",
 "params": {
 "message": "GitHub'a giriş yapın",
 "url": "https://github.com/login/oauth/authorize?client_id=..."
 }
}
```

İstemci URL'yi tarayıcıda açar, tamamlanmasını bekler, kullanıcı döndüğünde döner. OAuth akışları, ödeme yetkilendirmeleri ve formun yetersiz kaldığı belge imzalama için kullanışlıdır.

Kayma riski notu: SEP-1036 yanıt şekli hala yerleşiyor; bazı SDK'lar geri çağırma URL'sini döndürür, diğerleri bir tamamlama jetonu döndürür. URL modunu üretmeden önce SDK'nızın sürüm notlarını okuyun.

### Ricada bulunma ne zaman doğru araç

- Sonuçlu eylemler öncesi kullanıcı onayı (sonuçlu ipucu + ricada bulunma).
- Ayrıştırma (N eşleşmeden birini seçme).
- İlk çalıştırma kurulumu (API anahtarları, dizinler, tercihler).
- OAuth tarzı akışlar (URL modu).

### Ricada bulunma ne zaman yanlış

- Aracın gerekli argümanlarını doldurmak, modelin metinle sorabileceği. Normal bir yeniden isteme (re-prompt) kullanın, ricada bulunma dialogu değil.
- Yüksek frekanslı çağrılar. Ricada bulunma konuşmayı kesintiye uğratır; döngü içinde tetiklemeyin.
- Sunucunun sonradan doğrulayabileceği her şey. Doğrulayın, bir hata döndürün, modelin kullanıcıya metinle sormasına izin verin.

### İnsan döngüde köprüsü

Ricada bulunma artı örnekleme, MCP'nin "insan döngüde" modelini birlikte etkinleştirir. Bir sunucunun ajan döngüsü, ya kullanıcı girdisi (ricada bulunma) ya da model akıl yürütmek için (örnekleme) duraklayabilir. Faz 13 · 11 örnelemeyi kapsadı; bu ders ricada bulunmayı kapsar. Tam orta döngü kontrolü için birleştirin.

## Kullan

`code/main.py`, notlar sunucusunu şunlarla genişletir:

- Kök-listesi-değişikliği bildirimlerinden sonra sunucunun sorguladığı `roots/list` yanıtı.
- Birden fazla not eşleştiğinde ayrıştırma için `elicitation/create` kullanan `notes_delete` aracı.
- İlk çalıştırma yapılandırma sayfasını açmak için URL modu ricada bulunma kullanan `notes_setup` aracı (simüle edilmiş).
- Beyan edilen köklerin dışındaki URI'lerdeki işlemleri reddeden bir sınır kontrolü.

Demo üç senaryo çalıştırır: mutlu yol (tek eşleşme), ayrıştırma (üç eşleşme, ricada bulunma tetiklenir), kök-dışına-yazma (reddedildi).

## Sun

Bu ders `outputs/skill-elicitation-form-designer.md` dosyasını üretir. Kullanıcı onayı veya ayrıştırma gerektirebilen bir araç verildiğinde, beceri ricada bulunma formu şemasını ve mesaj şablonunu tasarlar.

## Alıştırmalar

1. `code/main.py`'i çalıştırın. Ayrıştırma yolunu tetikleyin; simüle edilmiş kullanıcı yanıtının araca geri yönlendirildiğini doğrulayın.

2. Her seferinde ricada bulunma onayı gerektiren yeni bir `notes_archive` aracı ekleyin (sonuçlu ipucu). UX'i kontrol edin: bu, modelin metinle yeniden sormasıyla nasıl karşılaştırılır?

3. İlk çalıştırma OAuth akışı için URL modu ricada bulunmayı uygulayın. Kayma riskini not edin ve bir SDK-sürüm koruması ekleyin.

4. `roots/list` elemini genişletin: bir bildirim geldiğinde, sunucu artık kapsam dışı olabilecek açık dosya saplarını atomik olarak yeniden okumalı ve yeniden taramalıdır.

5. GitHub'daki SEP-1036 soru tartışma dizisini okuyun. Sunucuların URL modu geri çağırmalarını nasıl ele almasını etkileyen bir açık soru belirleyin.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| Root (Kök) | "Rıza sınırı" | İstemcinin sunucunun dokunmasına izin verdiği URI |
| `roots/list` | "Sunucu kapsam ister" | İstemci mevcut kök kümesini döndürür |
| `notifications/roots/list_changed` | "Kullanıcı kapsamı değiştirdi" | İstemci kök kümesinin değiştiğini belirtir |
| Elicitation (Ricada bulunma) | "Çağrı ortasında kullanıcıya sor" | Sunucu tarafından başlatılan yapılandırılmış kullanıcı girdisi isteği |
| `elicitation/create` | "Metod" | Ricada bulunma istekleri için JSON-RPC metodu |
| Form mode | "Şema-driven form" | İstemci UI'ında form olarak oluşturulan düz JSON Şeması |
| URL mode | "Tarayıcı yönlendirmesi" | SEP-1036 deneysel; bir URL açar ve bekler |
| `accept` / `decline` / `cancel` | "Kullanıcı yanıt sonuçları" | Sunucunun ele aldığı üç dal |
| Disambiguation (Ayrıştırma) | "Birini seç" | Bir aracın N adayı olduğu yaygın ricada bulunma kullanım durumu |
| Flat form | "Yalnızca üst düzey özellikler" | Ricada bulunma şemaları iç içe geçemez |

## İleri Okuma

- [MCP — Client roots spec](https://modelcontextprotocol.io/specification/draft/client/roots) — kanonik kökler referansı
- [MCP — Client elicitation spec](https://modelcontextprotocol.io/specification/draft/client/elicitation) — kanonik ricada bulunma referansı
- [Cisco — What's new in MCP elicitation, structured content, OAuth enhancements](https://blogs.cisco.com/developer/whats-new-in-mcp-elicitation-structured-content-and-oauth-enhancements) — 2025-11-25 eklemelerinin yürüyüşü
- [MCP — GitHub SEP-1036](https://github.com/modelcontextprotocol/modelcontextprotocol) — URL modu ricada bulunma önerisi (deneysel, kayma riski)
- [The New Stack — How elicitation brings human-in-the-loop to AI tools](https://thenewstack.io/how-elicitation-in-mcp-brings-human-in-the-loop-to-ai-tools/) — UX yürüyüşü
