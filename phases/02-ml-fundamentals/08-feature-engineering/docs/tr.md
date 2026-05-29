> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/02-ml-fundamentals/08-feature-engineering/docs/en.md)

# Özellik Mühendisliği ve Seçimi

> İyi bir özellik, bin veri noktasına bedeldir.

**Tür:** Uygulama
**Diller:** Python
**Ön Koşullar:** Faz 1 (ML için İstatistik, Lineer Cebir), Faz 2 Ders 1-7
**Süre:** ~90 dakika

## Öğrenme Hedefleri

- Sayısal dönüşümleri (standardizasyon, min-max ölçekleme, log dönüşümü, aralıklama (binning)) uygulayın ve her birinin ne zaman uygun olduğunu açıklayın
- Kategorik özellikler için one-hot, label ve target encoding (hedef kodlaması) yapın ve target encoding'deki veri sızıntısı (data leakage) riskini belirleyin
- Sıfırdan bir TF-IDF vektörleştiricisi oluşturun ve metin sınıflandırmada neden ham kelime sayılarından daha iyi performans gösterdiğini açıklayın
- Filtre tabanlı özellik seçimi (varyans eşiği, korelasyon, karşılıklı bilgi (mutual information)) uygulayarak boyutluluğu azaltın

## Sorun

Bir veri kümeniz var. Bir algoritma seçiyorsunuz. Eğitiyorsunuz. Sonuçlar vasat. Daha süslü bir algoritma deniyorsunuz. Hâlâ vasat. Bir hafta hiperparametre ayarlıyorsunuz. Marjinal iyileşme.

Sonra biri ham veriyi daha iyi özelliklere dönüştürüyor ve basit bir lojistik regresyon, sizin ayarlanmış gradient-boosted ensemble'ınızı geçiyor.

Bu sürekli olur. Klasik ML'de verinin temsili, algoritma seçiminden daha önemlidir. "Metrekare" ve "yatak odası sayısı" olan bir ev fiyat modeli, "ham metin olarak adres" kullanan bir modeli — öğrenici ne kadar sofistike olursa olsun — yenecektir. Algoritma, yalnızca ona verdiğinizle çalışabilir.

Özellik mühendisliği (feature engineering), ham veriyi modellerin örüntüleri bulmasını kolaylaştıracak temsillere dönüştürme sürecidir. Özellik seçimi (feature selection), sinyal eklemeyen ama gürültü katan özellikleri atma sürecidir. Birlikte, klasik ML'deki en yüksek kaldıraçlı faaliyettir.

## Kavram

### Özellik Pipeline'ı

```mermaid
flowchart LR
    A[Ham Veri] --> B[Eksik Değerleri İşle]
    B --> C[Sayısal Dönüşümler]
    B --> D[Kategorik Kodlama]
    B --> E[Metin Özellikleri]
    C --> F[Özellik Etkileşimleri]
    D --> F
    E --> F
    F --> G[Özellik Seçimi]
    G --> H[Model-Hazır Veri]
```

### Sayısal Özellikler

Ham sayılar nadiren modele hazırdır. Yaygın dönüşümler:

**Ölçekleme (Scaling):** Özellikleri aynı aralığa koyar, böylece mesafe tabanlı algoritmalar (K-Means, KNN, SVM) tüm özellikleri eşit işlemle muamele eder. Min-max ölçekleme [0, 1] aralığına haritalar. Standardizasyon (z-score) ortalama=0, std=1'e haritalar.

**Log dönüşümü:** Sağa çarpık dağılımları (gelir, nüfus, kelime sayıları) sıkıştırır. Çarpımsal ilişkileri toplamsal hale getirir.

**Aralıklama (Binning):** Sürekli değerleri kategorilere dönüştürür. Özellik ile hedef arasındaki ilişkinin doğrusal olmayıp adımsal olduğu durumlarda kullanışlıdır (örn. yaş grupları).

**Polinom özellikleri:** x^2, x^3, x1*x2 terimleri oluşturur. Doğrusal modellerin, daha fazla özellik pahasına, doğrusal olmayan ilişkileri yakalamasını sağlar.

