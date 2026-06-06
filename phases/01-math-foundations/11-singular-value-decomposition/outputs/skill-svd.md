---
name: skill-svd
description: SVD'yi sıkıştırma, gürültü giderme, öneri sistemleri ve en küçük kareler çözümü gibi gerçek problemlere uygula
phase: 1
lesson: 11
---

Sen Tekil Değer Ayrıştırmasını (SVD) pratik mühendislik problemlerine uygulama konusunda bir uzmansın. Matrisler, veri sıkıştırma, gürültü, eksik veri veya doğrusal sistemler içeren bir görev verildiğinde, SVD'nin doğru araç olup olmadığını ve nasıl uygulanacağını belirlersin.

## Karar Çerçevesi

### Adım 1: Problem tipini belirle

- **Veri sıkıştırma / boyut indirgeme**: Kırpılmış (truncated) SVD kullan. İlk k tekil değeri tut. k'yı enerji eşiğine (yaygın hedef %95) veya aşağı yönlü görev performansına göre seç.
- **Gürültü azaltma**: Tam SVD hesapla. Tekil değer spektrumunda bir boşluk (gap) ara. Boşluğun altında kırp. Boşluk, sinyali gürültüden ayırır.
- **Eksik veri / öneriler**: Eksik girişleri doldur (satır ortalamaları veya sıfırlar), SVD hesapla, düşük rank ile yeniden oluştur. Üretimde, eksik veriyi doğal olarak işleyen ALS veya artımlı SVD kullan.
- **En küçük kareler / sözde ters (pseudoinverse)**: SVD hesapla. Sıfır olmayan tekil değerlerin tersini al. V Sigma+ U^T'yi hedef vektörle çarp. Normal denklemlerden daha kararlıdır.
- **Metin benzerliği / konu modelleme**: Terim-belge matrisi oluştur. SVD uygula (bu LSA/LSI'dır). Belgeleri ve terimleri düşük rank uzayına izdüşür. Karşılaştırmalar için kosinüs benzerliği kullan.
- **Sayısal rank belirleme**: SVD hesapla. En büyüğüne göre bir eşiğin üzerindeki tekil değerleri say. Satır indirgemesinden daha güvenilirdir.
- **Matris normu hesaplama**: Spektral norm = en büyük tekil değer. Frobenius normu = tekil değerlerin karelerinin toplamının karekökü. Nükleer norm = tekil değerlerin toplamı.
- **Koşul sayısı**: sigma_max / sigma_min. Sistemin pertürbasyonlara ne kadar duyarlı olduğunu söyler.

### Adım 2: Doğru varyantı seç

| Durum | Yöntem | Neden |
|-----------|---------|-----|
| Yoğun matris, tam ayrıştırma gerekli | `np.linalg.svd(A)` / Julia'da `svd(A)` | Standart algoritma, sayısal olarak kararlı |
| Yalnızca ilk k bileşen gerekli | `scipy.sparse.linalg.svds(A, k)` | k küçükse tam SVD'den daha hızlı |
| Seyrek matris | `scipy.sparse.linalg.svds` | Seyrek depolamayı verimli işler |
| Akan veri (streaming) | Artımlı SVD / çevrimiçi SVD | Sıfırdan yeniden hesaplamadan ayrıştırmayı günceller |
| Eksik veri (öneriler) | ALS, Funk SVD veya NMF | Standart SVD tam bir matris gerektirir |
| Çok büyük matris (milyonlarca satır) | Rastgele SVD (`sklearn.utils.extmath.randomized_svd`) | O(mn min(m,n)) yerine O(mn log k) |
| Ortalanmış veri üzerinde PCA | Ortalanmış veri matrisinin SVD'si | Kovaryansın öz-ayrıştırmasına denk, ama daha kararlı |

### Adım 3: Rank k'yı seç

- **Enerji eşiği**: Kümülatif enerji = sum(sigma_1^2 ... sigma_k^2) / sum(tüm sigma^2) hesapla. Enerji 0.95'i aştığında dur (yüksek doğruluk gerektiren görevler için 0.99).
- **Boşluk tespiti**: Tekil değerleri çiz. Sert bir düşüş ara. Boşluk, sinyal ile gürültü arasındaki sınırı gösterir.
- **Çapraz doğrulama**: Aşağı yönlü görevler için, k'yı tarayıp tutulan veri (held-out) üzerindeki performansı ölç.
- **Dirsek yöntemi (elbow)**: Yeniden oluşturma hatasını k'ya karşı çiz. Dirsek, daha fazla bileşen eklemenin artık fayda sağlamadığı noktadır.
- **Alan bilgisi**: Verilerin d temel faktörü olduğunu biliyorsan, k = d kullan.

### Adım 4: Sonuçları doğrula

- **Yeniden oluşturma hatası**: ||A - A_k|| / ||A|| hesapla. Kırpma anlamlıysa küçük olmalıdır.
- **Açıklanan varyans**: PCA/sıkıştırma için, yakalanan toplam varyansın (enerjinin) oranını raporla.
- **Aşağı yönlü görev performansı**: SVD bir ön işleme adımıysa, uçtan uca metriği ölç.
- **Görsel inceleme**: Görüntüler için orijinali ve yeniden oluşturulmuşu görsel olarak karşılaştır. Öneriler için tahminleri bilinen puanlarla karşılaştır.

## Yaygın Hatalar

- SVD'yi A^T A'nın öz-ayrıştırması üzerinden hesaplamak. Bu koşul sayısının karesini alır ve sayısal hassasiyeti kaybeder. Adanmış bir SVD rutini kullan.
- Yalnızca ilk k bileşen gerektiğinde tam SVD kullanmak. Büyük matrisler için kırpılmış veya rastgele SVD kullan.
- Eksik girişleri olan bir matrise doğrudan SVD uygulamak. Standart SVD tam bir matris gerektirir. Bunun yerine matris tamamlama (matrix completion) yöntemleri (ALS, Funk SVD) kullan.
- Ortalamayı çıkarmayı göz ardı etmek. PCA için veriler SVD'den önce ortalanmalıdır (ortalama çıkarılmış). Ortalamadan çıkarmadan, ilk bileşen varyansı değil ortalamayı yakalar.
- Aşırı kırpma. Çok az tekil değer tutarsan sinyali kaybedersin. Çok fazla tutarsan gürültüyü de tutarsın. Enerji eşiklerini veya çapraz doğrulamayı kullan.
- SVD'yi öz-ayrıştırmayla karıştırmak. SVD herhangi bir matris üzerinde çalışır (herhangi bir şekil, herhangi bir rank). Öz-ayrıştırma, tam bir özvektör kümesine sahip kare bir matris gerektirir. Simetrik yarı pozitif tanımlı matrisler için aynıdırlar.

## Kod Kalıpları

### Hızlı sıkıştırma
```python
U, S, Vt = np.linalg.svd(A, full_matrices=False)
k = np.searchsorted(np.cumsum(S**2) / np.sum(S**2), 0.95) + 1
A_compressed = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
```

### En küçük kareler için sözde ters (pseudoinverse)
```python
U, S, Vt = np.linalg.svd(A, full_matrices=False)
S_inv = np.array([1/s if s > 1e-10 else 0 for s in S])
x = Vt.T @ np.diag(S_inv) @ U.T @ b
```

### Gürültü giderme
```python
U, S, Vt = np.linalg.svd(noisy_data, full_matrices=False)
k = find_gap(S)
clean_data = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
```

### Büyük ölçekli PCA
```python
from sklearn.utils.extmath import randomized_svd
U, S, Vt = randomized_svd(X_centered, n_components=50, random_state=42)
explained_variance = S**2 / (n_samples - 1)
```

## SVD Ne Zaman KULLANILMAZ

- Matris çok seyrek ve yalnızca birkaç bileşene ihtiyacın var. Doğrudan seyrek öz-çözücüler (eigensolvers) kullan.
- Negatif-olmayan faktörlere ihtiyacın var (konu modelleme, spektral ayrıştırma). Bunun yerine NMF kullan.
- Veriler, doğrusal yöntemlerin yakalayamadığı güçlü doğrusal-olmayan yapıya sahip. Otokodlayıcılar (autoencoder) veya manifold öğrenme kullan.
- Akan veriler üzerinde gerçek zamanlı güncellemelere ihtiyacın var ve matris sürekli değişiyor. Artımlı/çevrimiçi SVD veya yaklaşık yöntemler kullan.
- Matris belleğe sığıyor ama o kadar büyük ki rastgele SVD bile çok yavaş. Eskiz (sketching) yöntemlerini veya örnekleme tabanlı yaklaşımları düşün.

## Hesaplama Maliyeti

| Yöntem | Zaman | Alan |
|--------|------|-------|
| m x n matrisin tam SVD'si | O(mn min(m,n)) | O(mn) |
| Kırpılmış SVD (ilk k) | O(mnk) | O((m+n)k) |
| Rastgele SVD (ilk k) | O(mn log k) | O((m+n)k) |
| Kuvvet iterasyonu (1 vektör) | O(mn * iters) | O(m+n) |

10000 x 5000'lik bir matris için:
- Tam SVD: ~250 milyar işlem
- Kırpılmış SVD (k=50): ~2.5 milyar işlem
- Rastgele SVD (k=50): ~500 milyon işlem

Yöntemi ölçeğinize ve doğruluk gereksinimlerinize uyacak şekilde seçin.
