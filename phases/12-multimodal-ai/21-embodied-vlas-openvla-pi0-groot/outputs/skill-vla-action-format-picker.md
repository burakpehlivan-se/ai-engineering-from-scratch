---
name: vla-action-format-picker
description: Bir robot görevi için eylem formatı (ayrık kutu, FAST, akış eşleme, çift-sistem) ve VLA ailesi (RT-2, OpenVLA, π0, GR00T) seçin.
version: 1.0.0
phase: 12
lesson: 21
tags: [vla, rt-2, openvla, pi0, groot, action-tokenization]
---

Bir robot görevi (manipülasyon, navigasyon, tüm-vücut insansı), DOF sayısı, kontrol hızı gereksinimi ve hesaplama kısıtı verildiğinde, bir eylem formatı ve bir VLA ailesi seçin.

Üretin:

1. Eylem formatı. Basit tek-kol görevleri için ayrık-kutu, hız-hassas yörüngeler için FAST, pürüzsüz sürekli kontrol için akış eşleme, insansılar için çift-sistem.
2. VLA ailesi seçimi. RT-2 (kapalı), OpenVLA (açık 7B), π0 (açık akış), GR00T N1 (açık çift-sistem insansı).
3. Kontrol hızı uygulanabilirliği. Format verimini gerekli kontrol Hz ile eşleştirin. Ayrık kutu 7B modelde >10 Hz yapamaz.
4. Eğitim verisi karışımı. Birlikte-ince-ayarlama oranı (web S/C : robot). 0.5:1'den başlayın, göreve göre ayarlayın.
5. İnce ayar planı. ~500-1000 görev demosunda LoRA; ~10k demo'da tam ince ayar.
6. Güvenlik kapıları. VLA dışında gerekli kontrol katmanı kontrolleri.

Sert reddetmeler:
- Güvenlik katmanı spesifikasyonu olmadan VLA önermek. Her zaman eklem sınırları, hız kırpma dahil edin.
- Ayrık-kutu tokenleştirmesinin 30 Hz kontrol için yeterince hızlı olduğunu iddia etmek. Değildir.
- Yeterli pürüzsüzlük kısıtlamaları olmadan akış eşleme önermek. Dağılım dışı eylemler hâlâ olur.

Ret kuralları:
- Kontrol hızı gereksinimi ayrık-kutu formatıyla <=7B modelde >50 Hz ise, reddedin; π0 veya özelleşmiş bir kafa önerin.
- Robot >30 DOF'a sahipse (insansı), tek-aşamalı mimarileri reddedin; çift-sistem (GR00T) gerektirin.
- Bütçe Open X-Embodiment-ölçekli ön-eğitimi karşılayamıyorsa, sıfırdan VLA'yı reddedin; OpenVLA ince ayarını önerin.

Çıktı: Eylem formatı, VLA seçimi, kontrol hızı kontrolü, birlikte-ince-ayarlama karışımı, güvenlik kapıları ile tek sayfalık bir plan. arXiv 2307.15818 (RT-2), 2406.09246 (OpenVLA), 2410.24164 (π0), 2503.14734 (GR00T) ile bitirin.
