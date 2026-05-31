# Named Entity Recognition (NER)

> İsimleri dışarı çıkarın. Belirsiz sınırlar, iç içe varlıklar ve alan jargonuyla uğraşana kadar kolay görünür.

**Tür:** İnşa
**Diller:** Python
**Ön Koşullar:** Faz 5 · 02 (BoW + TF-IDF), Faz 5 · 03 (Word Embedding'ler)
**Süre:** ~75 dakika

## Problem

"Apple sued Google over its iPhone search deal in the US." Beş varlık: Apple (ORG), Google (ORG), iPhone (PRODUCT), search deal (belki), US (GPE). İyi bir NER sistemi bunların hepsini doğru türlerle çıkarır. Kötüsü iPhone'u kaçırır, Apple meyvesi ile Apple şirketini karıştırır ve "US"ı PERSON olarak etiketler.

NER, her yapılandırılmış çıkarma hattının altında çalışan at midir. Özgeçmiş ayrıştırma, uyumluluk log taraması, tıbbi kayıt anonimleştirme, arama sorgusu anlama, chatbot yanıtları için temellendirme, yasal sözleşme çıkarma. Hiç tam olarak göremezsiniz; her zaman ona bağımlısınızdır.

Bu ders klasik yolu (kural tabanlı, HMM, CRF) moderne (BiLSTM-CRF, sonra transformer'lar) ilerler. Her adım bir öncekinin belirli bir kısıtlamasını çözer. Ders, bu kalıptır.

## Kavram

**BIO etiketleme** (veya BILOU) varlık çıkarmasını bir dizi-etiketleme (sequence-labeling) sorununa dönüştürür. Her token'ı `B-TYPE` (varlığın başlangıcı), `I-TYPE` (varlığın içinde) veya `O` (herhangi bir varlığın dışında) olarak etiketleyin.

```
Apple    B-ORG
sued     O
Google   B-ORG
over     O
its      O
iPhone   B-PRODUCT
search   O
deal     O
in       O
the      O
US       B-GPE
.        O
```

Çok tokenlı varlıklar zincirlenir: `New B-GPE`, `York I-GPE`, `City I-GPE`. BIO'yu anlayan bir model keyfi aralıkları çıkarabilir.

Mimari ilerleme:

- **Kural tabanlı.** Regex + sözlük (gazetteer) aramaları. Bilinen varlıklarda yüksek hassasiyet, yenilerde sıfır kapsama.
- **HMM.** Hidden Markov Model. Etiket verildiğinde token'ın emisyon olasılığı, etiketten etikete geçiş olasılığı. Viterbi çözümü. Etiketlenmiş verilerde eğitilir.
- **CRF.** Conditional Random Field. HMM'a benzer ama ayrıştırıcı (discriminative); bu yüzden keyfi özellikleri (kelime şekli, büyük harf kullanımı, komşu kelimeler) karıştırabilirsiniz. 2026'da düşük kaynaklı konuşlandırmalar için hâlâ klasik üretim at mididir.
- **BiLSTM-CRF.** El yapımı yerine öğrenilmiş özellikler. LSTM cümleyi her iki yönde okur, üzerindeki CRF katmanı tutarlı etiket dizilerini zorunlu kılar.
- **Transformer tabanlı.** Token sınıflandırma başlığı ile BERT'i fine-tune edin. En yüksek hassasiyet. En fazla hesaplama.

## İnşa Et

### Adım 1: BIO etiketleme yardımcıları

```python
def spans_to_bio(tokens, spans):
    labels = ["O"] * len(tokens)
    for start, end, label in spans:
        labels[start] = f"B-{label}"
        for i in range(start + 1, end):
            labels[i] = f"I-{label}"
    return labels


def bio_to_spans(tokens, labels):
    spans = []
    current = None
    for i, label in enumerate(labels):
        if label.startswith("B-"):
            if current:
                spans.append(current)
            current = (i, i + 1, label[2:])
        elif label.startswith("I-") and current and current[2] == label[2:]:
            current = (current[0], i + 1, current[2])
        else:
            if current:
                spans.append(current)
                current = None
    if current:
        spans.append(current)
    return spans
```

```python
>>> tokens = ["Apple", "sued", "Google", "over", "iPhone", "sales", "."]
>>> labels = ["B-ORG", "O", "B-ORG", "O", "B-PRODUCT", "O", "O"]
>>> bio_to_spans(tokens, labels)
[(0, 1, 'ORG'), (2, 3, 'ORG'), (4, 5, 'PRODUCT')]
```

### Adım 2: el yapımı özellikler

Klasik (sinir olmayan) NER için özellikler oyunun kurallarıdır. Yararlı olanlar:

```python
def token_features(token, prev_token, next_token):
    return {
        "lower": token.lower(),
        "is_upper": token.isupper(),
        "is_title": token.istitle(),
        "has_digit": any(c.isdigit() for c in token),
        "suffix_3": token[-3:].lower(),
        "shape": word_shape(token),
        "prev_lower": prev_token.lower() if prev_token else "<BOS>",
        "next_lower": next_token.lower() if next_token else "<EOS>",
    }


def word_shape(word):
    out = []
    for c in word:
        if c.isupper():
            out.append("X")
        elif c.islower():
            out.append("x")
        elif c.isdigit():
            out.append("d")
        else:
            out.append(c)
    return "".join(out)
```

`word_shape("iPhone")` `xXxxxx` döndürür. `word_shape("USA-2024")` `XXX-dddd` döndürür. Büyük harf desenleri özel isimler için yüksek sinyaldir.

### Adım 3: basit kural tabanlı + sözlük taban çizgisi

```python
ORG_GAZETTEER = {"Apple", "Google", "Microsoft", "OpenAI", "Meta", "Amazon", "Netflix"}
GPE_GAZETTEER = {"US", "USA", "UK", "India", "Germany", "France"}
PRODUCT_GAZETTEER = {"iPhone", "Android", "Windows", "ChatGPT", "Claude"}


def rule_based_ner(tokens):
    labels = []
    for token in tokens:
        if token in ORG_GAZETTEER:
            labels.append("B-ORG")
        elif token in GPE_GAZETTEER:
            labels.append("B-GPE")
        elif token in PRODUCT_GAZETTEER:
            labels.append("B-PRODUCT")
        else:
            labels.append("O")
    return labels
```

Üretim sözlükleri (gazetteers) Wikipedia ve DBpedia'dan kazılmış milyonlarca girişe sahiptir. Kapsama iyidir. Ayırt etme (`Apple` şirketi vs meyve) berbattır. Bu yüzden istatistiksel modeller kazandı.

### Adım 4: CRF adımı (taslak, tam uygulama değil)

50 satırda sıfırdan tam CRF, olasılık teorisi temelleri olmadan aydınlatıcı değildir. Bunun yerine `sklearn-crfsuite` kullanın:

```python
import sklearn_crfsuite

def to_features(tokens):
    out = []
    for i, tok in enumerate(tokens):
        prev = tokens[i - 1] if i > 0 else ""
        nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
        out.append({
            "word.lower()": tok.lower(),
            "word.isupper()": tok.isupper(),
            "word.istitle()": tok.istitle(),
            "word.isdigit()": tok.isdigit(),
            "word.suffix3": tok[-3:].lower(),
            "word.shape": word_shape(tok),
            "prev.word.lower()": prev.lower(),
            "next.word.lower()": nxt.lower(),
            "BOS": i == 0,
            "EOS": i == len(tokens) - 1,
        })
    return out


crf = sklearn_crfsuite.CRF(algorithm="lbfgs", c1=0.1, c2=0.1, max_iterations=100, all_possible_transitions=True)
X_train = [to_features(s) for s in sentences_tokenized]
crf.fit(X_train, bio_labels_train)
```

`c1` ve `c2` L1 ve L2 düzenlileştirmesidir. `all_possible_transitions=True` modelin yasağı dizilerin (örneğin `O` sonrası `I-ORG`) düşük olasılıklı olduğunu öğrenmesini sağlar; bu, CRF'in BIO tutarlılığını siz kural koymadan zorunlu kılma biçimidir.

### Adım 5: BiLSTM-CRF'in ekledikleri

Özellikler öğrenilmiş hale gelir. Girdiler: token embedding'leri (GloVe veya fastText). LSTM soldan sağa ve sağdan sola okur. Birleştirilmiş gizli durumlar bir CRF çıkış katmanından geçer. CRF hâlâ etiket-dizisi tutarlılığını zorunlu kılar; LSTM el yapımı özellikleri öğrenilenlerle değiştirir.

```python
import torch
import torch.nn as nn


class BiLSTM_CRF_Head(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, n_labels):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, bidirectional=True, batch_first=True)
        self.fc = nn.Linear(hidden_dim * 2, n_labels)

    def forward(self, token_ids):
        e = self.embed(token_ids)
        h, _ = self.lstm(e)
        emissions = self.fc(h)
        return emissions
```

CRF katmanı için `torchcrf.CRF` kullanın (pip install pytorch-crf). El yapımı CRF'e göre kazanç, on binlerce etiketlenmiş cümleniz olmadıkça beklediğinizden daha küçüktür.

## Kullan

spaCy, üretim kalitesinde NER'i kutudan çıktığı haliyle sunar.

```python
import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("Apple sued Google over its iPhone search deal in the US.")
for ent in doc.ents:
    print(f"{ent.text:20s} {ent.label_}")
```

```
Apple                ORG
Google               ORG
iPhone               ORG
US                   GPE
```

`iPhone`'un `ORG` olarak etiketlendiğine dikkat edin, `PRODUCT` olarak değil — spaCy'in küçük modelinin ürün varlığı kapsaması zayıftır. Büyük model (`en_core_web_lg`) daha iyidir. Transformer modeli (`en_core_web_trf`) daha da iyidir.

BERT tabanlı NER için Hugging Face:

```python
from transformers import pipeline

ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
print(ner("Apple sued Google over its iPhone in the US."))
```

```
[{'entity_group': 'ORG', 'word': 'Apple', ...},
 {'entity_group': 'ORG', 'word': 'Google', ...},
 {'entity_group': 'MISC', 'word': 'iPhone', ...},
 {'entity_group': 'LOC', 'word': 'US', ...}]
```

`aggregation_strategy="simple"` bitişik B-X, I-X token'larını bir aralığa birleştirir. Olmadan, token düzeyinde etiketlersiniz ve kendiniz birleştirmeniz gerekir.

### LLM tabanlı NER (2026 seçeneği)

Sıfır atımlı (zero-shot) ve az örnekli (few-shot) LLM NER, artık birçok alanda fine-tune edilmiş modellerle rekabet eder durumdadır ve etiketli verinin scarce olduğu durumlarda dramatik olarak daha iyidir.

- **Sıfır atımlı prompting.** LLM'e bir varlık türü listesi ve örnek bir şema verin. JSON çıktısı isteyin. Kutudan çıktığı haliyle çalışır; yeni alanlarda hassasiyet orta düzeydedir.
- **Çok Aşamalı (multi-step) prompting.** Görevi aday çıkarma → anlam açıklama → karar → yeniden kontrol olarak ayrıştırın. Çok aşamalı bir istem (tek atımlı değil) biyomedikal NER'de hassasiyeti önemli ölçüde artırır. Aynı kalıp hukuki, finansal ve bilimsel alanlar için de çalışır.
- **RAG ile dinamik prompting.** Her çıkarım çağrısı için küçük bir etiketli tohum kümesinden en benzer etiketli örnekleri getirin; few-shot istemini dinamik olarak oluşturun. 2026 benchmark'larında bu, statik prompting'e kıyasla GPT-4 biyomedikal NER F1'ini %11-12 artırır.
- **Varlık türü başına ayrıştırma.** Uzun belgeler için, tüm varlık türlerini tek bir çağırıda çıkaran tek bir çağrı, uzunluk arttıkça duyarlılık (recall) kaybeder. Varlık türü başına bir çıkarma çalıştırın. Daha yüksek çıkarım maliyeti, önemli ölçüde daha yüksek hassasiyet. Bu, klinik notlar ve yasal sözleşmeler için standart kalıptır.

2026 itibarıyla üretim önerisi: eğitim verisi toplamadan önce bir LLM sıfır atımlı taban çizgisiyle başlayın. Genellikle F1 yeterince iyidir ve fine-tune etmeniz gerekmez.

### Klasik NER'in hâlâ kazandığı durumlar

LLM'ler mevcut olsa bile, klasik NER kazanır:

- Gecikme bütçesi 50 ms altında ise.
- On binlerce etiketli örneğiniz varsa ve %98+ F1'e ihtiyacınız varsa.
- Alan, önceden eğitilmiş bir CRF'in veya BiLSTM'in iyi transfer ettiği stabil bir ontolojiye sahipse.
- Düzenleyici kısıtlamalar, tesis içi, üretken olmayan bir model gerektiriyorsa.

### Dağıldığı durumlar

- **Alan kayması.** CoNLL'de eğitilmiş NER yasal sözleşmelerde bir sözlükten daha kötü performans gösterir. Kendi alanınızda fine-tune edin.
- **İç içe varlıklar.** "Bank of America Tower" aynı anda bir ORG ve bir FACILITY'dir. Standart BIO örtüşen aralıkları temsil edemez. İç içe NER (çoklu geçiş veya aralık tabanlı modeller) gerekir.
- **Uzun varlıklar.** "United States Federal Deposit Insurance Corporation." Token düzeyinde modeller bunu bazen böler. `aggregation_strategy` veya son-işleme kullanın.
- **Seyrek türler.** Tıbbi NER etiketleri: DRUG_BRAND, ADVERSE_EVENT, DOSE. Genel amaçlı modellerin haberi yoktur. Scispacy ve BioBERT orada başlangıç noktalarıdır.

## Ürün Haline Getir

`outputs/skill-ner-picker.md` olarak kaydedin:

```markdown
---
name: ner-picker
description: Belirli bir çıkarma görevi için doğru NER yaklaşımını seçin.
version: 1.0.0
phase: 5
lesson: 06
tags: [nlp, ner, extraction]
---

Bir görev tanımı (alan, etiket kümesi, dil, gecikme, veri hacmi) verildiğinde çıktı olarak:

1. Yaklaşım. Kural tabanlı + sözlük, CRF, BiLSTM-CRF veya transformer fine-tune.
2. Başlangıç modeli. Adlandırın (spaCy model kimliği, Hugging Face kontrol noktası kimliği veya "özel, sıfırdan eğitilmiş").
3. Etiketleme stratejisi. BIO, BILOU veya aralık tabanlı. Bir cümlede gerekçelendirin.
4. Değerlendirme. `seqeval` kullanın. Her zaman varlık düzeyinde F1 raporlayın (token düzeyinde değil).

500'den az etiketli örnek için transformer fine-tune önermeyi reddedin, kullanıcı zaten bir önceden eğitilmiş alan modeline sahip değilse. İç içe varlıkları aralık tabanlı veya çoklu geçiş modelleri gerektiriyor olarak işaretleyin. Kullanıcı "üretim ölçeği"nden bahsediyorsa ve etiketler CoNLL-2003 ile aynıysa bir sözlük denetimi isteyin.
```

## Alıştırmalar

1. **Kolay.** `bio_to_spans`'ı (`spans_to_bio`'nun tersi) uygulayın ve 10 cümle üzerinde çift yönlü tutarlılık doğrulaması yapın.
2. **Orta.** sklearn-crfsuite CRF'ini CoNLL-2003 İngilizce NER veri kümesi üzerinde eğitin. `seqeval` kullanarak varlık başına F1 raporlayın. Tipik sonuç: ~84 F1.
3. **Zor.** Alan-spesifik bir NER veri kümesi (tıbbi, hukuki veya finansal) üzerinde `distilbert-base-cased` fine-tune edin. spaCy küçük modeliyle karşılaştırın. Veri sızıntısı kontrollerini belgeleyin ve sizi şaşırtan şeyleri yazın.

## Anahtar Terimler

| Terim | İnsanların Söylediği | Gerçekte Ne Anlama Gelir |
|------|-----------------|-----------------------|
| NER | İsimleri çıkarma | Token aralıklarını türlerle etiketleme (PERSON, ORG, GPE, DATE, ...). |
| BIO | Etiketleme şeması | `B-X` başlatır, `I-X` devam eder, `O` dışarıda. |
| BILOU | Daha iyi BIO | Daha temiz sınırlar için `L-X` (son), `U-X` (birim) ekler. |
| CRF | Yapılandırılmış sınıflandırıcı | Yalnızca emisyonları değil, etiketler arasındaki geçişleri modellemer. Geçerli dizileri zorunlu kılar. |
| İç içe NER | Örtüşen varlıklar | Bir aralık, onun bir alt aralığından farklı bir varlıktır. BIO bunu ifade edemez. |
| Varlık düzeyinde F1 | Düzgün NER metriği | Tahmin edilen aralık gerçek aralıkla tam olarak eşleşmelidir. Token düzeyinde F1 hassasiyeti olduğundan fazla gösterir. |

## İleri Okuma

- [Lample et al. (2016). Neural Architectures for Named Entity Recognition](https://arxiv.org/abs/1603.01360) — BiLSTM-CRF makalesi. Kanonik.
- [Devlin et al. (2018). BERT: Pre-training of Deep Bidirectional Transformers](https://arxiv.org/abs/1810.04805) — standart haline gelen token sınıflandırma kalıbını tanıtır.
- [spaCy linguistic features — named entities](https://spacy.io/usage/linguistic-features#named-entities) — `Doc.ents` ve `Span` üzerindeki her nitelik için pratik referans.
- [seqeval](https://github.com/chakki-works/seqeval) — doğru metrik kütüphanesi. Her zaman kullanın.
