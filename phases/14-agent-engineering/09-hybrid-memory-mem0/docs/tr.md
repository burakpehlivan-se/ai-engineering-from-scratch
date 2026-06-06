# Hibrit Hafıza: Vektör + Graf + KV (Mem0)

> Mem0 (Chhikara ve diğerleri, 2025) hafızayı paralel üç depo olarak ele alır — семан틱 benzerlik için vektör, hızlı olgu arama için KV, varlık-ilişki akıl yürütmesi için graf. Bir puanlama katmanı almadaki üçünü birleştirir. Bu, 2026'da harici hafıza için production standardıdır.

**Tür:** İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 · 07 (MemGPT), Faz 14 · 08 (Letta Blokları)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Tek bir deponun (yalnızca vektör, yalnızca graf, yalnızca KV) agent hafızası için neden yetersiz olduğunu açıklayın.
- Mem0'ın üç paralel deposunu ve her birinin neyi optimize ettiğini adlandırın.
- Mem0'ın birleştirme puanlamasını (relevance, importance, recency) ve neden ağırlıklı toplam olduğunu, hiyerarşi olmadığını açıklayın.
- Üçüne de yazan `add()` ve sonuçları birleştiren `search()` ile stdlib'da bir üç depolu hafıza uygulayın.

## Problem

Tek bir depo üç sorgu sınıfından biri için yanlıştır:

- **Semantik benzerlik** — "geçen hafta agent kayması hakkında ne konuşmuştuk?" Vektör kazanır; KV ve graf kaybeder.
- **Olgu arama** — "kullanıcının telefon numarası nedir?" KV kazanır; vektör boşa harcanır, graf aşırıdır.
- **İlişki akıl yürütmesi** — "hangi müşteriler aynı fatura varlığını paylaşıyor?" Graf kazanır; vektör ve KV cevap veremez.

Production agent'ları tek bir oturumda üçünü de çağırır. Tek depolu bir hafıza her zaman ikisi için yanlıştır. Mem0 katkısı, üçünü de tek bir `add`/`search` yüzeyinin arkasına bağlamak ve birleştirme puanlama fonksiyonuyla birleştirmektir.

## Kavram

### Üç depo paralel

Mem0 (arXiv:2504.19413, Nisan 2025) `add(text, user_id, metadata)` üzerinde:

1. Metinden aday olguları çıkarır (LLM tarafından驱动 bir adım).
2. Her olguyu semantik arama için vektör deposuna (embedding) yazar.
3. Her olguyu O(1) arama için (user_id, fact_type, entity) ile anahtarlı KV deposuna yazar.
4. Her olguyu ilişki sorguları için tipli kenarlar olarak graf deposuna (Mem0g) yazar.

`search(query, user_id)` üzerinde:

1. Vektör deposu embedding kosinüsüne göre top-k döndürür.
2. KV deposu sorgudan türetilen (user_id, type, entity) ile doğrudan eşleşmeleri döndürür.
3. Graf deposu sorgu varlıklarından erişilebilir alt grafı döndürür.
4. Birleştirme katmanı üçünü birleştirir.

### Birleştirme puanlama

```text
score = w_relevance * relevance(q, record)
      + w_importance * importance(record)
      + w_recency * recency(record)
```