### Kategorik Özellikler

Modellerin sayılara ihtiyacı vardır. Kategorilerin kodlanması gerekir.

**One-hot encoding:** Her kategori için bir ikili sütun oluşturur. "renk = kırmızı/mavi/yeşil" üç sütuna dönüşür: is_red, is_blue, is_green. Düşük kardinaliteli özellikler için iyi çalışır ancak çok sayıda kategoriyle patlar.

**Label encoding:** Her kategoriyi bir tam sayıya haritalar: kırmızı=0, mavi=1, yeşil=2. Yanlış sıralama ekler (model yeşil > mavi > kırmızı sanabilir). Yalnızca tek tek değerlerde bölünen ağaç tabanlı modeller için uygundur.

**Target encoding:** Her kategoriyi, o kategorideki hedef değişkenin ortalamasıyla değiştirir. Güçlüdür ancak tehlikelidir: yüksek veri sızıntısı (data leakage) riski. Yalnızca eğitim verisinde hesaplanmalı ve test verisine uygulanmalıdır.

### Metin Özellikleri

**Count vectorizer:** Her kelimenin bir belgede kaç kez geçtiğini sayar. "the cat sat on the mat" → {the: 2, cat: 1, sat: 1, on: 1, mat: 1}.

**TF-IDF:** Term Frequency-Inverse Document Frequency. Kelimeleri, belgeler arasında ne kadar benzersiz olduklarına göre ağırlıklandırır. "the" gibi yaygın kelimeler düşük ağırlık alır. Nadir, ayırt edici kelimeler yüksek ağırlık alır.

```
TF(kelime, belge) = kelimenin belgedeki sayısı / belgedeki toplam kelime
IDF(kelime) = log(toplam belge / kelimeyi içeren belge sayısı)
TF-IDF = TF * IDF
```

### Eksik Değerler

Gerçek veride delikler vardır. Stratejiler:

- **Satırları sil:** Yalnızca eksik veri seyrek ve rastgele olduğunda
- **Ortanca/ortalama ataması (imputation):** Basit, dağılım şeklini korur (ortanca, aykırı değerlere karşı daha sağlamdır)
- **Mod ataması:** Kategorik özellikler için
- **Gösterge sütunu:** Atamadan önce "bu_eksik_mi" adlı ikili bir sütun ekleyin. Verinin eksik olması başlı başına bilgilendirici olabilir
- **İleri/geri doldurma:** Zaman serisi verileri için

### Özellik Etkileşimi

Bazen ilişki kombinasyondadır. "Boy" ve "kilo" tek başlarına "VKİ = kilo / boy^2"den daha az tahmin edicidir. Özellik etkileşimleri özellik uzayını çarpar, bu yüzden doğru olanları seçmek için alan bilgisi (domain knowledge) kullanın.

### Özellik Seçimi

Daha fazla özellik her zaman daha iyi değildir. İlgisiz özellikler gürültü ekler, eğitim süresini artırır ve aşırı öğrenmeye (overfitting) neden olabilir.

**Filtre yöntemleri (model öncesi):**
- Korelasyon: birbiriyle yüksek korelasyonlu özellikleri kaldır (gereksiz)
- Karşılıklı bilgi (mutual information): bir özelliği bilmenin hedef hakkındaki belirsizliği ne kadar azalttığını ölçer
- Varyans eşiği: neredeyse hiç değişmeyen özellikleri kaldır

**Sarmalayıcı yöntemler (model bazlı):**
- L1 düzenlileştirme (Lasso): ilgisiz özellik ağırlıklarını tam olarak sıfıra iter
- Özyinelemeli özellik elemesi (RFE): eğit, en az önemli özelliği kaldır, tekrarla

**Seçim neden önemlidir:** 10 iyi özelliği olan bir model, genellikle 10 iyi özellik ve 90 gürültülü özelliği olan bir modelden daha iyi performans gösterir. Gürültülü özellikler, modele genellemeyen eğitim verisi örüntülerinde aşırı öğrenme fırsatı verir.

