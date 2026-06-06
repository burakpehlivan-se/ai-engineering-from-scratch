---
name: positional-encoding-picker
description: Bağlam uzunluğu ve eğitim bütçesine göre konumsal kodlama (RoPE, ALiBi, sinüzoidal) + ölçekleme stratejisi seç
version: 1.0.0
phase: 7
lesson: 4
tags: [transformers, konumsal-kodlama, rope, alibi]
---

Bir transformer spesifikasyonu (çıkarımda hedef bağlam uzunluğu, eğitilmiş bağlam uzunluğu, ekstrapolasyon gereksinimi, ince-ayar token bütçesi) verildiğinde, aşağıdakileri üret:

1. Temel kodlama. Şunlardan biri: RoPE, ALiBi, sinüzoidal, öğrenilmiş mutlak. Tek cümlelik gerekçe.
2. Hiperparametreler. RoPE ise: `base` değeri, çift bölünme için `d_head` gereksinimi. ALiBi ise: eğim formülü. Sinüzoidal ise: `max_len`.
3. Uzatma stratejisi. Hedef > eğitilmiş ise: NTK-farkında ölçekleme faktörü, YaRN yapılandırması, LongRoPE spesifikasyonu veya konum-aradeğerleme oranı. İnce-ayar token bütçesini belirt.
4. Test planı. Maksimum bağlamda NIAH (samanlıktaki iğne, needle-in-a-haystack) geçme oranı hedefi, eğitilmiş uzunluk temel çizgisine göre X içinde karmaşıklık (perplexity).
5. Geri dönüş. Uzun bağlam değerlendirmesi başarısız olursa ne yapılmalı: daha büyük `base` ile yeniden eğit, ALiBi'ye geç veya dağıtılan bağlam uzunluğunu sınırla.

2026'da yeni modeller için sinüzoidal veya öğrenilmiş mutlak önerme — ekstrapolasyon yapmazlar ve her modern yığın RoPE veya ALiBi varsayar. İnce-ayar aşaması olmadan eğitilmiş uzunluğun 8 katı ötesinde RoPE ölçekleme. Tam dağıtılan uzunluk üzerinde NIAH çalıştırması olmadan uzun bağlam yapılandırması gönderme.
