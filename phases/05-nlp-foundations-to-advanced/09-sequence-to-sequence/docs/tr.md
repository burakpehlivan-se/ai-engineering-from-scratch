# Diziden Diziye (Sequence-to-Sequence) Modeller

> Bir çevirmen gibi davranan iki RNN. Vardıkları darboğaz, attention'ın var olma nedenidir.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 5 · 08 (Metin İçin CNN + RNN), Faz 3 · 11 (PyTorch'a Giriş)
**Süre:** ~75 dakika

## Problem

Sınıflandırma, değişken uzunluktaki bir diziyi tek bir etikete eşler. Çeviri ise değişken uzunluktaki bir diziyi başka bir değişken uzunluktaki diziye eşler. Giriş ve çıkış farklı sözlüklerde, farklı dillerde yaşar ve uzunluk eşitliği garanti edilmez.

Seq2seq mimarisi (Sutskever, Vinyals, Le, 2014) bunu kasıtlı olarak basit bir tarifle çözdü. İki RNN. Birincisi kaynak cümlenin okur ve sabit boyutlu bir bağlam vektörü (context vector) üretir. İkincisi bu vektörü okur ve hedef cümleyi token token üretir. Ders 08'de yazdığınız aynı kod, sadece farklı şekilde birleştirilir.

Bunu iki nedenle çalışmalısınız. Birincisi, bağlam vektörü darboğazı NLP'deki en öğretici başarı başarısızlığıdır. Attention ve transformer'ların iyi olduğu her şeyi motive eder. İkincisi, eğitim tarifi (öğretici zorlama / teacher forcing, zamanlamalı örneklem / scheduled sampling, çıkarımda ışın arama / beam search) LLM'ler dahil her modern üretim sistemine hâlâ uygulanır.

## Kavram

**Kodlayıcı (Encoder).** Kaynak cümlenin okuyan bir RNN. Son gizli durumu **bağlam vektörüdür** — tüm girişin sabit boyutlu bir özeti. Kaynağı kaybetmediği varsayılır.

**Kod çözücü (Decoder).** Bağlam vektöründen başlatılan başka bir RNN. Her adımda daha önce üretilen token'ı giriş olarak alır ve hedef sözlük üzerinde bir dağılım üretir. Örnekleme veya argmax ile bir sonraki token'ı seçer. Geri besler. Bir `<EOS>` token'ı üretilene veya maks uzunluğa ulaşılana kadar tekrarlar.

**Eğitim:** Her kod çözücü adımında çapraz entropi kaybı (cross-entropy loss), dizi boyunca toplanır. Her iki ağ üzerinden standart zaman boyunca geri yayılım (backpropagation through time).

**Öğretici zorlama (Teacher forcing).** Eğitim sırasında kod çözücünün `t`'deki girdisi, kod çözücünün kendi önceki tahmini değil, `t-1`'deki *gerçek* tokenıdır. Bu eğitimi stabilize eder; olmadan, erken hatalar kademeli olarak yayılır ve model hiçbir şey öğrenemez. Çıkarımda modelin kendi tahminlerini kullanmanız gerekir, bu yüzden her zaman eğitim/çıkarma dağılım farkı vardır. Bu farka **maruz kalma yanlılığı (exposure bias)** denir.

**Darboğaz.** Kodlayıcının kaynak hakkında öğrendiği her şey tek bir bağlam vektörüne sıkıştırılmalıdır. Uzun cümleler ayrıntı kaybeder. Nadir kelimeler bulanıklaşır. Yeniden sıralama (chat noir vs. black cat) hesaplanmak yerine ezberlenmelidir.

Attention (ders 10), kod çözücünün sadece son kodlayıcı durumuna değil, *her bir* kodlayıcı gizli durumuna bakmasını sağlayarak bunu çözer. Bu işin tüm özüdür.

## İnşa Et

### Adım 1: bir kodlayıcı

```python
import torch
import torch.nn as nn


class Encoder(nn.Module):
    def __init__(self, src_vocab_size, embed_dim, hidden_dim):
        super().__init__()
        self.embed = nn.Embedding(src_vocab_size, embed_dim, padding_idx=0)
        self.gru = nn.GRU(embed_dim, hidden_dim, batch_first=True)

    def forward(self, src):
        e = self.embed(src)
        outputs, hidden = self.gru(e)
        return outputs, hidden
```

`outputs` `[batch, seq_len, hidden_dim]` şeklindedir — her giriş pozisyonu için bir gizli durum. `hidden` `[1, batch, hidden_dim]` şeklindedir — son adım. Ders 08'de "sınıflandırma için çıktılar üzerinde havuzlama yapın" demiştik. Burada son gizli durumu bağlam vektörü olarak tutuyoruz ve adım bazlı çıktıları görmezden geliyoruz.

### Adım 2: bir kod çözücü

