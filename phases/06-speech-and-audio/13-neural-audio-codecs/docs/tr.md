# Nöral Ses Codec'leri — EnCodec, SNAC, Mimi, DAC ve Anlamsal-Akustik Bölünme

> 2026 ses üretimi neredeyse tamamen token'lardır. EnCodec, SNAC, Mimi ve DAC sürekli dalga formlarını bir transformerin tahmin edebileceği ayrık dizilere dönüştürür. Anlamsal ve akustik token bölünmesi — birinci kod kitabının (codebook) anlamsal, geri kalanının akustik olması — Transformer'dan bu yana ses için en önemli mimari kaymadır.

**Tür:** Öğren
**Diller:** Python
**Ön koşullar:** Faz 6 · 02 (Spektrogramlar), Faz 10 · 11 (Mikteleme), Faz 5 · 19 (Alt Sözcük Tokenizasyonu)
**Süre:** ~60 dakika

## Problem

Dil modelleri ayrık token'larla çalışır. Ses süreklidir. Konuşma / müzik için LLM tarzı bir model istiyorsanız — MusicGen, Moshi, Sesame CSM, VibeVoice, Orpheus — önce bir **nöral ses codec'ine** (neural audio codec) ihtiyacınız vardır: sesi küçük bir sözlükteki token'lara diskretize eden öğrenilmiş bir kodlayıcı ve dalga formunu yeniden oluşturan eşlik eden bir çözümleyici.

İki aile ortaya çıktı:

1. **Yeniden oluşturma öncelikli codec'ler** — EnCodec, DAC. Algısal ses kalitesini optimize eder. Token'lar "akustiktir" — konuşmacı kimliğini, tınıyı, arka plan gürültüsünü de dahil olmak üzere her şeyi yakalar.
2. **Anlamsal öncelikli codec'ler** — Mimi (Kyutai), SpeechTokenizer. Birinci kod kitabının dilbilgisel / fonetik içeriği (genellikle WavLM'den damıtma yoluyla) kodlamasını zorlar. Sonraki kod kitapları akustik ayrıntılardır.

2024-2026 içgörüsü: **saf yeniden oluşturma codec'i, metinden üretmeye çalıştığınızda bulanık bir konuşma verir.** Codec token'ları üzerindeki LLM'in aynı sözlükte hem dil yapısını hem de akustik yapısı öğrenmesi gerekir, bu ölçeklenmez. Bunları ayırmak — anlamsal kod kitabı 0, akustik kod kitapları 1-N — Moshi ve Sesame CSM'yi çalıştıran şeydir.

## Kavram

![Dört codec manzarası: EnCodec, DAC, SNAC (çoklu ölçek), Mimi (anlamsal+akustik)](../assets/codec-comparison.svg)

### Temel numara: Artıklıklı Vektör Miktelmesi (RVQ)

Büyük bir kod kitabı yerine (iyi kalite için milyonlarca kod gerektirir), tüm modern ses codec'leri **RVQ** kullanır: küçük kod kitaplarının bir kaskadı. Birinci kod kitabı kodlayıcı çıktısını mikler; ikincisi artığı (residual) mikler; vb. Her kod kitabı 1024 koddur. 8 kod kitabı = 1024^8 = 10^24 etkili sözlük.

Çıkarımda, çözümleyici her kare için seçilen tüm kodları toplar ve yeniden oluşturur.

### 2026'da önemli dört codec

**EnCodec (Meta, 2022).** Referans. Dalga formu üzerinde kodlayıcı-çözümleyici, RVQ darboğazı. 24 kHz, 32 kod kitabı mümkün, varsayılan 4 kod kitabı @ 1.5 kbps. `1D konvolüsyon + transformer + 1D konvolüsyon` mimarisi kullanır. MusicGen tarafından kullanılır.

**DAC (Descript, 2023).** L2-normalize kod kitapları, periyodik aktivasyon fonksiyonları, iyileştirilmiş kayıplarla RVQ. Herhangi bir açık codec'in en yüksek yeniden oluşturma doğruluğu — 12 kod kitabıyla orijinal konuşmadan bazen ayırt edilemez. 44.1 kHz tam bant.

**SNAC (Hubert Siuzdak, 2024).** Çoklu ölçekli RVQ — kaba kod kitapları ince olanlardan daha düşük kare hızında çalışır. Sesi hiyerarşik olarak modeller: ~12 Hz'de kaba bir "eskiz" artı 50 Hz'de ayrıntı. Orpheus-3B tarafından kullanılır çünkü hiyerarşik yapı LM tabanlı üretime iyi eşlenir.

