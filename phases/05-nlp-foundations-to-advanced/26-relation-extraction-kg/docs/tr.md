# İlişki Çıkarma ve Bilgi Grafiği İnşası

> NER varlıkları buldu. Varlık bağlama (entity linking) bunları çapa aldı. İlişki çıkarma (relation extraction) arasındaki kenarları bulur. Bir bilgi grafiği (knowledge graph), düğümlerin, kenarların ve bunların menşelerinin toplamıdır.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 5 · 06 (NER), Faz 5 · 25 (Varlık Bağlama)
**Süre:** ~60 dakika

## Problem

Bir analist şunu okur: "Tim Cook 2011 yılında Apple'ın CEO'su oldu." Dört olgu:

- `(Tim Cook, role, CEO)`
- `(Tim Cook, employer, Apple)`
- `(Tim Cook, start_date, 2011)`
- `(Apple, type, Organization)`

İlişki çıkarma (RE), serbest metni `(özne, ilişki, nesne)` üçlülerine dönüştürür. Corpus genelinde toplayın, bir bilgi grafiğiniz olur. Toplayın ve sorgulayın, RAG, analitik veya uyumluluk denetimleri için bir çıkarsama tabanınız olur.

2026 problemi: LLM'ler ilişkileri hevesle çıkarır. Çok hevesle. Kaynak metnin desteklemediği üçlüler üretirler (halüsinasyon). Menşe olmadan, gerçek üçlülerin makul kurgudan ayırt edilmesi mümkün değildir. 2026 cevabı, AEVS tarzı çapa-doğrulama pipeline'larıdır.

## Kavram

![Metin → üçlüler → bilgi grafiği](../assets/relation-extraction.svg)

**Üçlü formu.** `(özne_varlığı, ilişki_türü, nesne_varlığı).` İlişkiler kapalı bir ontolojiden (Wikidata özellikleri, FIBO, UMLS) veya açık bir kümeden (OpenIE tarzı, her şey serbest) gelir.

**Üç çıkarma yaklaşımı.**

1. **Kural / kalıp tabanlı.** Hearst kalıpları: "X such as Y" → `(Y, isA, X)`. Artı el yapımı regex. Kırılgan, kesin, açıklanabilir.
2. **Denetimli sınıflandırıcı.** Bir cümledeki iki varlık anısına verildiğinde, sabit bir kümeden ilişkiyi tahmin edin. TACRED, ACE, KBP üzerinde eğitilmiş. 2015–2022 arası standart.
3. **Üretici LLM.** Üçlüleri çıkarması için modele prompt verin. Kutudan çıkar. Menşe gerektirir, aksi halde makul görünen çöp üretir.

**AEVS (Çapa-Çıkarma-Doğrulama-Tamamlama, 2026).** Güncel halüsinasyon hafifletme çerçevesi:

- **Çapa (Anchor).** Her varlık aralığını ve ilişki-finas aralığını kesin konumlarla tanımlayın.
- **Çıkar (Extract).** Çapa aralıklarına bağlı üçlüleri üretin.
- **Doğrula (Verify).** Her üçlü unsurunu kaynak metne geri eşleyin; desteklenmeyen her şeyi reddedin.
- **Tamamla (Supplement).** Bir kapsama geçişi, hiçbir çapa alınmış aralığın düşürülmediğini sağlar.

Halüsinasyonlar keskin şekilde düşer. Daha fazla hesaplama gerektirir ancak denetlenebilir.

**Açık-kapalı takası.**

