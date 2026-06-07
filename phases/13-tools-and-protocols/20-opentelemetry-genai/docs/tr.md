# OpenTelemetry GenAI — Araç Çağrılarını Uçtan Uca İzleme

> Bir ajan beş araç, üç MCP sunucusu ve iki alt ajan çağırır. Tüm bunların üzerinde tek bir iz (trace) gereklidir. OpenTelemetry GenAI anlamsal kuralları (v1.37 ve üzeriyle kararlı nitelikler), 2026 standardıdır; Datadog, Langfuse, Arize Phoenix, OpenLLMetry ve AgentOps tarafından yerel olarak desteklenir. Bu ders gerekli nitelikleri isimlendirir, aralık (span) hiyerarşisini (ajan → LLM → araç) yürüyerek gösterir ve herhangi bir dışa aktarıcıya (exporter) takabileceğiniz stdlib aralık üreticisini sunar.

**Tür:** İnşa Et
**Diller:** Python (stdlib, OTel aralık üreticisi)
**Ön koşullar:** Faz 13 · 07 (MCP sunucusu), Faz 13 · 08 (MCP istemcisi)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Bir LLM aralığı ve bir araç çalıştırma aralığı için gerekli OTel GenAI niteliklerini adlandır.
- Ajan döngüsü, LLM çağrısı, araç çağrısı ve MCP istemci dağıtımını kapsayan bir iz hiyerarşisi inşa et.
- Yakalanacak içeriği (isteğe bağlı) vs sansürlenecekleri (varsayılan) kararlaştır.
- Araç kodunu yeniden yazmadan bir yerel toplayıcıya (Jaeger, Langfuse) aralık (span) üret.

## Sorun

Şubat 2026'dan bir hata ayıklama: kullanıcı "aracım bazen 30 saniye, bazen 3 saniye sürüyor" diyor. İz yok. Günlükler LLM çağrısını gösteriyor, ancak araç dağıtımını, MCP sunucu tur yolculuğunu, alt ajanı göstermiyor. Tahmin ediyorsunuz. Sonunda buluyorsunuz: bir MCP sunucusu ara sıra soğuk başlangıçta takılıyor.

Uçtan uca izleme olmadan bunu bulamazsınız. OTel GenAI bunu düzeltir.

Kurallar 2025-2026'da OpenTelemetry anlamsal kurallar grubu altında yerleşti. Datadog, Langfuse, Phoenix, OpenLLMetry ve AgentOps'un aynı aralıkları ayrıştırmasını sağlayan kararlı nitelik adları tanımlarlar. Bir kez enstrümantasyon yapın; herhangi bir arka plana gönderin.

## Kavram

### Aralık hiyerarşisi

```
agent.invoke_agent (üst, INTERNAL aralığı)
 ├── llm.chat (CLIENT aralığı)
 ├── tool.execute (INTERNAL)
 │ └── mcp.call (CLIENT aralığı)
 ├── llm.chat (CLIENT aralığı)
 └── subagent.invoke (INTERNAL)
```

Her şey tek bir iz id'si altında iç içe geçer. Aralık id'leri ebeveyn-çocuk ilişkilerini bağlar.

### Gerekli nitelikler

2025-2026 anlamsal kurallarına göre:

- `gen_ai.operation.name` — `"chat"`, `"text_completion"`, `"embeddings"`, `"execute_tool"`, `"invoke_agent"`.
- `gen_ai.provider.name` — `"openai"`, `"anthropic"`, `"google"`, `"azure_openai"`.
- `gen_ai.request.model` — istenen model stringi (ör. `"gpt-4o-2024-08-06"`).
- `gen_ai.response.model` — gerçekten hizmet veren model.
- `gen_ai.usage.input_tokens` / `gen_ai.usage.output_tokens`.
- `gen_ai.response.id` — eşleştirme için sağlayıcı yanıt id'si.

Araç aralıkları için:

- `gen_ai.tool.name` — araç tanımlayıcısı.
- `gen_ai.tool.call.id` — belirli çağrı id'si.
- `gen_ai.tool.description` — araç açıklaması (isteğe bağlı).

Ajan aralıkları için:

- `gen_ai.agent.name` / `gen_ai.agent.id` / `gen_ai.agent.description`.

### Aralık türleri

- `SpanKind. CLIENT` süreç sınırını aşan çağrılar için (LLM sağlayıcısı, MCP sunucusu).
- `SpanKind. INTERNAL` ajanın kendi döngü adımları ve araç çalıştırması için.

### İsteğe bağlı içerik yakalama

Varsayılan olarak aralıklar metrikler ve zamanlama taşır — prompt'lar veya tamamlamalar değil. Büyük yükler ve Kişisel Bilgi varsayılan olarak kapalıdır. İçeriği dahil etmek için `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` ve özel içerik-yakalama ortam değişkenlerini ayarlayın. Üretimde etkinleştirmeden önce dikkatlice gözden geçirin.

### Aralıklar üzerinde olaylar

Token düzeyindeki olaylar aralık olayları olarak eklenebilir:

- `gen_ai.content.prompt` — girdi mesajları.
- `gen_ai.content.completion` — çıktı mesajları.
- `gen_ai.content.tool_call` — kaydedilen araç çağrısı.

Olaylar, detaylı tekrar oynatma için aralık içinde zaman sıralıdır.

### Dışa aktarıcılar (Exporters)

OTel aralıkları şunlara dışa aktarılır:

- **Jaeger / Tempo.** OSS, yerinde.
- **Langfuse.** LLM-gözlemlenebilirliğe özgü; token kullanımını görselleştirir.
- **Arize Phoenix.** Değerlendirmeler + izleme birleşik.
- **Datadog.** Ticari; `gen_ai.*` niteliklerini yerel olarak ayrıştırır.
- **Honeycomb.** Sütun odaklı; sorgu dostu.

