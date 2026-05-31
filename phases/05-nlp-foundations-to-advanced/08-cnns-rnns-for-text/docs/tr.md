# Metin İçin CNN ve RNN

> Evrişimler (convolutions) n-gram'ları öğrenir. Özyinelemeler (recurrences) hatırlar. Her ikisi de attention tarafından geçersiz kılınır. Her ikisi de kısıtlı donanımda hâlâ önemlidir.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 3 · 11 (PyTorch'a Giriş), Faz 5 · 03 (Kelime Gömme), Faz 4 · 02 (Sıfırdan Evrişimler)
**Süre:** ~75 dakika

## Problem

TF-IDF ve Word2Vec, kelime sırasını göz ardı eden düz vektörler üretiyordu. Bunlar üzerine inşa edilmiş bir sınıflandırıcı `dog bites man` ile `man bites dog` arasındaki farkı anlayamazdı. Kelime sırası bazen sinyali taşıyordu.

Transformer'lar gelmeden önce bu boşluğu dolduran iki mimari aile vardı.

**Metin için evrişimsel ağlar (TextCNN).** Kelime gömme (word embedding) dizileri üzerinde 1D evrişimler uygular. Genişliği 3 olan bir filtre öğrenilebilir bir trigram dedektörüdür: üç kelimeyi kapsar ve bir puan çıktı verir. Farklı genişliklerde (2, 3, 4, 5) filtreleri üst üste koyarak çok ölçekli (multi-scale) desenleri algılar. Maks havuzlama (max-pooling) ile sabit boyutlu bir temsile dönüştürür. Düz, paralel, hızlı.

**Özyinelemeli ağlar (RNN, LSTM, GRU).** Tokenları tek tek işler, ileriye bilgi taşıyan bir gizli durum (hidden state) korur. Sıralı, bellek taşıyan, esnek giriş uzunlukları. 2014'ten 2017'ye kadar dizi modellemeye (sequence modeling) hükmetti, sonra attention ortaya çıktı.

Bu ders her ikisini de inşa eder, ardından attention'ı motive eden hatayı adlandırır.

## Kavram

**TextCNN** (Kim, 2014). Tokenlar gömülür. Genişliği `k` olan bir 1D evrişim, filtreleri ardışık `k`-gram'ların üzerine kaydırır ve bir harita çıkışı (feature map) üretir. Bu harita üzerindeki genel maks havuzlama (global max-pooling) en güçlü aktivasyonu seçer. Farklı genişliklerden havuzlanmış çıktıları birleştirir (concatenate). Bir sınıflandırıcı kafasına besler.

Neden çalışır? Bir filtre öğrenilebilir bir n-gram'dır. Maks havuzlama konumdan bağımsızdır, bu yüzden "not good" incelemenin başında da ortasında da aynı özelliği tetikler. 100 filtreli üç filtre genişliği size 300 öğrenilmiş n-gram dedektörü verir. Eğitim paraleldir; sıralı bağımlılık yoktur.

**RNN.** Her zaman adımında `t`, gizli durum `h_t = f(W * x_t + U * h_{t-1} + b)` olarak güncellenir. `W`, `U`, `b` zaman boyunca paylaşılır. Zaman `T`'deki gizli durum tüm ön ekin (prefix) bir özetidir. Sınıflandırma için `h_1 ... h_T` üzerinde havuzlama yapılır (maks, ortalama veya sonuncu).

Sade RNN'ler kaybolan gradyan (vanishing gradient) sorunu yaşar. **LSTM** neyi unutacağını, neyi depolayacağını ve neyi çıkaracağını karar veren kapılar (gates) ekler, uzun diziler boyunca gradyanları stabilize eder. **GRU** LSTM'i iki kapıya basitleştirir; daha az parametre ile benzer performans gösterir.

**İki yönlü RNN'ler (Bidirectional RNNs)** bir RNN'i ileriye,另一个ını geriye çalıştırır ve gizli durumları birleştirir. Her token'ın temsili hem sol hem sağ bağlamı (context) görür. Etiketleme görevleri için gereklidir.

## İnşa Et

### Adım 1: PyTorch ile TextCNN

```python
import torch
import torch.nn as nn
import torch.nn.functional as F


class TextCNN(nn.Module):
    def __init__(self, vocab_size, embed_dim, n_classes, filter_widths=(2, 3, 4), n_filters=64, dropout=0.3):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.convs = nn.ModuleList([
            nn.Conv1d(embed_dim, n_filters, kernel_size=k)
            for k in filter_widths
        ])
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(n_filters * len(filter_widths), n_classes)

    def forward(self, token_ids):
        x = self.embed(token_ids).transpose(1, 2)
        pooled = []
        for conv in self.convs:
            c = F.relu(conv(x))
            p = F.max_pool1d(c, c.size(2)).squeeze(2)
            pooled.append(p)
        h = torch.cat(pooled, dim=1)
        return self.fc(self.dropout(h))
```

