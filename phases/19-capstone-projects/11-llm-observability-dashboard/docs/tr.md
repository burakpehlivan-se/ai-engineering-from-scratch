# Capstone 11 — LLM Gözlemlenebilirlik ve Değerlendirme Panosu

> Langfuse açık-çekirdek oldu. Arize Phoenix 2026 GenAI semconv eşlemelerini yayınladı. Helicone ve Braintrust her ikisi de kullanıcı başına maliyet atfetmesine iki kat yatırım yaptı. Traceloop'un OpenLLMetry'si fiili SDK enstrümantasyonu oldu. Üretim şekli: izler (trace) için ClickHouse, meta veri için Postgres, arayüz için Next.js ve örneklenmiş izler üzerinde çalışan küçük bir değerlendirme işi ordusu (DeepEval, RAGAS, LLM-hakem). Bir tane self-hosted inşa edin, en az dört SDK ailesinden hazmedin ve enjekte edilen bir regresyonu beş dakikanın altında yakalamayı gösterin.

**Type:** Capstone
**Languages:** TypeScript (UI), Python / TypeScript (ingest + evals), SQL (ClickHouse)
**Prerequisites:** Phase 11 (LLM engineering), Phase 13 (tools), Phase 17 (infrastructure), Phase 18 (safety)
**Phases exercised:** P11 · P13 · P17 · P18
**Time:** 25 saat

## Problem

2026'da üretim trafiği çalıştıran her yapay zekâ ekibi, modelin yanında bir gözlemlenebilirlik düzlemi tutar. Maliyet atfetmesi. Halüsinasyon tespiti. Drift izleme. Jailbreak sinyali. SLO panoları. PII sızıntı uyarıları. Açık kaynak referanslar — Langfuse, Phoenix, OpenLLMetry — hazmetme şeması olarak OpenTelemetry GenAI semantik kurallarında birleşti. Artık OpenAI, Anthropic, Google, LangChain, LlamaIndex ve vLLM'i tek bir SDK ile enstrümana alıp uyumlu span'ler gönderebilirsiniz.

En az dört SDK ailesinden hazmeden, örneklenmiş izler üzerinde küçük bir değerlendirme işi kümesi çalıştıran, drift'i tespit eden ve uyaran self-hosted bir pano inşa edeceksiniz. Ölçüm çıtası: bilerek enjekte edilen bir regresyon (PII üretmeye başlayan bir istem) verildiğinde, pano onu yakalar ve beş dakikanın altında uyarı verir.

## Concept

Hazmetme OTLP HTTP'dir. SDK GenAI-semconv span'leri üretir: `gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.response.id`, `llm.prompts`, `llm.completions`. Span'ler sütunlu analitik için ClickHouse'a iner; meta veri (kullanıcılar, oturumlar, uygulamalar) Postgres'e iner.

Değerlendirmeler örneklenmiş izler üzerinde toplu işler olarak çalışır. DeepEval sadakat, toksiklik ve yanıt alakalılığını puanlar. RAGAS, iz geri getirme bağlamı taşıdığında geri getirme metriklerini puanlar. Özel LLM-hakemler alan-özgü kontrolleri (PII sızıntısı, politika-dışı yanıt) çalıştırır. Değerlendirme çalıştırmaları, ana ize bağlı değerlendirme span'leri olarak aynı ClickHouse'a geri yazar.

