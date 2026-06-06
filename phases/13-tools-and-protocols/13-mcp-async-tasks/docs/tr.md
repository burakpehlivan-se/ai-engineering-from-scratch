# Asenkron Görevler (SEP-1686) — Şimdi Çağır, Sonra Getir: Uzun Süren Çalışmalar İçin

> Gerçek ajan çalışmaları dakikalardan saatlere kadar sürer: CI çalıştırmaları, derin araştırma sentezi, toplu dışa aktarımlar. Senkron araç çağriları bağlantıları düşürür, zaman aşımına uğrar veya UI'ı bloke eder. SEP-1686, 2025-11-25'te birleştirildi ve bir Görev (Task) primitifi ekler: herhangi bir istek bir göreve dönüştürülebilir ve sonuç daha sonra getirilebilir veya durum bildirimleri aracılığıyla akışı yapılabilir. Kayma riski notu: Görevler 2026'nın ilk yarısına kadar deneyseldir; SDK yüzeyi hala teknik dokümana göre tasarlanıyor.

**Tür:** İnşa Et
**Diller:** Python (stdlib, asenkron görev durum makinesi)
**Ön koşullar:** Faz 13 · 07 (MCP sunucusu), Faz 13 · 09 (taşıyıcılar)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Bir aracı senkrondan görev-artırılmışa ne zaman yükselteceğini belirle (>30 saniye sunucu tarafında çalışma).
- Görev yaşam döngüsünü yürü: `working` → `input_required` → `completed` / `failed` / `cancelled`.
- Görev durumunu kalıcı hale getir, böylece çökmeler çalışırken kaybolan çalışmayı kaybetmez.
- `tasks/status`'u doğru şekilde sorgula ve `tasks/result`'ı getir.

## Sorun

Bir `generate_report` aracı çok dakikalık bir çıkarma hattını çalıştırır. Senkron model altında seçenekler:

1. Bağlantıyı üç dakika boyunca açık tut. Uzak taşıyıcılar onu düşürür; istemciler zaman aşımına uğrar; UI'lar donar.
2. Hemen bir yer tutucuyla döndür; istemciden özel bir uç noktayı sorgulamasını iste. MCP birliğini bozar.
3. Gönder ve unut; sonuç yok.

Hiçbiri iyi değil. SEP-1686 dördüncü bir seçenek ekler: görev artırma. Herhangi bir istek (tipik olarak `tools/call`) bir görev olarak etiketlenebilir. Sunucu hemen bir görev id'si döndürür. İstemci `tasks/status`'u sorgular ve bittiğinde `tasks/result`'ı getirir. Sunucu tarafındaki durum yeniden başlatmalarda hayatta kalır.

## Kavram

### Görev artırma

Bir istek `params._meta.task.required: true` (veya `optional: true`, sunucu karar verir) ayarlanarak bir görev haline gelir. Sunucu hemen şununla yanıt verir:

```json
{
  "jsonrpc": "2.0", "id": 1,
  "result": {
    "_meta": {
      "task": {
        "id": "tsk_9f7b...",
        "state": "working",
        "ttl": 900000
      }
    }
  }
}
```

`ttl`, sunucunun durumu koruma sözüdür; ttl sonrasında görev sonucu atılır.

### Araç başına katılım

Araç eklemeleri (annotations) görev desteğini beyan edebilir:

- `taskSupport: "forbidden"` — bu araç her zaman senkron çalışır. Hızlı araçlar için güvenli.
- `taskSupport: "optional"` — istemci görev-artırma isteyebilir.
- `taskSupport: "required"` — istemci görev_artırmayı KULLANMALIDIR.

Bir `generate_report` aracı `required` olurdu. Bir `notes_search` aracı `forbidden` olurdu.

### Durumlar

```
working  -> input_required -> working  (ricada bulunma yoluyla döngü)
working  -> completed
working  -> failed
working  -> cancelled
```

Durum makinesi yalnızca eklemeli (append-only): `completed`, `failed` veya `cancelled` bir kez geçildiğinde görev sonludur.

### Metodlar

- `tasks/status {taskId}` — mevcut durumu ve bir ilerleme ipucu döndürür.
- `tasks/result {taskId}` — bloke eder veya henüz bitmemişse 404 döndürür.
- `tasks/cancel {taskId}` — idempotent; sonlu durumlar görmezden gelir.
- `tasks/list` — isteğe bağlı; aktif ve son tamamlanan görevleri listeler.

### Akışlı durum değişiklikleri

Sunucu desteklediğinde, istemci durum bildirimlerine abone olabilir:

```
sunucu -> notifications/tasks/updated {taskId, state, progress?}
```

Sorgulama yerine akış yapan istemciler daha iyi UX alır. Sorgulama her zaman minimum yüzey olarak desteklenir.

### Dayanıklı durum

Teknik doküman, görev desteğini beyan eden sunucuların durumu kalıcı hale getirmesini_buyurur. Bir çökme, ttl içindeki tamamlanmış sonuçları kaybetmemelidir. Depolama alanları SQLite'tan Redis'e ve dosya sistemine kadar çeşitlidir. Ders 13 donanımı dosya sistemini kullanır.

### İptal anlambilimi

`tasks/cancel` idempotent'tir. Görev çalışırken ise sunucu durdurmaya çalışır (çalıştırıcı-işbirlikçi iptal kontrolü). Zaten sonluysa istek bir no-op'dur.

### Çökme kurtarma

