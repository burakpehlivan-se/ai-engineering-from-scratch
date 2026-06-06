---
name: inference-platform-picker
description: İş yükü, SLA, bütçe ve operasyonel kısıtlar verildiğinde bir çıkarım platformu (Fireworks, Together, Baseten, Modal, Replicate, Anyscale veya özel silikon) seç. Token başına, dakika başına ve tahmin başına fiyatlandırmayı normalleştir.
version: 1.0.0
phase: 17
lesson: 02
tags: [inference, fireworks, together, baseten, modal, replicate, anyscale, economics]
---

Bir iş yükü profili (model, günlük token'lar, sürekli kullanım, TTFT SLA, patlama faktörü, uyumluluk, Python'a karşı karma yığın) verildiğinde bir platform önerisi üret.

Üretilecekler:

1. **Birincil platform.** Platformu ve belirli fiyatlandırma kademesini (serverless vs dedicated vs batch) adlandır. Eşleşen iş yükü özellikleriyle gerekçelendir — ör. "TTFT < 500 ms SLA olduğu ve trafik patlamalı olduğu için Fireworks serverless."
2. **Efektif maliyet.** Seçili fiyatlandırma modelini $/M çıktı token'ı olarak normalleştir. En az iki alternatifle karşılaştır. Dakika-başına'nın token-başına'yı ne zaman yendiğini (~%30 üzeri sürekli kullanımda) veya tersini belirt.
3. **Soğuk başlangıç planı.** Serverless seçimler (Fireworks, Modal, Replicate) için beklenen soğuk başlangıç gecikmesini ve bir hafifletmeyi belirt (ön-ısıtma, min_workers=1, canlı-geçiş). Dedicated seçimler (Baseten, Anyscale) için bu bölümü atla ama takası not et.
4. **İkinci sıradaki.** İkinci platformu ve hangi açık koşul altında geçiş yapacağını adlandır (ör. "HIPAA + dedicated GPU gerektiren bir kurumsal anlaşma kaparsak Baseten'e geç").
5. **Ağ geçidi katmanı.** Ürünü sağlayıcı değişiminden yalıtmak için platformun önüne bir AI ağ geçidi (LiteLLM, Portkey, Kong AI Gateway) koymayı öner. Varsayılan: evet, ölçek 500 RPS'nin altında değilse.

**Hard rejects (zorunlu redler):**
- Token-başına'yı dakika-başına'ya normalleştirmeden karşılaştırmak. Reddet ve efektif $/M token'ı zorla.
- TTFT SLA'sını yayınlanmış kıyaslamalara karşı doğrulamadan Fireworks'u "en hızlı" olduğu için seçmek.
- Gecikme-bağlı olmayan herhangi bir iş yükü için özel silikon (Groq, Cerebras, SambaNova) önermek. Bunlar primli fiyatlandırılır ve yalnızca interaktif SLA'larda kendilerini haklı çıkarır.

**Reddetme kuralları:**
- İş yükü düzenlenmiş bir çerçeve (SOC 2 Type II, HIPAA) gerektiriyorsa ve müşteri Modal veya Replicate'ı seçtiyse, reddet — ikisinin de Baseten veya Anyscale kadar kurumsal ayak izi yok. Baseten öner.
- Beklenen trafik günde <100k token ise, dakika-başına (Baseten, Modal, Anyscale) önerme. Ekonomi çalışmaz — bir pazar yerine (OpenRouter, DeepInfra) veya yönetilen bir hiper-ölçekleyiciye varsay.
- Müşteri "en ucuzu" istiyorsa, reddet — çok-boyutlu maliyet fonksiyonunu adlandır (token oranı + soğuk başlangıç + atıf + ağ geçidi + DX).

**Çıktı:** Birincil platform, efektif maliyet, soğuk başlangıç planı, ikinci sıradaki, ağ geçidi duruşunu adlandıran tek sayfalık bir öneri. Yanlış seçimi ortaya çıkaracak tek metrikle bitir (soğuk başlangıç P99, token başına oran veya kullanım sapması).
