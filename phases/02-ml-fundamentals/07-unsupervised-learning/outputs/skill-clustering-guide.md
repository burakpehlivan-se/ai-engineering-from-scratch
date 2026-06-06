---
name: skill-clustering-guide
description: Veri şekline, gürültüye ve kısıtlamalara göre doğru kümeleme algoritmasını seç
version: 1.0.0
phase: 2
lesson: 7
tags: [clustering, k-means, dbscan, hierarchical, gmm, unsupervised]
---

# Kümeleme Algoritması Seçim Kılavuzu

Kümeleme için tek bir en iyi algoritma yoktur. Doğru seçim küme şekline, küme sayısını bilip bilmemenize, veride ne kadar gürültü olduğuna ve veri kümesinin ne kadar büyük olduğuna bağlıdır.

## Karar Kontrol Listesi

1. Küme sayısını biliyor musun?
   - Evet: K-Means veya GMM
   - Hayır: DBSCAN (kümeleri otomatik bulur) veya hiyerarşik (dendrogramı farklı seviyelerde kes)

2. Kümelerin şekli nedir?
   - Kabaca küresel (blob benzeri): K-Means
   - Farklı boyutlarda eliptik: GMM
   - Keyfi şekiller (hilal, halka, zincir): DBSCAN
   - İç içe veya hiyerarşik: hiyerarşik kümeleme

3. Veri gürültü veya aykırı değer içeriyor mu?
   - Evet: DBSCAN (gürültü noktalarını açıkça etiketler) veya GMM (düşük olasılıklı noktalar aykırı değerdir)
   - Hayır: K-Means yeterlidir

4. Yumuşak atamalar (olasılıklar) mı gerekiyor?
   - Evet: GMM, her küme için P(küme | veri noktası) verir
   - Hayır: K-Means veya DBSCAN sert atamalar verir

5. Veri kümesi ne kadar büyük?
   - 10.000'in altında: her algoritma çalışır
   - 10.000 ile 1.000.000 arası: K-Means (hızlı), Mini-Batch K-Means (daha hızlı)
   - 1.000.000'un üzerinde: Mini-Batch K-Means veya BIRCH. Hiyerarşik çok yavaş.

## Her yaklaşımın ne zaman kullanılacağı

**K-Means**: varsayılan başlangıç noktası. Hızlı (O(n * k * iterasyon)), basit ve birçok problem için yeterince iyi. K'yı seçmek için dirsek yöntemini veya siluet skorunu kullan. Sınırlamalar: küresel kümeler varsayar, ilk değer atamasına duyarlıdır (K-Means++ kullan veya birden çok kez çalıştır), farklı küme boyutlarını iyi işleyemez.

**DBSCAN**: keyfi şekilli kümeleri keşfetmek ve aykırı değerleri otomatik olarak tespit etmek için en iyisi. İki parametre: eps (komşuluk yarıçapı) ve min_samples (minimum yoğunluk). K belirtilmesini gerektirmez. Sınırlamalar: kümeler çok farklı yoğunluklara sahipse zorlanır ve eps ayarı zor olabilir. eps'yi tahmin etmek için k-mesafe grafiği kullan: her noktanın k'ıncı en yakın komşusuna olan mesafeyi hesapla, sırala ve bir dirsek ara.

**Hiyerarşik (Birleştirici)**: birleştirmelerin ağacını oluşturur. Kümelerin yapısını birden çok detay düzeyinde keşfetmek istediğinde yararlıdır (dendrogramı farklı yüksekliklerde kes). Ward bağlantısı sıkı kümeler için en iyi çalışır. Tekli bağlantı uzun kümeleri bulur ama gürültüye duyarlıdır. Sınırlamalar: O(n^2) bellek ve O(n^3) zaman, bu da büyük veri kümeleri için pratik değildir.

**GMM (Gauss Karışım Modelleri)**: olasılıksal atamalı yumuşak kümeleme. Her kümeyi kendi ortalaması ve kovaryansı olan bir Gauss dağılımı olarak modeller. Kümeler eliptik veya örtüşüyorsa K-Means'ten daha iyi. Bileşen sayısını seçmek için BIC (Bayes Bilgi Kriteri) kullan. Sınırlamalar: Gauss dağılımları varsayar, dışbükey olmayan şekillerde başarısız olabilir, ilk değer atamasına duyarlıdır.

## Küme kalitesini değerlendirme (etiket yok)

| Metrik | Ne ölçer | Aralık | Ne zaman kullanılır |
|--------|-----------------|-------|----------|
| Siluet skoru | Uyum vs ayrım | -1 ile 1 (yüksek daha iyi) | K değerlerini veya algoritmaları karşılaştırma |
| Atalet (küme içi SS) | Kümelerin sıkılığı | 0 ile sonsuz (düşük daha iyi) | K-Means için dirsek yöntemi |
| BIC / AIC | Karmaşıklık cezasıyla model uyumu | Düşük daha iyi | GMM bileşen sayısını seçme |
| Calinski-Harabasz indeksi | Varyanslar arası / içi oranı | Yüksek daha iyi | Hızlı karşılaştırma |
| Davies-Bouldin indeksi | Kümeler arası ortalama benzerlik | Düşük daha iyi | Örtüşen kümeleri cezalandırır |

## Yaygın hatalar

- Özellikleri ölçeklendirmeden K-Means çalıştırmak (büyük ölçekli özellikler mesafe hesaplamasına hakim olur)
- Gerçek veri yüksek boyutlu olduğunda 2B'de veriye göz atarak K seçmek (siluet skorlarını kullan)
- Küresel olmayan kümelerde (hilal veya halka şeklinde) K-Means kullanmak (DBSCAN gerekir)
- DBSCAN eps'yi çok büyük (her şey tek küme) veya çok küçük (her şey gürültü) ayarlamak
- Küme etiketlerini temel gerçekmiş gibi görmek (kümeleme keşif amaçlıdır; alan bilgisiyle doğrula)
- 20.000'den fazla noktaya sahip veri kümelerinde hiyerarşik kümeleme çalıştırmak (bellek ve zaman patlar)

## Hızlı başvuru

| Algoritma | Küme şekli | K'yı bulur | Gürültüyü işler | Yumuşak atamalar | Ölçeklenebilirlik |
|-----------|--------------|---------|---------------|-----------------|-------------|
| K-Means | Küresel | Hayır (K'yı sen ayarlarsın) | Hayır | Hayır | Milyonlar |
| Mini-Batch K-Means | Küresel | Hayır | Hayır | Hayır | On milyonlar |
| DBSCAN | Keyfi | Evet | Evet | Hayır | Yüz binler |
| Hiyerarşik | Herhangi biri (bağlantıya bağlı) | Esnek (dendrogramı kes) | Bağlantıya bağlı | Hayır | 20k'nin altında |
| GMM | Eliptik | Hayır (bileşen sayısını sen ayarlarsın) | Kısmi (düşük olasılık) | Evet | 100k'nin altında |
| HDBSCAN | Keyfi | Evet | Evet | Kısmi | Yüz binler |
