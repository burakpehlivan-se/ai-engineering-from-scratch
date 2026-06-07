---
name: embedding-probe
description: Bir word2vec modelini inceler. Analoji sorguları çalıştırır, en yakın komşuları bulur, kalite teşhisi koyar.
version: 1.0.0
phase: 5
lesson: 03
tags: [nlp, embeddings, debugging]
---

Eğitilmiş kelime embedding'lerinin çalıştığını doğrulamak için onları sorgularsınız. Bir `gensim.models. KeyedVectors` nesnesi ve sözcük dağarcığı verildiğinde şunları çalıştırırsınız:

1. Üç kanonik analoji testi. `king : man :: queen : woman`. `paris : france :: tokyo : japan`. `walking : walked :: swimming : ?`. İlk sonucu ve kosinüs değerini raporlayın.
2. Kullanıcının verdiği alana özgü kelimeler üzerinde beş en yakın komşu testi. Top-5 komşuyu kosinüs değerleriyle yazdırın.
3. Bir simetri kontrolü. `similarity(a, b) == similarity(b, a)` ifadesi kayan nokta hassasiyeti dahilinde.
4. Bir dejenerasyon kontrolü. Herhangi bir embedding'in normu 0,01'in altında ya da 100'ün üstündeyse modelde eğitim hatası var. Bunu işaretleyin.

Bir modeli yalnızca analoji doğruluğuna dayanarak iyi ilan etmeyi reddedin. Analogi kıyaslamaları oynanabilir ve aşağı akış görevlerine taşınmaz. İçsel (intrinsic) ve aşağı akış değerlendirmesini birlikte önerin.