- **Relevance** — vektör kosinüsü, KV tam eşleşme, graf yol ağırlığı.
- **Importance** — yazma sırasında etiketlenmiş veya öğrenilmiş (bazı olgular daha önemlidir: isimler, ID'ler, politikalar).
- **Recency** — son yazma veya okumadan bu yana üstel azalma.

Ağırlıklar ürüne göre ayarlanır. Sohbet agent'ları için daha yüksek `w_recency`; uyumluluk agent'ları için daha yüksek `w_importance`; arama agent'ları için daha yüksek `w_relevance`.

### Mem0g ve zamansal akıl yürütmesi

Mem0g bir çatışma dedektörü ekler. Yeni bir olgu mevcut bir kenarla çeliştiğinde, mevcut kenar geçersiz olarak işaretlenir ancak silinmez. Zamansal sorgular ("kullanıcının Mart'taki şehri neydi?") geçerli-zaman-alt-grafını dolaşır.

Bu, Letta'nın geçersiz kılma kalıbının genelleştirdiği uyumluluk düzeyindeki davranıştır.

### Benchmark sayıları

Mem0 makalesi rapor ediyor (2025):

- **LoCoMo** (uzun biçimli konuşma hafızası): 91.6
- **LongMemEval** (uzun vadeli epizodik hafıza): 93.4
- **BEAM 1M** (1M-token hafıza benchmark'ı): 64.1

Karşılaştırma temelleri (tam bağlam 128k LLM, düz vektör deposu, düz KV) hepsi 10+ puan kaybeder. Benchmark'lar tek başına seçimi haklı çıkarmaz — operasyonel şekil haklı çıkarır — ancak sayılar tasarımın yuvarlama hatası olmadığını gösterir.

### Kapsam sınıflandırması

Mem0 hafızayı kempa göre böler:

- **Kullanıcı hafızası** — oturumlar arası kalıcı, `user_id` ile anahtarlı.
- **Oturum hafızası** — tek bir thread içinde kalıcı.
- **Agent hafızası** — agent başına örnek durumu.

Her yazma bir kapsam seçer. Alma, kapsam ağırlıklarıyla kapsamlar arası sorgulanabilir. Kapsamları düşünmeden karıştırmak "asistan Alice'e Bob'un projesi hakkında söyledi" olaylarının nasıl oluştuğudur.

### Bu kalıp nerede yanlış gider

- **Embedding kayması.** İlk yüzlerce sorguda doğru görünen vektör sonuçları corpus büyüdükçe düşer. En çok kullanılan-N kaydının periyodik yeniden-embed'ini ekleyin.
- **KV şema kayması.** `(user_id, type, entity)` basit görünür ancak her ekip kendi `type`'ını ekleyene kadar. Tip setini üç aylık olarak denetleyin.
- **Graf patlaması.** Bir gürültülü çıkarıcı mesaj başına 50 kenar ekler. Her `add` çağrısında graf yazmasını sınırlayın; düşük güvenilirlikli kenarları düşürün.

## İnşa Et

`code/main.py` üç depo kalıbını stdlib'da uygular:

- `VectorStore` — embedding yerine basit token-overlap benzerliği.
- `KVStore` — `(user_id, fact_type, entity)` ile anahtarlı dict.
- `GraphStore` — tipli kenarlar (subject, relation, object, valid).
- `Mem0` — `add()`, `search()`, birleştirme puanlaması ve kapsam farkındalıklı aramayla üst düzey cephe (facade).
- Çoklu kullanıcı, çoklu oturum konuşmasında çalışılmış bir trace.

Çalıştırın:

```bash
python3 code/main.py
```

Çıktı üç ayrı recall yolu artı birleştirilmiş top-k gösterir. `main()`'in üstündeki puanlama ağırlıklarını çevirin ve sıralamanın nasıl değiştiğini izleyin.

## Kullan

- **Mem0 (Apache 2.0)** — production-ready. Postgres + Qdrant + Neo4j ile self-hosted veya yönetilen bulut.
- **Letta** — üç katmanlı core/recall/archival; kendi vektör ve graf arka uçlarınızı getirin.
- **Zep** — zamansal KG ve olgu çıkarma ile ticari alternatif.
- **Özel inşaatlar** — çıkarıcı (uyumluluk) veya birleştirme ağırlıkları (sesin hakim olduğu ses agent'ları) üzerinde tam kontrol gerektiğinde.

## Teslim Et

`outputs/skill-hybrid-memory.md`, birleştirme puanlayıcısı, kapsam sınıflandırması ve zamansal geçersiz kılma bağlı üç depolu bir hafıza iskeleti üretir.

## Alıştırmalar

1. Toy vektör benzerliğini gerçek bir embedding modeliyle (sentence-transformers, Ollama, OpenAI embeddings) değiştirin. Sentetik uzun bir konuşma üzerinde recall@10 ölçün. Sıralama 1000 yazımda kayıyor mu?
2. Zamansal sorgu ekleyin: `search(query, as_of=timestamp)`. Yalnızca o zamanda veya önce geçerli kayıtları döndürün. Hangi depoya en çok iş düşer?
3. Bir çatışma dedektörü uygulayan: gelen bir olgu bir graf kenarıyla çelişiyorsa eski kenarı geçersiz kılın ve her ikisini de kaydedin. "Kullanıcı Berlin'de yaşıyor" -> "Kullanıcı Lizbon'da yaşıyor" üzerinde test edin.
4. Birleştirme puanlayıcısını `user_feedback` boyutu (alınan kayıtlarda baş aşağı) ekleyecek şekilde taşıyın. Oyun oynamayı (agent'ın zaten beğendiği kayıtları yalnızca döndürmesi) nasıl önlersiniz?
5. Mem0 dokümanlarını okuyun (`docs.mem0.ai`). Toy kodu `mem0` istemci çağrılarına taşıyın. Aynı 20 test sorgusu üzerinde arama kalitesini karşılaştırın.

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Hybrid memory | "Vektör artı graf artı KV" | Paralel yazılan üç depo, aramada birleştirilir |
| Fact extraction | "Hafıza işleme" | Metni (varlık, ilişki, olgu) tuple'larına bölen LLM adımı |
| Fusion scoring | "Relevance sıralaması" | Relevance, importance, recency ağırlıklı toplamı |
| Scope | "Hafıza ad alanı" | user / session / agent — kimin neyi gördüğünü belirler |
| Mem0g | "Hafıza grafı" | İlişki sorguları için zamansal geçerlilikle tipli kenarlar |
| Temporal invalidation | "Yumuşak silme" | Çelişen kenarları geçersiz işaretle; asla silme |
| Embedding drift | "Arama çürümesi" | Corpus büyüdükçe vektör kalitesi düşer; periyodik olarak yeniden embed edin |

## İleri Okuma

- [Chhikara ve diğerleri, Mem0 (arXiv:2504.19413)](https://arxiv.org/abs/2504.19413) — orijinal makale
- [Mem0 docs](https://docs.mem0.ai/platform/overview) — production API, SDK'lar, yönetilen bulut
- [Packer ve diğerleri, MemGPT (arXiv:2310.08560)](https://arxiv.org/abs/2310.08560) — sanal bağlam öncülü
- [Letta, Memory Blocks blog](https://www.letta.com/blog/memory-blocks) — üç katmanlı kardeş tasarım
