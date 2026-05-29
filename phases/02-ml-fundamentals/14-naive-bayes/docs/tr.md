# Naive Bayes

> "Naive" (saf) varsayım yanlıştır, ama yine de çalışır. İşte güzelliği de budur.

**Tür:** Build
**Dil:** Python
**Ön Koşullar:** Phase 2, Ders 01-07 (sınıflandırma, Bayes teoremi)
**Süre:** ~75 dakika

## Öğrenim Hedefleri

- Multinomial Naive Bayes'i sıfırdan, Laplace smoothing (düzgünleştirme) ile metin sınıflandırma için uygulamak
- Naive bağımsızlık varsayımının matematiksel olarak neden yanlış olduğunu ama pratikte neden doğru sınıf sıralaması ürettiğini açıklamak
- Multinomial, Bernoulli ve Gaussian Naive Bayes varyantlarını karşılaştırmak ve verilen özellik (feature) tipi için doğru olanı seçmek
- Naive Bayes'i lojistik regresyona karşı yüksek boyutlu seyrek (sparse) veride değerlendirmek ve bias-variance tradeoff'unu açıklamak

## Problem

Metin sınıflandırmanız gerekiyor. E-postaları spam veya spam değil olarak. Müşteri yorumlarını pozitif veya negatif olarak. Destek taleplerini kategorilere ayırmanız. Binlerce özelliğiniz (her kelime için bir tane) ve sınırlı eğitim veriniz var.

Çoğu sınıflandırıcı (classifier) burada boğulur. Lojistik regresyonun binlerce ağırlığı güvenilir şekilde tahmin edebilmesi için yeterli örneğe ihtiyacı vardır. Karar ağaçları (decision trees) her seferinde tek bir kelimeye göre bölünür ve aşırı uyuma (overfitting) eğilimlidir. 10.000 boyutta KNN anlamsızdır çünkü her nokta diğer her noktaya eşit uzaklıktadır.

Naive Bayes bunu halleder. Matematiksel olarak yanlış bir varsayım yapar (her özelliğin, sınıf verildiğinde diğer her özellikten bağımsız olduğunu varsayar) ve yine de özellikle küçük eğitim kümelerinde "daha akıllı" modellerden daha iyi performans gösterir. Veri üzerinde tek bir geçişte (single pass) eğitilir. Milyonlarca özelliğe ölçeklenir. Olasılık tahminleri üretir (bağımsızlık varsayımı nedeniyle genellikle kötü kalibre edilmiş olsa da).

Yanlış bir varsayımın neden iyi tahminlere yol açtığını anlamak, size makine öğrenimi hakkında temel bir şey öğretir: en iyi model en doğru olan değil, veriniz için en iyi bias-variance tradeoff'una sahip olandır.

## Konsept

### Bayes Teoremi (Hızlı Tekrar)

Bayes teoremi koşullu olasılıkları (conditional probabilities) tersine çevirir:

```
P(class | features) = P(features | class) * P(class) / P(features)
```

`P(class | features)` — bir belgenin içindeki kelimelere göre bir sınıfa ait olma olasılığını — hesaplamak istiyoruz. Bunu şuradan hesaplayabiliriz:
- `P(features | class)` — bu kelimeleri bu sınıftaki belgelerde görme olasılığı (likelihood)
- `P(class)` — sınıfın önsel olasılığı (prior probability) (spam genelde ne kadar yaygın?)
- `P(features)` — kanıt (evidence), tüm sınıflar için aynı olduğundan karşılaştırma yaparken göz ardı edilebilir

En yüksek `P(class | features)` değerine sahip sınıf kazanır.

### Naive Bağımsızlık Varsayımı (Naive Independence Assumption)

`P(features | class)` değerini tam olarak hesaplamak, tüm özelliklerin ortak dağılımını (joint distribution) tahmin etmeyi gerektirir. 10.000 kelimelik bir kelime dağarcığı (vocabulary) ile 2^10.000 olası kombinasyon üzerinde bir dağılım tahmin etmeniz gerekir. İmkansız.

Naive varsayım: her özellik, sınıf verildiğinde koşullu olarak bağımsızdır (conditionally independent).

```
P(w1, w2, ..., wn | class) = P(w1 | class) * P(w2 | class) * ... * P(wn | class)
```

İmkansız bir ortak dağılım yerine, n tane basit özellik başına dağılım tahmin edersiniz. Her biri sadece bir sayım (count) gerektirir.