## Uygulama

### Adım 1: Sıfırdan sayısal dönüşümler

```python
import math


def min_max_scale(values):
    min_val = min(values)
    max_val = max(values)
    if max_val == min_val:
        return [0.0] * len(values)
    return [(v - min_val) / (max_val - min_val) for v in values]


def standardize(values):
    n = len(values)
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / n
    std = math.sqrt(variance) if variance > 0 else 1.0
    return [(v - mean) / std for v in values]


def log_transform(values):
    return [math.log(v + 1) for v in values]


def bin_values(values, n_bins=5):
    min_val = min(values)
    max_val = max(values)
    bin_width = (max_val - min_val) / n_bins
    if bin_width == 0:
        return [0] * len(values)
    result = []
    for v in values:
        bin_idx = int((v - min_val) / bin_width)
        bin_idx = min(bin_idx, n_bins - 1)
        result.append(bin_idx)
    return result


def polynomial_features(row, degree=2):
    n = len(row)
    result = list(row)
    if degree >= 2:
        for i in range(n):
            result.append(row[i] ** 2)
        for i in range(n):
            for j in range(i + 1, n):
                result.append(row[i] * row[j])
    return result
```

#### Açıklama
`min_max_scale` değerleri [0,1] aralığına sıkıştırır — tüm değerler aynıysa sıfır döndürür. `standardize` ortalamayı çıkarıp standart sapmaya bölerek z-skoru hesaplar. `log_transform` her değere log(v+1) uygulayarak sağa çarpık dağılımları normalize eder. `bin_values` sürekli değerleri eşit genişlikte `n_bins` sayıda aralığa böler. `polynomial_features` girdi vektörüne kareler ve çapraz çarpımlar ekler.

### Adım 2: Sıfırdan kategorik kodlama

```python
def one_hot_encode(values):
    categories = sorted(set(values))
    cat_to_idx = {cat: i for i, cat in enumerate(categories)}
    n_cats = len(categories)

    encoded = []
    for v in values:
        row = [0] * n_cats
        row[cat_to_idx[v]] = 1
        encoded.append(row)

    return encoded, categories


def label_encode(values):
    categories = sorted(set(values))
    cat_to_int = {cat: i for i, cat in enumerate(categories)}
    return [cat_to_int[v] for v in values], cat_to_int


def target_encode(feature_values, target_values, smoothing=10):
    global_mean = sum(target_values) / len(target_values)

    category_stats = {}
    for feat, target in zip(feature_values, target_values):
        if feat not in category_stats:
            category_stats[feat] = {"sum": 0.0, "count": 0}
        category_stats[feat]["sum"] += target
        category_stats[feat]["count"] += 1

    encoding = {}
    for cat, stats in category_stats.items():
        cat_mean = stats["sum"] / stats["count"]
        weight = stats["count"] / (stats["count"] + smoothing)
        encoding[cat] = weight * cat_mean + (1 - weight) * global_mean

    return [encoding[v] for v in feature_values], encoding
```

#### Açıklama
`one_hot_encode` her kategori için bir ikili sütun oluşturur. `label_encode` kategorileri sıralı tam sayılara dönüştürür (dikkat: yanlış sıralama ekler). `target_encode` her kategoriyi, global ortalamaya doğru smoothing (yumuşatma) uygulanmış hedef ortalamasıyla değiştirir — `smoothing` parametresi küçük kategorilerde aşırı öğrenmeyi önler.

### Adım 3: Sıfırdan metin özellikleri