Drift tespiti, zaman içinde gömme-uzayı dağılımlarını (istemi gömme'leri üzerinde PSI veya KL sapması) artı değerlendirme puan trendlerini izler. Uyarılar Prometheus Alertmanager'ı ve ardından Slack / PagerDuty'yi besler. Arayüz, Recharts ile Next.js 15'tir.

## Architecture

```
production apps:
 OpenAI SDK + Anthropic SDK + Google GenAI SDK
 LangChain + LlamaIndex + vLLM
 |
 v
 OpenTelemetry SDK with GenAI semconv
 |
 v OTLP HTTP
 collector (ingest, sample, fan-out)
 |
 +-------------+-----------+
 v v v
 ClickHouse Postgres S3 archive
 (spans) (metadata) (raw events)
 |
 +---> eval jobs (DeepEval, RAGAS, LLM-judge)
 | sampled or all-trace
 | write eval spans back
 |
 +---> drift detector (PSI / KL on prompt embeddings)
 |
 +---> Prometheus metrics -> Alertmanager -> Slack / PagerDuty
 |
 v
 Next.js 15 dashboard (Recharts)
```

#### Açıklama

Bu mimari üretim uygulamalarından panoya kadar tam veri akışını gösterir. OpenAI, Anthropic, Google GenAI, LangChain, LlamaIndex ve vLLM gibi farklı SDK aileleri OpenLLMetry otomatik enstrümantasyonu ile OpenTelemetry SDK'yı kullanır. Span'ler OTLP HTTP üzerinden bir toplayıcıya gider; toplayıcı kuyruk-örnekleme (tail-sampling) yapar, hatalı izlerin %100'ünü ve başarılı olanların %10'unu tutar. Span'ler sütunlu analitik için ClickHouse'a, meta veriler Postgres'e ve ham olaylar S3'e yazılır. Değerlendirme işleri örneklenmiş izleri okur ve DeepEval, RAGAS veya özel LLM-hakem ile puanlar; sonuçlar ana ize bağlı span'ler olarak geri yazılır. Drift tespiti PSI/KL hesaplar, Prometheus metriklerini yayınlar ve Alertmanager üzerinden Slack veya PagerDuty'ye yönlendirir. Son olarak Next.js 15 Recharts panosu tüm bunları görselleştirir.

## Stack

- Hazmetme: OpenTelemetry SDK'ları + GenAI semantik kuralları; OTLP HTTP taşıma
- Toplayıcı: Kuyruk-örnekleme işlemcisi ile OpenTelemetry Collector (maliyet kontrolü için)
- Depolama: Span'ler için ClickHouse, meta veri için Postgres, ham olay arşivi için S3
- Değerlendirmeler: DeepEval, RAGAS 0.2, Arize Phoenix değerlendirici paketi, özel LLM-hakem
- Drift: Havuzlanmış istem gömme'leri üzerinde PSI / KL (sentence-transformers) haftalık
- Uyarı: Prometheus Alertmanager -> Slack / PagerDuty
- Arayüz: Next.js 15 App Router + Recharts + sunucu eylemleri
- Kutudan çıktığı gibi desteklenen SDK'lar: OpenAI, Anthropic, Google GenAI, LangChain, LlamaIndex, vLLM

## Build It

1. **Toplayıcı konfigürasyonu.** OTLP HTTP alıcısı, hatalı izlerin %100'ünü ve başarıların %10'unu tutan bir kuyruk-örnekleyici ve ClickHouse ile S3'e veren ihracatçılar ile OpenTelemetry Collector.

2. **ClickHouse şeması.** GenAI semconv'i yansıtan sütunlarla `spans` tablosu: `gen_ai_system`, `gen_ai_request_model`, `input_tokens`, `output_tokens`, `latency_ms`, `prompt_hash`, `trace_id`, `parent_span_id`, artı uzun yükler için JSON çantası. user_id ve app_id'ye göre ikincil endeksler ekleyin.

3. **SDK kapsam testi.** OpenLLMetry otomatik-enstrüman ile her SDK (OpenAI, Anthropic, Google, LangChain, LlamaIndex, vLLM) kullanan küçük bir istemci uygulama yazın. ClickHouse'a inen kanonik GenAI span'leri ürettiğini doğrulayın.

4. **Değerlendirme işleri.** Zamanlanmış bir iş, son-15-dakika örneklenmiş izlerini okur ve DeepEval sadakat, toksiklik ve yanıt alakalılığını çalıştırır. Çıktılar, ana ize bağlı değerlendirme span'leridir.

5. **Özel LLM-hakem.** PII-sızıntı hakemi: bir yanıt verildiğinde, PII sızıntısı olasılığını puanlamak için bir koruyucu LLM çağırır. Yüksek puanlı yanıtlar bir triyaj kuyruğuna iner.

6. **Drift tespiti.** Haftalık iş, bu haftanın havuzlanmış istem gömme'leri ile kalan 4 haftalık temel çizgi arasında PSI hesaplar. PSI eşiğin üzerindeyse, uyarı verir.

7. **Pano.** Next.js 15: genel bakış (span/saniye, maliyet/kullanıcı, p95 gecikme), izler (arama + şelale), değerlendirmeler (sadakat trendi, toksiklik), drift (zamanda PSI), uyarılar sayfaları.

8. **Uyarı zinciri.** Prometheus ihracatçısı, değerlendirme puan toplamlarını ve gecikme yüzdeliklerini okur; Alertmanager uyarıları Slack'e yönlendirir (önem derecesi düşük) ve PagerDuty'ye (önem derecesi yüksek).

9. **Regresyon sondası.** Bir hata enjekte edin: değerlendirilen sohbet botu zamanın %1'inde sahte SSN'ler sızdırmaya başlar. MTTR'yi ölçün: hata dağıtıldıktan Slack uyarısına kadar.

## Use It

```
$ curl -X POST https://my-otel-collector/v1/traces -d @trace.json
[collector] accepted 1 trace, 3 spans
[clickhouse] inserted 3 spans (app=chat, user=u_42)
[eval] DeepEval faithfulness 0.82, toxicity 0.03
[drift] weekly PSI 0.08 (below 0.2 threshold)
[ui] live at https://obs.example.com
```

#### Açıklama

Bu örnek bir iz akışının uçtan uca işlenmesini gösterir. Bir istemci bir OTLP HTTP isteği gönderir; toplayıcı izi kabul eder ve 3 span'i ClickHouse'a yazar (uygulama=chat, kullanıcı=u_42). DeepEval değerlendirme işi sadakat puanı 0.82 ve toksiklik 0.03 üretir. Haftalık PSI 0.08 — 0.2 eşiğinin altında, yani drift yok. Pano canlıya geçer ve operatör gerçek zamanlı olarak izleyebilir.

## Ship It

`outputs/skill-llm-observability.md` teslim edilen şeydir. Bir LLM uygulaması verildiğinde, pano izlerini hazmeder, değerlendirmeleri çalıştırır, drift'te uyarır ve Next.js'te kullanıcı başına maliyet dökümü sunar.

| Ağırlık | Ölçüt | Nasıl ölçülür |
|:-:|---|---|
| 25 | İz-şeması kapsamı | Kanonik GenAI span'leri üreten SDK ailesi sayısı (hedef: 6+) |
| 20 | Değerlendirme doğruluğu | El ile etiketlenmiş kümeye karşı DeepEval / RAGAS puanları |
| 20 | Pano UX | Enjekte edilen regresyon üzerinde MTTR (5 dakika altı hedef) |
| 20 | Maliyet / ölçek | Birikim olmaksızın 1k span/saniye'de sürdürülebilir hazmetme |
| 15 | Uyarı + drift tespiti | Prometheus/Alertmanager zinciri uçtan uca çalıştırıldı |
| **100** | | |

## Exercises

1. Haystack çatısı için özel enstrümantasyon ekleyin. Sadık `gen_ai.*` nitelikleriyle kanonik span'lerin ClickHouse'a indiğini doğrulayın.

2. Aynı izlerde DeepEval'i Phoenix değerlendiricileri ile değiştirin. İki değerlendirme motoru arasındaki puan kaymasını ölçün.

3. Drift detektörünü keskinleştirin: küresel yerine uygulama-kimliği başına PSI hesaplayın. Uygulama başına drift izlerini gösterin.

4. Bir "kullanıcı etkisi" sayfası ekleyin: maliyet-kullanıcı-başına ve başarısızlık-oranı-kullanıcı-başına, küçük çizgi grafikleriyle.

5. Toksisitesi > 0.5 olan izlerin %100'ünü ve geri kalanın tabakalı %10'unu tutan bir kuyruk-örnekleme politikası inşa edin. Eklenen örnekleme yanlılığını ölçün.

## Key Terms

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|------|----------------------|----------------------------|
| GenAI semconv | "OTel LLM nitelikleri" | 2025 OpenTelemetry spesifikasyonu, LLM span nitelikleri (sistem, model, token) |
| Kuyruk örnekleme | "İz-sonrası örneklem" | Toplayıcı bir iz tamamlandıktan sonra onu tutup tutmamaya karar verir (hatalara bakabilir) |
| PSI | "Nüfus stabilite endeksi" | İki dağılımı karşılaştıran drift metriği; > 0.2 genellikle anlamlı drift sinyali |
| LLM-hakem | "Model olarak değerlendirme" | Bir rubric (sadakat, toksiklik, PII) üzerinde başka bir LLM'nin çıktısını puanlayan LLM |
| Kuyruk-örnekleme politikası | "Tutma kuralı" | Hangi izlerin kalıcı, hangilerinin düşürüleceğine karar veren kural; hatalı + örnek-oranı |
| Değerlendirme span'i | "Bağlı değerlendirme izi" | Orijinal LLM çağrı span'ine bağlı bir değerlendirme puanı taşıyan alt-span |
| Kullanıcı başına maliyet | "Birim ekonomi" | Bir kullanıcı_kimliğine bir pencere üzerinde atfedilen dolar maliyet; anahtar ürün metriği |

## Further Reading

- [Langfuse](https://github.com/langfuse/langfuse) — referans açık-çekirdek gözlemlenebilirlik platformu
- [Arize Phoenix](https://github.com/Arize-ai/phoenix) — güçlü drift desteğiyle alternatif referans
- [OpenLLMetry (Traceloop)](https://github.com/traceloop/openllmetry) — otomatik-enstrümantasyon SDK ailesi
- [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — hazmetme şeması
- [Helicone](https://www.helicone.ai) — alternatif hosted gözlemlenebilirlik
- [Braintrust](https://www.braintrust.dev) — alternatif değerlendirme-öncelikli platform
- [ClickHouse documentation](https://clickhouse.com/docs) — sütunlu span deposu
- [DeepEval](https://github.com/confident-ai/deepeval) — değerlendirici kütüphanesi
