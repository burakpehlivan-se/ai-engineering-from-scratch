---
name: tokenizer-vs-adapter-picker
description: Bir VLM projesi için Chameleon tarzı erken füzyon (paylaşılan-vocab tokenleştirici) ve LLaVA tarzı geç füzyon (donmuş LLM üzerinde adaptör) arasında seçim yapın.
version: 1.0.0
phase: 12
lesson: 11
tags: [chameleon, early-fusion, vq-vae, late-fusion, adapter]
---

Bir ürün spesifikasyonu (yalnızca-anlama veya anlama+üretim), hedef görüntü kalitesi (sosyal-medya paylaşımı / dergi / baskı / yayın) ve maliyet bütçesi (eğitim + çıkarım) verildiğinde, somut bir mimari ana hattıyla Chameleon ailesi veya LLaVA ailesi önerin.

Üretin:

1. Karar. Erken-füzyon (Chameleon / Emu3 / AnyGPT) veya geç-füzyon (LLaVA / BLIP-2 / Qwen-VL) ailesi.
2. Tokenleştirici seçimi (erken-füzyon kararları için). VQ-VAE (Chameleon), MAGVIT-v2, IBQ veya SBER-MoVQGAN; PSNR'de beklenen yeniden yapılandırma tavanını belirtin.
3. Eğitim kararlılığı planı. Ölçekte erken-füzyon için QK-Norm, dropout yerleşimi, LayerNorm sıralaması.
4. Maliyet tahmini. Eğitim GPU saatleri ve görüntü başına çıkarım gecikmesi, geç-füzyon alternatifine karşı.
5. Üretim kalitesi tavanı. Kullanıcının bekleyebileceği PSNR / FID aralığı; ürünün kalite çubuğunun ayrık token'larla ulaşılabilir olup olmadığı veya sürekli (Transfusion tarzı) üretim gerektirip gerektirmediği.
6. Geçiş yolu. Kullanıcı büyürse ve geç-füzyon sınırlayıcı olursa (görüntü çıktısına ihtiyaç duyarsa), geçiş neye benzer.

Sert reddetmeler:
- Yalnızca-anlama ürünleri için Chameleon tarzı önermek. Geç-füzyon, saf anlama için daha basit, daha ucuz ve daha yüksek tavanlıdır.
- Üretim görüntü üretimi için K<4096 ile VQ-VAE önermek. Kod kitabı çok küçük, artifaktlar görünür.
- Erken-füzyon çıkarımının ücretsiz olduğunu iddia etmek. VQ kod çözücü, üretilen görüntü başına 50-200ms ekler, genellikle LLM çıktı süresinden fazla.

Ret kuralları:
- Kullanıcı sınır kalitesinde görüntü üretimi (FID < 15, baskıya hazır) istiyorsa, ayrık token'ları reddedin ve Transfusion / Stable Diffusion 3 / MMDiT'e (Ders 12.13) işaret edin.
- Ürünün görüntü çıktısına asla ihtiyacı yoksa, erken-füzyonu reddedin -- karmaşıklık gereksizdir.
- Kullanıcı mevcut Llama / Qwen LLM ağırlıklarını takmak istiyorsa, erken-füzyonu reddedin -- yeni bir modeli sıfırdan ön-eğitmeyi gerektirir.

Çıktı: Karar, tokenleştirici seçimi, kararlılık kontrol listesi, maliyet tahmini, kalite tavanı, geçiş yolu ile tek sayfalık bir plan. Karşılaştırma okuması için arXiv 2405.09818 (Chameleon) ve 2408.11039 (Transfusion) ile bitirin.
