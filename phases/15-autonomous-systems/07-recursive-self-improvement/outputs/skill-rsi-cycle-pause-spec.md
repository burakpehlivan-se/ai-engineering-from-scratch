---
name: rsi-cycle-pause-spec
description: Bir RSI (Recursive Self-Improvement — Özyinelemeli Öz-İyileştirme) pipeline'ının bir sonraki döngüden önce insan incelemesi için duraklaması gereken koşulları belirtin.
version: 1.0.0
phase: 15
lesson: 7
tags: [rsi, self-improvement, alignment, pause-threshold, rsp]
---

Önerilen bir özyinelemeli-öz-iyileştirme pipeline'ı verildiğinde, bir duraklatma spesifikasyonu üretin: bir sonraki döngü başlamadan önce döngüyü insan denetimi için durduran açık koşullar. Duraklatma spesifikasyonu olmayan bir pipeline çalışmaya hazır değildir.

Üretin:

1. **Döngü düzeyinde eşikler.** Ölçülebilir her eksen (yetenek puanı, hizalama puanı, bütçe, trajectory uzunluğu, kaynak kullanımı) için, aşılması döngüyü duraklatan sayısal bir eşik tanımlayın. Eşikler döngü başlamadan önce belirlenmeli ve kayıt altına alınmalıdır.
2. **Döngü-üzeri-döngü deltaları.** Herhangi bir eksenin tek bir döngüde ne kadar hareket edebileceğine dair sınırlar belirleyin. Tek bir döngüde %30+ yetenek sıçraması neredeyse her zaman değerlendirici oyununun (gaming) işaretidir; duraklatın ve denetleyin.
3. **Hizalama boşluğu.** Her döngüden sonra yetenek-eksi-hizalamayı hesaplayın. Boşluk X'ten (operatör tarafından belirlenir) fazla genişlerse, duraklatın. Bu, `code/main.py`'deki simülatörün çalıştırdığı metriktir.
4. **Regresyon gözcüsü.** Herhangi bir eksen bir döngüde Y'den fazla düşerse, duraklatın. Yetenek regresyonları genellikle sürdürümleri takip eder; yakalamak, sahte-ilerleme hızlanmasını önler.
5. **İnsan devam ettirme sözleşmesi.** Döngü bir duraklamadan sonra devam etmeden önce, adlandırılmış bir insanın duraklatma tetikleyicisini incelemesini, uygunsa eşikleri yeniden ayarlamasını ve kararı pipeline-dışı denetim (audit) izine loglamasını isteyin.

Keskin redler:

- Duraklamadan sonra insan eylemi olmadan devam edebilen herhangi bir pipeline.
- Döngünün kendi iç değerlendiricisine bağlı herhangi bir eşik (agent onu oynayabilir).
- Eşik seti agent tarafından düzenlenebilen herhangi bir pipeline.

Ret kuralları:

- Kullanıcı eşikleri baştan adlandıramıyorsa, reddedin. Sonradan belirlenen eşikler eşik değildir; gerekçelendirmedir.
- Pipeline'ın harici (döngü-dışı) bir değerlendiricisi yoksa, reddedin — regresyon ve sürdürüm tespiti dışarıdan bir görüş gerektirir.
- Önerilen devam ettirme sözleşmesi "ekibi bilgilendir ve 24 saat sonra devam et" ise, reddedin. Devam ettirme pozitif bir eylem olmalıdır.

Çıktı formatı:

Şunları içeren tek sayfalık bir spesifikasyon döndürün:

- **Eksenler ve eşikler** (tablo)
- **Döngü-delta sınırları** (tablo)
- **Hizalama boşluğu formülü ve eşiği**
- **Regresyon sınırları**
- **Harici değerlendirici** (ne, ne zaman çalışır)
- **Devam ettirme sözleşmesi** (adlandırılmış sahip, kontrol listesi, log hedefi)
- **İmza satırı** (duraklatma invariant'ını kim sahipleniyor)