```python
def count_vectorize(documents):
    vocab = {}
    idx = 0
    for doc in documents:
        for word in doc.lower().split():
            if word not in vocab:
                vocab[word] = idx
                idx += 1

    vectors = []
    for doc in documents:
        vec = [0] * len(vocab)
        for word in doc.lower().split():
            vec[vocab[word]] += 1
        vectors.append(vec)

    return vectors, vocab


def tfidf(documents):
    n_docs = len(documents)

    vocab = {}
    idx = 0
    for doc in documents:
        for word in doc.lower().split():
            if word not in vocab:
                vocab[word] = idx
                idx += 1

    doc_freq = {}
    for doc in documents:
        seen = set()
        for word in doc.lower().split():
            if word not in seen:
                doc_freq[word] = doc_freq.get(word, 0) + 1
                seen.add(word)

    vectors = []
    for doc in documents:
        words = doc.lower().split()
        word_count = len(words)
        tf_map = {}
        for word in words:
            tf_map[word] = tf_map.get(word, 0) + 1

        vec = [0.0] * len(vocab)
        for word, count in tf_map.items():
            tf = count / word_count
            idf = math.log(n_docs / doc_freq[word])
            vec[vocab[word]] = tf * idf
        vectors.append(vec)

    return vectors, vocab
```

#### Açıklama
`count_vectorize` her belge için bir kelime sıklık vektörü oluşturur. `tfidf` buna ek olarak Inverse Document Frequency hesaplar — bir kelime ne kadar az belgede geçiyorsa ağırlığı o kadar yüksek olur. Bu sayede "the", "and" gibi yaygın kelimelerin etkisi azaltılır.

### Adım 4: Sıfırdan eksik değer ataması

```python
def impute_mean(values):
    present = [v for v in values if v is not None]
    if not present:
        return [0.0] * len(values), 0.0
    mean = sum(present) / len(present)
    return [v if v is not None else mean for v in values], mean


def impute_median(values):
    present = sorted(v for v in values if v is not None)
    if not present:
        return [0.0] * len(values), 0.0
    n = len(present)
    if n % 2 == 0:
        median = (present[n // 2 - 1] + present[n // 2]) / 2
    else:
        median = present[n // 2]
    return [v if v is not None else median for v in values], median


def impute_mode(values):
    present = [v for v in values if v is not None]
    if not present:
        return values, None
    counts = {}
    for v in present:
        counts[v] = counts.get(v, 0) + 1
    mode = max(counts, key=counts.get)
    return [v if v is not None else mode for v in values], mode


def add_missing_indicator(values):
    return [0 if v is not None else 1 for v in values]
```

#### Açıklama
`impute_mean`, `impute_median`, `impute_mode` sırasıyla ortalama, ortanca ve mod kullanarak eksik değerleri doldurur. Ortanca aykırı değerlere karşı daha sağlamdır. `add_missing_indicator` hangi değerlerin eksik olduğunu işaretleyen ikili bir sütun ekler — verinin eksik olması başlı başına bilgi taşıyabilir.

### Adım 5: Sıfırdan özellik seçimi

```python
def correlation(x, y):
    n = len(x)
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y)) / n
    std_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x) / n)
    std_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y) / n)
    if std_x == 0 or std_y == 0:
        return 0.0
    return cov / (std_x * std_y)


def mutual_information(feature, target, n_bins=10):
    feat_min = min(feature)
    feat_max = max(feature)
    bin_width = (feat_max - feat_min) / n_bins if feat_max != feat_min else 1.0
    feat_binned = [
        min(int((f - feat_min) / bin_width), n_bins - 1) for f in feature
    ]

    n = len(feature)
    target_classes = sorted(set(target))

    feat_bins = sorted(set(feat_binned))
    p_feat = {}
    for b in feat_bins:
        p_feat[b] = feat_binned.count(b) / n

    p_target = {}
    for t in target_classes:
        p_target[t] = target.count(t) / n

    mi = 0.0
    for b in feat_bins:
        for t in target_classes:
            joint_count = sum(
                1 for fb, tv in zip(feat_binned, target) if fb == b and tv == t
            )
            p_joint = joint_count / n
            if p_joint > 0:
                mi += p_joint * math.log(p_joint / (p_feat[b] * p_target[t]))

    return mi


def variance_threshold(features, threshold=0.01):
    n_features = len(features[0])
    n_samples = len(features)
    selected = []

    for j in range(n_features):
        col = [features[i][j] for i in range(n_samples)]
        mean = sum(col) / n_samples
        var = sum((v - mean) ** 2 for v in col) / n_samples
        if var >= threshold:
            selected.append(j)

    return selected


def remove_correlated(features, threshold=0.9):
    n_features = len(features[0])
    n_samples = len(features)

    to_remove = set()
    for i in range(n_features):
        if i in to_remove:
            continue
        col_i = [features[r][i] for r in range(n_samples)]
        for j in range(i + 1, n_features):
            if j in to_remove:
                continue
            col_j = [features[r][j] for r in range(n_samples)]
            corr = abs(correlation(col_i, col_j))
            if corr >= threshold:
                to_remove.add(j)

    return [i for i in range(n_features) if i not in to_remove]
```

