# Async Görevleri (SEP-1686)  Uzun süreli iş için şimdi arayın, sonra getirin

> Gerçek ajan işi saatlerce dakikalar alır: bilgi bilgisine çalışmalar, derin araştırma sentezi, parti ihracatı. Senkroni araç bağlantıları bırakır, zaman keser veya kullanıcı arayüzünü engeller. 2025-11-25'te birleşmiş SEP-1686, bir Görev primitif ekler: Herhangi bir talebi bir görev haline getirmek için artırılabilir ve sonuç daha sonra alınır veya devlet bildirimleri üzerinden akışlanabilir. Drift risk notu: Görevler H1 2026'da deneysel olarak yürütülmektedir; SDK yüzeyleri hala spesifikasyon etrafında tasarlanmaktadır.

**Type:** Build
**Languages:** Python (stdlib, async task state machine)
**Prerequisites:** Phase 13 · 07 (MCP server), Phase 13 · 09 (transports)
**Time:** ~75 minutes

## Öğrenme Hedefleri

- Bir aracı senkronizme görevi arttırılmış bir araçtan (> 30 saniye sunucu tarafında çalışmak) ne zaman teşvik edileceğini belirleyin.
- Görev yaşam döngüsünü izleyin: `working`→ `input_required`→ `completed`- Ne ?`failed`- Ne ?`cancelled`- Evet .
- Görev durumunu sürdürün, böylece kazalar uçuş sırasında iş kaybı olmaz.
- Anket`tasks/status`Ve getir .`tasks/result`Doğru.

## Sorun

A.`generate_report`Araç, birkaç dakikalık bir çıkarma borusunu çalışır.

1. Uzak nakliye sistemi kapatır, müşteri çıkartır, kullanıcı araları dondurulur.
2. Hemen bir yer tutma ile geri dönün. Müşteriyi özel bir son noktaya sorgulamasını istesin.
3. Ateş ve unutma; sonuç yok.

SEP-1686 dördüncü bir görev ekliyor: görev artışı.`tools/call`) bir görev olarak etiketlenir.Server bir görev kimliğini hemen gönderir.Müşteri anketleri `tasks/status`Ve getirir.`tasks/result`Server tarafı durum yeniden başlatılmadan sağ kalır.

## Anlaşım

### Görev artışı

