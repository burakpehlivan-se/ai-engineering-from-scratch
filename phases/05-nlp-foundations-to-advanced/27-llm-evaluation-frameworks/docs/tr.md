# LLM Değerlendirmesi — RAGAS, DeepEval, G-Eval

> Tam eşleşme ve F1 anlamsal eşdeğerliği kaçırır. İnsan incelemesi ölçeklenmez. LLM-as-judge production cevabıdır — güvenilir sayılar için yeterli kalibrasyonla.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 5 · 13 (Soru-Cevap), Faz 5 · 14 (Bilgi Getirme)
**Süre:** ~75 dakika

## Problem

RAG sisteminiz şöyle yanıt veriyor: "29 Haziran 2007."
Altın referans: "29 Haziran, 2007."
Tam Eşleşme 0 puan veriyor. F1 ~%75 veriyor. Bir insan %100 verirdi.

Şimdi bunu 10.000 test vakasıyla çarpın. Retriever, chunking, prompt veya modeldeki her değişiklikle tekrar çarpın. Anlamı anlayan, büyük ölçekte ucuz çalışan, gerilemeler hakkında yalan söylemeyen ve doğru başarısızlık modlarını yüzeye çıkaran bir değerlendiriciye ihtiyacınız var.

2026'da bu soruna sahip üç çerçeve var.

- **RAGAS.** Retrieval-Augmented Generation Assessment. Dört RAG metriği (sadakat, cevap-ilgisi, bağlam-hassasiyeti, bağlam-hatırlaması) ile NLI + LLM-judge arka uçları. Araştırma destekli, hafif.
- **DeepEval.** LLM'ler için Pytest. G-Eval, görev-tamamlama, halüsinasyon, önyargı metrikleri. CI/CD-native.
- **G-Eval.** Bir yöntem (ve bir DeepEval metriği): zincirleme düşünüşlü (chain-of-thought) LLM-as-judge, özel kriterler, 0-1 puan.

Üçü de LLM-as-judge'a yaslanır. Bu ders yöntem ve etrafındaki güven katmanı için sezgi oluşturur.

## Kavram

![Dört değerlendirme boyutu, LLM-as-judge mimarisi](../assets/llm-evaluation.svg)

**LLM-as-judge.** Statik bir metriği, çıktıları bir rubrik (rubric) verilerek puanlayan bir LLM ile değiştirin. `(query, context, answer)` verildiğinde bir judge LLM'e prompt verin: "Sadakat üzerine 0-1 puan verin." Skoru döndürür.

Neden çalışır: LLM'ler insan yargısını çok küçük bir maliyet fraksiyonuyla yakınsar. GPT-4o-mini puanlama başına ~$0.003 ile 1000 örnekleme regresyon değerlendirme çalışmalarını $5'in altında sağlar.

Neden sessizce başarısız olur:

1. **Judge önyargısı.** Judge'lar daha uzun cevapları, kendi model ailesinden gelen cevapları ve prompt stilini eşleşen cevapları tercih eder.
2. **JSON ayrıştırma hataları.** Kötü JSON → NaN puanı → toplamadan sessizce hariç tutulur. RAGAS kullanıcıları bu acıyı bilir. try/except + açık başarısızlık modu ile kapak.
3. **Model sürümleri üzerinde kayma.** Judge'ı yükseltmek her metriği değiştirir. Judge modelini + sürümünü dondurun.

**RAG dörtlüsü.**

| Metrik | Soru | Arka uç |
|--------|----------|---------|
| Sadakat (Faithfulness) | Cevaptaki her iddia getirilen bağlamdan mı geliyor? | NLI tabanlı çıkarım |
| Cevap ilgisi (Answer relevance) | Cevap soruyu ele alıyor mu? | Cevaptan hipotez sorular üret; gerçek soruyla karşılaştır |
| Bağlam hassasiyeti (Context precision) | Getirilen parçacıklardan kaçı ilgiliydi? | LLM-judge |
| Bağlam hatırlaması (Context recall) | Getirme tüm gerekli olanları getirdi mi? | Altın cevaba karşı LLM-judge |

**G-Eval.** Özel bir kriter tanımlayın: "Cevap doğru kaynağı alıntıladı mı?" Çerçeve otomatik olarak zincirleme düşünüşlü değerlendirme adımlarına genişler, ardından 0-1 puan verir. RAGAS'ın kapsamadığı alan-specific kalite boyutları için iyidir.

**Kalibrasyon.** İnsan etiketlerine karşı bir korelasyonunuz olana kadar ham judge skoruna asla güvenmeyin. 100 el-etiketli örnek çalıştırın. Judge vs insan grafiği çizin. Spearman rho hesaplayın. Rho < 0.7 ise, judge rubriğinizin çalışması gerekir.

## İnşa Et

### Adım 1: NLI ile sadakat (RAGAS tarzı)