Bu varsayım açıkça yanlıştır. "Machine" ve "learning" kelimeleri hiçbir belgede bağımsız değildir. Ancak sınıflandırıcının doğru olasılık tahminlerine ihtiyacı yoktur. Doğru sıralamalara — hangi sınıfın en yüksek olasılığa sahip olduğuna — ihtiyacı vardır. Bağımsızlık varsayımı sistematik hatalar üretir, ancak bu hatalar tüm sınıfları benzer şekilde etkiler, bu nedenle sıralama doğru kalır.

### Neden Hâlâ Çalışıyor?

Üç neden:

1. **Sıralama, kalibrasyondan önemlidir (Ranking over calibration).** Sınıflandırma sadece en üst sıradaki sınıfın doğru olmasını gerektirir. P(spam) = 0.99999 olsa bile gerçek olasılık 0.7 iken, sınıflandırıcı spam'i doğru seçer. Doğru olasılıklara ihtiyacımız yok. Doğru kazanana ihtiyacımız var.

2. **Yüksek bias, düşük varyans (High bias, low variance).** Bağımsızlık varsayımı güçlü bir önseldir (prior). Modeli ciddi şekilde kısıtlar, bu da aşırı uyumu (overfitting) önler. Sınırlı eğitim verisiyle, hafif yanlış ama kararlı bir model, teorik olarak doğru ama çok kararsız bir modelden daha iyidir. Bu, bias-variance tradeoff'unun iş başındaki halidir.

3. **Özellik tekrarları birbirini götürür.** İlişkili (correlated) özellikler gereksiz kanıt sağlar. Sınıflandırıcı bu kanıtı iki kez sayar, ancak bunu doğru sınıf için de iki kez sayar. "Machine" ve "learning" her zaman birlikte görünüyorsa, her ikisi de "teknoloji" sınıfı için kanıt sağlar. NB bunları iki kez sayar, ama doğru sınıf için iki kez sayar.

Dördüncü, pratik bir neden: Naive Bayes son derece hızlıdır. Eğitim, frekansları saymak için veri üzerinde tek bir geçiştir. Tahmin ise bir matris çarpımıdır. Bir milyon belgeyi saniyeler içinde eğitebilirsiniz. Bu hız, daha yavaş modellere göre daha hızlı iterasyon yapabileceğiniz, daha fazla özellik seti deneyebileceğiniz ve daha çok deney yapabileceğiniz anlamına gelir.

### Adım Adım Matematik

Somut bir örnek üzerinden gidelim. İki sınıfımız olduğunu varsayalım: spam ve spam değil. Kelime dağarcığımızda üç kelime var: "free", "money", "meeting".

Eğitim verisi:
- Spam e-postaları "free"yi 80 kez, "money"yi 60 kez, "meeting"i 10 kez içeriyor (toplam 150 kelime)
- Spam olmayan e-postalar "free"yi 5 kez, "money"yi 10 kez, "meeting"i 100 kez içeriyor (toplam 115 kelime)
- E-postaların %40'ı spam, %60'ı spam değil

Laplace smoothing (alpha=1) ile:

```
P(free | spam)    = (80 + 1) / (150 + 3) = 81/153 = 0.529
P(money | spam)   = (60 + 1) / (150 + 3) = 61/153 = 0.399
P(meeting | spam) = (10 + 1) / (150 + 3) = 11/153 = 0.072

P(free | not-spam)    = (5 + 1) / (115 + 3) = 6/118 = 0.051
P(money | not-spam)   = (10 + 1) / (115 + 3) = 11/118 = 0.093
P(meeting | not-spam) = (100 + 1) / (115 + 3) = 101/118 = 0.856
```

Yeni e-posta şunları içeriyor: "free" (2 kez), "money" (1 kez), "meeting" (0 kez).

```
log P(spam | email) = log(0.4) + 2*log(0.529) + 1*log(0.399) + 0*log(0.072)
                    = -0.916 + 2*(-0.637) + (-0.919) + 0
                    = -3.109

log P(not-spam | email) = log(0.6) + 2*log(0.051) + 1*log(0.093) + 0*log(0.856)
                        = -0.511 + 2*(-2.976) + (-2.375) + 0
                        = -8.838
```

