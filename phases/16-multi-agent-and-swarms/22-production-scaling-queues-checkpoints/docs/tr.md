# Üretim Ölçekleme — Kuyruklar, Kontrol Noktaları, Dayanıklılık

> Multi-agent sistemlerini binlerce eşzamanlı koşuya ölçeklemek **dayanıklı yürütme (durable execution)** gerektirir. LangGraph'ın çalışma zamanı, her süper-adımdan sonra `thread_id` ile anahtarlanan bir kontrol noktası yazar (varsayılan olarak Postgres); işçi çökmeleri bir kira (lease) serbest bırakır ve başka bir işçi devam eder. Ajanlar insan girdisini bekleyerek süresiz olarak uyuyabilir. **MegaAgent** (arXiv:2408.09955) üç durumla (Boşta / İşleniyor / Yanıt) ve iki-katmanlı koordinasyonla (grup-içi sohbet + gruplar-arası yönetici sohbet) ajan başına bir üretici-tüketici kuyruğu çalıştırdı. **Fiber/asenkron**, LLM akışı için thread-per-iş'i yener: thread'ler token'ları beklerken zamanın %99'u boşta kalır, fiber'ler I/O üzerinde işbirlikçi biçimde bırakır. Karşıt görüş: Ashpreet Bedi'nin "Scaling Agentic Software" çalışması, yük kanıtlayana kadar **FastAPI + Postgres + başka hiçbir şey**'i savunur — basit mimariler beklenenden daha uzağa gider. Bu ders dayanıklı bir kontrol noktası günlüğü, durum geçişleriyle ajan başına bir iş kuyruğu, asenkron-vs-thread demosu inşa eder ve pragmatik "basitle başla" kuralını yerleştirir.

**Tip:** Öğren + İnşa Et
**Diller:** Python (stdlib, `asyncio`, `sqlite3`)
**Önkoşullar:** Faz 16 · 09 (Paralel Sürü Ağları), Faz 16 · 13 (Paylaşımlı Bellek)
**Süre:** ~75 dakika

## Problem

Prototip bir multi-agent sistemi, bellek içi olay döngüsünde üç ajanla bir dizüstü bilgisayarda çalışır. Üretime geçirirsiniz:

- Ajanlar bazen saatlerce çalışır (uzun araştırma, insan-bil-in-the-loop beklemeleri).
- İşçi süreçleri çöker. Yeniden başlatma durumu kaybeder.
- Tepe yük ortalamanın 10 katıdır; yatay ölçekleme gerekir.
- Kullanıcılar ajan-koşu başına öder; şarj için tam-olarak-bir kez (exactly-once) semantiği gerekir.

Bellek içi olay döngüsü bunların hiçbirini yapmaz. Altında dayanıklı bir yürütme katmanı gerekir. 2026 kanonik seçenekleri:

