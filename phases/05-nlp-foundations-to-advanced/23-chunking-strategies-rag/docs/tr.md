# RAG için Parçalama Stratejileri

> Parçalama yapılandırması, getirme kalitesini embedding modeli seçimi kadar etkiler (Vectara NAACL 2025). Parçalamayı yanlış yaparsanız yeniden sıralama (reranking) sizi kurtarmaz.

**Tür:** İnşa
**Diller:** Python
**Önkoşullar:** Faz 5 · 14 (Bilgi Getirme), Faz 5 · 22 (Embedding Modelleri)
**Süre:** ~60 dakika

## Sorun

50 sayfalık bir sözleşmeyi bir RAG sistemine koydunuz. Kullanıcı soruyor: "Fesih maddesi ne?" Getirici (retriever) kapak sayfasını getiriyor. Neden? Çünkü model 512 token'lık parçacıklarla eğitilmiş ve fesih maddesi 20. sayfada, sayfa sonu bölünmesiyle, sorguyu yerel anahtar sözcüklerle bağlayan hiçbir şey olmadan oturuyor.

Çözüm "daha iyi bir embedding modeli satın almak" değil. Çözüm parçalama. Ne kadar büyük? Örtüşme (overlap)? Nerede bölünsün? Çevresel bağlamla birlikte mi?

Şubat 2026 benchmark'ları şaşırtıcı sonuçlar gösteriyor:

- Vectara'nın 2026 çalışması: özyinelemeli (recursive) 512 token parçalama, anlamsal (semantic) parçalamayı %69 → %54 doğrulukla yendi.
- SPLADE + Mistral-8B Natural Questions'ta: örtüşme sıfır ölçülebilir fayda sağladı.
- Bağlam kayalığı (context cliff): yanıt kalitesi yaklaşık 2.500 token bağlam civarında keskin düşüş gösterir.

"Açık" cevap (anlamsal parçalama, %20 örtüşme, 1000 token) genellikle yanlıştır. Bu ders altı strateji için sezgi geliştirir ve hangisine ne zaman başvuracağınızı söyler.

## Kavram

![Bir parçacık üzerinde altı parçalama stratejisinin görselleştirilmesi](../assets/chunking.svg)

**Sabit parçalama (Fixed chunking).** Her N karakter veya token'da böl. En basit temel. Cümle ortasında keser. İyi sıkıştırma, kötü tutarlılık.

**Özyinelemeli (Recursive).** LangChain'in `RecursiveCharacterTextSplitter`'ı. Önce `\n\n` üzerinde bölmayı deneyin, sonra `\n`, sonra `.`, sonra boşluk. Düzgün geri düşer. 2026 varsayılanı.

**Anlamsal (Semantic).** Her cümleyi kodlayın. Bitişik cümleler arasında kosinüs benzerliğini hesaplayın. Benzerlik eşik değerinin altına düştüğü yerde böl. Konu tutarlılığını korur. Daha yavaş; bazen getirmeyi olumsuz etkileyen 40 token'lık küçük parçacıklar üretir.

**Cümle (Sentence).** Cümle sınırlarında böl. Parçacık başına bir cümle veya N cümlelik pencere. 5k token'a kadar anlamsal parçalamayla eşleşir, maliyetinin kesirinde.

**Ebeveyn belge (Parent-document).** Küçük çocuk parçacıklarını getirme için saklayın *ve* daha büyük ebeveyn parçacığını bağlam için saklayın. Çocukla getirin; ebeveyni döndürün. Kusurlu儿童 parçacıkları bile makul ebeveynler döndürür.

**Geç parçalama (Late chunking, 2024).** Önce tüm belgeyi token düzeyinde kodlayın, ardından token embedding'lerini parçacık embedding'lerine havuzlayın (pool). Çapraz parçacık bağlamını korur. Uzun bağlam kodlayıcılarıyla çalışır (BGE-M3, Jina v3). Daha yüksek hesaplama.

**Bağlamalı getirme (Contextual retrieval, Anthropic, 2024).** Her parçacığın belge içindeki konumunu özetleyen bir LLM üretilen özet ekleyin ("Bu parçacık fesih maddelerinin 3.2 bölümü..."). Anthropic'in kendi benchmark'ında %35-50 getirme iyileştirmesi. İndeksleme pahalı.

