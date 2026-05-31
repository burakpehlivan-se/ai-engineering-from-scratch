# Coreference Çözümleme

> "Onu aradı. Cevap vermedi. Doktor öğle yemeğindeydi." İki kişiye üç referans ve hiçbiri isimlendirilmemiş. Coreference çözümlemesi kimin kim olduğunu bulur.

**Tür:** Öğren
**Diller:** Python
**Önkoşullar:** Faz 5 · 06 (NER), Faz 5 · 07 (POS ve Ayrıştırma)
**Süre:** ~60 dakika

## Sorun

300 kelimelik bir makaleden Apple Inc.'in her bahsini çıkarın. Makale "Apple" dediğinde kolay. "Şirket", "onlar", "Cupertino'nun teknoloji devi" veya "Jobs'un firması" dediğinde zor. Bu bahisleri aynı varlığa çözümlemeden, NEL boru hattınız (pipeline) bahislerin %60-80'ini kaçırır.

Coreference çözümlemesi, aynı gerçek dünya varlığına işaret eden her ifadeyi bir küme (cluster) halinde bağlar. Yüzey düzeyindeki NLP (NER, ayrıştırma) ile alt anlamlama (bilgi çıkarma, soru cevaplama, özetleme, bilgi grafiği) arasındaki yapıştırıcıdır.

2026'da neden önemli:

- Özetleme: "CEO açıklandı..." vs "Tim Cook açıklandı..." — özet CEO'yu isimlendirmeli.
- Soru cevaplama: "Onu kim aradı?" "Onu" çözümlemeyi gerektirir.
- Bilgi çıkarma: "PER1 Apple'ı kurdu" ve "Jobs Apple'ı kurdu" olarak ayrı girişler içeren bir bilgi grafiği yanlıştır.
- Çoklu belge bilgi çıkarma: Aynı olayla ilgili makalelerdeki bahisleri birleştirme, çapraz belge coreference'dır.

## Kavram

![Coreference kümeleme: bahisler → varlıklar](../assets/coref.svg)

**Görev.** Girdi: bir belge. Çıktı: her kümenin bir varlığa işaret ettiği bahislerin (aralıkların) kümelemesi.

**Bahis türleri.**

- **İsimli varlık (Named entity).** "Tim Cook"
- **İsimlendirme (Nominal).** "CEO", "şirket"
- **Zamirsel (Pronominal).** "o", "o (dişi)", "onlar", "o (nesne)"
- **Yan cümle (Appositive).** "Tim Cook, Apple'ın CEO'su,"

**Mimariler.**

1. **Kural tabanlı (Hobbs, 1978).** Dilbilgisel kurallar kullanan sözdizimsel ağaç tabanlı zamir çözümlemesi. İyi temel. Zamirlerde yenilmesi şaşırtıcı derecede zor.
2. **Bahis çifti sınıflandırıcısı.** Her bahis çifti (m_i, m_j) için, coreference yapıp yapmayacağını tahmin et. Geçişkencilik kapanışıyla (transitive closure) kümele. 2016 öncesi standart.
3. **Bahis sıralaması (Mention-ranking).** Her bahis için, aday öncelleri sıralayın (hiç yok dahil). En yükseği seçin.
4. **Aralık tabanlı uçtan uca (Lee vd., 2017).** Transformer encoder. Uzunluk sınırına kadar tüm aday aralıkları numaralandırın. Bahis puanlarını tahmin edin. Her aralık için olasılık tahmin edin. açgözlü (greedy) kümele. Modern varsayılan.
5. **Üretimsel (2024+).** Bir LLM'e prompt verin: "Bu metindeki her zamiri ve öncelini listeleyin." Kolay durumlarda iyi çalışır, uzun belgelerde ve seyrek referanslarda zorlanır.

**Değerlendirme metrikleri.** Beş standart metrik (MUC, B³, CEAF, BLANC, LEA) çünkü tek bir metrik kümeleme kalitesini yakalayamaz. İlk üçünün ortalamasını CoNLL F1 olarak raporlayın. 2026'da CoNLL-2012 üzerinde en iyi durum (state-of-the-art): ~83 F1.

**Bilinen zor durumlar.**

