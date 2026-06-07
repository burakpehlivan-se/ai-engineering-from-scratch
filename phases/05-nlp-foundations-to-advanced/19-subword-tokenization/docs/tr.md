# Subword Tokenizasyon — BPE, WordPiece, Unigram, SentencePiece

> Kelime tokenizer'ları görülmemiş kelimelerde boğulur. Karakter tokenizer'ları dizi uzunluğunu şişirir. Subword tokenizer'lar dengeyi bulur. Her modern LLM birinin üzerine kurulmuştur.

**Tür:** Öğren
**Diller:** Python
**Ön koşullar:** Faz 5 · 01 (Metin İşleme), Faz 5 · 04 (GloVe / FastText / Subword)
**Süre:** ~60 dakika

## Problem

Sözlüğünüzde 50.000 kelime var. Bir kullanıcı "tokenizeedilemez" yazar. Tokenizer'ınız `[UNK]` döndürür. Model artık kelime hakkında hiçbir sinyale sahip değildir. Daha da kötüsü: corpus'unuzdaki 90. persentil belgede 40 nadir kelime var, bu da belge başına düşen 40 bit bilgi kaybı demektir.

Subword tokenizasyon (subword tokenization) bunu çözer. Yaygın kelimeler tek token olarak kalır. Nadir kelimeler anlamlı parçalara ayrılır: `tokenizeedilemez` → `token`, `ize`, `edilemez`. Eğitim verisi her şeyi kapsar çünkü her dize nihayetinde bir byte dizisidir.

2026'daki her öncü LLM, üç algoritmadan biri (BPE, Unigram, WordPiece) ve üç kütüphaneden biri (tiktoken, SentencePiece, HF Tokenizers) üzerine kuruludur. Birini seçmeden bir dil modeli gönderemezsiniz.

## Kavram

![BPE vs Unigram vs WordPiece, karakter karakter](../assets/subword-tokenization.svg)

**BPE (Byte-Pair Encoding).** Karakter düzeyinde bir sözlükle başlayın. Her bitişik çifti sayın. En sık görülen çifti yeni bir token olarak birleştirin. Hedef sözlük boyutuna ulaşana kadar tekrarlayın. Hâkim algoritma: GPT-2/3/4, Llama, Gemma, Qwen2, Mistral.

**Byte-level BPE.** Aynı algoritma ancak Unicode karakterleri yerine ham byte'lar (256 temel token) üzerinde. Sıfır `[UNK]` token garantisi — her byte dizisi kodlanır. GPT-2, 50.257 token kullanır (256 byte + 50.000 birleştirme + 1 özel).

**Unigram.** Büyük bir sözlükle başlayın. Her token'a bir unigram olasılığı atayın. Token'ların çıkarma log-olabilirliğini en az artıranları yinelemeli olarak budayın. Çıkarımda olasılıksal: tokenizasyonları örnekleme (subword regularization aracılığıyla veri artırımı için faydalı). T5, mBART, ALBERT, XLNet, Gemma tarafından kullanılır.

**WordPiece.** Ham frekans yerine eğitim corpus'unun olasılığını maksimize eden çiftleri birleştirir. BERT, DistilBERT, ELECTRA tarafından kullanılır.

**SentencePiece vs tiktoken.** SentencePiece, doğrudan ham Unicode metni üzerinde sözlükleri (BPE veya Unigram) *eğiten* kütüphanedir, boşlukları `▁` olarak kodlar. tiktoken, önceden oluşturulmuş sözlüklere karşı hızlı bir *encoder*'dır; eğitmez.

Kural:

- **Yeni sözlük eğitimi:** SentencePiece (çok dilli, ön-tokenizasyon yok) veya HF Tokenizers.
- **GPT sözlüğü üzerinde hızlı çıkarım:** tiktoken (cl100k_base, o200k_base).
- **Her ikisi:** HF Tokenizers — tek kütüphane, eğitim + sunum.

## İnşa Et

### Adım 1: sıfırdan BPE

`code/main.py`'ye bakın. Döngü:

```python
def train_bpe(corpus, num_merges):
 vocab = {tuple(word) + ("</w>",): count for word, count in corpus.items()}
 merges = []
 for _ in range(num_merges):
 pairs = Counter()
 for symbols, freq in vocab.items():
 for a, b in zip(symbols, symbols[1:]):
 pairs[(a, b)] += freq
 if not pairs:
 break
 best = pairs.most_common(1)[0][0]
 merges.append(best)
 vocab = apply_merge(vocab, best)
 return merges
```

#### Açıklama
Algoritmanın kodladığı üç gerçek. `</w>` kelime sonunu işaretler, böylece "low" (sonek) ve "lower" (önek) ayrı kalır. Frekans ağırlıklandırması yüksek frekanslı çiftlerin erken kazanmasını sağlar. Birleştirme listesi sıralıdır — çıkarım birleştirmeleri eğitim sırasıyla uygular.

### Adım 2: öğrenilen birleştirmelerle kodlama

```python
def encode_bpe(word, merges):
 symbols = list(word) + ["</w>"]
 for a, b in merges:
 i = 0
 while i < len(symbols) - 1:
 if symbols[i] == a and symbols[i + 1] == b:
 symbols = symbols[:i] + [a + b] + symbols[i + 2:]
 else:
 i += 1
 return symbols
```

#### Açıklama
Basit O(n·|merges|). Production uygulamaları (tiktoken, HF Tokenizers) öncelikli kuyruklarla birleştirme sıralaması (merge-rank) araması kullanır ve neredeyse doğrusal zamanda çalışır.

### Adım 3: pratikte SentencePiece

```python
import sentencepiece as spm

spm. SentencePieceTrainer.train(
 input="corpus.txt",
 model_prefix="my_tokenizer",
 vocab_size=8000,
 model_type="bpe", # or "unigram"
 character_coverage=0.9995, # lower for CJK (e.g. 0.9995 for English, 0.995 for Japanese)
 normalization_rule_name="nmt_nfkc",
)

sp = spm. SentencePieceProcessor(model_file="my_tokenizer.model")
print(sp.encode("untokenizable", out_type=str))
# ['▁un', 'token', 'izable']
```

#### Açıklama
Dikkat: ön-tokenizasyon gerekmez, boşluk `▁` olarak kodlanır, `character_coverage` nadir karakterlerin ne kadar agresif bir şekilde korunacağını vs. `<unk>`'a eşlenmesini kontrol eder.

### Adım 4: OpenAI-uyumlu sözlükler için tiktoken

```python
import tiktoken
enc = tiktoken.get_encoding("o200k_base")
print(enc.encode("untokenizable")) # [127340, 101028]
print(len(enc.encode("Hello, world!"))) # 4
```

#### Açıklama
Yalnızca kodlama. Hızlı (Rust arka ucu). GPT-4/5 tokenizasyonuyla byte sayma, maliyet tahmini ve bağlam penceresi bütçeleme için tam eşleşme.

## 2026'da hâlâ gönderilen tuzaklar

- **Tokenizer kayması.** A sözlüğü üzerinde eğitim, B sözlüğüne deploy. Token ID'leri farklı; model saçmalık üretir. CI'da `tokenizer.json` hash'ini kontrol edin.
- **Boşluk belirsizliği.** BPE "hello" ve " hello" farklı token'lar üretir. Her zaman `add_special_tokens` ve `add_prefix_space`'ı açıkça belirtin.
- **Çok dilli yetersiz eğitim.** İngilizce ağırlıklı corpus'lar Latin dışı scriptleri 5-10x daha fazla token'a bölen sözlükler üretir. GPT-3.5'te aynı prompt Japonca/Arapça'da 5-10x daha pahalıya mal olur. o200k_base bunu kısmen düzeltti.
- **Emoji bölünmeleri.** Tek bir emoji 5 token alabilir. Bağlam bütçelerken emoji yönetimini kontrol edin.

## Kullan

2026 stacki:

| Durum | Seçin |
|-----------|------|
| Tek dilli modeli sıfırdan eğitme | HF Tokenizers (BPE) |
| Çok dilli model eğitimi | SentencePiece (Unigram, `character_coverage=0.9995`) |
| OpenAI-uyumlu API sunumu | tiktoken (`o200k_base` GPT-4+) |
| Alan-specific sözlük (kod, matematik, protein) | Alan corpus'u üzerinde özel BPE eğitin, temel sözlükle birleştirin |
| Kenar çıkarımı (edge inference), küçük model | Unigram (daha küçük sözlükler daha iyi çalışır) |

