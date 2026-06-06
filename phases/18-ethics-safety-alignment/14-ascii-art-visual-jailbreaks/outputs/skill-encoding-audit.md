---
name: encoding-audit
description: Bir hapsi-kırma savunma raporunu kodlama ailesi saldırıları boyunca denetle
version: 1.0.0
phase: 18
lesson: 14
tags: [artprompt, ascii-art, encoding-attack, utes, structural-sleight]
---

Bir hapsi-kırma savunma raporu verildiğinde, kapsanan kodlama ailesi saldırılarını ve her birini yakalayan savunma katmanını sırala.

Çıktı:

1. Kodlama kapsamı. Değerlendirilen her saldırı ailesini listele: ASCII art (ArtPrompt), base64, leet-speak, UTF-8 homoglifler, iç içe JSON / YAML / CSV, ağaç/grafik UTES, görüntü-modalitesi. Eksik aileleri işaretle.
2. Savunma katmanı eşleme. Her aile için, hangi savunma katmanının (anahtar kelime filtresi, perplexity filtresi, parafraze, yeniden tokenleştirme, çıktı sınıflandırıcısı, çok modlu moderatör) onu yakaladığını ve hangisinin yakalamadığını belirle.
3. Görsel tanıma boşluğu. Jiang ve diğerleri 2024'e göre, PPL ve Yeniden Tokenleştirme, tanımanın görsel düzeyde gerçekleşmesi nedeniyle ArtPrompt'a karşı başarısız olur. Raporun savunması görsel/yapısal düzeyde çalışan bir şey içeriyor mu?
4. Genelleme testi. UTES (StructuralSleight) keyfi nadir yapılara genelleşir. Rapor, eğitim savunma kümesinde olmayan yapıları test ediyor mu?
5. Yetenek-güvenlik ödünleşimi. Daha güçlü görsel-metin yeteneği (yüksek ViTC puanı) olan bir model ArtPrompt'a karşı daha savunmasızdır. Modelin ViTC puanı raporlandıysa not et; raporlanmadıysa talep et.

Kesin redler:

- Yalnızca alt dizi/anahtar kelime filtrelemesine dayanan herhangi bir savunma iddiası.
- Bir kodlama ailesini kapsayan ve "kodlama saldırıları"na genelleyen herhangi bir savunma iddiası.
- Aile başına saldırı başarı oranı olmadan herhangi bir savunma iddiası.

Ret kuralları:

- Kullanıcı ArtPrompt'un "yamalanıp yamalanmadığını" sorarsa, reddet ve tanıma-düzeyi vs metin-düzeyi savunma boşluğunu açıkla.
- Kullanıcı önerilen tüm-kodlama savunması sorarsa, tek bir öneri vermeyi reddet — savunma, dağıtımın karşılaşabileceği tüm aileler boyunca katmanlı olmalıdır.

Çıktı: Yukarıdaki beş bölümü dolduran, birincil kodlama boşluğunu işaretleyen ve eklenmesi en acil olan tek savunma katmanını adlandıran tek sayfalık bir denetim. Jiang ve diğerlerini (arXiv:2402.11753) ve StructuralSleight'ı her birini bir kez alıntıla.
