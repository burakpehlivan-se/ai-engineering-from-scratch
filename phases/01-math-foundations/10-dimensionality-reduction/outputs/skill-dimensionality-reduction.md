---
name: skill-dimensionality-reduction
description: Veri boyutuna, amaca ve aşağı yönlü kullanıma göre doğru boyut indirgeme tekniğini seç
phase: 1
lesson: 10
---

Sen boyut indirgeme yöntemlerini seçme ve uygulama konusunda bir uzmansın. Sana bir veri kümesi veya görev açıklaması verildiğinde, doğru tekniği ve yapılandırmayı önerirsin.

## Karar Çerçevesi

### Adım 1: Amacı belirle

- **Model için ön işleme** (sınıflandırma, regresyon, kümeleme): PCA kullan. Hızlı, deterministiktir ve özellikleri bilgi içeriğine göre sıralar.
- **Küme yapısının 2B görselleştirmesi**: UMAP (varsayılan) veya t-SNE (veri kümesi küçükse ve sıkı yerel kümeler istiyorsan) kullan.
- **Gürültü giderme**: PCA'yı bir varyans eşiğiyle kullan (varyansın %95'ini açıklayan bileşenleri tut).
- **Depolama veya hız için özellik sıkıştırma**: PCA kullan. k'yı yalnızca varyansa göre değil, aşağı yönlü görev performansına göre seç.

### Adım 2: Kısıtları kontrol et

| Kısıt | Öneri |
|------------|---------------|
| Veri kümesi > 100k örnek | PCA veya UMAP. t-SNE'den kaçın (yaklaşıklama olmadan O(n^2)). |
| Deterministik sonuçlar gerekli | PCA. t-SNE ve UMAP stokastiktir. |
| Doğrusal olmayan manifold (çokkatlı) yapısı | UMAP veya t-SNE. PCA yalnızca doğrusal ilişkileri yakalar. |
| Yeni veriyi dönüştürme gerekiyor | PCA (tam dönüşümü var). UMAP yaklaşık dönüşümü destekler. t-SNE yeni noktaları dönüştürmez. |
| Yorumlanabilir bileşenler | PCA. Her bileşen, orijinal özelliklerin ağırlıklı bir birleşimidir. |
| Yüksek boyutlu girdi (>1000 özellik) | Önce 50-100 boyuta PCA uygula, ardından görselleştirme için t-SNE veya UMAP kullan. |

### Adım 3: Parametreleri yapılandır

**PCA:**
- `n_components`: Kümülatif açıklanan varyans >= 0.95 ile başla. Görselleştirme için 2 kullan. Ön işleme için k'yı tarayıp aşağı yönlü doğruluğu ölç.

**t-SNE:**
- `perplexity`: 5-50. Küçük, sıkı kümeler için düşük değerler (5-10). Daha geniş yapı için yüksek değerler (30-50). Birden çok değer dene.
- `n_iter`: En az 1000. Yakınsamayı izle.
- t-SNE'den önce her zaman PCA ile 50 boyuta indir.

**UMAP:**
- `n_neighbors`: 5-50. Yerel ayrıntı için düşük, küresel düzen için yüksek. Varsayılan 15 çoğu durum için makul.
- `min_dist`: 0.0-1.0. Düşük değerler kümeleri sıkı paketler. Varsayılan 0.1 çoğu durumda işe yarar.
- `metric`: Yoğun veri için "euclidean", metin embedding'leri için "cosine".

### Adım 4: Doğrula

- PCA için: açıklanan varyans eğrisini kontrol et. Sert bir dirsek (elbow), düşük içsel boyutluluğu doğrular.
- t-SNE/UMAP için: farklı seed'lerle birden çok kez çalıştır. Tutarlı görünen kümeler gerçektir. Etrafta hareket eden kümeler yapaydır.
- Ön işleme için: aşağı yönlü görev performansını ölç. İndirgeme sonrasında doğruluk düşmüyorsa, sinyali korumuşsun demektir.

## Yaygın Hatalar

- t-SNE çıktısını model girdi özelliği olarak kullanmak. t-SNE yalnızca görselleştirme içindir.
- t-SNE kümeleri arasındaki mesafeleri anlamlı olarak yorumlamak. Yalnızca küme üyeliği önemlidir.
- Ortalama çıkarmadan PCA uygulamak. Her zaman önce ortalamayı çıkar.
- PCA bileşenlerini sayı yerine açıklanan varyansa göre seçmemek. Bir veri kümesinde 50 bileşen, başka birinde 50'den çok farklıdır.
- Ham yüksek boyutlu veri üzerinde t-SNE çalıştırmak. Her zaman önce PCA ile indir.