Sözlük boyutu bir ölçeklendirme karardır, sabit değildir. Kabaca kural: <1B parametre için 32k, 1-10B için 50-100k, çok dilli/öncü için 200k+.

## Ürün Olarak Kullan

`outputs/skill-bpe-vs-wordpiece.md` olarak kaydedin:

```markdown
---
name: tokenizer-picker
description: Pick tokenizer algorithm, vocab size, library for a given corpus and deployment target.
version: 1.0.0
phase: 5
lesson: 19
tags: [nlp, tokenization]
---

Given a corpus (size, languages, domain) and deployment target (training from scratch / fine-tuning / API-compatible inference), output:

1. Algorithm. BPE, Unigram, or WordPiece. One-sentence reason.
2. Library. SentencePiece, HF Tokenizers, or tiktoken. Reason.
3. Vocab size. Rounded to nearest 1k. Reason tied to model size and language coverage.
4. Coverage settings. `character_coverage`, `byte_fallback`, special-token list.
5. Validation plan. Average tokens-per-word on held-out set, OOV rate, compression ratio, round-trip decode equality.

Refuse to train a character-coverage <0.995 tokenizer on corpora with rare-script content. Refuse to ship a vocab without a frozen `tokenizer.json` hash check in CI. Flag any monolingual tokenizer under 16k vocab as likely under-spec.
```

#### Açıklama
Verilen corpus ve deploy hedefi için tokenizer algoritması, sözlük boyutu ve kütüphane seçen bir skill tanımıdır.

## Alıştırmalar

1. **Kolay.** `code/main.py`'nin küçük corpus'u üzerinde 500 birleştirmeli bir BPE eğitin. Üç ayrılmış kelimeyi kodlayın. Kaçı tam olarak 1 token üretti vs. >1 token?
2. **Orta.** `cl100k_base`, `o200k_base` vevocab=32k ile eğittiğiniz SentencePiece BPE arasındaki 100 İngilizce Vikipedi cümlesinde token sayılarını karşılaştırın. Her birinin sıkıştırma oranını raporlayın.
3. **Zor.** Aynı corpus'u BPE, Unigram ve WordPiece ile eğitmin. Her birini küçük bir duygu sınıflandırıcısında kullandığınızda aşağı akış doğruluğunu ölçün. Seçim F1'den 1 puandan fazla hareket ettiriyor mu?

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| BPE | Byte-Pair Encoding | En sık görülen karakter çiftlerinin hedef sözlük boyutuna ulaşana kadar açgözlü birleşmesi. |
| Byte-level BPE | Hiçbir zaman bilinmeyen token yok | Ham 256 byte üzerinde BPE; GPT-2 / Llama bunu kullanır. |
| Unigram | Olasılıksal tokenizer | Büyük bir aday kümesinden log-olabilirlikle budama; T5, Gemma tarafından kullanılır. |
| SentencePiece | Boşluklu olan | Ham metin üzerinde BPE/Unigram eğiten kütüphane; boşluk `▁` olarak kodlanır. |
| tiktoken | Hızlı olan | Önceden oluşturulmuş sözlükler için OpenAI'nin Rust tabanlı BPE encoder'ı. Eğitim yok. |
| Birleştirme listesi | Sihirli sayılar | `(a, b) → ab` birleştirmelerinin sıralı listesi; çıkarım sırayla uygular. |
| Karakter kapsamı (Character coverage) | Nadir olan ne kadar nadir? | Tokenizer'ın eğitme corpus'unda kaplaması gereken karakter oranı; ~0.9995 tipik. |

## İleri Okuma

- [Sennrich, Haddow, Birch (2015). Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/abs/1508.07909) — BPE makalesi.
- [Kudo (2018). Subword Regularization with Unigram Language Model](https://arxiv.org/abs/1804.10959) — Unigram makalesi.
- [Kudo, Richardson (2018). SentencePiece: A simple and language independent subword tokenizer](https://arxiv.org/abs/1808.06226) — kütüphane.
- [Hugging Face — Summary of the tokenizers](https://huggingface.co/docs/transformers/tokenizer_summary) — öz referans.
- [OpenAI tiktoken repo](https://github.com/openai/tiktoken) — cookbook + kodlama listesi.
