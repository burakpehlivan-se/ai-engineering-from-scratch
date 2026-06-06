---
name: long-video-strategy-planner
description: Uzun-video anlama görevi için kaba-bağlam, halka-dikkat (ring-attention), token-sıkıştırma veya ajantik-geri getirme arasında seçim yapın ve gecikme + geri çağırma beklentilerini hesaplayın.
version: 1.0.0
phase: 12
lesson: 18
tags: [long-video, gemini, ring-attention, videoagent, retrieval]
---

Bir video süresi, sorgu karmaşıklığı (tek olay vs bütünsel özet) ve açık vs kapalı kısıtlar verildiğinde, uzun-video stratejisi seçin ve bir yapılandırma yayınlayın.

Üretin:

1. Strateji seçimi. Kaba-bağlam, halka-dikkat (LongVILA), token-sıkıştırma (Video-XL) veya ajantik-geri getirme (VideoAgent).
2. Token bütçesi. Süre * FPS * kare_başına_token. LLM bağlamını aşarsa uyarın.
3. Beklenen geri çağırma. İğne-samanlıkta geri çağırma video-uzunluk yüzdelerinde. İlgili olduğunda Gemini 1.5 raporlarına atıfta bulunun.
4. Gecikme. Kaba-bağlam için prefill süresi; ajantik için geri getirme + VLM.
5. Mühendislik yolu. Seçilen strateji için kod parçacığı iskeleti.
6. Geri dönüş planı. Hibrid: kaba-bağlam küresel özet + ajantik yerel detay.

Sert reddetmeler:
- Açık 72B modelde 2 saatlik bir video için kaba-bağlam önermek. Bağlam sığmaz.
- Aantik geri getirmenin her zaman kazandığını iddia etmek. Bütünsel-özet soruları için kaba-bağlama kaybeder.
- Geri çağırma vergisini işaretlemeden token sıkıştırma önermek.

Ret kuralları:
- Hedef 90 dakikalık bir video sınır geri çağırmada (>%95) ise, açık-yalnız seçenekleri reddedin ve Gemini 2.5 Pro önerin.
- Kullanıcı araç-çağrısı döngülerini karşılayamıyorsa, ajantik-geri getirmeyi reddedin ve sıkıştırılmış kaba-bağlam önerin.
- Kullanıcı gerçek zamanlı (oynadıkça akış) gerektiriyorsa, geri getirmeyi reddedin (çok yavaş) ve akış Qwen2.5-VL önerin.

Çıktı: Strateji, bütçe, geri çağırma, gecikme, mühendislik yolu ve geri dönüş ile tek sayfalık bir plan. Karşılaştırma için arXiv 2403.05530 (Gemini 1.5) ve 2403.10517 (VideoAgent) ile bitirin.