Spam açık ara kazanır. "Free" kelimesinin iki kez geçmesi spam için güçlü bir kanıttır. "Meeting" kelimesinin geçmemesinin her iki log toplamına da katkısı sıfırdır (0 * log(P)) — Multinomial NB'de bulunmayan kelimelerin etkisi yoktur. Kelime yokluğunu açıkça modelleyen Bernoulli NB'dir.

### Üç Varyant

Naive Bayes'in üç çeşidi vardır. Her biri `P(feature | class)` değerini farklı modeller.

#### Multinomial Naive Bayes

Her özelliği bir sayım (count) olarak modeller. Özelliklerin kelime frekansları veya TF-IDF değerleri olduğu metin verisi için en iyisidir.

```
P(word_i | class) = (count of word_i in class + alpha) / (total words in class + alpha * vocab_size)
```

`alpha` parametresi Laplace smoothing'dir (aşağıda açıklanmıştır). Bu varyant, metin sınıflandırma için işgücüdür.

#### Gaussian Naive Bayes

Her özelliği normal dağılım olarak modeller. Sürekli (continuous) özellikler için en iyisidir.

```
P(x_i | class) = (1 / sqrt(2 * pi * var)) * exp(-(x_i - mean)^2 / (2 * var))
```

Her sınıf, özellik başına kendi ortalamasına (mean) ve varyansına (variance) sahiptir. Bu, özellikler her sınıf içinde gerçekten bir çan eğrisi (bell curve) izlediğinde iyi çalışır.

#### Bernoulli Naive Bayes

Her özelliği ikili (binary) olarak modeller: var veya yok. Kısa metin veya ikili özellik vektörleri için en iyisidir.

```
P(word_i | class) = (docs in class containing word_i + alpha) / (total docs in class + 2 * alpha)
```

Multinomial'den farklı olarak Bernoulli, bir kelimenin yokluğunu açıkça cezalandırır. "Free" genelde spam'de geçiyorsa ama bu e-postada geçmiyorsa, Bernoulli bunu spam aleyhine kanıt olarak sayar.

### Her Varyant Ne Zaman Kullanılır

| Varyant | Özellik Tipi | En İyi Olduğu Yer | Örnek |
|---------|--------------|-------------------|-------|
| Multinomial | Sayımlar veya frekanslar | Metin sınıflandırma, bag-of-words | E-posta spam, konu sınıflandırma |
| Gaussian | Sürekli değerler | Normale yakın özelliklere sahip tablo verisi | Iris sınıflandırması, sensör verisi |
| Bernoulli | İkili (0/1) | Kısa metin, ikili özellik vektörleri | SMS spam, var/yok özellikleri |

### Laplace Smoothing

Bir kelime test verisinde geçtiği halde belirli bir sınıfın eğitim verisinde hiç geçmemişse ne olur?

Düzgünleştirme (smoothing) olmadan: `P(word | class) = 0/N = 0`. Bir tane sıfır tüm çarpımı sıfır yaparak `P(class | features) = 0` sonucunu verir, diğer tüm kanıtlar ne olursa olsun. Görülmemiş tek bir kelime, ne kadar başka kanıt olursa olsun tüm tahmini yok eder.

Laplace smoothing, her özellik sayımına küçük bir `alpha` değeri (genelde 1) ekler:

```
P(word_i | class) = (count(word_i, class) + alpha) / (total_words_in_class + alpha * vocab_size)
```

Alpha=1 ile her kelime en azından küçük bir olasılık alır. Test e-postasında "discombobulate" kelimesinin geçmesi artık spam olasılığını öldürmez. Smoothing'in Bayesçi bir yorumu vardır: kelime dağılımları üzerinde düzgün bir Dirichlet prior koymaya eşdeğerdir.

Yüksek alpha daha güçlü smoothing (daha tekdüze dağılımlar) anlamına gelir. Düşük alpha, modelin veriye daha çok güvendiği anlamına gelir. Alpha ayarladığınız bir hiperparametredir (hyperparameter).

Alpha'nın etkisi:

| Alpha | Etki | Ne zaman kullanılır |
|-------|------|---------------------|
| 0.001 | Neredeyse hiç smoothing yok, veriye güven | Çok büyük eğitim seti, görülmemiş özellik beklenmiyor |
| 0.1 | Hafif smoothing | Büyük eğitim seti |
| 1.0 | Standart Laplace smoothing | Varsayılan başlangıç noktası |
| 10.0 | Ağır smoothing, dağılımları düzleştirir | Çok küçük eğitim seti, çok sayıda görülmemiş özellik bekleniyor |