`transpose(1, 2)` operasyonu `[batch, seq_len, embed_dim]` tensörünü `[batch, embed_dim, seq_len]`形状ına dönüştürür çünkü `nn.Conv1d` orta ekseni kanal (channel) olarak işler. Havuzlanmış çıktı, giriş uzunluğundan bağımsız olarak sabit boyutludur.

### Adım 2: LSTM sınıflandırıcısı

```python
class LSTMClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, n_classes, bidirectional=True, dropout=0.3):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=bidirectional)
        factor = 2 if bidirectional else 1
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim * factor, n_classes)

    def forward(self, token_ids):
        x = self.embed(token_ids)
        out, _ = self.lstm(x)
        pooled = out.max(dim=1).values
        return self.fc(self.dropout(pooled))
```

Dizi üzerinde maks havuzlama yapın, son durum havuzlaması değil. Sınıflandırma için maks havuzlama genellikle son gizli durumu almaktan daha iyi sonuç verir çünkü uzun bir dizinin sonundaki bilgi son duruma baskın çıkma eğilimindedir.

### Adım 3: kaybolan gradyan gösterimi (sezgisel açıklama)

Kapı mekanizması olmayan düz bir RNN, uzun menzilli bağımlılıkları (long-range dependencies) öğrenemez. Bir oyuncak görevi düşünün: bir dizide `A` token'ının herhangi bir yerde görünüp görünmediğini tahmin edin. `A` 1. pozisyondaysa ve dizi 100 token uzunluğundaysa, kayıptan gelen gradyan 99 kez tekrarlanan ağırlık çarpımından geriye akmalıdır. Ağırlık 1'den küçükse gradyan kaybolur (vanishes). 1'den büyükse patlar (explodes).

```python
def vanishing_gradient_sim(seq_len, recurrent_weight=0.9):
    import math
    return math.pow(recurrent_weight, seq_len)


# At weight=0.9 over 100 steps:
#   0.9 ^ 100 ≈ 2.7e-5
# The gradient from step 100 to step 1 is effectively zero.
```

LSTM'ler bunu sadece toplamsal etkileşimlerle (additive interactions) çalışan bir **hücre durumu (cell state)** ile çözer (unutma kapısı bunu çarpımsal olarak ölçeklendirir, ama gradyanlar "otoban" boyunca akar). GRU benzer bir şeyi daha az parametre ile yapar. Her ikisi de 100+ adım uzunluğundaki dizilerde kararlı eğitim sağlar.

### Adım 4: neden bu hâlâ yeterli değildi

LSTM'lerle bile üç sorun devam etti.

1. **Sıralı darboğaz (Sequential bottleneck).** 1000 uzunluğunda bir dizi üzerinde RNN eğitmek 1000 seri ileri/geri adım gerektirir. Zaman boyunca paralelleştirilemez.
2. **Kodlayıcı-Kod çözücü (encoder-decoder) kurulumlarında sabit boyutlu bağlam vektörü.** Kod çözücü (decoder), kodlayıcının (encoder) yalnızca son gizli durumunu görür ve bu tüm giriş üzerine sıkıştırılmıştır. Uzun girişler ayrıntı kaybeder. Ders 09 bunu doğrudan ele alır.
3. **Uzak bağımlılık doğruluk tavanı.** LSTM'ler düz RNN'lerden daha iyi performans gösterir ama 200+ adım boyunca belirli bilgiyi iletmekte hâlâ zorlanır.

Attention hepsini çözdü. Transformer'lar özyinelemeyi tamamen bıraktı. Ders 10 dönüm noktasıdır.

## Kullan

PyTorch'un `nn.LSTM`, `nn.GRU` ve `nn.Conv1d` modülleri üretim kalitesindedir. Eğitim kodu standarttır.

Hugging Face, giriş katmanı olarak taktığınız önceden eğitilmiş gömmeleri sunar:

```python
from transformers import AutoModel

encoder = AutoModel.from_pretrained("bert-base-uncased")
for param in encoder.parameters():
    param.requires_grad = False


class BertCNN(nn.Module):
    def __init__(self, n_classes, filter_widths=(2, 3, 4), n_filters=64):
        super().__init__()
        self.encoder = encoder
        self.convs = nn.ModuleList([nn.Conv1d(768, n_filters, kernel_size=k) for k in filter_widths])
        self.fc = nn.Linear(n_filters * len(filter_widths), n_classes)

    def forward(self, input_ids, attention_mask):
        with torch.no_grad():
            out = self.encoder(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        x = out.transpose(1, 2)
        pooled = [F.max_pool1d(F.relu(conv(x)), kernel_size=conv(x).size(2)).squeeze(2) for conv in self.convs]
        return self.fc(torch.cat(pooled, dim=1))
```

