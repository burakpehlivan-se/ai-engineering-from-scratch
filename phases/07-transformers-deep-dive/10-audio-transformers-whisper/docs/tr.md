# Ses Transformer'ları — Whisper Mimarisi

> Ses, zaman üzerinde frekans görüntüsüdür. Whisper, mel spektrogramlarını yiyen ve geri konuşan bir ViT'tir.

**Tür:** Öğren
**Diller:** Python
**Önkoşullar:** Faz 7 · 05 (Tam Transformer), Faz 7 · 08 (Encoder-Decoder), Faz 7 · 09 (ViT)
**Süre:** ~45 dakika

## Sorun

Whisper'dan (OpenAI, Radford ve diğerleri, 2022) önce, durum-en-iyi (state-of-the-art) otomatik konuşma tanıma (ASR), wav2vec 2.0 ve HuBERT demekti — kendi kendine denetimli özellik çıkarıcılar (self-supervised feature extractors) ve bir inceltilmiş kafa. Yüksek kalite, pahalı veri hatları, alana kırılgan. Çok dilli konuşma tanıma, dil ailesi başına ayrı modeller gerektiriyordu.

Whisper üç bahse girdi:

1. **Her şey üzerinde eğitin.** 97 dilde internet'ten kazılmış 680.000 saat zayıf etiketli ses. Temiz akademik metin kümesi yok. Fonem etiketleri yok.
2. **Çoklu görev tek model.** Tek bir decoder, transkripsiyon, çeviri, ses aktivitesi tespiti, dil tanımlama ve zaman damgası (timestamp) üzerine görev token'larıyla ortak olarak eğitildi.
3. **Standart encoder-decoder transformer.** Encoder log-mel spektrogramlarını tüketir. Decoder otonom olarak metin token'ları üretir. Vocoder yok, CTC yok, HMM yok.

Sonuç: Whisper large-v3, aksanlara, gırtılağa ve sıfır temiz etiketli verisi olan dillere karşı dayanıklıdır. 2026'da her açık kaynaklı ses asistanının ve ticari olanlarının çoğunun varsayılan ses ön yüzüdür.

## Kavram

![Whisper hattı: ses → mel → encoder → decoder → metin](../assets/whisper.svg)

### Adım 1 — yeniden örnekleme + pencereleme

16 kHz'te ses. 30 saniyeye kırp/doldur. Log-mel spektrogramı hesapla: 80 mel kutusu, 10 ms adım → ~3.000 çerçeve × 80 özellik. Bu Whisper'ın看到dığı "görüntü girdisi"dir.

### Adım 2: konvolüyon gövdesi (convolutional stem)

Çekirdek 3 ve adım 2 ile iki Conv1D katmanı, 3.000 çerçeveyi 1.500'e düşürür. Dizi uzunluğunu çok fazla parametre eklemeden ikiye böler.

### Adım 3: encoder

1.500 zaman adımı üzerinde 24 katmanlı (büyük model için) transformer encoder. Sinüzoidal konumsal kodlama, self-attention, GELU FFN. 1.500 × 1.280 gizli durum üretir.

### Adım 4: decoder

24 katmanlı transformer decoder. GPT-2'nin bir süper kümesi olan ve birkaç sese özel özel token içeren BPE sözlüğünden otonom olarak token üretir.

### Adım 5: görev token'ları

Decoder istemi, modele ne yapacağını söyleyen kontrol token'larıyla başlar:

```
<|startoftranscript|>  <|en|>  <|transcribe|>  <|0.00|>
```

veya

```
<|startoftranscript|>  <|fr|>  <|translate|>   <|0.00|>
```

#### Açıklama
Model bu sözleşmeyle eğitildi. Görevi ön ek (prefix) ile kontrol edersiniz. 2026'da talimat-eğitimin (instruction-tuning) karşılığı, ancak sese uygulanmış.

### Adım 6: çıktı

Genişlik 5 ile ışın araması ve log-olasılık eşiği. `<|notimestamps|>` token'ı yoksa zaman damgaları her 0.02 saniyede bir tahmin edilir.

### Whisper boyutları

| Model | Parametre | Katman | d_head | Baş | VRAM (fp16) |
|-------|--------|--------|---------|-------|-------------|
| Tiny | 39M | 4 | 384 | 6 | ~1 GB |
| Base | 74M | 6 | 512 | 8 | ~1 GB |
| Small | 244M | 12 | 768 | 12 | ~2 GB |
| Medium | 769M | 24 | 1024 | 16 | ~5 GB |
| Large | 1550M | 32 | 1280 | 20 | ~10 GB |
| Large-v3 | 1550M | 32 | 1280 | 20 | ~10 GB |
| Large-v3-turbo | 809M | 32 | 1280 | 20 | ~6 GB (4 katmanlı decoder) |

