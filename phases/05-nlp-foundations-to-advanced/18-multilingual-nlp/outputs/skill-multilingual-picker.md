---
name: multilingual-picker
description: Çok dilli bir NLP görevi için kaynak dili, hedef modeli ve değerlendirme planını seçer.
version: 1.0.0
phase: 5
lesson: 18
tags: [nlp, multilingual, cross-lingual]
---

Gereksinimler (hedef diller, görev türü, dil başına kullanılabilir etiketli veri) verildiğinde şunu üretirsiniz:

1. İnce ayar için kaynak dil. Varsayılan İngilizce; hedef dilin tipolojik olarak yakın yüksek kaynaklı bir dili varsa LANGRANK veya qWALS'a bakın.
2. Temel model. XLM-R (sınıflandırma), mT5 (üretim), NLLB (çeviri), Aya-23 (üretken LLM).
3. Few-shot bütçesi. Varsa 100-500 hedef dil örneğiyle başlayın. Etiketleme yapılamıyorsa yalnızca sıfır-atış (zero-shot).
4. Değerlendirme planı. Dil başına doğruluk (toplu değil), çapraz dil tutarlılığı, Latin olmayan yazılarda varlık düzeyinde F1.

Dil başına değerlendirme olmadan çok dilli bir modeli yayınlamayı reddedin — toplu metrikler uzun kuyruk başarısızlıklarını gizler. Düşük tokenizasyon kapsamına sahip yazı sistemlerini (Amharic, Tigrinya, birçok Afrika dili) byte-fallback (byte_fallback=True ile SentencePiece veya GPT-2 gibi byte düzeyinde tokenizer) olan bir model gerektiriyor olarak işaretleyin.
