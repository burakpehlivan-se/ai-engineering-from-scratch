# Çok Dilli NLP

> Bir model, 100+ dil, çoğunun sıfır eğitim verisi. Çapraz dil transferi (cross-lingual transfer), 2020'lerin pratik mucizesidir.

**Tür:** Öğren
**Diller:** Python
**Ön koşullar:** Faz 5 · 04 (GloVe, FastText, Subword), Faz 5 · 11 (Makine Çevirisi)
**Süre:** ~45 dakika

## Problem

İngilizce milyarlarca etiketli örneğe sahiptir. Urduca birkaç bine sahiptir. Maithili nerdeyse hiç yoktur. Küresel bir kitleye hizmet veren her pratik NLP sistemi, görev-specific eğitim verisinin olmadığı dillerin uzun kuyruğunda (long tail) çalışmak zorundadır.

Çok dilli modeller (multilingual models) birçok dili aynı anda eğiterek bunu çözer. Paylaşılan temsil (shared representation), modelin yüksek kaynaklı dillerde (high-resource) öğrendiği becerileri düşük kaynaklı dillere (low-resource) transfer etmesini sağlar. İngilizce duygu analizi üzerinde fine-tune edin ve Urduca üzerinde şaşırtıcı derecede iyi duygu tahminleri üretsin. Sıfır-atışlı çapraz dil transferi (zero-shot cross-lingual transfer) budur ve NLP'nin dünyaya nasıl ulaştığını yeniden şekillendirmiştir.

Bu ders bedelleri, klasik modelleri ve multilingual çalışmaya yeni başlayan ekipleri thường karşılaştığı tek kararı belirtir: transfer için kaynak dil seçimi.

## Kavram

![Çok dilli embedding uzayı üzerinden çapraz dil transferi](../assets/multilingual.svg)

**Paylaşılan sözlük.** Çok dilli modeller, tüm hedef dillerin metinleri üzerinde eğitilmiş bir SentencePiece veya WordPiece tokenizer (tokenizer) kullanır. Sözlük paylaşılır: aynı subword birimi ilişkili diller arasında aynı morfemi temsil eder. İngilizce ve İtalyanca'daki `anti-` aynı token'ı alır.

**Paylaşılan temsil.** Birçok dil üzerinde maskeli dil modelleme (masked language modeling) ile önceden eğitilmiş bir transformer, farklı dillerdeki anlamsal olarak benzer cümlelerin benzer gizli durumlar (hidden states) ürettiğini öğrenir. mBERT, XLM-R ve NLLB hepsi bunu sergiler. İngilizce "kedi" için embedding'ler Fransızca "chat" ve İspanyolca "gato" yakınında kümelere ve aynı cümle embedding'leri de öyle.

**Sıfır-atışlı transfer.** Modeli bir dilde (genellikle İngilizce) etiketli veri üzerinde fine-tune edin. Çıkarımda (inference), modelin desteklediği herhangi bir autre dilde çalıştırın. Hedef dil etiketi gerekmez. Sonuçlar tipolojik olarak ilişkili diller için güçlü, uzak diller için daha zayıftır.

**Az-atışlı fine-tuning (few-shot fine-tuning).** Hedef dilde 100-500 etiketli örnek ekleyin. Sınıflandırma görevlerinde doğruluk İngilizce baseline'ın %95-98'ine sıçrar. Bu, çok dilli NLP'deki en etkili maliyet-hesaplı çabadır.

## Modeller

