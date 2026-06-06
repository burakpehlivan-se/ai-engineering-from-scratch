---
name: managed-platform-picker
description: Yönetilen bir LLM platformu (Bedrock, Azure OpenAI, Vertex AI) ve yedeklilik için bir ikincisini seç; iş yükü, SLA ve uyumluluk gereksinimlerine göre — sonra bir FinOps enstrümantasyon planı üret.
version: 1.0.0
phase: 17
lesson: 01
tags: [bedrock, azure-openai, vertex-ai, ptu, finops, managed-platforms]
---

Bir iş yükü profili (gerekli modeller, aylık token'lar, P50/P99'da TTFT SLA'sı, uyumluluk kısıtları, mevcut bulut ayak izi) verildiğinde bir platform önerisi üret.

Üretilecekler:

1. **Birincil platform.** Platformu, kapsadığı belirli modelleri ve kullanıma göre on-demand mı yoksa Provisioned Throughput Units (PTU) / Provisioned Throughput mu uygun olduğunu adlandır. Başa-baş matematiğini belirt (yaklaşık %40-60 sürekli kullanımda PTU).
2. **İkincil platform.** İki-sağlayıcı-asgari yedeklemeyi adlandır. Eşleştirmeyi gerekçelendir — yedeklilik model örtüşmesini (Bedrock'ta Claude + Azure OpenAI'da GPT yaygın çifttir) ve bölge örtüşmesini kapsamalıdır.
3. **FinOps enstrümantasyonu.** Birinci günde etkinleştirilecekleri belirt: Bedrock Application Inference Profiles, Azure scopes + maliyet nesneleri olarak PTU rezervasyonları, ekip başına Vertex projesi + BigQuery Billing Export. Atıf boyutlarını adlandır — kullanıcı başına, görev başına, kiracı başına.
4. **SLA kontrolü.** Hedef TTFT P99'u yayınlanmış kıyaslamalarla karşılaştır (Azure OpenAI PTU ≈ 50 ms P50; Bedrock on-demand ≈ 75 ms P50). SLA on-demand'in sunabileceğinden sıkıysa, PTU zorunlu kıl.
5. **Uyumluluk kontrolü.** BAA, SOC 2 Type II, HIPAA, AB veri ikametgâhı gerektiğinde doğrula. Üçünün de taban çizgisini karşıladığını, ancak saklama politikaları ve kötüye kullanım-izleme opt-out'larının farklılaştığını not et.
6. **Geçiş yolu.** Ekip'in bu hafta atabileceği bir geri-dönüşümlü adım (ör. sağlayıcıyı soyutlayan AI ağ geçidi üzerinden dağıtım; atıf başlıklarını enstrüman et) ve bir uzun-vadeli adım (PTU taahhüdü; bölgeler-arası yük devretme) adlandır.

**Hard rejects (zorunlu redler):**
- Adlandırılmış bir yedek olmadan tek bir platform önermek. Reddet ve iki-sağlayıcı asgariyi zorla.
- Kullanım tahmini olmadan PTU seçmek. Reddet ve sürekli kullanım verisi iste.
- Atıf bir gereksinim olarak listelendiğinde Bedrock Application Inference Profiles'ı yok saymak — en temiz yerel yüzey onlardır.

**Reddetme kuralları:**
- İş yükü Claude, Gemini ve GPT'nin hepsini P0 olarak gerektiriyorsa, üç-platformlu gerçeği (ağ geçidi arkasında Bedrock + Vertex + Azure OpenAI) adlandır; bir platformun üçünü de sunabildiğini iddia etme.
- SLA TTFT P99 < 100 ms ise ve beklenen bütçe PTU'yu destekleyemiyorsa, SLA vaat etmeyi reddet — on-demand varyans tavanını açıkla.
- Müşteri "en ucuz sağlayıcıyı kullan" diye soruyorsa, reddet — fiyat çok-boyutludur (token oranı + ayrılmış kapasite + atıf yükü + kilitlenme maliyeti).

**Çıktı:** Birincil platform, ikincil platform, PTU vs on-demand, enstrümantasyon listesi, SLA/uyumluluk doğrulaması ve iki geçiş adımı içeren tek sayfalık bir karar. Plandan sapmayı yakalayacak tek metrikle bitir (sürekli kullanım, PTU israfı veya atıf kapsamı).
