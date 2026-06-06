---
name: sequence-architecture-picker
description: Uzunluk, çıktı hacmi (throughput) ve eğitim bütçesine göre dizi mimarisi (RNN, transformer, SSM, hibrit) seç
version: 1.0.0
phase: 7
lesson: 1
tags: [transformers, mimari, rnn, ssm]
---

Bir dizi problemi (maksimum uzunluk, parti şekli, eğitim token bütçesi, çıkarım gecikme hedefi, cihaz sınıfı) verildiğinde, aşağıdakileri üret:

1. Birincil mimari. Şunlardan biri: transformer, durum-uzaylı model (Mamba/RWKV), hibrit SSM+attention, RNN. Baskın kısıtlamaya bağlı tek cümlelik gerekçe.
2. Bağlam uzunluğu stratejisi. Transformer ise: tam dikkat kesme noktası, kayan pencere boyutu, RoPE ölçekleme faktörü. SSM ise: tarama parça boyutu. RNN ise: gizli genişlik.
3. Eğitim FLOP profili. Mimari + bağlamdan token başına yaklaşık FLOP'lar; spesifikasyonun hesaplama bütçesine uyup uymadığını belirt.
4. Çıkarım bellek profili. Transformer'lar için KV önbelleği, SSM'ler için durum boyutu, RNN'ler için token başına bellek. Hedef cihazın 1 partiyi tutamadığı durumları işaretle.
5. Risk notu. Bu seçimin spesifikasyonun ölçeğinde bilinen belirli bir başarısızlık modu (örneğin 24 GB GPU'da Flash Attention olmadan 64K bağlamda transformer OOM).

1B token üzerindeki herhangi bir eğitim çalışması için saf RNN önerme; gradyan akışı ve paralellik cezalarını açıkça belirt. 64K üzeri bağlam için tam dikkatli transformer önerme; `O(N^2)` bellek maliyetini belirt. Üretim için 12 aydan kısa süre önce yayımlanmış yeni bir mimariyi, adlandırılmış bir geri dönüş seçeneği olmadan önerme.
