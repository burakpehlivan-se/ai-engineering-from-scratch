# Makine Çevirisi

> Çeviri, NLP araştırmalarını otuz yıl boyunca finanse eden ve hâlâ finanse etmeye devam eden görevdir.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 5 · 10 (Attention Mechanism), Faz 5 · 04 (GloVe, FastText, Subword)
**Süre:** ~75 dakika

## Problem

Bir model, bir dildeki cümleyi okur ve başka bir dilde cümle üretir. Uzunluk değişir. Kelime sırası değişir. Bazı kaynak kelimeler birden fazla hedef kelimeye karşılık gelir ve tersi de geçerlidir. İdiomlar tek-tüzel eşleştirmeye direnir. Fransızca'da "I miss you" → "tu me manques" — kelimesi kelimesine "sensin bana eksik olan". Kelime düzeyindeki hizalama bu durumda işe yaramaz.

Makine çevirisi, NLP'yi encoder-decoder'ları, attention'ı, transformer'ları ve nihayet tüm LLM paradigmasını icat etmeye zorlayan görevdir. İleriye doğru atılan her adım, çeviri kalitesinin ölçülebilir olduğu ve insan ile makine arasındaki farkın inatçı olduğu için gelmiştir.

Bu ders tarih dersini atlar ve 2026'nın çalışan pipelinesını öğretir: önceden eğitilmiş çok dilli encoder-decoder (NLLB-200 veya mBART), subword tokenization, beam search, BLEU ve chrF değerlendirmesi, ve hâlâ production'a yakalancmadan ulaşan birkaç hata modu.

## Kavram

![MT pipeline: tokenize → encode → decode with attention → detokenize](../assets/mt-pipeline.svg)

Modern MT, paralel metin üzerinde eğitilmiş bir transformer encoder-decoder'ıdır. Encoder, kaynak dili kendi tokenization'ıyla okur. Decoder, hedefi encoder çıktısını cross-attention (ders 10) kullanarak her seferinde bir subword üretir. Decoding, greedy decoding tuzağına düşmemek için beam search kullanır. Çıktı detokenize edilir, büyük harf küçültülür ve bir referansla puanlanır.

Üç operasyonel seçim, gerçek dünya MT kalitesini belirler:

- **Tokenizer.** SentencePiece BPE, karışık dil corpus'u üzerinde eğitilir. Diller arasında paylaşılan kelime haznesi, NLLB'de zero-shot çiftlerini mümkün kılar.
- **Model boyutu.** NLLB-200 distilled 600M dizüstü bilgisayara sığar. NLLB-200 3.3B yayınlanmış production varsayılanıdır. 54.5B araştırma tavanıdır.
- **Decoding.** Genel içerik için beam genişliği 4-5. Çok kısa çıkışları önlemek için length penalty. Terminoloji tutarlılığı gerektiğinde constrained decoding.

## İnşa Et

### Adım 1: önceden eğitilmiş MT çağrısı

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_id = "facebook/nllb-200-distilled-600M"
tok = AutoTokenizer.from_pretrained(model_id, src_lang="eng_Latn")
model = AutoModelForSeq2SeqLM.from_pretrained(model_id)

src = "The cats are running."
inputs = tok(src, return_tensors="pt")

