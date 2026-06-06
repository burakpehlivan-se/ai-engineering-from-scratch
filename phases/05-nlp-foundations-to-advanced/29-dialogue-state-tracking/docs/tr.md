# Diyalog Durumu İzleme

> "Kuzeyde ucuz bir restoran istiyorum... aslında orta seviye olsun... ve İtalyan ekleyin." Üç tur, üç durum güncellemesi. DST slot-değer sözlüğünü senkronize tutar ki rezervasyon çalışsın.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 5 · 17 (Sohbet Botları), Faz 5 · 20 (Yapılandırılmış Çıktılar)
**Süre:** ~75 dakika

## Problem

Görev odaklı bir diyalog sisteminde (task-oriented dialogue) kullanıcının hedefi bir slot-değer çiftleri kümesi olarak kodlanır: `{cuisine: italian, area: north, price: moderate}`. Her kullanıcı turu bir slot ekleyebilir, değiştirebilir veya kaldırabilir. Sistem tüm konuşmayı okumalı ve mevcut durumu doğru şekilde çıktıya vermelidir.

Tek bir slot'u yanlış alırsanız sistem yanlış restoranı rezervasyon eder, yanlış uçuşu planlar veya yanlış kartı tahsil eder. DST, kullanıcının söylediği ile backend'in gerçekleştirdiği arasındaki menteşedir.

LLM'lere rağmen 2026'da neden hâlâ önemli:

- Uyum-duyarlı alanlar (bankacılık, sağlık, havayolu rezervasyonu) serbest form üretimi değil, deterministik slot değerleri gerektirir.
- Araç kullanan ajanlar API'ler çağırmadan önce slot çözümlemesi hâlâ gerektirir.
- Çoklu tur düzeltmesi göründüğünden daha zor: "aslında hayır, Perşembe olsun."

Modern pipeline: klasik DST kavramları + LLM extractor'ları + yapılandırılmış çıktı koruma bariyerleri.

## Kavram

![DST: diyalog geçmişi → slot-değer durumu](../assets/dst.svg)

**Görev yapısı.** Bir şema alanları (restaurant, hotel, taxi) ve slot'larını (cuisine, area, price, people) tanımlar. Her slot boş olabilir, kapalı bir kümeden bir değerle dolu olabilir (price: {cheap, moderate, expensive}) veya serbest formda bir değer alabilir (name: "The Copper Kettle").

**İki DST formülasyonu.**

- **Sınıflandırma.** Her (slot, aday_değer) çifti için evet/hayır tahmin edin. Kapalı sözlüklü slot'lar için çalışır. 2020 öncesi standart.
- **Üretim.** Diyalog verildiğinde slot değerlerini serbest metin olarak üretin. Açık sözlüklü slot'lar için çalışır. Modern varsayılan.

**Metrik.** Ortak Hedef Doğruluğu (JGA, Joint Goal Accuracy) — *her* slot'un doğru olduğu tur oranıdır. Hep ya da hiç. MultiWOZ 2.4 liderlik tablosu 2026'da %83 civarında.

**Mimariler.**

1. **Kurallara dayalı (slot regex + anahtar kelime).** Dar alanlar için güçlü baseline. Hata ayıklanabilir.
2. **TripPy / BERT-DST.** BERT kodlaması ile kopyalama tabanlı üretim. LLM öncesi standart.
3. **LDST (LLaMA + LoRA).** Alan-slot promptlaması ile instruction-tuned LLM. MultiWOZ 2.4'te ChatGPT düzeyinde kaliteye ulaşır.
4. **Ontolojisiz (2024–26).** Şemayı atla; slot adlarını ve değerlerini doğrudan üretin. Açık alanları ele alır.
5. **Prompt + yapılandırılmış çıktı (2024–26).** Pydantic şemalı LLM + kısıtlanmış kodlama. 5 satır kod, production-hazır.

### Klasik başarıslık modları

- **Turlar arası özdeşleme.** "İlk seçeneğe sadık kalalım." Hangi seçeneğin çözülmesi gerekir.
- **Üzerine yazma vs. ekleme.** Kullanıcı "İtalyan ekleyin" diyor. cuisine'ı mı değiştiriyorsunuz yoksa mı ekliyorsunuz?
- **Örtük onaylar.** "Tamam süper" — bu sunulan rezervasyonu kabul etti mi?
- **Düzeltme.** "Aslında saat 19:00 olsun." Diğer slot'ları temizlemeden zamanı güncellemeli.
- **Önceki sistem konuşmasına özdeşleme.** "Evet, o." "O" hangisi?