Large-v3-turbo (2024) decoder'ı 32 katmandan 4'e düşürdü. <1 WER puanı regresyonuyla 8× daha hızlı çözümleme. Bu çözümleme hız kilidi, Whisper-turbo'nun 2026'da gerçek zamanlı ses ajanları için varsayılan olmasının nedenidir.

### Whisper'ın yapamadığı şeyler

- Konuşmacı tanımlama (diarization) — kim konuşuyor. Bunun için pyannote ile eşleştirin.
- Doğrudan gerçek zamanlı akış (streaming) — 30 saniyelik pencere sabittir. Modern sarmalayıcılar (`faster-whisper`, `WhisperX`) VAD + örtüşme yoluyla akış ekler.
- Dış parçalama olmadan 30 saniyeyi aşan uzun bağlam. Pratikte iyi çalışır çünkü insan konuşması transkripsiyon için nadiren uzun menzilli bağlam gerektirir.

### 2026 manzarası

| Görev | Model | Notlar |
|------|-------|-------|
| İngilizce ASR | Whisper-turbo, Moonshine | Moonshine kenarda 4× daha hızlı |
| Çok dilli ASR | Whisper-large-v3 | 97 dil |
| Akışlı ASR | faster-whisper + VAD | 150 ms gecikme hedefleri ulaşılabilir |
| TTS | Piper, XTTS-v2, Kokoro | Encoder-decoder kalıbı, ancak Whisper şeklinde |
| Ses + dil | AudioLM, SeamlessM4T | Bir transformer'da metin token'ları + ses token'ları |

## İnşa Et

`code/main.py`'ye bakın. Whisper'ı eğitmiyoruz — log-mel spektrogram hattını + görev-token istem biçimlendiricisini (prompt formatter) oluşturuyoruz. Üretimde gerçekten dokunduğunuz bölümler bunlardır.

### Adım 1: sesi sentezle

440 Hz'te 1 saniyelik sinüs dalgası, 16 kHz'te örneklenmiş. 16.000 örnek.

### Adım 2: log-mel spektrogramı (basitleştirilmiş)

Tam mel spektrogramı FFT gerektirir. `librosa` olmadan hattı gösteren basitleştirilmiş çerçeveleme + kare-başına enerji versiyonu yapıyoruz:

```python
def frame_signal(x, frame_size=400, hop=160):
    frames = []
    for start in range(0, len(x) - frame_size + 1, hop):
        frames.append(x[start:start + frame_size])
    return frames
```

#### Açıklama
Çerçeve = 25 ms, adım = 10 ms. Whisper'ın pencerelemesiyle eşleşir. Kare-başına enerji, pedagoji için mel kutusunun yerine geçer.

### Adım 3: 30 saniyeye doldur

Whisper her zaman 30 saniyelik parçaları işler. Spektrogramı 3.000 çerçeveye doldurun (veya kırpın).

### Adım 4: istem token'larını oluştur

```python
def whisper_prompt(lang="en", task="transcribe", timestamps=True):
    tokens = ["<|startoftranscript|>", f"<|{lang}|>", f"<|{task}|>"]
    if not timestamps:
        tokens.append("<|notimestamps|>")
    return tokens
```

#### Açıklama
Bu tüm görev-kontrol yüzeyidir. 4 token'lık bir ön ek.

## Kullan

```python
import whisper
model = whisper.load_model("large-v3-turbo")
result = model.transcribe("meeting.wav", language="en", task="transcribe")
print(result["text"])
print(result["segments"][0]["start"], result["segments"][0]["end"])
```

Daha hızlı, OpenAI-uyumlu:

```python
from faster_whisper import WhisperModel
model = WhisperModel("large-v3-turbo", compute_type="int8_float16")
segments, info = model.transcribe("meeting.wav", vad_filter=True)
for s in segments:
    print(f"{s.start:.2f} - {s.end:.2f}: {s.text}")
```

#### Açıklama
`faster-whisper`, CTranslate2 tabanlıdır ve OpenAI referansından 4× daha hızlıdır. int8 nicemleme (quantization) kullanır.

**2026'da Whisper ne zaman seçilir:**

- Tek modelle çok dilli ASR.
- Gürültülü, çeşitli sesin dayanıklı transkripsiyonu.
- Araştırma / prototipleme ASR — en hızlı başlangıç noktası.

