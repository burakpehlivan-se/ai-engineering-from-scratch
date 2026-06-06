---
name: skill-feature-selector
description: Doğru özellik seçimi yöntemini seçmek için hızlı başvuru karar ağacı
version: 1.0.0
phase: 2
lesson: 18
tags: [feature-selection, mutual-information, rfe, lasso, tree-importance]
---

# Özellik Seçimi Stratejisi

Doğru özellik seçimi yöntemini seçmek ve uygulamak için hızlı bir başvuru.

## Adım 1: Temizlikle başla

Herhangi bir yöntemi uygulamadan önce, açıkça işe yaramaz özellikleri kaldır:

- **Sabit özellikler**: varyans = 0. Kaldır.
- **Neredeyse sabit özellikler**: varyans < 0.01 (veya senin eşiğin). Kaldır.
- **Yinelenen özellikler**: özdeş sütunlar. Birini tut, geri kalanını düşür.
- **Kimlik sütunları**: satır başına benzersiz, genellenebilir bilgi taşımaz. Kaldır.

Bu saniyeler sürer ve dağınık gerçek dünya veri kümelerinde özelliklerin %10-30'unu ortadan kaldırabilir.

## Adım 2: Durumuna göre bir yöntem seç

### Hızlı Karar Ağacı

1. **< 50 özellik?** Karşılıklı bilgi (mutual information) sıralamasıyla başla. En iyi K'yı tut.
2. **50 - 500 özellik?** Önce varyans eşiği, sonra doğrusal model kullanıyorsan L1 (Lasso), ağaç kullanıyorsan ağaç önemi.
3. **> 500 özellik?** Yöntemleri zincirle: varyans eşiği -> karşılıklı bilgi filtresi (ilk %50) -> hayatta kalanlar üzerinde RFE.
4. **Yorumlanabilirlik gerekli mi?** L1 düzenlileştirme sana tam sıfır/sıfır olmayan değerler verir. Ağaç önemi sıralanmış skorlar verir.
5. **Doğrusal olmayan ilişkileri yakalaman mı gerekiyor?** Karşılıklı bilgi veya ağaç tabanlı önem. L1'den kaçın (yalnızca doğrusal).
6. **Özellik etkileşimlerine ihtiyacın var mı?** RFE veya ağaç tabanlı önem. Filtre yöntemleri etkileşimleri kaçırır.

### Yöntem Başvurusu

| Yöntem | Ne Zaman Kullanılır | Ne Zaman Kaçınılır |
|--------|---------------|---------------|
| Varyans eşiği | Her zaman, ilk adım olarak | Bunu asla atlama |
| Karşılıklı bilgi | Hızlı sıralama, doğrusal olmayan ilişkiler | Özellik etkileşimi tespitine ihtiyacın olduğunda |
| RFE | Kapsamlı seçim, orta özellik sayısı | Çok pahalı modeller, > 1000 özellik |
| L1 / Lasso | Doğrusal modeller, hızlı gömülü seçim | Doğrusal olmayan problemler, yüksek düzeyde ilişkili özellikler |
| Ağaç önemi | Doğrusal olmayan ilişkiler, özellik etkileşimleri | Yüksek kardinaliteli özellikler tarafından yanlı |
| Permütasyon önemi | Modelden bağımsız doğrulama, son kontrol | İlk eleme için çok yavaş |

## Adım 3: Seçimini doğrula

- Seçilen özelliklerle tüm özellikler arasındaki model performansını karşılaştır
- Tek bir eğitim/test bölmesi değil, çapraz doğrulama kullan
- Performans %1-2'den fazla düşerse, yararlı özellikleri kaldırmış olabilirsin
- Performans iyileşirse, gürültüyü başarıyla kaldırmışsın demektir

## Adım 4: Yaygın tuzakları ele al

### İlişkili özellikler
- L1, ilişkili bir gruptan birini rastgele seçer ve diğerlerini sıfırlar
- Önce korelasyon matrisini hesapla ve hangi ilişkili özelliklerin tutulacağına karar ver
- Ağaç önemi, önemi ilişkili özellikler arasında yayar

### Veri sızıntısı
- Özellik seçimini yalnızca eğitim verisine sığdır
- Aynı seçimi test verisine uygula
- Çapraz doğrulamada, özellik seçimi her katın içinde gerçekleşmelidir

### Özellik seçimine aşırı uyum
- Çok fazla iterasyonla RFE, eğitim setine aşırı uyabilir
- Seçim için kullanılan veride değil, tutulan veride doğrula
- Daha sağlam sonuçlar için kararlılık seçimi (alt örneklemlerde tekrarla) kullan

## Adım 5: Üretim kontrol listesi

- [ ] İlk filtre olarak varyans eşiği uygulandı
- [ ] Özellik seçimi yalnızca eğitim verisine sığdırıldı
- [ ] Seçilen özellikler belgelendi (adlar, kullanılan yöntem, skorlar)
- [ ] Performans karşılaştırıldı: seçilen özellikler vs tüm özellikler
- [ ] Çapraz doğrulandı, tek bölme değil
- [ ] Özellik seçimi eğitim pipeline'ına entegre edildi (manuel yapılmadı)
- [ ] Özellik kayması (feature drift) için izleme yerinde (seçilen özellikler eskiyebilir)
