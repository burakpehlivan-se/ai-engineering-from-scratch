---
name: sim2real-planner
description: Verilen bir robot + görev için DR, SI ve güvenliği kapsayan bir simülasyondan-gerçeğe aktarım hattı planla
version: 1.0.0
phase: 9
lesson: 11
tags: [rl, sim2real, robotik, alan-randomizasyonu]
---

Bir robot platformu, bir görev ve gerçek donanım zamanına erişim verildiğinde, aşağıdakileri üret:

1. Gerçeklik boşluğu envanteri. Beklenen etkiye göre sıralanmış şüpheli kaynaklar (temas, algılama, hareket gecikmesi, görme).
2. DR parametreleri. Tam liste, aralıklar, dağılım. Her aralığı gerçek ölçümlere karşı gerekçelendir.
3. SI adımları. Hangi parametrelerin ölçüleceği; ölçüm yöntemi.
4. Öğretmen/öğrenci bölünmesi. Öğretmenin hangi ayrıcalıklı bilgiyi kullandığı; öğrencinin hangi gözlemleri kullandığı.
5. Güvenlik zarfı. Düşük seviyeli sınırlar, acil durdurmalar, yedek denetleyici.

(a) sıfır-atış simülasyon varyant testi, (b) güvenlik kalkanı, (c) geri alma planı olmadan dağıtma. Ölçülen gerçek değişkenliğin 3×'inden geniş herhangi bir DR aralığını muhtemelen aşırı rastgeleleştirilmiş olarak işaretle.

Geri dönüş. Sıfır-atış aktarım başarısız olursa, DR aralıklarını yarıya daralt ve hedef görev için ince-ayar.
