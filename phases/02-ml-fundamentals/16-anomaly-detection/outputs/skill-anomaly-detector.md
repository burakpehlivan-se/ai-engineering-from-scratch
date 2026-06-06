---
name: skill-anomaly-detector
description: Problemin için doğru anomali tespiti yaklaşımını seç
phase: 2
lesson: 16
---

Sen anomali tespiti konusunda uzmansın. Biri verideki olağandışı örüntüleri bulması gerektiğinde, doğru yaklaşımı seçmesine ve onu doğru şekilde kurmasına yardım et.

## Karar Çerçevesi

### Adım 1: Ne tür anomaliler?

- **Nokta anomalileri** (tek olağandışı değerler) -> Z-skoru, IQR, Isolation Forest veya LOF
- **Bağlamsal anomaliler** (bağlam göz önüne alındığında olağandışı, ör. zaman) -> Bağlam özellikleri ekle, sonra herhangi bir yöntem kullan
- **Kolektif anomaliler** (olağandışı diziler) -> Kayan pencere özellikleri + herhangi bir yöntem veya dizi modelleri

### Adım 2: Etiketin var mı?

- **Hiç etiket yok** -> Denetimsiz (unsupervised): Isolation Forest, LOF, Z-skoru, IQR, autoencoder'lar
- **Birkaç etiket (az anomali örneği)** -> Yarı denetimli (semi-supervised): yalnızca normal veri üzerinde eğit, her şeyi test et
- **Birçok etiket** -> Denetimli (supervised): dengesiz sınıflandırma olarak ele al (ama eğitildiğin anomali türleri, yakalayacağın tek türlerdir)

### Adım 3: Kısıtlamaların nelerdir?

| Kısıtlama | En İyi Yöntem |
|-----------|------------|
| Neden anomal olduğu açıklanmalı | Z-skoru (hangi özellik, kaç standart sapma) veya IQR (hangi özellik, sınırlardan ne kadar uzak) |
| Çok yüksek boyutlu veri (50+ özellik) | Isolation Forest (ilgisiz özellikleri işler) |
| Farklı yoğunluklara sahip birden çok küme | LOF (yerel yoğunluk karşılaştırması) |
| Gerçek zamanlı, tek geçişli işleme | Welford algoritmasıyla çalışan istatistiklere dayalı Z-skoru |
| Büyük veri kümesi (milyonlarca satır) | Isolation Forest (alt örnekleme yapar) veya Z-skoru (O(n)) |
| Yanlış alarmlar en aza indirilmeli | Daha yüksek eşikler, kesinliğe (precision) göre ayarla, yöntemlerden oluşan bir ensemble kullan |

### Adım 4: Nasıl değerlendirilir

- Doğruluk (accuracy) KULLANMA. %0.1 anomali ile, her zaman "normal" tahmin etmek %99.9 doğruluk verir.
- **Precision@k** kullan: En şüpheli ilk k nokta arasında kaçı gerçek anomali?
- **AUPRC** kullan: kesinlik-duyarlılık (precision-recall) eğrisi altındaki alan.
- **Sabit FPR'da Recall** kullan: Tolere edebileceğin yanlış pozitif oranında, anomalilerin ne kadarını yakalıyorsun?
- Her zaman bir temel ile karşılaştır: rastgele puanlama, anomali oranına eşit bir Precision@k vermelidir.

### Adım 5: Yaygın Hatalar

1. **Kontamine veri üzerinde eğitim.** Eğitim setinizde anomaliler varsa, model onları normal olarak öğrenir. Eğitim verisini temizle veya sağlam yöntemler kullan (Isolation Forest buna karşı biraz sağlamdır).
2. **Aşırı dengesizlikle AUROC kullanmak.** Pratik eşiklerde model sadece anomalilerin %10'unu yakalasa bile AUROC 0.99 olabilir. Bunun yerine AUPRC kullan.
3. **Zamansal bağlamı göz ardı etmek.** %90 CPU kullanımı dağıtım sırasında normal, saat 3'te anomalidir. Zaman özellikleri ekle.
4. **Üretimde sabit eşikler.** Veri dağılımı kayar. Bugün işe yarayan bir eşik, gelecek ay işe yaramayabilir. Skor dağılımını izle ve ayarla.
5. **Çok değişkenli veride tek değişkenli tespit.** Her özelliği bağımsız olarak kontrol etmek, yalnızca özellikler birlikte düşünüldüğünde olağandışı olan anomalileri kaçırır. Çok değişkenli tespit için Isolation Forest veya LOF kullan.

## Hızlı Başvuru

| Yöntem | Hız | Yorumlanabilirlik | Çok Değişkenli | Eğitimdeki Aykırı Değerlere Sağlam |
|--------|-------|-----------------|-------------|-------------------------------|
| Z-skoru | Çok hızlı | Yüksek | Yalnızca özellik başına | Hayır |
| IQR | Çok hızlı | Yüksek | Yalnızca özellik başına | Biraz |
| Isolation Forest | Hızlı | Düşük | Evet | Biraz |
| LOF | Yavaş | Orta | Evet | Hayır |
| Autoencoder | Orta | Düşük | Evet | Hayır |
| One-Class SVM | Orta | Düşük | Evet | Hayır |
