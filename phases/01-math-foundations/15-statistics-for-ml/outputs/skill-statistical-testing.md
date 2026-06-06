---
name: skill-statistical-testing
description: ML modellerini karşılaştırmak ve deneyleri değerlendirmek için doğru istatistiksel testi seç
version: 1.0.0
phase: 1
lesson: 15
tags: [statistics, hypothesis-testing, model-comparison]
---

# ML için İstatistiksel Testler

Modelleri karşılaştırırken, A/B deneyleri yürütürken veya sonuçları doğrularken doğru testi nasıl seçersin.

## Karar Kontrol Listesi

1. Ne karşılaştırıyorsun? Ortalamaları, oranları, dağılımları veya korelasyonları mı?
2. Kaç grup var? Bir örneklem ve referans mı, iki grup mu, yoksa birden çok grup mu?
3. Gözlemler eşleştirilmiş mi (aynı test kümesi, aynı katlar) yoksa bağımsız mı?
4. Veriler normal dağılıma sahip mi? n < 30 ve açıkça normal değilse, parametrik olmayan (non-parametric) kullan.
5. Veriler sürekli mi, sıralı mı, kategorik mi?
6. Kaç test çalıştırıyorsun? Birden fazlaysa düzeltme uygula.

## Karar ağacı

```text
Ortalamaları mı karşılaştırıyorsun?
  İki grup?
    Eşleştirilmiş (aynı veri bölmeleri)? --> Eşleştirilmiş t-testi (veya normal değilse Wilcoxon signed-rank)
    Bağımsız? --> Welch'in t-testi (veya normal değilse Mann-Whitney U)
  Birden çok grup?
    Eşleştirilmiş? --> Tekrarlanan ölçümler ANOVA'sı (veya Friedman testi)
    Bağımsız? --> Tek yönlü ANOVA (veya Kruskal-Wallis)

Oranları mı karşılaştırıyorsun?
  İki grup? --> Ki-kare testi veya Fisher'ın kesin testi (küçük n)
  Birden çok grup? --> Ki-kare testi

Dağılımları mı karşılaştırıyorsun?
  Bir dağılım referans mı? --> Kolmogorov-Smirnov testi
  İkisi de ampirik mi? --> İki örneklem KS testi

İlişki mi ölçüyorsun?
  İkisi de sürekli, kabaca normal? --> Pearson korelasyonu
  Sıralı veya normal değil? --> Spearman sıra korelasyonu
  Kategorik x Kategorik? --> Bağımsızlık ki-kare testi

Birçok test mi çalıştırıyorsun?
  Bonferroni düzeltmesi uygula: duzeltilmis_alpha = alpha / test_sayisi
  Ya da Holm-Bonferroni kullan (daha az muhafazakâr, yine de aile bazlı hatayı kontrol eder)
```

## Her testin ne zaman kullanılacağı

| Test | Veri tipi | Varsayımlar | ML kullanım durumu |
|---|---|---|---|
| Eşleştirilmiş t-testi | Sürekli, eşleştirilmiş | Normal farklar | Aynı k-katlı bölmelerde 2 modeli karşılaştırma |
| Wilcoxon signed-rank | Sürekli/sıralı, eşleştirilmiş | Yok (parametrik olmayan) | 2 modeli karşılaştırma, küçük k (5-10 kat) |
| Welch'in t-testi | Sürekli, bağımsız | Kabaca normal | İki ayrı veri kümesinde model karşılaştırma |
| Mann-Whitney U | Sürekli/sıralı, bağımsız | Yok | Gecikme dağılımlarını karşılaştırma |
| ANOVA | Sürekli, 3+ grup | Normal, eşit varyans | Birden çok model mimarisini karşılaştırma |
| Kruskal-Wallis | Sürekli/sıralı, 3+ grup | Yok | Birden çok modeli karşılaştırma, normal olmayan metrikler |
| Ki-kare | Kategorik sayımlar | Beklenen sayım >= 5 | Sınıf dağılımlarını, karışıklık matrislerini karşılaştırma |
| Fisher'ın kesin testi | Kategorik sayımlar | Küçük örneklem | Nadir olay karşılaştırması |
| KS testi | Sürekli | Yok | Tahminlerin beklenen dağılımı takip edip etmediğini kontrol etme |
| Bootstrap CI | Herhangi bir istatistik | Yok | AUC, F1, herhangi bir metrik için güven aralığı |
| McNemar'ın testi | Eşleştirilmiş ikili | Yok | Aynı test kümesinde iki sınıflandırıcıyı karşılaştırma |

## Model karşılaştırma reçetesi

1. Deneyleri çalıştırmadan önce metrik ve anlamlılık düzeyini (alpha = 0.05) tanımla.
2. Her iki modeli de aynı k-katlı çapraz doğrulama bölmelerinde çalıştır (k = 5 veya 10).
3. Eşleştirilmiş puanları topla: (a_1, b_1), (a_2, b_2), ..., (a_k, b_k).
4. Farkları hesapla: d_i = b_i - a_i.
5. Eşleştirilmiş test çalıştır (k <= 10 için Wilcoxon, k > 10 veya normal farklar için eşleştirilmiş t-testi).
6. Şunları raporla: p-değeri, ortalama fark, %95 güven aralığı, etki büyüklüğü (Cohen's d).
7. Eğer p < alpha VE etki büyüklüğü anlamlıysa, fark gerçektir ve harekete geçmeye değer.

## Yaygın hatalar

- Veri eşleştirildiğinde bağımsız test kullanmak. Her iki model de aynı test katlarında değerlendirildiyse, eşleştirilmiş test kullanmalısın. Bağımsız testler eşleştirmeyi çöpe atar ve istatistiksel gücü kaybeder.
- p < 0.05'i etki büyüklüğü olmadan raporlamak. İstatistiksel olarak anlamlı %0.1'lik bir doğruluk iyileşmesi, dağıtmaya değmez. Her zaman Cohen's d'yi veya ham ortalama farkı hesapla.
- Modelleri farklı test kümelerinde karşılaştırmak. Test kümesi her iki model için de aynı OLMALIDIR. Farklı test kümeleri karşılaştırmayı anlamsız kılar.
- 20 karşılaştırma çalıştırıp en iyisini Bonferroni düzeltmesi olmadan raporlamak. 20 testle alpha = 0.05'te, şans eseri 1 yanlış pozitif beklersin.
- Dengesiz verilerde doğruluğu (accuracy) kullanmak. %99 çoğunluk sınıfında, önemsiz bir sınıflandırıcı %99 elde eder. F1, precision-recall AUC veya Matthews korelasyon katsayısı kullan.
- Çapraz doğrulama katlarını bağımsız örnekler olarak ele almak. Eğitim verilerini paylaşırlar, bu da bağımsızlık varsayımını ihlal eder. Düzeltilmiş yeniden örneklenmiş t-testi bunu hesaba katar.

## Hızlı başvuru: etki büyüklüğü yorumu

| Cohen's d | Yorum |
|---|---|
| 0.2 | Küçük etki |
| 0.5 | Orta etki |
| 0.8 | Büyük etki |
| > 1.0 | Çok büyük etki |

| Raporlanacak | Neden |
|---|---|
| p-değeri | Fark gerçek mi? |
| Güven aralığı | Fark ne kadar büyük olabilir? |
| Etki büyüklüğü (Cohen's d) | Fark anlamlı mı? |
| Örneklem büyüklüğü (n veya k kat) | Sonuca güvenebilir miyiz? |
