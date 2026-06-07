# A2A — Ajanlar Arası Protokol

> MCP ajanla araç arasındadır. A2A (Agent2Agent) ajanla ajan arasındadır — farklı çerçeveler üzerine inşa edilmiş opak ajanların işbirliği yapmasını sağlayan açık bir protokol. Google tarafından Nisan 2025'te yayınlandı, Haziran 2025'te Linux Foundation'a bağışlandı, Nisan 2026'da AWS, Cisco, Microsoft, Salesforce, SAP ve ServiceNow dahil 150'den fazla destekçiyle v1.0'a ulaştı. IBM'in ACP'sini emdi ve AP2 ödeme eklentisini ekledi. Bu ders Agent Card'ı, Görev yaşam döngüsünü ve iki taşıma bağlamasını yürüyerek gösterir.

**Tür:** İnşa Et
**Diller:** Python (stdlib, Agent Card + Görev donanımı)
**Ön koşullar:** Faz 13 · 06 (MCP temelleri), Faz 13 · 08 (MCP istemcisi)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Ajanla araç (MCP) ile ajanla ajan (A2A) kullanım durumlarını ayırt et.
- Yetenekler ve uç noktası meta verileriyle `/.well-known/agent.json`'da bir Agent Card yayımla.
- Görev yaşam döngüsünü yürü (submitted → working → input-required → completed / failed / canceled / rejected).
- Metin, dosya, veri içeren Parçalarla (Parts) Mesajları ve çıktı olarak Yapıtları (Artifacts) kullan.

## Sorun

Bir müşteri hizmetleri ajanının, özel bir yazan ajana rapor yazma görevini devretmesi gerekir. A2A öncesi seçenekler:

- Özel REST API. Çalışır ancak her eşleştirme bir kereliğine yapılı.
- Ortak kod tabanı. İki ajanın aynı çerçeveyi çalıştırmasını gerektirir.
- MCP. Uymaz: MCP araçları çağırmak içindir, iki ajanın her birinin opak iç akıl yürütmelerini koruyarak işbirliği yapması için değil.

A2A boşluğu doldurur. Etkileşimi, bir ajanın diğerine bir Görev göndermesi olarak modeller, bir yaşam döngüsü, mesajlar ve yapıtlarla. Çağrılan ajanın iç durumu opak kalır — çağıran yalnızca görev durum geçişlerini ve sonunda çıkanları görür.

A2A, "çerçeveler arası ajanların birbirleriyle konuşmasını sağlayan" protokoldür. MCP'yi değiştirmez; ikisi tamamlayıcıdır.

## Kavram

### Agent Card

Her A2A uyumlu ajan `/.well-known/agent.json`'da bir kart yayınlar:

```json
{
 "schemaVersion": "1.0",
 "name": "research-agent",
 "description": "Akademik makaleleri özetler ve alıntılar taslağı çıkarır.",
 "url": "https://research.example.com/a2a",
 "version": "1.2.0",
 "skills": [
 {
 "id": "summarize_paper",
 "name": "Makaleyi özetle",
 "description": "Bir makale PDF'ini okuyun ve 3 paragraflık bir özet üretin.",
 "inputModes": ["text", "file"],
 "outputModes": ["text", "artifact"]
 }
 ],
 "capabilities": {"streaming": true, "pushNotifications": true}
}
```

Keşif URL tabanlıdır: kartı çekin, A2A uç noktasının URL'sini öğrenin, yetenekleri listeleyin.

### İmzalanmış Agent Card'lar (AP2)

AP2 eklentisi (Eylül 2025) Agent Card'lara kriptografik imzalar ekler. Bir yayıncı kendi kartını bir JWT ile imzalar; tüketiciler doğrular. Taklidi önler.

### Görev yaşam döngüsü

```
submitted -> working -> completed | failed | canceled | rejected
 -> input_required -> working (mesaj yoluyla döngü)
```

İstemciler `tasks/send` ile başlatır. Çağrılan ajan durumlar arasında geçiş yapar; istemciler SSE veya sorgulama yoluyla durum güncellemelerine abone olur.

### Mesajlar ve Parçalar

Bir mesaj bir veya daha fazla Parça (Part) taşır:

- `text` — düz içerik.
- `file` — mimeType ile base64 blob.
- `data` — tipli JSON yükü (çağrılan ajan için yapılandırılmış girdi).

Örnek:

```json
{
 "role": "user",
 "parts": [
 {"type": "text", "text": "Bu makaleyi özetle."},
 {"type": "file", "file": {"name": "paper.pdf", "mimeType": "application/pdf", "bytes": "..."}},
 {"type": "data", "data": {"targetLength": "3 paragraf"}}
 ]
}
```

### Yapıtlar (Artifacts)

Çıktılar Yapıtlardır, çıplak stringler değildir. Bir Yapı, adlı, tipli bir çıktıdır:

```json
{
 "name": "summary",
 "parts": [{"type": "text", "text": "..."}],
 "mimeType": "text/markdown"
}
```

Yapıtlar parçacıklar olarak akış (streaming) yapılabilir. Çağırıcı biriktirir.

### İki taşıma bağlaması

1. **HTTP üzerinden JSON-RPC.** `/a2a` uç noktası, istekler için POST, akış için isteğe bağlı SSE. Varsayılan bağlama.
2. **gRPC.** gRPC'nin doğal olduğu kurumsal ortamlar için.

Her iki bağlama aynı mantıksal mesaj şeklini taşır.

### Opaklık korunması

Temel bir tasarım ilkesi: çağrılan ajanın iç durumu opaktır. Çağırıcı görev durumunu ve yapıtları görür. Çağrılan ajanın düş zinciri, araç çağrıları, alt ajan devretmeleri — hepsi görünmez. Bu, araç çağrısının saydam olduğu MCP'den farklıdır.

