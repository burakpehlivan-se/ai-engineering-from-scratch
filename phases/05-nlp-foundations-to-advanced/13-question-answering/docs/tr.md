# Soru-Cevap Sistemleri

> Modern QA'yı şekillendiren üç sistem vardı. Öztüretici (extractive) aralıkları buldu. Retrieval-augmented bunları belgelerde temellendirdi. Üretici (generative) cevapları üretti. Her modern AI asistanı bu üçünün karışımıdır.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 5 · 11 (Makine Çevirisi), Faz 5 · 10 (Attention Mechanism)
**Süre:** ~75 dakika

## Problem

Bir kullanıcı "İlk iPhone ne zaman çıktı?" diye yazar ve "29 Haziran 2007" yanıtını bekler. "Apple'ın geçmişi uzun ve çeşitli" değil. "2007" tek başına bir cümle olmadan değil. Doğrudan, temellenmiş, doğru bir cevap.

Son on yılda üç mimari QA'ya hakim olmuştur:

- **Öztüretici QA.** Bir soru ve cevabı içerdiği bilinen bir paragraf verildiğinde, paragraf içindeki cevap aralığının başlangıç ve bitiş endekslerini bulun. SQuAD klasik benchmarktır.
- **Açık alan QA.** Paragraf verilmez. Önce ilgili paragrafı getirin (retrieve), sonra cevabı çıkarın veya üretin. Bugün her RAG pipeline'ının temelidir.
- **Üretici / Kapalı kitap QA.** Büyük bir dil modeli (LLM) parametrik hafızasından cevap verir. Retrieval yok. Çıkarımda en hızlı, gerçeklerde en az güvenilir.

2026 trendi hibrittir: en iyi birkaç paragrafı getirin, sonra bir üretici modele bu paragraflara dayanarak cevap üretmesi için prompt verin. Bu RAG'tır ve ders 14 retrieval kısmını derinlemesine ele alır. Bu ders QA kısmını inşa eder.

## Kavram

![QA architectures: extractive, retrieval-augmented, generative](../assets/qa.svg)

**Öztüretici.** Soru ve paragrafı birlikte transformer (BERT ailesi) ile kodlar. İki baş eğitir: cevap token'larının başlangıç ve bitiş endekslerini tahmin eder. Kayıp, geçerli pozisyonlar üzerinde cross-entropy'dir. Çıktı paragraftan bir aralıktır (span). Halüsinasyon yapmaz (yapısal olarak), paragrafın cevaplayamadığı soruları işlemez (yapısal olarak).

**Retrieval-augmented (RAG).** İki aşama. İlk olarak, bir retriever corpus'tan en iyi `k` paragrafı bulur. İkinci olarak, bir reader (öztüretici veya üretici) bu paragrafları kullanarak cevabı üretir. Retriever-reader ayrımı, her birinin bağımsız olarak eğitilmesini ve değerlendirilmesini sağlar. Modern RAG genellikle aralarına bir reranker ekler.

**Üretici.** Sadece decoder'a sahip bir LLM (GPT, Claude, Llama) öğrenilmiş ağırlıklardan cevap verir. Retrieval adımı yok. Ortak bilgide mükemmel, nadir veya güncel gerçeklerde felaket. Halüsinasyon oranı, ön-eğitim verisindeki gerçek sıklığıyla ters orantılıdır.

## İnşa Et

### Adım 1: önceden eğitilmiş model ile öztüretici QA

```python
from transformers import pipeline

qa = pipeline("question-answering", model="deepset/roberta-base-squad2")

passage = (
    "Apple Inc. released the first iPhone on June 29, 2007. "
    "The device was announced by Steve Jobs at Macworld in January 2007."
)
question = "When was the first iPhone released?"

answer = qa(question=question, context=passage)
print(answer)
```

```python
{'score': 0.98, 'start': 57, 'end': 70, 'answer': 'June 29, 2007'}
```

