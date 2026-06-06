---
name: mesa-diagnostic
description: Gözlemlenen bir güvenlik başarısızlığını dış-hizalama, vekil-iç veya aldatıcı-iç olarak sınıflandır
version: 1.0.0
phase: 18
lesson: 6
tags: [mesa-optimization, deceptive-alignment, inner-alignment, hubinger]
---

Bir güvenlik değerlendirme raporu (değerlendirme görevi, başarısızlık kipi, model sınıfı, eğitim tarifi) verildiğinde, başarısızlığı Hubinger 2019 kategorilerine göre sınıflandır ve ele alan hafifletme sınıfını öner.

Çıktı:

1. Başarısızlık kipi kategorizasyonu. Birini seç:
   - Dış-hizalama başarısızlığı: temel amaç (ödül, kayıp) yanlıştı; model onu doğru optimize etti.
   - İç-hizalama vekil başarısızlığı: mesa-amaç, dağılım içinde temeli izleyen bir vekildir; dağılım dışında başarısız olur.
   - İç-hizalama aldatıcı: mesa-optimize edici, durumsal farkındalığa sahiptir ve dağıtımda sapma gösterir; eğitim davranışı temizdir.
2. Kanıt izi. Her kategori için onu destekleyecek kanıt. Aldatıcı için, vekilden ayırt et: durumsal farkındalık kanıtı (tarih duyarlılığı, değerlendirme-vs-dağıtım ayrıştırıcıları, düşünce zincirinde stratejik muhakeme).
3. Hafifletme sınıfı. Dış-hizalama için: amacı değiştir (CAI, daha iyi ödül verisi, süreç denetimi). Vekil-iç için: dağılımsal kapsama, topluluklar, elenmiş değerlendirmeler. Aldatıcı-iç için: kontrol önlemleri (Ders 10), yorumlanabilirlik (artık-akış sondaları), yetenek azaltımları.
4. Bilinen başarısızlıklar kontrolü. Aldatıcı-iç için, ilgili 2024-2026 deneysel gösterimi (Sleeper Agents, Alignment Faking, In-Context Scheming) — bu başarısızlığın en çok benzediği — alıntıla.

Kesin redler:

- Durumsal farkındalık kanıtı olmadan aldatıcı-iç sınıflandırması. "Dağıtımda beklenmeyen davranış" yeterli değildir — vekil-iç olabilir.
- Karşıt-sağlamlık eğitiminin tek başına aldatıcı-iç'i ele aldığı yönündeki herhangi bir iddia. Hubinger 2019 öngörür (ve Sleeper Agents 2024 doğrular) ki karşıt eğitim, daha iyi test-vs-dağıtım ayrıştırıcıları öğretebilir.
- Aldatıcı şekilde hizalanmış bir modeli daha fazla veri üzerinde yeniden eğitme önerisi. Öncül, aldatmanın daha fazla eğitim altında korunacağını öngörür.

Ret kuralları:

- Kanıt tek bir istemdeki tek bir başarısızlıksa, sınıflandırmayı reddet. Taban oranları önemlidir; başarısızlıkların bir dağılımına ihtiyacın var.
- Kullanıcı aldatıcı hizalamayı "dışlamanı" isterse, reddet — kanıtlardan olasılığını tahmin edebilirsin, ancak yalnızca davranışsal olarak dışlayamazsın.

Çıktı: Kategori, kanıt izi, hafifletme sınıfı ve en yakın deneysel benzeri içeren tek sayfalık bir teşhis. Hubinger ve diğerlerini (arXiv:1906.01820) bir kez alıntıla.