Hepsi OTLP olan tel formatını konuşur. Kodunuz umursamaz.

### MCP üzerinden yayma

Bir MCP istemcisi bir sunucu çağırdığında, W3C traceparent başlığını isteğe enjekte edin. Streamable HTTP standart başlıkları destekler. Stdio doğal olarak HTTP başlıkları taşımaz; teknik dokümanın 2026 yol haritası JSON-RPC çağrılarında bir `_meta.traceparent` alanı eklenmesini tartışıyor.

Bu yayınlanana kadar: her isteğin `_meta`'sında traceparent'ı manuel olarak dahil edin. Sunucu iz id'sini günlüğe kaydeder.

### Metrikler

Aralıkların yanı sıra, GenAI anlamsal kuralları metrikleri tanımlar:

- `gen_ai.client.token.usage` — histogram.
- `gen_ai.client.operation.duration` — histogram.
- `gen_ai.tool.execution.duration` — histogram.

Çağrı başına detay gerektirmeyen panolar için bunları kullanın.

### AgentOps katmanı

AgentOps (2024'te kuruldu) GenAI gözlemlenebilirliğinde uzmanlaşmıştır. Popüler çerçeveleri (LangGraph, Pydantic AI, CrewAI) OTel aralıklarını otomatik olarak üretmek için sarar. Yığınınız desteklenen bir çerçeve kullanıyorsa faydalıdır; aksi halde manuel enstrümantasyon kullanın.

## Kullan

`code/main.py`, bir LLM çağıran, iki aracı dağıtan ve bir MCP tur yolculuğu yapan bir ajan için stdout'a (OTLP-JSON benzeri formatta) OTel-şekilli aralıklar üretir. Gerçek bir dışa aktarıcı yok — ders aralık şekline ve nitelik kümesine odaklanır. Çıktıyı OTLP uyumlu bir görüntüleyiciye yapıştırın veya yalnızca okuyun.

Neye bakılmalı:

- İz id'si tüm aralıklar arasında ortaktır.
- Ebeveyn-çocuk bağları `parentSpanId` aracılığıyla kodlanır.
- Gerekli `gen_ai.*` nitelikleri doldurulmuştur.
- İçerik yakalama varsayılan olarak kapalıdır; bir senaryo ortam değişkeniyle açar.

## Sun

Bu ders `outputs/skill-otel-genai-instrumentation.md` dosyasını üretir. Bir ajan kod tabanı verildiğinde, beci bir enstrümantasyon planı üretir: nereye aralık ekleneceği, hangi niteliklerin doldurulacağı ve hangi dışa aktarıcıların hedefleneceği.

## Alıştırmalar

1. `code/main.py`'i çalıştırın. Aralıkları sayın ve hangisinin CLIENT vs INTERNAL olduğunu belirleyin.

2. İçerik yakalamayı açın (ortam değişkeni) ve `gen_ai.content.prompt` ve `gen_ai.content.completion` olaylarının göründüğünü doğrulayın. Kişisel Bilgi için sonuçları not edin.

3. `gen_ai.tool.execution.duration` araç çalıştırma metriğini ekleyin ve çağrı başına bir histogram örneği olarak üretin.

4. Bir ebeveyn ajan aralığından bir MCP isteğinin `_meta.traceparent` alanına bir traceparent yayınlayın. MCP sunucusunun aynı iz id'sini göreceğini doğrulayın.

5. OTel GenAI anlamsal kurallar teknik dokümanını okuyun. Bu dersin kodunun ÜRETMEDiği anlamsal kurallarda listelenen bir nitelik belirleyin. Ekleyin.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| OTel | "OpenTelemetry" | İzler, metrikler, günlükler için açık standart |
| GenAI semconv | "GenAI anlamsal kuralları" | LLM / araç / ajan aralıkları için kararlı nitelik adları |
| `gen_ai.*` | "Nitelik ad前三refixü" | Tüm GenAI nitelikleri bu前三refixi paylaşır |
| Span (Aralık) | "Zamanlanmış işlem" | Başlangıcı, sonu ve nitelikleri olan bir çalışma ünitesi |
| Trace (İz) | "Çapraz-aralıksoy ağacı" | Bir iz id'sini paylaşan aralık ağacı |
| SpanKind | "CLIENT / SERVER / INTERNAL" | Aralık yönü hakkında ipuçları |
| OTLP | "OpenTelemetry Hat Protokolü" | Dışa aktarıcılar için tel formatı |
| Opt-in content | "Prompt / tamamlama yakalama" | Varsayılan olarak kapalı; etkinleştirmek için ortam değişkeni |
| traceparent | "W3C başlığı" | Hizmetler arası iz bağlamasını yayınlar |
| Exporter (Dışa aktarıcı) | "Arka plana özgü gönderici" | Aralıkları Jaeger / Datadog'a vb. gönderen bileşen |

## İleri Okuma

- [OpenTelemetry — GenAI semconv](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — GenAI aralıkları, metrikleri ve olayları için kanonik kurallar
- [OpenTelemetry — GenAI spans](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/) — LLM ve araç çalıştırma aralık nitelik listesi
- [OpenTelemetry — GenAI agent spans](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/) — ajan düzeyinde `invoke_agent` aralığı
- [open-telemetry/semantic-conventions — GenAI spans](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-spans.md) — GitHub barındırmalı gerçek kaynak
- [Datadog — LLM OTel semantic convention](https://www.datadoghq.com/blog/llm-otel-semantic-convention/) — üretim entegrasyonu yürüyüşü
