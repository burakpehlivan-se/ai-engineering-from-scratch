> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/02-ml-fundamentals/05-support-vector-machines/docs/en.md)

# Destek Vektör Makineleri

> İki sınıf arasındaki en geniş sokağı bulun. Tüm fikir budur.

**Tür:** Uygulama
**Diller:** Python
**Ön Koşullar:** Faz 1 (Ders 08 Optimizasyon, 14 Normlar ve Mesafeler, 18 Konveks Optimizasyon)
**Süre:** ~90 dakika

## Öğrenme Hedefleri

- Sıfırdan bir doğrusal SVM uygulayın (hinge kaybı ve primal formülasyonda gradyan inişi ile)
- Maksimum marj ilkesini açıklayın ve eğitilmiş bir modelden destek vektörlerini belirleyin
- Doğrusal, polinomyal ve RBF çekirdeklerini karşılaştırın ve çekirdek hilesinin yüksek boyutlu eşlemeyi nasıl önlediğini açıklayın
- Marj genişliği ile sınıflandırma hataları arasındaki C parametresiyle kontrol edilen takası değerlendirin

## Sorun

İki sınıf veri noktanız var ve bunları ayıran bir çizgi (veya hiperdüzlem) çizmeniz gerekiyor. Sonsuz sayıda çizgi işe yarayabilir. Hangisini seçmelisiniz?

En geniş marja sahip olan. Marj, karar sınırı ile her iki taraftaki en yakın veri noktaları arasındaki mesafedir. Daha geniş bir marj, sınıflandırıcının daha kendine güvenli ve görülmemiş verilere daha iyi genelleme yaptığı anlamına gelir.

Bu sezgi, ML'deki en matematiksel olarak zarif algoritmalardan biri olan Destek Vektör Makinelerini doğurur.

## Kavram

### Maksimum marj sınıflandırıcısı

Doğrusal olarak ayrılabilir veriler için, etiketler y_i ∈ {-1, +1} ve özellik vektörleri x_i ile, sınıfları ayıran bir hiperdüzlem w^T x + b = 0 istiyoruz.

```
maksimize    2 / ||w||     (marj genişliği)
kısıt olarak y_i × (w^T x_i + b) ≥ 1  tüm i için
```

Marj sınırlarında oturan veri noktaları (y_i × (w^T x_i + b) = 1 olanlar) destek vektörleridir. Karar sınırını belirleyen tek noktalardır.

### Destek vektörleri: kritik azınlık

Çoğu eğitim noktası ilgisizdir. Sadece destek vektörleri önemlidir. Bu yüzden SVM'ler tahmin zamanında bellek verimlidir: sadece destek vektörlerini depolamanız gerekir, tüm eğitim setini değil.

### Yumuşak marj: C parametresiyle gürültüyü ele alma

Gerçek veri nadiren mükemmel ayrılabilir. Bazı noktalar sınırın yanlış tarafında veya marjın içinde olabilir. Yumuşak marj formülasyonu, gevşek değişkenler ekleyerek ihlallere izin verir.

| C değeri | Davranış |
|----------|----------|
| Büyük C | İhlalleri ağır cezalandırır. Dar marj, daha az yanlış sınıflandırma. Aşırı uyum |
| Küçük C | Daha fazla ihlale izin verir. Geniş marj, daha fazla yanlış sınıflandırma. Yetersiz uyum |

### Çekirdek hilesi: doğrusal olmayan sınırları ele alma

Doğrusal SVM sadece doğrusal olarak ayrılabilir verilerle çalışır. Ama çoğu gerçek dünya sorunu doğrusal değildir. Çekirdek hilesi, verileri yüksek boyutlu bir uzaya dönüştürerek doğrusal ayrılabilir hale getirir — ama asla o uzayda hesaplama yapmaz.

Yaygın çekirdekler:
- **Doğrusal:** K(x, z) = x^T z — orijinal uzayda çalışır
- **Polinomyal:** K(x, z) = (x^T z + c)^d — polinom özellikler ekler
- **RBF (Gauss):** K(x, z) = exp(-γ||x-z||²) — sonsuz boyutlu uzaya eşler

## Alıştırmalar

1. Sıfırdan bir SVM uygulayın
2. Farklı çekirdekleri görselleştirin ve karşılaştırın
3. C parametresinin etkisini inceleyin

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| SVM | "Sınır çizme" | Maksimum marjla veriyi ayıran model |
| Marj | "Güven aralığı" | Karar sınırı ile en yakın noktalar arası mesafe |
| Destek vektörü | "Kritik noktalar" | Marj sınırlarını belirleyen veri noktaları |
| Çekirdek | "Boyut değiştirici" | Veriyi yüksek boyutlu uzaya dönüştüren fonksiyon |
| C parametresi | "Denge parametresi" | Marj genişliği ile hata arasında denge |
