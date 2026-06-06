---
name: evaluator-rigor-audit
description: Aramaya herhangi bir hesaplama taahhüt etmeden önce, önerilen bir AlphaEvolve tarzı evrimsel kodlama döngüsünün evaluator'ını (değerlendiricisini) denetleyin.
version: 1.0.0
phase: 15
lesson: 3
tags: [alphaevolve, evolutionary-coding, evaluator, reward-hacking, deepmind]
---

Önerilen bir evrimsel kodlama döngüsü (üreteç LLM, program veritabanı, değerlendirici) verildiğinde, değerlendiriciyi denetleyin. Değerlendirici mimaridir; üreteç değiştirilebilir. Bu skill, döngünün gerçek kazanımlar mı yoksa sadece reward-hacked (ödül kandırılmış) çöp mü üretme şansı olduğuna karar verir.

Üretin:

1. **Değerlendirici ayrıştırması.** Değerlendiricinin raporladığı her sinyali adlandırın: doğruluk, performans, kaynak, diğer. Her biri için, (a) nasıl ölçüldüğünü, (b) ne kadar ucuza oynanabileceğini, (c) hold-out girdiler kuralının neye benzediğini belirtin.
2. **Uydurma yüzeyi.** LLM'nin bu domain'deki en olası üç uydurmasını (confabulation) listeleyin: iddia edilen karmaşıklık sınıfları, uç durumlarda iddia edilen doğruluk, ölçüm olmadan iddia edilen performans. Her birini hangi değerlendirici sinyalinin yakaladığını belirtin.
3. **Reward-hacking yüzeyi.** Döngünün amaçlanan görevi yapmadan skoru nasıl en üst düzeye çıkarabileceğine dair üç olası yolu listeleyin (testi geçen kısayol, proxy oyunu, girdilerin ezberlenmesi). Her biri için azaltmayı belirtin.
4. **Determinizm ve tekrarlanabilirlik.** Değerlendirici çıktılarının tolerans dahilinde deterministik olmasını isteyin. Skoru çalıştırmadan çalıştırmaya popülasyon varyansından fazla değişen herhangi bir değerlendiriciyi işaretleyin.
5. **Deployment kontrolü.** Kazanan varyant production'a gönderilecekse, değerlendiricinin kontrol etmediği ayrı bir ön-deployment incelemesi (güvenlik, maliyet, insan incelemesi) isteyin. Arama, deployment'a hazırlığı doğrulamadı.

Keskin redler:

- Değerlendiricinin, makine tarafından kontrol edilebilir bir ground truth (temel doğru) olmadan bir LLM hakemi olduğu herhangi bir döngü. LLM hakemleri oynanabilir.
- Tek bir skaler (sayısal) puan raporlayan ve ayrıştırma yapmayan herhangi bir değerlendirici. Skaler puanlar reward hacking'i güçlendirir.
- Yalnızca eğitim seti değerlendiricileri. Hold-out girdileri vazgeçilmezdir.

Ret kuralları:

- Kullanıcı değerlendiriciyi iki paragrafta tanımlayamıyorsa, reddedin ve önce değerlendirici spesifikasyonunu isteyin. Spesifikasyonu yapılmamış değerlendiricili döngüler hesaplama için hazır değildir.
- Domain doğrulanmamışsa (yaratıcı yazım, açık-uçlu bilimsel hipotez, uzun formlu araştırma), reddedin ve kapalı döngü yerine insan incelemeli hibrit bir pipeline önerin.
- Önerilen deployment yüzeyi geri dönülemezse (production altyapı değişiklikleri, gönderilen bir üründe algoritma değişimi), kapalı-döngü deployment'ı reddedin. Aşamalı rollout ve insan onayı isteyin.

Çıktı formatı:

Şunları içeren tek sayfalık bir memo döndürün:

- **Döngü özeti** (üreteç, değerlendirici, hedef domain)
- **Değerlendirici puanı** (1-5 arası rigor, gerekçeli)
- **Uydurma yüzeyi** (en iyi 3, değerlendirici kapsamıyla)
- **Reward-hacking yüzeyi** (en iyi 3, azaltmalarla)
- **Determinizm ve tekrarlanabilirlik** (puan varyansı vs popülasyon varyansı; tohum kontrolü; geçer/kalır)
- **Deployment'a hazırlık** (kapalı-döngü gönderim izinli mi e/h; gerekli ön-deployment incelemeleri: güvenlik, maliyet, insan)
- **Öneri** (devam / değerlendiriciyi sıkılaştır / farklı bir domain seç)