out = model.generate(
    **inputs,
    forced_bos_token_id=tok.convert_tokens_to_ids("fra_Latn"),
    num_beams=5,
    length_penalty=1.0,
    max_new_tokens=64,
)
print(tok.batch_decode(out, skip_special_tokens=True)[0])
```

```text
Les chats courent.
```

#### Açıklama
Bu kod, NLLB-200 distilled modelini kullanarak İngilizce bir cümleyi Fransızca'ya çevirir. `src_lang` tokenizer'a hangi yazıyı ve segmentasyonu uygulayacağını söyler. `forced_bos_token_id` decoder'a hangi dili üreteceğini söyler. Her ikisi de NLLB'ye özgü trickslerdir; mBART ve M2M-100 kendi convention'larını kullanır ve birbirlerinin yerine geçirilemezler.

Burada üç önemli nokta var. `src_lang`, tokenizer'a hangi yazıyı ve segmentasyonu uygulayacağını söyler. `forced_bos_token_id`, decoder'a hangi dili üreteceğini söyler. Her ikisi NLLB'ye özgü trickslerdir; mBART ve M2M-100 kendi convention'larını kullanır ve birbirlerinin yerine geçirilemezler.

### Adım 2: BLEU ve chrF

BLEU, çıktı ile reference arasındaki n-gram örtüşmesini ölçer. Dört reference n-gram boyutu (1-4), precision'ların geometrik ortalaması, çok kısa çıkışlar için brevity penalty. Skor [0, 100] arasındadır. Sık kullanılır. Yorumlaması sinir bozucudur: 30 BLEU "kullanılabilir"; 40 "iyi"; 50 "olağanüstü"; 1 BLEU altındaki farklar gürültüdür.

chrF, karakter düzeyinde F-score ölçer. BLEU'nun eşleşmeleri az saydığı morfolojik olarak zengin dillere karşı daha hassastır. Genellikle BLEU ile birlikte raporlanır.

```python
import sacrebleu

hypotheses = ["Les chats courent."]
references = [["Les chats courent."]]

bleu = sacrebleu.corpus_bleu(hypotheses, references)
chrf = sacrebleu.corpus_chrf(hypotheses, references)
print(f"BLEU: {bleu.score:.1f}  chrF: {chrf.score:.1f}")
```

#### Açıklama
Bu kod, sacrebleu kütüphanesi kullanarak bir çeviri hipotezinin BLEU ve chrF skorlarını hesaplar. Her zaman `sacrebleu` kullanın — tokenization'ı normalleştirerek skorların makaleler arasında karşılaştırılmasını sağlar. Kendi BLEU hesaplamanızı yapmak yanıltıcı benchmarklara yol açar.

Her zaman `sacrebleu` kullanın. Tokenization'ı normalleştirerek skorların makaleler arasında karşılaştırılmasını sağlar. Kendi BLEU hesaplamanızı yapmak yanıltıcı benchmarklara yol açar.

### Üç katmanlı değerlendirme hiyerarşisi (2026)

Modern MT değerlendirmesi üç tamamlayıcı metrik ailesi kullanır. En az ikisiyle production'a çıkın:

- **Sezgisel** (BLEU, chrF). Hızlı, reference-tabanlı, yorumlanabilir, paraphrase'e duyarsız. Eski karşılaştırma ve regresyon tespiti için kullanın.
- **Öğrenilmiş** (COMET, BLEURT, BERTScore). İnsan yargısı üzerinde eğitilmiş nöral modeller; çevirinin kaynak ve reference ile anlamsal benzerliğini karşılaştırır. COMET, 2023'ten beri MT araştırmasıyla en yüksek ilişkiye sahiptir ve kalitenin önemli olduğu 2026 production varsayılanıdır.
- **LLM-as-judge** (reference-free). Büyük bir modelden çevirileri akıcılık, yeterlilik, ton, kültürel uygunluk açısından puanlaması istenir. İyi tasarlanmış bir rubrikle GPT-4-as-judge, insan anlaşmasıyla ~%80 eşleşir. Reference'ın olmadığı açık uçlu içerik için kullanın.

Pratik 2026 stacki: BLEU ve chrF için `sacrebleu`, COMET için `unbabel-comet`, ve son insan yüzü sinyali için bir LLM. Her metriği production verisine güvenmeden önce 50-100 insan etiketli örnekle kalibre edin.

Reference-free metrikler (COMET-QE, BLEURT-QE, LLM-as-judge), reference olmadan çevirileri değerlendirmenizi sağlar; bu, reference çevirilerin olmadığı uzun kuyruk dil çiftleri için önemlidir.

### Adım 3: production'da neler kırılır

Yukarıdaki çalışan pipeline %80 zamanında akıcı çevirir ve kalan %20'yi sessizce başarısız olur. Adı konulmuş hata modları:

- **Hallucination (Varsanı).** Model, kaynakta olmayan bir içerik üretir. Tanınmayan alan sözlüğünde yaygındır. Belirti: çıktı akıcıdır ancak kaynağın belirtmediği iddiaları içerir. Hafifletme: alan terimlerinde constrained decoding, düzenlenmiş içerikte insan incelemesi, çıktının inputtan çok daha uzun olması durumunda izleme.
- **Hedef-dışı üretim (Off-target generation).** Model yanlış dile çevirir. NLLB, nadir dil çiftlerinde bunu yapmaya şaşırtıcı derecede yatkındır. Hafifletme: `forced_bos_token_id`'yi doğrulayın ve her zaman çıktı üzerinde dil kimliği model kontrolü ile decode edin.
- **Terminoloji kayması (Terminology drift).** "Sign up" belge 1'de "s'inscrire" ve belge 2'de "créer un compte" olur. UI metni ve kullanıcıya yönelik stringler için tutarlılık, ham kaliteden daha önemlidir. Hafifletme: sözlük kısıtlı decoding veya post-edit dictionary.
- **Resmiyet uyuşmazlığı (Formality mismatch).** Fransızca "tu" vs "vous", Japonca saygı düzeyleri. Model, eğitimde hangi formun daha yaygın olduğunu seçer. Müşteriye yönelik içerikte bu genellikle yanlıştır. Hafifletme: model destekliyorsa bir resmiyet token'ı ile prompt prefix'i, ya da yalnızca resmi corpus üzerinde fine-tune edilmiş küçük bir model.
- **Kısa inputta uzunluk patlaması.** Çok kısa input cümleleri genellikle aşırı uzun çeviriler üretir çünkü length penalty ~5 kaynak token'ın altında bir çukura düşer. Hafifletme: kaynak uzunluğuyla orantılı sert max-length cap'i.

### Adım 4: bir alan için fine-tuning

Önceden eğitilmiş modeller genelcilerdir. Hukuki, tıbbi veya oyun-dialogu çevirisi, alan paralel verisi üzerinde fine-tuning ile ölçülebilir şekilde fayda sağlar. Tarif olağanüstü değildir:

```python
from transformers import Trainer, TrainingArguments
from datasets import Dataset

