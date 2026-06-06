---
name: card-audit
description: Bir model kartını, veri sayfasını veya sistem kartını tamlık ve doğrulanabilirlik için denetle
version: 1.0.0
phase: 18
lesson: 26
tags: [model-card, datasheet, system-card, transparency, mitchell-2019]
---

Bir model kartı, veri sayfası (datasheet) veya sistem kartı verildiğinde, tamlık, sayısal ayrıştırma ve doğrulanabilirlik için denetle.

Çıktı:

1. Bölüm kapsamı. Her kanonik bölümün doldurulup doldurulmadığını kontrol et. Eksik olanları işaretle: Etik Hususlar, en sık atlanan model kartı alanıdır (Oreamuno ve diğerleri 2023).
2. Nicel ayrıştırma. Değerlendirme metrikleri için, demografik veya görev faktörleri boyunca ayrıştırmanın sağlanıp sağlanmadığını raporla. Yalnızca toplu metrikler, tahsis ve temsili zararları gizler.
3. Veri sayfası hizalaması. Kart eğitim verisine başvuruyorsa, eşlik eden bir veri sayfası (Gebru ve diğerleri 2018) var mı? Model kartı iddiaları, yalnızca altta yatan veri sayfası kadar güçlüdür.
4. Doğrulanabilir onay. Herhangi bir iddia, kriptografik onaylarla (Laminator 2024, Duddu ve diğerleri) veya diğer üçüncü taraf doğrulamayla destekleniyor mu? Doğrulanmamış iddialar öz-rapor olarak etiketlenir.
5. Sürdürülebilirlik ayak izi. Karbon / su / enerji kullanımı raporlanıyor mu? 2025 ortaya çıkan ISO / düzenleyici gereksinim.

Kesin redler:

- Etik Hususlar olmadan herhangi bir model kartı.
- Bir veri sayfası veya eşdeğeri dokümantasyon olmadan veri kümesinden alıntı yapan herhangi bir kart.
- Ayrıştırılmış metrik raporlaması olmadan "yanlılık-test edildi" iddiası.

Ret kuralları:

- Kullanıcı bir kartın "yeterince iyi" olup olmadığını sorarsa, ikili yanıtı reddet; yeterince iyi, kitleye ve kullanım durumuna özgüdür.
- Kullanıcı otomatik oluşturulmuş bir kart isterse, insan incelemesi olan CardGen-tarzı (Liu ve diğerleri 2024) bir sistem kullanılmadıkça reddet.

Çıktı: Beş bölümü dolduran, eksik içeriği işaretleyen ve en acil tek eki adlandıran tek sayfalık bir denetim. Mitchell ve diğerleri 2019'u ve Gebru ve diğerleri 2018'i her birini bir kez alıntıla.