### Her varsayımanı yenen kural

Parçacık boyutunu sorgu türüyle eşleştirin:

| Sorgu türü | Parçacık boyutu |
|------------|-----------|
| Olgusal ("CEO'nun adı ne?") | 256-512 token |
| Analitik / çoklu adım | 512-1024 token |
| Bütün bölüm kavrama | 1024-2048 token |

NVIDIA'nın 2026 benchmark'ı. Parçacık, cevabı artı yerel bağlamı içerecek kadar büyük, getiricinin üst-K'sının cevaba odaklanmasını sağlayacak kadar küçük olmalıdır.

## İnşa Et

### Adım 1: sabit ve özyinelemeli parçalama

```python
def chunk_fixed(text, size=512, overlap=0):
    step = size - overlap
    return [text[i:i + size] for i in range(0, len(text), step)]


def chunk_recursive(text, size=512, seps=("\n\n", "\n", ". ", " ")):
    if len(text) <= size:
        return [text]
    for sep in seps:
        if sep not in text:
            continue
        parts = text.split(sep)
        chunks = []
        buf = ""
        for p in parts:
            if len(p) > size:
                if buf:
                    chunks.append(buf)
                    buf = ""
                chunks.extend(chunk_recursive(p, size=size, seps=seps[1:] or (" ",)))
                continue
            candidate = buf + sep + p if buf else p
            if len(candidate) <= size:
                buf = candidate
            else:
                if buf:
                    chunks.append(buf)
                buf = p
        if buf:
            chunks.append(buf)
        return [c for c in chunks if c.strip()]
    return chunk_fixed(text, size)
```

#### Açıklama
Bu kod, sabit ve özyinelemeli parçalama stratejilerini uygular. Sabit parçalama belirli aralıklarla bölerken, özyinelemeli parçalama ayırıcılara göre öncelikli olarak böler ve daha doğal parçacıklar üretir.

### Adım 2: anlamsal parçalama

```python
def chunk_semantic(text, encoder, threshold=0.6, min_chars=200, max_chars=2048):
    sentences = split_sentences(text)
    if not sentences:
        return []
    embs = encoder.encode(sentences, normalize_embeddings=True)
    chunks = [[sentences[0]]]
    for i in range(1, len(sentences)):
        sim = float(embs[i] @ embs[i - 1])
        current_len = sum(len(s) for s in chunks[-1])
        if sim < threshold and current_len >= min_chars:
            chunks.append([sentences[i]])
        else:
            chunks[-1].append(sentences[i])

    result = []
    for group in chunks:
        text_group = " ".join(group)
        if len(text_group) > max_chars:
            result.extend(chunk_recursive(text_group, size=max_chars))
        else:
            result.append(text_group)
    return result
```

#### Açıklama
Bu kod, anlamsal parçalama uygular. Bitişik cümlelerin embedding benzerliğini hesaplar ve benzerlik eşik değerinin altına düştüğü yerde böler. `threshold` değerini kendi alanınızda ayarlayın.

`threshold` değerini kendi alanınızda ayarlayın. Çok yüksek → parçacıklar. Çok düşük → devasa bir parçacık.

### Adım 3: ebeveyn belge

```python
def chunk_parent_child(text, parent_size=2048, child_size=256):
    parents = chunk_recursive(text, size=parent_size)
    mapping = []
    for p_idx, parent in enumerate(parents):
        children = chunk_recursive(parent, size=child_size)
        for child in children:
            mapping.append({"child": child, "parent_idx": p_idx, "parent": parent})
    return mapping


def retrieve_parent(child_query, mapping, encoder, top_k=3):
    child_embs = encoder.encode([m["child"] for m in mapping], normalize_embeddings=True)
    q_emb = encoder.encode([child_query], normalize_embeddings=True)[0]
    scores = child_embs @ q_emb
    top = np.argsort(-scores)[:top_k]
    seen, parents = set(), []
    for i in top:
        if mapping[i]["parent_idx"] not in seen:
            parents.append(mapping[i]["parent"])
            seen.add(mapping[i]["parent_idx"])
    return parents
```