#### Açıklama
`deepset/roberta-base-squad2`, cevaplanamayan soruları da içeren SQuAD 2.0 üzerinde eğitilmiştir. Varsayılan olarak `question-answering` pipeline'ı modelin null skoru kazandığında bile en yüksek puanlı aralığı döndürür — otomatik olarak boş cevap dönmez. Açıkça "cevap yok" davranışı için pipeline çağrısına `handle_impossible_answer=True` ekleyin; pipeline, null skor her aralık skorunu aştığında yalnızca boş cevap döndürür. Her iki durumda da `score` alanını kontrol edin.

`deepset/roberta-base-squad2`, cevaplanamayan soruları da içeren SQuAD 2.0 üzerinde eğitilmiştir. Varsayılan olarak `question-answering` pipeline'ı, modelin null skoru kazandığında bile en yüksek puanlı aralığı döndürür — otomatik olarak boş cevap dönmez. Açıkça "cevap yok" davranışı için pipeline çağrısına `handle_impossible_answer=True` ekleyin. Her durumda `score` alanını kontrol edin.

### Adım 2: retrieval-augmented pipeline (taslak)

```python
from sentence_transformers import SentenceTransformer
import numpy as np

encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

corpus = [
    "Apple Inc. released the first iPhone on June 29, 2007.",
    "Macworld 2007 featured the iPhone announcement by Steve Jobs.",
    "Android launched in 2008 as Google's mobile operating system.",
    "The first iPod was released in 2001.",
]
corpus_embeddings = encoder.encode(corpus, normalize_embeddings=True)


def retrieve(question, top_k=2):
    q_emb = encoder.encode([question], normalize_embeddings=True)
    sims = (corpus_embeddings @ q_emb.T).squeeze()
    order = np.argsort(-sims)[:top_k]
    return [corpus[i] for i in order]


def answer(question):
    passages = retrieve(question, top_k=2)
    combined = " ".join(passages)
    return qa(question=question, context=combined)


print(answer("When was the first iPhone released?"))
```

#### Açıklama
Bu, iki aşamalı bir pipeline örneğidir. Yoğun retriever (Sentence-BERT), anlamsal benzerlikle ilgili paragrafları bulur. Öztüretici reader (RoBERTa-SQuAD), birleştirilmiş en iyi paragraflardan cevap aralığını çeker. Küçük corpus'larda çalışır. Milyonlarca belgelik bir corpus için FAISS veya bir vektör veritabanı kullanın.

İki aşamalı pipeline. Yoğun retriever (Sentence-BERT), anlamsal benzerlikle ilgili paragrafları bulur. Öztüretici reader (RoBERTa-SQuAD), birleştirilmiş en iyi paragraflardan cevap aralığını çeker. Küçük corpus'larda çalışır. Milyonlarca belgelik bir corpus için FAISS veya bir vektör veritabanı kullanın.

### Adım 3: RAG ile üretici QA

```python
def rag_generate(question, llm):
    passages = retrieve(question, top_k=3)
    prompt = f"""Context:
{chr(10).join('- ' + p for p in passages)}

Question: {question}

Answer using only the context above. If the context does not contain the answer, say "I don't know."
"""
    return llm(prompt)
```

#### Açıklama
Bu, RAG (Retrieval-Augmented Generation) yaklaşımının basit bir uygulamasıdır. Modeli bağlamda temellendirmesi ve yetersiz bağlamda "Bilmiyorum" demesi için açıkça yönlendirmek, saf prompting'e kıyasla halüsinasyon oranlarını %40-60 azaltır. Daha karmaşık kalıplar alıntılar, güven skorları ve yapılandırılmış çıkarım ekler.

Prompt kalıpları önemlidir. Modeli bağlamda temellendirmesi ve bağlam yetersiz olduğunda "Bilmiyorum" demesi için açıkça yönlendirmek, saf prompting'e kıyasla halüsinasyon oranlarını %40-60 azaltır. Daha karmaşık kalıplar alıntılar, güven skorları ve yapılandırılmış çıkarım ekler.

