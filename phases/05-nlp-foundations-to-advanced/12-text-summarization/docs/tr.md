# Metin Özetleme

> Öztüretici (extractive) sistemler size belgenin ne dediğini söyler. Özdürtücü (abstractive) sistemler ise yazarın ne kastettiğini söyler. Farklı görevler, farklı tuzaklar.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 5 · 02 (BoW + TF-IDF), Faz 5 · 11 (Makine Çevirisi)
**Süre:** ~75 dakika

## Problem

2.000 kelimelik bir haber makalesi feed'inize düşer. 120 kelimelik bir özet istersiniz. Ya makalenin en önemli üç cümlesini seçersiniz (öztüretici) ya da içeriği kendi kelimelerinizle yeniden yazarsınız (özdürtücü). Her ikisine de özetleme denir. Birbirinden tamamen farklı problemlerdir.

Öztüretici özetleme bir sıralama problemidir. Her cümleyi puanlar, en iyi `k` tanesini döndürür. Çıktı her zaman dilbilgisel olarak doğrudur因为Metin özetleme, belgelerin ana fikrini daha kısa bir biçimde aktarma görevidir. İki temel yaklaşım vardır: öztüretici (extractive) ve özdürtücü (abstractive).

Öztüretici özetleme bir sıralama problemidir. Her cümleyi puanlar, en iyi `k` tanesini döndürür. Çıktı her zaman dilbilgisel olarak doğrudur çünkü birebir kopyalanmıştır. Risk, içeriğin makale geneline yayılmış olması durumunda parçaları kaçırmasıdır.

Özdürtücü özetleme bir üretim problemidir. Bir transformer, girdiye koşullu olarak yeni metin üretir. Çıktı akıcı ve sıkıştırılmıştır ancak kaynakta olmayan gerçekleri uydurabilir. Risk, kendinden emin bir şekilde yanlış bilgi üretmektir.

Bu derste her ikisi de kendi hata modlarıyla birlikte ele alınır.

## Kavram

![Extractive TextRank vs abstractive transformer](../assets/summarization.svg)

**Öztüretici.** Makaleyi bir graf olarak ele alır: düğümler cümleler, kenarlar benzerliklerdir. Graf üzerinde PageRank (veya benzeri) çalıştırarak cümleleri her şeyle ne kadar bağlı olduklarına göre puanlar. En yüksek puanlı cümleler özet olur. Klasik uygulama **TextRank**'tir (Mihalcea ve Tarau, 2004).

**Özdürtücü.** Bir transformer encoder-decoder'ını (BART, T5, Pegasus) belge-öz çiftleri üzerinde fine-tune edin. Çıkarımda model, belgeyi okur ve cross-attention aracılığıyla token token özet üretir. Pegasus özellikle gap-sentence ön-egitim hedefini kullanır, bu da onu çok fazla fine-tuning olmadan mükemmel bir özetleme aracı yapar.

Değerlendirme **ROUGE** (Recall-Oriented Understudy for Gisting Evaluation) ile yapılır. ROUGE-1 ve ROUGE-2 unigram ve bigram örtüşmesini puanlar. ROUGE-L en uzun ortak alt diziye göre puan verir. Daha yükseği daha iyidir ancak 40 ROUGE-L "iyi" ve 50 "olağanüstü"dür. Her makale üçünü de raporlar. `rouge-score` paketini kullanın.

## İnşa Et

### Adım 1: TextRank (öztüretici)

```python
import math
import re
from collections import Counter


def sentence_split(text):
    return re.split(r"(?<=[.!?])\s+", text.strip())


def similarity(s1, s2):
    w1 = Counter(s1.lower().split())
    w2 = Counter(s2.lower().split())
    intersection = sum((w1 & w2).values())
    denom = math.log(len(w1) + 1) + math.log(len(w2) + 1)
    if denom == 0:
        return 0.0
    return intersection / denom


def textrank(text, top_k=3, damping=0.85, iterations=50, epsilon=1e-4):
    sentences = sentence_split(text)
    n = len(sentences)
    if n <= top_k:
        return sentences

    sim = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                sim[i][j] = similarity(sentences[i], sentences[j])

    scores = [1.0] * n
    for _ in range(iterations):
        new_scores = [1 - damping] * n
        for i in range(n):
            total_out = sum(sim[i]) or 1e-9
            for j in range(n):
                if sim[i][j] > 0:
                    new_scores[j] += damping * sim[i][j] / total_out * scores[i]
        if max(abs(s - ns) for s, ns in zip(scores, new_scores)) < epsilon:
            scores = new_scores
            break
        scores = new_scores

    ranked = sorted(range(n), key=lambda k: scores[k], reverse=True)[:top_k]
    ranked.sort()
    return [sentences[i] for i in ranked]
```

#### Açıklama
Bu kod, orijinal TextRank varyantını uygular. Benzerlik fonksiyonu log-normalize edilmiş kelime örtüşmesi kullanır. TF-IDF vektörlerinin cosinusu da işe yarar. Sönümleme faktörü 0.85 ve iterasyon sayısı PageRank varsayımlarıdır.