Kısıtlamalara uygun olduğunda kullan kontrol listesi.

- **Edge / cihaz üzerinde çıkarım (Edge / on-device inference).** GloVe gömmeleri ile TextCNN, bir transformer'dan 10-100 kat daha küçüktür. Dağıtım hedefiniz bir telefonsa, işte bu teknoloji yığınıdır.
- **Akışlı / çevrimiçi sınıflandırma.** RNN token'ları tek tek işler; transformer'lar tüm diziyi gerektirir. Gerçek zamanlı gelen metin için LSTM'ler hâlâ kazanır.
- **Temel çizgi için küçük modeller.** Yeni bir görevde hızlı döngü. CPU'da 5 dakikada bir TextCNN eğitin.
- **Sınırlı veri ile dizi etiketleme.** BiLSTM-CRF (ders 06) 1k-10k etiketli cümle için hâlâ üretim kalitesinde bir NER mimarisidir.

Geri kalan her şey bir transformer'a gider.

## Ürün Haline Getir

`outputs/prompt-text-encoder-picker.md` olarak kaydedin:

```markdown
---
name: text-encoder-picker
description: Pick a text encoder architecture for a given constraint set.
phase: 5
lesson: 08
---

Given constraints (task, data volume, latency budget, deploy target, compute budget), output:

1. Encoder architecture: TextCNN, BiLSTM, BiLSTM-CRF, transformer fine-tune, or "use a pretrained transformer as a frozen encoder + small head".
2. Embedding input: random init, GloVe / fastText frozen, or contextualized transformer embeddings.
3. Training recipe in 5 lines: optimizer, learning rate, batch size, epochs, regularization.
4. One monitoring signal. For RNN/CNN models: attention mechanism absence means they miss long-range deps; check per-length accuracy. For transformers: fine-tuning collapse if LR too high; check train loss.

Refuse to recommend fine-tuning a transformer when data is under ~500 labeled examples without showing that a TextCNN / BiLSTM baseline has plateaued. Flag edge deployment as needing architecture-before-everything.
```

## Alıştırmalar

1. **Kolay.** 3 sınıflı bir oyuncak veri seti (verileri siz oluşturun) üzerinde bir TextCNN eğitin. Filtre genişliklerinin (2, 3, 4) ortalama F1'de tek bir genişlikten (3) daha iyi performans gösterdiğini doğrulayın.
2. **Orta.** LSTM sınıflandırıcısı için maks havuzlama, ortalama havuzlama ve son durum havuzlamasını uygulayın. Küçük bir veri seti üzerinde karşılaştırın; hangi havuzlamanın kazandığını belgeleyin ve neden olduğunu hipotezleyin.
3. **Zor.** Bir BiLSTM-CRF NER etiketleyicisi inşa edin (ders 06 ve bunu birleştirin). CoNLL-2003 üzerinde eğitin. Ders 06'daki tek CRF temel çizgisi ve bir BERT ince ayarı (fine-tune) ile karşılaştırın. Eğitim süresi, bellek ve F1'i bildirin.

## Anahtar Terimler

| Terim | İnsanlar ne söyler | Aslında ne anlama gelir |
|-------|-------------------|------------------------|
| TextCNN | Metin için CNN | Kelime gömmeleri üzerinde 1D evrişimler yığını ile genel maks havuzlama. Kim (2014). |
| RNN | Özyinelemeli ağ | Her zaman adımında güncellenen gizli durum: `h_t = f(W x_t + U h_{t-1})`. |
| LSTM | Kapılı RNN | Giriş / unutma / çıkış kapıları + hücre durumu ekler. Uzun dizilerde kararlı eğitim. |
| GRU | Basitleştirilmiş LSTM | Üç yerine iki kapı. Benzer doğruluk, daha az parametre. |
| İkili yönlü (Bidirectional) | Her iki yön | İleriye + geriye RNN birleştirilir. Her token bağlamının her iki tarafını görür. |
| Kaybolan gradyan (Vanishing gradient) | Eğitim sinyali ölür | Düz RNN'lerde <1 ağırlıklarla tekrarlanan çarpım, erken adım gradyanlarını etkin olarak sıfır yapar. |

## İleri Okuma

- [Kim, Y. (2014). Convolutional Neural Networks for Sentence Classification](https://arxiv.org/abs/1408.5882) — TextCNN makalesi. Sekiz sayfa. Okunabilir.
- [Hochreiter, S. ve Schmidhuber, J. (1997). Long Short-Term Memory](https://www.bioinf.jku.at/publications/older/2604.pdf) — LSTM makalesi. Beklenmedik derecede net.
- [Olah, C. (2015). Understanding LSTM Networks](https://colah.github.io/posts/2015-08-Understanding-LSTMs/) — LSTM'leri herkes için erişilebilir kılan diyagramlar.
