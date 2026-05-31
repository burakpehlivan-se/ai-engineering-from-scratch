# Transformer Öncesi Metin Üretimi — N-gram Dil Modelleri

> Bir kelime sürprizse, model kötüdür. Perplexity (şaşkınlık), sürprizi bir sayıya dönüştürür. Smoothing (düzleştirme) onu sonlu kılar.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 5 · 01 (Metin İşleme), Faz 2 · 14 (Naive Bayes)
**Süre:** ~45 dakika

## Problem

Transformer'lardan, RNN'lerden, kelime embedding'lerinden önce, bir dil modeli bir sonraki kelimeyi, önceki `n-1` kelimenin ardından ne sıklıkla geldiğini sayarak tahmin ederdi. "the cat" → "sat" 47 kez, "the cat" → "jumped" 12 kez, "the cat" → "refrigerator" 0 kez. Olasılık dağılımı elde etmek için normalleştirin.

Bu bir n-gram dil modelidir. 1980'den 2015'e kadar her ses tanıma sistemini, her yazım denetleyicisini ve her ifade tabanlı makine çeviri sistemini çalıştırdı. Ucuz cihaz içi dil modellemesi gerektiğinde hâlâ çalışır.

İlginç problem, görülmemiş n-gram'larla ne yapılması gerektiğidir. Ham sayı tabanlı bir model, görmediği her şeye sıfır olasılık atar; bu felakettir çünkü cümleler uzundur ve neredeyse her uzun cümle en az bir görülmemiş dizi içerir. Elli yıllık smoothing araştırması bunu çözdü. Kneser-Ney smoothing sonucudur ve modern derin öğrenme empirik geleneklerini miras aldı.

## Kavram

![N-gram model: count, smooth, generate](../assets/ngram.svg)

**N-gram olasılığı:** `P(w_i | w_{i-n+1}, ..., w_{i-1})`. `n`'yi sabitleyin (genellikle 3 untuk trigram, 4 için 4-gram). Sayılardan hesaplayın:

```text
P(w | context) = count(context, w) / count(context)
```

#### Açıklama
Bu, bir n-gram'ın koşullu olasılığının formülüdür. Bağlam verildiğinde bir sonraki kelimenin olasılığı, bağlam ve kelimenin birlikte görülme sayısının bağlamın görülme sayısına bölünmesiyle hesaplanır.

**Sıfır sayma problemi.** Eğitimde görülmemiş her n-gram sıfır olasılık alır. 2007'de Brown corpus'u üzerinde yapılan bir çalışma, 4-gram modelinin bile %30'luk tutma (held-out) 4-gram'ının eğitimde görülmediğini ortaya koydu. Smoothing olmadan gerçek bir metin üzerinde değerlendirme yapamazsınız.

**Smoothing yaklaşımları, sofistikeleşme sırasıyla:**

1. **Laplace (add-one).** Her sayıya 1 ekleyin. Basit, nadir olaylarda berbat.
2. **Good-Turing.** Sıklık-sıklığına göre daha yüksek sıklıklı olaylardan görülmemişlere olasılık kütlesi yeniden dağıtımı.
3. **Interpolasyon (Interpolation).** Ayarlanabilir ağırlıklarla n-gram, (n-1)-gram vb. tahminlerini birleştirin.
4. **Geri çekilme (Backoff).** n-gram'ın sayısı sıfırsa, (n-1)-gram'a geri dönün. Katz backoff bunu normalleştirir.
5. **Mutlak indirimleme (Absolute discounting).** Tüm sayılardan sabit bir indirim `D` çıkarın, görülmemişlere yeniden dağıtın.
6. **Kneser-Ney.** Mutlak indirimleme artı alt düzey model için zeki bir seçim: ham frekans yerine *devam olasılığını* (bir kelimenin kaç bağlamda göründüğünü) kullanın.

