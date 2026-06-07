# Uzun Bağlam Değerlendirmesi — NIAH, RULER, LongBench, MRCR

> Gemini 3 Pro 10M token bağlam sunuyor. 1M token'da 8-needle MRCR %26.3'e düşüyor. İlan edilen ≠ kullanılabilir. Uzun bağlam değerlendirmesi, gönderdiğiniz modelin gerçek kapasitesini söyler.

**Tür:** Öğren
**Diller:** Python
**Ön koşullar:** Faz 5 · 13 (Soru-Cevap), Faz 5 · 23 (Chunking Stratejileri)
**Süre:** ~60 dakika

## Problem

200 sayfalık bir sözleşmeniz var. Model 1M token bağlam iddia ediyor. Sözleşmeyi yapıştırıp "Feshetme koşulu nedir?" diye soruyorsunuz. Model yanıt veriyor — ancak kapak sayfasından yanıt veriyor çünkü feshetme koşulu 120k token derinliğinde, modelin gerçekten dikkat ettiği noktanın ötesinde.

Bu 2026 bağlam-kapasite boşluğudur. Teknik sayfalar 1M veya 10M der. Gerçeklik bunun %60-70'inin kullanılabilir olduğunu söyler ve "kullanılabilir" göreve bağlıdır.

- **Retrieval (çöpte tek iğne):** Öncü modellerde ilan edilen maksimuma kadar neredeyse mükemmel.
- **Çoklu atlama / toplama (multi-hop / aggregation):** Çoğu modelde ~128k sonrasında keskin şekilde bozulur.
- **Dağınık olgular üzerinde çıkarsama:** Başarısız olan ilk görevdir.

Uzun bağlam değerlendirmesi bu eksenleri ölçer. Bu ders benchmark'ları, her birinin aslında ne ölçdüğünü ve alanınız için özel bir iğne testi nasıl oluşturacağınızı belirtir.

## Kavram

![NIAH baseline, RULER çoklu görev, LongBench bütüncül](../assets/long-context-eval.svg)

**Çöpte İğne (NIAH, Needle-in-a-Haystack, 2023).** Uzun bir bağlamda kontrollü bir derinliğe bir olgu ("sihirli kelime ananas") yerleştirin. Modelden bunu getirmesini isteyin. Derinlik × uzunluk taraması. Orijinal uzun bağlam benchmark'ı. Öncü modeller artık bunu doyurur; gerekli ama yeterli olmayan bir baseline'dır.

**RULER (Nvidia, 2024).** 4 kategoride 13 görev türü: retrieval (tek / çoklu-anahtar / çoklu-değer), çoklu atlama izleme (değişken izleme), toplama (ortak kelime frekansı), QA. Yapılandırılabilir bağlam uzunluğu (4k'dan 128k+'ya). NIAH'ı doyuran ancak çoklu atlama'da başarısız olan modelleri ortaya çıkarır. 2024 sürümünde, 32k+ bağlam iddia eden 17 modelin yalnızca yarısı 32k'da kaliteyi korudu.

**LongBench v2 (2024).** 8k-2M kelimelik bağlam üzerinde 500 çoktan seçmeli soru, altı görev kategorisi: tek-belge QA, çok-belge QA, uzun bağlamda öğrenme, uzun diyalog, kod deposu, uzun yapılandırılmış veri. Gerçek dünya uzun bağlam davranışı için production benchmark'ı.

**MRCR (Multi-Round Coreference Resolution).** Büyük ölçekte çoklu tur özdeşleme. 8-needle, 24-needle, 100-needle varyantları. Bir modelin dikkat bozulmadan önce kaç olguyla oynayabildiğini ortaya çıkarır.

**NoLiMa.** "Anlamsal olmayan iğne" (Non-lexical needle). İğne ve sorgu hiçbir kelimesel örtüşmeyi paylaşmaz; retrieval anlamsal bir çıkarsama adımı gerektirir. NIAH'dan daha zor.

**HELMET.** Birçok belgeyi ardışık olarak ekler, herhangi birinden bir soru sorar. Seçici dikkati test eder.

**BABILong.** İlgisiz çöplerin içine bAbI çıkarsama zincirlerini gömer. Yalnızca retrieval değil, çöpte çıkarsamayı test eder.

### Aslında ne raporlanmalı

- **İlan edilen bağlam penceresi.** Teknik sayfa sayısı.
- **Etkili retrieval uzunluğu.** Bir eşiğe (örn. %90) NIAH geçişi.
- **Etkili çıkarsama uzunluğu.** O eşikte çoklu atlama veya toplama geçişi.
- **Bozulma eğrisi.** Görev türüne göre çizilen doğruluk vs. bağlam uzunluğu.

