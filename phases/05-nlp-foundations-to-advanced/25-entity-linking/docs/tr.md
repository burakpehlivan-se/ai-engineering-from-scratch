# Varlık Bağlantı ve Karışıklık Giderme

> NER "Paris" buldu. Varlık bağlantısı (entity linking) karar veriyor: Paris, Fransa mı? Paris Hilton mu? Paris, Teksas mı? Paris (Truhan prensi mi)? Bağlantı yapmadan, bilgi grafiğiniz belirsiz kalır.

**Tür:** İnşa
**Diller:** Python
**Önkoşullar:** Faz 5 · 06 (NER), Faz 5 · 24 (Coreference Çözümlemesi)
**Süre:** ~60 dakika

## Sorun

Bir cümle şöyle diyor: "Jordan basını yendi." NER, "Jordan"ı KİŞİ olarak etiketliyor. Güzel. Ama *hangi* Jordan?

- Michael Jordan (basketbol)?
- Michael B. Jordan (oyuncu)?
- Michael I. Jordan (Berkeley ML profesörü — evet, bu karışıklık ML makalelerinde gerçek)?
- Jordan (ülke)?
- Jordan (İbranice erkek adı)?

Varlık bağlantısı (EL), her bahsi bir bilgi tabanındaki (Wikidata, Wikipedia, DBpedia veya alan bilgi tabanınız) benzersiz bir girişe çözümlediğinde iki alt görev vardır:

1. **Aday oluşturma.** "Jordan" verildiğinde, hangi bilgi tabanı girişleri olası?
2. **Karışıklık giderme.** Bağlam verildiğinde, hangi aday doğru olan?

Her iki adım da öğrenilebilir. Her ikisi de benchmark edilmiştir. Birleşik boru hattı on yıldır stabil — değişen karıştırıcının (disambiguator) kalitesidir.

## Kavram

![Varlık bağlantısı boru hattı: bahis → adaylar → karışıklığı giderilmiş varlık](../assets/entity-linking.svg)

**Aday oluşturma.** Bahis yüzey biçimini ("Jordan") verildiğinde, bir alias indeksinde adaylara bakın. Wikipedia sözlükleri çoğu isimli varlığı kapsar: "JFK" → John F. Kennedy, Jacqueline Kennedy, JFK havalimanı, JFK (film). Tipik indeks bahis başına 10-30 aday döndürür.

**Karışıklık giderme: üç yaklaşım.**

1. **Öncel + bağlam (Milne & Witten, 2008).** `P(varlık | bahis) × bağlam-benzerliği(varlık, metin)`. İyi çalışır, hızlı, eğitim gerektirmez.
2. **Embedding tabanlı (ESS / REL / Blink).** Bahis + bağlamı kodlayın. Her adayın tanımını kodlayın. Maksimum kosinüs benzerliğini seçin. 2020-2024 varsayılanı.
3. **Üretimsel (GENRE, 2021; LLM tabanlı, 2023+).** Varlığın kanonik adını karakter karakter çözümleyin. Geçerli varlık adlarından oluşan bir trie ile kısıtlı çıkış, çıktının geçerli bir bilgi tabanı kimliği olmasını garanti eder.

**Uçtan uca vs boru hattı.** Modern modeller (ELQ, BLINK, ExtEnD, GENRE) NER + aday oluşturma + karışıklık gidermeyi tek geçişte çalıştırır. Boru hattı sistemleri üretimde hâlâ baskındır çünkü bileşenleri değiştirebilirsiniz.

### İki ölçüm

- **Bahis hatırlama (recall) (aday oluşturma).** Doğru bilgi tabanı girişinin aday listesinde göründüğü altın (gold) bahislerin oranı. Tüm boru hattı için taban.
- **Karışıklık giderme doğruluğu / F1.** Doğru adaylar verildiğinde, üst-1'in ne sıklıkla doğru olduğu.

Her ikisini de her zaman raporlayın. %80 aday hatırlama üzerinde %99 karışıklık giderme oranına sahip bir sistem %80'lik bir boru hattıdır.

## İnşa Et

### Adım 1: Wikipedia yönlendirmelerinden bir alias indeksi oluşturun

```python
alias_to_entities = {
    "jordan": ["Q41421 (Michael Jordan)", "Q810 (Jordan, country)", "Q254110 (Michael B. Jordan)"],
    "paris":  ["Q90 (Paris, France)", "Q663094 (Paris, Texas)", "Q55411 (Paris Hilton)"],
    "apple":  ["Q312 (Apple Inc.)", "Q89 (apple, fruit)"],
}
```

#### Açıklama
Bu kod, Wikipedia alias verisini tersine indeks olarak depolar. Her yüzey biçimini olası varlık kimlikleriyle eşleştirir.

Wikipedia alias verisi: ~18M (alias, varlık) çifti. Wikidata dökümlerinden indirin. Tersine indeks olarak saklayın.

### Adım 2: bağlam tabanlı karışıklık giderme

