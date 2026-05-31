# Sentiment Analysis

> Kanonik NLP görevi. Klasik metin sınıflandırması hakkında bilmeniz gereken her şey burada karşımıza çıkıyor.

**Tür:** İnşa
**Diller:** Python
**Ön Koşullar:** Faz 5 · 02 (BoW + TF-IDF), Faz 2 · 14 (Naive Bayes)
**Süre:** ~75 dakika

## Problem

"The food was not great." Olumlu mu olumsuz mu?

Sentiment basit görünür. Bir yorumcu bir şeyi beğendiğini veya beğenmediğini söylemiştir. Cümleyi etiketleyin. Kanonik NLP görevi olmasının nedeni, her kolay görünen durumun zor bir durumu saklıyor olmasıdır. Olumsuzluk anlam tersine çevirir. Alaycılığı (sarcasm) tersine çevirir. "Not bad at all" iki olumsuz kodlu kelimeye rağmen olumludur. Emoji'ler çevre metinden daha fazla sinyal taşır. Alan vocabulary'si önemlidir (`tight` müzik incelemesinde vs `tight` moda incelemesinde).

Sentiment, klasik NLP için çalışan bir laboratuvardır. Her naive taban çizgisinin neden belirli bir başarısızlık moduna sahip olduğunu anlarsanız, her daha zengin modelin neden icat edildiğini anlarsınız. Bu ders sıfırdan bir Naive Bayes taban çizgisi oluşturur, lojistik regresyon ekler ve üretim sentiment'ini uyumluluk düzeyinde bir sorun yapan tuzakları adlandırır.

## Kavram

Klasik sentiment iki adımlı bir tariftir.

1. **Temsil.** Metni bir özellik vektörüne dönüştürün. BoW, TF-IDF veya n-gram'lar.
2. **Sınıflandır.** Etiketlenmiş örnekler üzerinde bir doğrusal model (Naive Bayes, lojistik regresyon, SVM) uydurun.

Naive Bayes, işe yarayan en aptal modeldir. Her özelliğin etiket verildiğinde bağımsız olduğunu varsayın. Sayımlardan `P(kelime | olumlu)` ve `P(kelime | olumsuz)` tahmin edin. Çıkarımda olasılıkları çarpın. "Naive" bağımsızlık varsayımı gülünç derecede yanlıştır ama sonuçlar şaşırtıcı kadar güçlüdür. Neden: seyrek metin özellikleri ve orta düzey veriyle, sınıflandırıcı her kelimenin hangi tarafa eğildiğine ne kadar eğildiğinden daha fazla önem verir.

Lojistik regresyon bağımsızlık varsayımını düzeltir. Olumsuz ağırlıklar da dahil olmak üzere özellik başına bir ağırlık öğrenir. `not good` bigram özelliği olarak olumsuz bir ağırlık alır. Naive Bayes, hiç etiketlemediği bigramlar için bunu yapamaz.

## İnşa Et

### Adım 1: gerçek bir mini veri kümesi

```python
POSITIVE = [
    "absolutely loved this movie",
    "beautiful cinematography and a great story",
    "one of the best films of the year",
    "brilliant acting from the lead",
    "heartwarming and funny",
]

NEGATIVE = [
    "boring and far too long",
    "not worth your time",
    "the plot made no sense",
    "terrible acting, awful script",
    "i want my two hours back",
]
```

Küçük, kasıtlı olarak. Gerçek iş on binlerce örnek kullanır (IMDb, SST-2, Yelp polaritesi). Matematik özdeştir.

### Adım 2: sıfırdan multinomial Naive Bayes