### Log-Uzayında Hesaplama (Log-Space Computation)

Yüzlerce olasılığı (her biri 1'den küçük) çarpmak kayan nokta alt taşmasına (floating-point underflow) neden olur. Gerçek değer çok küçük pozitif bir sayı olsa bile çarpım kayan noktada sıfır olur.

Çözüm: log uzayında çalışmak. Olasılıkları çarpmak yerine logaritmalarını toplarız:

```
log P(class | x1, x2, ..., xn) = log P(class) + sum_i log P(xi | class)
```

Bu, tahmini bir iç çarpıma (dot product) dönüştürür:

```
log_scores = X @ log_feature_probs.T + log_class_priors
prediction = argmax(log_scores)
```

Matris çarpımı. Naive Bayes tahmininin bu kadar hızlı olmasının nedeni budur — tek katmanlı doğrusal bir modelle (single-layer linear model) aynı işlemdir.

### Naive Bayes vs Lojistik Regresyon

İkisi de metin için doğrusal sınıflandırıcılardır (linear classifiers). Fark, neyi modelledikleridir.

| Yön | Naive Bayes | Lojistik Regresyon |
|-----|-------------|-------------------|
| Tip | Generative (P(X\|Y) modeller) | Discriminative (P(Y\|X) modeller) |
| Eğitim | Frekansları sayar | Kayıp fonksiyonunu optimize eder |
| Küçük veri | Daha iyi (güçlü prior yardımcı olur) | Daha kötü (ağırlıkları tahmin etmek için yeterli veri yok) |
| Büyük veri | Daha kötü (yanlış varsayım zarar verir) | Daha iyi (esnek sınır) |
| Özellikler | Bağımsızlık varsayar | Korelasyonları işler |
| Hız | Tek geçiş, çok hızlı | İteratif optimizasyon |
| Kalibrasyon | Zayıf olasılıklar | Daha iyi olasılıklar |

Temel kural: Naive Bayes ile başlayın. Yeterli veriniz varsa ve NB'nin performansı platoya ulaştıysa, lojistik regresyona geçin.

### Sınıflandırma Pipeline'ı

```mermaid
flowchart LR
    A[Raw Text] --> B[Tokenize]
    B --> C[Build Vocabulary]
    C --> D[Count Word Frequencies]
    D --> E[Apply Smoothing]
    E --> F[Compute Log Probabilities]
    F --> G[Predict: argmax P class given words]

    style A fill:#f9f,stroke:#333
    style G fill:#9f9,stroke:#333
```

Pratikte, kayan nokta alt taşmasını önlemek için log uzayında çalışırız. Birçok küçük olasılığı çarpmak yerine logaritmalarını toplarız:

```
log P(class | features) = log P(class) + sum_i log P(feature_i | class)
```

## Build It (Kendin İnşa Et)

`code/naive_bayes.py` dosyasındaki kod, MultinomialNB ve GaussianNB'yi sıfırdan uygular.

### MultinomialNB

Sıfırdan uygulama:

1. **fit(X, y)**: Her sınıf için, her özelliğin frekansını say. Laplace smoothing ekle. Log olasılıklarını hesapla. Sınıf önsel olasılıklarını (class priors) log cinsinden sakla.

2. **predict_log_proba(X)**: Her örnek için, log P(class) + tüm sınıflar için log P(feature_i | class) toplamını hesapla. Bu bir matris çarpımıdır: X @ log_probs.T + log_priors.

3. **predict(X)**: En yüksek log olasılığına sahip sınıfı döndür.

```python
class MultinomialNB:
    def __init__(self, alpha=1.0):
        self.alpha = alpha

    def fit(self, X, y):
        classes = np.unique(y)
        n_classes = len(classes)
        n_features = X.shape[1]

        self.classes_ = classes
        self.class_log_prior_ = np.zeros(n_classes)
        self.feature_log_prob_ = np.zeros((n_classes, n_features))

        for i, c in enumerate(classes):
            X_c = X[y == c]
            self.class_log_prior_[i] = np.log(X_c.shape[0] / X.shape[0])
            counts = X_c.sum(axis=0) + self.alpha
            self.feature_log_prob_[i] = np.log(counts / counts.sum())

        return self
```

#### Açıklama
Bu kod, Multinomial Naive Bayes sınıflandırıcısını sıfırdan uygular. `fit` metodu, her sınıf için özelliklerin log-olasılıklarını ve sınıfların log-önsel olasılıklarını hesaplar. `counts = X_c.sum(axis=0) + self.alpha` satırı, Laplace smoothing ekleyerek her kelimenin sınıf içindeki toplam sayısını bulur. Eğitim tamamlandıktan sonra tahmin yapmak, sadece bir matris çarpımı ve bias eklemesidir — bu nedenle Naive Bayes bu kadar hızlıdır.

### GaussianNB

Sürekli özellikler için, sınıf başına ve özellik başına ortalama (mean) ve varyans (variance) tahmin ederiz:

```python
class GaussianNB:
    def __init__(self):
        pass

    def fit(self, X, y):
        classes = np.unique(y)
        self.classes_ = classes
        self.means_ = np.zeros((len(classes), X.shape[1]))
        self.vars_ = np.zeros((len(classes), X.shape[1]))
        self.priors_ = np.zeros(len(classes))

        for i, c in enumerate(classes):
            X_c = X[y == c]
            self.means_[i] = X_c.mean(axis=0)
            self.vars_[i] = X_c.var(axis=0) + 1e-9
            self.priors_[i] = X_c.shape[0] / X.shape[0]

        return self
```

#### Açıklama
Bu kod, Gaussian Naive Bayes sınıflandırıcısını sıfırdan uygular. `fit` metodu, her sınıf-özellik çifti için ortalama ve varyans hesaplar. `X_c.var(axis=0) + 1e-9` ifadesindeki küçük ekleme (1e-9), sıfır varyanslı özelliklerde bölme hatasını önler. Tahmin aşamasında, her özellik için Gaussian PDF (olasılık yoğunluk fonksiyonu) hesaplanır ve bu değerler log-uzayında toplanır.

### Demo: Metin Sınıflandırma

Kod, iki sınıfı (teknoloji makaleleri vs spor makaleleri) simüle eden sentetik bag-of-words verisi üretir. Her sınıfın farklı bir kelime frekans dağılımı vardır. MultinomialNB, kelime sayımlarını kullanarak bunları sınıflandırır.

Sentetik veri şöyle çalışır: 200 "kelime" (özellik sütunu) oluştururuz. 0-39 arası kelimeler teknoloji makalelerinde yüksek, sporda düşük frekansa sahiptir. 80-119 arası kelimeler sporda yüksek, teknolojide düşük frekansa sahiptir. 40-79 arası kelimeler her ikisinde de orta frekansa sahiptir. Bu, bazı kelimelerin güçlü sınıf göstergesi olduğu, diğerlerinin ise gürültü olduğu gerçekçi bir senaryo oluşturur.

### Demo: Sürekli Özellikler

Kod, Iris benzeri veri (3 sınıf, 4 özellik, Gaussian kümeler) üretir. GaussianNB, sınıf başına ortalama ve varyans kullanarak sınıflandırma yapar. Her sınıfın farklı bir merkezi (ortalama vektörü) ve farklı bir yayılımı (varyansı) vardır, bu da ölçümlerin kategoriler arasında sistematik olarak farklılaştığı gerçek dünya verilerini taklit eder.

Kod ayrıca şunları da gösterir:
- **Smoothing karşılaştırması:** Farklı alpha değerleriyle MultinomialNB eğiterek smoothing gücünün doğruluk (accuracy) üzerindeki etkisini gösterir.
- **Eğitim seti boyutu deneyi:** Eğitim verisi 20'den 1600 örneğe çıktıkça NB doğruluğunun nasıl iyileştiğini gösterir. NB, çok az örnekle bile makul doğruluğa ulaşır — bu onun ana avantajıdır.
- **Karmaşıklık matrisi (Confusion matrix):** Sınıf başına precision, recall ve F1 skoru ile NB'nin nerelerde hata yaptığını gösterir.

### Tahmin Hızı

Naive Bayes tahmini bir matris çarpımıdır. d özellikli n örnek ve k sınıf için:
- MultinomialNB: tek matris çarpımı (n x d) @ (d x k) = O(n * d * k)
- GaussianNB: n * k Gaussian PDF değerlendirmesi, her biri d özellik üzerinde = O(n * d * k)

Her ikisi de her boyutta doğrusaldır (linear). Bunu KNN (tüm eğitim noktalarına mesafe hesaplaması gerektirir) veya RBF çekirdekli SVM (tüm destek vektörlerine karşı çekirdek değerlendirmesi gerektirir) ile karşılaştırın. NB, tahmin zamanında katbekat daha hızlıdır.

## Use It (Kullan)

sklearn ile her iki varyant da tek satırdır:

```python
from sklearn.naive_bayes import GaussianNB, MultinomialNB

gnb = GaussianNB()
gnb.fit(X_train, y_train)
print(f"GaussianNB accuracy: {gnb.score(X_test, y_test):.3f}")

mnb = MultinomialNB(alpha=1.0)
mnb.fit(X_train_counts, y_train)
print(f"MultinomialNB accuracy: {mnb.score(X_test_counts, y_test):.3f}")
```

#### Açıklama
scikit-learn kütüphanesi, Naive Bayes'in her iki varyantını da hazır sunar. `GaussianNB` sürekli değerli özellikler için, `MultinomialNB` ise sayım/frekans tipi özellikler için kullanılır. `alpha=1.0` parametresi Laplace smoothing'i etkinleştirir. Kod, sıfırdan yazılan uygulamaları sklearn ile aynı veri üzerinde karşılaştırarak doğruluğu teyit eder.

Metin sınıflandırma için sklearn ile:

```python
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

text_clf = Pipeline([
    ("vectorizer", CountVectorizer()),
    ("classifier", MultinomialNB(alpha=1.0)),
])

text_clf.fit(train_texts, train_labels)
accuracy = text_clf.score(test_texts, test_labels)
```

#### Açıklama
`Pipeline`, metin vektörizasyonu ve sınıflandırmayı tek bir nesnede birleştirir. `CountVectorizer` ham metni kelime sayım matrisine dönüştürür. `MultinomialNB` bu sayımlarla sınıflandırma yapar. Pipeline, hem eğitim hem de tahmin aşamalarında tüm adımları sırayla uygulayarak kullanımı kolaylaştırır.

### TF-IDF ile Naive Bayes

Ham kelime sayımları, her kelimeye geçtiği kadar eşit ağırlık verir. Ancak "the" ve "is" gibi yaygın kelimeler her sınıfta sıkça geçer — bilgi taşımazlar. TF-IDF (Term Frequency - Inverse Document Frequency), yaygın kelimelerin ağırlığını azaltır ve nadir, ayırt edici kelimelerin ağırlığını artırır.

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

text_clf = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("classifier", MultinomialNB(alpha=0.1)),
])
```

#### Açıklama
`TfidfVectorizer`, kelime sayımlarını TF-IDF ağırlıklarına dönüştürür. TF-IDF değerleri negatif olmadığı için MultinomialNB ile çalışır. TF-IDF + MultinomialNB kombinasyonu, metin sınıflandırma için en güçlü temel yaklaşımlardan biridir ve 10.000'den az eğitim örneği olan veri kümelerinde sıklıkla daha karmaşık modelleri geride bırakır.

### Kısa Metin için BernoulliNB

Kısa metinler (tweetler, SMS, sohbet mesajları) için BernoulliNB, MultinomialNB'den daha iyi performans gösterebilir. Kısa metinlerde kelime sayımları düşük olduğu için MultinomialNB'nin güvendiği frekans bilgisi gürültülüdür. BernoulliNB sadece var/yok ile ilgilenir, bu kısa metinlerde daha güvenilirdir.

```python
from sklearn.naive_bayes import BernoulliNB
from sklearn.feature_extraction.text import CountVectorizer

