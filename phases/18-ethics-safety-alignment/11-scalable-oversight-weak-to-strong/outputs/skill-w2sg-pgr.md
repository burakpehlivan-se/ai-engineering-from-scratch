---
name: w2sg-pgr
description: Ölçeklenebilir-denetim veya W2SG (zayıftan-güçlüye genelleme) iddiasını performans-boşluğu-geri-kazanılan (PGR) metriği aracılığıyla denetle
version: 1.0.0
phase: 18
lesson: 11
tags: [scalable-oversight, weak-to-strong, pgr, debate, recursive-reward-modeling]
---

Ölçeklenebilir-denetim veya W2SG makalesi / raporu verildiğinde, kurulumun iddiasını destekleyip desteklemediğini denetle.

Çıktı:

1. Zayıf / güçlü belirleme. Zayıf denetçiyi ve güçlü modeli açıkça adlandır. Yetenek boşluğu parametrelerde, eğitim token'larında, kıyaslama puanında veya göreve özgü değerlendirmede mi ölçülüyor?
2. Tavan tanımı. Modelin görevdeki denetimli tavanı nedir? Tavan olmadan PGR hesaplanamaz.
3. PGR hesaplaması. PGR = (ince-ayarlı - zayıf) / (tavan - zayıf). İşareti, büyüklüğü ve paydayı kontrol et. Küçük paydalar PGR'yi yapay olarak şişirir.
4. Öncül sızıntı kontrolü. Güçlü modelin ön eğitim verisi görevin zemin gerçeğini içeriyor mu? İçeriyorsa, "geri kazanma" genelleştirme yerine öncül getirimi olabilir.
5. Hizalama-vs-yetenek bölünmesi. Zayıftan-güçlüye boşluk bir yetenek boşluğu mu yoksa bir hizalama boşluğu mu? Burns ve diğerleri 2023, kendi boşluklarının yetenek-şeklinde olduğunu açıkça belirtir; hizalama-şeklindeki boşluklar farklı davranabilir.

Ölçeklenebilir-denetim mekanizması denetimleri için:
- Münazara: yargıcın bilgisini, münazara yapıyı ve görevin hakikat-yanlılarını ödüllendirip ödüllendirmediğini belirle. Khan ve diğerleri 2024'ü (arXiv:2402.06782) münazaranın nerede yardımcı olduğu ve nerede başarısız olduğu konusunda alıntıla.
- RRM (özyineli ödül modellemesi): özyinele derinliğini ve U+1 zaten güvenilmezse ne olduğunu belirle.
- Görev ayrıştırması: ayrıştırma prosedürünü ve alt görevlerin bağımsız olarak kontrol edilip edilemeyeceğini belirle.

Kesin redler:

- Altın etiketler üzerinde tavan olmadan yapılan herhangi bir PGR iddiası.
- Hizalamayı çözdüğünü iddia eden herhangi bir W2SG iddiası — W2SG, hizalamayı değil, yetenek geri kazanımını ölçer.
- 2024 münazara ampirik literatürünü görmezden gelen herhangi bir münazara mekanizması iddiası.

Ret kuralları:

- Kullanıcı "W2SG süper hizalamayı çözüyor mu" diye sorarsa, ikili yanıtı reddet ve PGR'nin bir çözüm değil ölçülebilir bir metrik olduğunu açıkla.
- Kullanıcı hangi ölçeklenebilir-denetim mekanizmasının en iyi olduğunu sorarsa, reddet — yanıt göreve bağlıdır.

Çıktı: Yukarıdaki beş bölümü dolduran, PGR'yi raporlayan veya talep eden ve zayıf-güçlü boşluğunun yetenek-şeklinde mi yoksa hizalama-şeklinde mi olduğunu işaretleyen tek sayfalık bir denetim. Burns ve diğerleri 2023'ü ve Lang ve diğerlerini (arXiv:2501.13124) her birini bir kez alıntıla.
