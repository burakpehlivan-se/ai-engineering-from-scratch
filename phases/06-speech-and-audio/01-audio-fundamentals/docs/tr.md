# Ses Temelleri — Dalga Şekilleri, Örnekleme, Fourier Dönüşümü

> Dalga şekilleri ham sinyaldir. Spektrogramlar temsildir. Mel özellikleri makine öğrenmesine uygun formudur. Her modern ASR ve TTS hattı bu merdiveni tırmanır ve ilk basamak örnekleme ve Fourier kavramını anlamaktır.

**Tür:** Öğrenme
**Diller:** Python
**Ön koşullar:** Faz 1 · 06 (Vektörler & Matrisler), Faz 1 · 14 (Olasılık Dağılımları)
**Süre:** ~45 dakika

## Problem

Bir mikrofon basınç-zaman sinyali üretir. Sinir ağınız tensörler tüketir. İkisinin arasında bir dizi kural vardır ve bunlar ihlal edildiğinde sessiz hatalar ortaya çıkar: model güzel eğitilir ama WER ikiye katlanır, ya da TTS bir cıslama sesi gönderir, ya da bir ses klonlama sistemi konuşmacı yerine mikrofonu ezberler.

Konuşma sistemlerindeki her hata üç sorundan birine geri döner:

1. Veri hangi sampling rate ile kaydedildi ve modelin beklentisi nedir?
2. Sinyal aliasing (örneklem hatalı) mi?
3. Ham örnekler üzerinde mi yoksa frekans temsili üzerinde mi çalışıyorsunuz?

Bunları doğru yaparsanız Faz 6'nın geri kalanı kolaylaşır. Yanlış yaparsanız Whisper-Large-v4 bile çöp üretir.

## Kavram

![Dalga şekli, örnekleme, DFT ve frekans bini görselleştirme](../assets/audio-fundamentals.svg)

**Dalga şekli.** `[-1.0, 1.0]` aralığında tek boyutlu bir float dizisi. Örnek numarasıyla indekslenir. Saniyeye çevirmek için sampling rate'e bölünür: `t = n / sr`. 16 kHz'de 10 saniyelik bir kesik 160.000 float'lık bir dizidir.

**Sampling rate (sr).** Saniyede kaç örnek. 2026'da yaygın hızlar:

| Hız | Kullanım |
|------|---------|
| 8 kHz | Telekomünikasyon, eski VOIP. Nyquist 4 kHz'te ünsüzleri öldürür. ASR için kaçının. |
| 16 kHz | ASR standardı. Whisper, Parakeet, SeamlessM4T v2 hepsi 16 kHz tüketir. |
| 22.05 kHz | Eski modeller için TTS vocoder eğitimi. |
| 24 kHz | Modern TTS (Kokoro, F5-TTS, xTTS v2). |
| 44.1 kHz | CD sesi, müzik. |
| 48 kHz | Film, profesyonel ses, yüksek sadakatli TTS (VALL-E 2, NaturalSpeech 3). |

**Nyquist-Shannon.** `sr` sampling rate'i `sr/2`'ye kadar olan frekansları açıkça temsil edebilir. `sr/2` sınırı *Nyquist frekansı*dır. Nyquist'in üzerindeki enerji *aliasing*'e uğrar — daha düşük frekanslara katlanır — ve sinyali bozar. Downsampling öncesi her zaman alçak geçiren filtre uygulayın.

**Bit derinliği.** 16-bit PCM (imzalı int16, aralık ±32,767) evrensel değişim formatıdır. Müzik için 24-bit, iç DSP için 32-bit float. `soundfile` gibi kütüphaneler int16 okur ama `[-1, 1]` aralığında float32 diziler sunar.

**Fourier Dönüşümü.** Herhangi bir sonlu sinyal, farklı frekanslardaki sinüzoidlerin toplamıdır. Ayrık Fourier Dönüşümü (DFT), `N` örnek için `N` karmaşık katsayı hesaplar — her frekans bin'i için bir tane. `bin k` frekansı `k · sr / N` Hz'e eşlenir. Genlik o frekanstaki genliktir, açı fazdır.

