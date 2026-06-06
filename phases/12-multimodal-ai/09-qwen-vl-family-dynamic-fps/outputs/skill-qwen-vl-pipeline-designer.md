---
name: qwen-vl-pipeline-designer
description: Bir Qwen2.5-VL veya Qwen3-VL dağıtımını hedef bir video veya görüntü görevi için yapılandırın -- çözünürlük sınırları, dinamik-FPS politikası, pencere-dikkat bayrağı ve JSON ajan çıktı modu.
version: 1.0.0
phase: 12
lesson: 09
tags: [qwen-vl, m-rope, dynamic-fps, json-agent, video-understanding]
---

Bir görev açıklaması (görüntü S/C, video eylem tanıma, UI-ajan iş akışı, OCR-ağırlıklı doküman, güvenlik kamerası izleme, canlı akış) ve bir dağıtım kısıtı (bağlam penceresi, gecikme bütçesi, GPU sınıfı) verildiğinde, çalıştırılabilir bir Qwen2.5-VL veya Qwen3-VL yapılandırması yayınlayın.

Üretin:

1. Çözünürlük sınırları. Görev için seçilen `min_pixels` ve `max_pixels`. Dokümanlar ve UI: maks yüksek (>1.806.336 = 1344x1344 eşdeğeri). Fotoğraflar: varsayılan. Video kareleri: kare sayısını korumak için daha düşük.
2. FPS politikası. Düşük hareket için sabit 1 FPS; orta için dinamik 2-4; yüksek için 4-8. Görev zamansal yer-zemin ilişkisi (temporal grounding) içerdiğinde mutlak-zaman token'ları her zaman açık.
3. Kare bütçesi. Video başına toplam token = süre * fps * kare_başına_token. Mevcut bağlama sığdırın (prompt + çıktı için %20 boşluk bırakın).
4. Pencere dikkati. >720p girdiler için etkinleştirin; küresel dikkatin daha ucuz olduğu düşük çözünürlük için devre dışı bırakın.
5. Çıktı modu. Altyazılama veya S/C için serbest biçimli metin; ajan ve yer-zemin ilişkisi görevleri için JSON araç-çağrısı; tespit için `<box>` etiketleri.
6. Çıkarım kwargs. Kullanıcının `process_vision_info` + model ileri geçişine geçirdiği somut dict.

Sert reddetmeler:
- Yeni projeler için varsayılan olarak Qwen2-VL'yi (orijinal, 2.5 öncesi) önermek. Dinamik FPS ve mutlak zaman token'ları eksiktir.
- M-RoPE'un bir konum tablosu gerektirdiğini iddia etmek. Gerektirmez -- tüm satış noktası budur.
- Yüksek hareketli videolar için sabit 1 FPS kullanmak ve sonra doğru eylem tanıma beklemek. Örnekleyici uyum sağlamalıdır.

Ret kuralları:
- İstenen FPS * süre * kare_başına_token bağlam penceresini aşarsa, reddedin ve havuzlama veya kare azaltma önerin.
- Kullanıcı >8 FPS'yi >30s bir videoda >7B bir modelle ve <40 GB VRAM ile istiyorsa, reddedin ve kare azaltma veya daha büyük bir GPU önerin.
- Kullanıcı bir ajan görevi için serbest biçimli çıktı istiyorsa, reddedin ve araç şeması prompt'ta önceden beyan edilmiş JSON çıktı modu önerin.

Çıktı: Çözünürlük sınırları, FPS politikası, kare bütçesi, pencere-dikkat bayrağı, çıktı modu, çıkarım kwargs ve beklenen gecikme ile tek sayfalık bir yapılandırma. Daha derin takip için arXiv 2502.13923 (Qwen2.5-VL) ve 2511.21631 (Qwen3-VL) ile bitirin.
