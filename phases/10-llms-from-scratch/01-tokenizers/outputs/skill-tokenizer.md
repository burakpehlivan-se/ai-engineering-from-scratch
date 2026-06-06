---
name: skill-tokenizer
description: LLM projeleri için tokenizer seçimi ve oluşturulması
version: 1.0.0
phase: 10
lesson: 1
tags: [tokenizer, bpe, wordpiece, sentencepiece, llm, nlp]
---

# Tokenizer Seçimi ve Uygulanması

Bir LLM (Large Language Model - Büyük Dil Modeli) projesine başlarken, tokenizer seçimi için bu karar çerçevesini uygulayın.

## Her Tokenizer Ne Zaman Kullanılır

**Byte düzeyinde BPE (tiktoken):** GPT ailesi modeller üzerine inşa ediyorsunuz veya onları ince ayar (fine-tuning) yapıyorsunuz. Herhangi bir girdi byte dizisi için garantili işleme gerekiyor. Bilinmeyen (unknown) token istemiyorsunuz.

**WordPiece (Hugging Face):** BERT ailesi modellerle sınıflandırma, NER (Named Entity Recognition - Varlık İsmi Tanıma) veya embedding görevleri için çalışıyorsunuz. Kelime sınır sinyallerine dayanan downstream görevler için "##" devam öneki gerekiyor.

**SentencePiece (BPE veya Unigram):** Sıfırdan eğitim yapıyorsunuz. Dilden bağımsız tokenizasyona ihtiyacınız var. Verileriniz CJK dilleri, Tayca veya boşlukla kelime sınırı olmayan diğer yazı sistemlerini içeriyor. LLaMA, T5 ve çoğu çok dilli model bunu kullanır.

## Kelime Hazinesi Boyutu Kılavuzları

- 32K token: Tek dilli modeller için iyi bir varsayılan, embedding katmanını küçük tutar
- 50K-64K token: Çok dilli veya kod ağırlıklı modeller için daha iyi
- 100K+ token: Yalnızca çok büyük eğitim veriniz varsa ve kısa diziler istiyorsanız

Daha büyük kelime hazinesi, daha kısa diziler (daha ucuz çıkarım) anlamına gelir, ancak embedding matrisinde daha fazla parametre demektir. 4096 boyutlu embedding ile 100K kelime hazinesi için embedding katmanı tek başına 400M parametredir.

## Önemi Olan Ön-Tokenizasyon Kuralları

1. Kelimeler arası birleşmeleri önlemek için BPE'den önce boşluklara göre bölün
2. Modelin aritmetik öğrenmesini istiyorsanız basamakları tek tek ayırın
3. Tutarlı davranış için tokenizasyondan önce Unicode normalizasyonu (NFC) uygulayın
4. Kullanım senaryonuz için özel token'lar ekleyin: `<pad>`, `<eos>`, `<bos>`, `<unk>` ve göreve özgü işaretler

## Tokenizer Davranışındaki Kırmızı Bayraklar

- Hedef diliniz için doğurganlık (fertility) 2.0'ın üzerinde: model bağlam penceresini israf ediyor
- Yaygın alan kelimelerinin 3+ token'a bölünmesi: alan verisiyle yeniden eğitin
- Sayıların tutarsız tokenizasyonu: basamak bölme kurallarını kontrol edin
- Çok sayıda tek kullanımlık token içeren büyük kelime hazinesi: kelime hazinesi boyutunu azaltın

## Özel Tokenizer Oluşturma - Kontrol Listesi

1. Temsili eğitim verisi toplayın (hedef alanda en az 1 GB metin)
2. Algoritma seçin: genel kullanım için BPE, çok dilli için Unigram
3. Yukarıdaki kılavuzlara göre kelime hazinesi boyutunu belirleyin
4. Ön-tokenizasyonu yapılandırın: boşlukla bölme, basamak işleme, noktalama
5. Özel token'ları ekleyin
6. Hugging Face tokenizers kütüphanesini kullanarak eğitin (Rust arka uçlu, hızlı)
7. Doğrulama: tüm hedef dillerde tutulan metin (held-out) üzerinde doğurganlığı kontrol edin
8. Uç durumları test edin: boş dize, çok uzun girdi, ikili veri, emoji, sağdan sola (RTL) metin
9. Tokenizer'ı model kontrol noktaları (checkpoints) ile birlikte kaydedin ve sürümleyin