pairs = [
    {"src": "The defendant pleaded guilty.", "tgt": "L'accusé a plaidé coupable."},
]

ds = Dataset.from_list(pairs)


def preprocess(ex):
    return tok(
        ex["src"],
        text_target=ex["tgt"],
        truncation=True,
        max_length=128,
        padding="max_length",
    )


ds = ds.map(preprocess, remove_columns=["src", "tgt"])

args = TrainingArguments(output_dir="out", per_device_train_batch_size=4, num_train_epochs=3, learning_rate=3e-5)
Trainer(model=model, args=args, train_dataset=ds).train()
```

#### Açıklama
Bu kod, NLLB modelini bir hukuki alan çifti üzerinde fine-tune eder. Birkaç bin yüksek kaliteli paralel örnek, birkaç yüz bin gürültülü web kazımı olandan daha iyidir. Eğitim verisinin kalitesi, production'daki en büyük kaldıraçtır.

Birkaç bin yüksek kaliteli paralel örnek, birkaç yüz bin gürültülü web kazımı olandan daha iyidir. Eğitim verisinin kalitesi, production'daki en büyük kaldıraçtır.

## Kullan

2026 MT production stacki:

| Kullanım durumu | Önerilen başlangıç noktası |
|---------|---------------------------|
| Her hangi birinden her hangi birine, 200 dil | `facebook/nllb-200-distilled-600M` (dizüstü) veya `nllb-200-3.3B` (production) |
| İngilizce merkezli, yüksek kalite, 50 dil | `facebook/mbart-large-50-many-to-many-mmt` |
| Kısa çalışmalar, ucuz çıkarım, İngilizce-Fransızca/Almanca/İspanyolca | Helsinki-NLP / Marian modelleri |
| Gecikme kritik, tarayıcı tarafı | ONNX-quantized Marian (~50 MB) |
| Maksimum kalite, ödemeye hazır | GPT-4 / Claude / Gemini ile çeviri prompt'ları |

2026 itibarıyla LLM'ler artık bazı dil çiftlerinde özel MT modellerini geçmektedir, özellikle de deyimsel içerikte ve uzun bağlamda. Tökülme, token başına maliyet ve gecikmedir. Bağlam uzunluğu, üslupsal tutarlılık veya prompting ile alan adaptasyonu verimden daha önemli olduğunda bir LLM seçin.

## Ürün Olarak Kullan

`outputs/skill-mt-evaluator.md` olarak kaydedin:

```markdown
---
name: mt-evaluator
description: Evaluate a machine translation output for shipping.
version: 1.0.0
phase: 5
lesson: 11
tags: [nlp, translation, evaluation]
---

