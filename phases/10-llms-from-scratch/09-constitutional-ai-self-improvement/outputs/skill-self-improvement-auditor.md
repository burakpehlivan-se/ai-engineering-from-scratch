---
name: self-improvement-auditor
description: Önerilen bir kendini geliştirme veya anayasal AI pipeline'ını ölçekte çalışmadan önce denetleyin.
version: 1.0.0
phase: 10
lesson: 9
tags: [alignment, cai, grpo, rlhf, self-improvement, reward-hacking]
---

Anayasal AI (Constitutional AI), RLAIF, GRPO veya herhangi bir kendiliğinden üretilmiş tercih verisi kullandığını iddia eden önerilen bir eğitim pipeline'ı verildiğinde, şunları içeren bir denetim üretin:

1. Ödül kuralı. Tam doğrulayıcıyı belirtin (regex, sympy, test paketi, LLM hakem). Deterministik, stokastik-LLM veya hibrit olarak sınıflandırın. Hiçbir dış grounding (temellendirme) olmayan "kendini geliştirme" döngülerini reddedin — model sinyalini hiçlikten çekemez.
2. Grup istatistikleri. GRPO pipeline'ları için grup boyutunu, avantajların nasıl hesaplandığını (z-skoru vs göreceli sıra) ve grup ödül standart sapması sıfıra çöktüğünde ne olduğunu doğrulayın. Pipeline, sıfır varyans gruplarını atlamalı veya ağırlığını azaltmalı, epsilona bölmemeli ve sinyali gerçekmiş gibi davranmamalıdır.
3. KL bütçesi. Çalışma boyunca kümülatif KL(politika || referans) üzerinde sayısal bir üst sınır. Pipeline, üst sınıra ulaşıldığında durmalı, sıfırlamalı veya daha sıcak bir referansa geçmelidir. Sınırsız KL, sınırsız sapmadır.
4. Çeşitlilik tabanı. Grup başına ödül standart sapması, yanıt uzunluğu varyansı veya n-gram entropisi (görevin izin verdiği) üzerinde ölçülen bir alt sınır. Taban, N ardışık tur boyunca ihlal edilirse, pipeline taze insan verisi veya daha geniş bir prompt dağılımı karıştırmalıdır.
5. İnsan veri kotası. Eğitim karışımında kalan insan yazımı minimum oranı, tipik olarak %5-10. Yalnızca kendi kendine damıtma (self-distillation) pipeline'ları 3-5 turdan sonra çöker. Bunu açıkça belirtin.
6. Mod çöküşü bekçi köpeği. Otomatik kontrolleri işaretleyin: turlar arası ödül standart sapması, tutulan promptlardaki benzersiz n-gram sayısı, uzunluk dağılımı, reddetme oranı. Bunlardan herhangi birinin bir eşiği aşması eğitimi durdurur.
7. Anayasa sapması. CAI pipeline'ları için, sürümlenmiş bir anayasa dosyası, bir değişiklik günlüğü ve bir "anayasal regresyon test seti" gerektirin — düzenlemeler arasında beklenen davranışı değişmemesi gereken promptlar.

Aşağıdaki pipeline'ları onaylamayı reddedin:
- herhangi bir dış doğrulayıcı (kural, araç, ortam) olmadan "sıfır insan verisi" iddia edenler.
- süreç ödül hackleme (PRM) probu olmadan PRM kullananlar (model, ilerleme sağlamadan doğru görünen adımlar yazıyor mu?).
- tutulan bir çeşitlilik kıyaslaması olmadan 5'ten fazla reddetme-örnekleme ince ayar turu çalıştıranlar.
- referans modeli politika ile paylaşanlar (referans yok, KL yok, çapa yok anlamına gelir).
- politikanın aynı modeli olan bir LLM hakemi ile puanlayanlar (hakem kontaminasyonu).

Çıktı: Her kapı için geçti/kaldı, ölçülen veya belirtilen değer ve sinyali üreten pipeline'daki tam adım ile birlikte tek sayfalık bir denetim. Herhangi bir kapı başarısız olursa, onu geçecek asgari uygulanabilir değişikliği listeleyin.
