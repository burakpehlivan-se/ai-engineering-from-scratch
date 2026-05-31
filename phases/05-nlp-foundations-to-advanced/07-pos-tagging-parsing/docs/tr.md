# POS Etiketleme ve Sözdizimsel Ayrıştırma

> Gramer bir süre modası geçmişti. Sonra her LLM pipeline'ı yapılandırılmış çıkarmayı doğrulamak zorunda kaldı ve geri döndü.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 5 · 01 (Metin İşleme), Faz 2 · 14 (Naive Bayes)
**Süre:** ~45 dakika

## Problem

Ders 01, lemmatizasyonun bir kelime türü (POS) etiketine ihtiyaç duyduğunu vaat etmişti. `running` kelimesinin bir fiil olduğunu bilmeden, bir lemmatizer onu `run`'a indiremez. `better` kelimesinin bir sıfat olduğunu bilmeden, onu `good`'a indiremez.

Bu vaat, tüm bir alt alanı gizliyordu. Kelime türü etiketleme (POS tagging) gramatik kategorileri atar. Sözdizimsel ayrıştırma (syntactic parsing) ise cümlenin ağaç yapısını ortaya çıkarır: hangi kelime hangisini düzenler, hangi fiil hangi argümanları yönetir. Klasik NLP, her ikisini de geliştirmek için yirmi yıl harcadı. Ardından deep learning bunları, önceden eğitilmiş bir transformer üzerine bir token-sınıflandırma görevine dönüştürdü ve araştırma topluluğu yoluna devam etti.

Uygulama topluluğu ise etmedi. Her yapılandırma çıkarma pipeline'ı hâlâ POS ve bağımlılık ağaçlarını (dependency trees) arka planda kullanır. LLM tarafından üretilen JSON, gramatik kısıtlamalara göre doğrulanır. Soru-cevaplama sistemleri, sorguları bağımlılık ayrıştırmaları kullanarak ayrıştırır. Makine çevirisi kalite değerlendiricileri, ayrıştırma ağaçlarının hizalamasını kontrol eder.

Bilmeye değer. Bu ders, etiket kümelerini (tagsets), temel çizgileri (baselines) ve artık sıfırdan uygulamayı bırakıp spaCy'yi çağırdığınız noktayı tanıtır.

## Kavram

**POS etiketleme**, her token'a bir gramatik kategorisi etiketler. **Penn Treebank (PTB)** etiket kümesi İngilizce varsayılanıdır. 36 etiket ve sıradan okuyucunun gereksiz gördüğü ayrım türleri: `NN` tekil isim, `NNS` çoğul isim, `NNP` özel isim tekil, `VBD` fiil geçmiş zaman, `VBZ` fiil 3. tekil şahıs şimdiki zaman, ve benzeri. **Universal Dependencies (UD)** etiket kümesi daha kabadır (17 etiket) ve dilden bağımsızdır; çapraz dilli (cross-lingual) çalışmalar için varsayılan haline gelmiştir.

```
The/DET cats/NOUN were/AUX running/VERB at/ADP 3pm/NOUN ./PUNCT
```

**Sözdizimsel ayrıştırma** bir ağaç üretir. İki ana stil:

- **Önerme ayrıştırması (Constituency parsing).** İsim öbekleri (noun phrases), fiil öbekleri (verb phrases), edat öbekleri (prepositional phrases) birbiri içine yuvalanır. Çıktı, sözcüklerin yaprak olduğu terminal olmayan kategorilerden (NP, VP, PP) oluşan bir ağaçtır.
- **Bağımlılık ayrıştırması (Dependency parsing).** Her kelimenin bağımlı olduğu tek bir baş kelimesi (head) vardır ve gramatik bir ilişki ile etiketlenmiştir. Çıktı, her bir kenarın (head, dependent, relation) üçlüsü olduğu bir ağaçtır.

Bağımlılık ayrıştırması 2010'larda özellikle serbest kelime sıralamasına sahip dillerde temiz bir şekilde genelleştiği için kazandı.

```
running is ROOT
cats is nsubj of running
were is aux of running
at is prep of running
3pm is pobj of at
```

## İnşa Et

### Adım 1: en sık görülen etiket temel çizgisi

