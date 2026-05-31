# Doğal Dil Çıkarımı — Metinsel Zorunluluk

> "t, h'yi zorunlu kılıyor" ifadesi, t'yi okuyan bir insanın h'nin doğru olacağına varması anlamına gelir. NLI, zorunluluk / çelişki / nötr tahmin görevidir. Yüzeyde sıkıcıdır, üretimde kritik görev üstlenir.

**Tür:** Öğren
**Diller:** Python
**Önkoşullar:** Faz 5 · 05 (Duygu Analizi), Faz 5 · 13 (Soru Cevaplama)
**Süre:** ~60 dakika

## Sorun

Bir özetleyici oluşturdunuz. Özet üretti. Bu özette bir halüsünasyon (sanrılı üretim) olmadığınu nasıl anlarsınız?

Bir sohbet botu oluşturdunuz. "Evet" diye cevap verdi. Bu cevabın getirilen parçacık tarafından desteklendiğini nasıl anlarsınız?

10.000 haber makalesini konuya göre sınıflandırmanız gerekiyor. Eğitim etiketiniz yok. Bir modeli yeniden kullanabilir miyiz?

Üç sorun da Doğal Dil Çıkarımı'na (Natural Language Inference - NLI) indirgenir. NLI şunu sorar: bir ön koşul (premise) `t` ve bir hipotez `h` verildiğinde, `h`, `t` tarafından zorunlu kılınmış mı, çelişiyor mu, yoksa nötr mü (ilgisiz mi)?

- **Halüsünasyon kontrolü:** `t` = kaynak belge, `h` = özet iddiası. Zorunlu kılınmama = halüsünasyon.
- **Temellendirilmiş Soru Cevaplama:** `t` = getirilen parçacık, `h` = üretilen cevap. Zorunlu kılınmama = uydurma.
- **Sıfır atıflı sınıflandırma (Zero-shot classification):** `t` = belge, `h` = sözelleştirilmiş etiket ("Bu sporla ilgili"). Zorunlu kılınma = tahmin edilen etiket.

Bir görev, üç üretim kullanımı. Bu yüzden her RAG değerlendirme çerçevesi (framework) alt kısımda bir NLI modeli çalıştırır.

## Kavram

![NLI: üç yönlü sınıflandırma, ön koşul vs hipotez](../assets/nli.svg)

**Üç etiket.**

- **Zorunlu Kılınma (Entailment).** `t` → `h`. "Kedi halının üzerinde" ifadesi "Bir kedi var" ifadesini zorunlu kılar.
- **Çelişki (Contradiction).** `t` → ¬`h`. "Kedi halının üzerinde" ifadesi "Kedi yok" ifadesiyle çelişir.
- **Neötr (Neutral).** Her iki yönde de çıkarım yok. "Kedi halının üzerinde" ifadesi "Kedi aç" ifadesine karşı nötrdür.

**Mantıksal zorunluluk değil.** NLI, *doğal dil* çıkarımıdır — tipik bir okuyucunun çıkaracağı anlam, katı mantık değil. "John köpeğini yürüdü" ifadesi NLI'da "John'un bir köpeği var" anlamını zorunlu kılar, ancak katı birinci derece mantık (first-order logic) bunu ancak sahiplik aksiyomatize edilirse kabul eder.

**Veri setleri.**

