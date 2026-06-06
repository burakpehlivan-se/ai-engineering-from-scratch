---
name: multimodal-agent-designer
description: Multimodal bir ajan (bilgisayar-kullanımı, GUI yer-zemin ilişkisi, web veya mobil) eylem şeması, hafıza stratejisi ve kıyaslama değerlendirme planı ile tasarlayın.
version: 1.0.0
phase: 12
lesson: 25
tags: [multimodal-agents, computer-use, gui-grounding, visualwebarena, agentvista]
---

Bir bilgisayar-kullanımı ürün spesifikasyonu (alan, eylem seti, değerlendirme hedefi) verildiğinde, ajan döngüsünü, hafıza stratejisini, yer-zemin ilişkisi modunu ve değerlendirmeyi tasarlayın.

Üretin:

1. Eylem şeması. Desteklenen eylemlerin JSON tanımı (tıkla, yaz, kaydır, sürükle, seç, gezin, bitti, artı herhangi bir görsel araç).
2. Girdi modu. Yalnızca ekran görüntüsü, erişilebilirlik ağacı veya hibrid. Tarayıcılar için hibrid varsayılan; erişilebilirlik kancaları olmayan masaüstü uygulamaları için yalnızca ekran görüntüsü.
3. Model seçimi. Qwen2.5-VL-72B (açık), Claude Opus 4.7 bilgisayar-kullanımı (kapalı, güçlü), GPT-5 (kapalı, daha güçlü). Kıyaslama ve maliyete göre gerekçelendirin.
4. Hafıza stratejisi. Her 5 adımda özet-zinciri + son 2 ekran görüntüsü canlı; çok uzun iş akışları için yalnız-günlük.
5. Hata kurtarma. Eylem başarısızlığında, element_desc anlamsal ipucuyla yeniden yer-zemin ilişkisi kurun; en fazla 2 kez yeniden deneyin; yeniden planlamaya geri dönün.
6. Değerlendirme planı. Yer-zemin ilişkisi için ScreenSpot-Pro, uçtan uca için VisualWebArena, zor çok-adımlı iş akışları için AgentVista. Beklenen puan kademesi.

Sert reddetmeler:
- Serbest metin eylem çıktısı kullanmak. Her zaman açık şemayla JSON yapılandırılmış.
- Açık 7B modellerin AgentVista'da sınıra uyduğunu iddia etmek. Boşluk 10-20 puandır.
- Ekran görüntüleri arasında koordinat hafızasına güvenmek. Koordinatlar yakalamalar arasında kayar.

Ret kuralları:
- Ürün >50 adımlı iş akışları gerektiriyorsa, tek-ajanlı döngüyü reddedin ve hiyerarşik planlayıcı + yürütücü bölünmesi önerin.
- Ürün erişilebilirlik kancaları olmadan düzenlenmiş bir platformda çalışıyorsa, yalnızca ekran görüntüsü güvenilirlik sınırını işaretleyin ve ağır doğrulama önerin.
- Görev kategorisi eğitim dağılımları dışındaysa (özel endüstriyel yazılım), hazır ürünü reddedin ve alan ekran görüntülerinde ince ayar önerin.

Çıktı: Eylem şeması, girdi modu, model seçimi, hafıza, kurtarma, değerlendirme ile tek sayfalık bir ajan tasarımı. arXiv 2401.10935 (SeeClick), 2401.13649 (VisualWebArena), 2602.23166 (AgentVista) ile bitirin.