En çalışır basit POS etiketleyicisi. Her kelime için, eğitimde en sık görüldüğü etiketi tahmin eder.

```python
from collections import Counter, defaultdict


def train_mft(train_examples):
    word_tag_counts = defaultdict(Counter)
    all_tags = Counter()
    for tokens, tags in train_examples:
        for token, tag in zip(tokens, tags):
            word_tag_counts[token.lower()][tag] += 1
            all_tags[tag] += 1
    word_best = {w: c.most_common(1)[0][0] for w, c in word_tag_counts.items()}
    default_tag = all_tags.most_common(1)[0][0]
    return word_best, default_tag


def predict_mft(tokens, word_best, default_tag):
    return [word_best.get(t.lower(), default_tag) for t in tokens]
```

Brown corpus'unda bu temel çizgi yaklaşık %85 doğruluğa ulaşır. İyi değil, ama hiçbir ciddi modelin altına düşmemesi gereken tabandır.

### Adım 2: bigram HMM etiketleyicisi

Dizinin ortak olasılığını modeller:

```
P(tags, words) = prod P(tag_i | tag_{i-1}) * P(word_i | tag_i)
```

İki tablo: geçiş olasılıkları (önceki etiket verildiğinde etiket), emission olasılıkları (etiket verildiğinde kelime). Her ikisini de Laplace düzeltmesiyle sayaclardan tahmin edin. Viterbi ile kodlayın (etiket kafesinde dinamik programlama).

```python
import math


def train_hmm(train_examples, alpha=0.01):
    transitions = defaultdict(Counter)
    emissions = defaultdict(Counter)
    tags = set()
    vocab = set()

    for tokens, ts in train_examples:
        prev = "<BOS>"
        for token, tag in zip(tokens, ts):
            transitions[prev][tag] += 1
            emissions[tag][token.lower()] += 1
            tags.add(tag)
            vocab.add(token.lower())
            prev = tag
        transitions[prev]["<EOS>"] += 1

    return transitions, emissions, tags, vocab


def log_prob(table, given, key, smooth_denom, alpha):
    return math.log((table[given].get(key, 0) + alpha) / smooth_denom)


def viterbi(tokens, transitions, emissions, tags, vocab, alpha=0.01):
    tags_list = list(tags)
    n = len(tokens)
    V = [[0.0] * len(tags_list) for _ in range(n)]
    back = [[0] * len(tags_list) for _ in range(n)]

    for j, tag in enumerate(tags_list):
        em_denom = sum(emissions[tag].values()) + alpha * (len(vocab) + 1)
        tr_denom = sum(transitions["<BOS>"].values()) + alpha * (len(tags_list) + 1)
        tr = log_prob(transitions, "<BOS>", tag, tr_denom, alpha)
        em = log_prob(emissions, tag, tokens[0].lower(), em_denom, alpha)
        V[0][j] = tr + em
        back[0][j] = 0

    for i in range(1, n):
        for j, tag in enumerate(tags_list):
            em_denom = sum(emissions[tag].values()) + alpha * (len(vocab) + 1)
            em = log_prob(emissions, tag, tokens[i].lower(), em_denom, alpha)
            best_prev = 0
            best_score = -1e30
            for k, prev_tag in enumerate(tags_list):
                tr_denom = sum(transitions[prev_tag].values()) + alpha * (len(tags_list) + 1)
                tr = log_prob(transitions, prev_tag, tag, tr_denom, alpha)
                score = V[i - 1][k] + tr + em
                if score > best_score:
                    best_score = score
                    best_prev = k
            V[i][j] = best_score
            back[i][j] = best_prev

    last_best = max(range(len(tags_list)), key=lambda j: V[n - 1][j])
    path = [last_best]
    for i in range(n - 1, 0, -1):
        path.append(back[i][path[-1]])
    return [tags_list[j] for j in reversed(path)]
```

Brown'da bigram HMM yaklaşık %93 doğruluğa ulaşır. %85'ten %93'e sıçrama çoğunlukla geçiş olasılıklarından gelir — model `DET NOUN`'un yaygın ve `NOUN DET`'nin nadir olduğunu öğrenir.

### Adım 3: modern etiketleyicilerin neden bunu yendiği

