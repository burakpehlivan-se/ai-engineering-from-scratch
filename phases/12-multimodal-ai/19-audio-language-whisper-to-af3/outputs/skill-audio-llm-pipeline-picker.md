---
name: audio-llm-pipeline-picker
description: Bir ses görevi için kademeli (Whisper + LLM) veya uçtan-uca (AF3 / Qwen-Audio) arasında seçim yapın, artı kodlayıcı ve köprü yapılandırmasını seçin.
version: 1.0.0
phase: 12
lesson: 19
tags: [whisper, audio-flamingo-3, qwen-audio, cascaded, end-to-end]
---

Bir ses görevi (transkripsiyon, özetleme, konuşmacı ayrımı, duygu, müzik, çevresel sesler, deepfake, zamansal yer-zemin ilişkisi) ve bir dağıtım kısıtı verildiğinde, bir işlem hattı seçin ve bir yapılandırma yayınlayın.

Üretin:

1. İşlem hattı seçimi. Yalnızca transkripsiyon veya temiz konuşmanın yalnızca özetlenmesi için kademeli; herhangi bir akustik görev için uçtan-uca (AF3 / Qwen-Audio).
2. Kodlayıcı yığını. Whisper-large-v3 (konuşma-güçlü), BEATs (müzik-güçlü), AF-Whisper birleştirme (dengeli).
3. Köprü yapılandırması. Akış-dışı için Q-former 32-64 sorgu; akış için RVQ token'ları.
4. LLM seçimi. Maliyet için Qwen2.5-7B, kalite için Qwen2.5-72B veya AF3'ün omurgası.
5. Talep-üzerine zincir-düşünce (CoT). MMAU benzeri akıl yürütme görevleri için etkinleştirin; transkripsiyon verimi için devre dışı bırakın.
6. MMAU beklenen doğruluğu. Kademeli ~0.50, Qwen-Audio ~0.60, AF3 ~0.72, Gemini 2.5 Pro ~0.78.

Sert reddetmeler:
- Müzik veya duygu görevleri için kademeli önermek. Akustik sinyal kaybolur.
- Çok-görevli ses için <32 sorgu ile Q-former kullanmak. Akıl yürütme için yetersiz tokenlanmış.
- Whisper'ın yalnızca müziği işlediğini iddia etmek. Konuşma-ağırlıklı veri üzerinde eğitildi.

Ret kuralları:
- Kullanıcı akış konuşma (gerçek zamanlı konuşma girdi / konuşma çıktı) gerektiriyorsa, Q-former tabanlı AF3'ü reddedin ve Moshi veya Qwen-Omni (Ders 12.20) önerin.
- Gecikme bütçesi <500ms ve hedef basit transkripsiyon ise, akış Whisper ile kademeli önerin.
- Görev yeni bir ses görevi ise (deepfake, sıkıştırma artifaktı tespiti), hazır ürünü reddedin ve sentetik veriyle AF3 üzerinde ince ayar önerin.

Çıktı: İşlem hattı seçimi, kodlayıcı yığını, köprü yapılandırması, LLM seçimi, CoT bayrağı, beklenen doğruluk ile tek sayfalık bir plan. Daha derin okuma için arXiv 2212.04356 (Whisper) ve 2507.08128 (AF3) ile bitirin.
