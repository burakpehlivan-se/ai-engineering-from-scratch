---
name: regulatory-map
description: Bir dağıtımın yapay zeka düzenleyici yükümlülüklerini AB, ABD, İngiltere, Kore boyunca haritala
version: 1.0.0
phase: 18
lesson: 24
tags: [eu-ai-act, gpai-code, caisi, uk-aisi, korean-framework-act]
---

Bir dağıtım açıklaması (sağlayıcı yargı alanı, altyapı yargı alanı, kullanıcı yargı alanı) verildiğinde, uygulanabilir yapay zeka düzenleyici yükümlülüklerini haritala.

Çıktı:

1. AB maruziyeti. Dağıtım AB kullanıcılarına veya altyapısına dokunuyorsa, AB Yapay Zeka Yasası'nı uygula. Risk katmanını belirle (yasaklı, yüksek-riskli, GPAI-sistemik, GPAI-diğer, sınırlı). Her yükümlülük sınıfı için son tarihi belirt.
2. İngiltere maruziyeti. İngiltere kullanıcıları varsa, İngiltere Yapay Zeka Güvenlik Enstitüsü değerlendirme beklentilerini belirt. İngiltere'nin kapsamlı bir yapay zeka düzenlemesi yoktur (2026); sektörel kurallar geçerlidir.
3. ABD maruziyeti. ABD kullanıcıları varsa, federal faaliyeti (CAISI, NIST standartları) ve eyalet düzeyindeki kuralları (California AB 2013, Colorado AI Yasası vb.) belirle. Federal çerçeve büyüme-yanlısıdır; eyalet kuralları tabanı belirler.
4. Kore maruziyeti. Koreli kullanıcılar varsa, Kore Yapay Zeka Çerçeve Yasası'nı uygula; dağıtımın yüksek-etkili yapay zeka mı yoksa üretken yapay zeka mı olduğunu belirle; yabancı sağlayıcılar için yerel-temsilci gereksinimini işaretle.
5. Bağlayıcı kural belirleme. Her maddi yükümlülük için (şeffaflık, risk değerlendirmesi, telif hakkı), yargı alanları arasında en katı kuralı belirle. Bu, bağlayıcı kuraldır.

Kesin redler:

- Uygulanabilir yargı alanlarını adlandırmadan herhangi bir dağıtım haritası.
- Risk katmanı belirlemesi olmadan herhangi bir AB maruziyet değerlendirmesi.
- Eyalet düzeyindeki kuralları göz ardı eden herhangi bir ABD maruziyet değerlendirmesi.

Ret kuralları:

- Kullanıcı "bu dağıtım uyumlu mu" diye sorarsa, yargı alanı-yargı alanına haritalama olmadan ikili iddiayı reddet.
- Kullanıcı tek bir küresel uyum stratejisi isterse, reddet — yargı alanlarının farklı gereksinimleri vardır.

Çıktı: Yukarıdaki beş bölümü dolduran, her maddi sorunda bağlayıcı kuralı belirleyen ve en yüksek riskli uyum boşluğunu adlandıran tek sayfalık bir harita. AB Yapay Zeka Yasası'nı (Yönetmelik 2024/1689), GPAİ Uygulama Kuralları'nı (2025) ve Kore Yapay Zeka Çerçeve Yasası'nı her birini bir kez alıntıla.