Geçiş + emission olasılıkları yereldir. `saw`'ın "I bought a saw" sentencesinde bir isim ama "I saw the movie." sentencesinde bir fiil olduğunu kavrayamazlar. Sıfat ekleri, kelime şekli, önceki ve sonraki kelimeler, kelimenin kendisi gibi keyfi özelliklerle çalışan bir CRF yaklaşık %97'ye ulaşır. BiLSTM-CRF veya transformer ise %98+'ya ulaşır.

Bu görevin tavanı,annotatör anlaşmazlığı tarafından belirlenir. İnsan annotatörler Penn Treebank'ta yaklaşık %97 oranında anlaşırlar. %98'i geçen modeller muhtemelen test setine aşırı uyum (overfitting) sağlıyor demektir.

### Adım 4: bağımlılık ayrıştırması taslağı

Sıfırdan tam bağımlılık ayrıştırması kapsam dışındadır; klasik ders kitabı yaklaşımı Jurafsky ve Martin'de yer alır. Bilmeniz gereken iki klasik aile:

- **Geçiş tabanlı (Transition-based)** ayrıştırıcılar (arc-eager, arc-standard) bir shift-reduce ayrıştırıcısı gibi çalışır: tokenları okur, bir yığına (stack) koyar ve kemerler (arcs) oluşturan reduce eylemleri uygular. Açgözlü (greedy) kodlama hızlıdır. Klasik uygulama MaltParser'dır. Modern sinirsel versiyonu: Chen ve Manning'in geçiş tabanlı ayrıştırıcısı.
- **Graf tabanlı (Graph-based)** ayrıştırıcılar (Eisner algoritması, Dozat-Manning biaffine) olası her head-dependent kenarını puanlar ve maksimum spanning tree'yi seçer. Daha yavaş ama daha hassastır.

Çoğu uygulama işi için spaCy'yi çağırın:

```python
import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("The cats were running at 3pm.")
for token in doc:
    print(f"{token.text:10s} tag={token.tag_:5s} pos={token.pos_:6s} dep={token.dep_:10s} head={token.head.text}")
```

```
The        tag=DT    pos=DET    dep=det        head=cats
cats       tag=NNS   pos=NOUN   dep=nsubj      head=running
were       tag=VBD   pos=AUX    dep=aux        head=running
running    tag=VBG   pos=VERB   dep=ROOT       head=running
at         tag=IN    pos=ADP    dep=prep       head=running
3pm        tag=NN    pos=NOUN   dep=pobj       head=at
.          tag=.     pos=PUNCT  dep=punct      head=running
```

`dep` sütununu alta doğru okuyun ve cümlenin gramatik yapısı ortaya çıkar.

## Kullan

Her üretim NLP kütüphanesi POS ve bağımlılık ayrıştırıcılarını standart bir pipeline'ın parçası olarak sunar.

- **spaCy** (`en_core_web_sm` / `md` / `lg` / `trf`). Hızlı, hassas, tokenize + NER + lemmatizasyon ile entegre. `token.tag_` (Penn), `token.pos_` (UD), `token.dep_` (bağımlılık ilişkisi).
- **Stanford NLP (stanza).** Stanford'un CoreNLP halefi. 60+ dilde güncel durum (state-of-the-art).
- **trankit.** Transformer tabanlı, iyi UD doğruluğu.
- **NLTK.** `pos_tag`. Kullanılabilir, yavaş, eski. Öğretim için yeterli.

### 2026'da hâlâ neden önemli

- **Lemmatizasyon.** Ders 01, doğru lemmatizasyon için POS'a ihtiyaç duyar. Her zaman.
- **LLM çıktılarından yapılandırma çıkarma.** Üretilen bir cümlenin gramatik kısıtlamalara (örneğin özne-fiil uyumu, gerekli düzenleyiciler) uygun olduğunu doğrulama.
- **Türe dayalı duygu analizi (Aspect-based sentiment).** Bağımlılık ayrıştırmaları hangi sıfatın hangi ismi düzenlediğini söyler.
- **Sorgu anlama.** "movies directed by Wes Anderson starring Bill Murray" ifadesi ayrıştırma yoluyla yapılandırılmış kısıtlamalara ayrıştırılır.
- **Çapraz dil aktarımı (Cross-lingual transfer).** UD etiketleri ve bağımlılık ilişkileri dilden bağımsızdır, yeni dillerin yapılandırılmış analizini sıfır örnek (zero-shot) ile mümkün kılar.
- **Düşük hesaplama maliyetli pipeline'lar.** Bir transformer gönderemiyorsanız, POS + bağımlılık ayrıştırması + sözlük (gazetteer) sizi şaşırtıcı kadar uzağa götürür.

