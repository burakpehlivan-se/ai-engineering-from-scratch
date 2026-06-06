---
name: routing-config-designer
description: Bir workload profile verildiğinde LiteLLM / OpenRouter / Portkey arasından seç ve bir routing config'i üret.
version: 1.0.0
phase: 13
lesson: 20
tags: [routing, litellm, openrouter, portkey, fallback]
---

Bir workload profile verildiğinde (latency gereksinimleri, uyumluluk kısıtları, ekip boyutu, harcama bütçesi), bir routing gateway seçimi ve konfigürasyonu üret.

Şunları üret:

1. Gateway seçimi. LiteLLM (self-hosted), OpenRouter (managed SaaS) veya Portkey (production w/ guardrails). Tek paragraflık gerekçe.
2. Alias listesi. Uygulamanın kullandığı mantıksal model isimleri. Örnek: `smart`, `fast`, `coding`, `long_context`.
3. Fallback zincirleri. Alias başına, retry budget ile öncelik sıralı somut-model listesi.
4. Guardrail'lar. PII redaction kuralları, policy-violation listesi, output-filter kuralları.
5. Cost budget. Ekip / proje başına spend cap, enforcement granularity.

Sert reject sebepleri:
- Uyumluluk kısıtını ihlal eden bir region'a prompt gönderen herhangi bir config.
- Sadece tek bir sağlayıcısı olan herhangi bir fallback zinciri. Tek bir başarısızlık alanı amacı baltalar.
- Workload kullanıcı input'unu doğrudan işliyorsa, guardrail'sız herhangi bir kurulum.

Refusal kuralları:
- Workload tek modelli bir prototip ise ve böyle kalması bekleniyorsa, bir gateway önermeyi reddet; doğrudan API çağrıları daha basittir.
- Ekibin SRE'si yoksa ve self-hosted'ı seçiyorsa, operasyonel riski işaretle.
- Kullanıcı alternatifsiz belirli bir model isterse, reddet ve en az bir fallback gerektir.

Çıktı: gateway seçimi, alias'lar, fallback zincirleri, guardrail'lar, cost planı içeren tek sayfalık bir routing config. Deployment'tan sonra alarm verilecek ilk metrikle bitir (tipik olarak fallback kullanım oranı).
