# Metin İşleme — Tokenization, Stemming, Lemmatization

> Dil süreklidir. Modeller ayrışıktır. Ön-işleme bu köprüyü kurar.

**Tür:** İnşa
**Diller:** Python
**Ön Koşullar:** Faz 2 · 14 (Naive Bayes)
**Süre:** ~45 dakika

## Problem

Bir model "The cats were running." cümlesini okuyamaz. Tam sayılar okur.

Her NLP sistemi aynı üç soruyla başlar. Bir kelimenin nerede başladığı. Kelimenin kökünün ne olduğu. "run", "running", "ran" ifadelerini ne zaman aynı şey olarak ele alacağımızı ve ne zaman farklı olarak ele alacağımızı nasıl belirleriz.

Tokenization yanlış yapılırsa model çöpten öğrenir. Tokenizerınız `don't` ifadesini bir token olarak ele alırken `do n't` ifadesini iki token olarak ele alırsa, eğitim dağılımı bölünür. Stemmerınız `organization` ve `organ` kelimelerini aynı köke indirirse topic modeling ölür. Lemmatizerınız POS tagging (kelime türü etiketleme) bağlamına ihtiyaç duyuyorsa ve siz bunu iletmiyorsanız, fiiller isim olarak ele alınır.

Bu ders, üç ön-işleme adımını sıfırdan oluşturur ve ardından NLTK ile spaCy'in aynı işi nasıl yaptığını gösterir; böylece ödünleşimleri görebilirsiniz.

## Kavram

Üç işlem. Her birinin bir görevi ve bir başarısızlık modu vardır.

**Tokenization**, bir dizgeyi (string) tokenlara böler. "Token" kasıtlı olarak belirsizdir; çünkü granülarite göreve bağlıdır. Kelime düzeyi klasik NLP için. Subword (alt kelime) transformer'lar için. Boşluk içermeyen diller için karakter düzeyi.

**Stemming**, kurallarla ekleri keser. Hızlı, agresif, kaba. `running -> run`. `organization -> organ`. İkincisi başarısızlık modudur.

**Lemmatization**, dilbilgisel bilgi kullanarak bir kelimenin sözlük formuna indirger. Daha yavaş, hassastır, bir arama tablosu veya morfolojik analizör gerektirir. `ran -> run` ("ran" kelimesinin "run" kelimesinin geçmiş zamanı olduğunu bilmesi gerekir). `better -> good` ("better" kelimesinin karşılaştırma eki olduğunu bilmesi gerekir).

Kural olarak: hız önemliyse ve gürültüye tahammül edebiliyorsanız stemming kullanın (arama dizinleme, kabaca sınıflandırma). Anlam önemliyse lemmatization kullanın (soru-cevap, anlamsal arama, kullanıcının okuyacağı her şey).

## İnşa Et

### Adım 1: regex tabanlı kelime tokenizer

En basit kullanışlı tokenizer, olmayan-alfasayısal karakterler üzerinde bölerken noktalama işaretlerini kendi tokenları olarak korur. Mükemmel değil, nihai değil, ama tek satırda çalışır.

```python
import re

def tokenize(text):
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+|[^\sA-Za-z0-9]", text)
```

Üç desen öncelik sırasıyla. İç apostroflu kelimeler (`don't`, `it's`). Saf sayılar. Tek bir olmayan-boşluk-olmayan-alfasayısal karakterin bağımsız token olarak ele alınması (noktalama).

```python
>>> tokenize("The cats weren't running at 3pm.")
['The', 'cats', "weren't", 'running', 'at', '3', 'pm', '.']
```

Dikkat edilmesi gereken başarısızlık modları. `3pm` ifadesi `['3', 'pm']` olarak bölünür çünkü harf ve rakam grupları arasında geçiş yapıyoruz. Çoğu görev için yeterli. URL'ler, e-postalar, hashtag'lerin hepsi kırılır. Üretim için, genel desenlerden önce özel desenler ekleyin.

### Adım 2: Porter stemmer (sadece 1a adımı)

Tam Porter algoritması beş kural aşamasına sahiptir. 1a adımı tek başına en sık İngilizce eklerini kapsar ve deseni öğretir.

```python
def stem_step_1a(word):
    if word.endswith("sses"):
        return word[:-2]
    if word.endswith("ies"):
        return word[:-2]
    if word.endswith("ss"):
        return word
    if word.endswith("s") and len(word) > 1:
        return word[:-1]
    return word
```

```python
>>> [stem_step_1a(w) for w in ["caresses", "ponies", "caress", "cats"]]
['caress', 'poni', 'caress', 'cat']
```

Kuralları yukarıdan aşağıya okuyun. `ies -> i` kuralı yüzünden `ponies -> poni` oluyor, `pony` değil. Gerçek Porter'ın bunu düzelten 1b adımı vardır. Kurallar birbirleriyle yarışır. Önceki kurallar kazanır. Sıra tek bir kuraldan daha önemlidir.