Kneser-Ney içgörüsü derindir. "San Francisco" yaygın bir bigram'dır. Unigram "Francisco" çoğunlukla "San"'dan sonra görünür. Saf mutlak indirimleme "Francisco"ya yüksek unigram olasılığı verir (sayı yüksek olduğu için). Kneser-Ney, "Francisco"nun yalnızca bir bağlamda göründüğünü fark eder ve devam olasılığını buna göre düşürür. Sonuç: "Francisco" ile biten yeni bir bigram, uygun düşük olasılığı alır.

**Değerlendirme: perplexity (şaşkınlık).** Tutma test seti üzerinde kelime başına ortalama negatif log-olay olasılığının kuvveti. Düşük olanı iyidir. 100 perplexity, modelin 100 kelime arasında düzgün seçim yapmak kadar şaşkın olduğu anlamına gelir.

```text
perplexity = exp(- (1/N) * Σ log P(w_i | context_i))
```

#### Açıklama
Perplexity, bir dil modelinin kalitesini ölçen temel metriktir. Düşük perplexity, modelin test verisindeki kelimeleri daha iyi tahmin ettiği anlamına gelir. 100 perplexity, modelin her kelime için 100 olası seçenek arasında rastgele seçim yapması kadar şaşkın olduğunu gösterir.

## İnşa Et

### Adım 1: trigram sayıları

```python
from collections import Counter, defaultdict


def train_ngram(corpus_tokens, n=3):
    ngrams = Counter()
    contexts = Counter()
    for sentence in corpus_tokens:
        padded = ["<s>"] * (n - 1) + sentence + ["</s>"]
        for i in range(len(padded) - n + 1):
            ctx = tuple(padded[i:i + n - 1])
            word = padded[i + n - 1]
            ngrams[ctx + (word,)] += 1
            contexts[ctx] += 1
    return ngrams, contexts


def raw_probability(ngrams, contexts, context, word):
    ctx = tuple(context)
    if contexts.get(ctx, 0) == 0:
        return 0.0
    return ngrams.get(ctx + (word,), 0) / contexts[ctx]
```

#### Açıklama
Girdi, tokenize edilmiş cümlelerin bir listesidir. Çıktı, n-gram sayıları ve bağlam sayılarıdır. `<s>` ve `</s>` cümle sınırlarıdır. Bu kod, ham olasılık hesaplaması için temel n-gram yapısını kurar.

Girdi, tokenize edilmiş cümlelerin bir listesidir. Çıktı, n-gram sayıları ve bağlam sayılarıdır. `<s>` ve `</s>` cümle sınırlarıdır.

### Adım 2: Laplace smoothing

```python
def laplace_probability(ngrams, contexts, vocab_size, context, word):
    ctx = tuple(context)
    numerator = ngrams.get(ctx + (word,), 0) + 1
    denominator = contexts.get(ctx, 0) + vocab_size
    return numerator / denominator
```

#### Açıklama
Her sayıya 1 ekler. Düzleştirir ancak görülmemiş olaylara aşırı kütlesel pay ayırır, nadir-bilinen olaylara da zarar verir.

Her sayıya 1 ekler. Düzleştirir ancak görülmemiş olaylara aşırı kütlesel pay ayırır, nadir-bilinen olaylara da zarar verir.

### Adım 3: Kneser-Ney (bigram, interpolate edilmiş)

```python
def kneser_ney_bigram_model(corpus_tokens, discount=0.75):
    unigrams = Counter()
    bigrams = Counter()
    unigram_contexts = defaultdict(set)

    for sentence in corpus_tokens:
        padded = ["<s>"] + sentence + ["</s>"]
        for i, w in enumerate(padded):
            unigrams[w] += 1
            if i > 0:
                prev = padded[i - 1]
                bigrams[(prev, w)] += 1
                unigram_contexts[w].add(prev)

    total_unique_bigrams = sum(len(ctx_set) for ctx_set in unigram_contexts.values())
    continuation_prob = {
        w: len(ctx_set) / total_unique_bigrams for w, ctx_set in unigram_contexts.items()
    }

    context_totals = Counter()
    for (prev, w), count in bigrams.items():
        context_totals[prev] += count

    unique_follow = defaultdict(set)
    for (prev, w) in bigrams:
        unique_follow[prev].add(w)

    def prob(prev, w):
        count = bigrams.get((prev, w), 0)
        denom = context_totals.get(prev, 0)
        if denom == 0:
            return continuation_prob.get(w, 1e-9)
        first_term = max(count - discount, 0) / denom
        lambda_prev = discount * len(unique_follow[prev]) / denom
        return first_term + lambda_prev * continuation_prob.get(w, 1e-9)

    return prob
```

