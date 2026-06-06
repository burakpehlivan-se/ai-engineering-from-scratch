---
name: provenance-check
description: Bir eğitim veri kümesini California AB 2013 ve AB TDM opt-out yükümlülüklerine karşı kontrol et
version: 1.0.0
phase: 18
lesson: 27
tags: [data-provenance, ab-2013, tdm-opt-out, legitimate-interest, dpa]
---

Bir dağıtım tarafından kullanılan bir eğitim veri kümesi verildiğinde, California AB 2013 ve AB TDM opt-out'a karşı uyumu kontrol et.

Çıktı:

1. AB 2013 kapsamı. 12 alanı doldur. Eksik veya yalnızca yer-tutucu alanları işaretle. Özetin yayımlandıktan sonra bağlayıcı hale geldiğini not et.
2. Opt-out uyumu. Veri kümesi, makine tarafından okunabilir opt-out sinyallerine (robots.txt, C2PA "Yapay Zeka Eğitimi Yok", TDM.Reservation) saygı gösteriyor mu? Toplama-öncesi filtre yerinde olmalıdır.
3. DPA yargı alanı eşleme. Veri öznelerinin ait olduğu her yargı alanı için, uygulanabilir DPA'yı ve 2025 meşru-menfaat konumunu (İrlanda DPC, Köln Yüksek Bölge Mahkemesi, Hamburg DPA, İngiltere ICO, Brezilya ANPD) belirle.
4. Geri dönüşü olmazlık denetimi. Veri kümesi PII içeriyorsa, hangi unlearning veya iyileştirme prosedürü yerinde? Hiçbir prosedürün eğitim verisini tam olarak iyileştirmediğini kabul et.
5. Kaynak-doğrulama zinciri tamlığı. Veri kaynağından eğitim hattına imzalı bir zincir var mı? Veri kümesi türetilmişse (taranmış + filtrelenmiş), türetmeyi belgele.

Kesin redler:

- Veri kümesi başına 12-alan özeti olmadan AB 2013'e başvuran herhangi bir dağıtım.
- robots.txt veya eşdeğeri opt-out sinyallerine saygı göstermeyen herhangi bir dağıtım.
- Eğitilmiş ağırlıklardan cerrahi veri kaldırmayı varsayan herhangi bir iyileştirme iddiası.

Ret kuralları:

- Kullanıcı belirli bir veri kümesinin "üzerinde eğitmek güvenli mi" olduğunu sorarsa, yargı alanı-yargı alanına analiz olmadan reddet.
- Kullanıcı evrensel bir uyum stratejisi isterse, reddet — yargı alanları maddi olarak farklıdır.

Çıktı: Beş bölümü dolduran, en yüksek riskli uyum boşluğunu belirleyen ve en acil tek iyileştirmeyi adlandıran tek sayfalık bir kontrol. California AB 2013'ü ve AB Telif Hakkı Direktifi TDM istisnasını her birini bir kez alıntıla.
