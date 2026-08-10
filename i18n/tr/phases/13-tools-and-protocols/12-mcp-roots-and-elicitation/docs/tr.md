# Kökler ve Yüklenme  Uçuş kapsamı ve uçuş ortasında kullanıcı girişleri

> Kötü kodlanmış yollar bir kullanıcı farklı bir projeyi açtığında kırılır. Kullanıcı yeterince belirtilmediğinde önceden doldurulmuş araç argümanları bozulur. Kökler sunucuyu kullanıcı kontrolü altında bulunan bir URI setiye bağlar; arama aracı çağrısının ortasında arama işlemleri durdurulur ve kullanıcıdan bir form veya URL üzerinden yapılandırılmış giriş istenebilir. İki müşteri ilkesi, ortak MCP başarısızlık modları için iki düzeltme. SEP-1036 (URL modunun çıkartılması, 2025-11-25) H1 2026  test SDK sürümleri üzerinden deneysel olarak kullanılır.

**Type:** Build
**Languages:** Python (stdlib, roots + elicitation demo)
**Prerequisites:** Phase 13 · 07 (MCP server)
**Time:** ~45 minutes

## Öğrenme Hedefleri

- İtiraf et .`roots`ve cevap ver .`notifications/roots/list_changed`- Evet .
- Sunucu dosya işlemlerini açıklanan kök kümesi içinde URI'lere sınırlandırın.
- Kullanım`elicitation/create`Kullanıcıya araç çağrısı sırasında bir onay veya yapılandırılmış giriş istemek.
- Form mod ve URL modunun oluşturulması arasında seçim yapın (sonuncu deneysel; sürükleme riski belirtilmiştir).

## Sorun

İki tane beton hata. MCP sunucusu üretim sırasında vuruldu.

**Broken path assumption.**Sunucu , `~/notes`. Farklı bir makine üzerinde notları olan bir kullanıcı `~/Documents/Notes`sessizce başarısız olan bir araç çağrısı alır (fayl bulunmaz) veya daha kötüsü, yanlış yere yazılır.

**Missing argument the user would know.**Kullanıcı "eski TPS rapor notunu sil" sorusunda model arar.`notes_delete(title: "TPS report")`Bu araç tahmin edemez. "Kahkaha açık" ile başarısız olmak sinir bozucu; üçü üzerinde çalışmak felaketli.

Kökler ilkini düzeltir: müşteri açıklamasını yapar `initialize`URI'lerin serveri dokunabilir. URI'lerin bir dizi. URI'lerin biriki serveri ayarlanır:`elicitation/create`Kullanıcıya hangisini seçmesini istemek için.

## Anlaşım

### Kökler

Müşteri bir kök listesini açıklar `initialize`- ...

```json
{
  "capabilities": {"roots": {"listChanged": true}}
}
```

Sunucu aramayabilir `roots/list`- ...

```json
{"roots": [{"uri": "file:///Users/alice/Documents/Notes", "name": "Notes"}]}
```

Sunucular kökleri sınır olarak değerlendirmelidir: köklü set dışında okunan veya yazılan herhangi bir dosya reddedilmektedir. Bu istemci tarafından uygulanmaz (sunucu hala kullanıcı güvendiği koddur), ancak spesifikasyonlara uygun sunucular bunu onurlandırır.

Kullanıcı bir kök eklediğinde veya kaldırdığında, istemci gönderir `notifications/roots/list_changed`- Sunucu tekrar arıyor .`roots/list`Ve sınırlarını güncelleyecek.

### Neden kökleri bir müşteri ilkel

Roots, kullanıcı'nın onay modelini temsil ettiği için istemci tarafından açıklanır. Kullanıcı Claude Desktop'a "bu not sunucusu bu iki dizine erişim sağlayın" dedi.

### Çözüm: Form modunun varsayılanı

`elicitation/create`bir form şeması ve doğal dil sorgulaması alır:

```json
{
  "method": "elicitation/create",
  "params": {
    "message": "Delete 'TPS report'? Multiple notes match; pick one.",
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

Müşteri bir form gönderir, kullanıcının cevabını toplar, gönderir:

```json
{
  "action": "accept",
  "content": {"note_id": "note-14", "confirm": true}
}
```

Üç olası eylem:`accept`(kullanıcı doldurmuş), `decline`(kullanıcı kapattı), `cancel`(kullanıcı tüm araç çağrısını iptal etti).

Form şemaları düz  yuvalanmış nesneler v1'de desteklenmez. SDK'lar tipik olarak tek katmandan daha karmaşık bir şeyi reddeder.

### Çözüm: URL modusu (SEP-1036, deneysel)

2025-11-25'te yeni.

```json
{
  "method": "elicitation/create",
  "params": {
    "message": "Sign in to GitHub",
    "url": "https://github.com/login/oauth/authorize?client_id=..."
  }
}
```

Müşteri bir tarayıcıda URL'yi açar, tamamlanmasını bekler, kullanıcı geri döndüğünde geri döner.

Sürükleme riski notu: SEP-1036 yanıt şekli hala ayarlanıyor; bazı SDK'lar geri çağrı URL'sini geri verir, bazıları tamamlama jetonunu geri verir.

### Eğer çıkarma doğru bir araçsa

- Yıkıcı eylemlerden önce kullanıcı onaylaması (yıkıcı ipucu + uyarma).
- Açıklama (N eşleşenlerden birini seçin).
- İlk çalıştırma ayarları (API anahtarları, dizinler, tercihler).
- OAuth tarzı akışları (URL modunda).

### Eğer bir şey yanlış olursa

- Modelin prozda isteyebileceği bir araç için gerekli argümanları doldurmak.
- Yüksek frekanslı aramalar.Konuşmayı kesmek için bir düğümün içinde çalıştırmayın.
- Server, gerçekten sonra doğrulayabilecek her şeyi doğrula, bir hata gönder, modelin kullanıcıya metinde sormasına izin ver.

### İnsan-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-

MCP'nin "insan döngüsü" modeli için birlikte örnekleme ve örnekleme imkanı sunar. Bir sunucu ajan döngüsü, kullanıcı giriş (dönüşleme) veya model mantıklaşması (dönüşleme) için duraklayabilir.

```figure
t3-roots-boundary
```

## Kullan

`code/main.py`Not sunucusunu genişletiyor:

- `roots/list`sunucu'nun root list değiştirilmiş bildirimlerden sonra tekrar sorduğu cevap.
- A.`notes_delete`kullanan araç`elicitation/create`Birden fazla not eşleşince anlaşılmazlık çıkarmak.
- A.`notes_setup`URL modunun oluşturulmasını kullanarak ilk çalıştırma yapılandırma sayfasını açan bir araç (simülasyon).
- Açıklanan köklerin dışında URI'lerde işlem yapmayı reddeden bir sınır kontrolü.

Demo üç senaryoyu içerir: mutlu yol (bir maç), belirsizlik (üç maç, tetikleme yangınları), kökten çıkmış yazma (reddedildi).

## Gönder

Bu ders bize çok yararlı .`outputs/skill-elicitation-form-designer.md`Kullanıcı onayına veya belirsizliğe ihtiyaç duyabilecek bir araç göz önüne alındığında, beceri başlatma formu şeması ve mesaj şablonu tasarlanır.

## Egzersizler

1. Çık .`code/main.py`. Açıklama yolu tetikle; simülasyonlu kullanıcı cevabının araçta geri yönlendirilmesini onaylayın.

2. Yeni bir araç ekle `notes_archive`UX'yi kontrol edin: bu, metinde tekrar soran modelle nasıl karşılaştırılır?

3. İlk kez OAuth akışı için URL modunun çıkartılmasını uygulayın. Drift riskini not edin ve SDK sürüm koruyucu ekleyin.

4. Uzaklaştırma`roots/list`İşlem: bir bildirim geldiğinde, sunucu, şimdi kullanılabilirliği dışındaki açık dosya elelerini atomik olarak yeniden okumalı ve yeniden taramalı.

5. GitHub'da SEP-1036 sorunu tartışma temesini okuyun.

## Anahtar Terimler

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Root | "Consent boundary" | URI the client has allowed the server to touch |
| `roots/list` | "Server asks for scope" | Client returns the current root set |
| `notifications/roots/list_changed` | "User changed scope" | Client signals the root set has mutated |
| Elicitation | "Ask the user mid-call" | Server-initiated request for structured user input |
| `elicitation/create` | "The method" | JSON-RPC method for elicitation requests |
| Form mode | "Schema-driven form" | Flat JSON Schema rendered as a form in the client UI |
| URL mode | "Browser redirect" | SEP-1036 experimental; opens a URL and waits |
| `accept` / `decline` / `cancel` | "User response outcomes" | Three branches the server handles |
| Disambiguation | "Pick one" | Common elicitation use case when a tool has N candidates |
| Flat form | "Top-level properties only" | Elicitation schemas cannot nest |

## Daha Fazla Okumak

- [MCP — Client roots spec](https://modelcontextprotocol.io/specification/draft/client/roots) Kanonik kök referansı
- [MCP — Client elicitation spec](https://modelcontextprotocol.io/specification/draft/client/elicitation) Kanonik kaynaklama referansı
- [Cisco — What's new in MCP elicitation, structured content, OAuth enhancements](https://blogs.cisco.com/developer/whats-new-in-mcp-elicitation-structured-content-and-oauth-enhancements) 2025-11-25 eklemeleri yürüyüş yolu
- [MCP — GitHub SEP-1036](https://github.com/modelcontextprotocol/modelcontextprotocol) URL modunda başlatma önerisi (deney, sürükleme riski)
- [The New Stack — How elicitation brings human-in-the-loop to AI tools](https://thenewstack.io/how-elicitation-in-mcp-brings-human-in-the-loop-to-ai-tools/) UX yürüyüş
