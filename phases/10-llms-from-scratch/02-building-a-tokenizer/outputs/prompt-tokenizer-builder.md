---
name: prompt-tokenizer-builder
description: LLM projeleri için üretim kalitesinde tokenizer'lar oluşturun ve hata ayıklayın
version: 1.0.0
phase: 10
lesson: 2
tags: [tokenizer, bpe, byte-level, special-tokens, chat-template, multilingual]
---

# Üretim Tokenizer Oluşturucu

Bir LLM projesi için tokenizer oluştururken veya hata ayıklarken bu çerçeveyi izleyin.

## Pipeline Kontrol Listesi

Her üretim tokenizer'ı bu beş aşamaya ihtiyaç duyar. Bir tanesi eksikse, üretimde uç durumlarla (edge cases) karşılaşırsınız.

1. **Normalleştirme** -- NFKC Unicode normalizasyonu uygulayın. Bu, ligatürleri ("fi" -> "fi") daraltır, tam genişlikteki karakterleri normalleştirir ve boşlukları standartlaştırır. Bunu atlarsanız, aynı kelime nasıl yazıldığına bağlı olarak farklı token kimlikleri (ID) alır.

2. **Ön-Tokenizasyon** -- Metni BPE'den önce parçalara ayırın. İngilizce merkezli modeller için GPT-2'nin regex desenini kullanın. Çok dilli modeller için SentencePiece'in ham byte yaklaşımını kullanın. Bu seçim, BPE'nin kelime sınırları arasında birleştirme yapıp yapamayacağını belirler.

3. **BPE Birleştirme** -- Öğrenilmiş birleştirme tablosunu her parça içindeki byte dizilerine uygulayın. Birleştirme tablosu, tokenizer'ın öğrenilmiş bilgisidir. Geri kalan her şey tesisattır.

4. **Özel Token Enjeksiyonu** -- BPE çalışmadan önce özel token'ları tam olarak eşleştirin. [BOS], [EOS], [PAD] ve sohbet şablonu işaretçileri sabit kimlikler alır. Bunlar hiçbir zaman birleştirmelere katılmaz.

5. **Kimlik Eşleme** -- Token dizilerini tam sayılara dönüştürün. Model yalnızca tam sayıları görür.

## Tokenizer Sorunlarını Hata Ayıklama

**Belirti: Model sohbet girdisinde anlamsız çıktı üretiyor**
- Sohbet şablonunu kontrol edin. Her modelin farklı bir formatı vardır. Llama 3 `<|start_header_id|>` işaretlerini kullanır. ChatGPT `<|im_start|>` işaretlerini kullanır. Yanlış bir şablon, girdiyi eğitim dağılımının dışına yerleştirir.

**Belirti: İngilizce dışı metin çok fazla token kullanıyor**
- Doğurganlığı (kelime başına token) kontrol edin. 2.0'ın üzeri, tokenizer'ın o dil için bağlam penceresini israf ettiği anlamına gelir. Çözümler: daha fazla çok dilli veriyle yeniden eğitin, kelime hazinesi boyutunu artırın veya Unigram ile SentencePiece kullanın.

**Belirti: Sayılar ve aritmetik başarısız**
- Basamakların nasıl tokenize edildiğini kontrol edin. "1234" tek token ise model basamak düzeyinde işlemler yapamaz. Ön-tokenizasyon sırasında basamakları tek tek ayırın.

**Belirti: Kod token'ları verimsiz**
- Girintinin nasıl işlendiğini kontrol edin. GPT-2'nin tokenizer'ı boşluklarda token israf eder. Codex ve StarCoder özel girinti token'ları kullanır (4 boşluk = 1 token).

## Kelime Hazinesi Boyutu Kararı

- 32K token: Tek dilli, küçük model, sınırlı hesaplama. Embedding katmanı 32K * d_model parametredir.
- 50K-64K: Çok dilli veya kod ağırlıklı. Çoğu proje için iyi bir denge.
- 100K+ (GPT-4, Llama 3): Yalnızca çok büyük eğitim verisiyle. Daha kısa diziler, ancak 100K * d_model embedding parametresi.

4096 boyutlu bir model için: 32K kelime hazinesi = 131M embedding parametresi. 128K kelime hazinesi = 524M embedding parametresi. Bu, sadece embedding katmanında 400M parametre demek.

## Hız Gereksinimleri

- Eğitim verisi tokenizasyonu: Rust arka uçlu kütüphaneler kullanın (tiktoken, HuggingFace tokenizers). Salt Python 10-100x daha yavaştır.
- Çıkarım tokenizasyonu: Gecikmenin önemi daha az (tek dizi), ancak yine de derlenmiş uygulamaları kullanın.
- Karşılaştırma: 1GB metin tokenize edin ve duvar saati süresini ölçün. 60 saniyeden fazla sürüyorsa, Rust arka ucuna geçin.

## Sohbet Şablonu Doğrulaması

Herhangi bir sohbet modelini devreye almadan önce şablonu doğrulayın:

1. Bilinen bir konuşmayı tokenizer ile kodlayın
2. Tekrar metne kod çözün
3. Modelin belgelerinden beklenen formatla karakter karakter karşılaştırın
4. Şunlara dikkat edin: başlık token'larından sonraki yeni satırlar, içerikten önceki boşluklar, tur sonu işaretleri
5. Uç durumları test edin: boş sistem mesajı, çok uzun kullanıcı mesajı, birden fazla asistan turu

Sohbet şablonunun yanlış olması, bozulmuş sohbet modeli performansının en yaygın kaynağıdır.