text_clf = Pipeline([
    ("vectorizer", CountVectorizer(binary=True)),
    ("classifier", BernoulliNB(alpha=1.0)),
])
```

#### Açıklama
`CountVectorizer(binary=True)` parametresi tüm sayımları 0/1'e dönüştürür. Bu olmadan BernoulliNB yine çalışır, ancak tasarlanmadığı sayım değerlerini görür. BernoulliNB, kelimenin kaç kez geçtiğinden ziyade var olup olmadığına odaklandığı için kısa metinlerde daha iyi sonuç verir.

### NB Olasılıklarını Kalibre Etme

NB olasılıkları kötü kalibre edilmiştir. NB, P(spam) = 0.95 dediğinde gerçek olasılık 0.7 olabilir. Güvenilir olasılık tahminlerine ihtiyacınız varsa (örneğin bir eşik belirlemek veya diğer modellerle birleştirmek için), sklearn'in `CalibratedClassifierCV` sınıfını kullanın:

```python
from sklearn.calibration import CalibratedClassifierCV

calibrated_nb = CalibratedClassifierCV(MultinomialNB(), cv=5, method="sigmoid")
calibrated_nb.fit(X_train, y_train)
proba = calibrated_nb.predict_proba(X_test)
```

#### Açıklama
Bu kod, NB'nin ham skorlarının üzerine çapraz doğrulama (cross-validation) ile bir lojistik regresyon yerleştirir. `method="sigmoid"` parametresi Platt scaling olarak bilinir ve NB'nin çıktılarını gerçek olasılık dağılımına daha yakın hale getirir. Elde edilen olasılıklar gerçek sınıf frekanslarına çok daha yakındır.

### Yaygın Tuzaklar

1. **Negatif özellik değerleri.** MultinomialNB negatif olmayan özellikler gerektirir. Negatif değerleriniz varsa (belirli ayarlarla TF-IDF veya standartlaştırılmış özellikler gibi), bunun yerine GaussianNB kullanın veya özellikleri pozitif yapmak için kaydırın.

2. **Sıfır varyanslı özellikler.** GaussianNB varyansa böler. Bir özelliğin bir sınıf için varyansı sıfırsa (tüm değerler aynıysa), olasılık hesaplaması bozulur. Kod, tüm varyanslara küçük bir smoothing terimi (1e-9) ekleyerek bunu önler.

3. **Sınıf dengesizliği (Class imbalance).** E-postaların %99'u spam değilse, P(not-spam) = 0.99 önsel olasılığı o kadar güçlüdür ki likelihood kanıtını bastırır. Sınıf önsel olasılıklarını manuel olarak ayarlayabilir veya sklearn'de `class_prior` parametresini kullanabilirsiniz.

4. **Özellik ölçekleme (Feature scaling).** MultinomialNB ölçekleme gerektirmez (sayımlarla çalışır). GaussianNB de ölçekleme gerektirmez (özellik başına istatistikleri kendisi tahmin eder). Bu, özellik ölçeklerine duyarlı olan lojistik regresyon ve SVM'e göre bir avantajdır.

## Ship It (Teslim Et)

Bu ders şunları üretir:
- `outputs/skill-naive-bayes-chooser.md` — doğru NB varyantını seçmek için bir karar becerisi
- `code/naive_bayes.py` — sıfırdan MultinomialNB ve GaussianNB, sklearn karşılaştırması ile

### Naive Bayes Ne Zaman Başarısız Olur?

NB, bağımsızlık varsayımı yanlış sıralamalara (sadece yanlış olasılıklara değil) neden olduğunda başarısız olur. Bu şu durumlarda gerçekleşir:

1. **Güçlü özellik etkileşimleri.** Sınıf, iki özelliğin birleşimine bağlıysa ama tek başlarına hiçbirine bağlı değilse (XOR benzeri desenler), NB bunu tamamen kaçırır. Her özellik tek başına hiçbir kanıt sağlamaz ve NB bunları doğrusal olmayan şekilde birleştiremez.

2. **Zıt kanıtlı yüksek korelasyonlu özellikler.** Özellik A "spam" derken özellik B "spam değil" diyorsa, ama A ve B mükemmel korelasyonluysa (gerçekte her zaman aynı fikirdeler), NB hiç olmayan bir çelişkili kanıt görür.

3. **Çok büyük eğitim setleri.** Yeterli veriyle, lojistik regresyon gibi discriminative modeller gerçek karar sınırını öğrenir ve NB'yi geride bırakır. Küçük veride yardımcı olan bağımsızlık varsayımı artık modeli geri tutar.

Pratikte, bu başarısızlık modları metin sınıflandırma için nadirdir. Metin özellikleri çok sayıdadır, tek başlarına zayıftır ve bağımsızlık varsayımının hataları birbirini götürme eğilimindedir. Az sayıda güçlü korelasyonlu özelliği olan tablo verisi için önce lojistik regresyon veya ağaç tabanlı modelleri düşünün.

## Alıştırmalar

1. **Smoothing deneyi.** MultinomialNB'yi metin verisinde alpha değerleri 0.01, 0.1, 1.0, 10.0 ve 100.0 ile eğitin. Doğruluk vs alpha grafiğini çizin. Performans nerede zirve yapıyor? Çok yüksek alpha neden zarar verir?

2. **Özellik bağımsızlığı testi.** Gerçek bir metin veri kümesi alın. Açıkça ilişkili iki kelime seçin ("machine" ve "learning" gibi). P(word1 | class) * P(word2 | class) değerini hesaplayın ve P(word1 AND word2 | class) ile karşılaştırın. Bağımsızlık varsayımı ne kadar yanlış? Sınıflandırma doğruluğunu etkiliyor mu?

3. **Bernoulli uygulaması.** Koda bir BernoulliNB sınıfı ekleyin. Bag-of-words'ü ikili (var/yok) hale dönüştürün ve metin verisinde MultinomialNB ile doğruluğu karşılaştırın. Bernoulli ne zaman kazanır?

4. **NB vs Lojistik Regresyon.** İkisini de metin verisinde eğitin. 100 eğitim örneği ile başlayın ve 10.000'e çıkarın. Her ikisi için doğruluk vs eğitim seti büyüklüğü grafiğini çizin. Lojistik Regresyon Naive Bayes'i hangi noktada geçiyor?

5. **Spam filtresi.** Tam bir spam sınıflandırıcı oluşturun: ham e-posta metnini tokenize edin, kelime dağarcığı oluşturun, bag-of-words özellikleri çıkarın, MultinomialNB eğitin, precision ve recall ile değerlendirin (sadece doğruluk değil — neden?).

## Anahtar Terimler

| Terim | İnsanların dediği | Gerçek anlamı |
|-------|------------------|---------------|
| Naive Bayes | "Basit olasılıksal sınıflandırıcı" | Bayes teoremini, özelliklerin sınıf verildiğinde koşullu olarak bağımsız olduğu varsayımıyla uygulayan bir sınıflandırıcı |
| Koşullu bağımsızlık (Conditional independence) | "Özellikler birbirini etkilemez" | P(A, B \| C) = P(A \| C) * P(B \| C) — C'yi bildikten sonra B'yi bilmek, A hakkında size yeni bir şey söylemez |
| Laplace smoothing | "Bir-ekle smoothing" (Add-one smoothing) | Sıfır olasılıkların tahmini domine etmesini önlemek için her özellik sayımına küçük bir sayı eklemek |
| Prior (Önsel) | "Veriyi görmeden önce inandığın şey" | P(class) — herhangi bir özellik gözlemlemeden önce her sınıfın olasılığı |
| Likelihood | "Veri ne kadar uyuyor" | P(features \| class) — sınıf biliniyorsa bu özellikleri gözlemleme olasılığı |
| Posterior (Sonsal) | "Veriyi gördükten sonra inandığın şey" | P(class \| features) — özellikleri gözlemledikten sonra sınıfın güncellenmiş olasılığı |
| Generative model | "Verinin nasıl üretildiğini modeller" | P(X \| Y) ve P(Y)'yi öğrenen, ardından Bayes teoremini kullanarak P(Y \| X)'i elde eden model |
| Discriminative model | "Karar sınırını modeller" | X'in nasıl üretildiğini modellemeden doğrudan P(Y \| X)'i öğrenen model |
| Log olasılık (Log probability) | "Alt taşmayı önle" | Birçok küçük sayının çarpımının kayan noktada sıfır olmasını önlemek için log P yerine P ile çalışmak |

## Daha Fazla Okuma

- [scikit-learn Naive Bayes dokümantasyonu](https://scikit-learn.org/stable/modules/naive_bayes.html) — üç varyantın tümü matematiksel detaylarıyla
- [McCallum and Nigam, A Comparison of Event Models for Naive Bayes Text Classification (1998)](https://www.cs.cmu.edu/~knigam/papers/multinomial-aaaiws98.pdf) — metin için Multinomial ve Bernoulli'nin klasik karşılaştırması
- [Rennie et al., Tackling the Poor Assumptions of Naive Bayes Text Classifiers (2003)](https://people.csail.mit.edu/jrennie/papers/icml03-nb.pdf) — NB'nin metin için iyileştirmeleri
- [Ng and Jordan, On Discriminative vs. Generative Classifiers (2001)](https://ai.stanford.edu/~ang/papers/nips01-discriminativegenerative.pdf) — NB'nin LR'den daha az veriyle daha hızlı yakınsadığını kanıtlar