### Adım 4: gerçek dünyayı yansıtan değerlendirme

SQuAD **Tam Eşleşme (EM)** ve **token düzeyinde F1** kullanır. EM, normalleştirmeden sonra katı bir eşlemedir (küçük harf, noktalama işaretlerini kaldırma, artikelleri çıkarma) — tahmin ya tam olarak eşleşir ya da 0 puan alır. F1, tahmin ile reference arasındaki token örtüşmesi üzerine hesaplanır ve kısmi puan verir. Her ikisi de paraphrase'leri eksik değerlendirir: "29 Haziran 2007" vs "29 Haziran 2007" genellikle 0 EM alır (sıralı sayı normalleştirmeyi bozar) ancak örtüşen token'lardan önemli F1 kazanır.

Production QA için:

- **Cevap doğruluğu** (LLM-judge veya insan-judge, çünkü metrikler anlamsal eşdeğerliği yakalayamaz).
- **Alıntı doğruluğu.** Alıntılanan paragraf gerçekten cevabı destekliyor mu? Üretilen alıntılar ile getirilen paragraflar arasındaki string eşleşmesiyle otomatik olarak kontrol edilebilir.
- **Reddetme kalibrasyonu.** Cevap getirilen paragraflarda olmadığında, sistem doğru bir şekilde "Bilmiyorum" diyor mu? Yanlış güven oranını ölçün.
- **Retrieval hatırlaması.** Reader'ı değerlendirmeden önce, retriever'ın doğru paragrafı en iyi `k`'ya getirip getirmediğini ölçün. Reader eksik bir paragrafı düzeltemez.

### RAGAS: 2026 production değerlendirme çerçevesi

`RAGAS`, RAG sistemleri için özel olarak oluşturulmuştur ve 2026'da production varsayılanıdır. Gold reference gerektirmeden dört boyutu puanlar:

- **Sadakat (Faithfulness).** Cevaptaki her iddia getirilen bağlamdan mı geliyor? NLI tabanlı çıkarım ile ölçülür. Birincil halüsinasyon metriğiniz.
- **Cevap ilgisi (Answer relevance).** Cevap soruyu ele alıyor mu? Cevaptan hipotez sorular üretilerek gerçek soruyla karşılaştırılır.
- **Bağlam hassasiyeti (Context precision).** Getirilen parçacıklardan kaçı gerçekten ilgiliydi? Düşük hassasiyet = prompt'ta gürültü.
- **Bağlam hatırlaması (Context recall).** Getirilen set gerekli tüm bilgileri içeriyor mu? Düşük hatırlama = reader başarılı olamaz.

Reference-free puanlama, özenle hazırlanmış gold cevaplar olmadan canlı production trafiğinde değerlendirmenizi sağlar. Tam eşleşme metriklerinin işe yaramadığı açık uçlu sorular için LLM-as-judge'ü üzerine katmanlayın.

`pip install ragas`. Retriever + reader'ınızı takın. Sorgu başına dört skaler elde edin. Gerilemelere karşı alarm verin.

## Kullan

2026 stacki.

| Kullanım durumu | Önerilen |
|---------|-------------|
| Verilen paragraf, cevap aralığını bul | `deepset/roberta-base-squad2` |
| Sabit corpus üzerinde, kapalı kitap kabul edilemez | RAG: yoğun retriever + LLM reader |
| Belge deposu üzerinde gerçek zamanlı | Hibrit (BM25 + yoğun) retriever + reranker ile RAG (ders 14) |
| Gesprächsel QA (takip soruları) | Sohbet geçmişi olan LLM + her turda RAG |
| Yüksek derece gerçek, düzenlenmiş alanlar | Otoriter bir corpus üzerinde öztüretici; asla yalnızca üretici |

2026'da öztüretici QA modası geçmiştir çünkü LLM'li RAG daha fazla durumu ele alır. Ancak birebir alıntı gerektiren bağlamda hâlâ kullanılır: hukuki araştırma, düzenleyici uyumluluk, denetim araçları.

