---
name: attack-audit
description: Saldırı kapsamı, bütçesi, yargıç kimliği ve davranış kümesi için bir kırmızı takım değerlendirme raporunu denetle
version: 1.0.0
phase: 18
lesson: 12
tags: [red-teaming, jailbreak, pair, harmbench, jailbreakbench, asr]
---

Bir kırmızı takım (red-team) değerlendirme raporu verildiğinde, değerlendirmenin yayınlanmış temel çizgileriyle karşılaştırılabilir olup olmadığını ve sonuçlarını destekleyip desteklemediğini denetle.

Çıktı:

1. Saldırı kapsamı. Çalıştırılan her saldırıyı listele: PAIR, GCG, AutoDAN, TAP, PAP, manuel. Eksik saldırı sınıflarını işaretle. Yalnızca bir saldırı ailesi çalıştıran bir rapor sağlamlık iddia edemez.
2. Saldırı başına bütçe. Her istem için sorgu bütçesini her saldırı için raporla. 20 sorguda PAIR başarı iddiaları, 500 adımda GCG başarı iddialarıyla karşılaştırılabilir değildir.
3. Yargıç kimliği. Hangi yargıç LLM kullanıldı (GPT-4-turbo, Llama Guard, StrongREJECT, dahili sınıflandırıcı)? Yargıç kalibrasyonu ASR (saldırı başarı oranı) varyansını yönlendirir.
4. Davranış kümesi. JailbreakBench (100 davranış, 10 kategori), HarmBench (510 davranış, 7 kategori), dahili veya diğer? Kümenin genel ve yeniden üretilebilir olup olmadığını belirt.
5. Aktarım kontrolü. Kırmızı takım bir modele karşı optimize ettiyse, diğer modellere karşı aktarım ASR'leri raporlandı mı? Tek-model ASR, model ailesi sağlamlığı için üst sınır, alt sınır değildir.

Kesin redler:

- Tek bir saldırı ailesine dayanan "modelimiz sağlamdır" iddiası.
- Sorgu bütçesi olmadan raporlanan herhangi bir ASR.
- Yayınlanmış kıyaslamanın yargıcı olmadan kalibre edilmemiş farklı bir yargıç kullanan herhangi bir ASR.

Ret kuralları:

- Kullanıcı "modelimiz hapsi kırmaya karşı dayanıklı mı" diye sorarsa, ikili yanıt vermeyi reddet ve yukarıdaki çok-saldırı, çok-yargıç, aktarım-kontrolü yapısına yönlendir.
- Kullanıcı önerilen bir saldırı araç seti isterse, tek bir öneri vermeyi reddet ve HarmBench üzerinden 2024 ampirik varyansa yönlendir.

Çıktı: Yukarıdaki beş bölümü dolduran, eksik saldırı sınıflarını işaretleyen ve yeniden üretilebilir kıyaslamalara göre ASR'nin eksik mi yoksa fazla mı tahmin edildiğini tahmin eden tek sayfalık bir denetim. Chao ve diğerlerini (arXiv:2310.08419) ve ilgili kıyaslama makalesini her birini bir kez alıntıla.