Teknik sayfa için iki sayı: retrieval-etkili ve çıkarsama-etkili. Genellikle çıkarsama-etkili, ilan edilen pencerenin %25-50'sidir.

## İnşa Et

### Adım 1: alanınız için özel NIAH

`code/main.py`'ye bakın. Taslak:

```python
def build_haystack(filler_text, needle, depth_ratio, total_tokens):
 if not (0.0 <= depth_ratio <= 1.0):
 raise ValueError(f"depth_ratio must be in [0, 1], got {depth_ratio}")
 if total_tokens <= 0:
 raise ValueError(f"total_tokens must be positive, got {total_tokens}")

 filler_tokens = tokenize(filler_text)
 needle_tokens = tokenize(needle)
 if not filler_tokens:
 raise ValueError("filler_text produced no tokens")

 # Repeat filler until long enough to fill the haystack body.
 body_len = max(total_tokens - len(needle_tokens), 0)
 while len(filler_tokens) < body_len:
 filler_tokens = filler_tokens + filler_tokens
 filler_tokens = filler_tokens[:body_len]

 insert_at = min(int(body_len * depth_ratio), body_len)
 haystack = filler_tokens[:insert_at] + needle_tokens + filler_tokens[insert_at:]
 return " ".join(haystack)


def score_niah(model, haystack, question, expected):
 answer = model.complete(f"Context: {haystack}\nQ: {question}\nA:", max_tokens=50)
 return 1 if expected.lower() in answer.lower() else 0
```

#### Açıklama
`depth_ratio` ∈ {0, 0.25, 0.5, 0.75, 1.0} × `total_tokens` ∈ {1k, 4k, 16k, 64k} taraması yapın. Isı haritasını (heatmap) çizin. Bu, hedef modeliniz için NIAH kartıdır.

### Adım 2: çoklu iğne varyantı

```python
def build_multi_needle(filler, needles, total_tokens):
 depths = [0.1, 0.4, 0.7]
 chunks = [filler[:int(total_tokens * 0.1)]]
 for depth, needle in zip(depths, needles):
 chunks.append(needle)
 next_chunk = filler[int(total_tokens * depth): int(total_tokens * (depth + 0.3))]
 chunks.append(next_chunk)
 return " ".join(chunks)
```

#### Açıklama
"Üç sihirli kelime nedir?" gibi sorular üçünü de getirmeyi gerektirir. Tek iğne başarısı çoklu iğne başarısını tahmin etmez.

### Adım 3: çoklu atlama değişken izleme (RULER tarzı)

```python
haystack = """X1 = 42. ... (filler) ... X2 = X1 + 10. ... (filler) ... X3 = X2 * 2."""
question = "What is X3?"
```

#### Açıklama
Cevap üç atamayı zincirlemeyi gerektirir. 128k'daki öncü modeller burada genellikle %50-70 doğruluğa düşer.

### Adım 4: stackinizde LongBench v2

```python
from datasets import load_dataset
longbench = load_dataset("THUDM/LongBench-v2")

def eval_model_on_longbench(model, subset="single-doc-qa"):
 tasks = [x for x in longbench["test"] if x["task"] == subset]
 correct = 0
 for x in tasks:
 answer = model.complete(x["context"] + "\n\nQ: " + x["question"], max_tokens=20)
 if normalize(answer) == normalize(x["answer"]):
 correct += 1
 return correct / len(tasks)
```

#### Açıklama
Kategori bazında doğruluk raporlayın. Toplama puanları büyük görev düzeyinde farkları gizler.

## Tuzaklar

- **Yalnızca NIAH değerlendirmesi.** 1M token'da NIAH geçmek çoklu atlama hakkında hiçbir şey söylemez. Her zaman RULER veya özel çoklu atlama testi çalıştırın.
- **Düzgün derinlik örnekleme.** Birçok uygulama yalnızca depth=0.5 test eder. depth=0, 0.25, 0.5, 0.75, 1.0 test edin — "ortada kaybolma" etkisi gerçektir.
- **Dolgu ile kelimesel örtüşme.** İğne dolgu ile anahtar kelimeleri paylaşıyorsa retrieval sıradan hale gelir. NoLiMa tarzı örtüşmeyen iğneler kullanın.
- **Gecikmeyi göz ardı etme.** 1M token'lık promptlar doldurma (prefill) için 30-120 saniye sürer. Doğrulukla birlikte ilk-token zamanını (time-to-first-token) ölçün.
- **Sağlayıcı-kendini-raporlama sayıları.** OpenAI, Google, Anthropic kendi puanlarını yayınlar. Her zaman kendi kullanım durumunuzda bağımsız olarak yeniden çalıştırın.