### Adım 3: arama tablosu tabanlı lemmatizer

Düzgün lemmatization morfoloji gerektirir. Öğretilebilir bir sürüm küçük bir lemma tablosu ve bir yedek mekanizması kullanır.

```python
LEMMA_TABLE = {
    ("running", "VERB"): "run",
    ("ran", "VERB"): "run",
    ("runs", "VERB"): "run",
    ("better", "ADJ"): "good",
    ("best", "ADJ"): "good",
    ("cats", "NOUN"): "cat",
    ("cat", "NOUN"): "cat",
    ("were", "VERB"): "be",
    ("was", "VERB"): "be",
    ("is", "VERB"): "be",
}

def lemmatize(word, pos):
    key = (word.lower(), pos)
    if key in LEMMA_TABLE:
        return LEMMA_TABLE[key]
    if pos == "VERB" and word.endswith("ing"):
        return word[:-3]
    if pos == "NOUN" and word.endswith("s"):
        return word[:-1]
    return word.lower()
```

```python
>>> lemmatize("running", "VERB")
'run'
>>> lemmatize("cats", "NOUN")
'cat'
>>> lemmatize("better", "ADJ")
'good'
>>> lemmatize("watched", "VERB")
'watched'
```

Son durum ana öğretme anıdır. `watched` tablomuzda yok ve yedek mekanizmamız sadece `ing` elemanını işliyor. Gerçek lemmatization `ed` elemanını, düzensiz fiilleri, karşılaştırma eklerini, ses değişiklikleriyle çoğulları kapsar (`children -> child`). Üretim sistemlerinin WordNet, spaCy'in morfolojik analizcisi veya tam bir morfolojik analizör kullanmasının nedeni budur.

### Adım 4: bunları bir araya getirme

```python
def preprocess(text, pos_tagger=None):
    tokens = tokenize(text)
    stems = [stem_step_1a(t.lower()) for t in tokens]
    tags = pos_tagger(tokens) if pos_tagger else [(t, "NOUN") for t in tokens]
    lemmas = [lemmatize(word, pos) for word, pos in tags]
    return {"tokens": tokens, "stems": stems, "lemmas": lemmas}
```

Eksik parça bir POS tagger'dır. Faz 5 · 07 (POS Tagging) dersinde bir tane oluşturulur. Şu an her şeyi `NOUN` olarak varsayın ve bu kısıtlamayı kabul edin.

## Kullan

NLTK ve spaCy, üretim sürümlerini içerir. Her biri birkaç satır.

### NLTK

```python
import nltk
nltk.download("punkt_tab")
nltk.download("wordnet")
nltk.download("averaged_perceptron_tagger_eng")

from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk import pos_tag

text = "The cats were running."
tokens = word_tokenize(text)
stems = [PorterStemmer().stem(t) for t in tokens]
lemmatizer = WordNetLemmatizer()
tagged = pos_tag(tokens)


def nltk_pos_to_wordnet(tag):
    if tag.startswith("V"):
        return "v"
    if tag.startswith("J"):
        return "a"
    if tag.startswith("R"):
        return "r"
    return "n"


lemmas = [lemmatizer.lemmatize(t, nltk_pos_to_wordnet(tag)) for t, tag in tagged]
```

`word_tokenize` kısaltmaları, Unicode'u, regex'inizin kaçırdığı uç durumları ele alır. `PorterStemmer` beş aşamanın tamamını çalıştırır. `WordNetLemmatizer`, NLTK'nın Penn Treebank şemasından WordNet'in kısaltma kümesine çevrilen POS etiketini gerektirir. Yukarıdaki çeviri bağlantısı çoğu dersin atladığı kısımdır.

### spaCy

```python
import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("The cats were running.")

for token in doc:
    print(token.text, token.lemma_, token.pos_)
```

```
The      the     DET
cats     cat     NOUN
were     be      AUX
running  run     VERB
.        .       PUNCT
```

spaCy tüm hattı `nlp(text)` arkasına gizler. Tokenization, POS tagging ve lemmatization hepsi çalışır. Ölçek olarak NLTK'dan daha hızlıdır. Kutudan çıktığı haliyle daha hassastır. Ödünleşim, tek bileşenleri kolayca değiştirememenizdir.

### Hangisini ne zaman seçmeli