```python
from typing import Callable
from transformers import pipeline

nli = pipeline("text-classification",
 model="MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli",
 top_k=None)

# `llm` is any callable: prompt str -> generated str.
# Example: llm = lambda p: client.messages.create(model="claude-haiku-4-5", ...).content[0].text
LLM = Callable[[str], str]


def atomic_claims(answer: str, llm: LLM) -> list[str]:
 prompt = f"""Break this answer into simple factual claims (one per line):
{answer}
"""
 return llm(prompt).splitlines()


def faithfulness(answer: str, context: str, llm: LLM) -> float:
 claims = atomic_claims(answer, llm)
 if not claims:
 return 0.0
 supported = 0
 for claim in claims:
 result = nli({"text": context, "text_pair": claim})[0]
 entail = next((s for s in result if s["label"] == "entailment"), None)
 if entail and entail["score"] > 0.5:
 supported += 1
 return supported / len(claims)
```

#### Açıklama
Cevabı atomik iddialara ayırın. Her iddiayı getirilen bağlama karşı NLI ile kontrol edin. Sadakat = desteklenen iddia oranıdır.

### Adım 2: cevap ilgisi

```python
import numpy as np
from sentence_transformers import SentenceTransformer

# encoder: any model implementing .encode(texts, normalize_embeddings=True) -> ndarray
# e.g., encoder = SentenceTransformer("BAAI/bge-small-en-v1.5")

def answer_relevance(question: str, answer: str, encoder, llm: LLM, n: int = 3) -> float:
 prompt = f"Write {n} questions this answer could be the answer to:\n{answer}"
 generated = [line for line in llm(prompt).splitlines() if line.strip()][:n]
 if not generated:
 return 0.0
 q_emb = np.asarray(encoder.encode([question], normalize_embeddings=True)[0])
 g_embs = np.asarray(encoder.encode(generated, normalize_embeddings=True))
 sims = [float(q_emb @ g_emb) for g_emb in g_embs]
 return sum(sims) / len(sims)
```

#### Açıklama
Cevap sorulan sorudan farklı sorular ima ediyorsa ilgi düşer.

### Adım 3: G-Eval özel metriği

```python
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams, LLMTestCase

metric = GEval(
 name="Correctness",
 criteria="The answer should be factually accurate and match the expected output.",
 evaluation_steps=[
 "Read the expected output.",
 "Read the actual output.",
 "List factual claims in the actual output.",
 "For each claim, mark supported or unsupported by the expected output.",
 "Return score = fraction supported.",
 ],
 evaluation_params=[LLMTestCaseParams. INPUT, LLMTestCaseParams. ACTUAL_OUTPUT, LLMTestCaseParams. EXPECTED_OUTPUT],
)

test = LLMTestCase(input="When was the first iPhone released?",
 actual_output="June 29th, 2007.",
 expected_output="June 29, 2007.")
metric.measure(test)
print(metric.score, metric.reason)
```

#### Açıklama
Değerlendirme adımları rubrikir. Açık adımlar, örtük "0-1 puan ver" promptlarından daha kararlıdır.

### Adım 4: CI kapısı

```python
import deepeval
from deepeval.metrics import FaithfulnessMetric, ContextualRelevancyMetric


def test_rag_system():
 cases = load_regression_cases()
 faith = FaithfulnessMetric(threshold=0.85)
 rel = ContextualRelevancyMetric(threshold=0.7)
 for case in cases:
 faith.measure(case)
 assert faith.score >= 0.85, f"faithfulness regression on {case.id}"
 rel.measure(case)
 assert rel.score >= 0.7, f"relevancy regression on {case.id}"
```

#### Açıklama
Pytest dosyası olarak gönderin. Her PR'da çalıştırın. Gerilemelerde birleştirmeleri engelleyin.

### Adım 5: sıfırdan oyuncak değerlendirme

`code/main.py`'ye bakın. Sadakat (cevap iddiaları ile bağlam örtüşmesi) ve ilgi (cevap token'ları ile soru token'ları örtüşmesi) için yalnızca stdlib aproximasyonları. Production değil. Biçimi gösterir.

## Tuzaklar

- **Kalibrasyon yok.** İnsan etiketleriyle 0.3 korelasyonlu bir judge gürültüdür. Gönderimden önce bir kalibrasyon çalıştırması gerekir.
- **Kendini değerlendirme.** Aynı LLM'i üretmek ve yargılamak için kullanmak puanları %10-20 şişirir. Judge için farklı bir model ailesi kullanın.
- **Çiftli yargılamada konumsal önyargı.** Judge'lar sunulan ilk seçeneği tercih eder. Her zaman sırayı rastgeleleştirin ve her ikisini de çalıştırın.
- **Ham toplama başarısızlıkları gizler.** Ortalama puan 0.85 genellikle %5 felaket düzeyinde başarısızlığı gizler. Her zaman alt çeyreği (quantile) inceleyin.
- **Altın veri seti çürümesi.** Sürümsüzlü (unversioned) değerlendirme setleri zamanla kayarak Boyner karşılaştırmayı bozar. Veri setini her değişiklikle etiketleyin.
- **LLM maliyeti.** Ölçekte, çağrılar maliyeti hakim eder. Kalibrasyon eşiğini karşılayan en ucuz modeli kullanın. GPT-4o-mini, Claude Haiku, Mistral-small.

