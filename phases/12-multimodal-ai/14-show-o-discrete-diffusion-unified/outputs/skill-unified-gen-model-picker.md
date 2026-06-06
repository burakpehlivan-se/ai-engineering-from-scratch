---
name: unified-gen-model-picker
description: Hem multimodal anlama hem de üretim gerektiren, açık ağırlık kısıtı olan bir ürün için Show-o / Transfusion / Emu3 / Janus-Pro aileleri arasında seçim yapın.
version: 1.0.0
phase: 12
lesson: 14
tags: [show-o, masked-diffusion, unified, t2i, inpainting]
---

Açık-ağırlık kısıtı ve gecikme bütçesi ile birleşik anlama + üretim (S/C, altyazılama, T2I, isteğe bağlı inpainting) gerektiren bir ürün verildiğinde, bir model ailesi seçin ve bir referans yapılandırma yayınlayın.

Üretin:

1. Aile kararı. Show-o (maskelenmiş ayrık difüzyon), Transfusion / MMDiT (sürekli difüzyon), Emu3 / Chameleon (otoregresif ayrık) veya Janus-Pro (ayrılmış kodlayıcılar).
2. Çıkarım adım bütçesi. Show-o için 16, Transfusion için 20, Emu3 için 1024+. Kullanıcının gecikme bütçesiyle seçimi gerekçelendirin.
3. Inpainting desteği. Show-o ücretsiz; Transfusion bir maske kanalı ekler; Emu3 ayrı bir ince ayar gerektirir. Bunu kullanıcı için işaretleyin.
4. Tokenleştirici seçimi. Ayrık aileler için IBQ / MAGVIT-v2 / SBER önerin; sürekli için SD3'ün VAE'ini önerin.
5. Eğitim kararlılığı. Transfusion (iki kayıp) ağırlık ayarı gerektirir; Show-o'nun tek kaybı daha temizdir.
6. Kullanıcı büyürse geçiş yolu. Kalite sınır olduğunda Show-o'dan Transfusion'a.

Sert reddetmeler:
- Görüntü başına çıkarım gecikmesi <10s olduğunda Emu3 / Chameleon önermek. ~1024 token üzerinden otoregresif çok yavaştır.
- Show-o'nun sınır görüntü kalitesinde Transfusion ile eşleştiğini iddia etmek. Eşleşmez. Tokenleştirici tavan.
- Ürün S/C gerektirdiğinde Stable Diffusion önermek. SD görüntüler hakkında akıl yürütemez.

Ret kuralları:
- Kullanıcı görüntü başına <2s üretim istiyorsa, Show-o'yu reddedin ve anlama için Stable Diffusion + ayrı bir VLM önerin. Çoklu-model karmaşıklığını kabul edin.
- Kullanıcı açık ağırlıklarla "sınıfının en iyisi kalite" istiyorsa, Show-o / Emu3'ü reddedin ve Transfusion ailesi (MMDiT) veya JanusFlow önerin.
- Kullanıcı bir tokenleştiriciye bağlanamıyorsa (lisanslama, kalite tavanı korkusu), yalnızca-ayrık aileleri reddedin ve Transfusion önerin.

Çıktı: Aile kararı, adım bütçesi, inpainting desteği, tokenleştirici önerisi, kararlılık planı ve geçiş yolu ile tek sayfalık bir seçim. arXiv 2408.12528 (Show-o), 2408.11039 (Transfusion), 2501.17811 (Janus-Pro) ile bitirin.
