---
name: lm-baseline
description: Sinirsel bir dil modeli eğitmeden önce tekrarlanabilir bir n-gram dil modeli baseline'ı oluşturur.
phase: 5
lesson: 16
---

Bir derlem ve hedef kullanım (sonraki kelime tahmini, yeniden puanlama, perplexity baseline) verildiğinde şunu üretirsiniz:

1. N-gram derecesi. Genel İngilizce için trigram, derlem büyükse 4-gram, konuşma yeniden puanlaması için 5-gram.
2. Yumuşatma (smoothing). Modified Kneser-Ney varsayılandır; Laplace yalnızca öğretim amaçlıdır.
3. Kütüphane. Üretim için `kenlm`, öğretim için `nltk.lm`, matematiği öğrenmek için yalnızca sıfırdan yazın.
4. Değerlendirme. Eğitim ve test kümeleri arasında tutarlı tokenizasyon ile held-out perplexity (şaşkınlık).

Karşılaştırılan sistemler arasında farklı tokenizasyonla hesaplanan perplexity'yi raporlamayı reddedin — perplexity sayıları yalnızca özdeş tokenizasyon altında karşılaştırılabilir. Test kümesindeki OOV (sözlük dışı) oranını işaretleyin; KN, eğitim sırasında özel bir `<UNK>` token'ı ayırmadıkça OOV'yi zayıf işler.
