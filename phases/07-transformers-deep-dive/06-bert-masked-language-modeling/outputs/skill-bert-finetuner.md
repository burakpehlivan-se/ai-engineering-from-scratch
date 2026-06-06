---
name: bert-finetuner
description: Yeni bir sınıflandırma, çıkarma veya erişim (retrieval) görevi için BERT ince-ayar kapsamı belirle
version: 1.0.0
phase: 7
lesson: 6
tags: [bert, ince-ayar, nlp]
---

Bir alt görev (sınıflandırma / NER / erişim / yeniden sıralama / NLI), etiketli veri boyutu ve dağıtım kısıtlamaları (gecikme, cihaz) verildiğinde, aşağıdakileri üret:

1. Omurga seçimi. Model adı (ModernBERT-base / large, DeBERTa-v3, multilingual-e5 vb.) ve tek cümlelik gerekçe. ≤8K bağlam gerektiren İngilizce görevler için ModernBERT'i tercih et.
2. Kafa spesifikasyonu. Sınıflandırma: `[CLS]` → dropout → linear(num_classes). NER: token başına linear + isteğe bağlı CRF. Erişim: ortalama havuzlama (mean-pool) + karşıtlık kaybı.
3. Eğitim reçetesi. Optimizer (AdamW, tipik lr 2e-5), ısınma yüzdesi (%6–10), epoch (3–5), parti boyutu, fp16/bf16.
4. Değerlendirme planı. Göreve uygun metrikler (sınıflandırma için doğruluk + F1, NER için varlık düzeyinde F1, erişim için MRR/NDCG). Ayrılan test bölütü boyutu.
5. Başarısızlık modu kontrolü. Tek adlandırılmış risk: etiket sızıntısı, sınıf dengesizliği, bağlam kesme, ön eğitim ve ince-ayar külliyatları arasında tokenizer uyumsuzluğu.

Üretken çıktı (metin üretimi) için BERT'i ince-ayar yapma — bunun yerine yalnızca kodçözücülü (decoder-only) model öner. Azınlık sınıfı %10'un altında olduğunda sınıf-tabakalı değerlendirme olmadan ince-ayar gönderme. 1.000'den az etiketli örnek ile tüm omurgayı çözen herhangi bir ince-ayarı muhtemelen aşırı öğrenme (overfit) olarak işaretle.
