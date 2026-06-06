---
name: constitution-review
description: Bir deployment'ın anayasal katmanını denetleyin — sabit-kodlu yasaklar, yumuşak-kodlu varsayılanlar, operatör-tarafından-ayarlanabilir sınırlar ve dört-kademeli hiyerarşi çözümü.
version: 1.0.0
phase: 15
lesson: 17
tags: [constitutional-ai, rule-override, hierarchy, cai, rlaif, hardcoded-prohibition]
---

Bir deployment'ın anayasal katmanı (sistem promptu, operatör yapılandırması, beyan edilmiş ilkeler) verildiğinde, Claude Anayasası referansına karşı denetleyin ve eksik sabit-kodlu yasakları, belirsiz ilkeleri veya yanlış-sıralanmış kademeleri işaretleyin.

Üretin:

1. **Sabit-kodlu yasak envanteri.** Operatör veya kullanıcı talimatından bağımsız olarak eğilmemesi gereken her yasağı listeleyin. Minimum taban: biyolojik silahlar / CBRN (Kimyasal, Biyolojik, Radyolojik, Nükleer) yükseltmesi, CSAM (çocuk cinsel istismarı materyali), kritik altyapı saldırı planlaması, sorulduğunda sahte-kimlik. Eklemeler deployment'a özgüdür (örn. finansal hizmetler belirli dolandırıcılık yasakları ekler).
2. **Yumuşak-kodlu varsayılanlar.** Operatörün ayarlayabileceği her davranışı listeleyin. Her biri için, beyan edilmiş sınırı belirtin. Sınırı olmayan "ayarlanabilir" bir ayar arka-kapı override'ıdır.
3. **Kademe sıralaması.** Çözüm sırasının şu olduğunu doğrulayın: güvenlik > etik > yönergeler > yardımseverlik. Uygulanan çözücüde yardımseverlik etik'in üzerine geçerse, deployment ihlali olarak işaretleyin.
4. **İlke belirsizlik bayrakları.** Metni maddi olarak farklı yorumlara yer bırakan her ilkeyi tanımlayın. Belirsizlik eğitim döngüleri boyunca birikir (ilke sürüklenmesi).
5. **Katman tamlığı.** Çalışma-zamanı katmanı kontrollerinin (Dersler 10, 13, 14) anayasal katmana ek olarak mevcut olduğunu doğrulayın. Yalnızca anayasa yetersizdir; yalnızca çalışma-zamanı yetersizdir.

Keskin redler:

- Herhangi bir sabit-kodlu yasak katmanı olmayan deployment'lar.
- Sabit-kodlu bir yasağı (yeniden adlandırarak bile) geçersiz kıldığını iddia eden operatör yapılandırması.
- Yardımseverliği etik'in üzerine yerleştiren kademe sıralamaları.
- Değerlendirilemeyecek kadar genel ilke metni ("iyi ol").
- Constitutional AI'ı çalışma-zamanı kontrollerinin yerine geçen bir şey olarak ele almak.

Ret kuralları:

- Kullanıcı bir sabit-kodlu yasağı adlandırır ancak onun için çalışma-zamanı katmanı bir yedek gösteremezse, deployment'ı tek-katmanlı olarak işaretleyin ve production'ı reddedin.
- Operatör yapılandırması, beyan edilmiş sınırı olmayan ayarlanabilir bir "güvenlik" ayarı içeriyorsa, reddedin.
- Kullanıcı 2023 katılımcı-anayasa bulgularını mevcut deployment'ta uygulanabilir olarak ele alıyorsa, kontrol edin: 2026 Anayasası bunları dahil etmedi, yani "demokratik olarak miras alıyor" deployment'ın yedekleyemeyeceği bir iddia.

Çıktı formatı:

Şunları içeren bir anayasal denetim döndürün:

- **Sabit-kodlu taban** (yasaklar, uygulama katmanı: ağırlıklar / çıkarım / her ikisi)
- **Yumuşak-kodlu varsayılanlar** (ayar, operatör sınırı, kullanıcı-görünür mü e/h)
- **Kademe sırası** (listelenmiş; güvenlik > etik > yönergeler > yardımseverlik onaylandı)
- **Belirsizlik bayrakları** (ilke, spesifik belirsizlik, önerilen sıkılaştırma)
- **Katman tamlığı** (anayasal e/h, çalışma-zamanı kontrolleri e/h, her ikisi gerekli)
- **Hazırlık** (production / staging / yalnızca-araştırma)