```python
def disambiguate(mention, context, alias_index, entity_desc):
    candidates = alias_index.get(mention.lower(), [])
    if not candidates:
        return None, 0.0
    context_words = set(tokenize(context))
    best, best_score = None, -1
    for entity_id in candidates:
        desc_words = set(tokenize(entity_desc[entity_id]))
        union = len(context_words | desc_words)
        score = len(context_words & desc_words) / union if union else 0.0
        if score > best_score:
            best, best_score = entity_id, score
    return best, best_score
```

#### Açıklama
Bu fonksiyon, Jaccard örtüşmesini kullanarak bağlam tabanlı karışıklık giderme yapar. Her adayın tanımıyla bağlam sözcüklerinin örtüşmesini hesaplar. Bu bir oyuncak örnektir — gerçek uygulamalarda embedding benzerliği kullanın.

Jaccard örtüşmesi bir oyuncak. Embedding'ler üzerinde kosinüs benzerliğiyle değiştirin (transformer versiyonu için `code/main.py` adım-2'ye bakın).

### Adım 3: embedding tabanlı (BLINK tarzı)

```python
from sentence_transformers import SentenceTransformer
encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed_mention(text, mention_span):
    start, end = mention_span
    marked = f"{text[:start]} [MENTION] {text[start:end]} [/MENTION] {text[end:]}"
    return encoder.encode([marked], normalize_embeddings=True)[0]

def embed_entity(entity_id, description):
    return encoder.encode([f"{entity_id}: {description}"], normalize_embeddings=True)[0]
```

#### Açıklama
Bu kod, bir bahsi ve bağlamı embedding kullanarak temsil eder. [MENTION] ve [/MENTION] etiketleri bahis konumunu işaretler. İndeksleme zamanında her bilgi tabanı varlığını bir kez kodlayın. Sorgu zamanında bahis + bağlamı bir kez kodlayın, aday havuzuna nokta çarpımı yapın, maksimumu seçin.

İndeksleme zamanında her bilgi tabanı varlığını bir kez kodlayın. Sorgu zamanında bahis + bağlamı bir kez kodlayın, aday havuzuna nokta çarpımı yapın, maksimumu seçin.

### Adım 4: üretimsel varlık bağlantısı (kavram)

