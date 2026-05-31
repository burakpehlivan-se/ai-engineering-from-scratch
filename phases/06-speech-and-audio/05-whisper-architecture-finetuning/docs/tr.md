# Whisper — Mimari ve İnce Ayar

> Whisper 30 saniyelik pencereye sahip bir transformer encoder-decoder'dır; 680 bin saat çok dilli zayıf denetimli ses-metin çifti üzerinde eğitilmiştir. Tek mimari,birden fazla görev, 99 dil genelinde sağlam. 2026 referans ASR'ı.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 6 · 04 (ASR), Faz 5 · 10 (Attention), Faz 7 · 05 (Tam Transformer)
**Süre:** ~75 dakika

## Problem

Whisper, Eylül 2022'de OpenAI tarafından yayınlanan, bir emtia olarak sunulan ilk ASR modeliydi: sesi yapıştırın, metni alın, 99 dil, gürültüye sağlam, dizüstü bilgisayarda çalışır. 2024'e kadar OpenAI Large-v3 ve Turbo varyanslarını çıkardı; 2026'ya kadar Whisper, podcast transkripsiyonundan ses asistanlarına ve YouTube altyazılarına kadar her şeyin varsayılan temelidir.

Ama Whisper'ı sonsuza kadar bir siyah kutu olarak ele alamazsınız. Alan kayması onu öldürür — teknik jargon, konuşmacı aksanları, özel isimler, kısa klipler, sessizlik. şunları bilmeniz gerekir:

1. İçeride gerçekte ne olduğu.
2. Ona parçalanmış, akışa uygun veya uzun form sesini nasıl doğru şekilde vereceğiniz.
3. Ne zaman ince ayar yapılacağı ve nasıl yapılacağı.

## Kavram

![Whisper encoder-decoder, görevler, parçalanmış çıkarım, ince ayar](../assets/whisper.svg)

**Mimari.** Standart transformer encoder-decoder.

- Girdi: 30 saniyelik log-mel spektrogramı, 80 mel, 10 ms adım → 3000 çerçeve. Daha kısa klipler sıfırla doldurulur, daha uzun klipler parçalanır.
- Encoder: conv-downsample (adım 2) + `N` transformer bloğu. Large-v3 için: 32 katman, 1280 boyut, 20 baş.
- Decoder: Nedenli öz-dikkat + encoder çıktısına cross-attention ile `N` transformer bloğu. Encoder ile aynı boyut.
- Çıktı: 51.865 jetonluk bir sözlük üzerinde BPE jetonları.