- Sayfalar önce tanıtılan varlıklara işaret eden kesin tanımlamalar (definite descriptions).
- Köprüleme anforası (bridging anaphora) ("tekerlekler" → daha önce bahsedilen bir araba).
- Çince ve Japonca gibi dillerde sıfır anfora (zero anaphora).
- Atıfor (Cataphora) (önceden gelen zamir): "Onu yürürken, Mary güldü."

## İnşa Et

### Adım 1: önceden eğitilmiş sinirsel coreference (AllenNLP / spaCy-experimental)

```python
import spacy
nlp = spacy.load("en_coreference_web_trf")   # experimental model
doc = nlp("Apple announced new products. The company said they would ship soon.")
for cluster in doc._.coref_clusters:
    print(cluster, "->", [m.text for m in cluster])
```

#### Açıklama
Bu kod, spaCy'nin deneysel coreference modelini kullanarak bir belge üzerindeki coreference kümelerini tespit eder ve her kümedeki bahisleri listeler.

Uzun bir belge上面, şuna benzer bir şey alırsınız:
- Küme 1: [Apple, The company, they]
- Küme 2: [new products]

### Adım 2: kural tabanlı zamir çözümleyici (öğretme amaçlı)

Tam bir stdlib-only uygulama için `code/main.py` dosyasına bakın:

1. Bahisleri çıkarın: isimli varlıklar (büyük harfli aralıklar), zamirler (sözlük araması), kesin tanımlamalar ("the X").
2. Her zamir için, önceki K bahise bakın ve şu kriterlere göre puanlayın:
   - cinsiyet/tane uyumu (sezgisel)
   - yakınlık (daha yakınlık kazanır)
   - sözdizimsel rol (özne tercih edilir)
3. En yüksek puanlı önceli bağlayın.

Sinirsel modellerle rekabet edemez. Ancak uçtan uca bir modelin yapması gereken arama alanını ve kararları gösterir.

### Adım 3: coreference için LLM'leri kullanma

```python
prompt = f"""Text: {text}

List every pronoun and noun phrase that refers to a person or company.
Cluster them by what they refer to. Output JSON:
[{{"entity": "Apple", "mentions": ["Apple", "the company", "it"]}}, ...]
"""
```

#### Açıklama
Bu prompt, LLM'den bir metindeki tüm zamirleri ve isim ifadelerini listelemesini ve bunları referanslarına göre kümelemesini ister. İki başarısızlık moduna dikkat edin.

İzlenmesi gereken iki başarısızlık modu var. Birincisi, LLM'ler aşırı birleştirme yapar ("him" ve "her" iki farklı kişiyi işaret ederken). İkincisi, LLM'ler uzun belgelerde bahisleri sessizce düşürür. Her zaman aralık ofseti kontrolleriyle doğrulayın.

### Adım 4: değerlendirme

Standart conll-2012 betiği MUC, B³, CEAF-φ4 hesaplar ve ortalamayı raporlar. Dahili bir değerlendirme için, etiketli test kümenizde aralık düzeyinde kesinlik ve hatırlamayla başlayın, ardından bahis-bağlama F1 ekleyin.

## Tuzaklar

- **Tekil küme patlaması (Singleton explosion).** Bazı sistemler her bahisi kendi kümesi olarak raporlar. B³ affedici. Muc cezalandırır. Her zaman üç metriği de kontrol edin.
- **Uzun bağlamda zamirler.** 2.000 token'ın üzerindeki belgelerde performans ~15 F1 düşer. Dikkatli parçalayın.
- **Cinsiyet varsayımları.** Katı cinsiyet kuralları, ikili olmayan (non-binary) referanslarda, kuruluşlarda, hayvanlarda bozulur. Öğrenilmiş modeller veya tarafsız puanlama kullanın.
- **Uzun belgelerde LLM sapması.** Tek bir API çağrısı 50+ paragrafta bahisleri güvenilir bir şekilde kümeleyemez. Kayan pencere (sliding window) + birleştirme kullanın.

## Kullan

2026 yığını:

| Durum | Seçin |
|-----------|------|
| İngilizce, tek belge | `en_coreference_web_trf` (spaCy-experimental) veya AllenNLP sinirsel coref |
| Çok dilli | OntoNotes veya Multilingual CoNLL üzerinde eğitilmiş SpanBERT / XLM-R |
| Çapraz belge olay coref'i | Özelleştirilmiş uçtan uca modeller (2025–26 en iyi durum) |
| Hızlı LLM temeli | Yapılandırılmış çıktı (structured-output) coref prompt'lu GPT-4o / Claude |
| Üretim konuşma sistemleri | Kural tabanlı geri dönüş + sinirsel birincil + kritik alanlar için manuel inceleme |

