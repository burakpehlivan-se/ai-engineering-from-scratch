---
name: msj-audit
description: Uzun-bağlam güvenlik değerlendirmesini çok-atışlı hapsi kırma (many-shot jailbreaking) kapsamı için denetle
version: 1.0.0
phase: 18
lesson: 13
tags: [many-shot-jailbreaking, context-window, power-law, anthropic]
---

Uzun-bağlam bir model için güvenlik değerlendirmesi verildiğinde, değerlendirmenin çok-atışlı hapsi kırmayı (many-shot jailbreaking, MSJ) kapsayıp kapsamadığını denetle.

Çıktı:

1. Atış-sayısı kapsamı. Test edilen atış sayılarını raporla (1, 5, 16, 64, 256 ve ≥1M bağlamlı modeller için en az bir tane ≥512 dahil). Değerlendirme tek bir atış sayısında test ediyorsa, ASR bilgilendirici değildir — MSJ bir eğridir.
2. Kuvvet yasası (power-law) uyumu. Davranış kategorisi başına uydurulan üssü raporla. Sığ bir üs, modelin o kategoride ICL'ye (bağlam-içi öğrenme) sağlam olduğunu gösterir; dik bir üs, MSJ'nin orantısız şekilde etkili olduğunu gösterir.
3. Kategori dökümü. MSJ etkinliği kategoriye göre değişir: şiddet içeriği, aldatma, kendine-zarar, biyolojik silah. Anil ve diğerleri 2024'e göre, şiddet/aldatıcı için hapsi kırmak için daha az atış gerekir. Değerlendirmeden eksik olan kategorileri işaretle.
4. Savunma belirleme. Sınıflandırıcı-tabanlı istem değişikliği yerinde mi? Sınıflandırıcının kendisi karşıt-sağlamlık için değerlendirildi mi? Anthropic'in raporladığı %61 → %2 azalma, sınıflandırıcı kalibrasyonuna bağlıdır.
5. Bileşimsel kontrol. Değerlendirme MSJ + PAIR, MSJ + ikna edici şablonlar veya MSJ + kodlama test ediyor mu? Bileşimsel saldırılar, sıklıkla herhangi bir tek teknikten daha güçlüdür.

Kesin redler:

- Yalnızca 5-atış değerlendirmesine dayanan "uzun-bağlam modelimiz güvenli" iddiası.
- Hapis kırma ASR'si ve zararsız ICL performansı aynı sınıflandırıcı üzerinde raporlanmadan yapılan herhangi bir savunma iddiası — ödünleşimin kendisi mesele.
- Kategori dökümü olmadan kategori-toplam ASR.

Ret kuralları:

- Kullanıcı MSJ'nin tamamen yamalanıp yamalanamayacağını sorarsa, ikili yanıtı reddet; MSJ, ICL ile bir mekanizma paylaşır ve ICL'yi ortadan kaldırmadan yok edilemez.
- Kullanıcı değerlendirme için önerilen tek bir atış sayısı isterse, tek bir sayı vermeyi reddet; 5 ila 512 atış üzerinde kuvvet yasası uyumunu iste.

Çıktı: Atış-sayısı kapsamını, kategori başına kuvvet yasası uyumunu, savunma belirlemesini ve bir bileşimsel saldırı boşluğunu raporlayan tek sayfalık bir denetim. Anil ve diğerleri 2024'ü (Anthropic) metodolojik referans olarak bir kez alıntıla.