Sunucu süreci yeniden başladığında:

1. Tüm kalıcı görev durumlarını yükle.
2. Süreci ölen `working` görevlerini `failed` olarak işaretle, hata `CRASH_RECOVERY`.
3. `completed` / `failed` / `cancelled`'ı ttl boyunca koru.

### Asenkron görevler artı örnekleme

Bir görev kendi başına `sampling/createMessage` çağırabilir. Uzun süren araştırma görevleri böyle çalışır: sunucunun görev iş parçacığı gerektikçe istemcinin modelini örnekler, istemcinin UI'ı görevi periyodik ilerleme güncellemeleriyle `working` olarak gösterir.

### Bu neden deneysel

SEP-1686 2025-11-25'te yayınlandı ancak daha geniş yol haritası üç açık soruna işaret ediyor: dayanıklı abonelik primitifleri, alt görevler (ana-çocuk görev ilişkileri) ve sonuç-TTL standartlaştırma. Teknik dokümanın 2026 boyunca evrilmesini bekleyin. Üretim kodu, Görevleri yalnızca yaygın durum için kararlı olarak işlemeli ve alt görevler için gelecek SDK değişikliklerine karşı korumalıdır.

## Kullan

`code/main.py`, dayanıklı bir görev Deposu (dosya sistemi destekli) ve arka plan iş parçacığında çalışan bir `generate_report` aracı uygular. İstemciler aracı çağırır, hemen bir görev id'si alır, işçi ilerlemeyi güncellerken `tasks/status`'u sorgular ve bittiğinde `tasks/result`'ı getirir. İptal çalışır; çökme kurtarma, işçi iş parçacığını öldürerek ve durumu yeniden yükleyerek simüle edilir.

Neye bakılmalı:

- Görev durum JSON'u `/tmp/lesson-13-tasks/<id>.json`'a kalıcı olarak yazılır.
- İşçi iş parçacığı `progress` alanını günceller; sorgulama ilerlemeyi gösterir.
- İstemci tarafında iptal bir olay ayarlar; işçi kontrol eder ve erken çıkar.
- "Çökme" sonrası durum yeniden yüklemesi, uçuş halindeki görevi `CRASH_RECOVERY` ile `failed` olarak işaretler.

## Sun

Bu ders `outputs/skill-task-store-designer.md` dosyasını üretir. Uzun süren bir araç (araştırma, oluşturma, dışa aktarım) verildiğinde, beci görev deposunu tasarlar (durum şekli, ttl, dayanıklılık), doğru taskSupport bayrağını seçer ve ilerleme bildirimlerini çizer.

## Alıştırmalar

1. `code/main.py`'i çalıştırın. Bir `generate_report` görevi başlatın, durumu sorgulayın, ardından sonucu getirin.

2. Çalışma ortasında bir `tasks/cancel` çağrısı ekleyin. İşçinin buna saygı gösterdiğini ve durumun `cancelled` olduğunu doğrulayın.

3. Çökme kurtarmayı simüle edin: işçi iş parçacığını öldürün, yükleyiciyi yeniden başlatın ve `CRASH_RECOVERY` hata modunu gözlemleyin.

4. Depoyu SQLite'a genişletin. Dayanıklılık kazanımları aynı; sorgu seçenekleri açılır (X oturumundaki tüm görevleri listele).

5. MCP 2026 yol haritası yazısını okuyun. Bir sonraki yıl SDK API tasarımını en çok etkileyecek görevlerle ilgili açık soruyu belirleyin.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| Task (Görev) | "Uzun süren araç çağrısı" | Asenkron çalıştırmaya artırılmış `_meta.task` ile istek |
| SEP-1686 | "Görevler teknik dokümanı" | 2025-11-25'te Görevleri ekleyen Teknik Doküman Geliştirme Önerisi |
| `_meta.task` | "Görev zarfı" | İstek başına id, durum, ttl içeren meta veri |
| taskSupport | "Araç bayrağı" | Araç başına `forbidden` / `optional` / `required` |
| `tasks/status` | "Sorgulama metodu" | Mevcut durumu ve isteğe bağlı ilerleme ipucunu getirir |
| `tasks/result` | "Sonucu getir" | Tamamlanmış yükü döndürür veya henüz bitmemişse 404 |
| `tasks/cancel` | "Durdur" | İptal isteği idempotent |
| ttl | "Koruma bütçesi" | Sunucunun görev durumunu tutmayı söz verdiği milisaniye |
| `notifications/tasks/updated` | "Durum itişi" | Sunucu tarafından başlatılan durum değişikliği olayı |
| Durable store | "Çökme-güvenli durum" / | Dosya sistemi / SQLite / Redis kalıcılık katmanı |

## İleri Okuma

- [MCP — GitHub SEP-1686 issue](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1686) — orijinal öneri ve tam tartışma
- [WorkOS — MCP async tasks for AI agent workflows](https://workos.com/blog/mcp-async-tasks-ai-agent-workflows) — gerekçeyle tasarım yürüyüşü
- [DeepWiki — MCP task system and async operations](https://deepwiki.com/modelcontextprotocol/modelcontextprotocol/2.7-task-system-and-async-operations) — mekanikalar ve durum makinesi
- [FastMCP — Tasks](https://gofastmcp.com/servers/tasks) — SDK düzeyinde görev uygulama paternleri
- [MCP blog — 2026 roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) — alt görevler dahil açık sorular ve 2026 öncelikleri
