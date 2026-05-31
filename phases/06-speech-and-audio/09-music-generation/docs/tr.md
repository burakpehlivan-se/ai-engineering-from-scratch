# Müzik Üretimi — MusicGen, Stable Audio, Suno ve Lisans Depreminde

> 2026 müzik üretimi: Suno v5 ve Udio v4 ticari alanda baskın; MusicGen, Stable Audio Open ve ACE-Step açık kaynakta öncü. Teknik problem büyük ölçüde çözüldü. Hukuki problem (Warner Music 500M dolar uzlaşma, UMG uzlaşma) alanı 2025-2026'da yeniden şekillendirdi.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 6 · 02 (Spektrogramlar), Faz 4 · 10 (Difüzyon Modelleri)
**Süre:** ~75 dakika

## Problem

Metin → 30 saniyeden 4 dakikaya kadar müzik klibi, sözler, vokaller ve yapı. Üç alt problem:

1. **Enstrümantal üretim.** "Lo-fi hip-hop davulları ve sıcak tuşlar" gibi metin → ses. MusicGen, Stable Audio, AudioLDM.
2. **Şarkı üretimi (vokaller + sözlerle).** "Yağmurlu Teksas geceleri hakkında bir country şarkısı" → tam şarkı. Suno, Udio, YuE, ACE-Step.
3. **Koşullu / kontrollü.** Mevcut klibi uzatma, köprüyü yeniden üretme, türü değiştirme, dal ayırma (stem separation) veya boyama (inpainting). Udio'nun boyama + dal ayırması 2026'da eşleşmesi gereken özelliktir.

## Kavram

![Müzik üretimi: token-LM vs difüzyon, 2026 model haritası](../assets/music-generation.svg)

### Nöral codec token'ları üzerinde Token LM

Meta'nın **MusicGen**'i (2023, MIT) ve birçok türevi: metin/melodi gömmeleriyle koşullandırma, otoregresif olarak EnCodec token'larını (32 kHz, 4 kod kitabı) tahmin etme, EnCodec ile çözümleme. 300M - 3.3B parametre. Güçlü referans; 30 saniyenin ötesinde zorlanır.

