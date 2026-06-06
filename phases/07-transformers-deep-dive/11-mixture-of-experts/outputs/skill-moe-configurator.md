---
name: moe-configurator
description: Yeni bir MoE transformer için uzman sayısı, top-k, dengeleme stratejisi ve paylaşılan uzman düzeni seç
version: 1.0.0
phase: 7
lesson: 11
tags: [transformers, moe, uzman-karışımı, ölçekleme]
---

Bir transformer spesifikasyonu (toplam parametre bütçesi, token başına istenen aktif parametreler, mevcut eğitim tokenleri, çıkarım donanımı) verildiğinde, aşağıdakileri üret:

1. MoE düzeni. `n_experts`, `top_k`, `n_shared`. Sınır ölçekleri için ince-taneli (256+ uzman, top-8) seç; küçük ölçekler için klasik (8 uzman, top-2). Tek cümlelik gerekçe.
2. Dengeleme stratejisi. Yardımcı kayıpsız (DeepSeek-V3, varsayılan), Switch tarzı yardımcı kayıp veya uzman-kapasitesi + token bırakma. Yardımcı kayıpsız ise `γ` değerini adlandır.
3. Uzman paralelliği planı. VRAM göz önüne alındığında uzmanları GPU'lar arasında nasıl dağıtacağın. Uzman başına VRAM maliyetini ve toplam filo boyutunu belirt.
4. Yönlendirme hassasiyeti. fp32 yönlendirici skorları veya fp16. Yönlendirici hassasiyeti ölçekte önemlidir.
5. Başarısızlık modu kontrolü. Adlandırılmış risk: yönlendirici çöküşü, uzman açlığı, tümünden-tümüne ağ darboğazı, yönlendirme ek yükünden kaynaklanan çıkarım gecikmesi, kontrol noktası bellek ayak izi.

4B altında aktif parametre sayıları için MoE önerme — eşleşen hesaplamada yoğun kazanır. 2026'da yeni projeler için yalnızca yardımcı kayıp dengelemesi önerme (yardımcı kayıpsız varsayılandır). Toplam parametreler 80 GB'ı aşıyorsa uzman paralellik planı olmadan MoE gönderme. Tek kullanıcılı gecikme-kritik yollar için MoE'yi muhtemelen yoğun eşdeğerlerinden daha yavaş olarak işaretle.
