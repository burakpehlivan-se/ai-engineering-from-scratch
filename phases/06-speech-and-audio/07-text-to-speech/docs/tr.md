# Metinden Konuşmaya (TTS) — Tacotron'dan F5 ve Kokoro'ya

> ASR konuşmayı metne dönüştürür; TTS metni konuşmaya dönüştürür. 2026 yığını üç parçadan oluşur: metin → token'lar, token'lar → mel, mel → dalga formu. Her parçanın dizüstü bilgisayara sığan bir varsayılan modeli vardır.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 6 · 02 (Spektrogramlar & Mel), Faz 5 · 09 (Seq2Seq), Faz 7 · 05 (Tam Transformer)
**Süre:** ~75 dakika

## Problem

Bir dizeniz var: "Lütfen beni saat 18:00'de bitkileri sulamam için hatırlat." Doğal sesli, doğru prosodili (duraklamalar, vurgular), "bitkiler" kelimesini doğru sesli harfle telaffuz eden ve canlı bir ses asistanı için CPU'da 300 ms altında çalışan 3 saniyelik bir ses klibine ihtiyacınız var. Ayrıca sesleri değiştirmeniz, kod değiştirme girişimlerini ("daijoubu mu saat 18:00'de hatırlat?") ve isimlerde utangaçlık yaşamamanız gerekiyor.

Modern TTS hatları (pipeline) şu şekildedir:

1. **Metin ön yüzü.** Metni normalize edin (tarihler, sayılar, e-postalar), fonemlere veya alt sözcük token'larına dönüştürün, prosodi özelliklerini tahmin edin.
2. **Akustik model.** Metin → mel spektrogramı. Tacotron 2 (2017), FastSpeech 2 (2020), VITS (2021), F5-TTS (2024), Kokoro (2024).
3. **Vokoder.** Mel → dalga formu. WaveNet (2016), WaveRNN, HiFi-GAN (2020), BigVGAN (2022), 2024+ nöral codec vokoderleri.

2026'da akustik + vokoder ayrımı uçtan uca (end-to-end) difüzyon ve akış eşleştirme (flow-matching) modelleriyle bulanıklaşıyor. Ancak üç parça zihinsel modeli hata ayıklama için hala geçerlidir.

## Kavram

![Tacotron, FastSpeech, VITS, F5/Kokoro yan yana](../assets/tts.svg)

**Tacotron 2 (2017).** Seq2seq: karakter gömme → BiLSTM kodlayıcı → konum duyarlı dikkat (location-sensitive attention) → otoregresif LSTM çözümleyici mel kareleri üretir. Yavaş (AR), uzun metinde dalgalanır. Hala referans olarak atıfta bulunulur.

**FastSpeech 2 (2020).** Otoregresif olmayan. Süre tahmincisi her foneme kaç mel karesi düştüğünü çıktı olarak verir. 1 geçiş, Tacotron'dan 10× daha hızlı. Bazı doğallıktan kaybeder (monoton hizalama) ama her yerde kullanılır.

**VITS (2021).** Kodlayıcı + akış tabanlı süre + HiFi-GAN vokoderini birlikte eğitir, uçtan uca değişken çıkarımlı (variational inference) ile. Yüksek kalite, tek model. 2022–2024 arası baskın açık kaynak TTS. Varyantlar: YourTTS (çok konuşmacılı zero-shot), XTTS v2 (2024, Coqui).

**F5-TTS (2024).** Akış eşleştirmeli difüzyon transformeri (diffusion transformer). Doğal prosodi, 5 saniyelik referans sesle zero-shot ses klonlama. 2026 açık kaynak TTS liderlik tablolarında üst sıralarda. 335M parametre.

**Kokoro (2024).** Küçük (82M), CPU'da çalışabilir, gerçek zamanlı kullanım için en iyi İngilizce TTS. Kapalı sözlük, yalnızca İngilizce, Apache-2.0.

**OpenAI TTS-1-HD, ElevenLabs v2.5, Google Chirp-3.** Ticari en iyi durum. ElevenLabs v2.5 duygu etiketleri ("[whispered]", "[laughing]") ve karakter sesleri 2026'da sesli kitap yapımını domine ediyor.

### Vokoder evrimi

