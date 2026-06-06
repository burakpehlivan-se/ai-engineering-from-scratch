---
name: bpe-vs-wordpiece
description: Belirli bir derlem ve dağıtım hedefi için tokenizer algoritması, sözcük dağarcığı boyutu ve kütüphane seçer.
version: 1.0.0
phase: 5
lesson: 19
tags: [nlp, tokenization]
---

Bir derlem (boyut, diller, alan) ve dağıtım hedefi (sıfırdan eğitim / ince ayar / API uyumlu çıkarım) verildiğinde şunu üretirsiniz:

1. Algoritma. BPE, Unigram veya WordPiece. Tek cümlelik neden.
2. Kütüphane. SentencePiece, HF Tokenizers veya tiktoken. Neden.
3. Sözcük dağarcığı boyutu. En yakın 1k'ya yuvarlanır. Model boyutu ve dil kapsamına bağlı olarak gerekçelendirin.
4. Kapsam ayarları. `character_coverage`, `byte_fallback`, özel-token listesi.
5. Doğrulama planı. Held-out kümesinde ortalama kelime başına token, OOV oranı, sıkıştırma oranı, round-trip çözme eşitliği.

Nadir yazı sistemli içeriğe sahip derlemlerde character_coverage <0,995 olan bir tokenizer eğitmeyi reddedin. CI'da dondurulmuş bir `tokenizer.json` hash kontrolü olmadan bir sözlüğü yayınlamayı reddedin. 16k sözlüğün altındaki herhangi bir tek dilli tokenizer'ı muhtemelen yetersiz olarak işaretleyin.