İki önemli nokta: benzerlik fonksiyonu log-normalize edilmiş kelime örtüşmesi kullanır, bu orijinal TextRank varyantıdır. TF-IDF vektörlerinin cosinusu da işe yarar. Sönümleme faktörü 0.85 ve iterasyon sayısı PageRank varsayımlarıdır.

### Adım 2: BART ile özdürtücü özetleme

```python
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

article = """(long news article text)"""

summary = summarizer(article, max_length=120, min_length=60, do_sample=False)
print(summary[0]["summary_text"])
```

#### Açıklama
BART-large-CNN, CNN/DailyMail corpus'u üzerinde fine-tune edilmiştir. Kutusundan çıkar çıkmaz haber tarzı özetler üretir. Diğer alanlar (bilimsel makaleler, dialog, hukuk) için ilgili Pegasus checkpoint'ini veya hedef veriniz üzerinde fine-tune edin.

BART-large-CNN, CNN/DailyMail corpus'u üzerinde fine-tune edilmiştir. Kutusundan çıkar çıkmaz haber tarzı özetler üretir. Diğer alanlar (bilimsel makaleler, dialog, hukuk) için ilgili Pegasus checkpoint'ini veya hedef veriniz üzerinde fine-tune edin.

### Adım 3: ROUGE değerlendirmesi

```python
from rouge_score import rouge_scorer

scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
scores = scorer.score(reference_summary, generated_summary)
print({k: round(v.fmeasure, 3) for k, v in scores.items()})
```

#### Açıklama
Her zaman stemming kullanın. Stemming olmadan "running" ve "run" farklı kelimeler sayılır ve ROUGE eşleşmeleri eksik sayar.

Her zaman stemming kullanın. Stemming olmadan "running" ve "run" farklı kelimeler sayılır ve ROUGE eşleşmeleri eksik sayar.

### ROUGE ötesinde (2026 özetleme değerlendirmesi)

ROUGE yirmi yıldır baskın özetleme metriğidir ve 2026'da tek başına yetersizdir. NLG makalelerinin büyük ölçekli meta-analizi şunları göstermiştir:

- **BERTScore** (bağlamsal embedding benzerliği) 2023'e kadar zemin kazandı ve artık çoğu özetleme makalesinde ROUGE ile birlikte raporlanıyor.
- **BARTScore**, değerlendirmeyi üretim olarak ele alır: özetlemeyi, verilen kaynak karşısında bir önceden eğitilmiş BART'ın ne kadar olası atadığına göre puanlar.
- **MoverScore** (bağlamsal embedding'ler üzerinde Earth Mover's Distance), 2025 özetleme benchmark'larında zirveye ulaştı çünkü ROUGE'dan daha iyi anlamsal örtüşmeyi yakalıyor.
- **FactCC** ve **QA-tabanlı sadakat**, 2021-2023'te yaygındı, artık sık sık **G-Eval** (tutarlılık, tutarlılık, akıcılık, ilgiyi zincir düşünce akışı ile puanlayan bir GPT-4 prompt zinciri) ile değiştiriliyor.
- **G-Eval** ve benzer LLM-judge yaklaşımları, iyi tasarlanmış rubriklerle insan yargısıyla ~%80 eşleşir.

Production önerisi: eski karşılaştırma için ROUGE-L, anlamsal örtüşme için BERTScore, tutarlılık ve gerçeksellik için G-Eval raporlayın. 50-100 insan etiketli özet ile kalibre edin.

### Adım 4: gerçeklik problemi

Özdürtücü özetler halüsinasyona (hallucination) yatkındır. Öztüretici özetler çok daha düşük halüsinasyon riski taşır çünkü çıktı birebir kaynaktan kopyalanmıştır, ancak kaynak cümleleri bağlam dışına çıkarılmışsa, tarihsel değilse veya düzenden alıntılanmışsa yine de yanıltıcı olabilirler. Bu, production sistemlerinin uyum-komşu içerik için hâlâ öztüretici yöntemleri tercih etmesinin en büyük nedenidir.

Belirtilmesi gereken halüsinasyon türleri:

- **Varlık değişimi (Entity swap).** Kaynak "John Smith" der. Özet "John Brown" der.
- **Sayı kayması (Number drift).** Kaynak "25.000" der. Özet "25 milyon" der.
- **Duygu çevirisi (Polarity flip).** Kaynak "teklifi reddetti" der. Özet "teklifi kabul etti" der.
- **Gerçek uydurma (Fact invention).** Kaynak CEO'yu anmaz. Özet CEO'nun onayladığını söyler.

İşte işe yarar değerlendirme yaklaşımları:

- **FactCC.** Kaynak cümle ile özet cümlesi arasındaki çıkarım (entailment) üzerinde eğitilmiş ikili bir sınıflandırıcı. Gerçek/gerçek değil olarak tahmin eder.
- **QA-tabanlı gerçeklik.** Bir QA modeline, yanıtlarının kaynakta olduğu sorular sorun. Özet farklı yanıtları destekliyorsa, işaretleyin.
- **Varlık düzeyinde F1.** Kaynak ile özet arasındaki adlı varlıkları karşılaştırın. Yalnızca özette bulunan varlıklar şüphelidir.