**Mimi (Kyutai, 2024).** 2026 oyun değiştirici. 12.5 Hz kare hızı (son derece düşük), 8 kod kitabı @ 4.4 kbps. Kod kitabı 0, **WavLM'den damıtılmıştır** — WavLM'nin konuşma-içerik özelliklerini tahmin etmesi için eğitilir. Kod kitapları 1-7 artıklık akustiklerdir. Bu bölünme Moshi'yi (Ders 15) ve Sesame CSM'yi besler.

### Kare hızları dil modelleme için önemlidir

Daha düşük kare hızı = daha kısa dizi = daha hızlı LM.

| Codec | Kare hızı | 1 s = N kare | İyi olduğu alan |
|-------|-----------|--------------|----------------|
| EnCodec-24k | 75 Hz | 75 | müzik, genel ses |
| DAC-44.1k | 86 Hz | 86 | yüksek doğruluklu müzik |
| SNAC-24k (kaba) | ~12 Hz | 12 | AR-LM verimli |
| Mimi | 12.5 Hz | 12.5 | akışlı konuşma |

12.5 Hz'de 10 saniyelik bir ifade yalnızca 125 codec karesidir — bir transformercı kolayca tahmin edebilir.

### Anlamsal vs akustik token'lar

```
kare_t → [anlamsal_token_t, akustik_token_0_t, akustik_token_1_t, ..., akustik_token_6_t]
```

- **Anlamsal token (Mimi'de kod kitabı 0).** Ne söylendiğini kodlar — fonemler, kelimeler, içerik. WavLM'den yardımcı öngörü kaybı (auxiliary prediction loss) ile damıtılır.
- **Akustik token'lar (kitapları 1-7).** Tını, konuşmacı kimliği, prosodi, arka plan gürültüsü, ince ayrıntıları kodlar.

Bir AR LM önce anlamsal token'ı (metinle koşullandırarak) tahmin eder, sonra akustik token'ları (anlamsal + konuşmacı referansıyla koşullandırarak) tahmin eder. Bu ayrıştırma, modern TTS'nin neden zero-shot ses klonlayabildiğinin nedenidir: anlamsal model içeriği, akustik model tınıyı yönetir.

### 2026 yeniden oluşturma kalitesi (bit/saniye, daha düşük bit hızı daha iyidir)

| Codec | Bit hızı | PESQ | ViSQOL |
|-------|---------|------|--------|
| Opus-20kbps | 20 kbps | 4.0 | 4.3 |
| EnCodec-6kbps | 6 kbps | 3.2 | 3.8 |
| DAC-6kbps | 6 kbps | 3.5 | 4.0 |
| SNAC-3kbps | 3 kbps | 3.3 | 3.8 |
| Mimi-4.4kbps | 4.4 kbps | 3.1 | 3.7 |

Opus gibi geleneksel codec'ler bit başına algısal kalitede hala kazanır. Nöral codec'ler **ayrık token'lar** (Opus bunu üretmez) ve **üretici model kalitesi** (LM bu token'larla ne yapabilir) konusunda kazanır.

## İnşa Et

### Adım 1: EnCodec ile kodlama

```python
from encodec import EncodecModel
import torch

model = EncodecModel.encodec_model_24khz()
model.set_target_bandwidth(6.0)  # kbps

wav = torch.randn(1, 1, 24000)
with torch.no_grad():
    encoded = model.encode(wav)
codes, scale = encoded[0]
# codes: (1, n_codebooks, n_frames), dtype=int64
```

#### Açıklama
6 kbps'de `n_codebooks=8`. Her kod 0-1023 (10-bit) arasındadır.

### Adım 2: çözümleme ve yeniden oluşturma ölçümü

```python
with torch.no_grad():
    wav_recon = model.decode([(codes, scale)])

from torchaudio.functional import compute_deltas
import torch.nn.functional as F

mse = F.mse_loss(wav_recon[:, :, :wav.shape[-1]], wav).item()
```

#### Açıklama
Kodlanmış sesi çözümleyerek orijinal ile ortalama karesel hata (MSE) hesaplar.

### Adım 3: anlamsal-akustik bölünme (Mimi tarzı)

```python
from moshi.models import loaders
mimi = loaders.get_mimi()

with torch.no_grad():
    codes = mimi.encode(wav)  # boyut (1, 8, kareler@12.5Hz)

anlamsal = codes[:, 0]
akustik = codes[:, 1:]
```

#### Açıklama
Anlamsal kod kitabı 0, WavLM ile hizalanmıştır. Doğrudan sese gitmeye kıyasla çok daha küçük sözlükle bir metinden-anlamsala transformer eğitebilirsiniz. Sonra ayrı bir akustikten-dalga formuna çözümleyici konuşmacı referansıyla koşullandırılır.

### Adım 4: codec token'ları üzerinde neden AR LM çalışır

Mimi'nin 12.5 Hz × 8 kod kitabıyla 10 saniyelik bir konuşma klibi için:

```
N_token = 10 * 12.5 * 8 = 1000 token
```

1000 token bir transformercı için önemsiz bir bağlam (context)'tır. 256M parametreli bir transformer modern GPU'da milisaniyeler içinde 10 saniye üretebilir.

## Kullan

Sorunu codec'e eşleyin:

| Görev | Codec |
|-------|-------|
| Genel müzik üretimi | EnCodec-24k |
| En yüksek doğrulukta yeniden oluşturma | DAC-44.1k |
| Üzerinde AR LM olan konuşma (TTS) | SNAC veya Mimi |
| Akışlı tam çift taraflı konuşma | Mimi (12.5 Hz) |
| Metin ile ses efekti kütüphanesi | EnCodec + T5 koşullandırma |
| İncelikli ses düzenleme | DAC + boyama |

Genel kural: **bir üretici model inşa ediyorsanız Mimi veya SNAC ile başlayın. Bir sıkıştırma hattı inşa ediyorsanız Opus kullanın.**

## Tuzaklar

- **Çok fazla kod kitabı.** Kod kitabı eklemek doğruluğu doğrusal olarak artırır ama LM dizi uzunluğunu da doğrusal olarak artırır. 8-12'de durun.
- **Kare hızı uyumsuzluğu.** LM'yi 12.5 Hz Mimi üzerinde eğitip 50 Hz EnCodec üzerinde ince ayar yapmak sessizce başarısız olur.
- **Tüm kod kitaplarını eşit varsayma.** Mimi'de kod kitabı 0 içeriği taşır; kaybetmek anlaşılırlığı yok eder. Kod kitabı 7'yi kaybetmek zor fark edilir.
- **Yeniden oluşturma kalitesini tek metrik olarak kullanma.** Bir codec harika yeniden oluşturmaya sahip olabilir ama anlamsal yapı kötüyse LM tabanlı üretim için işe yaramaz olabilir.

## Gönder

`outputs/skill-codec-picker.md` olarak kaydedin. Verilen bir üretici veya sıkıştırma görevi için bir codec seçin.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Oyuncak bir skaler + artıklıklı miktar (quantizer) uygular ve kod kitabı ekledikçe yeniden oluşturma hatasını ölçer.
2. **Orta.** `encodec`'i kurun ve 1, 4, 8, 32 kod kitabını ayrılmış bir konuşma klibi üzerinde karşılaştırın. PESQ veya MSE'yi bit hızına göre çizin.
3. **Zor.** Mimi'yi yükleyin. Bir klibi kodlayın. Kod kitabı 0'ı rastgele tamsayılarla değiştirin; çözümleyin. Sonra kod kitabı 7'yi benzer şekilde değiştirin. İki bozulmayı karşılaştırın — kod kitabı 0 bozulması anlaşılırlığı yok etmelidir; kod kitabı 7 bozulması neredeyse hiçbir şeyi değiştirmemelidir.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|---------------------|------------------------|
| RVQ | Artıklıklı mikteleme | Küçük kod kitaplarının kaskadı; her biri bir öncekinin artığını mikler. |
| Kare hızı | Codec hızı | Saniye başına kaç token-karesi. Düşük = daha hızlı LM. |
| Anlamsal kod kitabı | Kod kitabı 0 (Mimi) | SSL özelliklerinden damıtılmış kod kitabı; içeriği kodlar. |
| Akustik kod kitapları | Geri kalan her şey | Tını, prosodi, gürültü, ince ayrıntı. |
| PESQ / ViSQOL | Algısal kalite | MOS ile ilişkili nesnel metrikler. |
| EnCodec | Meta codec'i | RVQ referansı; MusicGen tarafından kullanılır. |
| Mimi | Kyutai codec'i | 12.5 Hz kare hızı; anlamsal-akustik bölünme; Moshi'yi besler. |

## İleri Okuma

- [Défossez et al. (2023). EnCodec](https://arxiv.org/abs/2210.13438) — RVQ referansı.
- [Kumar et al. (2023). Descript Audio Codec (DAC)](https://arxiv.org/abs/2306.06546) — en yüksek doğruluklu açık kaynak.
- [Siuzdak (2024). SNAC](https://arxiv.org/abs/2410.14411) — çoklu ölçekli RVQ.
- [Kyutai (2024). Mimi codec'i](https://kyutai.org/codec-explainer) — anlamsal-akustik bölünme, WavLM damıtması.
- [Borsos et al. (2023). AudioLM](https://arxiv.org/abs/2209.03143) — iki aşamalı anlamsal/akustik paradigması.
- [Zeghidour et al. (2021). SoundStream](https://arxiv.org/abs/2107.03312) — orijinal akışlı RVQ codec'i.