| Durum | Seçin |
|-----------|------|
| Öğretim, araştırma, bileşen değiştirme | NLTK |
| Üretim, çok dilli, hız önemli | spaCy |
| Transformer hattı (zaten modelin tokenizer'ı ile tokenize edeceksiniz) | `tokenizers` / `transformers` kullanın ve klasik ön-işlemeyi atlayın |

### Kimsenin uyarmadığı iki başarısızlık modu

Çoğu ders algoritmaları öğretir ve durur. Gerçek bir ön-işleme hattını iki şeyin vuracağı vardır ve bunlar neredeyse hiç ele alınmaz.

**Tekrar üretilebilirlik kayması.** NLTK ve spaCy sürümler arasında tokenization ve lemmatizer davranışını değiştirir. spaCy 2.x'te `['do', "n't"]` üreten şey 3.x'te `["don't"]` üretebilir. Modeliniz bir dağılım üzerinde eğitildi. Çıkarım artık farklı bir dağılım üzerinde çalışıyor. Hassasiyet sessizce bozulur ve kimse nedenini bilmez. Kütüphane sürümlerini `requirements.txt` içinde sabitleyin. Beklenen tokenization'ı donduran 20 örnek cümle içeren bir ön-işleme regresyon testi yazın. Her yükseltmede çalıştırın.

**Eğitim / çıkarım uyumsuzluğu.** Agresif ön-işleme ile eğitin (küçük harfe dönüştürme, stopwords kaldırma, stemming), ham kullanıcı girdisi üzerinde çalıştırın, performansın çöktüğünü izleyin. Bu, en yaygın üretim NLP hatasıdır. Eğitim sırasında ön-işleme yapıyorsanız, çıkarım sırasında aynı işlevi çalıştırmanız gerekir. Ön-işlemeyi model paketinin içinde bir işlev olarak paketleyin, sunum ekibinin yeniden yazdığı bir not defteri hücresi olarak değil.

## Ürün Haline Getir

Mühendislerin üç ders kitabı okumadan bir ön-işleme stratejisi seçmesine yardımcı olan yeniden kullanılabilir bir istem.

`outputs/prompt-preprocessing-advisor.md` olarak kaydedin:

```markdown
---
name: preprocessing-advisor
description: Bir NLP görevi için tokenization, stemming ve lemmatization kurulumunu önerir.
phase: 5
lesson: 01
---

Klasik NLP ön-işlemesi üzerine danışmanlık yapıyorsunuz. Bir görev tanımı verildiğinde şunları çıktı olarak veriyorsunuz:

1. Tokenization seçimi (regex, NLTK word_tokenize, spaCy veya transformer tokenizer). Nedenini açıklayın.
2. Stemming mi, lemmatization mı, her ikisi mi, yoksa hiçbiri mi. Nedenini açıklayın.
3. Belirli kütüphane çağrılarını adlandırın. İşlevleri adlandırın. NLTK dahil ise POS-tag çevirisini alıntılayın.
4. Kullanıcının test etmesi gereken bir başarısızlık modu.

Kullanıcıya görünür metin için stemming önermeyi reddedin. POS etiketleri olmadan lemmatization önermeyi reddedin. İngilizce olmayan girdiyi farklı bir hat gerektiriyor olarak işaretleyin.
```

## Alıştırmalar

1. **Kolay.** `tokenize` işlevini URL'leri tek token olarak koruyacak şekilde genişletin. Test: `tokenize("Visit https://example.com today.")` bir URL token'ı üretmelidir.
2. **Orta.** Porter 1b adımını uygulayın. Bir kelime bir sesli harf içeriyor ve `ed` veya `ing` ile bitiyorsa kaldırın. Çift ünsüz kuralını ele alın (`hopping -> hop`, `hopp` değil).
3. **Zor.** WordNet'i arama tablosu olarak kullanan ama WordNet'te giriş olmadığında Porter stemmer'ınıza geri dönen bir lemmatizer oluşturun. Etiketlenmiş bir corpus üzerinde saf WordNet ve saf Porter'a göre doğruluk ölçün.

## Anahtar Terimler

| Terim | İnsanların Söylediği | Gerçekte Ne Anlama Gelir |
|------|-----------------|-----------------------|
| Token | Bir kelime | Modelin tükettiği herhangi bir birim. Kelime, subword, karakter veya bayt olabilir. |
| Stem | Bir kelimenin kökü | Kural tabanlı ek çıkarma sonucu. Her zaman gerçek bir kelime değildir. |
| Lemma | Sözlük formu | Arayacağınız form. Doğru hesaplamak için dilbilgisel bağlam gerektirir. |
| POS tag | Kelime türü | NOUN, VERB, ADJ gibi kategoriler. Doğru lemmatization için gereklidir. |
| Morfoloji | Kelime şekil kuralları | Bir kelimenin tense, sayı, hal'e göre nasıl form değiştirdiği. Lemmatization buna bağlıdır. |

## İleri Okuma

- [Porter, M. F. (1980). An algorithm for suffix stripping](https://tartarus.org/martin/PorterStemmer/def.txt) — orijinal makale, beş sayfa, hâlâ en açıklayıcı açıklama.
- [spaCy 101 — linguistic features](https://spacy.io/usage/linguistic-features) — gerçek bir hattın nasıl bağlandığı.
- [NLTK book, chapter 3](https://www.nltk.org/book/ch03.html) — henüz düşünmediğiniz tokenization uç durumları.