Kullanıcıya yönelik ve gerçekliğin önemli olduğu her şey için (haberler, tıp, hukuk, finans), öztüretici daha güvenli bir varsayımdır. Özdürtücü bir gerçeklik kontrolü gerektirir.

## Kullan

2026 stacki:

| Kullanım durumu | Önerilen |
|---------|-------------|
| Haber, 3-5 cümle özet, İngilizce | `facebook/bart-large-cnn` |
| Bilimsel makaleler | `google/pegasus-pubmed` veya ayarlanmış bir T5 |
| Çok belgeli, uzun biçim | 32k+ bağlama sahip herhangi bir LLM, promptlanmış |
| Dialog özeti | `philschmid/bart-large-cnn-samsum` |
| Öztüretici, yapısal olarak düşük halüsinasyon riski | TextRank veya `sumy`'in LSA / LexRank'i |

2026'da hesaplama kısıtı olmadığında uzun bağlama sahip LLM'ler genellikle özel modelleri geçer. Tökülme maliyet ve tekrarlanabilirliktir; özel modeller daha tutarlı çıktılar verir.

## Ürün Olarak Kullan

`outputs/skill-summary-picker.md` olarak kaydedin:

```markdown
---
name: summary-picker
description: Pick extractive or abstractive, named library, factuality check.
version: 1.0.0
phase: 5
lesson: 12
tags: [nlp, summarization]
---

Given a task (document type, compliance requirement, length, compute budget), output:

1. Approach. Extractive or abstractive. Explain in one sentence why.
2. Starting model / library. Name it. `sumy.TextRankSummarizer`, `facebook/bart-large-cnn`, `google/pegasus-pubmed`, or an LLM prompt.
3. Evaluation plan. ROUGE-1, ROUGE-2, ROUGE-L (use rouge-score with stemming). Plus factuality check if abstractive.
4. One failure mode to probe. Entity swap is the most common in abstractive news summarization; flag samples where source entities do not appear in summary.

Refuse abstractive summarization for medical, legal, financial, or regulated content without a factuality gate. Flag input over the model's context window as needing chunked map-reduce summarization (not just truncation).
```

#### Açıklama
Bu, bir metin özetleme görevi verildiğinde yaklaşım, model/kütüphane, değerlendirme planı ve hata modu seçimi yapan bir skill tanımıdır.

## Alıştırmalar

1. **Kolay.** 5 haber makalesi üzerinde TextRank çalıştırın. İlk 3 cümleri bir reference özetle karşılaştırın. ROUGE-L ölçün. CNN/DailyMail tarzı makalelerde 30-45 arası ROUGE-L görmelisiniz.
2. **Orta.** Varlık düzeyinde gerçeklik uygulayın: kaynak ve özetten adlı varlıkları çıkarın (spaCy), kaynak varlıklarının özetteki hatırlama (recall) ve özet varlıklarının kaynağa göre precision'ını hesaplayın. Yüksek precision ve düşük hatırlama, güvenli ama kısa demektir; düşük precision halüsinasyonlu varlıklar demektir.
3. **Zor.** BART-large-CNN'i bir LLM (Claude veya GPT-4) ile 50 CNN/DailyMail makalesi üzerinde karşılaştırın. ROUGE-L, gerçeklik (varlık F1'i) ve özet başına maliyeti raporlayın. Her birinin nerede kazandığını belgeleyin.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Öztüretici (Extractive) | Cümleleri seç | Kaynaktan cümleleri birebir döndür. Asla halüsinasyon üretmez. |
| Özdürtücü (Abstractive) | Yeniden yaz | Kaynağa koşullu yeni metin üretebilir. Halüsinasyon yapabilir. |
| ROUGE | Özet metriği | Sistem çıktısı ile reference arasında n-gram / LCS örtüşmesi. |
| TextRank | Graf tabanlı öztüretici | Cümle benzerliği grafiği üzerinde PageRank. |
| Gerçeklik (Factuality) | Doğru mu | Özet iddialarının kaynak tarafından desteklenip desteklenmediği. |
| Halüsinasyon | Uydurma içerik | Kaynağın desteklemediği özet içeriği. |

## İleri Okuma

- [Mihalcea ve Tarau (2004). TextRank: Bringing Order into Texts](https://aclanthology.org/W04-3252/) — öztüretici klasik makale.
- [Lewis et al. (2019). BART: Denoising Sequence-to-Sequence Pre-training](https://arxiv.org/abs/1910.13461) — BART makalesi.
- [Zhang et al. (2019). PEGASUS: Pre-training with Extracted Gap-sentences](https://arxiv.org/abs/1912.08777) — Pegasus ve gap-sentence hedefi.
- [Lin (2004). ROUGE: A Package for Automatic Evaluation of Summaries](https://aclanthology.org/W04-1013/) — ROUGE makalesi.
- [Maynez et al. (2020). On Faithfulness and Factuality in Abstractive Summarization](https://arxiv.org/abs/2005.00661) — gerçeklik manzarası makalesi.