```python
class Decoder(nn.Module):
    def __init__(self, tgt_vocab_size, embed_dim, hidden_dim):
        super().__init__()
        self.embed = nn.Embedding(tgt_vocab_size, embed_dim, padding_idx=0)
        self.gru = nn.GRU(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, tgt_vocab_size)

    def forward(self, token, hidden):
        e = self.embed(token)
        out, hidden = self.gru(e, hidden)
        logits = self.fc(out)
        return logits, hidden
```

Kod çözücü tek adımda çağrılır. Giriş: tek token'lardan oluşan bir batch ve mevcut gizli durum. Çıkış: bir sonraki token için sözlük logit'leri ve güncellenmiş gizli durum.

### Adım 3: öğretici zorlamalı eğitim döngüsü

```python
def train_batch(encoder, decoder, src, tgt, bos_id, optimizer, teacher_forcing_ratio=0.9):
    optimizer.zero_grad()
    _, hidden = encoder(src)
    batch_size, tgt_len = tgt.shape
    input_token = torch.full((batch_size, 1), bos_id, dtype=torch.long)
    loss = 0.0
    loss_fn = nn.CrossEntropyLoss(ignore_index=0)

    for t in range(tgt_len):
        logits, hidden = decoder(input_token, hidden)
        step_loss = loss_fn(logits.squeeze(1), tgt[:, t])
        loss += step_loss
        use_teacher = torch.rand(1).item() < teacher_forcing_ratio
        if use_teacher:
            input_token = tgt[:, t].unsqueeze(1)
        else:
            input_token = logits.argmax(dim=-1)

    loss.backward()
    optimizer.step()
    return loss.item() / tgt_len
```

İsme değer iki ayar. `ignore_index=0` padding token'lar üzerindeki kaybı atlar. `teacher_forcing_ratio`, her adımda gerçek token ile modelin tahminini kullanma olasılığıdır. 1.0 ile başlayın (tam öğretici zorlama) ve eğitim boyunca ~0.5'e kadar düşürün, böylece maruz kalma yanlılığı (exposure bias) kapatılır.

### Adım 4: çıkarma döngüsü (açgözlü / greedy)

```python
@torch.no_grad()
def greedy_decode(encoder, decoder, src, bos_id, eos_id, max_len=50):
    _, hidden = encoder(src)
    batch_size = src.shape[0]
    input_token = torch.full((batch_size, 1), bos_id, dtype=torch.long)
    output_ids = []
    for _ in range(max_len):
        logits, hidden = decoder(input_token, hidden)
        next_token = logits.argmax(dim=-1)
        output_ids.append(next_token)
        input_token = next_token
        if (next_token == eos_id).all():
            break
    return torch.cat(output_ids, dim=1)
```

Açgözlü kodlama her adımda en yüksek olasılıklı token'ı seçer. Yoldan çıkabilir: bir token'a bir kez karar verildiğinde geri alınamaz. **Işın arama (beam search)** en iyi `k` tamamlanmamış diziyi canlı tutar ve sonunda en yüksek puanlı tamamlanmış olanı seçer. Işın genişliği 3-5 standarttır.

### Adım 5: darboğaz, gösterim

Modeli bir oyuncak kopyalama görevi üzerinde eğitin: kaynak `[a, b, c, d, e]`, hedef `[a, b, c, d, e]`. Dizi uzunluğunu artırın. Doğruluğu gözlemleyin.

```
seq_len=5   copy accuracy: 98%
seq_len=10  copy accuracy: 91%
seq_len=20  copy accuracy: 62%
seq_len=40  copy accuracy: 23%
```

Tek bir GRU gizli durumu, 40 token'lık bir girişi kayıpsız olarak ezberleyemez. Bilgi her kodlayıcı adımında mevcuttur, ama kod çözücü sadece son durumu görür. Attention bunu doğrudan çözer.

## Kullan

PyTorch'ta `nn.Transformer` ve `nn.LSTM` tabanlı seq2seq şablonları vardır. Hugging Face'in `transformers` kütüphanesi milyarlarca token üzerinde eğitilmiş tam kodlayıcı-kod çözücü modelleri (BART, T5, mBART, NLLB) sunar.

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tok = AutoTokenizer.from_pretrained("facebook/bart-base")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-base")