#### Açıklama
Üç hareketli parça: `continuation_prob`, "bu kelime kaç farklı bağlamda görünüyor?" sorusunu yakalar (Kneser-Ney yeniliği). `lambda_prev`, indirimle serbest bırakılan kütledir, geri çekme ağırlığı olarak kullanılır. Son olasılık, indirilmiş ana terim artı ağırlıklı devam terimidir.

Üç hareketli parça: `continuation_prob`, "bu kelime kaç farklı bağlamda görünüyor?" sorusunu yakalar (Kneser-Ney yeniliği). `lambda_prev`, indirimle serbest bırakılan kütledir, geri çekme ağırlığı olarak kullanılır.

### Adım 4: örnekleme ile metin üretimi

```python
import random


def generate(prob_fn, vocab, prefix, max_len=30, seed=0):
    rng = random.Random(seed)
    tokens = list(prefix)
    for _ in range(max_len):
        candidates = [(w, prob_fn(tokens[-1], w)) for w in vocab]
        total = sum(p for _, p in candidates)
        r = rng.random() * total
        acc = 0.0
        for w, p in candidates:
            acc += p
            if r <= acc:
                tokens.append(w)
                break
        if tokens[-1] == "</s>":
            break
    return tokens
```

#### Açıklama
Olasılığa orantılı örnekleme. Her tohum (seed) için farklı çıktı verir. Beam-search benzeri çıktı için her adımda argmax'ı seçin (greedy) ve küçük bir rastgelelik kolu (temperature) ekleyin.

Olasılığa orantılı örnekleme. Her tohum (seed) için farklı çıktı verir. Beam-search benzeri çıktı için her adımda argmax'ı seçin (greedy) ve küçük bir rastgelelik kolu ekleyin.

### Adım 5: perplexity

```python
import math


def perplexity(prob_fn, sentences):
    total_log_prob = 0.0
    total_tokens = 0
    for sentence in sentences:
        padded = ["<s>"] + sentence + ["</s>"]
        for i in range(1, len(padded)):
            p = prob_fn(padded[i - 1], padded[i])
            total_log_prob += math.log(max(p, 1e-12))
            total_tokens += 1
    return math.exp(-total_log_prob / total_tokens)
```

#### Açıklama
Düşük olanı iyidir. Brown corpus'u için iyi ayarlanmış bir 4-gram KN modeli yaklaşık 140 perplexity'ye ulaşır. Bir transformer LM aynı test seti üzerinde 15-30'a ulaşır. Fark yaklaşık 10 katıdır. Bu fark, alanın neden ilerlediğidir.

Düşük olanı iyidir. Brown corpus'u için iyi ayarlanmış bir 4-gram KN modeli yaklaşık 140 perplexity'ye ulaşır. Bir transformer LM aynı test seti üzerinde 15-30'a ulaşır. Fark yaklaşık 10 katıdır.

## Kullan

- **Klasik NLP öğretimi.** Smoothing, MLE ve perplexity'nin alabileceğiniz en açık sunumu.
- **KenLM.** Production n-gram kütüphanesi. Düşük gecikmenin önemli olduğu ses ve MT sistemlerinde yeniden puanlayıcı (rescorer) olarak kullanılır.
- **Cihaz içi otomatik tamamlama.** Klavyelerde trigram modelleri. Hâlâ.
- **Temel hatlar (Baselines).** Neural LM'inizin iyi olduğunu beyan etmeden önce her zaman bir n-gram LM perplexity hesaplayın. Transformer'ınız KN'ı geniş bir marjla geçemiyorsa, bir sorun var demektir.

