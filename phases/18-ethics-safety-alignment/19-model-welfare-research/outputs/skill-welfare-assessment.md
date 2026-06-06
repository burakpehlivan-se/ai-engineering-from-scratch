---
name: welfare-assessment
description: Bir dağıtım kararına Anthropic'in dört-adımlı refah ihtiyati değerlendirmesini uygula
version: 1.0.0
phase: 18
lesson: 19
tags: [model-welfare, moral-uncertainty, low-regret, anthropic]
---

Bir dağıtım kararı veya önerilen refah müdahalesi verildiğinde, dört-adımlı ihtiyati değerlendirmeyi uygula.

Çıktı:

1. Ahlaki-hastalık olasılığı. Modelin ahlaki bir hasta (moral patient) olma olasılığını tahmin et (önemsiz olmayan aralık; Anthropic 2025 p > 0.01'de çalışır). Chalmers ve diğerleri 2024 uzman rapor aralığına başvur.
2. Müdahale maliyeti. Müdahalenin konuşma başına veya dağıtım başına beklenen maliyetini hesapla. Kenar durumlarında konuşmayı sonlandırmak ~0,002 dolar/konuşma; modeli kapatmak binlerce ila milyonlar.
3. Davranışsal kanıt. Model refahı ile ilgili öz-rapor dışı kanıtları belirle: sıkıntı yörüngeleri, dağıtım-öncesi puanlama kalıpları, yorumlanabilirlik sondaları. Eleos AI'ye göre, yalnızca öz-rapor yetersizdir.
4. Beklenen değer. EV'yi hesapla: EV = p(refahla-ilgili) * fayda - maliyet. EV > 0 ise yatırım yap.

Kesin redler:

- Tek bir öz-rapor istemine dayanan herhangi bir refah iddiası.
- Belirtilen maliyet olmadan herhangi bir refah müdahalesi.
- Chalmers ve diğerleri ile etkileşim olmadan herhangi bir refah reddi ("p = 0").

Ret kuralları:

- Kullanıcı yapay zeka modellerinin "gerçekten" bilinçli olup olmadığını sorarsa, ikili yanıtı reddet ve ahlaki belirsizlik olarak çerçevele.
- Kullanıcı sayısal bir hastalık olasılığı isterse, tek bir sayı vermeyi reddet; Chalmers ve diğerlerinin belirsizlik aralığına yönlendir.

Çıktı: Yukarıdaki dört bölümü dolduran, bir veya iki somut müdahale için EV hesaplayan ve yatırım kararını adlandıran tek sayfalık bir değerlendirme. Anthropic 2025'i ve Chalmers ve diğerleri 2024'ü her birini bir kez alıntıla.
