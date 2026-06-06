---
name: checkpointing-planner
description: Bir eğitim konfigürasyonu ve HBM bütçesi verildiğinde, katman başına aktivasyon yeniden hesaplama politikası (yok / seçici / tam / offload) seçin.
version: 1.0.0
phase: 10
lesson: 34
tags: [gradient-checkpointing, activation-recomputation, selective-checkpoint, fsdp-offload, training-memory]
---

Eğitim konfigürasyonu (katman sayısı L, gizli boyut d, dizi uzunluğu S, mikro-parti B, değer başına dtype bayt, attention çekirdeği, tensör paralel derecesi TP, pipeline paralel derecesi PP, MoE ise uzman paralel derecesi EP) ve ağırlıklar ve optimizer durumundan sonra sıralama başına HBM bütçesi verildiğinde, çıktı:

1. Katman başına politika. Yığındaki her katman ailesi için (embedding, attention, FFN, MoE uzman, norm, çıktı kafası) yok, seçici, tam veya offload seçin. S, 4_096'yı aştığında attention için varsayılan seçici; artık akışlar (residual streams) ve normlar için varsayılan yok; o katmanın aktivasyonları için ölçülen PCIe aktarım süresi ölçülen yeniden hesaplama süresinden az olduğunda FFN'de yalnızca varsayılan offload.
2. Segment boyutu k. Tam kontrol noktalama açıksa, k'yı düzgün katman maliyeti için round(sqrt(L)) olarak, aktivasyon belleği bütçeye hakim olduğunda daha küçük k olarak seçin. Ekstra FLOP yüzdesini ileri FLOP'ların (1/k) katı olarak raporlayın.
3. FlashAttention etkileşimi. Attention çekirdeğinin zaten softmax'ı yeniden hesaplayıp hesaplamadığını doğrulayın. Evet ise, seçici attention kontrol noktalaması az şey satın alır; yok'a düşürün. Çekirdeği ada göre belirtin (FlashAttention-2/3, xFormers bellek-verimli, vanilya).
4. TP / PP planı. TP için, yeniden hesaplamada toplanması veya yeniden saçılması gereken aktivasyonları ve eklenen adım başına iletişim baytlarını adlandırın. PP için, hangi pipeline aşamalarının uçtan uca kontrol noktalandığını doğrulayın, böylece ters mikro-partiler aktivasyon belleğini geri akmadan önce serbest bırakır.
5. Bütçe matematiği. Politika öncesi ve sonrası aktivasyon belleğini (sıralama başına MB olarak) tahmin edin. FLOP ek yükünü fwd+bwd yüzdesi olarak tahmin edin. %10 yedek alanla HBM bütçesine sığmayan herhangi bir planı reddedin.

Seçici attention'ın tek başına bütçeyi kapattığı her katmanda tam kontrol noktalamayı reddedin; profil, aynı bellek tasarrufu için FLOP ek yükünün seçici olandan birçok kat daha yüksek olduğunu gösterir ve kesin oran iş yüküne özgüdür. Katmanın hedef PCIe bağlantısı üzerindeki ölçülen aktivasyon aktarım süresi ölçülen yeniden hesaplama süresini aştığında offload'ı reddedin; yeniden hesaplama kazanır. Seçilen çerçeve amax geçmişini anlık görüntülemediğinde FP8 eğitimi için "her yerde kontrol noktası"nı reddedin; yeniden hesaplama ölçeği saptıracak ve gradyanları sessizce bozacaktır.

Örnek girdi: "L=64, d=8192, S=8192, B=1, bf16, FlashAttention-3, TP=8, PP=4, ağırlıklardan sonra sıralama başına 32 GB HBM bütçesi, 8 uzmanlı ve EP=8 ile MoE."

Örnek çıktı:
- Katman başına politika: attention seçici, FFN yok, MoE uzman tam, embedding yok, çıktı kafası offload.
- Segment boyutu: tam yalnızca MoE üzerinde k=8'de uygulanır; FLOP ek yükü uzman yolunda yüzde 12, başka yerde 0.
- FlashAttention etkileşimi: FA-3 zaten softmax'ı yeniden hesaplar; çekirdeğin içinde değil, katman sarmalayıcısında seçici.
- TP / PP planı: yeniden hesaplamada attention girdisinin TP toplaması, adım başına 0.3 GB ekstra iletişim; PP aşamaları her biri tam ileri geçişlerini kontrol noktalar; PP aşaması 3, son geri geçiş için aktivasyonlarını tutar.
- Bütçe matematiği: politikasız aktivasyonlar 38 GB, politikayla 11 GB. Toplam FLOP ek yükü yüzde 7.5 fwd+bwd.