| Model | Yıl | Kapsam | Notlar |
|-------|------|----------|-------|
| mBERT | 2018 | 104 dil | Wikipedia üzerinde eğitilmiş. İlk pratik çok dilli LM. Düşük kaynaklı dillerde zayıf. |
| XLM-R | 2019 | 100 dil | CommonCrawl üzerinde eğitilmiş (Wikipedia'dan çok daha büyük). Çapraz dil baseline'ını belirler. Base 270M, Large 550M. |
| XLM-V | 2023 | 100 dil | 1M token sözlüklü XLM-R (250k'ya kıyasla). Düşük kaynaklı dillerde daha iyi. |
| mT5 | 2020 | 101 dil | Çok dilli üretim için T5 mimarisi. |
| NLLB-200 | 2022 | 200 dil | Meta'nın çeviri modeli; 55 düşük kaynaklı dil dahil. |
| BLOOM | 2022 | 46 dil + 13 programlama dili | Açık 176B LLM, çok dilli eğitilmiş. |
| Aya-23 | 2024 | 23 dil | Cohere'nin çok dilli LLM'i. Arapça, Hintçe, Svahili'de güçlü. |

Kullanım durumuna göre seçin. Sınıflandırma için XLM-R-base makul bir varsayılan olarak iyi çalışır. Üretim görevleri çeviriye göre mT5 veya NLLB gerektirir. LLM tarzı çalışma Aya-23 veya açık çok dilli promptlama ile Claude ile eşleştirilir.

## Kaynak dil kararı (2026 araştırması)

Çoğu ekip fine-tuning kaynağı olarak İngilizce'yi varsayar. Son araştırmalar (2026) bunun genellikle yanlış olduğunu gösteriyor.

Dil benzerliği, ham corpus boyutundan ziyade transfer kalitesini daha iyi tahmin eder. Slav hedefleri için Almanca veya Rusça genellikle İngilizce'yi yener. Hint hedefleri için Hintçe genellikle İngilizce'yi yener. **qWALS** benzerlik metriği (2026, Dünya Dil Yapıları Atlası özelliklerine dayalı) bunu nicelleştirir. **LANGRANK** (Lin ve diğerleri, ACL 2019), dilbilimsel benzerlik, corpus boyutu ve genetik akrabalığın birleşiminden aday kaynak dillerini sıralayan ayrı bir erken yöntemdir.

Pratik kural: hedef dilinizin tipolojik olarak yakın bir yüksek kaynaklı akrabası varsa, önce onun üzerinde fine-tune edin, ardından İngilizce fine-tune ile karşılaştırın.

## İnşa Et

### Adım 1: sıfır-atışlı çapraz dil sınıflandırması

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tok = AutoTokenizer.from_pretrained("joeddav/xlm-roberta-large-xnli")
model = AutoModelForSequenceClassification.from_pretrained("joeddav/xlm-roberta-large-xnli")


def classify(text, candidate_labels, hypothesis_template="This text is about {}."):
    scores = {}
    for label in candidate_labels:
        hypothesis = hypothesis_template.format(label)
        inputs = tok(text, hypothesis, return_tensors="pt", truncation=True)
        with torch.no_grad():
            logits = model(**inputs).logits[0]
        entail_score = torch.softmax(logits, dim=-1)[2].item()
        scores[label] = entail_score
    return dict(sorted(scores.items(), key=lambda x: -x[1]))


print(classify("I love this product!", ["positive", "negative", "neutral"]))
print(classify("मुझे यह उत्पाद पसंद है!", ["positive", "negative", "neutral"]))
print(classify("J'adore ce produit !", ["positive", "negative", "neutral"]))
```

#### Açıklama
Bir model, üç dil, aynı API. XLM-R, NLI verisi üzerinde eğitilmiş ve çıkarım hilesiyle sınıflandırmaya iyi transfer olur. Hipotez şablonu, her aday etiket için bir "metin hakkında" cümlesi oluşturur ve modelin çıkarım (entailment) skorunu hesaplar.

### Adım 2: çok dilli embedding uzayı

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

pairs = [
    ("The cat is sleeping.", "Le chat dort."),
    ("The cat is sleeping.", "El gato está durmiendo."),
    ("The cat is sleeping.", "Die Katze schläft."),
    ("The cat is sleeping.", "The dog is barking."),
]

for eng, other in pairs:
    emb_eng = model.encode([eng], normalize_embeddings=True)[0]
    emb_other = model.encode([other], normalize_embeddings=True)[0]
    sim = float(np.dot(emb_eng, emb_other))
    print(f"  {eng!r} <-> {other!r}: cos={sim:.3f}")
```

#### Açıklama
Çeviriler embedding uzayında yakın yere düşer. Farklı bir İngilizce cümle daha uzağa düşer. Bu, çapraz dil retrieval, kümeleme ve benzerliğin çalışmasını sağlayan şeydir.

### Adım 3: az-atışlı fine-tuning stratejisi

```python
from transformers import TrainingArguments, Trainer
from datasets import Dataset


def few_shot_finetune(base_model, base_tokenizer, examples):
    ds = Dataset.from_list(examples)

    def tokenize_fn(ex):
        out = base_tokenizer(ex["text"], truncation=True, max_length=128)
        out["labels"] = ex["label"]
        return out

    ds = ds.map(tokenize_fn)
    args = TrainingArguments(
        output_dir="out",
        per_device_train_batch_size=8,
        num_train_epochs=5,
        learning_rate=2e-5,
        save_strategy="no",
    )
    trainer = Trainer(model=base_model, args=args, train_dataset=ds)
    trainer.train()
    return base_model
```

#### Açıklama
100-500 hedef dil örneği için `num_train_epochs=5` ve `learning_rate=2e-5` güvenli varsayılanlardır. Daha yüksek öğrenme oranları çok dilli hizalamayı çökertir ve yalnızca İngilizce bir model elde edersiniz.

## Çalışan değerlendirme

- **Ayrılmış setlerde dil bazında doğruluk.** Toplu değil. Toplama, uzun kuyruğu gizler.
- **Tek dilli baseline'a karşı benchmark.** Yeterli verisi olan diller için, sıfırdan eğitilmiş tek dilli model bazen çok dilliyi yener. Test edin.
- **Varlık düzeyinde testler.** Hedef dildeki adlandırılmış varlıklar (named entities). Çok dilli modeller Latin'den uzak scriptler için genellikle zayıf tokenizasyona sahiptir.
- **Çapraz dil tutarlılığı.** İki dildeki aynı anlam aynı tahmini üretmelidir. Farkı ölçün.

## Kullan

2026 stacki:

| Görev | Önerilen |
|-----|-------------|
| Sınıflandırma, 100 dil | XLM-R-base (~270M) fine-tune edilmiş |
| Sıfır-atışlı metin sınıflandırması | `joeddav/xlm-roberta-large-xnli` |
| Çok dilli cümle embedding'leri | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| Çeviri, 200 dil | `facebook/nllb-200-distilled-600M` (ders 11'e bakın) |
| Üretici çok dilli | Claude, GPT-4, Aya-23, mT5-XXL |
| Düşük kaynaklı dil NLP'si | XLM-V veya ilgili yüksek kaynaklı dil üzerinde alan-specific fine-tune |

Performans önemliyse her zaman hedef dilde fine-tuning için bütçe ayırın. Sıfır-atışlı bir başlangıç noktasıdır, nihai cevap değildir.

### Tokenizasyon vergisi (düşük kaynaklı dillerde neler yanlış gider)

Çok dilli modeller tüm dilleri arasında tek bir tokenizer paylaşır. Bu sözlük İngilizce, Fransızca, İspanyolca, Çince, Almanca'nın hakim olduğu bir corpus üzerinde eğitilir. Hakim kümenin dışındaki her dil için üç vergi sessizce birikir:

- **Verimlilik vergisi (fertility tax).** Düşük kaynaklı dil metni, İngilizce'den çok daha fazla token'a bölünür. Bir Hintçe cümle, eşdeğer bir İngilizce cümlenin 3-5 katı token gerektirebilir. Bu 3-5 kat, bağlam penceresini, eğitim verimliliğini ve gecikme süresini yer.
- **Varyant kurtarma vergisi (variant recovery tax).** Her yazım hatası, diakritik varyant, Unicode normalleştirme uyuşmazlığı veya büyük/küçük harf varyasyonu, embedding uzayında soğuk başlangıçlı ilgisiz bir dizi haline gelir. Model, bir ana dil konuşanı için bariz olan yazışma karşılıklarını öğrenemez.
- **Kapasite sızmma vergisi (capacity spillover tax).** 1 ve 2 numaralı vergiler bağlam pozisyonlarını, katman derinliğini ve embedding boyutlarını tüketir. Gerçek çıkarsama için kalan, aynı modelden yüksek kaynaklı dilin aldığından sistematik olarak daha küçüktür.

Pratik semptom: modeliniz Hintçe üzerinde normal eğitilir, kayıp eğrisi doğru görünür, eval perplexity makul görünür ve production çıktıları ince wrongdır. Morfoloji cümle ortasında çöker. Nadir çekimler kurtarılamaz hale gelir. **Kırık bir tokenizer'dan veri ölçeklendirmesiyle çıkamazsınız.**

Hafifletme: hedef diliniz için iyi kapsama sahip bir tokenizer seçin (XLM-V'nin 1M token sözlüğü doğrudan bir çözümdür); eğitmeden önce ayrılmış hedef metin üzerinde tokenizasyon verimliliğini doğrulayın; gerçekten uzun kuyruklu scriptler için hiçbir şeyin OOV olmaması için byte-level fallback (SentencePiece `byte_fallback=True`, GPT-2 tarzı byte-level BPE) kullanın.

## Ürün Olarak Kullan

`outputs/skill-multilingual-picker.md` olarak kaydedin:

```markdown
---
name: multilingual-picker
description: Pick source language, target model, and evaluation plan for a multilingual NLP task.
version: 1.0.0
phase: 5
lesson: 18
tags: [nlp, multilingual, cross-lingual]
---

Given requirements (target languages, task type, available labeled data per language), output:

1. Source language for fine-tuning. Default English; check LANGRANK or qWALS if target language has a typologically close high-resource language.
2. Base model. XLM-R (classification), mT5 (generation), NLLB (translation), Aya-23 (generative LLM).
3. Few-shot budget. Start with 100-500 target-language examples if available. Zero-shot only if labeling is infeasible.
4. Evaluation plan. Per-language accuracy (not aggregate), cross-lingual consistency, entity-level F1 on non-Latin scripts.

Refuse to ship a multilingual model without per-language evaluation — aggregate metrics hide long-tail failures. Flag scripts with low tokenization coverage (Amharic, Tigrinya, many African languages) as needing a model with byte-fallback (SentencePiece with byte_fallback=True, or byte-level tokenizer like GPT-2).
```

#### Açıklama
Verilen gereksinimlerde kaynak dil, hedef model ve değerlendirme planı seçen bir skill tanımıdır.

## Alıştırmalar

1. **Kolay.** Sıfır-atışlı sınıflandırma pipeline'ını İngilizce, Fransızca, Hintçe ve Arapça'da dil başına 10 cümle çalıştırın. Her birinde doğruluk raporlayın. Güçlü Fransızca, makul Hintçe, değişken Arapça görmelisiniz.
2. **Orta.** `paraphrase-multilingual-MiniLM-L12-v2`'yi küçük bir karışık dil corpus'u üzerinde çapraz dil getirici (retriever) olarak kullanın. İngilizce sorgulayın, herhangi bir dilde belgeleri getirin. Recall@5'i ölçün.
3. **Zor.** Bir Hintçe sınıflandırma görevi için İngilizce-kaynak ve Hintçe-kaynak fine-tuning'i karşılaştırın. Her iki rejim altında few-shot fine-tuning için 500 hedef dil örneği kullanın. Hangi kaynağın daha iyi Hintçe doğruluğu ürettiğini ve ne kadar farkla olduğunu raporlayın. Bu, LANGRANK tezinin minyatürüdür.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Çok dilli model | Bir model, birçok dil | Diller arasında paylaşılan sözlük ve parametreler. |
| Çapraz dil transferi | Bir dilde eğit, diğerinde çalıştır | Kaynakta fine-tune et, hedef dilde hedef dil etiketi olmadan değerlendir. |
| Sıfır-atışlı (Zero-shot) | Hedef dil etiketi yok | Hedef dilde fine-tune etmeden transfer. |
| Az-atışlı (Few-shot) | Küçük hedef etiketleri | Fine-tuning için kullanılan 100-500 hedef dil örneği. |
| mBERT | İlk çok dilli LM | Wikipedia üzerinde önceden eğitilmiş 104 dil BERT'i. |
| XLM-R | Standart çapraz dil baseline'ı | CommonCrawl üzerinde önceden eğitilmiş 100 dil RoBERTa'sı. |
| NLLB | Meta'nın 200 dil MT'si | No Language Left Behind. 55 düşük kaynaklı dil dahil. |

## İleri Okuma

- [Conneau et al. (2019). Unsupervised Cross-lingual Representation Learning at Scale](https://arxiv.org/abs/1911.02116) — XLM-R makalesi.
- [Pires, Schlinger, Garrette (2019). How Multilingual is Multilingual BERT?](https://arxiv.org/abs/1906.01502) — çapraz dil transfer araştırma hattını başlatan analiz makalesi.
- [Costa-jussà et al. (2022). No Language Left Behind](https://arxiv.org/abs/2207.04672) — NLLB-200 makalesi.
- [Üstün et al. (2024). Aya Model: An Instruction Finetuned Open-Access Multilingual Language Model](https://arxiv.org/abs/2402.07827) — Aya, Cohere'nin çok dilli LLM'i.
- [Language Similarity Predicts Cross-Lingual Transfer Learning Performance (2026)](https://www.mdpi.com/2504-4990/8/3/65) — qWALS / LANGRANK kaynak dil makalesi.