Bir istek, belirleyerek bir görev haline gelir.`params._meta.task.required: true`(veya `optional: true`Sunucu hemen cevap verir:

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

`ttl`TTL'den sonra görev sonucu atılır.

### Araç başına seçme

Araç açıklamaları görev desteğini açıklayabilir:

- `taskSupport: "forbidden"` bu araç her zaman senkroni çalışmaktadır.
- `taskSupport: "optional"` Müşteri görev artışını isteyebilir.
- `taskSupport: "required"` müşteri görev artırmasını kullanmalıdır.

A.`generate_report`Araç olabilir.`required`- A.`notes_search`Araç olabilir.`forbidden`- Evet .

### Devletler

```
working  -> input_required -> working  (loop via elicitation)
working  -> completed
working  -> failed
working  -> cancelled
```

Devlet makinesinin sadece eklenmesi: bir kez `completed`- Evet .`failed`veya`cancelled`, görev terminal.

### Metotlar

- `tasks/status {taskId}` mevcut durum ve ilerleme ipucu gönderir.
- `tasks/result {taskId}` henüz yapılmamışsa 404'i engeller veya gönderir.
- `tasks/cancel {taskId}` idempotent; terminal devletler ihmal eder.
- `tasks/list` seçmeli; aktif ve son bitirilmiş görevleri listeliyor.

### Akış durum değişikliği

Sunucu desteklediğinde, müşteri devlete bildirimlere abone olabilir:

```
server -> notifications/tasks/updated {taskId, state, progress?}
```

Anket yerine akış yapan müşteriler daha iyi bir deneyim kazanırlar. Anketler her zaman en az yüzeyin olarak desteklenir.

### Kalıcı durum

Spec, görev desteğini sürdürmek için açıklayan sunucuların durumunu sürdürmesini gerektirir. Bir çöküş ttl içinde tamamlanmış sonuçları kaybetmemelidir. Kaynaklar SQLite'den Redis'e kadar dosya sistemine kadar uzanır. Ders 13 kullanımı dosya sistemini kullanır.

### İptal semantikası

`tasks/cancel`Eğer görev idempotent ise, sunucu durdurmaya çalışır (işleştirici-kooperatif iptal kontrolü).

### Kaza kurtarma

Sunucu süreci yeniden başlatıldığında:

1. Tüm devamlı görev durumlarını yükle.
2. Birini işaretle .`working`Bu süreçler son bulmuştur.`failed`Hata ile`CRASH_RECOVERY`- Evet .
3. Koruyun .`completed`- Ne ?`failed`- Ne ?`cancelled`- Bu yüzden.

### Asynk görevleri ve örnekleme

Bir görev kendi kendine çağırabilir.`sampling/createMessage`. Uzun süreli araştırma görevleri böyle çalışır: sunucu'nun görev dizisi, istemcinin modelini gerektiği gibi örnekler alırken istemcinin UI'si görevi `working`Devamlı gelişmelerle ilgili güncelleştirmelerle.

### Bu neden deneysel?

SEP-1686 2025-11-25'te gönderildi ancak daha geniş yol haritası üç açık konuyu ortaya koydu: dayanıklı abonelik ilkleri, alt görevler (ana-öğren görev ilişkileri) ve sonuç-TTL standartlaştırma.

```figure
tp-task-lifecycle
```

## Kullan

`code/main.py`Dayanıklı bir görev depoyu (dosya sistemi desteklenmiş) ve bir `generate_report`Kullanıcılar aracı arayıp, hemen bir görev kimliği alırlar, anket yaparlar.`tasks/status`İşçi ilerlemeyi güncelleyecekken, ve getir `tasks/result`İptal işlevleri; kaza kurtarma işçi ipini öldürerek ve yeniden yükleme durumunu simüle eder.

Neye bakılır:

- Görev durumu JSON devam etti `/tmp/lesson-13-tasks/<id>.json`- Evet .
- İşçi dalgası güncellemeleri `progress`Toplantı alanı; anket ilerlediğini gösteriyor.
- Müşteri tarafından iptal bir etkinlik belirler; işçi erken kontrol eder ve ayrılır.
- "Kraş"ın devleti yeniden yüklenmesi uçuş sırasında görevleri işaret eder.`failed`- Evet .`CRASH_RECOVERY`- Evet .

## Gönder

Bu ders bize çok yararlı .`outputs/skill-task-store-designer.md`. Uzun zamandır kullanılmış bir araç ( araştırma, inşa, ihracat) göz önüne alındığında, becerik görev depolarını (sazlık şekli, ttl, dayanıklılık) tasarlar, doğru görevyi seçer Destek bayrağı ve ilerleme bildirimlerini çizer.

## Egzersizler

1. Çık .`code/main.py`- Bir atış yap .`generate_report`Görev, oylama durumu, sonra sonuçları getir.

2. Bir ekle`tasks/cancel`İşçiyi onurlandırıp devletin...`cancelled`- Evet .

3. Çarpışma kurtarma simülasyonu: işçi ipini öldür, yükleme cihazını yeniden başlat ve `CRASH_RECOVERY`Başarısızlık modusu.

4. Bulguyu SQLite'e uzatın. Süreklilik kazancı aynıdır; sorgu seçenekleri açılır (Sessiyon X'den tüm görevleri listelenir).

5. 2026 için MCP yol haritası yazısını okuyun.

## Anahtar Terimler

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Task | "Long-running tool call" | Request augmented with `_meta.task` for async execution |
| SEP-1686 | "Tasks spec" | Spec Evolution Proposal that added Tasks in 2025-11-25 |
| `_meta.task` | "Task envelope" | Per-request metadata containing id, state, ttl |
| taskSupport | "Tool flag" | `forbidden` / `optional` / `required` per tool |
| `tasks/status` | "Poll method" | Fetch current state and optional progress hint |
| `tasks/result` | "Fetch result" | Returns the completed payload or 404 if not yet done |
| `tasks/cancel` | "Stop it" | Idempotent cancellation request |
| ttl | "Retention budget" | Milliseconds the server promises to keep the task state |
| `notifications/tasks/updated` | "State push" | Server-initiated state-change event |
| Durable store | "Crash-safe state" | Filesystem / SQLite / Redis persistence layer |

## Daha Fazla Okumak

- [MCP — GitHub SEP-1686 issue](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1686) Başlangıç önerisi ve tam tartışma
- [WorkOS — MCP async tasks for AI agent workflows](https://workos.com/blog/mcp-async-tasks-ai-agent-workflows) Dolayısıyla tasarım yürüyüşü
- [DeepWiki — MCP task system and async operations](https://deepwiki.com/modelcontextprotocol/modelcontextprotocol/2.7-task-system-and-async-operations) mekanik ve devlet makinesi
- [FastMCP — Tasks](https://gofastmcp.com/servers/tasks) SDK düzeyinde görevlerin uygulanması kalıpları
- [MCP blog — 2026 roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) Açık konular ve alt görevler dahil olmak üzere 2026 öncelikleri