Large-v3 1.55B parametre içerir. Turbo 4 katmanlı bir decoder kullanır (32'den), gecikmeyi 8× keser ve <%1 WER bedeliyle.

**İstem biçimi.** Whisper, decoder istemindeki özel jetonlarla yönlendirilen bir çok görevli modeldir:

```
<|startoftranscript|><|en|><|transcribe|><|notimestamps|> Hello world.
```

- `<|en|>` — dil etiketi; çeviriye karşı transkripsiyon davranışını zorlar.
- `<|transcribe|>` veya `<|translate|>` — herhangi bir dil girdisinden İngilizce çıktı çevirisi veya birebir transkripsiyon.
- `<|notimestamps|>` — kelime düzeyinde zaman damgalarını atla (daha hızlı).

İstem bir modelin birçok görevi yapmasını sağlar. `<|en|>`'yi `<|fr|>` ile değiştirirseniz Fransızca transkripsiyon yapar.

**30 saniyelik pencere.** Her şey 30 saniyeye sabitlenmiştir. Daha uzun klipler parçalanmalıdır; daha kısa klipler doldurulur. Pencereler doğal olarak akışa uygun değildir — bu yüzden WhisperX, Whisper-Streaming ve faster-whisper vardır.

**Log-mel normalizasyonu.** `(log_mel - ortalama) / std` burada istatistikler Whisper'ın kendi eğitim kümesinden gelir. Whisper'ın ön işlemini (`whisper.audio.log_mel_spectrogram`) kullanmalısınız; `librosa.feature.melspectrogram` değil.

### 2026'daki Varyanslar

| Varyans | Parametreler | Gecikme (A100) | WER (LibriSpeech-clean) |
|---------|-------------|----------------|------------------------|
| Tiny | 39M | 1× gerçek zaman | %5.4 |
| Base | 74M | 1× | %4.1 |
| Small | 244M | 1× | %3.0 |
| Medium | 769M | 1× | %2.7 |
| Large-v3 | 1.55B | 2× | %1.8 |
| Large-v3-turbo | 809M | 8× | %1.58 |
| Whisper-Streaming (2024) | 1.55B | akış | %2.0 |

### İnce ayar

2026'da kanonik iş akışı:

1. Hizalı transkripsiyonlarla hedef alanda 10–100 saat ses toplayın.
2. `generate_with_loss` geri çağrısıyla `transformers.Seq2SeqTrainer` çalıştırın.
3. Parametre verimli: attention katmanlarının `q_proj`, `k_proj`, `v_proj`'ünde LoRA, GPU belleğini <%0.3 WER bedeliyle 4× azaltır.
4. 10 saatin altında encoder'ı dondurun. Yalnızca decoder'ı ince ayar yapın.
5. Whisper'ın kendi tokenizer'ını ve istem biçimini kullanın; tokenizer'ları değiştirmeyin.

Topluluk sonuçları: 20 saat tıbbi diktasyon üzerinde Medium'u ince ayar yapmak WER'yi tıbbi kelime haznesinde %12'den %4.5'e düşürür. 4 saat İzlandaca üzerinde Turbo'yu ince ayar yapmak WER'yi %18'den %6'ya düşürür.

## İnşa Et

### Adım 1: Whisper'ı kutusundan çıkar çıkmaz çalıştırın

```python
import whisper
model = whisper.load_model("large-v3-turbo")
result = model.transcribe(
    "clip.wav",
    language="en",
    task="transcribe",
    temperature=0.0,
    condition_on_previous_text=False,  # kaçak tekrar sorununu önler
)
print(result["text"])
for seg in result["segments"]:
    print(f"[{seg['start']:.2f}–{seg['end']:.2f}] {seg['text']}")
```

#### Açıklama
`temperature=0.0` (örnekleme varsayılanı 0.0 → 0.2 → 0.4 … geri dönüş zinciri), `condition_on_previous_text=False` (kaskatlı halüsination sorununu önler) ve `no_speech_threshold=0.6` (sessizlik algılama) her zaman geçersiz kılınması gereken temel ayarlardır.

### Adım 2: parçalanmış uzun form

```python
# whisperx 2026'da kelime düzeyinde zaman damgalarıyla uzun form için referanstır
import whisperx
model = whisperx.load_model("large-v3-turbo", device="cuda", compute_type="float16")
segments = model.transcribe("1hour.mp3", batch_size=16, chunk_size=30)
```

#### Açıklama
WhisperX şunları ekler: (1) Silero VAD kapısı, (2) wav2vec 2.0 ile kelime düzeyinde hizalama, (3) `pyannote.audio` ile diarizasyon. 2026 üretimi transkripsiyon için işgücü.

### Adım 3: LoRA ile ince ayar

```python
from transformers import WhisperForConditionalGeneration, WhisperProcessor
from peft import LoraConfig, get_peft_model

model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large-v3-turbo")
lora = LoraConfig(
    r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1, bias="none", task_type="SEQ_2_SEQ_LM",
)
model = get_peft_model(model, lora)
# model.print_trainable_parameters()  -> ~3M eğitilebilir / 809M toplam
```

#### Açıklama
Sonra standart Trainer döngüsü. Her 1000 adımda kontrol noktası. Ayrılmış veride WER ile değerlendirin.

### Adım 4: her katmanın ne öğrendiğini inceleyin

```python
# Decoder sırasında cross-attention ağırlıklarını alarak decoder'ın nereye baktığını görün.
with torch.inference_mode():
    out = model.generate(
        input_features=features,
        return_dict_in_generate=True,
        output_attentions=True,
    )
# out.cross_attentions: katman × baş × adım × kaynak_uzunluğu
```

#### Açıklama
Isı haritasıyla görselleştirin — decoder adımları encoder çerçevelerini tararken diyagonal hizalama göreceksiniz. Bu diyagonal Whisper'ın kelime zaman damgası kavramıdır.

## Kullan

2026 yığını:

| Durum | Seçin |
|-------|------|
| Genel İngilizce, çevrimdışı | `whisperx` aracılığıyla Large-v3-turbo |
| Mobil / kenar | Nicellenmiş Whisper-Tiny (int8) veya Moonshine |
| Çok dilli uzun form | `whisperx` + diarizasyon ile Large-v3 |
| Düşük kaynaklı dil | LoRA ile Medium veya Turbo ince ayarı |
| Akış (2 s gecikme) | Whisper-Streaming veya Parakeet-TDT |
| Kelime düzeyinde zaman damgaları | WhisperX (wav2vec 2.0 ile zorunlu hizalama) |

`faster-whisper` (CTranslate2 arka ucu) 2026'da en hızlı CPU+GPU çıkarım çalışma zamanıdır — özdeş çıktıyla 4× daha hızlıdır.

## 2026'da Hala Yaygınlaşan Tuzaklar

- **Sessizlikte halüsination metni.** Whisper altyazılarla eğitildiğinden "Thanks for watching!", "Subscribe!", şarkı sözleri üretir. Her zaman VAD ile kapattıktan sonra çağırın.
- **`condition_on_previous_text` kaskatı.** Bir halüsination sonraki pencereleri kirletir. Parçalar arasında akıcılık gerekmedikçe `False` ayarlayın.
- **Kısa klip doldurma.** 2 saniyelik bir klip 30 saniyeye doldurulduğunda sonda sessizlikte halüsination yapabilir. `pad=False` veya VAD kapısı kullanın.
- **Yanlış mel istatistikleri.** librosa'nın mel'lerini Whisper'ınkileri yerine kullanmak neredeyse rastgele çıktı üretir. `whisper.audio.log_mel_spectrogram` kullanın.

## Gönder

`outputs/skill-whisper-tuner.md` olarak kaydedin. Belirli bir alan için bir Whisper ince ayar veya çıkarım hattı tasarlayın.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Whisper tarzı bir istemi tokenize eder, çözülmüş şekil bütçeleri hesaplar ve 10 dakikalık bir kesik için parçalama programını yazdırır.
2. **Orta.** `faster-whisper` yükleyin, 10 dakikalık bir podcast'i transkripsiyon edin, WER'yi bir insan transkripsiyonuyla karşılaştırın. `language="auto"` ile zorlanmış `language="en"`'yi deneyin.
3. **Zor.** HF `datasets` kullanarak Whisper'ın zorlandığı bir dil seçin (ör. Urduca), 2 saat veriyle 2 epoch için Medium'u LoRA ile ince ayar yapın ve WER farkını raporlayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|---------------------|------------------------|
| 30 sn pencere | Whisper'ın limiti | Sert girdi tavanı; daha uzun sesi parçalayın. |
| SOT | Transkripsiyon başlangıcı | `<\|startoftranscript\|>` decoder istemini başlatır. |
| Zaman damgası jetonu | Zamansal hizalama | Her 0.02 sn_ofset 51k sözlükte özel bir jetondur. |
| Turbo | Hızlı varyans | 4 decoder katmanı, 8× daha hızlı, <%1 WER gerilemesi. |
| WhisperX | Uzun form sarmalayıcısı | VAD + Whisper + wav2vec hizalama + diarizasyon. |
| LoRA ince ayarı | Verimli ayarlama | Attention'a düşük sıralı adaptörler ekle; parametrelerin ~%0.3'ünü eğit. |
| Halüsination | Sessiz hata | Whisper gürültüden/sessizlikten akıcı İngilizce üretir. |

## İleri Okuma

- [Radford et al. (2022). Whisper makalesi](https://arxiv.org/abs/2212.04356) — Orijinal mimari ve eğitim reçetesi.
- [OpenAI (2024). Whisper Large-v3-turbo yayını](https://github.com/openai/whisper/discussions/2363) — 4 katmanlı decoder, 8× hızlanma.
- [Bain et al. (2023). WhisperX](https://arxiv.org/abs/2303.00747) — Uzun form, kelime hizalı, diarize edilmiş.
- [Systran — faster-whisper deposu](https://github.com/SYSTRAN/faster-whisper) — CTranslate2 destekli, 4× daha hızlı.
- [HuggingFace — Whisper ince ayar eğitimi](https://huggingface.co/blog/fine-tune-whisper) — Kanonik LoRA / tam ince ayar yol gösterici.