#### Açıklama
Bu kod, ebeveyn-çocuk parçalama stratejisini uygular. Küçük çocuk parçacıklarıyla getirme yapılır, ancak daha büyük ebeveyn parçacıkları döndürülür. Anahtar bilgi: ebeveynleri tekrarlayın. Birden fazla çocuk aynı ebeveynle eşleşebilir; tümünü döndürmek bağlamı boşa harcar.

Temel bilgi: ebeveynleri tekrarlayın (dedupe). Birden fazla çocuk aynı ebeveynle eşleşebilir; tümünü döndürmek bağlamı boşa harcar.

### Adım 4: bağlamalı getirme (Anthropic modeli)

```python
def contextualize_chunks(document, chunks, llm):
    context_prompts = [
        f"""<document>{document}</document>
Here is the chunk to situate: <chunk>{c}</chunk>
Write 50-100 words placing this chunk in the document's context."""
        for c in chunks
    ]
    contexts = llm.batch(context_prompts)
    return [f"{ctx}\n\n{c}" for ctx, c in zip(contexts, chunks)]
```

#### Açıklama
Bu kod, her parçacığa belge içindeki konumunu açıklayan bir LLM özet ekler. Bağlamalılaştırılmış parçacıkları indeksleyin. Sorgu anında getirme ekstra çevresel sinyalden faydalanır.

Bağlamalılaştırılmış parçacıkları indeksleyin. Sorgu anında getirme ekstra çevresel sinyalden faydalanır.

### Adım 5: değerlendirme

```python
def recall_at_k(queries, corpus_chunks, encoder, k=5):
    chunk_embs = encoder.encode(corpus_chunks, normalize_embeddings=True)
    hits = 0
    for q_text, gold_idxs in queries:
        q_emb = encoder.encode([q_text], normalize_embeddings=True)[0]
        top = np.argsort(-(chunk_embs @ q_emb))[:k]
        if any(i in gold_idxs for i in top):
            hits += 1
    return hits / len(queries)
```

#### Açıklama
Bu kod, recall@k metriğini hesaplar. Her sorgu için en iyi k parçacık içinde altın dizinlerden herhangi biri varsa isabet sayılır.

Her zaman benchmark çalıştırın. Corpusunuz için en iyi strateji herhangi bir blog yazısıyla eşleşmeyebilir.

## Tuzaklar

- **Yalnızca olgusal sorgularda değerlendirme.** Çoklu adım sorguları çok farklı kazananları ortaya çıkarır. Sorgu türüne göre ayrılmış (stratified) bir değerlendirme kümesi kullanın.
- **Minimum boyut olmadan anlamsal parçalama.** Getirmeyi olumsuz etkileyen 40 token'lık parçacıklar üretir. Her zaman `min_tokens` uygulayın.
- **Örtüşmeyi kült olarak uygulama.** 2026 çalışmaları, örtüşmenin genellikle sıfır fayda sağladığını ve indeks maliyetini ikiye katladığını buluyor. Önermeyin, ölçün.
- **Min/maks uygulaması olmama.** 5 token veya 5000 token'lık parçacıklar getirmeyi bozar. Sınırlayın.
- **Çapraz belge parçalama.** Hiçbir zaman bir parçacığın iki belgeyi kapsamamasına izin verin. Her zaman belge başına parçalayın, ardından birleştirin.

## Kullan

2026 yığını:

| Durum | Strateji |
|-----------|----------|
| İlk inşa, bilinmeyen corpus | Özyinelemeli, 512 token, örtüşme yok |
| Olgusal Soru Cevaplama | Özyinelemeli, 256-512 token |
| Analitik / çoklu adım | Özyinelemeli, 512-1024 token + ebeveyn belge |
| Aşırı çapraz referans (sözleşmeler, makaleler) | Geç parçalama veya bağlamalı getirme |
| Konuşma / diyalog corpusu | Tur düzeyinde parçacıklar + konuşmacı meta verisi |
| Kısa ifadeler (tweet, yorum) | Bir belge = bir parçacık |

