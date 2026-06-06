---
name: gateway-picker
description: Ölçek, gecikme bütçesi, uyumluluk, ops duruşu ve fiyatlandırma toleransına göre bir AI ağ geçidi (LiteLLM, Portkey, Kong AI, Cloudflare/Vercel) seç.
version: 1.0.0
phase: 17
lesson: 19
tags: [ai-gateway, litellm, portkey, kong, cloudflare, vercel, bifrost, fallback, rate-limit, guardrails]
---

RPS (mevcut ve 12 aylık projeksiyon), gecikme bütçesi, uyumluluk (self-host zorunlu mu?), guardrail ihtiyacı (PII sansürleme, jailbreak algılama, denetim) ve fiyatlandırma toleransı verildiğinde bir ağ geçidi önerisi üret.

Üretilecekler:

1. **Birincil ağ geçidi.** Aracı adlandır. RPS tavanı, yükü ve özellik uyumuyla gerekçelendir.
2. **Yedekleme zinciri.** Sırayla üç sağlayıcı; OpenAI → Anthropic → self-hosted kanonik dizilimdir. Beklenen kullanılabilirliği hesapla.
3. **Hız sınırı politikası.** >500 RPS üzerinde kayan-pencere önerilir; aksi durumda token-bucket kabul edilebilir. Kiracı başına katmanlama.
4. **Guardrail'ler.** PII/jailbreak gerekliyse Portkey; ölçek + guardrail gerekirse Kong; yalnızca geliştirici katmanıysa LiteLLM.
5. **Gözlemlenebilirlik devri.** Phase 17 · 13 seçimine yönlendir; OTel GenAI sözleşmelerinin aktığını doğrula.
6. **Geçiş.** Uygulama-düzey entegrasyondan geliniyorsa, aşamalı yayılım (ağ geçidinde %1 kanarya, başarıda genişlet).

**Hard rejects (zorunlu redler):**
- LiteLLM'i >2000 RPS'de kullanmak. Reddet — Kong kıyaslaması kaskad başarısızlıklarını gösteriyor; önce geçiş yap.
- Portkey'i TTFT P99 < 100 ms SLA ile kullanmak. Reddet — 30 ms yükü bütçenin çok büyük kısmını yer.
- Düzenlenmiş bir şirket-içi müşteri için Cloudflare AI Gateway. Reddet — yalnızca yönetilen; self-host yok.

**Reddetme kuralları:**
- Ölçek belirsizliği büyükse (mevcut 100 RPS, 6 ayda planlanan 2K+), LiteLLM'e bağlanmadan önce geçiş planı iste.
- Uyumluluk SOC 2 Type II gerektiriyorsa ve seçilen ağ geçidi yönetilen SLA'sız yalnızca OSS ise, müşterinin kendi SOC 2 attestasyonunu iste.
- Ekibin Kubernetes'i yoksa ve Kong self-host seçiliyorsa, reddet — yönetilen Kong veya Portkey managed öner.

**Çıktı:** Ağ geçidi, yedekleme zinciri, hız sınırı politikası, guardrail duruşu, gözlemlenebilirlik akışı, geçiş planı içeren tek sayfalık bir karar. Tek bir metrikle bitir: son bir saat üzerinden ağ geçidi gecikmesi P99; ihlalde uyar.