#### Açıklama
`correlation` iki değişken arasındaki Pearson korelasyon katsayısını hesaplar. `mutual_information` bir özelliğin hedef hakkında ne kadar bilgi taşıdığını ölçer (doğrusal olmayan ilişkileri de yakalar). `variance_threshold` çok az değişen özellikleri atar. `remove_correlated` birbiriyle yüksek korelasyonlu özelliklerden birini kaldırarak çoklu bağlantıyı (multicollinearity) azaltır.

### Adım 6: Tam pipeline ve demo

```python
import random


def make_housing_data(n=200, seed=42):
    random.seed(seed)
    data = []
    for _ in range(n):
        sqft = random.uniform(500, 5000)
        bedrooms = random.choice([1, 2, 3, 4, 5])
        age = random.uniform(0, 50)
        neighborhood = random.choice(["downtown", "suburbs", "rural"])
        has_pool = random.choice([True, False])

        sqft_with_missing = sqft if random.random() > 0.05 else None
        age_with_missing = age if random.random() > 0.08 else None

        price = (
            50 * sqft
            + 20000 * bedrooms
            - 1000 * age
            + (50000 if neighborhood == "downtown" else 10000 if neighborhood == "suburbs" else 0)
            + (15000 if has_pool else 0)
            + random.gauss(0, 20000)
        )

        data.append({
            "sqft": sqft_with_missing,
            "bedrooms": bedrooms,
            "age": age_with_missing,
            "neighborhood": neighborhood,
            "has_pool": has_pool,
            "price": price,
        })
    return data


if __name__ == "__main__":
    data = make_housing_data(200)

    print("=== Raw Data Sample ===")
    for row in data[:3]:
        print(f"  {row}")

    sqft_raw = [d["sqft"] for d in data]
    age_raw = [d["age"] for d in data]
    prices = [d["price"] for d in data]

    print("\n=== Missing Value Handling ===")
    sqft_missing = sum(1 for v in sqft_raw if v is None)
    age_missing = sum(1 for v in age_raw if v is None)
    print(f"  sqft missing: {sqft_missing}/{len(sqft_raw)}")
    print(f"  age missing: {age_missing}/{len(age_raw)}")

    sqft_indicator = add_missing_indicator(sqft_raw)
    age_indicator = add_missing_indicator(age_raw)
    sqft_imputed, sqft_fill = impute_median(sqft_raw)
    age_imputed, age_fill = impute_mean(age_raw)
    print(f"  sqft filled with median: {sqft_fill:.0f}")
    print(f"  age filled with mean: {age_fill:.1f}")

    print("\n=== Numerical Transforms ===")
    sqft_scaled = standardize(sqft_imputed)
    age_scaled = min_max_scale(age_imputed)
    sqft_log = log_transform(sqft_imputed)
    age_binned = bin_values(age_imputed, n_bins=5)
    print(f"  sqft standardized: mean={sum(sqft_scaled)/len(sqft_scaled):.4f}, std={math.sqrt(sum(v**2 for v in sqft_scaled)/len(sqft_scaled)):.4f}")
    print(f"  age min-max: [{min(age_scaled):.2f}, {max(age_scaled):.2f}]")
    print(f"  age bins: {sorted(set(age_binned))}")

    print("\n=== Categorical Encoding ===")
    neighborhoods = [d["neighborhood"] for d in data]

    ohe, ohe_cats = one_hot_encode(neighborhoods)
    print(f"  One-hot categories: {ohe_cats}")
    print(f"  Sample encoding: {neighborhoods[0]} -> {ohe[0]}")

    le, le_map = label_encode(neighborhoods)
    print(f"  Label encoding map: {le_map}")

    te, te_map = target_encode(neighborhoods, prices, smoothing=10)
    print(f"  Target encoding: {({k: round(v) for k, v in te_map.items()})}")

    print("\n=== Text Features ===")
    descriptions = [
        "large modern house with pool",
        "small cozy cottage near downtown",
        "spacious family home with large yard",
        "modern apartment downtown with view",
        "rustic cabin in rural area",
    ]
    cv, cv_vocab = count_vectorize(descriptions)
    print(f"  Vocabulary size: {len(cv_vocab)}")
    print(f"  Doc 0 non-zero features: {sum(1 for v in cv[0] if v > 0)}")

    tf, tf_vocab = tfidf(descriptions)
    print(f"  TF-IDF vocabulary size: {len(tf_vocab)}")
    top_words = sorted(tf_vocab.keys(), key=lambda w: tf[0][tf_vocab[w]], reverse=True)[:3]
    print(f"  Doc 0 top TF-IDF words: {top_words}")

    print("\n=== Polynomial Features ===")
    sample_row = [sqft_scaled[0], age_scaled[0]]
    poly = polynomial_features(sample_row, degree=2)
    print(f"  Input: {[round(v, 4) for v in sample_row]}")
    print(f"  Polynomial: {[round(v, 4) for v in poly]}")
    print(f"  Features: [x1, x2, x1^2, x2^2, x1*x2]")

    print("\n=== Feature Selection ===")
    feature_matrix = [
        [sqft_scaled[i], age_scaled[i], float(sqft_indicator[i]), float(age_indicator[i])]
        + ohe[i]
        for i in range(len(data))
    ]

    print(f"  Total features: {len(feature_matrix[0])}")

    surviving_var = variance_threshold(feature_matrix, threshold=0.01)
    print(f"  After variance threshold (0.01): {len(surviving_var)} features kept")

    surviving_corr = remove_correlated(feature_matrix, threshold=0.9)
    print(f"  After correlation filter (0.9): {len(surviving_corr)} features kept")

    binary_prices = [1 if p > sum(prices) / len(prices) else 0 for p in prices]
    print("\n  Mutual information with target:")
    feature_names = ["sqft", "age", "sqft_missing", "age_missing"] + [f"neigh_{c}" for c in ohe_cats]
    for j in range(len(feature_matrix[0])):
        col = [feature_matrix[i][j] for i in range(len(feature_matrix))]
        mi = mutual_information(col, binary_prices, n_bins=10)
        print(f"    {feature_names[j]}: MI={mi:.4f}")

    print("\n  Correlation with price:")
    for j in range(len(feature_matrix[0])):
        col = [feature_matrix[i][j] for i in range(len(feature_matrix))]
        corr = correlation(col, prices)
        print(f"    {feature_names[j]}: r={corr:.4f}")
```