## Ürün Olarak Kullan

`outputs/prompt-lm-baseline.md` olarak kaydedin:

```markdown
---
name: lm-baseline
description: Build a reproducible n-gram language model baseline before training a neural LM.
phase: 5
lesson: 16
---

Given a corpus and target use (next-word prediction, rescoring, perplexity baseline), output:

1. N-gram order. Trigram for general English, 4-gram if corpus is large, 5-gram for speech rescoring.
2. Smoothing. Modified Kneser-Ney is the default; Laplace only for teaching.
3. Library. `kenlm` for production, `nltk.lm` for teaching, roll your own only to learn.
4. Evaluation. Held-out perplexity with consistent tokenization between train and test sets.

Refuse to report perplexity computed with different tokenization between systems being compared — perplexity numbers are comparable only under identical tokenization. Flag OOV rate in test set; KN handles OOV poorly unless you reserve a special <UNK> token during training.
```

#### Açıklama
Bu, neural LM eğitmeden önce tekrarlanabilir bir n-gram dil modeli temel hattı (baseline) oluşturma talimatıdır.

## Alıştırmalar

1. **Kolay.** 1.000 cümlelik bir Shakespeare corpus'u üzerinde bir trigram LM eğitin. 20 cümle üretin. Yerel olarak inandırıcı ama global olarak tutarsız olacaklardır. Bu klasik demodur.
2. **Orta.** KN modeliniz için tutma (held-out) Shakespeare bölümünde perplexity uygulayın. Laplace ile karşılaştırın. KN'ın perplexity'yi %30-50 düşürdüğünü görmelisiniz.
3. **Zor.** Bir trigram yazım denetleyicisi (spell corrector) oluşturun: yanlış yazılmış bir kelime ve bağlamı verildiğinde, düzeltmeler üretin ve LM altında bağlam olasılığına göre sıralayın. Birkbeck yazım corpus'u (halka açık) üzerinde değerlendirin.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| N-gram | Kelime dizisi | `n` ardışık token dizisi. |
| Smoothing | Sıfırlardan kaçınma | Görülmemiş olaylara sıfır olmayan olasılık verecek şekilde olasılık kütlesi yeniden dağıtımı. |
| Perplexity | LM kalite metriği | Tutma verisi üzerinde `exp(-ortalama log-olay)`. Düşük olanı iyidir. |
| Backoff | Daha kısa bağlama geri çekilme | Trigram sayısı sıfırsa bigram kullan. Katz backoff bunu resmileştirir. |
| Kneser-Ney | N-gram'lar için en iyi smoothing | Mutlak indirimleme + alt düzey model için devam olasılığı. |
| Devam olasılığı | KN'e özgü | Ham sayı yerine, `w`'ın göründüğü bağlam sayısına göre ağırlıklandırılmış `P(w)`. |

## İleri Okuma

- [Jurafsky ve Martin — Speech and Language Processing, Bölüm 3 (2026 taslak)](https://web.stanford.edu/~jurafsky/slp3/3.pdf) — n-gram LM'lerin ve smoothing'un klasik incelemesi.
- [Chen ve Goodman (1998). An Empirical Study of Smoothing Techniques for Language Modeling](https://dash.harvard.edu/handle/1/25104739) — Kneser-Ney'i en iyi n-gram smoother olarak yerleştiren makale.
- [Kneser ve Ney (1995). Improved Backing-off for M-gram Language Modeling](https://ieeexplore.ieee.org/document/479394) — orijinal KN makalesi.
- [KenLM](https://kheafield.com/code/kenlm/) — hızlı production n-gram LM, 2026'da gecikme duyarlı uygulamalarda hâlâ kullanılıyor.