---
name: decoupled-encoder-picker
description: Birleşik bir VLM'nin görsel kodlayıcılarını ayırıp ayırmayacağına karar verin ve Janus-Pro, JanusFlow ve InternVL-U arasında seçim yapın.
version: 1.0.0
phase: 12
lesson: 15
tags: [janus-pro, janusflow, internvl-u, decoupled-encoders, unified-model]
---

Birleşik-model spesifikasyonu (anlama + üretim, isteğe bağlı düzenleme / inpainting), bir hesaplama bütçesi ve bir açık-ağırlık kısıtı verildiğinde, ayrılmış-kodlayıcı bir mimari ve somut bir yapılandırma önerin.

Üretin:

1. Mimari seçimi. Janus-Pro (VQ üretim), JanusFlow (düzeltilmiş akış üretim), InternVL-U (yerel ön-eğitim + ayrılmış).
2. Kodlayıcı kombinasyonu. Anlama için SigLIP-SO400m; ayrık üretim için MAGVIT-v2 / IBQ VQ; sürekli için SD3 tarzı VAE.
3. Veri aşaması planı. Aşama 1 hizalama (50-100M çift), Aşama 2 birleşik (70M+ çift), Aşama 3 talimat (1M+ örnek). Janus-Pro'nun 5.4x model + 2.8x veri ölçeklendirme sonucuna atıfta bulunun.
4. Yönlendirme stratejisi. Prompt-etiket tabanlı (açık `<understand>` / `<generate>`) veya görev-sınıflandırıcı tabanlı.
5. Paylaşılan-gövde başlatması. Sıfırdan değil, önceden eğitilmiş bir LLM'den (DeepSeek, Qwen, Llama) başlatın.
6. Kalite tavanı. Beklenen MMMU (7B'de ~60) ve GenEval (Janus-Pro için 7B'de ~0.80 / InternVL-U için ~0.85+).

Sert reddetmeler:
- Kullanıcının kalite çubuğu her iki taraf için de sınır-rekabetçi olduğunda tek-kodlayıcılı birleşik bir model (Show-o / Transfusion) önermek. Ayrılmış yaklaşım tek yoldur.
- <10B model için sıfırdan ön-eğitim önermek. Önceden eğitilmiş bir LLM gövdesini yeniden kullanın.
- Herhangi bir yeni proje için Janus (orijinal) yerine Janus-Pro önermek. Janus-Pro halefidir.

Ret kuralları:
- Kullanıcı yalnızca anlama gerektiriyorsa, ayrılmışı reddedin ve LLaVA ailesi önerin. Bir kodlayıcı yeterlidir.
- Kullanıcı yalnızca üretim gerektiriyorsa, reddedin ve Stable Diffusion 3 / Flux önerin -- uzmanlar hâlâ T2I kalitesinde kazanır.
- Hesaplama <50k GPU saati ise, InternVL-U'yu (yerel ön-eğitim gerektirir) reddedin ve Janus-Pro (önceden eğitilmiş LLM'yi yeniden kullanır) önerin.

Çıktı: Mimari seçimi, kodlayıcı kombinasyonu, aşama planı, yönlendirme, paylaşılan-gövde başlatması ve kalite tavanı ile tek sayfalık bir plan. arXiv 2501.17811 (Janus-Pro), 2411.07975 (JanusFlow), 2603.09877 (InternVL-U) ile bitirin.
