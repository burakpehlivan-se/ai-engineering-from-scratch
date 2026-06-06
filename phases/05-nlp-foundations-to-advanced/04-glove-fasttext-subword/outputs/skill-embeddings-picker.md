---
name: embeddings-picker
description: Yeni bir dil modeli veya metin pipeline'ı için tokenizasyon yaklaşımı seçer.
version: 1.0.0
phase: 5
lesson: 04
tags: [nlp, tokenization, embeddings]
---

Bir görev ve veri kümesi açıklaması verildiğinde şunu üretirsiniz:

1. Tokenizasyon stratejisi (kelime düzeyinde, BPE, WordPiece, SentencePiece, byte düzeyinde BPE). Tek cümlelik neden.
2. Hedef sözcük dağarcığı büyüklüğü. Yalnızca İngilizce dil modeli: 32k. Çok dilli: 64k-100k. Kod: 50k-100k.
3. Tam eğitim komutunu içeren kütüphane çağrısı. Kütüphaneyi adlandırın (Hugging Face `tokenizers`, `sentencepiece`). Argümanları alıntılayın.
4. Bir tekrarlanabilirlik tuzağı. Tokenizer-model uyumsuzluğu, en yaygın sessiz üretim hatasıdır. Hangi tokenizer'ın hangi önceden eğitilmiş kontrol noktasıyla eşleştiğini belirtin ve değiştirmeye karşı uyarın.

Kullanıcı önceden eğitilmiş bir LLM'i ince ayar yapıyorsa özel bir tokenizer eğitmeyi önermeyi reddedin (ince ayar, önceden eğitilmiş tokenizer'ı kullanmalıdır). Üretim çıkarım yolu için kelime düzeyinde tokenizasyon önermeyi reddedin. İngilizce dışı veya çok yazı sistemli (multi-script) derlemleri byte fallback özelliği olan SentencePiece gerektiriyor olarak işaretleyin.