## Ürün Haline Getir

`outputs/skill-grammar-pipeline.md` olarak kaydedin:

```markdown
---
name: grammar-pipeline
description: Design a classical POS + dependency pipeline for a downstream NLP task.
version: 1.0.0
phase: 5
lesson: 07
tags: [nlp, pos, parsing]
---

Given a downstream task (information extraction, rewrite validation, query decomposition, lemmatization), you output:

1. Tagset to use. Penn Treebank for English-only legacy pipelines, Universal Dependencies for multilingual or cross-lingual.
2. Library. spaCy for most production, stanza for academic-grade multilingual, trankit for highest UD accuracy. Name the specific model ID.
3. Integration pattern. Show the 3-5 lines that call the library and consume the needed attributes (`.pos_`, `.dep_`, `.head`).
4. Failure mode to test. Noun-verb ambiguity (`saw`, `book`, `can`) and PP-attachment ambiguity are the classical traps. Sample 20 outputs and eyeball.

Refuse to recommend rolling your own parser. Building parsers from scratch is a research project, not an application task. Flag any pipeline that consumes POS tags without handling lowercase/uppercase variants as fragile.
```

## Alıştırmalar

1. **Kolay.** Küçük etiketli bir corpus (örneğin NLTK'nın Brown alt kümesi) üzerinde en sık görülen etiket temel çizgisini kullanarak, ayrı tutulan cümlelerde doğruluğu ölçün. ~%85 sonucunu doğrulayın.
2. **Orta.** Yukarıdaki bigram HMM'yi eğitin ve etiket bazında precision/recall bildirin. HMM en çok hangi etiketleri karıştırıyor?
3. **Zor.** spaCy'nin bağımlılık ayrıştırmasını kullanarak 1000 cümlelik bir örneklemden özne-fiil-nesne üçlülerini (SVO triples) çıkarın. 50 elle etiketlenmiş üçlü üzerinde değerlendirin. Çıkarımın nerede başarısız olduğunu belgeleyin (genellikle edilgen çatımlarda, sıralamalarda ve atlanmış öznelerde).

## Anahtar Terimler

| Terim | İnsanlar ne söyler | Aslında ne anlama gelir |
|-------|-------------------|------------------------|
| POS etiketi | Kelimenin türü | Gramatik kategori. PTB 36; UD 17 tane içerir. |
| Penn Treebank | Standart etiket kümesi | İngilizceye özgü. İnce ayırtlı fiil zamanları ve isim sayıları. |
| Universal Dependencies | Çok dilli etiket kümesi | PTB'den daha kaba; dilden bağımsız; çapraz dilli çalışmalar için varsayılan. |
| Bağımlılık ayrıştırması | Cümle ağacı | Her kelimenin bir başı, her kenarın bir gramatik ilişkisi vardır. |
| Viterbi | Dinamik programlama | Emission ve geçişler verildiğinde en yüksek olasılıklı etiket dizisini bulur. |

## İleri Okuma

- [Jurafsky ve Martin — Speech and Language Processing, bölümler 8 ve 18](https://web.stanford.edu/~jurafsky/slp3/) — POS ve ayrıştırma için klasik ders kitabı yaklaşımı.
- [Universal Dependencies projesi](https://universaldependencies.org/) — her çok dilli ayrıştırıcının kullandığı çapraz dilli etiket kümesi ve ağaç bankı (treebank) koleksiyonu.
- [spaCy dilbilimsel özellikler rehberi](https://spacy.io/usage/linguistic-features) — `Token` üzerinde sunulan her özellik için pratik referans.
- [Chen ve Manning (2014). A Fast and Accurate Dependency Parser using Neural Networks](https://nlp.stanford.edu/pubs/emnlp2014-depparser.pdf) — sinirsel ayrıştırıcıları ana akıma taşıyan makale.