1. Kontrol noktalı bir iş akışı motoru (Temporal, LangGraph çalışma zamanı).
2. Durum deposu olan bir mesaj kuyruğu (Postgres + SQS/RabbitMQ).
3. Aktör-model çerçeveleri (MegaAgent'ın ajan başına üretici-tüketici).
4. Elle-yapılmış FastAPI + Postgres (Bedi'nin argümanı).

Bu ders her birinin bir minyatürünü inşa eder.

## Kavram

### Dayanıklı yürütme kalıbı

Bir dayanıklı-yürütme motoru, her "adımdan" (LangGraph'ın dilinde süper-adım) sonra tam program durumunu kalıcı kılar. Çökme durumunda:

```
işçi adım ortasında çöker
 -> kira zaman aşımı
 -> başka bir işçi thread_id'yi alır
 -> son kontrol noktasından devam eder
 -> tekrar eden yan etki yok
```

#### Açıklama
Bunun çalışması için gereksinimler:

- **Serileştirilebilir durum.** Tüm ajan durumunun kalıcı kılınabilir olması gerekir. Canlı veritabanı bağlantılarına sahip fonksiyon kapanışları hayatta kalmaz.
- **Deterministik devam.** Aynı durum ve aynı girdiler verildiğinde, ajan aynı eylemleri üretir (veya LLM çağrıları için dış deterministik bir oracle'a başvurur).
- **Birim (idempotent) yan etkiler.** Dış çağrılar (araç çağrıları, ödemeler) birim olmalı veya bir tekilleştirme anahtarı kullanmalıdır.

LangGraph her süper-adımdan sonra bir kontrol noktası yazar; Temporal her aktiviteden sonra yazar; Restate olay-kaynaklı günlükler kullanır. Üçü de aynı kalıbı uygular.

### LangGraph'ın çalışma zamanı

Her ajanın bir `thread_id`'si vardır; durum yazılmış bir sözlüktür; her süper-adım kontrol noktaları tablosuna bir satır yazar. Devam ettirmede, çalışma zamanı sıfırdan değil, son kontrol noktasından yeniden oynatır. Ajanlar insan girdisini beklerken `interrupt()` çağırabilir; çalışma zamanı kalıcı kılar ve işçiyi serbest bırakır. Girdi geldiğinde, herhangi bir işçi devam edebilir.

Bu, Nisan 2026'da referans üretim tasarımıdır.

### MegaAgent'ın ajan başına kuyruğu

arXiv:2408.09955 bir ölçek deneyi tanımlar: bir kümede binlerce eşzamanlı ajan. Mimari:

```
ajan i:
 durum ∈ {Boşta, İşleniyor, Yanıt}
 gelen_kuyruk <- ajan i'ye adreslenmiş mesajlar
 giden_kuyruk -> yanıtlar + yan etkiler

koordinatörler:
 grup-içi sohbet (aynı gruptaki ajanlar)
 gruplar-arası yönetici sohbet (yüksek-düzey yönlendirme)
```

#### Açıklama
İki-katmanlı koordinasyon, grup-içi konuşmanın yoğun olmasını sağlarken gruplar-arası konuşmayı seyrek tutar — binlerce ajanda maliyeti doğrusal tutmak için kullanılan kalıp.

### Asenkron vs thread-per-iş

LLM çağrıları I/O-bağlıdır. Bir sonraki token'ı bekleyen bir thread zamanın %99'u boştadır. Thread'ler her biri ~1MB RAM'dir; 10.000 eşzamanlı çağrıda, bu yalnızca yığınlar için 10GB.

Fiber'lar (Python `asyncio`, Go goroutinleri, Rust `tokio`) I/O üzerinde işbirlikçi biçimde bırakır. Aynı 10.000 çağrı sürece rahatça sığar. LLM-ajan ölçeğinde, asenkron bir optimizasyon değildir — mimaridir.

İstisna: CPU-bağlı son-işleme (gömme, tokenizer hileleri) hâlâ thread veya süreç ister. I/O katmanınızı CPU katmanınızdan ayırın.

### Bedi'nin karşıt görüşü

"Scaling Agentic Software" (Ashpreet Bedi, 2026) çoğu takımın yükü ölçmeden önce aşırı mühendislik yaptığını savunur. Pragmatik varsayılan:

- FastAPI + Postgres.
- Her ajan koşusu bir satırdır; durum iyimser eşzamanlılık (optimistic concurrency) ile yerinde güncellenir.
- Arka plan işleri `pg_notify` veya basit bir Celery işçisi aracılığıyla.
- Uygulama kodunda yeniden deneme politikası.

Yönetilebilir görevlerde ~100 eşzamanlı ajan koşusunun altındaki yükler için, bu genellikle ihtiyacınız olan her şeydir. Başarısız olduğunu ölçtüğünüzde yükseltin.

Kural: basit mimarilerin çözemeyeceği somut bir soruna çarptığınızda dayanıklı-yürütme çerçevelerini benimseyin. Erken benimseme, karşılığını vermeyen seremonilerde zaman yakar.

### Tam-olarak-bir-kez semantiği

Ücretli ajan koşumları için, "tam-olarak-bir kez etkili" (en-az-bir kez teslim + birim tüketici) gerekir. Mühendislik hamleleri:

- **Koşu başına tekilleştirme anahtarı.** Her yan etki çağrısına dahil edin.
- **Outbox kalıbı.** Yan etkiler önce bir tabloya yazar, sonra ayrı bir süreç onları yürütür. Her iki adım da birim.
- **Telafi edici işlemler.** Bir yan etki başarılı olduğunda ancak izleme yazımı başarısız olduğunda, bir telafi planlayın.

Bunlar veritabanı-mühendisliği kalıplarıdır, LLM'ye özgü değildir. LLM vergisi yalnızca LLM çağrılarının yavaş olmasıdır; geri kalanı standart dağıtık sistemlerdir.

### Gökkuşağı (rainbow) dağıtımı

Anthropic'in multi-agent araştırma sistemi "gökkuşağı dağıtımları" kullanır: ajan çalışma zamanının birden fazla sürümü eşzamanlı çalışır, böylece uzun süreli ajanların her kod dağıtımında öldürülmesi gerekmez. Yeni sürümleri trafik diliminde kanarya olarak dağıtın; ajanları bitince eski sürümleri emekli edin.

Bu, uzun süreli durum bilgisi olan sistemler için standarttır; 2026 uyarlaması, ajanlar saatlerce yaşayabilir, dolayısıyla dağıtım döngüleri buna uyum sağlamalıdır.

### Kanonik üretim kontrol listesi

- Dayanıklı durum (kontrol noktaları, anlık görüntüler veya outbox + yeniden oynatılabilir günlük).
- Birim yan etkiler.
- LLM çağrıları için asenkron I/O katmanı.
- Tekilleştirmeyle en-az-bir kez teslim.
- Durum bilgisi olan iş yükleri için gökkuşağı/kanarya dağıtımı.
- Gözlemlenebilirlik: ajan başına izler, süper-adım denetimi, yeniden deneme sayacı.

## İnşa Et

`code/main.py` şunları uygular:

- `CheckpointStore` — SQLite-destekli, thread-id anahtarlı kontrol noktası günlüğü. Her süper-adım bir satır ekler.
- `run_with_checkpoint(agent, thread_id)` — bir koşunun ortasında çökmeyi simüle eder; ikinci bir işçi son kontrol noktasından devam eder.
- `AgentQueue` — küçük bir iş kuyruğuyla ajan başına Boşta / İşleniyor / Yanıt durum makinesi.
- `demo_async_vs_threads()` — 500 eşzamanlı simüle edilmiş "LLM çağrısını" asyncio ve thread aracılığıyla çalıştırır; duvar saati ve tepe belleği (yaklaşık) raporlar.

Çalıştır:

```
python3 code/main.py
```

#### Açıklama
Beklenen çıktı: simüle edilmiş çökme sonrası kontrol noktası devam ettirme başarılı olur; asenkron sürüm 500 eşzamanlı çağrıyı < 1s'de ele alır; thread sürümü birkaç saniye sürer ve eşzamanlı birim başına büyüklük sıraları daha fazla bellek kullanır.

## Kullan

`outputs/skill-scaling-advisor.md` dayanıklı-yürütme seçimi konusunda tavsiye verir: FastAPI + Postgres, LangGraph çalışma zamanı, Temporal veya özel. Yük, durum-saklama ihtiyaçları ve dağıtım sıklığı ile kalibre edilir.

## Yayınla

Kanonik üretim sertleştirmesi:

- **Basit başlayın (Bedi'nin kuralı).** Başarısız olduğunu ölçene kadar FastAPI + Postgres.
- **Optimize etmeden önce her şeyi izleyin.** Koşu başına gecikme histogramı, adım başına süre, yeniden deneme sayısı, başarısızlık kategorizasyonu.
- **Yan etkiler için outbox kalıbı.** Özellikle ödemeler ve dış API çağrıları.
- **Gökkuşağı dağıtımları.** Dağıtımlar sırasında uçuştaki ajan koşularını asla öldürmeyin.
- **Dayanıklı-yürütme motorlarını (Temporal / LangGraph / Restate) şu durumda benimseyin:** saatlerce insan-bil-in-the-loop beklemeleri, bölgeler-arası koordinasyon, karmaşık yeniden deneme/telafi politikaları.
- **I/O katmanı için asenkron.** CPU-bağlı son-İşleme için yalnızca thread.

## Alıştırmalar

1. `code/main.py` dosyasını çalıştırın. Kontrol noktası devamının çalıştığını doğrulayın; asenkron vs thread eşzamanlılık farkını ölçün.
2. Bir **outbox** tablosu uygulayın: her araç çağrısı önce outbox'a yazar, sonra ayrı bir goroutine/görev yürütür. Aracı çağrısını iki kez çalıştırarak birimliği doğrulayın.
3. Bir **gökkuşağı dağıtımı** simüle edin: iki eşzamanlı çalışma zamanı sürümü; yeni thread_id'lerin yarısını her birine yönlendirin; eski sürümdeki uçuştaki thread'lerin kesintiye uğramadığını doğrulayın.
4. LangGraph'ın çalışma zamanı belgesini (aşağıda bağlantılı) okuyun. Çalışma zamanının hangi özelliklerini elle-yapılmış bir FastAPI + Postgres sürümünde yeniden üretmek en uzun sürer? Bu, benimseme nedeni mi, yoksa erteleyebilir misiniz?
5. MegaAgent'ı (arXiv:2408.09955) Bölüm 3'ü okuyun. İki-katmanlı koordinasyon (grup-içi + gruplar-arası yönetici sohbet) açıktır. Bunu iki kuyruk ailesi olan bir mesaj kuyruğuna nasıl eşlersiniz?

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|------|----------------|------------------------|
| Dayanıklı yürütme | "Program durumunu kalıcı kıl" | Motor her süper-adımdan sonra durumu yazar; çökme kurtarma deterministiktir. |
| Süper-adım | "İşlemsel sınır" | Kontrol noktaları arasındaki iş birimi. LangGraph terimi. |
| thread_id | "Ajan koşu tanımlayıcısı" | Kontrol noktalarını ve devam ettirme mantığını bağlayan anahtar. |
| Birimlilik (Idempotency) | "Yeniden denemek güvenli" | Bir yan etkiyi tekrarlamak, tek denemenin sonucuyla aynı sonucu üretir. |
| Outbox kalıbı | "Yan etkileri ayır" | Niyeti bir tabloya yaz; ayrı bir yürütücü gerçekleştirir ve tamamlandı olarak işaretler. |
| En-az-bir kez teslim | "Olası kopyalar" | Mesaj kuyruğu semantiği; tekilleştirme anahtarı tüketiciyi etkili-bir-kez yapar. |
| Gökkuşağı dağıtımı | "Örtüşen sürümler" | Uzun süreli iş yükleri sırasında birden fazla çalışma zamanı sürümü eşzamanlı. |
| Asenkron fiber | "İşbirlikçi bırakma" | Kullanıcı-kip eşzamanlılık; I/O-bağlı yükler için thread'lerden ucuz. |
| Kontrol noktası | "Durum anlık görüntüsü" | Süper-adım sınırında serileştirilmiş durum; devam için anahtar. |

## İleri Okuma

- [LangChain — The runtime behind production deep agents](https://www.langchain.com/conceptual-guides/runtime-behind-production-deep-agents) — LangGraph çalışma zamanı tasarımı
- [MegaAgent](https://arxiv.org/abs/2408.09955) — ajan başına üretici-tüketici kuyruğu; binlerce eşzamanlı ajanda iki-katmanlı koordinasyon
- [Matrix](https://arxiv.org/abs/2511.21686) — mesaj kuyruklarını koordinasyon substratı olarak kullanan merkezsiz çerçeve
- [Temporal belgeleri](https://docs.temporal.io/) — dayanıklı yürütme için referans iş akışı motoru
- [Anthropic — Çok-ajanlı araştırma sistemi](https://www.anthropic.com/engineering/multi-agent-research-system) — gökkuşağı dağıtımı dahil üretim dersleri
