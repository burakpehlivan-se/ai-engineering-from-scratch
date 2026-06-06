---
name: llm-observability
description: OpenTelemetry GenAI span'lerini alan, değerlendirmeler çalıştıran ve enjekte edilen regresyonları beş dakika altında yakalayan kendi barındırılan bir LLM gözlemlenebilirlik panosu inşa et
version: 1.0.0
phase: 19
lesson: 11
tags: [capstone, observability, otel, langfuse, phoenix, evals, drift, clickhouse]
---

En az altı SDK ailesi (OpenAI, Anthropic, Google GenAI, LangChain, LlamaIndex, vLLM) üzerinden üretim LLM trafiği verildiğinde, OTLP GenAI-semconv span'lerini alan, değerlendirmeler çalıştıran, sapmayı tespit eden ve uyaran kendi barındırılan bir gözlemlenebilirlik düzlemi dağıt.

İnşa planı:

1. OTLP HTTP alıcısı, kuyruk-örnekleme işlemcisi (hataların %100'ünü, başarıların %10'unu, yüksek-toksisite/PII %100'ünü tut), ClickHouse + S3 ihracatçıları ile OpenTelemetry Collector.
2. GenAI semconv'u yansıtan ClickHouse span şeması: gen_ai.system, gen_ai.request.model, usage.input/output_tokens, latency_ms, user_id, app_id, artı istemler/tamamlamalar için JSON çantası.
3. Uygulamalar, kullanıcılar, oturumlar, ek açıklama kuyruğu için Postgres meta veri deposu.
4. SDK ailesi başına bir istemci uygulama üzerinde OpenLLMetry otomatik enstrümantasyonu; kanonik span'lerin indiğini doğrula.
5. Örneklenmiş izler üzerinde zamanlanmış DeepEval + RAGAS + Phoenix değerlendirici paketi; PII ve politika-dışı için özel LLM-yargıç.
6. Havuzlanmış istem gömüleri üzerinde haftalık PSI / KL sapma dedektörü; uyarı eşiği 0,2.
7. Değerlendirme puan toplamları ve gecikme yüzdeleri için Prometheus ihracatçısı; Alertmanager'dan Slack'e (uyarı) + PagerDuty'ye (kritik).
8. Next.js 15 App Router panosu: genel bakış, iz arama + çağlayan, değerlendirme trendleri, sapma grafiği, uyarılar.
9. Regresyon sondası: zamanın %1'inde sahte SSN sızdıran bir yanıt kalıbı enjekte et; MTTR (uyarı-yanma süresi) ölç.

Değerlendirme rubriği:

| Ağırlık | Kriter | Ölçüm |
|:-:|---|---|
| 25 | İz-şeması kapsamı | Kanonik GenAI span üreten SDK ailesi sayısı (hedef 6+) |
| 20 | Değerlendirme doğruluğu | El ile etiketlenmiş kümeye karşı DeepEval / RAGAS puanları |
| 20 | Pano UX | Enjekte edilen regresyonda MTTR (hedef 5 dakika altında) |
| 20 | Maliyet / ölçek | Birikim olmadan sürdürülen 1k span/saniye alım |
| 15 | Uyarı + sapma tespiti | Prometheus/Alertmanager zinciri uçtan uca çalıştırılmış |

Kesin redler:

- OpenTelemetry GenAI semconv'unda olmayan öznitelik adları icat eden span şemaları.
- Hataları düşüren kuyruk-örnekleme politikaları (iyi bilinen bir anti-kalıp).
- Alım oranında örnekleme olmadan çalışan değerlendirmeler (kabul edilemez maliyet).
- p50/p95/p99 ayrımı olmadan "gecikme" gösteren panolar.

Ret kuralları:

- Bir PII sansürleme politikası olmadan istem veya tamamlamaları kalıcı yapmayı reddet.
- SDK başına kanonik-span regresyon testi olmadan "çok-SDK desteği" iddia etmeyi reddet.
- Temel pencere olmadan sapma tespiti göndermeyi reddet; sıfır-atış sapması işe yaramaz.

Çıktı: Collector yapılandırmasını, ClickHouse şemasını, Next.js 15 panosunu, değerlendirme işlerini, sapma dedektörünü, uyarı zincirini, açıklamalı regresyonlarla 10k-iz demo veri kümesini ve enjekte edilen PII regresyonu için MTTR'yi ve iterasyon boyunca MTTR'yi düşüren en iyi üç pano UX iyileştirmesini belgeleyen bir yazıyı içeren bir depo.