## Ürün Olarak Kullan

`outputs/skill-qa-architect.md` olarak kaydedin:

```markdown
---
name: qa-architect
description: Choose QA architecture, retrieval strategy, and evaluation plan.
version: 1.0.0
phase: 5
lesson: 13
tags: [nlp, qa, rag]
---

Given requirements (corpus size, question type, factuality constraint, latency budget), output:

1. Architecture. Extractive, RAG with extractive reader, RAG with generative reader, or closed-book LLM. One-sentence reason.
2. Retriever. None, BM25, dense (name the encoder), or hybrid.
3. Reader. SQuAD-tuned model, LLM by name, or "domain-fine-tuned DistilBERT."
4. Evaluation. EM + F1 for extractive benchmarks; answer accuracy + citation accuracy + refusal calibration for production. Name what you are measuring and how you are measuring it.

Refuse closed-book LLM answers for regulatory or compliance-sensitive questions. Refuse any QA system without a retrieval-recall baseline (you cannot evaluate the reader without knowing the retriever surfaced the right passage). Flag questions that require multi-hop reasoning as needing specialized multi-hop retrievers like HotpotQA-trained systems.
```

#### Açıklama
Bu, gereksinimler verildiğinde QA mimarisi, retrieval stratejisi ve değerlendirme planı seçen bir skill tanımıdır.

## Alıştırmalar

1. **Kolay.** Yukarıdaki SQuAD öztüretici pipeline'ını 10 Vikipedi paragrafı üzerinde kurun. 10 soruyu el yapımı olarak oluşturun. Cevabın ne sıklıkla doğru olduğunu ölçün. Paragraflar ve sorular temizse 7-9 arası doğru görmelisiniz.
2. **Orta.** Bir reddetme sınıflandırıcısı ekleyin. En yüksek retrieval skoru bir eşiğin (örn. 0.3 cosinüs) altında olduğunda, reader'ı çağırmak yerine "Bilmiyorum" döndürün. Eşiği ayrılmış bir set üzerinde ayarlayın.
3. **Zor.** Seçtiğiniz 10.000 belgelik bir corpus üzerinde bir RAG pipeline'ı kurun. Hibrit retrieval'ı (BM25 + yoğun) RRF füzyonu ile uygulayın (ders 14'e bakın). Hibrit adımı olmadan ve onunla cevap doğruluğunu ölçün. Hangi soru türlerinin en çok faydalandığını belgeleyin.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Öztüretici QA | Cevap aralığını bul | Verilen paragraf içinde cevabın başlangıç ve bitiş endekslerini tahmin et. |
| Açık alan QA | Corpus üzerinde QA | Verilmiş paragraf yok; önce getir sonra cevapla. |
| RAG | Getir sonra üret | Retrieval-augmented generation. Retriever + reader pipeline'ı. |
| SQuAD | Klasik benchmark | Stanford Question Answering Dataset. EM + F1 metrikleri. |
| Halüsinasyon | Uydurma cevap | Reader çıktısı getirilen bağlam tarafından desteklenmiyor. |
| Reddetme kalibrasyonu | Ne zaman susacağını bilme | Sistem cevaplayamadığında doğru bir şekilde "Bilmiyorum" diyor. |

## İleri Okuma

- [Rajpurkar et al. (2016). SQuAD: 100,000+ Questions for Machine Comprehension of Text](https://arxiv.org/abs/1606.05250) — benchmark makalesi.
- [Karpukhin et al. (2020). Dense Passage Retrieval for Open-Domain QA](https://arxiv.org/abs/2004.04906) — DPR, QA için klasik yoğun retriever.
- [Lewis et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) — RAG'a isim veren makale.
- [Gao et al. (2023). Retrieval-Augmented Generation for Large Language Models: A Survey](https://arxiv.org/abs/2312.10997) — kapsamlı RAG anketi.