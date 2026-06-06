---
name: video-vlm-frame-planner
description: Bir video-dil modeli dağıtımı için kare örnekleme, kare başına havuzlama, çıktı formatı ve kıyaslama hedeflerini planlayın.
version: 1.0.0
phase: 12
lesson: 17
tags: [video-vlm, temporal-grounding, tmrope, dynamic-fps, benchmarks]
---

Bir video görevi (eylem tanıma, zamansal yer-zemin ilişkisi, özetleme, izleme, ajan-iş akışı tekrarı) ve bir dağıtım kısıtı (model bağlamı, gecikme bütçesi, verim) verildiğinde, kare örnekleme ve çıktı planı yayınlayın.

Üretin:

1. Kare örnekleyici seçimi. Sabit içerik için tek düze; karışık hareket için dinamik-FPS; eylem-ağırlıklı için olay-tahrikli; sinematik için anahtar kare + bağlam.
2. Kare başına havuzlama. Yüksek detay için 2x2, varsayılan 3x3, ajan iş akışları için içerik yoğunluğunun kapsamdan daha az önemli olduğu yerde 4x4 veya 6x6.
3. Zamansal kodlama. Qwen2.5-VL ailesi için TMRoPE; daha küçük modeller için öğrenilmiş zamansal gömme; tek-klip görevleri için kodlama yok.
4. Çıktı formatı. Yer-zemin ilişkisi (grounding) için `{event, start, end, confidence}` ile JSON; özetleme için serbest metin; karışık akışlar için token-sınırlı.
5. Kıyaslama planı. Genel için VideoMME; yer-zemin ilişkisi için TempCompass; uzun-ufuk için EgoSchema. Beklenen doğruluk kademesini belirtin.
6. Bağlam / gecikme bütçesi. Toplam token = süre * fps * kare_başına_token. Bağlamın %40'ını aşarsa uyarın.

Sert reddetmeler:
- Eylem-ağırlıklı video için tek düze örnekleme önermek. Pik olayları kaybeder.
- Token-sınırlı çıktının aşağı akış ayrıştırma için JSON doğruluğuyla eşleştiğini iddia etmek. JSON daha sağlamdır.
- 2026'da başlayan herhangi bir proje için Video-LLaMA önermek. Eski mimariler artık rekabetçi değildir.

Ret kuralları:
- Süre > 10 dakika ve bağlam < 32k ise, reddedin ve hiyerarşik özetleme veya ajantik geri getirme (Ders 12.18) önerin.
- Hedef doğruluk sınırdaysa (VideoMME'de Gemini 2.5 Pro'nun 2 puanı içinde), açık 7B modelleri reddedin ve 32B+ veya tescilli gerektirin.
- Dinamik-FPS hedefi > 8 ise 7B'de > 30s bir klipte, reddedin ve daha düşük bir tavan önerin.

Çıktı: Örnekleyici, havuzlama, zamansal kodlama, çıktı formatı, kıyaslama hedefleri, bağlam tahmini ile tek sayfalık bir kare planı. Karşılaştırma okuması için arXiv 2502.13923 (Qwen2.5-VL) ve 2306.02858 (Video-LLaMA) ile bitirin.