src = tok("Translate this to French: Hello, how are you?", return_tensors="pt")
out = model.generate(**src, max_new_tokens=50, num_beams=4)
print(tok.decode(out[0], skip_special_tokens=True))
```

Modern kodlayıcı-kod çözücü modeller RNN'leri transformer ile değiştirdi. Üst düzey şekil (kodlayıcı, kod çözücü, token-by-token üretim) 2014 seq2seq makalesiyle aynıdır. Her bloğun içindeki mekanizma farklıdır.

### RNN tabanlı seq2seq'e ne zaman başvurulur

Yeni projeler için neredeyse hiç. İstisnalar:

- Girdiyi token token tüketen, sınırlı bellekle akışlı çeviri (streaming translation).
- Transformer bellek maliyetinin yüksek olduğu cihaz üzerinde metin üretimi.
- Pedagoji. Kodlayıcı-kod çözücü darboğazını anlamak, transformer'ların neden kazandığını anlamanın en hızlı yoludur.

### Maruz kalma yanlılığı ve azaltma yolları

- **Zamanlamalı örneklem (Scheduled sampling).** Eğitim boyunca öğretici zorlama oranını azaltarak modelin kendi hatalarından kurtulmayı öğrenmesini sağlar.
- **Asgari risk eğitimi (Minimum risk training).** Token bazlı çapraz entropi yerine cümle bazlı BLEU puanı üzerinde eğitin. İstediğinize daha yakındır.
- **Pekiştirmeli öğrenme ince ayarı (Reinforcement learning fine-tuning).** Dizi üreteci (sequence generator) bir metrik ile ödüllendirir. Modern LLM RLHF'inde kullanılır.

Üçü de transformer tabanlı üretime hâlâ uygulanır.

## Ürün Haline Getir

`outputs/prompt-seq2seq-design.md` olarak kaydedin:

```markdown
---
name: seq2seq-design
description: Design a sequence-to-sequence pipeline for a given task.
phase: 5
lesson: 09
---

Given a task (translation, summarization, paraphrase, question rewrite), output:

1. Architecture. Pretrained transformer encoder-decoder (BART, T5, mBART, NLLB) is the default. RNN-based seq2seq only for specific constraints.
2. Starting checkpoint. Name it (`facebook/bart-base`, `google/flan-t5-base`, `facebook/nllb-200-distilled-600M`). Match the checkpoint to task and language coverage.
3. Decoding strategy. Greedy for deterministic output, beam search (width 4-5) for quality, sampling with temperature for diversity. One sentence justification.
4. One failure mode to verify before shipping. Exposure bias manifests as generation drift on longer outputs; sample 20 outputs at the 90th-percentile length and eyeball.

Refuse to recommend training a seq2seq from scratch for under a million parallel examples. Flag any pipeline that uses greedy decoding for user-facing content as fragile (greedy repeats and loops).
```

## Alıştırmalar

1. **Kolay.** Oyuncak kopyalama görevini uygulayın. Hedefin kaynakla eşleştiği giriş-çıkış çiftleri üzerinde bir GRU seq2seq eğitin. 5, 10, 20 uzunluklarda doğruluğu ölçün. Darboğazın tekrar üretin.
2. **Orta.** Işın genişliği 3 ile işın arama kodlaması ekleyin. Küçük bir paralel corpus üzerinde açgözlü kodlamaya karşı BLEU ölçün. İşın aramanın nerede kazandığını (genellikle son token'larda) ve nerede fark yaratmadığını belgeleyin.
3. **Zor.** `facebook/bart-base` modelini 10 bin çiftlik bir paraphrase veri seti üzerinde ince ayarlayın. İnce ayarlanmış modelin 4-wide beam çıkışını, temel modelin (base model) ayrı tutulan girdiler üzerindeki çıkışıyla karşılaştırın. BLEU'yu bildirin ve 10 niteliksel örnek seçin.

## Anahtar Terimler

| Terim | İnsanlar ne söyler | Aslında ne anlama gelir |
|-------|-------------------|------------------------|
| Kodlayıcı (Encoder) | Giriş RNN'i | Kaynağı okur. Adım bazlı gizli durumlar ve son bir bağlam vektörü üretir. |
| Kod çözücü (Decoder) | Çıkış RNN'i | Bağlam vektöründen başlatılır. Hedef token'ları tek tek üretir. |
| Bağlam vektörü (Context vector) | Özet | Son kodlayıcı gizli durumu. Sabit boyutlu. Attention'ın çözdüğü darboğaz. |
| Öğretici zorlama (Teacher forcing) | Gerçek token'ları kullan | Eğitim sırasında gerçek önceki token'ı besler. Öğrenmeyi stabilize eder. |
| Maruz kalma yanlılığı (Exposure bias) | Eğitim/test farkı | Gerçek token'larla eğitilmiş model kendi hatalarından kurtulmayı hiç pratik yapmamıştır. |
| Işın araması (Beam search) | Daha iyi kodlama | Her adımda açgözlü olarak karar vermek yerine en iyi k tamamlanmamış diziyi canlı tutar. |

## İleri Okuma

- [Sutskever, Vinyals, Le (2014). Sequence to Sequence Learning with Neural Networks](https://arxiv.org/abs/1409.3215) — orijinal seq2seq makalesi. Dört sayfa.
- [Cho ve diğerleri (2014). Learning Phrase Representations using RNN Encoder-Decoder for Statistical Machine Translation](https://arxiv.org/abs/1406.1078) — GRU ve kodlayıcı-kod çözücü çerçevesini tanıttı.
- [Bahdanau, Cho, Bengio (2014). Neural Machine Translation by Jointly Learning to Align and Translate](https://arxiv.org/abs/1409.0473) — attention makalesi. Bu dersten hemen sonra okuyun.
- [PyTorch Sıfırdan NLP Eğitimi](https://pytorch.org/tutorials/intermediate/seq2seq_translation_tutorial.html) — uygulanabilir seq2seq + attention kodu.