GENRE, varlığın Wikipedia başlığını karakter karakter çözümler. Kısıtlı çözümleme (ders 20'ye bakın) yalnızca geçerli başlıkların çıktılanmasını sağlar. Bilgi tabanı destekli bir trie ile sıkı entegrasyon. Modern varmı olan REL-GEN ve yapılandırılmış çıktı ile LLM tabanlı EL'dir.

```python
prompt = f"""Text: {text}
Mention: {mention}
List the best Wikipedia title for this mention.
Respond with JSON: {{"title": "..."}}"""
```

#### Açıklama
Bu prompt, LLM'den bir bahis için en iyi Wikipedia başlığını listelemesini ister. Bir beyaz liste (Outlines `choice`) ile birlikte, 2026'da sunulacak en basit EL boru hattıdır.

Bir beyaz liste (Outlines `choice`) ile birlikte, 2026'da sunulacak en basit EL boru hattıdır.

### Adım 5: AIDA-CoNLL üzerinde değerlendirme

AIDA-CoNLL standart EL benchmark'ıdır: 1.393 Reuters makalesi, 34 bin bahis, Wikipedia varlıkları. Bilgi tabanı içi doğruluk (`P@1`) ve bilgi tabanı dışı NIL tespit oranını raporlayın.

## Tuzaklar

- **NIL işleme.** Bazı bahisler bilgi tabanında yok (ortaya çıkan varlıklar, belirsiz kişiler). Sistemler yanlış varlığı tahmin etmek yerine NIL tahmin etmelidir. Ayrı ölçülür.
- **Bahis sınır hataları.** Yukarıdaki NER eksik aralıkları kaçırır ("Bank of America" yalnızca "Bank" olarak etiketlenir). EL hatırlama düşer.
- **Popülerlik yanlılığı (Popularity bias).** Eğitilmiş sistemler sık varlıkları aşırı tahmin eder. Bir ML makalesindeki "Michael I. Jordan" bahsi genellikle basketbol Jordan'ına bağlanır.
- **Çapraz dilli EL.** Çince metindeki bahisleri İngilizce Wikipedia varlıklarına eşleme. Çok dilli bir kodlayıcı veya bir çeviri adımı gerektirir.
- **Bilgi tabanı eskiyliği.** Yeni şirketler, olaylar, kişiler geçen yılki Wikipedia dökümünde yok. Üretim boru hattı için bir yenileme döngüsü gerekir.

## Kullan

2026 yığını:

| Durum | Seçin |
|-----------|------|
| Genel amaçlı İngilizce + Wikipedia | BLINK veya REL |
| Çapraz dilli, bilgi tabanı = Wikipedia | mGENRE |
| LLM dostu, az bahis/gün | Aday listeli + kısıtlı JSON ile Claude/GPT-4'ü uyarın |
| Alana özgü bilgi tabanı (tıbbi, hukuki) | Bilgi tabanı farkındalıklı getirme + alana özgü AIDA tarzı kümede ince ayarlı BERT |
| Aşırı düşük gecikme | Yalnızca tam eşleşme önceli (Milne-Witten temeli) |
| Araştırma en iyi durumu | GENRE / ExtEnD / üretimsel LLM-EL |

2026'da sunulan üretim modeli: NER → coref → her bahis üzerinde EL → kümeleri küme başına tek bir kanonik varlığa daraltma. Çıktı: belge içindeki varlık başına bir bilgi tabanı kimliği, bahis başına bir tane değil.

## Teslim Et

`outputs/skill-entity-linker.md` olarak kaydedin:

```markdown
---
name: entity-linker
description: Design an entity linking pipeline — KB, candidate generator, disambiguator, evaluation.
version: 1.0.0
phase: 5
lesson: 25
tags: [nlp, entity-linking, knowledge-graph]
---

Given a use case (domain KB, language, volume, latency budget), output:

1. Knowledge base. Wikidata / Wikipedia / custom KB. Version date. Refresh cadence.
2. Candidate generator. Alias-index, embedding, or hybrid. Target mention recall @ K.
3. Disambiguator. Prior + context, embedding-based, generative, or LLM-prompted.
4. NIL strategy. Threshold on top score, classifier, or explicit NIL candidate.
5. Evaluation. Mention recall @ 30, top-1 accuracy, NIL-detection F1 on held-out set.

Refuse any EL pipeline without a mention-recall baseline (you cannot evaluate a disambiguator without knowing candidate gen surfaced the right entity). Refuse any pipeline using LLM-prompted EL without constrained output to valid KB ids. Flag systems where popularity bias affects minority entities (e.g. name-clashes) without domain fine-tuning.
```

#### Açıklama
Bu şablon, bir bilgi tabanı ve kullanım durumu için varlık bağlantısı boru hattı tasarlayan bir yetenek tanımıdır.

## Alıştırmalar

1. **Kolay.** `code/main.py` dosyasındaki öncel+bağlam karıştırıcısını 10 belirsiz bahis (Paris, Jordan, Apple) üzerinde uygulayın. Doğru varlığı elle etiketleyin. Doğruluğu ölçün.
2. **Orta.** 50 belirsiz bahsi cümle dönüştürücüsüyle (sentence transformer) kodlayın. Her adayın tanımını kodlayın. Embedding tabanlı karışıklık gidermeyi Jaccard bağlam örtüşmesiyle karşılaştırın.
3. **Zor.** 1000 varlıklık bir alan bilgi tabanı oluşturun (ör. şirketinizdeki çalışanlar + ürünler). Uçtan uca NER + EL uygulayın. 100 ayrı tutulan cümlede kesinlik ve hatırlamayı ölçün.

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Varlık bağlantısı (Entity linking - EL) | Wikipedia'ya bağla | Bir bahsi benzersiz bir bilgi tabanı girişine eşle. |
| Aday oluşturma (Candidate generation) | Kim olabilir? | Bir bahis için olası bilgi tabanı girişlerinden kısa liste döndür. |
| Karışıklık giderme (Disambiguation) | Doğru olanı seç | Adayları bağlam kullanarak puanla, kazananı seç. |
| Alias indeksi (Alias index) | Arama tablosu | Yüzey biçiminden → aday varlıklara eşleme. |
| NIL | Bilgi tabanında yok | Hiçbir bilgi tabanı girişiyle eşleşmediğinin açık tahmini. |
| Bilgi tabanı (KB) | Bilgi havuzu | Wikidata, Wikipedia, DBpedia veya alan bilgi tabanınız. |
| AIDA-CoNLL | Benchmark | Altın varlık bağlantılarıyla 1.393 Reuters makalesi. |

## İleri Okuma

- [Milne, Witten (2008). Learning to Link with Wikipedia](https://www.cs.waikato.ac.nz/~ihw/papers/08-DM-IHW-LearningToLinkWithWikipedia.pdf) — temel öncel+bağlam yaklaşımı.
- [Wu vd. (2020). Zero-shot Entity Linking with Dense Entity Retrieval (BLINK)](https://arxiv.org/abs/1911.03814) — embedding tabanlı çalışma atı.
- [De Cao vd. (2021). Autoregressive Entity Retrieval (GENRE)](https://arxiv.org/abs/2010.00904) — kısıtlı çözümlemeli üretimsel EL.
- [Hoffart vd. (2011). Robust Disambiguation of Named Entities in Text (AIDA)](https://www.aclweb.org/anthology/D11-1072.pdf) — benchmark makalesi.
- [REL: Devlerin Omuzlarında Duran Bir Varlık Bağlantılayıcı (2020)](https://arxiv.org/abs/2006.01969) — açık üretim yığını.