**ACE-Step** (açık kaynak, Nisan 2026'da yayınlanmış 4B XL), tam şarkı söz koşullu üretim için bunu genişletir. Açık topluluğun Suno'ya en yakın karşılığı.

### Mel'ler veya gizli üzerlerde difüzyon

**Stable Audio (2023)** ve **Stable Audio Open (2024)**: sıkıştırılmış ses üzerinde gizli difüzyon (latent diffusion). Döngülerde, ses tasarımında, ortam dokularında (ambient) başarılı. Tam yapılandırılmış şarkılarda iyi değil.

**AudioLDM / AudioLDM2**: T2I tarzı gizli difüzyon aracılığıyla metinden sese, müziğe, ses efektlerine, konuşmaya genelleştirilmiş.

### Hibrit (üretim) — Suno, Udio, Lyria

Kapalı ağırlıklar. Büyük olasılıkla AR codec LM + difüzyon tabanlı vokoder, özel vokal/davul/melodi kafalarıyla. Suno v5 (2026) ELO 1293 kalite lideri. Udio v4 boyama + dal ayırma ekler (bas, davul, vokaller ayrı indirme).

### Değerlendirme

- **FAD (Fréchet Ses Mesafesi).** VGGish veya PANNs özellikleri kullanarak gerçek ile üretilen ses dağılımı arasındaki gömme düzeyinde mesafe. Düşük daha iyi. MusicGen küçük: MusicCaps'te 4.5 FAD; SOTA ~3.0.
- **Müziksellik (öznel).** İnsan tercihi. Suno v5 ELO 1293 lider.
- **Metin-ses uyumu.** Çıktı ile istem arasındaki CLAP puanı.
- **Müziksellik hataları.** Ritim dışı geçişler, vokal ifade kayması, 30 saniye sonrası yapı kaybı.

## 2026 model haritası

| Model | Parametre | Süre | Vokaller | Lisans |
|-------|-----------|------|----------|--------|
| MusicGen-large | 3.3B | 30 s | hayır | MIT |
| Stable Audio Open | 1.2B | 47 s | hayır | Stability ticari olmayan |
| ACE-Step XL (Nis 2026) | 4B | > 2 dk | evet | Apache-2.0 |
| YuE | 7B | > 2 dk | evet, çok dilli | Apache-2.0 |
| Suno v5 (kapalı) | ? | 4 dk | evet, ELO 1293 | ticari |
| Udio v4 (kapalı) | ? | 4 dk | evet + dallar | ticari |
| Google Lyria 3 (kapalı) | ? | gerçek zamanlı | evet | ticari |
| MiniMax Music 2.5 | ? | 4 dk | evet | ticari API |

## Hukuki manzara (2025-2026)

- **Warner Music vs Suno uzlaşması.** 500M dolar. WMG artık Suno'daki yapay zeka benzerliği, müzik hakları ve kullanıcı tarafından oluşturulan parçalar üzerinde denetim sahibi. Udio'da benzer UMG uzlaşması.
- **AB Yapay Zeka Yasası** + **Kaliforniya SB 942**: Yapay zeka tarafından üretilen müziğin beyan edilmesi gerekir.
- **Riffusion / MusicGen** MIT kapsamında uyum yükümlülüğü yok ama ticari vokaller de yok.

Göndermek için güvenli modeller:

1. Yalnızca enstrümantal üretin (MusicGen, Stable Audio Open, MIT/CC0 çıktıları).
2. Üretim başına lisansla ticari API'ler kullanın (Suno, Udio, ElevenLabs Music).
3. Sahip olunan veya lisanslı katalogda eğitin (çoğu işletme buraya ulaşır).
4. Üretimleri filigranlar + meta veriler ile etiketleyin.

## İnşa Et

### Adım 1: MusicGen ile üretim

```python
from audiocraft.models import MusicGen
import torchaudio

model = MusicGen.get_pretrained("facebook/musicgen-small")
model.set_generation_params(duration=10)
wav = model.generate(["upbeat synthwave with driving drums, 128 BPM"])
torchaudio.save("out.wav", wav[0].cpu(), 32000)
```

#### Açıklama
Üç boyut: `small` (300M, hızlı), `medium` (1.5B), `large` (3.3B). Küçük "fikir işe yarıyor mu" sorusu için yeterlidir.

### Adım 2: melodi koşullandırması

```python
melody, sr = torchaudio.load("humming.wav")
wav = model.generate_with_chroma(
    ["jazz piano cover"],
    melody.squeeze(),
    sr,
)
```

#### Açıklama
MusicGen-melody bir kromagram (chromagram) alır ve tınıyı değiştirirken melodiyi korur. "Bu melodieyi bir yaylı çalgı dörtlüsü olarak ver" gibi kullanışlıdır.

### Adım 3: FAD değerlendirmesi

```python
from frechet_audio_distance import FrechetAudioDistance
fad = FrechetAudioDistance()

fad.get_fad_score("generated_folder/", "reference_folder/")
```

#### Açıklama
VGGish-gömme mesafesi hesaplar. Tür düzeyinde regresyon testleri için kullanışlıdır; insan dinleyicilerin yerini tutmaz.

### Adım 4: LLM-müzik iş akışına ekleme

Dersler 7-8'deki fikirlerle birleştirin:

```python
prompt = "Write a 30-second jazz loop. Describe the drums, bass, and piano voicing."
description = llm.complete(prompt)
music = musicgen.generate([description], duration=30)
```

#### Açıklama
LLM ile müzik üretimi arasında köprü kurarak istemden açıklamaya, açıklamadan müziğe dönüşüm sağlar.

## Kullan

| Hedef | Yığın |
|-------|-------|
| Enstrümantal ses tasarımı | Stable Audio Open |
| Oyun / uyarlanabilir müzik | Google Lyria RealTime (kapalı) |
| Vokalli tam şarkılar (ticari) | Suno v5 veya Udio v4, açık lisansla |
| Vokalli tam şarkılar (açık) | ACE-Step XL veya YuE |
| Kısa reklam jingle'ı | MusicGen, hummalı referansla melodi koşullu |
| Müzik videosu arka planı | MusicGen + Stable Video Diffusion |

## 2026'da hala gönderilen tuzaklar

- **Telif hakkı aklama istemleri.** "Taylor Swift tarzında şarkı" — artık ticari Suno/Udio bunları filtreliyor, açık modeller filtrelemiyor. Kendi filtre listenizi ekleyin.
- **30 saniye sonrası tekrar / kayma.** AR modelleri döngüye girer. Birden fazla üretimi çapraz soluyun veya yapısal tutarlılık için ACE-Step kullanın.
- **Tempo kayması.** Modeller BPM'den sapar. İstemde BPM etiketleri kullanın ve librosa'nın `beat_track` fonksiyonuyla filtreleyin.
- **Vokal anlaşılırlığı.** Suno mükemmeldir; açık modeller kelimelerde genellikle bulanıktır. Sözler önemliyse ticari API kullanın veya ince ayar yapın.
- **Mono çıktı.** Açık modeller mono veya sahte stereo üretir. Doğru bir stereo yeniden oluşturma (ezst, Cartesia'nın stereo difüzyonu) ile yükseltin.

## Gönder

`outputs/skill-music-designer.md` olarak kaydedin. Bir müzik üretim dağıtımı için model, lisans stratejisi, süre/yapı planı ve beyan meta verilerini seçin.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. ASCII sembolleriyle "üretici" bir akor ilerlemesi + davul deseni üretir — bir müzik üretimi çizgi filmi. İsterseniz herhangi bir MIDI oynatıcıyla çalın.
2. **Orta.** `audiocraft`'ı kurun, MusicGen-small ile 4 farklı tür istemiyle 10 saniyelik klipler üretin, referans tür kümesine göre FAD ölçün.
3. **Zor.** ACE-Step (veya MusicGen-melody) kullanarak aynı melodi için farklı tını istemleriyle üç varyasyon üretin. Uyumu doğrulamak için isteme göre CLAP benzerliği hesaplayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|---------------------|------------------------|
| FAD | Ses FID'i | Gerçek vs üretilen gömme dağılımları arası Fréchet mesafesi. |
| Kromagram | Melodi olarak perdeler | Kare bazlı 12 boyutlu vektör; melodi koşullandırması girdisi. |
| Dallar | Enstrüman parçaları | Ayrılmış bas/davul/vokaller/melodi olarak WAV. |
| Boyama | Bir bölümü yeniden üretme | Bir zaman penceresini maskeleyin; model yalnızca onu yeniden üretir. |
| CLAP | Metin-ses CLIP'i | Karşıt (contrastive) ses-metin gömmesi; metin-ses uyumunu değerlendirir. |
| EnCodec | Müzik codec'i | Meta'nın MusicGen tarafından kullanılan nöral codec'i; 32 kHz, 4 kod kitabı. |

## İleri Okuma

- [Copet et al. (2023). MusicGen](https://arxiv.org/abs/2306.05284) — açık otoregresif referans.
- [Evans et al. (2024). Stable Audio Open](https://arxiv.org/abs/2407.14358) — ses tasarımı varsayılanı.
- [ACE-Step](https://github.com/ace-step/ACE-Step) — açık 4B tam şarkı üretici, Nisan 2026.
- [Suno v5 platform belgeleri](https://suno.com) — ticari kalite lideri.
- [AudioLDM2](https://arxiv.org/abs/2308.05734) — müzik + ses efektleri için gizli difüzyon.
- [WMG-Suno uzlaşma haberi](https://www.musicbusinessworldwide.com/suno-warner-music-settlement/) — Kasım 2025 emsal.