- **SNLI** (2015). 570 bin insan etiketli çift, görüntü açıklamaları ön koşul olarak kullanılmış. Dar alan.
- **MultiNLI** (2017). 10 türde 433 bin çift. 2026'da standart eğitim kümesi.
- **ANLI** (2019. Zorlamalı NLI (Adversarial NLI). İnsanlar mevcut modelleri kırmak için özel örnekler yazdı. Daha zor.
- **DocNLI, ConTRoL** (2020–21). Belge uzunluğunda ön koşullar. Çoklu adım ve uzun menzilli çıkarımı test eder.

**Mimari.** Bir transformer encoder'ı (BERT, RoBERTa, DeBERTa) `[CLS] ön_koşul [SEP] hipotez [SEP]` biçiminde okur. `[CLS]` temsili 3 yönlü softmax'a beslenir. MNLI üzerinde eğitilir, ayrı tutulan (held-out) benchmark'larda değerlendirilir, dağılım içi çiftlerde %90'ın üzerinde doğruluk elde edilir.

**NLI ile sıfır atıflı sınıflandırma.** Bir belge ve aday etiketler verildiğinde, her etiketi bir hipoteze dönüştürün ("Bu metin sporla ilgili"). Her biri için zorunlu kılma olasılığını hesaplayın. Maksimum olanı seçin. Bu, Hugging Face'in `zero-shot-classification` pipeline'ının arkasındaki mekanizmadır.

## İnşa Et

### Adım 1: önceden eğitilmiş bir NLI modelini çalıştırın

```python
from transformers import pipeline

nli = pipeline("text-classification",
               model="facebook/bart-large-mnli",
               top_k=None)  # return all labels; replaces deprecated return_all_scores=True

premise = "The cat is sleeping on the couch."
hypothesis = "There is a cat in the room."

result = nli({"text": premise, "text_pair": hypothesis})[0]
print(result)
# [{'label': 'entailment', 'score': 0.97},
#  {'label': 'neutral', 'score': 0.02},
#  {'label': 'contradiction', 'score': 0.01}]
```

#### Açıklama
Bu kod, önceden eğitilmiş bir NLI modelini yükler ve bir ön koşul ile hipotez çifti arasındaki ilişkiyi tahmin eder. `facebook/bart-large-mnli` modeli, three-way sınıflandırma yaparak zorunlu kılma, nötr ve çelişki olasılıklarını döndürür.

Üretim için NLI'da `facebook/bart-large-mnli` ve `microsoft/deberta-v3-large-mnli` açık kaynaklı varsayılan modellerdir. DeBERTa-v3 liderlik tablolarında üst sıradadır.

### Adım 2: sıfır atıflı sınıflandırma

```python
zs = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

text = "The stock market rallied after the central bank cut interest rates."
labels = ["finance", "sports", "politics", "technology"]

result = zs(text, candidate_labels=labels)
print(result)
# {'labels': ['finance', 'politics', 'technology', 'sports'],
#  'scores': [0.92, 0.05, 0.02, 0.01]}
```

#### Açıklama
Bu kod, sıfır atıflı sınıflandırma yapar. Metni aday etiketlerle karşılaştırır ve her etiket için bir olasılık skoru üretir. Eğitim verisi gerekmez, ince ayar (fine-tuning) gerekmez.

Varsayılan şablon "This example is about {label}." şeklindedir. `hypothesis_template` ile özelleştirilebilir. Eğitim verisi gerekmez. İnce ayar gerekmez. Kutudan çıktığı gibi çalışır.

### Adım 3: RAG için sadakat kontrolü

```python
def is_faithful(answer, context, threshold=0.5):
    result = nli({"text": context, "text_pair": answer})[0]
    entail = next(s for s in result if s["label"] == "entailment")
    return entail["score"] > threshold
```

#### Açıklama
Bu fonksiyon, üretilen cevabın getirilen bağlam tarafından desteklenip desteklenmediğini kontrol eder. Zorunlu kılma olasılığı eşik değerinden yüksekse cevap sadıktır.

Bu, RAGAS sadakat (faithfulness) ölçümünün özüdür. Üretilen cevabı atomik iddialara bölün. Her iddiayı getirilen bağlamla karşılaştırın. Zorunlu kılınanların oranını raporlayın.

### Adım 4: el yapımı NLI sınıflandırıcısı (kavramsal)

Tam bir stdlib-only uygulama için `code/main.py` dosyasına bakın: ön koşul ve hipopez, sözcük örtüşmesi (lexical overlap) ve olumsuzluk tespiti yoluyla karşılaştırılır. Transformer modelleriyle rekabet edemez — ancak görevin biçimini gösterir: iki metin girilir, 3 yönlü etiket çıkartılır, kayıp (loss) = `{entail, contradict, neutral}` üzerinde çapraz entropi (cross-entropy).

## Tuzaklar

- **Hipoteze-dayalı kısayollar.** Modeller SNLI'da hipotezden tek başına %60 civarında etiket tahmin edebilir çünkü "not", "nobody", "never" gibi sözcükler çelişkiyle korelelidir. Etiket sızıntısını tespit etmek için güçlü bir temel (baseline).
- **Sözcük örtüşmesi sezgisel yaklaşımı.** Alt dizi sezgisel yaklaşımı (subsequence heuristic) SNLI'dan geçer ancak HANS/ANLI'da başarısız olur. Zorlamalı benchmark'ları kullanın.
- **Belge uzunluğunda bozulma.** Tek cümlelik NLI modelleri belge uzunluğundaki ön koşullarda 20+ F1 puanı düşüş gösterir. Uzun bağlam için DocNLI ile eğitilmiş modeller kullanın.
- **Sıfır atıflı şablon duyarlılığı.** "This example is about {label}" vs "{label}" vs "The topic is {label}" doğrulukta 10+ puan oynayabilir. Şablonu ayarlayın.
- **Alan uyumsuzluğu.** MNLI genel İngilizce üzerinde eğitilir. Hukuki, tıbbi ve bilimsel metinler için alana özgü NLI modelleri gerekir (ör. SciNLI, MedNLI).

## Kullan

2026 yığını (stack):

| Kullanım durumu | Model |
|---------|-------|
| Genel amaçlı NLI | `microsoft/deberta-v3-large-mnli` |
| Hızlı / kenar (edge) | `cross-encoder/nli-deberta-v3-base` |
| Sıfır atıflı sınıflandırma (hafif) | `facebook/bart-large-mnli` |
| Belge düzeyinde NLI | `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli` |
| Çok dilli | `MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli` |
| RAG'da halüsünasyon tespiti | RAGAS / DeepEval içindeki NLI katmanı |

2026 meta-modeli: NLI, metin anlamanın bant (duct tape)'ıdır. Ne zaman "A, B'yi destekliyor mu?" veya "A, B ile çelişiyor mu?" diye sorsanız — başka bir LLM çağrısı yapmadan önce NLI'a başvurun.

## Teslim Et

`outputs/skill-nli-picker.md` olarak kaydedin:

```markdown
---
name: nli-picker
description: Pick an NLI model, label template, and evaluation setup for a classification / faithfulness / zero-shot task.
version: 1.0.0
phase: 5
lesson: 21
tags: [nlp, nli, zero-shot]
---

Given a use case (faithfulness check, zero-shot classification, document-level inference), output:

1. Model. Named NLI checkpoint. Reason tied to domain, length, language.
2. Template (if zero-shot). Verbalization pattern. Example.
3. Threshold. Entailment cutoff for the decision rule. Reason based on calibration.
4. Evaluation. Accuracy on held-out labeled set, hypothesis-only baseline, adversarial subset.

Refuse to ship zero-shot classification without a 100-example labeled sanity check. Refuse to use a sentence-level NLI model on document-length premises. Flag any claim that NLI solves hallucination — it reduces it; it does not eliminate it.
```

#### Açıklama
Bu şablon, bir NLI modeli seçerken kullanılacak bir yetenek (skill) tanımıdır. Kullanım durumuna göre model, şablon, eşik ve değerlendirme planı çıkışı verir.

## Alıştırmalar

1. **Kolay.** `facebook/bart-large-mnli` modelini üç sınıfı da kapsayan 20 el yapımı (ön koşul, hipotez, etiket) üçlüsü üzerinde çalıştırın. Doğruluğu ölçün. Zorlamalı "alt dizi sezgisel yaklaşımı" tuzakları ekleyin ("I did not eat the cake" vs "I ate the cake") ve modelin kırılıp kırılmadığını görün.
2. **Orta.** Sıfır atıflı şablon `"This text is about {label}"` ile `"The topic is {label}"` ve `"{label}"` seçeneklerini 100 AG News başlığı üzerinde karşılaştırın. Doğruluk değişimini raporlayın.
3. **Zor.** Bir RAG sadakat kontrolcüsü oluşturun: atomik iddia ayrıştırma + her iddia için NLI. 50 RAG üretilen cevap ve altın (gold) bağlam ile değerlendirin. El etiketlerine göre yanlış pozitif ve yanlış negatif oranlarını ölçün.

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| NLI | Doğal Dil Çıkarımı (Natural Language Inference) | Ön koşul-hipotez ilişkisinin üç yönlü sınıflandırması. |
| RTE | Metinsel Zorunluluğun Tanınması (Recognizing Textual Entailment) | NLI'ın eski adı; aynı görev. |
| Zorunlu Kılınma (Entailment) | "t, h'yi ima eder" | Tipik bir okuyucu t verildiğinde h'nin doğru olacağına varır. |
| Çelişki (Contradiction) | "t, h'yi dışlar" | Tipik bir okuyucu t verildiğinde h'nin yanlış olacağına varır. |
| Nötr (Neutral) | "kararsız" | t'den h'ye her iki yönde de çıkarım yok. |
| Sıfır atıflı sınıflandırma (Zero-shot classification) | NLI olarak sınıflandırıcı | Etiketleri hipotez olarak sözelleştirin, maksimum zorunlu kılınmayı seçin. |
| Sadakat (Faithfulness) | Cevap destekleniyor mu? | (Getirilen bağlam, üretilen cevap) üzerinde NLI. |

## İleri Okuma

- [Bowman vd. (2015). A large annotated corpus for learning natural language inference](https://arxiv.org/abs/1508.05326) — SNLI.
- [Williams, Nangia, Bowman (2017). A Broad-Coverage Challenge Corpus for Sentence Understanding through Inference](https://arxiv.org/abs/1704.05426) — MultiNLI.
- [Nie vd. (2019). Adversarial NLI](https://arxiv.org/abs/1910.14599) — ANLI benchmark'ı.
- [Yin, Hay, Roth (2019). Benchmarking Zero-shot Text Classification](https://arxiv.org/abs/1909.00161) — NLI-as-classifier.
- [He vd. (2021). DeBERTa: Decoding-enhanced BERT with Disentangled Attention](https://arxiv.org/abs/2006.03654) — 2026 NLI Arbeitspferd.