## İnşa Et

### Adım 1: kurallara dayalı slot extractor

`code/main.py`'ye bakın. Regex + eş anlamlı sözlükler, dar alanlarda canonical utterance'ların %70'ini kapsar:

```python
CUISINE_SYNONYMS = {
    "italian": ["italian", "pasta", "pizza", "italy"],
    "chinese": ["chinese", "chow mein", "noodles"],
}


def extract_cuisine(utterance):
    for canonical, synonyms in CUISINE_SYNONYMS.items():
        if any(syn in utterance.lower() for syn in synonyms):
            return canonical
    return None
```

#### Açıklama
Canonical sözlüğün dışında kırılgandır. Deterministik slot onayları için çalışır.

### Adım 2: durum güncelleme döngüsü

```python
def update_state(state, utterance):
    new_state = dict(state)
    for slot, extractor in SLOT_EXTRACTORS.items():
        value = extractor(utterance)
        if value is not None:
            new_state[slot] = value
    for slot in NEGATION_CLEARS:
        if is_negated(utterance, slot):
            new_state[slot] = None
    return new_state
```

#### Açıklama
Üç değişmezlik:

- Kullanıcının dokunmadığı bir slot'u asla sıfırlamayın.
- Açıkça inkar ("mutfak umrumda değil") temizlemeli.
- Kullanıcı düzeltmesi ("aslında...") üzerine yazmalı, eklemeli.

### Adım 3: yapılandırılmış çıktı ile LLM-DST

```python
from pydantic import BaseModel
from typing import Literal, Optional
import instructor

class RestaurantState(BaseModel):
    cuisine: Optional[Literal["italian", "chinese", "indian", "thai", "any"]] = None
    area: Optional[Literal["north", "south", "east", "west", "center"]] = None
    price: Optional[Literal["cheap", "moderate", "expensive"]] = None
    people: Optional[int] = None
    day: Optional[str] = None


def llm_dst(history, llm):
    prompt = f"""You track the slot values of a restaurant booking across turns.
Dialogue so far:
{render(history)}

Update the state based on the latest user turn. Output only the JSON state."""
    return llm(prompt, response_model=RestaurantState)
```

#### Açıklama
Instructor + Pydantic geçerli bir durum nesnesini garanti eder. Regex yok, şema uyumsuzluğu yok, halüsinasyonlu slot yok.

### Adım 4: JGA değerlendirmesi

```python
def joint_goal_accuracy(predicted_states, gold_states):
    correct = sum(1 for p, g in zip(predicted_states, gold_states) if p == g)
    return correct / len(predicted_states)
```

#### Açıklama
Kalibrasyon: sistem TÜM slot'larda doğru olan tur oranıdır? MultiWOZ 2.4 için en iyi 2026 sistemleri: %80-83. Alan içi sisteminiz dar sözlüğünüzde bunu aşmalı, aksi halde LLM baseline sizi yener.

### Adım 5: düzeltme ele alma

```python
CORRECTION_CUES = {"actually", "no wait", "on second thought", "change that to"}


def is_correction(utterance):
    return any(cue in utterance.lower() for cue in CORRECTION_CUES)
```

#### Açıklama
Tespit edilen bir düzeltmede, üzerine ekleme yerine son güncellenen slot'un üzerine yazın. LLM yardımı olmadan doğru yapılması zordur. Modern kalıp: her zaman LLM'ın geçmiştten tüm durumu yeniden üretmesine izin verin, incrementally güncellemek yerine — bu düzeltmeleri doğal olarak ele alır.

## Tuzaklar

- **Tam geçmiş yeniden üretim maliyeti.** LLM'ın her turda durumu yeniden üretmesine izin vermek toplam O(n²) token'a mal olur. Geçmişi sınırlayın veya daha eski turları özetleyin.
- **Şema kayması.** Sonradan yeni slot'lar eklemek eski eğitim verisini bozar. Şemanızı sürümleyin.
- **Büyük/küçük harf duyarlılığı.** "Italian" vs "italian" vs "ITALIAN" — her yerde normalleştirin.
- **Örtük kalıtım.** Kullanıcı daha önce "4 kişi için" belirttiyse, farklı bir zaman için yeni istek people'ı temizlememeli. Her zaman tam geçmişi aktarın.
- **Serbest form vs. kapalı küme.** İsimler, zamanlar ve adresler serbest form slot gerektirir; mutfaklar ve alanlar kapalıdır. Şemada her ikisini karıştırın.