## Kullan

2026 stacki:

| Kullanım durumu | Çerçeve |
|---------|-----------|
| RAG kalite izleme | RAGAS (4 metrik) |
| CI/CD gerileme kapıları | DeepEval + pytest |
| Özel alan kriterleri | DeepEval içinde G-Eval |
| Çevrimiçi canlı trafik izleme | Referanssız modda RAGAS |
| İnsan-döngüde (human-in-the-loop) nokta kontrolleri | Anotasyon arayüzü ile LangSmith veya Phoenix |
| Red teaming / güvenlik değerlendirmesi | Promptfoo + DeepEval |

Tipik stack: izleme için RAGAS, CI için DeepEval, yeni boyutlar için G-Eval. Üçünü de çalıştırın; faydalı şekilde anlaşmazlar.

## Ürün Olarak Kullan

`outputs/skill-eval-architect.md` olarak kaydedin:

```markdown
---
name: eval-architect
description: Design an LLM evaluation plan with calibrated judge and CI gates.
version: 1.0.0
phase: 5
lesson: 27
tags: [nlp, evaluation, rag]
---

Given a use case (RAG / agent / generative task), output:

1. Metrics. Faithfulness / relevance / context-precision / context-recall + any custom G-Eval metrics with criteria.
2. Judge model. Named model + version, rationale for cost vs accuracy.
3. Calibration. Hand-labeled set size, target Spearman rho vs human > 0.7.
4. Dataset versioning. Tag strategy, change log, stratification.
5. CI gate. Thresholds per metric, regression-window logic, bottom-quantile alert.

Refuse to rely on a judge untested against ≥50 human-labeled examples. Refuse self-evaluation (same model generates + judges). Refuse aggregate-only reporting without bottom-10% surfacing. Flag any pipeline where judge upgrade lands without parallel baseline eval.
```

#### Açıklama
Verilen kullanım durumu için kalibrasyonlu judge ve CI kapılarıyla bir LLM değerlendirme planı tasarlayan bir skill tanımıdır.

## Alıştırmalar

1. **Kolay.** Bilinen halüsinasyonları olan 10 RAG örneği üzerinde RAGAS kullanın. Sadakat metriğinin her birini yakaladığını doğrulayın.
2. **Orta.** 50 QA cevabını doğruluk için 0-1 arası el ile etiketleyin. G-Eval ile puanlayın. Judge ile insan arasındaki Spearman rho'yu ölçün.
3. **Zor.** DeepEval ile bir pytest CI kapısı kurun. Retriever'ı kasıtlı olarak geriletin. Kapının başarısız olduğunu doğrulayın. En düşük %10 üzerinde eşik kontrolü ile alt çeyrek uyarısı ekleyin.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| LLM-as-judge | LLM ile puanlama | Bir judge modeline rubrik verilerek çıktıların 0-1 puanlanması. |
| RAGAS | RAG metrik kütüphanesi | 4 referanssız RAG metriğine sahip açık kaynak değerlendirme çerçevesi. |
| Sadakat (Faithfulness) | Cevap temellenmiş mi? | Cevap iddialarının getirilen bağlam tarafından desteklenen oranı. |
| Bağlam hassasiyeti (Context precision) | Getirilen parçacıklar ilgili mi? | Gerçekten önemli olan üst-K parçacığın oranı. |
| Bağlam hatırlaması (Context recall) | Getirme her şeyi buldu mu? | Altın cevap iddialarının getirilen parçacıklar tarafından desteklenen oranı. |
| G-Eval | Özel LLM judge | Rubrik + zincirleme düşünüşlü değerlendirme adımları + 0-1 puan. |
| Kalibrasyon | Güven ama doğrula | Judge puanı ile insan puanı arasındaki Spearman korelasyonu. |

## İleri Okuma

- [Es et al. (2023). RAGAS: Automated Evaluation of Retrieval Augmented Generation](https://arxiv.org/abs/2309.15217) — RAGAS makalesi.
- [Liu et al. (2023). G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment](https://arxiv.org/abs/2303.16634) — G-Eval makalesi.
- [DeepEval docs](https://deepeval.com/docs/metrics-introduction) — açık production stacki.
- [Zheng et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) — önyargılar, kalibrasyon, sınırlar.
- [MLflow GenAI Scorer](https://mlflow.org/blog/third-party-scorers) — RAGAS, DeepEval, Phoenix'i entegre eden birleştirici çerçeve.
