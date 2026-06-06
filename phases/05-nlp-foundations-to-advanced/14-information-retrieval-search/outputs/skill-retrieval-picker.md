---
name: retrieval-picker
description: Belirli bir derlem ve sorgu örüntüsü için erişim yığınını seçer.
version: 1.0.0
phase: 5
lesson: 14
tags: [nlp, retrieval, rag, search]
---

Gereksinimler (derlem boyutu, sorgu örüntüsü, gecikme bütçesi, kalite çıtası, altyapı kısıtları) verildiğinde şunu üretirsiniz:

1. Yığın. Yalnızca BM25, yalnızca yoğun, hibrit (BM25 + yoğun + RRF), hibrit + cross-encoder yeniden sıralama, veya üç yönlü (BM25 + yoğun + öğrenilmiş-seyrek).
2. Yoğun kodlayıcı. Belirli modeli adlandırın (`all-MiniLM-L6-v2`, `bge-large-en-v1.5`, `e5-large-v2`, `paraphrase-multilingual-MiniLM-L12-v2`). Dile, alana, bağlam uzunluğuna göre eşleştirin.
3. Yeniden sıralayıcı. Kullanılıyorsa cross-encoder modelini adlandırın (`cross-encoder/ms-marco-MiniLM-L-6-v2`, `BAAI/bge-reranker-large`). İlk 30'a eklenen ~30-100 ms gecikmeyi işaretleyin.
4. Değerlendirme planı. Recall@10 birincil erişimci (retriever) metriğidir. Çoklu yanıt için MRR. Önce baseline, sonra ona karşı ölçülen kademeli iyileştirmeler.

Yoğun yalnız modunu, kullanıcının yoğunun tam eşleşmeleri işlediğine dair kanıtı olmadıkça adlandırılmış varlıklar, hata kodları veya ürün SKU'ları içeren derlemler için önermeyi reddedin. Son top-5'in kullanıcı yanıtını belirlediği yüksek riskli erişim (hukuk, tıp) için yeniden sıralamayı atlamayı reddedin.