```python
import math
from collections import Counter


def train_nb(docs_by_class, vocab, alpha=1.0):
    class_priors = {}
    class_word_probs = {}
    total_docs = sum(len(d) for d in docs_by_class.values())

    for cls, docs in docs_by_class.items():
        class_priors[cls] = len(docs) / total_docs
        counts = Counter()
        for doc in docs:
            for token in doc:
                counts[token] += 1
        total = sum(counts.values()) + alpha * len(vocab)
        class_word_probs[cls] = {
            w: (counts[w] + alpha) / total for w in vocab
        }
    return class_priors, class_word_probs


def predict_nb(doc, class_priors, class_word_probs):
    scores = {}
    for cls in class_priors:
        s = math.log(class_priors[cls])
        for token in doc:
            if token in class_word_probs[cls]:
                s += math.log(class_word_probs[cls][token])
        scores[cls] = s
    return max(scores, key=scores.get)
```

Additif yumuşatma (alpha=1.0) Laplace yumuşatmasıdır. Olmadan, bir sınıfta hiç görülmemiş bir kelimenin olasılığı sıfırdır ve log sonsuza gider. `alpha=0.01` pratikte yaygındır. `alpha=1.0` öğretim varsayılanıdır.

### Adım 3: sıfırdan lojistik regresyon

```python
import numpy as np


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -20, 20)))


def train_lr(X, y, epochs=500, lr=0.05, l2=0.01):
    n_features = X.shape[1]
    w = np.zeros(n_features)
    b = 0.0
    for _ in range(epochs):
        logits = X @ w + b
        preds = sigmoid(logits)
        err = preds - y
        grad_w = X.T @ err / len(y) + l2 * w
        grad_b = err.mean()
        w -= lr * grad_w
        b -= lr * grad_b
    return w, b


def predict_lr(X, w, b):
    return (sigmoid(X @ w + b) >= 0.5).astype(int)
```

Burada L2 düzenlileştirme önemlidir. Metin özellikleri seyrektir; L2 olmadan model eğitim örneklerini ezer. `0.01` ile başlayın ve ayarlayın.

### Adım 4: olumsuzluğu ele alma (başarısızlık modu)

"Not good" ve "not bad" ifadelerini düşünün. Bir BoW sınıflandırıcısı `{not, good}` ve `{not, bad}` görür ve eğitimde hangisi daha çok göründüyse ondan öğrenir. Bir bigram sınıflandırıcısı `not_good` ve `not_bad` görür ve bunları farklı özellikler olarak öğrenir. Bu genellikle yeterlidir.

Bigram'larınız olmadığında işe yararan daha kaba bir düzeltme: **olumsuzluk kapsamı (negation scoping)**. Bir olumsuzluk kelimesinden sonra gelen token'ları bir sonraki noktalama işaretine kadar `NOT_` ile önekleyin.

```python
NEGATION_WORDS = {"not", "no", "never", "nor", "none", "nothing", "neither"}
NEGATION_TERMINATORS = {".", "!", "?", ",", ";"}


def apply_negation(tokens):
    out = []
    negate = False
    for token in tokens:
        if token in NEGATION_TERMINATORS:
            negate = False
            out.append(token)
            continue
        if token in NEGATION_WORDS:
            negate = True
            out.append(token)
            continue
        out.append(f"NOT_{token}" if negate else token)
    return out
```

```python
>>> apply_negation(["not", "good", "at", "all", ".", "but", "funny"])
['not', 'NOT_good', 'NOT_at', 'NOT_all', '.', 'but', 'funny']
```

Artık `good` ve `NOT_good` farklı özelliklerdir. Sınıflandırıcı bunlara zıt ağırlıklar verebilir. Üç satırlık ön-işleme, sentiment benchmark'larında ölçülebilir bir doğruluk artışı sağlar.

### Adım 5: önemli değerlendirme metrikleri

Sınıflar dengesizse yalnızca doğruluk yanıltıcıdır. Gerçek sentiment corpus'ları genellikle %70-80 olumlu veya %70-80 olumsuzdur; sabit bir çoğunluk sınıflandırıcısı %80 doğruluk alır ve işe yaramaz. Aşağıdakilerin her birini raporlayın:

- **Sınıf başına hassasiyet ve duyarlılık.** Sınıf başına bir çift. Makro ortalamasını alarak sınıf dengesine saygı gösteren bir tek sayı elde edin.
- **Makro-F1 (dengesiz veri için birincil metrik).** Sınıf başına F1 puanlarının ortalaması, eşit ağırlıklı. Sınıflar dengesiz olduğunda doğruluk yerine bunu kullanın.
- **Ağırlıklı-F1 (alternatif).** Makro ile aynı ama sınıf sıklığına göre ağırlıklandırılmış. Dengesizliğin kendisi iş anlamı taşıdığında makro-F1 ile birlikte raporlayın.
- **Karmaşıklık matrisi (confusion matrix).** Ham sayımlar. Herhangi bir skaler metriğe güvenmeden önce her zaman inceleyin; modelin hangi sınıf çiftini karıştırdığını ortaya çıkarır.
- **Sınıf başına hata örnekleri.** Sınıf başına 5 yanlış tahmin çekin. Okuyun. Gerçek hataları okumanın yerini hiçbir şey tutmaz.

Ciddi şekilde dengesiz veri için (> %95-5 oranı), doğruluk yerine **AUROC** ve **AUPRC** raporlayın. AUPRC, azınlık sınıfına daha duyarlıdır; bu genellikle önemli olan şeydir (spam, dolandırıcılık, nadir sentiment).

**Kaçınılması gereken yaygın hata.** Dengesiz veride makro-F1 yerine mikro-F1 raporlamak, çoğunluk sınıfı tarafından domine edilen yüksek görünen bir sayı verir. Makro-F1, azınlık sınıfı performansını görmenizi zorunlu kılar.

```python
def evaluate(y_true, y_pred):
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "precision": precision, "recall": recall, "f1": f1}
```

## Kullan

scikit-learn bunu altı satırda, doğru şekilde yapar.

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

pipe = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, stop_words=None)),
    ("clf", LogisticRegression(C=1.0, max_iter=1000)),
])
pipe.fit(X_train, y_train)
print(pipe.score(X_test, y_test))
```

Dikkat edilmesi gereken üç şey. `stop_words=None` olumsuzlukları korur. `ngram_range=(1, 2)` bigram'ları ekler; böylece `not_good` bir özellik haline gelir. `sublinear_tf=True` tekrarlayan kelimeleri bastırır. Bu üç bayrak, SST-2'de %75 doğruluklu bir taban çizgisi ile %85 doğruluklu bir taban çizgisi arasındaki farktır.

### Ne zaman bir transformer'a başvurmalı

- Alaycılık (sarcasm) tespiti. Klasik modeller burada başarısız olur. Nokta.
- Sentiment'in belge ortasında değiştiği uzun yorumlar.
- Aspect-based sentiment. "Camera was great but battery was terrible." Sentiment'i aspect'lere atfetmeniz gerekir. Yalnızca transformer'lar veya yapılandırılmış çıktı modelleri.
- İngilizce olmayan, düşük kaynaklı diller. Çok dilli BERT size sıfır atımlı bir taban çizgisini ücretsiz verir.

Yukarıdakilerden herhangi birine ihtiyacınız varsa, Faz 7'ye (transformers derinlemesine) geçin. Aksi takdirde, TF-IDF artı bigram artı olumsuzluk eleme üzerine Naive Bayes veya lojistik regresyon 2026 üretim taban çizginizdir.

### Tekrar üretilebilirlik tuzağı (tekrar)

Sentiment modellerini yeniden eğitmek rutindir. Yeniden değerlendirmek değildir. Makalelerde raporlanan doğruluk sayıları belirli bölmeleri, belirli ön-işlemeyi, belirli tokenizer'ları kullanır. Yeni modelinizi aynı hattı kullanmadan bir taban çizgisiyle karşılaştırırsanız, yanıltıcı farklar alırsınız. Her zaman taban çizgisini kendi hattınızda yeniden üretin, makalenin sayısında değil.

## Ürün Haline Getir

`outputs/prompt-sentiment-baseline.md` olarak kaydedin:

```markdown
---
name: sentiment-baseline
description: Yeni bir veri kümesi için bir sentiment analysis taban çizgisi tasarlayın.
phase: 5
lesson: 05
---

