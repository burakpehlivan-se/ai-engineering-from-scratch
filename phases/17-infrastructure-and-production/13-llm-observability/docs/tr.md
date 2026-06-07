# LLM Gözlemlenebilirlik Yığını Seçimi

> 2026 gözlemlenebilirlik pazarı iki kategoriye ayrılır. Geliştirme platformları (LangSmith, Langfuse, Comet Opik) izlemeyi eval'lerle, istem yönetimiyle, oturum replay'larıyla paketler. Ağ geçidi / işaretleme araçları (Helicone, SigNoz, OpenLLMetry, Phoenix) telemetriye odaklanır. Langfuse, güçlü OSS dengesi ile MIT-lisanslı çekirdeğe sahip (aylık 50K olay ücretsiz bulut). Phoenix, Elastic License 2.0 altında OpenTelemetry-yerel — drift/RAG görselleştirmesi için mükemmel, kalıcı bir üretim arka ucu değil. Arize AX, monolitik gözlemlenebilirlikten 100x daha ucuz olduğunu iddia eden sıfır-kopya Iceberg/Parquet entegrasyonu kullanır. LangSmith LangChain/LangGraph için lider, kullanıcı başına 39$, yalnızca Enterprise'da self-host. Helicone proxy-temelli, 15-30 dakika kurulum, 100K istek/ay ücretsiz, ancak agent izlerinde daha az derinlik. Yaygın üretim örüntüsü: Ağ Geçidi (Helicone/Portkey) + OpenTelemetry ile yapıştırılmış eval platformu (Phoenix/TruLens).

