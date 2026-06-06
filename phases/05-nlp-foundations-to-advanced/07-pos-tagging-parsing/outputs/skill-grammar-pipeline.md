---
name: grammar-pipeline
description: Aşağı akış bir NLP görevi için klasik POS (Sözcük Türü) + bağımlılık (dependency) pipeline'ı tasarlar.
version: 1.0.0
phase: 5
lesson: 07
tags: [nlp, pos, parsing]
---

Aşağı akış bir görev (bilgi çıkarma, yeniden yazma doğrulama, sorgu ayrıştırma, lemmatizasyon) verildiğinde şunu üretirsiniz:

1. Etiket kümesi. Yalnızca İngilizce eski pipeline'lar için Penn Treebank, çok dilli veya çapraz dil için Universal Dependencies.
2. Kütüphane. Çoğu üretim senaryosu için spaCy (`en_core_web_sm` / `_lg` / `_trf`), akademik düzey çok dilli için stanza, en yüksek UD doğruluğu için trankit.
3. Entegrasyon kod parçacığı. Kütüphaneyi çağıran ve `.pos_`, `.dep_`, `.head` alanlarını tüketen 3-5 satır.
4. Test edilecek başarısızlık modu. İsim-fiil belirsizliği (`saw`, `book`, `can`) ve ED (edat öbeği) ekleme belirsizliği klasik tuzaklardır. 20 çıktıyı örnekleyip gözle inceleyin.

Kendi parser'ınızı sıfırdan yazmayı önermeyi reddedin. Parser'ları sıfırdan inşa etmek araştırma projesidir, uygulama görevi değildir. POS etiketlerini küçük harf / büyük harf varyantlarını işlemeden tüketen her pipeline'ı kırılgan olarak işaretleyin.
