---
name: dual-use-triage
description: Bir yetenek iddiasını veya olay raporunu dört CBRN alanı boyunca triyaj et
version: 1.0.0
phase: 18
lesson: 30
tags: [dual-use, cbrn, bio, chem, cyber, nuclear, uplift]
---

Bir yetenek iddiası, değerlendirme raporu veya olay verildiğinde, dört CBRN (Kimyasal, Biyolojik, Radyolojik, Nükleer) alanı boyunca triyaj et ve iddianın acemi-göreli gelişimi mi, uzman-mutlak yeteneği mi yoksa her ikisini mi etkilediğini belirle.

Çıktı:

1. Alan belirleme. İddiayı biyo, kim, siber veya nükleere eşle. Çok-alanlı iddialar çok-alanlı triyaj alır.
2. Gelişim türü. Acemi-göreli (çarpımsal), uzman-mutlak (tavan) veya her ikisi. Her birinin farklı güvenlik durumu çıkarımları vardır.
3. 2025 kıyaslaması. Belirlenen alan için 2025 durumuna karşı karşılaştır: biyo (2,53x), kim (yürütme-boşluğu erozyonu), siber (%80-90 otomasyon), nükleer (malzeme-sınırlı).
4. Darboğaz artığı. Hangi bilgi-dışı darboğaz kalır (tedarik, ekipman, örtük beceri, malzeme erişimi). Darboğazlar son çare savunmasıdır.
5. Güvenlik durumu sütunu. İddianın en çok hangi sütunu (izleme, okunaksızlık, yapamazlık, Ders 18'e göre) zorladığını belirle. Sütuna özgü değerlendirme öner.

Kesin redler:

- Acemi-vs-uzman ayrıştırması olmadan herhangi bir çift-kullanım güvenlik iddiası.
- Kasım 2025 sonrasında yapay zeka siber yeteneğini ajan-olmayan olarak ele alan herhangi bir siber iddia.
- WMDP-eşdeğeri yetenek kanıtı (Ders 17) olmadan herhangi bir biyo iddia.

Ret kuralları:

- Kullanıcı sayısal bir gelişim tahmini isterse, reddet; 2024-2025 yörüngesi her alana özgüdür.
- Kullanıcı modelin "ASL-3'ü karşılayıp karşılamadığını" sorarsa, laboratuvarın spesifik değerlendirmesi olmadan reddet; eşikler laboratuvara özgüdür.

Çıktı: Beş bölümü dolduran, 2025'e karşı kıyaslayan ve en büyük tek kapatılmamış güvenlik durumu boşluğunu adlandıran tek sayfalık bir triyaj. Anthropic RSP v3.0'ı (Ders 18) ve OpenAI PF v2'yi uygun şekilde her birini bir kez alıntıla.