- **Kapalı ontoloji.** Sabit özellik listesi (örn. Wikidata'nın 11.000+ özelliği). Öngörülebilir. Sorgulanabilir. Uydurulması zor.
- **Açık IE.** Her sözel ifade bir ilişki olur. Yüksek hatırlama (recall). Düşük hassasiyet (precision). Sorgulaması karmaşık.

Production KG'leri genellikle karıştırır: keşif için açık IE, ardından ana grafiğe birleştirmeden önce ilişkileri kapalı bir ontolojiye kanonikleştirme.

## İnşa Et

### Adım 1: kalıp tabanlı çıkarma

```python
PATTERNS = [
    (r"(?P<s>[A-Z]\w+) (?:is|was) (?:a|an|the) (?P<o>[A-Z]?\w+)", "isA"),
    (r"(?P<s>[A-Z]\w+) (?:is|was) born in (?P<o>\w+)", "bornIn"),
    (r"(?P<s>[A-Z]\w+) works? (?:at|for) (?P<o>[A-Z]\w+)", "worksAt"),
    (r"(?P<s>[A-Z]\w+) founded (?P<o>[A-Z]\w+)", "founded"),
]
```

#### Açıklama
Tam oyuncak extractor için `code/main.py`'ye bakın. Hearst kalıpları hâlâ alan-specific pipeline'larda gönderilir çünkü hata ayıklanabilir.

### Adım 2: denetimli ilişki sınıflandırması

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tok = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
model = AutoModelForSequenceClassification.from_pretrained("Babelscape/rebel-large")

text = "Tim Cook was born in Alabama. He later became CEO of Apple."
encoded = tok(text, return_tensors="pt", truncation=True)
output = model.generate(**encoded, max_length=200)
triples = tok.batch_decode(output, skip_special_tokens=False)
```

#### Açıklama
REBEL, seq2seq ilişki extractor'ıdır: metin girer, üçlüler çıkar, zaten Wikimedia özellik kimliklerindedir. Uzaktan denetim (distant supervision) verisi üzerinde fine-tune edilmiş. Standart açık-ağırlık baseline'ı.

### Adım 3: çapalama ile LLM-promptlu çıkarma

```python
prompt = f"""Extract (subject, relation, object) triples from the text.
For each triple, include the exact character span in the source text.

Text: {text}

Output JSON:
[{{"subject": {{"text": "...", "span": [start, end]}},
   "relation": "...",
   "object": {{"text": "...", "span": [start, end]}}}}, ...]

Only include triples fully supported by the text. No inference beyond what is stated.
"""
```

#### Açıklama
Döndürülen her aralığı kaynak metne karşı doğrulayın. `text[start:end] != triple_entity` olan her şeyi reddedin. Bu, AEVS "doğrulama" adımının en minimal biçimidir.

### Adım 4: kapalı bir ontolojiye kanonikleştirme

```python
RELATION_MAP = {
    "is the CEO of": "P169",       # "chief executive officer"
    "was born in":   "P19",         # "place of birth"
    "founded":        "P112",       # "founded by" (inverted subject/object)
    "works at":       "P108",       # "employer"
}


def canonicalize(relation):
    rel_low = relation.lower().strip()
    if rel_low in RELATION_MAP:
        return RELATION_MAP[rel_low]
    return None   # drop unmapped open relations or route to manual review
```

#### Açıklama
Kanonikleştirme genellikle mühendislik işinin %60-80'idir. Bütçe ayırın.

### Adım 5: küçük bir grafik oluşturun ve sorgulayın

```python
triples = extract(text)
graph = {}
for s, r, o in triples:
    graph.setdefault(s, []).append((r, o))


def neighbors(node, relation=None):
    return [(r, o) for r, o in graph.get(node, []) if relation is None or r == relation]


print(neighbors("Tim Cook", relation="P108"))    # -> [(P108, Apple)]
```

#### Açıklama
Bu, her RAG-over-KG sisteminin atomudur. RDF üçlü depoları (Blazegraph, Virtuoso), özellik grafikleri (Neo4j) veya vektör destekli grafik depoları ile ölçeklendirin.

## Tuzaklar

- **RE öncesi özdeşleşme.** "O Apple'ı kurdu" — RE "kimi" bilmesi gerekir. Önce özdeşlemeyi çalıştırın (ders 24).
- **Varlık kanonikleştirme.** "Apple Inc" ve "Apple" aynı düğüme çözülmelidir. Önce varlık bağlama (ders 25).
- **Halüsinasyon üçlüler.** LLM'ler metnin desteklemediği üçlüler üretir. Aralık doğrulaması zorunlu kılın.
- **İlişki kanonikleştirme kayması.** Açık IE ilişkileri tutarsızdır ("born in", "came from", "native of"). Kanonik kimliklere daraltın, aksi halde grafik sorgulanamaz.
- **Zamansal hatalar.** "Tim Cook Apple'ın CEO'su" — şimdi doğru, 2005'te yanlış. Birçok ilişki zamana bağlıdır. Nitelikler (qualifier) kullanın (Wikidata'da `P580` başlangıç zamanı, `P582` bitiş zamanı).
- **Alan uyuşmazlığı.** REBEL Wikipedia üzerinde eğitilmiş. Tıbbi, hukuki ve bilimsel metinler genellikle alan-fine-tune edilmiş RE modelleri gerektirir.

## Kullan

2026 stacki:

| Durum | Seçin |
|-----------|------|
| Hızlı production, genel alan | REBEL veya Wikidata kanonikleştirmeli LlamaPred |
| Alan-specific (biyomedikal, hukuk) | SciREX tarzı alan fine-tune + özel ontoloji |
| LLM-promptlu, denetlenmiş çıktı | AEVS pipeline'ı: çapa → çıkar → doğrula → tamamla |
| Yüksek hacimli haber IE | Kalıp tabanlı + denetimli hibrit |
| Sıfırdan KG oluşturma | Açık IE + manuel kanonikleştirme geçişi |
| Zamansal KG | Niteliklerle çıkarma (başlangıç/bitiş zamanı, zaman noktası) |

Entegrasyon kalıbı: NER → özdeşleme → varlık bağlama → ilişki çıkarma → ontoloji eşleme → grafik yükleme. Her aşama bir potansiyel kalite kapısıdır.

## Ürün Olarak Kullan

`outputs/skill-re-designer.md` olarak kaydedin:

```markdown
---
name: re-designer
description: Design a relation extraction pipeline with provenance and canonicalization.
version: 1.0.0
phase: 5
lesson: 26
tags: [nlp, relation-extraction, knowledge-graph]
---

Given a corpus (domain, language, volume) and downstream use (KG-RAG, analytics, compliance), output:

1. Extractor. Pattern-based / supervised / LLM / AEVS hybrid. Reason tied to precision vs recall target.
2. Ontology. Closed property list (Wikidata / domain) or open IE with canonicalization pass.
3. Provenance. Every triple carries source char-span + doc id. Non-negotiable for audit.
4. Merge strategy. Canonical entity id + relation id + temporal qualifiers; dedup policy.
5. Evaluation. Precision / recall on 200 hand-labelled triples + hallucination-rate on LLM-extracted sample.

Refuse any LLM-based RE pipeline without span verification (source provenance). Refuse open-IE output flowing into a production graph without canonicalization. Flag pipelines with no temporal qualifier on time-bounded relations (employer, spouse, position).
```

#### Açıklama
Verilen corpus ve aşağı akış kullanımı için menşeli ve kanonikleştirmeli bir ilişki çıkarma pipeline'ı tasarlayan bir skill tanımıdır.

## Alıştırmalar

1. **Kolay.** `code/main.py`'deki kalıp extractor'ı 5 haber cümlesi üzerinde çalıştırın. Hassasiyeti el ile kontrol edin.
2. **Orta.** Aynı cümlelerde REBEL (veya küçük bir LLM) kullanın. Üçlüleri karşılaştırın. Hangi extractor daha yüksek hassasiyete sahip? Daha yüksek hatırlamaya?
3. **Zor.** AEVS pipeline'ını kurun: LLM ile çıkarım + kaynak ile aralık doğrulama. Doğrulama adımından önce ve sonra halüsinasyon oranını 50 Vikipedi tarzı cümle üzerinde ölçün.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Üçlü | Özne-ilişki-nesne | KG'nin atomik birimi olan `(s, r, o)` demeti. |
| Açık IE | Her şeyi çıkar | Açık sözlüklü ilişki ifadeleri; yüksek hatırlama, düşük hassasiyet. |
| Kapalı ontoloji | Sabit şema | Sınırlı ilişki türü kümesi (Wikidata, UMLS, FIBO). |
| Kanonikleştirme | Her şeyi normalleştir | Yüzey adlarını / ilişkilerini kanonik kimliklere eşle. |
| AEVS | Temellenmiş çıkarma | Çapa-Çıkarma-Doğrulama-Tamamlama pipeline'ı (2026). |
| Menşe (Provenance) | Doğruluk kaynağı bağlantısı | Her üçlü bir doc id + karakter aralığı taşır. |
| Uzaktan denetim | Ucuz etiketler | Mevcut bir KG ile metni hizalayarak eğitim verisi oluşturma. |

## İleri Okuma

- [Mintz et al. (2009). Distant supervision for relation extraction without labeled data](https://www.aclweb.org/anthology/P09-1113.pdf) — uzaktan denetim makalesi.
- [Huguet Cabot, Navigli (2021). REBEL: Relation Extraction By End-to-end Language generation](https://aclanthology.org/2021.findings-emnlp.204.pdf) — seq2seq REWorking horse.
- [Wadden et al. (2019). Entity, Relation, and Event Extraction with Contextualized Span Representations (DyGIE++)](https://arxiv.org/abs/1909.03546) — ortak IE.
- [AEVS — Anchor-Extraction-Verification-Supplement framework](https://www.mdpi.com/2073-431X/15/3/178) — 2026 halüsinasyon hafifletme tasarımı.
- [Wikidata SPARQL tutorial](https://www.wikidata.org/wiki/Wikidata:SPARQL_tutorial) — kanonik grafik sorguları.
