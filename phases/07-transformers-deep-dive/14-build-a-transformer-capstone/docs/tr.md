# Sıfırdan Bir Transformer İnşa Etme — Bitirme Projesi

> On üç ders. Bir model. Kısayol yok.

**Tür:** İnşa Et
**Diller:** Python
**Önkoşullar:** Faz 7 · 01'den 13'e kadar. Atlamayın.
**Süre:** ~120 dakika

## Sorun

Her makaleyi okudunuz. Dikkati, çoklu-baş bölmeleri, konumsal kodlamaları, encoder ve decoder bloklarını, BERT ve GPT kayıplarını, MoE'yi, KV-çerezi uyguladınız. Şimdi bunları bir görevde birlikte çalıştırın.

Bitirme projesi: karakter düzeyinde bir dil modelleme görevinde küçük bir sadece-decoder transformer'ı uçtan uca eğitin. Shakespeare okur. Yeni Shakespeare üretir. Dizüstü bilgisayarda 10 dakikadan az sürede eğitecek kadar küçüktür. Daha büyük bir veri kümesi ve daha uzun eğitimle değiştirildiğinde gerçek bir dil modeli elde edecek kadar doğrudur.

Bu, kursun "nanoGPT"'sidir. Orijinal değil — Karpathy'nin 2023 nanoGPT eğitimi, her öğrencinin en az bir kez yazdığı referans uygulamadır. Şekli alıyoruz ve ele aldığımız şeylere göre yeniden aletlendiriyoruz.

## Kavram

![Sıfırdan transformer blok diyagramı](../assets/capstone.svg)

Açıklamalı mimari:

```
input tokens (B, N)
   │
   ▼
token embedding + positional embedding  ◀── Ders 04 (RoPE seçeneği)
   │
   ▼
┌──── block × L ────────────────────┐
│  RMSNorm                          │  ◀── Ders 05
│  MultiHeadAttention (causal)      │  ◀── Ders 03 + 07 (nedensel maske)
│  residual                         │
│  RMSNorm                          │
│  SwiGLU FFN                       │  ◀── Ders 05
│  residual                         │
└────────────────────────────────── ┘
   │
   ▼
final RMSNorm
   │
   ▼
lm_head (tied to token embedding)
   │
   ▼
logits (B, N, V)
   │
   ▼
shift-by-one cross-entropy            ◀── Ders 07
```

### Ne sunuyoruz