Özyinelemeli 512 ile başlayın. 50 sorguluk bir değerlendirme kümesinde recall@5 ölçün. Oradan ayarlayın.

## Teslim Et

`outputs/skill-chunker.md` olarak kaydedin:

```markdown
---
name: chunker
description: Pick a chunking strategy, size, and overlap for a given corpus and query distribution.
version: 1.0.0
phase: 5
lesson: 23
tags: [nlp, rag, chunking]
---

Given a corpus (document types, avg length, domain) and query distribution (factoid / analytical / multi-hop), output:

1. Strategy. Recursive / sentence / semantic / parent-document / late / contextual. Reason.
2. Chunk size. Token count. Reason tied to query type.
3. Overlap. Default 0; justify if >0.
4. Min/max enforcement. `min_tokens`, `max_tokens` guards.
5. Evaluation plan. Recall@5 on 50-query stratified eval set (factoid, analytical, multi-hop).

Refuse any chunking strategy without min/max chunk size enforcement. Refuse overlap above 20% without an ablation showing it helps. Flag semantic chunking recommendations without a min-token floor.
```

#### Açıklama
Bu şablon, bir corpus ve sorgu dağılımı için parçalama stratejisi seçen bir yetenek tanımıdır.

## Alıştırmalar

1. **Kolay.** Bir 20 sayfalık belgeyi sabit(512, 0), özyinelemeli(512, 0) ve özyinelemeli(512, 100) ile parçalayın. Parçacık sayılarını ve sınır kalitesini karşılaştırın.
2. **Orta.** 5 belge üzerinde 30 sorguluk bir değerlendirme kümesi oluşturun. Özyinelemeli, anlamsal ve ebeveyn belge için recall@5 ölçün. Hangisi kazanır? Blog yazılarıyla eşleşiyor mu?
3. **Zor.** Bağlamalı getirme uygulayın. Temel özyinelemeliye göre MRR iyileştirmesini ölçün. Dizin maliyetini (LLM çağrıları) vs doğruluk artışını raporlayın.

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Parçacık (Chunk) | Belgenin bir parçası | Kodlanan, indekslenen ve getirilen alt belge birimi. |
| Örtüşme (Overlap) | Güvenlik payı | Bitişik parçacıklar arasında paylaşılan N token; 2026 benchmark'larında genellikle işe yaramaz. |
| Anlamsal parçalama (Semantic chunking) | Akıllı parçalama | Bitişik cümle embedding benzerliğinin düştüğü yerde böl. |
| Ebeveyn belge (Parent-document) | İki düzeyli getirme | Küçük çocukları getir, daha büyük ebeveynleri döndür. |
| Geç parçalama (Late chunking) | Embedding sonrası parçalama | Tüm belgeyi token düzeyinde kodla, parçacık vektörlerine havuzla. |
| Bağlamalı getirme (Contextual retrieval) | Anthropic'in hilesi | İndeksleme öncesi her parçacığa LLM üretilen özet ekle. |
| Bağlam kayalığı (Context cliff) | 2500 token duvarı | RAG'da yaklaşık 2.5k bağlam token'ında gözlenen kalite düşüşü (Ocak 2026). |

## İleri Okuma

- [Yepes vd. / LangChain — Recursive Character Splitting dokümanları](https://python.langchain.com/docs/how_to/recursive_text_splitter/) — üretimde varsayılan.
- [Vectara (2024, NAACL 2025). Chunking configurations analysis](https://arxiv.org/abs/2410.13070) — parçalama embedding seçimi kadar önemlidir.
- [Jina AI — Long-Context Embedding Modellerinde Geç Parçalama (2024)](https://jina.ai/news/late-chunking-in-long-context-embedding-models/) — geç parçalama makalesi.
- [Anthropic — Bağlamalı Getirme](https://www.anthropic.com/news/contextual-retrieval) — LLM üretilen bağlam önekleriyle %35-50 getirme iyileştirmesi.
- [NVIDIA 2026 parçacık boyutu benchmark'ı — Premai özeti](https://blog.premai.io/rag-chunking-strategies-the-2026-benchmark-guide/) — sorgu türüne göre parçacık boyutu.