Bir veri kümesi tanımı (alan, dil, boyut, etiket granularity'sı, gecikme bütçesi) verildiğinde çıktı olarak:

1. Özellik çıkarma tarifi. Tokenizer, n-gram aralığı, stopwords politikası (genellikle koru), olumsuzluk eleme (kapsamlı önek veya bigram'lar) belirtin.
2. Sınıflandırıcı. Taban çizgisi için Naive Bayes, üretim için lojistik regresyon, yalnızca alan alaycılık/aspect/cross-lingual gerektiriyorsa transformer.
3. Değerlendirme planı. Hassasiyet, duyarlılık, F1, karmaşıklık matrisi ve sınıf başına hata örneklerini raporlayın (yalnızca skaler değil).
4. Üretim sonrası izlenecek bir başarısızlık modu. Alan kayması ve alaycılık en üst ikisidir.

Sentiment görevleri için stopwords kaldırmayı önermeyi reddedin. Sınıflar dengesizse (örneğin %90 olumlu) doğruluğu tek metrik olarak raporlamayı reddedin. Subword-zengin dilleri kelime düzeyi TF-IDF yerine FastText veya transformer embedding'leri gerektiriyor olarak işaretleyin.
```

## Alıştırmalar

1. **Kolay.** `apply_negation`'ı scikit-learn hattına ön-işleme adımı olarak ekleyin ve küçük bir sentiment veri kümesinde F1 farkını ölçün.
2. **Orta.** Sınıf-ağırlıklı lojistik regresyonu uygulayın (scikit-learn'e `class_weight="balanced"` geçirin veya gradyanı kendiniz türetin). Sentezlenmiş %90-10 sınıf dengesizliği üzerindeki etkiyi ölçün.
3. **Zor.** Sentiment modelinin artık kalan değerleri (residuals) üzerinde ikinci bir sınıflandırıcı eğiterek bir alaycılık (sarcasm) dedektörü oluşturun. Deneysel kurulumunuzu belgeleyin. Doğruluğunuz şansın (chance) altında olduğunu okuyucuya uyarın (2 sınıflı alaycılıkta şans düzeyi yaklaşık %50'dir ve ilk denemelerin çoğu oraya iner).

## Anahtar Terimler

| Terim | İnsanların Söylediği | Gerçekte Ne Anlama Gelir |
|------|-----------------|-----------------------|
| Polarite | Olumlu veya olumsuz | İkili etiket; bazen nötr veya ayrıntılı (5 yıldız) olarak genişletilir. |
| Aspect-based sentiment | Aspect başına polarite | Metinde bahsedilen belirli varlıklara veya niteliklere sentiment atfetme. |
| Olumsuzluk kapsamı | Yakın token'ları tersine çevirme | "not" sonrası token'ları noktalama işaretine kadar `NOT_` ile önekleyin. |
| Laplace yumuşatması | Sayımlara 1 ekleme | Naive Bayes'te sıfır olasılıklı özellikleri önler. |
| L2 düzenlileştirme | Ağırlıkları küçültme | Kayba `lambda * sum(w^2)` ekler. Seyrek metin özellikleri için gereklidir. |

## İleri Okuma

- [Pang and Lee (2008). Opinion Mining and Sentiment Analysis](https://www.cs.cornell.edu/home/llee/opinion-mining-sentiment-analysis-survey.html) — temel anket. Uzun ama ilk dört bölüm her şeyi kapsıyor.
- [Wang and Manning (2012). Baselines and Bigrams: Simple, Good Sentiment and Topic Classification](https://aclanthology.org/P12-2018/) — bigram'ların + Naive Bayes'in kısa metinde yenilmesinin zor olduğunu gösteren makale.
- [scikit-learn text feature extraction docs](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction) — `CountVectorizer`, `TfidfVectorizer` ve ayarlayacağınız her ayar için referans.