Given a source text and a candidate translation, output:

1. Automatic score estimate. BLEU and chrF ranges you would expect. State whether a reference is available.
2. Five-point human-verifiable check list: (a) content preservation (no hallucinations), (b) correct language, (c) register / formality match, (d) terminology consistency with glossary if provided, (e) no truncation or length explosion.
3. One domain-specific issue to probe. E.g., for legal: named entities and statute citations. For medical: drug names and dosages. For UI: placeholder variables `{name}`.
4. Confidence flag. "Ship" / "Ship with review" / "Do not ship". Tie to the severity of issues found in step 2.

Refuse to ship a translation without a language-ID check on output. Refuse to evaluate without a reference unless the user explicitly opts in to reference-free scoring (COMET-QE, BLEURT-QE). Flag any content over 1000 tokens as likely needing chunked translation.
```

#### Açıklama
Bu, bir makine çevirisi çıktısını production'a göndermek için değerlendiren bir skill tanımıdır. Kaynak metin ve aday çeviri verildiğinde, otomatik skor tahmini, beş maddeli insan doğrulama kontrol listesi, alan sorunu ve güven bayrağı üretir.

## Alıştırmalar

1. **Kolay.** 5 cümlelik bir İngilizce paragrafı `nllb-200-distilled-600M` kullanarak Fransızca'ya ve sonra tekrar İngilizce'ye çevirin. Round-trip'in orijinale ne kadar yakın olduğunu ölçün. Anlamsal korunma ancak kelime seçimi kayması görmelisiniz.
2. **Orta.** Çeviri çıktıları üzerinde `fasttext lid.176` veya `langdetect` kullanarak bir dil kimliği kontrolü uygulayın. MT çağrısına entegre edin, böylece hedef-dışı üretimler döndürülmeden önce yakalanır.
3. **Zor.** `nllb-200-distilled-600M` modelini seçtiğiniz 5.000 çiftlik bir alan corpus'u üzerinde fine-tune edin. Fine-tuning öncesi ve sonrasında ayrılmış bir set üzerinde BLEU ölçün. Hangi cümle türlerinin iyileştiğini ve hangilerinin gerilediğini raporlayın.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| BLEU | Çeviri skoru | Brevity penalty ile n-gram precision. [0, 100]. |
| chrF | Karakter F-score | Karakter düzeyinde F-score. Morfolojik olarak zengin dillere daha hassas. |
| NMT | Nöral MT | Paralel metin üzerinde eğitilmiş transformer encoder-decoder. 2017+ varsayılanı. |
| NLLB | No Language Left Behind | Meta'nın 200 dil MT model ailesi. |
| Constrained decoding | Kontrollü çıkış | Belirli token'ların veya n-gram'ların çıkışta görünmesini/görünmemesini zorla. |
| Hallucination | Uydurulmuş içerik | Kaynak tarafından desteklenmeyen model çıktısı. |

## İleri Okuma

- [Costa-jussà et al. (2022). No Language Left Behind: Scaling Human-Centered Machine Translation](https://arxiv.org/abs/2207.04672) — NLLB makalesi.
- [Post (2018). A Call for Clarity in Reporting BLEU Scores](https://aclanthology.org/W18-6319/) — neden `sacrebleu` BLEU raporlamanın tek doğru yoludur.
- [Popović (2015). chrF: character n-gram F-score for automatic MT evaluation](https://aclanthology.org/W15-3049/) — chrF makalesi.
- [Hugging Face MT guide](https://huggingface.co/docs/transformers/tasks/translation) — pratik fine-tuning rehberi.