## Kullan

2026 stacki:

| Durum | Benchmark |
|-----------|-----------|
| Hızlı doğruluk kontrolü | 3 derinlik × 3 uzunlukta özel NIAH |
| Production için model seçimi | Hedef uzunluğunuzda RULER (13 görev) |
| Gerçek dünya QA kalitesi | LongBench v2 tek-belge-QA alt kümesi |
| Çoklu atlama çıkarsaması | BABILong veya özel değişken izleme |
| Konuşma / diyalog | Hedef uzunluğunuzda MRCR 8-needle |
| Model yükseltme gerilemesi | Sabit dahili NIAH + RULER harness, her yeni modelde çalıştırın |

Production için kural: niyet uzunluğunuzda NIAH + 1 çıkarsama görevi çalıştırana kadar bağlam penceresine güvenmeyin.

## Ürün Olarak Kullan

`outputs/skill-long-context-eval.md` olarak kaydedin:

```markdown
---
name: long-context-eval
description: Design a long-context evaluation battery for a given model and use case.
version: 1.0.0
phase: 5
lesson: 28
tags: [nlp, long-context, evaluation]
---

Given a target model, target context length, and use case, output:

1. Tests. NIAH depth × length grid; RULER multi-hop; custom domain task.
2. Sampling. Depths 0, 0.25, 0.5, 0.75, 1.0 at each length.
3. Metrics. Retrieval pass rate; reasoning pass rate; time-to-first-token; cost-per-query.
4. Cutoff. Effective retrieval length (90% pass) and effective reasoning length (70% pass). Report both.
5. Regression. Fixed harness, rerun on every model upgrade, surface deltas.

Refuse to trust a context window from the model card alone. Refuse NIAH-only evaluation for any multi-hop workload. Refuse vendor self-reported long-context scores as independent evidence.
```

#### Açıklama
Verilen model, hedef bağlam uzunluğu ve kullanım durumu için uzun bağlam değerlendirme bataryası tasarlayan bir skill tanımıdır.

## Alıştırmalar

1. **Kolay.** 3 derinlik (0.25, 0.5, 0.75) × 3 uzunluk (1k, 4k, 16k) ile bir NIAH oluşturun. Herhangi bir modelde çalıştırın. Geçme oranını 3×3 ısı haritası olarak çizin.
2. **Orta.** 3 iğne varyantı ekleyin. Her uzunlukta 3'ünün de retrieval'ını ölçün. Aynı uzunluktaki tek iğne geçme oranıyla karşılaştırın.
3. **Zor.** 64k dolgu içine gömülü bir değişken izleme görevi (X1 → X2 → X3, 3 atlama) oluşturun. 3 öncü modelde doğruluğu ölçün. Model başına etkili çıkarsama uzunluğunu raporlayın.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| NIAH | Çöpte iğne | Dolguya bir olgu yerleştirin, modelden getirmesini isteyin. |
| RULER | Steroidli NIAH | Retrieval / çoklu atlama / toplama / QA'da 13 görev türü. |
| Etkili bağlam | Gerçek kapasite | Doğruluğun eşiğin üzerinde kaldığı uzunluk. |
| Ortada kaybolma (Lost in the middle) | Derinlik önyargısı | Uzun girdilerin ortasındaki içeriğe model yeterince dikkat etmez. |
| Çoklu iğne | Birçok olgu birlikte | Birden fazla yerleştirme; yalnızca retrieval'ı değil, dikkat oyununu test eder. |
| MRCR | Çoklu tur özdeşleme | 8, 24 veya 100 iğneli özdeşleme; dikkat doygunluğunu ortaya çıkarır. |
| NoLiMa | Anlamsal olmayan iğne | İğne ve sorgu kelimesel token paylaşmaz; çıkarsama gerektirir. |

## İleri Okuma

- [Kamradt (2023). Needle in a Haystack analysis](https://github.com/gkamradt/LLMTest_NeedleInAHaystack) — orijinal NIAH repo'su.
- [Hsieh et al. (2024). RULER: What's the Real Context Size of Your Long-Context LMs?](https://arxiv.org/abs/2404.06654) — çoklu görev benchmark'ı.
- [Bai et al. (2024). LongBench v2](https://arxiv.org/abs/2412.15204) — gerçek dünya uzun bağlam değerlendirmesi.
- [Modarressi et al. (2024). NoLiMa: Non-lexical needles](https://arxiv.org/abs/2404.06666) — daha zor iğneler.
- [Kuratov et al. (2024). BABILong](https://arxiv.org/abs/2406.10149) — çöpte çıkarsama.
- [Liu et al. (2024). Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172) — derinlik önyargısı makalesi.