Gerekçe: A2A, rakiplerin içlerini ifşa etmeden işbirliği yapmasını sağlar. A2A "bu müşteri hizmetleri ajanını çağır" olabilir, çağıran o ajanın hizmeti nasıl uyguladığını öğrenmeden.

### Zaman çizelgesi

- **2025-04-09.** Google A2A'yı duyurdu.
- **2025-06-23.** Linux Foundation'a bağışlandı.
- **2025-08.** IBM'in ACP'sini emdi.
- **2025-09.** AP2 eklentisi (Ajan Ödemeleri) yayınlandı.
- **2026-04.** 150+ destekleyen kuruluşla v1.0 yayınlandı.

### MCP ile ilişki

| Boyut | MCP | A2A |
|-----------|-----|-----|
| Kullanım durumu | Ajanla araç | Ajanla ajan |
| Opaklık | Saydam araç çağrıları | Opak iç akıl yürütme |
| Tipik çağıran | Ajan çalışma zamanı | Başka bir ajan |
| Durum | Araç çağrısı sonucu | Yaşam döngüsüne sahip görev |
| Yetkilendirme | OAuth 2.1 (Faz 13 · 16) | JWT-imzalanmış Agent Card'lar (AP2) |
| Taşıma | Stdio / Streamable HTTP | HTTP üzerinden JSON-RPC / gRPC |

Belirli bir aracı çağırmak istediğinizde MCP kullanın. Tüm bir görevi başka bir ajana devretmek istediğinizde A2A kullanın. Birçok üretim sistemi her ikisini de kullanır: bir ajan araç katmanı için MCP, işbirliği katmanı için A2A kullanır.

## Kullan

`code/main.py`, minimal bir A2A donanımı uygular: bir araştırma ajanı kartını yayınlar, bir yazan ajan PDF ve metin talimatı içeren parçalarla bir `tasks/send` alır, working → input_required → working → completed geçişleri yapar ve bir metin yapıtı döndürür. Tümü stdlib; mesaj şekillerine odaklanmak için bellek içi taşıma kullanır.

Neye bakılmalı:

- Agent Card JSON şekli.
- Görev id atama ve durum geçişleri.
- Karışık tipli parçalara sahip Mesajlar.
- Görev ortasında input-required kolu.
- Tamamlamada Yapı dönüşü.

## Sun

Bu ders `outputs/skill-a2a-agent-spec.md` dosyasını üretir. Diğer ajanlar tarafından çağrılabilmesi gereken yeni bir ajan verildiğinde, beceri Agent Card JSON'unu, yetenekler şemasını ve uç noktası planını üretir.

## Alıştırmalar

1. `code/main.py`'i çalıştırın. Çağrılan ajanın netleştirme istediği input-required duraklaması dahil tam Görev yaşam döngüsünü izleyin.

2. İmzalanmış bir Agent Card ekleyin. HMAC ile kartın kanonik JSON'unu imzalayın. Bir doğrulayıcı yazın ve değişmiş bir kartta başarısız olduğunu doğrulayın.

3. Görev akışını (streaming) uygulayın: yazan ajan SSE üzerinden üç kademeli yapıt parçacığı üretir ve çağırıcı bunları biriktirir.

4. Bir MCP sunucusunu saran bir A2A ajanı tasarlayın. Her MCP aracını bir A2A yeteneğine eşleyin. Fedakarlıkları not edin — hangi opaklık kaybolur?

5. A2A v1.0 duyurusunu okuyun ve Nisan 2026 itibarıyla herhangi bir çerçeve tarafından henüz uygulanmamış bir özelliği belirleyin. (İpucu: çoklu atlama görev devretmesiyle ilgili.)

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| A2A | "Ajanlar Arası protokol" | Opak ajan işbirliği için açık protokol |
| Agent Card | "`.well-known/agent.json`" | Bir ajanın yeteneklerini ve uç noktasını tanımlayan yayımlanmış meta veri |
| Skill (Yetenek) | "Çağrılabilir birim" | Aracın desteklediği adlı bir işlem (MCP aracına benzer) |
| Task (Görev) | "Devretme ünitesi" | Yaşam döngüsüne ve son yapıta sahip bir çalışma kalemi |
| Message (Mesaj) | "Görev girdisi" | Parçaları (text, file, data) taşır |
| Part (Parça) | "Tipli parça" | Bir mesajın `text` / `file` / `data` elemanı |
| Artifact (Yapıt) | "Görev çıktısı" | Tamamlamada döndürülen adlı, tipli çıktı |
| AP2 | "Ajan Ödeme Protokolü" | Güven ve ödemeler için imzalanmış Agent Card eklentisi |
| Opaklık | "Kutu işbirliği" | Çağrılan ajanın içleri çağırandan gizlenir |
| Input-required | "Görev duraklaması" | Ajanın daha fazla bilgiye ihtiyaç duyduğu yaşam döngüsü durumu |

## İleri Okuma

- [a2a-protocol.org](https://a2a-protocol.org/latest/) — kanonik A2A teknik dokümanı
- [a2aproject/A2A — GitHub](https://github.com/a2aproject/A2A) — referans uygulamalar ve SDK'lar
- [Linux Foundation — A2A launch press release](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents) — Haziran 2025 yönetim devri
- [Google Cloud — A2A protocol upgrade](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade) — yol haritası ve ortak ivmesi
- [Google Dev — A2A 1.0 milestone](https://discuss.google.dev/t/the-a2a-1-0-milestone-ensuring-and-testing-backward-compatibility/352258) — v1.0 sürüm notları ve geriye uyumluluk rehberliği