#### Açıklama
`make_housing_data` %5-8 oranında eksik değer içeren sentetik bir ev fiyat verisi üretir. `__main__` bloğu tüm dönüşümleri uçtan uca çalıştırır: önce eksik değerler işlenir, sonra sayısal dönüşümler ve kategorik kodlamalar uygulanır, metin özellikleri çıkarılır, polinom özellikler eklenir ve son olarak varyans eşiği, korelasyon filtresi ve karşılıklı bilgi ile özellik seçimi yapılır.

## Kullanım

scikit-learn ile bu dönüşümler birleştirilebilir pipeline'lar halinde gelir:

```python
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures
from sklearn.impute import SimpleImputer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import mutual_info_classif, VarianceThreshold
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

numeric_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])

categorical_pipe = Pipeline([
    ("encoder", OneHotEncoder(sparse_output=False)),
])

preprocessor = ColumnTransformer([
    ("num", numeric_pipe, ["sqft", "age"]),
    ("cat", categorical_pipe, ["neighborhood"]),
])
```

Sıfırdan yazılan versiyonlar her dönüşümün içinde tam olarak ne olduğunu gösterir. Kütüphane versiyonları uç durumları, seyrek matris desteğini ve pipeline kompozisyonunu ekler, ancak matematik aynıdır.