**FFT.** Hızlı Fourier Dönüşümü: `N` 2'nin kuvveti olduğunda DFT için `O(N log N)` algoritması. Her ses kütüphanesi arkada FFT kullanır. 16 kHz'de 1024 örneklik bir FFT, 0–8 kHz aralığında 15,6 Hz çözünürlükle 512 kullanılabilir frekans bin'i verir.

**Çerçeveleme + pencere.** Tüm bir klibi FFT yapmayız. Onu örtüşmeli *çerçevelere* (tipik olarak 25 ms pencere, 10 ms adım) böleriz, her çerçeveyi bir pencere fonksiyonuyla (Hann, Hamming) çarparak kenar süreksizliklerini yok ederiz, sonra her çerçeveyi FFT'ye sokarız. Bu Kısa Süreli Fourier Dönüşümü'dür (STFT). Ders 02 buradan devam eder.

## İnşa Et

### Adım 1: bir kesik oku ve dalga şekline grafik çiz

`code/main.py` bağımsız demonstration için yalnızca stdlib `wave` modülünü kullanır. Üretimde `soundfile` veya `torchaudio.load` kullanırsınız (her ikisi de `(dalga şekli, sr)` tuple'ı döndürür):

```python
import soundfile as sf
waveform, sr = sf.read("clip.wav", dtype="float32")  # shape (T,), sr=int
```

#### Açıklama
`sf.read` ses dosyasını float32 dizisi olarak okur ve sampling rate bilgisini döndürür.

### Adım 2: temel ilkelerden bir sinüs dalgası sentezle

```python
import math

def sine(freq_hz, sr, seconds, amp=0.5):
    n = int(sr * seconds)
    return [amp * math.sin(2 * math.pi * freq_hz * i / sr) for i in range(n)]
```

#### Açıklama
Verilen frekans ve sürede bir sinüs dalgası üretir. 440 Hz (konser la'sı) 16 kHz'de 1 saniye için 16.000 float üretir. `wave.open(..., "wb")` kullanarak 16-bit PCM kodlamasıyla yazılır.

### Adım 3: DFT'yi elle hesapla

```python
def dft(x):
    N = len(x)
    out = []
    for k in range(N):
        re = sum(x[n] * math.cos(-2 * math.pi * k * n / N) for n in range(N))
        im = sum(x[n] * math.sin(-2 * math.pi * k * n / N) for n in range(N))
        out.append((re, im))
    return out
```

#### Açıklama
`O(N²)` karmaşıklığa sahip temel DFT uygulaması. `N=256` için doğrulama yapmak yeterli, gerçek ses için yetersizdir. Gerçek kod `numpy.fft.rfft` veya `torch.fft.rfft` kullanır.

### Adım 4: baskın frekansı bul

Genlik tepe indeksi `k_star` frekansı `k_star * sr / N`'e eşlenir. 440 Hz sinüsünde bu çalıştırıldığında `440 * N / sr` bin'inde bir tepe döndürmelidir.

### Adım 5: aliasing'i göster

10 kHz'de (Nyquist = 5 kHz) 7 kHz sinüsü örnekleyin. 7 kHz tonu Nyquist'in üzerindedir ve `10 − 7 = 3 kHz`'e katlanır. FFT tepesi 3 kHz'te görünür. Bu klasik aliasing gösterimi ve her DAC/ADC'nin neden duvar tipi alçak geçiren filtre ile gönderildiğinin nedenidir.

## Kullan

2026'da gerçekten kullanacağınız yığın:

| Görev | Kütüphane | Neden |
|------|---------|-------|
| WAV/FLAC/OGG okuma/yazma | `soundfile` (libsndfile sarmalayıcı) | En hızlı, kararlı, float32 döndürür. |
| Yeniden örnekleme | `torchaudio.transforms.Resample` veya `librosa.resample` | Doğru anti-aliasing dahildir. |
| STFT / Mel | `torchaudio` veya `librosa` | GPU dostu; PyTorch ekosistemi. |
| Gerçek zamanlı streaming | `sounddevice` veya `pyaudio` | Çapraz platformlu PortAudio bağları. |
| Dosya inceleme | `ffprobe` veya `soxi` | CLI, hızlı, sr/kanal/kodek raporlar. |

Karar kuralı: **örneklem hızını her şeyden önce eşleştirin**. Whisper 16 kHz mono float32 bekler. 44.1 kHz stereo verirseniz model hatası gibi görünen çöp alırsınız.

## Gönder

`outputs/skill-audio-loader.md` olarak kaydedin. Bu beceri, ses girdisinin alt modelin beklentileriyle eşleştiğini ve eşleşmediğinde doğru şekilde yeniden örneklendiğini kontrol etmenize yardımcı olur.

## Alıştırmalar

1. **Kolay.** 16 kHz'de 1 saniyelik 220 Hz + 440 Hz + 880 Hz karışımı sentezleyin. DFT çalıştırın. Beklenen bin'lerde üç tepe doğrulayın.
2. **Orta.** 48 kHz'de sesinizin 3 saniyelik WAV'ını kaydedin. `torchaudio.transforms.Resample` ile (anti-aliasing ile) 16 kHz'e downsample edin, sonra her üçüncü örneği alarak naive decimation ile 16 kHz'e downsample edin. Her ikisini de FFT'ye sokun. Aliasing nerede görünür?
3. **Zor.** Yalnızca `math` ve Adım 3'teki DFT'yi kullanarak STFT'yi sıfırdan oluşturun. Çerçeve boyutu 400, adım 160, Hann penceresi. `matplotlib.pyplot.imshow` ile genlikleri çizin. Bu Ders 02'nin spektrogramıdır.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|---------------------|------------------------|
| Sampling rate | Saniyede kaç örnek | ADC'nin sinyali ölçdüğü frekans (Hz cinsinden). |
| Nyquist | Temsil edilebilecek maksimum frekans | `sr/2`; üzerindeki enerji aşağıya Alias eder. |
| Bit derinliği | Her örneğin çözünürlüğü | `int16` = 65.536 seviye; `float32` = `[-1, 1]`'de 24-bit hassasiyet. |
| DFT | Diziler için Fourier dönüşümü | `N` örnek → `N` karmaşık frekans katsayısı. |
| FFT | Hızlı DFT | `N` = 2'nin kuvveti gerektiren `O(N log N)` algoritması. |
| Bin | Frekans sütunu | `k · sr / N` Hz; çözünürlük = `sr / N`. |
| STFT | Spektrogramın arkasındaki yapı | Zaman üzerinde çerçevelenmiş + pencerelenmiş FFT. |
| Aliasing | Garip frekans hayaletleri | Nyquist'in üzerindeki enerjinin alt bin'lere ayna gibi yansıması. |

## İleri Okuma

- [Shannon (1949). Communication in the Presence of Noise](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf) — Örnekleme teoreminin arkasındaki makale.
- [Smith — The Scientist and Engineer's Guide to Digital Signal Processing](https://www.dspguide.com/ch8.htm) — Ücretsiz, kanonik DSP ders kitabı.
- [librosa docs — audio primer](https://librosa.org/doc/latest/tutorial.html) — Kodla uygulamalı pratik yol gösterici.
- [Heinrich Kuttruff — Room Acoustics (6th ed.)](https://www.routledge.com/Room-Acoustics/Kuttruff/p/book/9781482260434) — Gerçek dünyadaki sesin neden temiz bir sinüzoid olmadığının referansı.
- [Steve Eddins — FFT Interpretation notebook](https://blogs.mathworks.com/steve/2020/03/30/fft-spectrum-and-spectral-densities/) — Frekans bin sezgisi 10 dakikada açıklığa kavuşur.