**Başka bir şey ne zaman seçilir:**

- Kenarda ultra-düşük gecikmeli akış — Moonshine eşleşen kalitede Whisper'ı geçer.
- <200 ms gerektiren gerçek zamanlı konuşma yapay zekası — özel akışlı ASR.
- Konuşmacı tanımlama — Whisper bunu yapmaz; pyannote ekleyin.

## Teslim Et

`outputs/skill-asr-configurator.md`'ye bakın. Bu beceri, yeni bir ses uygulaması için bir ASR modeli, çözümleme parametreleri ve ön-işleme hattı seçer.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. 16 kHz'te 10 ms adımlı 1 saniyelik sinyal için çerçeve sayısının ~100 çerçeve olduğunu doğrulayın. 30 saniye için: ~3.000 çerçeve.
2. **Orta.** `numpy.fft` kullanarak tam log-mel spektrogramını oluşturun. 80 mel kutusunun `librosa.feature.melspectrogram(n_mels=80)` ile sayısal hata içinde eşleştiğini doğrulayın.
3. **Zor.** Akışlı çıkarımı (streaming inference) uygulayın: sesi 2 saniye örtüşmeli 10 saniyelik pencerelere bölün, her parçada Whisper çalıştırın, transkripsiyonları birleştirin. 5 dakikalık bir podcast örneğinde tek geçişe karşı kelime-hata oranını ölçün.

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Mel spektrogramı | "Ses görüntüsü" | 2D temsil: bir eksende frekans kutuları, diğerinde zaman çerçeveleri; hücre başına log ölçekli enerji. |
| Log-mel | "Whisper'ın gördüğü" | Log'dan geçirilmiş mel spektrogramı; sesin algılanan yüksekliğini yaklaşık olarak temsil eder. |
| Çerçeve (Frame) | "Zaman dilimi" | 25 ms'lik örnek penceresi; 10 ms adımda çakışmalı. |
| Görev token'ı (Task token) | "Ses için istem ön eki" | Decoder isteminde `<\|transcribe\|>` / `<\|translate\|>` gibi özel token'lar. |
| Ses aktivitesi tespiti (VAD) | "Sesi bul" | ASR'dan önce sessizliği kaldıran kapı; maliyeti büyük ölçüde azaltır. |
| CTC | "İlişkisel Zamansal Sınıflandırma" | Klasik ASR kaybı, hizalamasız eğitim için; Whisper bunu kullanmaz. |
| Whisper-turbo | "Küçük decoder, tam encoder" | large-v3 encoder + 4 katmanlı decoder; 8× daha hızlı çözümleme. |
| Faster-whisper | "Üretim sarmalayıcısı" | CTranslate2 yeniden uygulaması; int8 nicemleme; OpenAI referansından 4× daha hızlı. |

## İleri Okuma

- [Radford ve diğerleri (2022). Robust Speech Recognition via Large-Scale Weak Supervision](https://arxiv.org/abs/2212.04356) — Whisper makalesi.
- [OpenAI Whisper depo](https://github.com/openai/whisper) — referans kod + model ağırlıkları. `whisper/model.py`'yi okuyarak ~400 satırda Conv1D gövdesi + encoder + decoder'ı üstten alta görün.
- [OpenAI Whisper — `whisper/decoding.py`](https://github.com/openai/whisper/blob/main/whisper/decoding.py) — Adımlar 5–6'da açıklanan ışın-aramaı + görev-token mantığı buradadır; 500 satır, tamamen okunabilir.
- [Baevski ve diğerleri (2020). wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations](https://arxiv.org/abs/2006.11477) — öncül; bazı ortamlarda hala SOTA özellikler.
- [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) — üretim sarmalayıcısı, referansın 4× daha hızlısı.
- [Jia ve diğerleri (2024). Moonshine: Speech Recognition for Live Transcription and Voice Commands](https://arxiv.org/abs/2410.15608) — 2024 kenar-dostu ASR, Whisper şeklinde ancak daha küçük.
- [HuggingFace blog — "Fine-Tune Whisper For Multilingual ASR with 🤗 Transformers"](https://huggingface.co/blog/fine-tune-whisper) — mel spektrogramı önişlemcisi ve zaman-daması işlemenin dahil olduğu kanonik inceltme tarifi.
- [HuggingFace `modeling_whisper.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/models/whisper/modeling_whisper.py) — encoder, decoder, çapraz-dikkat, üretimi içeren tam uygulama, dersin mimari diyagramını yansıtır.
