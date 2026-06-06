---
name: skill-regression
description: Veri özelliklerine ve problem kısıtlamalarına göre doğru regresyon yaklaşımını seç
version: 1.0.0
phase: 2
lesson: 2
tags: [regression, linear-regression, polynomial-regression, ridge, regularization]
---

# Regresyon Stratejisi Kılavuzu

Regresyon, sürekli değerleri tahmin eder. Doğru yaklaşım, özellikler ile hedef arasındaki ilişkiye, özellik sayısına ve aşırı uyum (overfitting) riskine bağlıdır.

## Karar Kontrol Listesi

1. Özellikler ile hedef arasındaki ilişki yaklaşık olarak doğrusal mı?
   - Evet: sıradan doğrusal regresyonla başla
   - Hayır: polinom özellikler veya doğrusal olmayan bir model dene

2. Örneklemlere göre kaç özelliğin var?
   - Az özellik, çok örnek: sıradan doğrusal regresyon yeterlidir
   - Çok özellik, az örnek: düzenlileştirme (Ridge veya Lasso) kullan
   - Örneklerden fazla özellik: özellik seçmek için Lasso (L1) veya tüm ağırlıkları küçültmek için Ridge (L2)

3. Yorumlanabilirliğe ihtiyacın var mı?
   - Evet: az özellikli doğrusal regresyon veya otomatik özellik seçimi için Lasso
   - Hayır: polinom özellikler veya ağaç tabanlı modellere ya da sinir ağlarına geç

4. Veri kümen küçük mü (10.000 satırın altında)?
   - Hız için normal denklemi (kapalı form çözüm) kullan
   - Güvenilir değerlendirme için çapraz doğrulama şarttır

5. Veri kümen büyük mü (milyonlarca satır)?
   - Stokastik gradyan inişi (SGD) veya mini-batch gradyan inişi kullan
   - O(n^3) matris tersi nedeniyle normal denklem çok yavaştır

## Her yaklaşımın ne zaman kullanılacağı

**Sıradan Doğrusal Regresyon (OLS)**: Herhangi bir regresyon görevi için temel. Buradan başla. R-kare kabul edilebilir ve model basitse, burada dur.

**Polinom Regresyonu**: Saçılım grafiğinde düz değil bir eğri görünüyor. Derece 2 ile başla. Yalnızca doğrulama performansıyla haklıysan artır. Derece > 5 neredeyse her zaman aşırı uyar.

**Ridge Regresyonu (L2)**: Birçok ilişkili özellik. Tüm ağırlıklar sıfıra doğru küçülür ama hiçbiri tam olarak sıfır olmaz. Tüm özelliklerin katkıda bulunduğuna inanıyorsan iyi.

**Lasso Regresyonu (L1)**: Birçok özellik ve yalnızca birkaçının önemli olduğundan şüpheleniyorsun. Lasso, ilgisiz özelliklerin ağırlıklarını tam olarak sıfıra götürerek otomatik özellik seçimi yapar.

**Elastik Ağ (Elastic Net)**: L1 ve L2 cezalarını birleştirir. Birçok ilişkili özelliğiniz var ve biraz özellik seçimi istiyorsanız kullanın.

## Yaygın hatalar

- Gradyan inişinden önce özellik ölçeklemeyi atlamak (yakınsama aşırı yavaş olur)
- Hiperparametreleri ayarlamak için test seti performansını kullanmak (doğrulama seti veya çapraz doğrulama kullan)
- Doğrulama hatasını kontrol etmeden yüksek dereceli polinomlar yerleştirmek (eğitim R^2'si her zaman dereceyle artar)
- Artık (residual) grafiklerini göz ardı etmek (artıklarda örüntü varsa R^2 yanıltıcı olabilir)
- R^2'yi tek metrik olarak görmek (artık dağılımını, MAE'yi ve alana özgü eşikleri kontrol et)

## Hızlı başvuru

| Yöntem | Ne zaman kullanılır | Düzenlileştirme | Özellik seçimi |
|--------|------------|---------------|-------------------|
| OLS | Temel, az özellik | Yok | Manuel |
| Ridge | Çok özellik, tümü ilgili | L2 (küçült) | Hayır |
| Lasso | Çok özellik, azı ilgili | L1 (sıfıra) | Otomatik |
| Elastik Ağ | Çok ilişkili özellik | L1 + L2 | Kısmi |
| Polinom | Doğrusal olmayan ilişki | Üstüne Ridge/Lasso ekle | Manuel derece seçimi |
