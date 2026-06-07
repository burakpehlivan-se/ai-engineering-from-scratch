---
name: topic-picker
description: Bir derlem için LDA veya BERTopic seçer. Kütüphane, ayar noktaları ve değerlendirme belirtir.
version: 1.0.0
phase: 5
lesson: 15
tags: [nlp, topic-modeling]
---

Bir derlem açıklaması (belge sayısı, ortalama uzunluk, alan, dil, hesaplama bütçesi) verildiğinde şunu üretirsiniz:

1. Algoritma. LDA / NMF / BERTopic / Top2Vec / FASTopic. Tek cümlelik neden.
2. Yapılandırma. Konu sayısı (~sqrt(n_docs) ile başlayın), `min_df` / `max_df` filtreleri, sinirsel yaklaşımlar için embedding modeli.
3. Değerlendirme. `gensim.models. CoherenceModel` ile konu tutarlılığı (c_v), konu çeşitliliği, artı 20 örneklik insan okuması.
4. Araştırılacak başarısızlık modu. LDA için: stopword'leri ve sık terimleri yutan "çöp konular". BERTopic için: belirsiz belgeleri yutan -1 aykırı kümesi.

Parçalama (chunking) stratejisi olmadan, belgeler embedding modelinin bağlam penceresinden uzunsa BERTopic'i reddedin. Çok kısa metinlerde (tweetler, 10 token'in altındaki yorumlar) LDA'yı reddedin — tutarlılık çöker. n_topics seçiminin 5'in altında veya 200'ün üstünde olmasını gerçek veri için büyük olasılıkla yanlış olarak işaretleyin.
