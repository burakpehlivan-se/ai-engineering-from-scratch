---
name: skill-feature-selector
description: Doğru feature selection method'unu seçmek için hızlı başvuru karar ağacı
version: 1.0.0
phase: 2
lesson: 18
tags: [feature-selection, mutual-information, rfe, lasso, tree-importance]
---

# Feature Selection Stratejisi

> Orijinal: source/phases/02-ml-fundamentals/18-feature-selection/outputs/skill-feature-selector.md

Doğru feature selection method'unu seçmek ve uygulamak için hızlı başvuru.

## Adım 1: Temizlikle başla

Herhangi bir method uygulamadan önce, bariz işe yaramaz özellikleri kaldır:

- **Sabit özellikler**: varyans = 0. Kaldır.
- **Sabite yakın özellikler**: varyans < 0.01 (veya senin eşiğin). Kaldır.
- **Yinelenen özellikler**: aynı sütunlar. Birini tut, diğerini at.
- **ID sütunları**: satır başına benzersiz, genellenebilir bilgi taşımaz. Kaldır.

Bu işlem saniyeler sürer ve dağınık gerçek dünya veri kümelerinde özelliklerin %10-30'unu eleyebilir.

## Adım 2: Durumuna göre bir method seç

### Hızlı Karar Ağacı

1. **< 50 özellik?** Mutual information sıralamasıyla başla. En iyi K kadarını tut.
2. **50 - 500 özellik?** Önce variance threshold kullan, ardından linear model kullanıyorsan L1 (Lasso), tree kullanıyorsan tree importance.
3. **> 500 özellik?** Method'ları zincirle: variance threshold -> mutual information filtresi (ilk %50) -> kalanlara RFE.
4. **Yorumlanabilirlik mi gerekiyor?** L1 regularization sana tam sıfır/sıfır değil verir. Tree importance sıralı puanlar verir.
5. **Nonlinear ilişkiler mi yakalaman gerekiyor?** Mutual information veya tree-based importance. L1'den kaçın (sadece linear).
6. **Özellik etkileşimleri mi gerekiyor?** RFE veya tree-based importance. Filter method'lar etkileşimleri kaçırır.

### Method Referansı

| Method | Ne Zaman Kullanılır | Ne Zaman Kaçınılır |
|--------|------------|---------------|
| Variance threshold | Her zaman, ilk adım olarak | Bunu asla atlama |
| Mutual information | Hızlı sıralama, nonlinear ilişkiler | Özellik etkileşim tespiti gerektiğinde |
| RFE | Kapsamlı seçim, orta ölçekli özellik sayısı | Çok pahalı modeller, > 1000 özellik |
| L1 / Lasso | Linear modeller, hızlı embedded seçim | Nonlinear problemler, yüksek korelasyonlu özellikler |
| Tree importance | Nonlinear ilişkiler, özellik etkileşimleri | Yüksek kardinaliteli özellikler yanlılık yaratır |
| Permutation importance | Model-agnostic doğrulama, son kontrol | İlk tarama için çok yavaş |

## Adım 3: Seçimini doğrula

- Seçilen özelliklerle vs tüm özelliklerle model performansını karşılaştır
- Tek bir train/test bölmesi değil, cross-validation kullan
- Performans %1-2'den fazla düşerse yararlı özellikleri kaldırmış olabilirsin
- Performans iyileşirse gürültüyü başarıyla temizlemişsin demektir

## Adım 4: Yaygın tuzakları yönet

### İlişkili özellikler
- L1, ilişkili bir gruptan keyfi olarak birini seçer ve diğerlerini sıfırlar
- Önce korelasyon matrisini hesapla ve hangi ilişkili özelliklerin kalacağına karar ver
- Tree importance, ilişkili özellikler arasında önemi dağıtır

### Veri sızıntısı (data leakage)
- Feature selection'ı yalnızca eğitim verisine uydur
- Aynı seçimi test verisine uygula
- Cross-validation'da feature selection her fold'un içinde gerçekleşmelidir

### Feature selection'a overfitting
- Çok fazla iterasyonlu RFE, eğitim setine overfit olabilir
- Seçim için kullanılan veriyle değil, ayrılmış veriyle doğrula
- Daha sağlam sonuçlar için stability selection (altörneklemlerde tekrarla) kullan

## Adım 5: Üretim kontrol listesi

- [ ] İlk filtre olarak variance threshold uygulandı
- [ ] Feature selection yalnızca eğitim verisine uyarlandı
- [ ] Seçilen özellikler belgelendi (isimler, kullanılan method, skorlar)
- [ ] Performans karşılaştırıldı: seçilen özellikler vs tüm özellikler
- [ ] Cross-validation ile değerlendirildi, tek bölmeli değil
- [ ] Feature selection eğitim pipeline'ına entegre edildi (manuel yapılmadı)
- [ ] Özellik kayması (feature drift) için izleme kuruldu (seçilen özellikler güncelliğini yitirebilir)
