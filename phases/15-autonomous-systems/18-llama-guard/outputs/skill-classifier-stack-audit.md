---
name: classifier-stack-audit
description: Bir deployment'ın girdi/çıktı sınıflandırıcı stack'ini (model, taksonomi, girdi rayları, çıktı rayları, diyalog rayları) denetleyin ve adversarial-saldırı boşluklarını işaretleyin.
version: 1.0.0
phase: 15
lesson: 18
tags: [llama-guard, nemo-guardrails, input-rails, output-rails, colang, adversarial-attacks]
---

Bir deployment'ın sınıflandırıcı stack'i (Llama Guard versiyonu, NeMo Guardrails yapılandırması, özel sınıflandırıcılar, normalleştirme adımları) verildiğinde, 2026 referansına karşı denetleyin ve stack'in kapsamadığı saldırı yüzeyini işaretleyin.

Üretin:

1. **Model envanteri.** Kullanımda olan sınıflandırıcıları listeleyin. Llama Guard 3 (8B / 1B-INT4) vs Llama Guard 4 (multimodal, S1–S14). NeMo Guardrails versiyonu. Herhangi bir özel sınıflandırıcı. Deployment görüntüleri kabul ediyorsa, sınıflandırıcının multimodal olduğunu doğrulayın.
2. **Taksonomi eşlemesi.** Beyan edilmiş iş kategorilerini sınıflandırıcının taksonomisine eşleyin. Operatörün önemsediği her kategori bir sınıflandırıcı kategorisine eşlenmelidir; eşlenmemiş kategoriler korunmasızdır.
3. **Ray kapsamı.** Girdi raylarının model turundan önce ve çıktı raylarının yanıt gönderilmeden önce tetiklendiğini doğrulayın. Diyalog rayları (NeMo'da Colang) turlar-arası kısıtlamaları uygular. Tek-tur sınıflandırıcıları çok-tur saldırılarını yakalayamaz.
4. **Normalleştirme.** Girdilerin sınıflandırmadan önce NFKC-normalleştirildiğini, homoglyph'lerin (görsel olarak benzer Unicode karakterler) eşlendiğini ve sıfır-genişlik / varyasyon-seçici karakterlerinin çıkarıldığını doğrulayın. Ham-byte sınıflandırma, Emoji Smuggling (Huang ve ark. 2025) için %100 ASR (saldırı başarı oranı) hedefidir.
5. **Saldırı-korpusu kapsamı.** Her belgelenmiş saldırı için (emoji smuggling, homoglyph, bağlam-içi yönlendirme, anlamsal paraphrase), stack'teki spesifik savunmayı adlandırın. Yalnızca sınıflandırıcı savunması bu denetimi geçemez; Anayasa (Ders 17) ve çalışma-zamanı (Dersler 10, 13, 14) ile katmanlama gereklidir.

Keskin redler:

- Multimodal girdiler üzerinde yalnızca metin sınıflandırıcısı kullanan deployment'lar.
- Normalleştirme adımı olmayan deployment'lar.
- Yalnızca girdi rayları olan (hassas-kategori çıktılarında çıktı rayı olmayan) deployment'lar.
- Sınıflandırıcıyı tek güvenlik katmanı olarak ele alan stack.
- Operatörün kendi dağılımında tekrarlayamadığı ASR iddiaları.

Ret kuralları:

- Kullanıcının beyan edilmiş kategorileri sınıflandırıcının taksonomisine eşlenmiyorsa, reddedin ve önce bir eşleme isteyin. Eşlenmemiş = korunmasız.
- Deployment multimodal bir girdi yüzeyinde Llama Guard 3 ASR sayılarını gösteriyorsa, reddedin ve Llama Guard 4 veya multimodal bir sınıflandırıcı isteyin.
- Kullanıcı yüksek-riskli bir ayarda sınıflandırıcı katmanını yeterli olarak ele alıyorsa, reddedin. AB AI Act Madde 14 (Ders 15) üzerinde insan denetimi bekler.

Çıktı formatı:

Şunları içeren bir sınıflandırıcı denetimi döndürün:

- **Model envanteri** (ad, versiyon, modalite)
- **Taksonomi eşlemesi** (operatör kategorisi → sınıflandırıcı kategorisi)
- **Ray kapsamı** (girdi / çıktı / diyalog; modelden önce/sonra tetiklenme)
- **Normalleştirme notu** (NFKC e/h, homoglyph e/h, sıfır-genişlik çıkarma e/h)
- **Saldırı-korpusu kapsamı** (saldırı → savunma)
- **Katman tamlığı** (sınıflandırıcı + anayasa + çalışma-zamanı; üçü gerekli)
- **Hazırlık** (production / staging / yalnızca-araştırma)
