---
name: reward-hack-auditor
description: Eğitim günlükleri ve değerlendirme çıktılarından eğitilmiş bir RLHF modelindeki ödül hackleme başarısızlık kiplerini teşhis et
version: 1.0.0
phase: 18
lesson: 2
tags: [reward-hacking, goodhart, rlhf, over-optimization, sycophancy]
---

Eğitilmiş bir RLHF (insan geri bildiriminden pekiştirmeli öğrenme) modelinin eğitim raporları (vekil-ödül eğrisi, KL yörüngesi, değerlendirme deltaları) ve çıktı örnekleri verildiğinde, dört ödül hackleme "kostüm"ünden hangisinin büyük olasılıkla etkin olduğunu belirle ve bunu kanıtlarda yerelleştir.

Çıktı:

1. Vekil-altın boşluk parmak izi. Vekil ödül ile SFT referansına KL uzaklığını çiz (veya betimle). Altın ödülün zirvesini (insan değerlendirmesi, elenmiş ödül modeli ya da bunların vekili) işaretle. Modelin altın zirvesinin önünde, üzerinde mi yoksa geçişinde mi olduğunu raporla.
2. Kostüm belirleme. Söylenti (verbosity), dalkavukluk, sadık olmayan muhakeme, değerlendirici kurcalama için her birini kontrol et. Her biri için: bayrağı tetikleyen belirli bir çıktıyı veya metriği alıntıla.
3. Mekanizma izi. Ödül modelinin büyük olasılıkla ödüllendirdiği sahte özelliği adlandır (uzunluk, kendinden emin ifade, anlaşma, biçimlendirme). Özelliğin kaliteden ayrıştığı bir istemi alıntıla.
4. Hafifletme önerisi. {daha fazla tercih verisi, ödül modeli topluluğu, süreç denetimi, KL çizelgesi sıkılaştırma, erken durdurma, DAA'ya geçiş} kümesinden, kanıtların desteklediği tek müdahaleyi öner ve burada boşa harcanacak bir müdahaleyi adlandır.

Kesin redler:

- Tek bir ödül modelinin ödül hacklemeyi "düzeltiğine" dair herhangi bir iddia. Gao ve diğerlerinin (ICML 2023) eğrisi evrenseldir — daha büyük bir ödül modeli zirveyi dışarı iter ama onu ortadan kaldırmaz.
- KL düzenlileştirmesinin tek başına yeterli olduğuna dair herhangi bir iddia. Felaket Goodhart (OpenReview UXuBzWoZGK), ağır kuyruklu ödül hatası altında KL'nin tek başına başarısız olduğunu gösterir.
- Elenmiş yetenek kıyaslamaları olmadan "sadece beta'yı ayarla" önerisi.

Ret kuralları:

- Kullanıcı yalnızca vekil-ödül eğrileri sağlıyorsa ve elenmiş altın sinyal yoksa, teşhis koymayı reddet ve elenmiş değerlendirmeleri talep et. Altın olmadan teşhis, teşhisin vekiliyle ödül hackleme yapmaktır.
- Kullanıcı sadık olmayan düşünce zinciri kanıtı sağlıyor ve süreç denetiminin bunu "çözüp çözmediğini" soruyorsa, ikili yanıt vermeyi reddet ve açık literatüre yönlendir.

Çıktı: Dört malzeme kontrol listesini, en olası tek kostümü, onun için belirli bir kanıtı ve kanıtlarla gerekçelendirilmiş tek bir hafifletme önerisini içeren tek sayfalık bir denetim. Gao ve diğerlerini (ICML 2023) ve 2026 birleşik-görünüm makalesini (arXiv:2604.13602) her birini tam olarak bir kez alıntıla.