- `GPTConfig` — tüm hiperparametreleri yapılandırmanız için tek yer.
- `MultiHeadAttention` — nedensel, toplu (batched), opsiyonel Flash tarzı yolla (PyTorch'un `scaled_dot_product_attention`).
- `SwiGLUFFN` — modern FFN.
- `Block` — ön-normalizasyon, artık-bağı sarılmış dikkat + FFN.
- `GPT` — gömmeler, yığılmış bloklar, LM kafası, generate().
- AdamW, kosinüs LR, gradyan kırpma (gradient clipping) ile eğitim döngüsü.
- Shakespeare metni üzerinde karakter-tokenizer.

### Ne sunmuyoruz

- RoPE — Ders 04'te kavramsal olarak uygulandı. Burada basitlik için öğrenilmiş konumsal gömmeler kullanıyoruz. Alıştırmalarda RoPE ile değiştirmeniz istenir.
- Üretim sırasında KV-çerez — her üretim adımında tüm önek üzerinde dikkat yeniden hesaplanır. Daha yavaş ama daha basit. Alıştırmalarda KV-çerez eklemeniz istenir.
- Flash Attention — PyTorch 2.0+ girdiler eşleştiğinde otomatik olarak dağıtır; `F.scaled_dot_product_attention` kullanıyoruz.
- MoE — blok başına tek FFN. MoE'yi Ders 11'de gördünüz.

### Hedef metrikler

Mac M2 dizüstü bilgisayarda, 4 katmanlı, 4 başlı, d_model=128 GPT, `tinyshakespeare.txt` üzerinde 2.000 adım eğitildiğinde:

- Eğitim kaybı ~4.2'den (rastgele) ~1,5'e yaklaşık 6 dakikada yakınsar.
- Örneklenmiş çıktı Shakespeare benzeri görünür: arkaik kelimeler, satır başları, "ROMEO:" gibi özel isimler ortaya çıkar.
- Kayıp (validation loss) (metnin son %10'u) eğitim kaybını yakından takip eder; bu boyut/bütçede aşırı uyum (overfitting) yoktur.

## İnşa Et

Bu ders PyTorch kullanır. `torch` yükleyin (CPU derlemesi yeterlidir). `code/main.py`'ye bakın. Betik şunları işler:

- `tinyshakespeare.txt` eksikse indirir (veya yerel kopyayı okur).
- Byte düzeyinde karakter tokenizer.
- %90/%10 eğitim/doğrulama ayrımı.
- Desteklenen donanımda bf16 otomatik döküm (autocast) ile eğitim döngüsü.
- Eğitim tamamlandıktan sonra örnekleme.

### Adım 1: veri

```python
text = open("tinyshakespeare.txt").read()
chars = sorted(set(text))
stoi = {c: i for i, c in enumerate(chars)}
itos = {i: c for c, i in stoi.items()}
encode = lambda s: [stoi[c] for c in s]
decode = lambda xs: "".join(itos[x] for x in xs)
```

#### Açıklama
65 benzersiz karakter. Küçük sözlük. 4 byte'lık vocab_size'a sığar. BPE yok, tokenizer dramı yok.

### Adım 2: model

`code/main.py`'ye bakın. Blok Ders 05'ten ders kitabındandır — ön-normalizasyon, RMSNorm, SwiGLU, nedensel MHA. 4/4/128 için parametre sayısı: ~800K.

### Adım 3: eğitim döngüsü

Uzunluk-256 token pencereden rastgele bir toplu (batch) alın. İleriye doğru geçiş. Bir kaydırma çapraz-entropisi. Geriye doğru geçiş. AdamW adımı. Günlük. Tekrar.

```python
for step in range(max_steps):
    x, y = get_batch("train")
    logits = model(x)
    loss = F.cross_entropy(logits.view(-1, vocab_size), y.view(-1))
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    opt.step()
    opt.zero_grad()
```

#### Açıklama
Bu klasik bir dil modeli eğitim döngüsüdür. Her adımda rastgele bir toplu alınır, ileriye doğru geçiş yapılır, kayıp hesaplanır, geriye doğru geçiş yapılır ve ağırlıklar güncellenir.

### Adım 4: örnekleme

Bir istem verildiğinde, tekrar tekrar ileriye doğru geçiş yapın, top-p logitlerinden örnekle, ekleyin ve devam edin. 500 token sonra durun.

### Adım 5: çıktıyı okuyun

2.000 adımdan sonra:

```
ROMEO:
Away and mild will not thy friend, that thou shalt wit:
The chief that well shame and hath been his friends,
...
```

Shakespeare değil. Ama Shakespeare benzeri. Dizüstü bilgisayarda ~800K parametre ve 6 dakika için net bir kazanç.

## Kullan

Bu bitirme projesi bir referans mimarisidir. Gerçek bir şeye dönüştürmek için üç genişletme:

1. **Tokenizer'ı değiştirin.** BPE kullanın (ör. `tiktoken.get_encoding("cl100k_base")`). Sözlük boyutu 65'ten ~50.000'e sıçrar. Model kapasitesinin telafi etmek için ölçeklenmesi gerekir.
2. **Daha büyük bir metin kümesi üzerinde eğitin.** `OpenWebText` veya `fineweb-edu` (HuggingFace) kullanın. Tek bir A100 üzerinde 10B token, 125M parametreli bir GPT için ~24 saat sürer.
3. **RoPE + KV-çerez + Flash Attention ekleyin.** Alttaki alıştırmalar her birinde size yol gösterir.

Bu, akıcı İngilizce üreten 125M parametreli bir GPT'ye dönüşür. Sınır modeli değil. Ancak aynı kod yolu — sadece daha büyüğü — 2026'da Karpathy, EleutherAI ve Allen Institute'un araştırma kontrol noktalarını eğitmek için kullandığı yoldur.

## Teslim Et

`outputs/skill-transformer-review.md`'ye bakın. Bu beceri, sıfırdan bir transformer uygulamasını önceki 13 dersin her birindeki doğruluk için inceler.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Eğitilmiş modelinizin son-adım doğrulama kaybının 2.0'nin altında olduğunu doğrulayın. `max_steps`'i 2.000'den 5.000'e değiştirin — doğrulama kaybı iyileşmeye devam eder mi?
2. **Orta.** Öğrenilmiş konumsal gömmeleri RoPE ile değiştirin. `MultiHeadAttention` içinde Q ve K'ya döndürmeyi uygulayın. Eğitin ve doğrulama kaybının en az aynı kadar düşük olduğunu doğrulayın.
3. **Orta.** Örnekleme döngüsüne bir KV-çerez uygulayın. Çerez ile ve çerez olmadan 500 token üretin. Dizüstü bilgisayarda gerçek zamanın 5–20× iyileşmesi gerekir.
4. **Zor.** Modele, bir sonraki artı bir token'ı tahmin eden ikinci bir kafa ekleyin (MTP — DeepSeek-V3'ten Çoklu-Token Tahmini). Ortak olarak eğitin. Yardımcı olur mu?
5. **Zor.** Blok başına tek FFN'i 4 uzmanlı bir MoE ile değiştirin. Yönlendirici + üst-2 yönlendirme. Eşleşen etkin parametrelerde doğrulama kaybının nasıl değiştiğini görün.

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| nanoGPT | "Karpathy'nin eğitim deposu" | Minimal sadece-decoder transformer eğitim kodu, ~300 LOC; kanonik referans. |
| tinyshakespeare | "Standart küçük metin kümesi" | ~1,1 MB metin; 2015'ten beri her karakter-LM eğitimi bunu kullanır. |
| Bağlı gömmeler (Tied embeddings) | "Girdi/çıktı matrisini paylaş" | LM kafası ağırlığı = token gömme matrisinin tersi; parametre tasarrufu, kaliteyi artırır. |
| bf16 otomatik döküm | "Eğitim hassasiyet hilesi" | İleriye/geriye doğru geçişi bf16'da çalıştır, optimize edici durumunu fp32'de tut; 2021'den beri standart. |
| Gradyan kırpma | "Sıçramaları durdur" | Küresel gradyan normunu 1.0'da sınırla; eğitim patlamalarını önler. |
| Kosinüs LR çizelgesi | "2020+ varsayılanı" | LR doğrusal olarak yükselir (ısınma) sonra kosinüs şeklinde tepe değerinin %10'una kadar azalır. |
| MFU | "Model FLOP Kullanımı" | Elde edilen FLOP / teorik tepe; 2026'da yoğun için %40, MoE için %30 güçlüdür. |
| Doğrulama kaybı | "Tutulmuş kayıp" | Modelin hiç görmediği veri üzerinde çapraz-entropi; aşırı uyum dedektörü. |

## İleri Okuma

- [Açıklamalı Transformer (Harvard NLP)](https://nlp.seas.harvard.edu/annotated-transformer/) — klasik açıklamalı uygulama.