**Tür:** Öğrenme
**Diller:** Python (stdlib, oyuncak iz örnekleme simülatörü)
**Önkoşullar:** Faz 17 · 08 (Inference Metrikleri), Faz 14 (Agent Mühendisliği)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Geliştirme platformlarını (paketlenmiş: eval'ler + istemler + oturumlar) ağ geçidi/telemetri araçlarından (yalnızca izler + metrikler) ayırt edin.
- Altı büyük aracı (Langfuse, LangSmith, Phoenix, Arize AX, Helicone, Opik) lisanslama, fiyatlandırma ve tatlı nokta kullanım senaryolarıyla eşleyin.
- Bir ağ geçidi aracını ayrı bir eval platformuyla birleştirmenizi sağlayan OpenTelemetry-yapıştırma örüntüsünü açıklayın.
- 2026 maliyet farklılaştırıcısını (Arize AX'in sıfır-kopya yaklaşımı vs monolitik ingest) adlandırın ve kabaca 100x çarpanını belirtin.

## Sorun

Bir LLM özelliği gönderdiniz. Çalışıyor. İstem başarısızlıklarına, araç döngülerine, gecikme regresyonlarına, maliyet sıçramalarına veya istem-cache hit oranına görünürlüğünüz yok. Google'da "LLM gözlemlenebilirlik" aratıyorsunuz ve üç farklı fiyat noktasında aynı sorunu çözdüğünü iddia eden sekiz araç çıkıyor.

Aynı sorunu çözmüyorlar. LangSmith "bu LangGraph çalıştırması neden başarısız oldu?" sorusuna cevap verir. Phoenix "RAG boru hattım mı sürükleniyor?" sorusuna cevap verir. Helicone "hangi uygulama token yakıyor?" sorusuna cevap verir. Langfuse "tüm bunu self-host edebilir miyim?" sorusuna cevap verir. Farklı araçlar, farklı kitleler.

Seçim dört eksen içerir: yığın (LangChain? ham SDK? çok-satıcılı?), lisans toleransı (yalnızca MIT? Elastic OK? ticari iyi?), bütçe (ücretsiz katman? 100$/ay? 1000$/ay?) ve self-host (zorunlu? güzel-olurdu? asla?).

## Kavram

### İki kategori

**Geliştirme platformları** gözlemlenebilirliği eval'lerle, istem yönetimiyle, veri seti versiyonlamayla, oturum replay'ıyla paketler. Deneyler çalıştırırsınız, hangi istemin işe yaradığını görürsünüz, yeni bir istemi veri seti-regresyonuyla eski kazananlara karşı test edersiniz. LangSmith, Langfuse, Comet Opik.

**Ağ geçidi/telemetri araçları** inference çağrılarını işaretler — istem, yanıt, token'lar, gecikme, model, maliyet. Helicone, SigNoz, OpenLLMetry, Phoenix. Minimalist. OpenTelemetry aracılığıyla ayrı bir eval aracıyla birleştirilebilir.

### Langfuse — OSS dengesi

- Çekirdek Apache / MIT lisanslı; Docker aracılığıyla self-host.
- Bulut ücretsiz katman: aylık 50K olay. Ücretli: ekip için 29$/ay.
- Eval'ler, istem yönetimi, izler, veri setleri. Dört geliştirme platformu özelliğinin makul kapsamı.
- Tatlı nokta: LangSmith-sınıfı özellikler istiyorsunuz, ancak self-host veya OSS lisansında kalmalısınız.

### Phoenix (Arize) — telemetri-öncelikli, OpenTelemetry-yerel

- Elastic License 2.0; self-host trivial.
- RAG ve drift görselleştirmesinde mükemmel. Gömme-uzayı serpme grafikleri birinci-sınıf olarak gönderilir.
- Kalıcı üretim arka ucu olarak tasarlanmamıştır — öncelikle geliştirme-zamanı gözlemlenebilirliği.
- Tatlı nokta: RAG boru hattı geliştirme, drift hata ayıklama, üretim için ayrı bir ağ geçidi ile eşleşir.

### Arize AX — ölçek oyunu

- Ticari. Iceberg/Parquet aracılığıyla sıfır-kopya veri gölü entegrasyonu.
- Ölçekte monolitik gözlemlenebilirlikten (Datadog-sınıfı) ~100x daha ucuz olduğunu iddia ediyor. Matematik: izleri kendi Parquet'inizde S3'te saklarsınız; Arize doğrudan okur.
- Tatlı nokta: günde >10M iz, mevcut veri gölü, Datadog fiyatlandırması olmadan LLM'e özgü gösterge panelleri istiyor.

### LangSmith — LangChain/LangGraph ilk

- Ticari, kullanıcı başına 39$/ay. Yalnızca Enterprise'da self-host.
- LangChain ve LangGraph yığınları için en iyi sınıf. İkisinde de değilseniz, daha az çekici.
- Tatlı nokta: LangChain'e bağlı ekip, ödemeye istekli.

### Helicone — proxy-temelli minimum uygulanabilir

- `OPENAI_API_BASE`'inizi Helicone proxy'sine değiştirerek 15-30 dakika kurulum.
- MIT lisanslı; 100K istek/ay ücretsiz, ücretli 20$/ay+.
- Yük devretme, önbellekleme, hız limitleri içerir — ağ geçidi olarak da hareket eder.
- Agent / çok-adımlı izlerde daha az derinlik.
- Tatlı nokta: hızlı başlangıç, tek-yığın uygulama, bir arada ağ geçidi + gözlemlenebilirlik ihtiyacı.

### Opik (Comet) — OSS geliştirme platformu

- Apache 2.0, tamamen OSS.
- Comet mirasıyla Langfuse'a benzer özellik seti.
- Tatlı nokta: Comet'te zaten olan ML ekipleri, aynı bölmede LLM gözlemlenebilirliği istiyor.

### SigNoz — OpenTelemetry-ilk tam APM

- Apache 2.0. Genel APM'yi OpenTelemetry aracılığıyla LLM ile birlikte ele alır.
- Tatlı nokta: servisler ve LLM çağrıları arasında birleşik gözlemlenebilirlik.

### Yapıştırıcı: OpenTelemetry + GenAI semantik kuralları

OpenTelemetry, 2025 sonunda GenAI semantik kurallarını yayınladı (`gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`). OTel tüketen araçlar birlikte çalışabilir. Ortaya çıkan üretim örüntüsü:

1. Her LLM çağrısından GenAI kurallarıyla OTel yayınlayın.
2. Günlük işler için ağ geçidine (Helicone / Portkey) yönlendirin.
3. Regresyonlar için eval platformuna (Phoenix / Langfuse) çift gönderin.
4. Arize AX veya DuckDB aracılığıyla uzun-vadeli analiz için veri gölünde (Iceberg) arşivleyin.

### Tuzak: yanlış katmanda işaretleme

Agent çerçevenizin içinde işaretleme (ör. LangSmith izleri eklemek) sizi o çerçeveye bağlar. HTTP/OpenAI-SDK katmanında (OpenLLMetry veya ağ geçidiniz aracılığıyla) işaretleme taşınabilirdir.

### Örnekleme — her şeyi tutamazsınız

Günde >1M istek'te, tam-iz saklama LLM çağrılarından daha pahalıya mal olur. Kurallara göre örnekleyin: hatalar %100, yüksek-maliyet %100, başarılar %5. Toplamaları her zaman tutun; ham veriyi uzun kuyruk için tutun.

### Hatırlamanız gereken sayılar

- Langfuse ücretsiz bulut: aylık 50K olay.
- LangSmith: kullanıcı başına 39$/ay.
- Helicone ücretsiz: aylık 100K istek.
- Arize AX iddiası: ölçekte monolitikten ~100x daha ucuz.
- OpenTelemetry GenAI kuralları: 2025'te gönderiliyor, 2026'da yaygın olarak benimseniyor.

## Kullan

`code/main.py`, 1M-izlik bir günü saklama stratejileri (%100 ingest, örnekleme, örnekleme + hatalar) üzerinden simüle eder. Depolama maliyetini ve her birinin altında neyin kaybolduğunu raporlar.

## Üret

Bu ders `outputs/skill-observability-stack.md` üretir. Yığın, ölçek, bütçe, lisans duruşu verildiğinde, aracı(ları) seçer.

## Alıştırmalar

1. Ekibiniz LangChain'de OSS self-hosted gözlemlenebilirlik istiyor. Langfuse veya Opik seçin ve gerekçelendirin.
2. Datadog'un 5M iz/gün için 150K$/ay teklif ettiği yerde, Arize AX için başabaşı hesaplayın.
3. Kuruluşunuzun kılavuzunun her LLM çağrısında zorunlu kılması gereken bir OpenTelemetry GenAI öznitelik seti tasarlayın.
4. Phoenix'in tek başına üretim için yeterli olup olmadığını tartışın. Ne zaman yetmez?
5. Helicone 20ms proxy ek yükü. P99 TTFT 300 ms'de, bu kabul edilebilir mi? SLA 100 ms ise?

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|----------------------|----------------------------|
| OpenLLMetry | "LLM'ler için OTel" | LLM'ler için açık-kaynak OpenTelemetry işaretlemesi |
| GenAI kuralları | "OTel öznitelikleri" | LLM çağrıları için standart OTel öznitelik adları |
| LangSmith | "LangChain gözlemlenebilirlik" | LangChain ekosistemiyle paketlenmiş ticari platform |
| Langfuse | "OSS LangSmith" | Benzer özellik setiyle MIT OSS |
| Phoenix | "Arize geliştirme aracı" | OpenTelemetry-yerel geliştirme/eval platformu |
| Arize AX | "ölçek gözlemlenebilirliği" | Ticari sıfır-kopya Iceberg/Parquet gözlemlenebilirlik |
| Helicone | "proxy gözlemlenebilirlik" | LLM telemetri + ağ geçidi özellikleri toplayan HTTP proxy |
| Opik | "Comet LLM" | Comet'ten Apache 2.0 OSS geliştirme platformu |
| Oturum replay | "iz yeniden çalıştırma" | Araç çağrılarıyla tam bir agent oturumunu yeniden oynat |
| Eval | "çevrimdışı test" | Etiketlenmiş veri seti üzerinde aday model/istem çalıştırma |

## İleri Okuma

- [SigNoz — Top LLM Observability Tools 2026](https://signoz.io/comparisons/llm-observability-tools/)
- [Langfuse — Arize AX Alternative analysis](https://langfuse.com/faq/all/best-phoenix-arize-alternatives)
- [PremAI — Setting Up Langfuse, LangSmith, Helicone, Phoenix](https://blog.premai.io/llm-observability-setting-up-langfuse-langsmith-helicone-phoenix/)
- [OpenTelemetry GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [Arize Phoenix docs](https://docs.arize.com/phoenix)
- [Helicone docs](https://docs.helicone.ai/)