2026'da sunulan entegrasyon modeli: önce NER çalıştırın, coref çalıştırın, coref kümelerini NER varlıklarına birleştirin. Alt görevler küme başına bir varlık görür, bahis başına bir varlık değil.

## Teslim Et

`outputs/skill-coref-picker.md` olarak kaydedin:

```markdown
---
name: coref-picker
description: Pick a coreference approach, evaluation plan, and integration strategy.
version: 1.0.0
phase: 5
lesson: 24
tags: [nlp, coref, information-extraction]
---

Given a use case (single-doc / multi-doc, domain, language), output:

1. Approach. Rule-based / neural span-based / LLM-prompted / hybrid. One-sentence reason.
2. Model. Named checkpoint if neural.
3. Integration. Order of operations: tokenize → NER → coref → downstream task.
4. Evaluation. CoNLL F1 (MUC + B³ + CEAF-φ4 average) on held-out set + manual cluster review on 20 documents.

Refuse LLM-only coref for documents over 2,000 tokens without sliding-window merge. Refuse any pipeline that runs coref without a mention-level precision-recall report. Flag gender-heuristic systems deployed in demographically diverse text.
```

#### Açıklama
Bu şablon, bir kullanım durumu için coreference yaklaşımı, değerlendirme planı ve entegrasyon stratejisi seçen bir yetenek tanımıdır.

## Alıştırmalar

1. **Kolay.** `code/main.py` dosyasındaki kural tabanlı çözümleyiciyi 5 el yapımı paragrafta çalıştırın. Temel doğrulukla (ground truth) karşılaştırarak bahis-bağlama doğruluğunu ölçün.
2. **Orta.** Bir haber makalesinde önceden eğitilmiş bir sinirsel coref modeli kullanın. Kümeleri kendi manuel etiketlemenizle karşılaştırın. Nerede başarısız oldu?
3. **Zor.** Coref geliştirilmiş bir NEL boru hattı oluşturun: önce NER, ardından coref kümeleriyle birleştirme. 100 makalede yalnızca NEL'e göre varlık kapsamı iyileştirmesini ölçün.

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Bahis (Mention) | Bir referans | Bir varlığa işaret eden metin aralığı (isim, zamir, isim ifadesi). |
| Öncel (Antecedent) | "O" neye işaret ediyor | Bir sonraki bahsin coreference yaptığı daha önceki bahis. |
| Küme (Cluster) | Varlığın bahisleri | Tümü aynı gerçek dünya varlığına işaret eden bahisler kümesi. |
| Anfora (Anaphora) | Geriye doğru referans | Sonraki bahis daha öncekine işaret eder ("o" → "John"). |
| Atıfor (Cataphora) | İleriye doğru referans | Daha önceki bahis sonrakine işaret eder ("O geldiğinde, John..."). |
| Köprüleme (Bridging) | Dolaylı referans | "Bir araba satın aldım. Tekerlekleri kötüydü." (arabanın TEBERLEKLERİ.) |
| CoNLL F1 | Liderlik tablolarındaki sayı | MUC, B³, CEAF-φ4 F1 puanlarının ortalaması. |

## İleri Okuma

- [Jurafsky & Martin, SLP3 Ch. 26 — Coreference Çözümlemesi ve Varlık Bağlama](https://web.stanford.edu/~jurafsky/slp3/26.pdf) — kanonik ders kitabı bölümü.
- [Lee vd. (2017). End-to-end Neural Coreference Resolution](https://arxiv.org/abs/1707.07045) — aralık tabanlı uçtan uca.
- [Joshi vd. (2020). SpanBERT](https://arxiv.org/abs/1907.10529) — coref'i geliştiren önceden eğitim.
- [Pradhan vd. (2012). CoNLL-2012 Shared Task](https://aclanthology.org/W12-4501/) — benchmark.
- [Hobbs (1978). Resolving Pronoun References](https://www.sciencedirect.com/science/article/pii/0024384178900064) — kural tabanlı klasik.