---
name: sentiment-baseline
description: Yeni bir veri kümesi için duygu analizi baseline'ı tasarlar.
phase: 5
lesson: 05
---

Bir veri kümesi açıklaması (alan, dil, boyut, etiket ayrıntı düzeyi, gecikme bütçesi) verildiğinde şunu üretirsiniz:

1. Özellik çıkarma reçetesi. Tokenizer'ı, n-gram aralığını, stopword politikasını (genellikle tutun), olumsuzlama işleme yöntemini (kapsamlı önek veya bigram).
2. Sınıflandırıcı. Baseline için Naive Bayes, üretim için lojistik regresyon, yalnızca alan ironi/aspect-tabanlı çıktı ya da çapraz dil kapsamı gerektiriyorsa transformer.
3. Değerlendirme planı. Precision (kesinlik), recall (duyarlılık), F1, karışıklık matrisi (confusion matrix) ve sınıf başına hata örneklerini raporlayın. Dengesiz veride asla yalnızca doğruluk (accuracy) raporlamayın.
4. Yayından sonra izlenecek bir başarısızlık modu. Alan kayması (domain drift) ve ironi en yaygın ilk ikidir. Haftalık örnek denetimi önerin.

Duygu görevleri için stopword'leri düşürmeyi önermeyi reddedin. Sınıflar dengesiz olduğunda accuracy'yi tek metrik olarak raporlamayı reddedin. Alt-kelime (subword) açısından zengin dilleri (Almanca, Fince, Türkçe) FastText veya transformer embedding'leri gerektiriyor olarak işaretleyin; kelime düzeyinde TF-IDF yetersiz kalır.