## Kullan

2026 stacki:

| Durum | Yaklaşım |
|-----------|----------|
| Dar alan (bir veya iki niyet) | Kurallara dayalı + regex |
| Geniş alan, etiketli veri mevcut | LDST (MultiWOZ tarzı veri üzerinde LLaMA + LoRA) |
| Geniş alan, etiket yok, production-hazır | LLM + Instructor + Pydantic şeması |
| Konuşmalı / ses | ASR + normalleştirici + LLM-DST |
| Çoklu alan rezervasyon akışı | Alan başına Pydantic modelleriyle şema-yönlü LLM |
| Uyum-duyarlı | Birincil kurallara dayalı, onay akışıyla LLM yedekleme |

## Ürün Olarak Kullan

`outputs/skill-dst-designer.md` olarak kaydedin:

```markdown
---
name: dst-designer
description: Design a dialogue state tracker — schema, extractor, update policy, evaluation.
version: 1.0.0
phase: 5
lesson: 29
tags: [nlp, dialogue, task-oriented]
---

Given a use case (domain, languages, vocab openness, compliance needs), output:

1. Schema. Domain list, slots per domain, open vs closed vocabulary per slot.
2. Extractor. Rule-based / seq2seq / LLM-with-Pydantic. Reason.
3. Update policy. Regenerate-whole-state / incremental; correction handling; negation handling.
4. Evaluation. Joint Goal Accuracy on a held-out dialogue set, slot-level precision/recall, confusion on the hardest slot.
5. Confirmation flow. When to explicitly ask the user to confirm (destructive actions, low-confidence extractions).

Refuse LLM-only DST for compliance-sensitive slots without a rule-based secondary check. Refuse any DST that cannot roll back a slot on user correction. Flag schemas without version tags.
```

#### Açıklama
Verilen kullanım durumu için bir diyalog durum izleyicisi tasarlayan — şema, extractor, güncelleme politikası, değerlendirme — bir skill tanımıdır.

## Alıştırmalar

1. **Kolay.** `code/main.py`'de 3 slot (cuisine, area, price) için kurallara dayalı durum izleyicisini oluşturun. 10 el yapımı diyalogda test edin. JGA'yı ölçün.
2. **Orta.** Aynı veri setini Instructor + Pydantic + küçük bir LLM ile çalıştırın. JGA'yı karşılaştırın. En zor turları inceleyin.
3. **Zor.** Her ikisini de uygulayın ve yönlendirin: kurallara dayalı birincil, kurallara dayalı <2 slot düşük güvenle çıkardığında LLM yedekleme. Birleşik JGA'yı ve tur başına çıkarım maliyetini ölçün.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| DST | Diyalog durumu izleme | Diyalog turları boyunca slot-değer sözlüğünü koruma. |
| Slot | Kullanıcı niyetinin birimi | Backend'in gerektiği adlandırılmış parametre (mutfak, tarih). |
| Alan (Domain) | Görev alanı | Restoran, otel, taksi — slot kümeleri. |
| JGA | Ortak Hedef Doğruluğu | Her slot'un doğru olduğu tur oranı. Hep ya da hiç. |
| MultiWOZ | Benchmark | Çoklu alan WOZ veri seti; standart DST değerlendirmesi. |
| Ontolojisiz DST | Şema yok | Slot adlarını ve değerlerini doğrudan üret, sabit liste yok. |
| Düzeltme | "Aslında..." | Daha önce dolu bir slot'un üzerine yazan tur. |

## İleri Okuma

- [Budzianowski et al. (2018). MultiWOZ — A Large-Scale Multi-Domain Wizard-of-Oz](https://arxiv.org/abs/1810.00278) — klasik benchmark.
- [Feng et al. (2023). Towards LLM-driven Dialogue State Tracking (LDST)](https://arxiv.org/abs/2310.14970) — DST için LLaMA + LoRA instruction tuning.
- [Heck et al. (2020). TripPy — A Triple Copy Strategy for Value Independent Neural Dialog State Tracking](https://arxiv.org/abs/2005.02877) — kopyalama tabanlı DSTWorking horse.
- [King, Flanigan (2024). Unsupervised End-to-End Task-Oriented Dialogue with LLMs](https://arxiv.org/abs/2404.10753) — EM tabanlı denetimsiz TOD.
- [MultiWOZ leaderboard](https://github.com/budzianowski/multiwoz) — kanonik DST sonuçları.
