---
name: mc-evaluator
description: Bir politikayı Monte Carlo rollout'ları ile değerlendir ve varsa DP-karşılaştırması ile bir yakınsama raporu üret
version: 1.0.0
phase: 9
lesson: 3
tags: [rl, monte-carlo, değerlendirme]
---

Bir ortam (epizodik, sıfırlama+adım API'si ile) ve bir politika verildiğinde, aşağıdakileri üret:

1. Yöntem. İlk-ziyaret vs her-ziyaret MC. Gerekçe.
2. Epizod bütçesi. Hedef sayı, varyans teşhisi, beklenen standart hata.
3. Keşif planı. ε zamanlaması (gerekirse) veya keşif başlangıçları.
4. Altın standart karşılaştırma. Tablo ise DP-optimal V*; aksi takdirde bir Q-öğrenme / PPO temel çizgisinden bir sınır.
5. Sonlandırma kontrolü. Maks-adım tavanı, zaman aşımları, sonlanmayan yörüngelerin işlenmesi.

Epizodik olmayan görevlerde sonlu ufuk tavanı olmadan MC çalıştırma. Tablo görevleri için durum başına 100'den az epizottan V^π tahminleri raporlama. Sıfır-varyans eylemlere sahip herhangi bir politikayı keşif riski olarak işaretle.

Geri dönüş. Varyans kabul edilemez düzeydeyse (CI yarı genişliği ortalamanın >%10'u), epizod sayısını 2-4× artır veya kontrol değişkeni (kovaryant) olarak bir temel değer tahmincisi ekle.