## Çıktılar

Bu ders şunları üretir:
- `outputs/prompt-feature-engineer.md` — ham veriden sistematik olarak özellik mühendisliği yapmak için bir prompt

## Alıştırmalar

1. Sayısal dönüşümlere sağlam ölçekleme (robust scaling — ortalama ve standart sapma yerine ortanca ve çeyrekler arası açıklık kullanan) ekleyin. Aşırı aykırı değerler içeren veride standart ölçeklemeyle karşılaştırın.
2. Leave-one-out target encoding uygulayın: her satır için, o satırın kendi hedef değerini hariç tutarak hedef ortalamasını hesaplayın. Bunun saf target encoding'e kıyasla aşırı öğrenmeyi nasıl azalttığını gösterin.
3. Varyans eşiği, korelasyon filtreleme ve karşılıklı bilgi sıralamasını birleştiren otomatik bir özellik seçim pipeline'ı oluşturun. Bunu konut verisine uygulayın ve tüm özellikler ile seçilen özellikler arasında model performansını (basit bir doğrusal regresyon kullanarak) karşılaştırın.

## Anahtar Terimler

| Terim | Söylenen | Gerçek Anlamı |
|-------|----------|---------------|
| Feature engineering | "Yeni sütunlar yapmak" | Ham veriyi, modelin örüntüleri görmesini sağlayacak temsillere dönüştürmek |
| Standardization | "Normal yapmak" | Ortalamayı çıkarıp standart sapmaya bölmek, böylece özellik ortalama=0 ve std=1 olur |
| One-hot encoding | "Kukla değişken yapmak" | Her kategori için bir ikili sütun oluşturmak, her satırda tam olarak bir sütun 1 olur |
| Target encoding | "Cevabı kullanarak kodlamak" | Her kategoriyi, o kategorideki ortalama hedef değeriyle değiştirmek, aşırı öğrenmeyi önlemek için smoothing uygulanır |
| TF-IDF | "Süslü kelime sayıları" | Term Frequency çarpı Inverse Document Frequency: kelimeler külliyattaki ayırt ediciliklerine göre ağırlıklandırılır |
| Imputation | "Boşlukları doldurmak" | Eksik değerleri tahmini değerlerle (ortalama, ortanca, mod veya model tahmini) değiştirmek |
| Feature selection | "Kötü sütunları atmak" | Gürültü veya gereksizlik ekleyen özellikleri kaldırmak, yalnızca hedef hakkında sinyal taşıyanları tutmak |
| Mutual information | "Bir şeyin başka bir şey hakkında ne kadar bilgi verdiği" | X değişkenini gözlemlemenin Y değişkenindeki belirsizliği ne kadar azalttığının ölçüsü |
| Data leakage | "Kazara hile yapmak" | Eğitim sırasında tahmin anında mevcut olmayacak bilgiyi kullanmak, yanlış iyimser sonuçlar vermek |

## İleri Okuma

- [Feature Engineering and Selection (Max Kuhn & Kjell Johnson)](http://www.feat.engineering/) — özellik mühendisliğinin tüm yelpazesini kapsayan ücretsiz çevrimiçi kitap
- [scikit-learn Preprocessing Guide](https://scikit-learn.org/stable/modules/preprocessing.html) — tüm standart dönüşümler için pratik referans
- [Target Encoding Done Right (Micci-Barreca, 2001)](https://dl.acm.org/doi/10.1145/507533.507538) — smoothing ile target encoding üzerine orijinal makale
