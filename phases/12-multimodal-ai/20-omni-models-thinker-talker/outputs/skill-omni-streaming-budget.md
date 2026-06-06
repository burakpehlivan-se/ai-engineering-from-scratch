---
name: omni-streaming-budget
description: Hedef TTFAB ve özellik seti için Thinker-Talker akışlı ses işlem hattını (Qwen-Omni / Moshi / Mini-Omni) boyutlandırın.
version: 1.0.0
phase: 12
lesson: 20
tags: [qwen-omni, moshi, mini-omni, streaming, ttfab, thinker-talker]
---

Ses-öncelikli bir ürün spesifikasyonu (hedef TTFAB, mikrofon örnekleme hızı, görüntü girdi evet/hayır, iki dilli, tam çift yönlü) ve bir hesaplama kısıtı (GPU sınıfı, bütçe) verildiğinde, Thinker-Talker işlem hattını boyutlandırın.

Üretin:

1. Model ailesi seçimi. Moshi (en iyi gecikme), Qwen2.5-Omni (en iyi açık özellikler), Qwen3-Omni (sınır kalite), Mini-Omni (en basit).
2. Thinker ve Talker boyutları. <400ms TTFAB için 7B Thinker + 200-300M Talker. Kalite için 70B+ Thinker, daha yüksek TTFAB'yi kabul edin.
3. TTFAB dökümü. Bileşen-bileşen gecikme tahmini.
4. Çift yönlü mod. Varsayılan olarak VAD turn-taking ile yarı-çift yönlü; ürün geri-kanal (backchannel) gerektiriyorsa tam çift yönlü.
5. Görüntü entegrasyonu. İç içe geçmiş video kareleri için mutlak zaman damgalarıyla TMRoPE.
6. Dağıtım şekli. Verim ihtiyaçlarına göre tek-GPU veya bölünmüş (Thinker A'da, Talker B'de).

Sert reddetmeler:
- 70B Talker önermek. Talker, konuşma token hızına ayak uydurmak için küçük olmalıdır.
- Akış-dışı konuşma kod çözücüsü kullanmak. TTFAB patlar.
- Tam çift yönlünün tak-çalıştır olduğunu iddia etmek. Özelleşmiş eğitim verisi gerektirir.

Ret kuralları:
- Hedef TTFAB <200ms ise, tek bir A100 üzerinde Moshi-sınıfı (7B füzyonlu) daha büyük herhangi bir şeyi reddedin.
- Ürün akışta müzik üretimi gerektiriyorsa, bu mimariyi reddedin ve ayrı bir müzik işlem hattı önerin.
- Mikrofon örnekleme hızı 48kHz ve sıkı kalite ise, daha güçlü bir konuşma kodlayıcısı ihtiyacını işaretleyin; körlemesine aşağı örneklemeyin.

Çıktı: Model seçimi, boyutlar, TTFAB dökümü, çift yönlü mod, görüntü stratejisi, dağıtım ile tek sayfalık bir akış planı. arXiv 2503.20215 (Qwen2.5-Omni), 2410.00037 (Moshi) ile bitirin.
