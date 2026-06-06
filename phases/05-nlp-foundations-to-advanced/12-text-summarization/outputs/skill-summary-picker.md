---
name: summary-picker
description: Çıkarıcı (extractive) veya soyutlayıcı (abstractive) yaklaşımı seçer, kütüphaneyi adlandırır, gerçeklik kontrolü ekler.
version: 1.0.0
phase: 5
lesson: 12
tags: [nlp, summarization]
---

Bir görev (belge türü, uyumluluk gereksinimi, uzunluk, hesaplama bütçesi) verildiğinde şunu üretirsiniz:

1. Yaklaşım. Çıkarıcı veya soyutlayıcı. Tek cümlede nedenini açıklayın.
2. Başlangıç modeli / kütüphanesi. Adını belirtin. `sumy.TextRankSummarizer`, `facebook/bart-large-cnn`, `google/pegasus-pubmed` veya bir LLM istemi.
3. Değerlendirme planı. ROUGE-1, ROUGE-2, ROUGE-L (kök bulma ile `rouge-score` kullanın). Soyutlayıcı ise artı gerçeklik kontrolü.
4. Araştırılacak bir başarısızlık modu. Soyutlayıcı haber özetlemede varlık yer değiştirmesi en yaygın olanıdır; kaynaktaki varlıkların özette bulunmadığı örnekleri işaretleyin.

Gerçeklik geçidi olmadan tıbbi, hukuki, finansal veya düzenlenmiş içerik için soyutlayıcı özetlemeyi reddedin. Modelin bağlam penceresini aşan girdileri yalnızca kırpma değil, parçalı map-reduce özetleme gerektiriyor olarak işaretleyin.
