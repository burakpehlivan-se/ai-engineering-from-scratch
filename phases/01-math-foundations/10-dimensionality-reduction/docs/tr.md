> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/10-dimensionality-reduction/docs/en.md)

# Boyut Azaltma

> Yüksek boyutlu verinin yapısı vardır. Doğru açıdan bakarak bulursunuz.

**Tür:** Uygulama
**Diller:** Python
**Ön Koşullar:** Faz 1, Ders 01 (Doğrusal Cebir Sezgisi), 02 (Vektörler, Matrisler ve İşlemler), 03 (Özdeğerler ve Özvektörler), 06 (Olasılık ve Dağılımlar)
**Süre:** ~90 dakika

## Öğrenme Hedefleri

- Sıfırdan PCA uygulayın: veriyi merkezle, kovaryans matrisini hesapla, özdeğere ayıkla ve projekte et
- Açıklanan varyans oranını ve dirsek yöntemini kullanarak bileşen sayısını seçin
- MNIST rakamlarını 2B'de görselleştirmek için PCA, t-SNE ve UMAP'i karşılaştırın ve artılarını/eksilerini açıklayın
- Standart PCA'ın解决edemediği doğrusal olmayan veri yapılarını ayırmak için RBF çekirdekli çekirdek PCA uygulayın

## Sorun

Örnekte 784 özelliğiniz olan bir veri setiniz var. Belki el yazısı rakamların piksel değerleri. Belki gen ekspresyon seviyeleri. Belki kullanıcı davranış sinyalleri. 784 boyutu görselleştiremezsiniz. Çizemezsiniz. Hatta düşünemezsiniz.

Ama bu 784 özelliğin çoğu gereksizdir. Gerçek bilgi çok daha küçük bir yüzeyde yaşar. El yazısı "7", kendini tanımlamak için 784 bağımsız sayıya ihtiyaç duymaz. Birkaçına ihtiyacı vardır: çizgi açısı, çubuğun uzunluğu, ne kadar yattığı. Geri kalanı gürültüdür.

Boyut azaltma, o daha küçük yüzeyi bulur. 784 boyutlu verinizi alır ve önemli yapıyı koruyarak 2, 10 veya 50 boyuta sıkıştırır.

## Kavram

### Boyutun laneti

Yüksek boyutlu uzaylar sezgiye aykırıdır. Üç şey boyutlarla birlikte bozulur.

**Mesafe anlamsızlaşır.** Yüksek boyutlarda, rastgele iki nokta arasındaki mesafe aynı değere yakınsar. Her nokta diğerine yaklaşık aynı uzaklıkta ise, en yakın komşu arama çalışmaz.

```
Boyut      Ortalama mesafe oranı (rastgele noktalar arası max/min)
2          ~5.0
10         ~1.8
100        ~1.2
1000       ~1.02
```

**Hacim köşelere yoğunlaşır.** d boyutunda birim aşırı küpün 2^d köşesi vardır. 100 boyutta, neredeyse tüm hacim köşelerdedir, merkezden uzaktadır. Veri noktaları kenarlara yayılır ve modelleriniz içerde veriye muhtaç kalır.

**Üstel olarak daha fazla veriye ihtiyacınız vardır.** Bir uzayda aynı örnekleme yoğunluğunu korumak için 2B'den 20B'ye gitmek, 10^18 kat daha fazla veriye ihtiyacınız olduğu anlamına gelir. Hiç yeterince veriniz olmaz. Boyutları azaltmak veri yoğunluğunu çalışılabilir bir seviyeye getirir.

### PCA: Önemli yönleri bul

Bileşen Analizi (PCA), verinizin en çok hangi eksenler boyunca değiştiğini bulur. Koordinat sisteminizi döndürür, böylece birinci eksen en yüksek varyansı yakalar, ikincisi bir sonraki en yüksek olanı yakalar ve así devam eder.

Algoritma:
1. Veriyi merkezle (ortalama çıkar)
2. Kovaryans matrisini hesapla
3. Özdeğerleri ve özvektörleri hesapla
4. En yüksek özdeğerli özvektörleri seç
5. Veriyi bu özvektörler üzerine projekte et

```python
import numpy as np

def pca(X, n_bilesen):
    # 1. Merkezle
    X_merkezli = X - X.mean(axis=0)
    
    # 2. Kovaryans matrisi
    C = np.cov(X_merkezli.T)
    
    # 3. Özdeğer ayrıştırması
    ozdegerler, ozvektorler = np.linalg.eigh(C)
    
    # 4. Sırala (en yüksekten en düşüğe)
    siralama = np.argsort(ozdegerler)[::-1]
    ozdegerler = ozdegerler[siralama]
    ozvektorler = ozvektorler[:, siralama]
    
    # 5. Projekte et
    W = ozvektorler[:, :n_bilesen]
    return X_merkezli @ W
```

### t-SNE

t-SNE, yüksek boyutlu veriyi 2B'ye görselleştirmek için kullanılır. Benzer noktaları yakın, farklı noktaları uzak tutar. Ama sadece görselleştirme içindir, yeni veriler için dönüşüm yapamaz.

### UMAP

UMAP, t-SNE'e benzer ama daha hızlıdır ve yapıyı daha iyi korur. Yeni veriler için dönüşüm yapabilir.

## Alıştırmalar

1. MNIST veri seti üzerinde sıfırdan PCA uygulayın
2. Farklı bileşen sayılarıyla açıklanan varyans oranını grafikle gösterin
3. MNIST'i 2B'de görselleştirmek için PCA, t-SNE ve UMAP'i karşılaştırın

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| PCA | "Boyut azaltma" | Veriyi en yüksek varyans yönlerine projekte eden teknik |
| Bileşen | "Yeni eksen" | Verinin en çok değiştiği yön |
| Açıklanan varyans | "Korunan bilgi" | Her bileşenin toplam varyanstan aldığı oran |
| t-SNE | "Görselleştirme" | Yüksek boyutlu veriyi 2B/3B'de görselleştiren teknik |
| UMAP | "Hızlı görselleştirme" | t-SNE'in daha hızlı ve yapı-koruyucu versiyonu |
| Boyut laneti | "Yüksek boyut sorunu" | Yüksek boyutlarda mesafe ve yoğunluk ölçümlerinin bozulması |