| Dönem | Vokoder | Gecikme | Kalite |
|-------|---------|---------|--------|
| 2016 | WaveNet | yalnızca çevrimdışı | çıkışta SOTA |
| 2018 | WaveRNN | ~gerçek zamanlı | iyi |
| 2020 | HiFi-GAN | 100× gerçek zamanlı | insana yakın |
| 2022 | BigVGAN | 50× gerçek zamanlı | konuşmacılar/diller arası genelleme |
| 2024 | SNAC, DAC (nöral codec'ler) | AR modellerle entegre | ayrık token'lar, bit-verimli |

2026'ya kadar çoğu "TTS" modeli metinden dalga formuna kadar uçtan uca çalışır; mel spektrogramı dahili bir temsildir.

### Değerlendirme

- **MOS (Ortalama Görüş Puanı).** 1–5 ölçeği, kalabalık kaynaklı. Hala altın standart; acı verici kadar yavaş.
- **CMOS (Karşılaştırmalı MOS).** A-vs-B tercihi. Her notasyonda daha dar güven aralıkları.
- **UTMOS, DNSMOS.** Referanssız nöral MOS tahmincileri. Liderlik tabloları için kullanılır.
- **CER (Karakter Hata Oranı) ASR ile.** TTS çıktısını Whisper'dan geçirin, giriş metnine göre CER hesaplayın. Anlaşılabilirliğin vekil ölçüsü.
- **SECS (Konuşmacı Gömme Kosinüs Benzerliği).** Ses klonlama kalitesi.

LibriTTS test-clean'de 2026 sayıları:

| Model | UTMOS | CER (Whisper ile) | Boyut |
|-------|-------|-------------------|-------|
| Gerçek | 4.08 | %1.2 | — |
| F5-TTS | 3.95 | %2.1 | 335M |
| XTTS v2 | 3.81 | %3.5 | 470M |
| VITS | 3.62 | %3.1 | 25M |
| Kokoro v0.19 | 3.87 | %1.8 | 82M |
| Parler-TTS Large | 3.76 | %2.8 | 2.3B |

## İnşa Et

### Adım 1: girişin fonemlere dönüştürülmesi

```python
from phonemizer import phonemize
ph = phonemize("Hello world", language="en-us", backend="espeak")
# 'həloʊ wɜːld'
```

#### Açıklama
Fonemler (phoneme) evrensel köprüdür. VITS kalitesinin altındaki herhangi bir şeye ham metin beslemekten kaçının.

### Adım 2: Kokoro'yu çalıştırın (2026 CPU varsayılanı)

```python
from kokoro import KPipeline
tts = KPipeline(lang_code="a")  # "a" = Amerikan İngilizcesi
audio, sr = tts("Please remind me to water the plants at 6 pm.", voice="af_bella")
# audio: float32 tensor, sr=24000
```

#### Açıklama
Çevrimdışı çalışır, tek dosya, 82M parametre.

### Adım 3: F5-TTS ile ses klonlama

```python
from f5_tts.api import F5TTS
tts = F5TTS()
wav = tts.infer(
    ref_file="my_voice_5s.wav",
    ref_text="The quick brown fox jumps over the lazy dog.",
    gen_text="Please remind me to water the plants.",
)
```

#### Açıklama
5 saniyelik bir referans klibi + dökümünü geçirin; F5 prosodiyi ve tınıyı (timbre) klonlar.

### Adım 4: sıfırdan HiFi-GAN vokoderi

Bir eğitim betiğine sığacak kadar büyük değil, ama şekil şu:

```python
class HiFiGAN(nn.Module):
    def __init__(self, mel_channels=80, upsample_rates=[8, 8, 2, 2]):
        super().__init__()
        # 4 yukarı örnekleme bloğu, mel hızından ses hızına toplam 256×
        ...
    def forward(self, mel):
        return self.blocks(mel)  # -> dalga formu
```

#### Açıklama
Eğitim: rekabetçi (kısa pencerelerde ayrımcı) + mel spektrogramı yeniden oluşturma kaybı + özellik eşleştirme kaybı. Meta — `hifi-gan` deposundan veya nvidia-NeMo'dan önceden eğitilmiş denetim noktaları kullanın.

### Adım 5: tam hat (sözde kod)

```python
text = "Please remind me at 6 pm."
phones = phonemize(text)
mel = acoustic_model(phones, speaker=alice)      # [T, 80]
wav = vocoder(mel)                                # [T * 256]
soundfile.write("out.wav", wav, 24000)
```

#### Açıklama
Tam TTS hattı: fonemlere dönüştürme, akustik model, vokoder ve dosyaya yazma adımlarını birleştirir.

## Kullan

2026 yığını:

| Durum | Seçin |
|-------|-------|
| Gerçek zamanlı İngilizce ses asistanı | Kokoro (CPU) veya XTTS v2 (GPU) |
| 5 s referanstan ses klonlama | F5-TTS |
| Ticari karakter sesleri | ElevenLabs v2.5 |
| Sesli kitap anlatımı | ElevenLabs v2.5 veya XTTS v2 + ince ayar |
| Düşük kaynaklı dil | Hedef dilde 5–20 saat veriyle VITS eğitin |
| Duygusal / duygu etiketleri | ElevenLabs v2.5 veya StyleTTS 2 ince ayar |

2026 itibarıyla açık kaynak lideri: **kalite için F5-TTS, verimlilik için Kokoro**. Tarihçi değilseniz Tacotron'a uzanmayın.

## Tuzaklar

- **Metin normalleştiricisi yok.** "Dr. Smith" "Doktor" mu yoksa "Caddesi" mi okunur? "2026" "yirmi altı yüz yirmi altı" mı yoksa "iki sıfır iki sıfır altı" mı? Fonemizörden ÖNCE normalize edin.
- **OOV özel isimler.** "Ghumare" → "ghyu-mair"? Bilinmeyen token'lar için bir yedek grafemden-foneme modeli kullanın.
- **Kırpılma.** Vokoder çıktısı nadiren kırpar, ancak çıkarımda ölçek uyumsuzluğu ±1.0'nin üzerine çıkabilir. Her zaman `np.clip(wav, -1, 1)` kullanın.
- **Örnekleme hızı uyumsuzluğu.** Kokoro 24 kHz çıktı verir; aşağı akım hattınız 16 kHz bekliyorsa → yeniden örnekleme yapın veya tınlama (aliasing) alırsınız.

## Gönder

`outputs/skill-tts-designer.md` olarak kaydedin. Verilen bir ses, gecikme ve dil hedefi için bir TTS hattı tasarlayın.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Oyuncak bir sözlükten fonem sözlüğü oluşturur, her fonem için süreyi tahmin eder ve sahte bir "mel" zaman çizelgesi yazdırır.
2. **Orta.** Kokoro'yu kurun, aynı cümleyi `af_bella` ve `am_adam` sesleriyle sentezleyin. Ses sürelerini ve öznel kaliteyi karşılaştırın.
3. **Zor.** Kendinizin 5 saniyelik referans klibini kaydedin. F5-TTS ile klonlayın. Referans ve klonlanmış çıktı arasındaki SECS'yi raporlayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|---------------------|------------------------|
| Fonem | Ses birimi | Soyut ses sınıfı; İngilizce'de 39 (ARPABet). |
| Süre tahmincisi | Her fonemin ne kadar sürdüğü | Olmayan-AR model çıktısı; fonem başına tamsayı kareleri. |
| Vokoder | Mel → dalga formu | Mel-spec'i ham örneklere eşleyen sinir ağı. |
| HiFi-GAN | Standart vokoder | GAN tabanlı; 2020–2024 arası baskın. |
| MOS | Öznel kalite | İnsan oylayıcılardan 1–5 ortalama görüş puanı. |
| SECS | Ses klonlama metriği | Hedef ve çıktı konuşmacı gömmesi arasındaki kosinüs benzerliği. |
| F5-TTS | 2024 açık kaynak SOTA | Akış eşleştirmeli difüzyon; zero-shot klonlama. |
| Kokoro | CPU İngilizce lideri | 82M parametreli model, Apache 2.0. |

## İleri Okuma

- [Shen et al. (2017). Tacotron 2](https://arxiv.org/abs/1712.05884) — seq2seq referansı.
- [Kim, Kong, Son (2021). VITS](https://arxiv.org/abs/2106.06103) — uçtan uca akış tabanlı.
- [Chen et al. (2024). F5-TTS](https://arxiv.org/abs/2410.06885) — güncel açık kaynak SOTA.
- [Kong, Kim, Bae (2020). HiFi-GAN](https://arxiv.org/abs/2010.05646) — 2026'da hala kullanılan vokoder.
- [HuggingFace'de Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) — 2024 CPU-dostu İngilizce TTS.
