# Ses Klonlama ve Ses Dönüştürme

> Ses klonlama (voice cloning), başkasının sesiyle metninizi okur. Ses dönüştürme (voice conversion), ne söylediğinizi koruyarak sesinizi başkasının sesine yeniden yazar. Her ikisi de aynı ayrıştırmaya dayanır: konuşmacı kimliğini içerikten ayırın.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 6 · 06 (Konuşmacı Tanıma), Faz 6 · 07 (TTS)
**Süre:** ~75 dakika

## Problem

2026'da 5 saniyelik bir ses klibi, tüketici GPU'suyla herhangi birinin sesinin yüksek kaliteli bir klonunu üretmek için yeterlidir. ElevenLabs, F5-TTS, OpenVoice v2, VoiceBox'ın hepsi zero-shot veya few-shot klonlama sunar. Teknoloji bir lütuftur (erişilebilirlik TTS, dublaj, yardımcı sesler) ve bir silah (dolandırıcılık çağrıları, siyasi deepfake'ler, Fikri Mülkiyet hırsızlığı).

Birbirleriyle yakından ilişkili iki görev:

- **Ses klonlama (TTS tarafı):** metin + 5 saniyelik referans ses → o sesle ses.
- **Ses dönüştürme (konuşma tarafı):** kaynak ses (kişi A, X diyor) + kişinin B referans sesi → B'nin X dediği ses.

Her ikisi de dalga formunu (içerik, konuşmacı, prosodi) ayrıştırır ve bir kaynağın içeriğini başka bir konuşmacı ile yeniden birleştirir.

2026'da artık taşıdığınız temel kısıt: **Filigran (watermark) ve rıza kapıları (consent gates) Avrupa Birliği'nde (Yapay Zeka Yasası, Ağustos 2026'da uygulanabilir) ve Kaliforniya'da (AB 2905, 2025'te yürürlükte) yasal olarak zorunludur**. Hattınız duyulamayan bir filigran çıkarmalı ve rızasız klonlamaları reddetmelidir.

## Kavram

![Ses klonlama vs dönüştürme: ayrıştır, konuşmacıyı değiştir, yeniden birleştir](../assets/voice-cloning.svg)

**Zero-shot klonlama.** Binlerce konuşmacı üzerinde eğitilmiş bir modele 5 saniyelik bir klibi geçirin. Konuşmacı kodlayıcısı (speaker encoder) klibi bir konuşmacı gömmesine (speaker embedding) eşler; TTS çözümleyicisi bu gömme artı metinle koşullandırılır.

Kullananlar: F5-TTS (2024), YourTTS (2022), XTTS v2 (2024), OpenVoice v2 (2024).

**Few-shot ince ayar.** Hedef sesin 5-30 dakikasını kaydedin. Bir taban modeli LoRA ile bir saat ince ayar yapın. Kalite "iyi"den "ayırılamaz" seviyeye sıçrar. Coqui ve ElevenLabs her ikisi de bu modeli destekler; topluluk F5-TTS ile kullanır.

**Ses dönüştürme (VC).** İki aile:

- **Tanıma-sentez.** İçerik temsili çıkarmak için ASR benzeri model çalıştırın (örn. yumuşak fonem olasılıkları, PPG'ler), ardından hedef konuşmacı gömmesiyle yeniden sentezleyin. Dile ve aksana karşı dayanıklı. KNN-VC (2023), Diff-HierVC (2023) tarafından kullanılır.
- **Ayırma (disentanglement).** İçeriği, konuşmacıyı ve prosodiyi gizli uzayda darboğazda ayıran bir oto-encoder (otomatik kodlayıcı) eğitin. Çıkarımda konuşmacı gömmesini değiştirin. Daha düşük kalite ama daha hızlı. AutoVC (2019), VITS-VC varyantları tarafından kullanılır.

**Nöral codec tabanlı klonlama (2024+).** VALL-E, VALL-E 2, NaturalSpeech 3, VoiceBox — sesi SoundStream / EnCodec'ten ayrık token'lar olarak işler, codec token'ları üzerinde büyük bir otoregresif veya akış eşleştirmeli model eğitir. Kısa istemlerde ElevenLabs'a yakın kalite.

### Etik kısmı, sonradan eklenen bir eklenti değil

**Filigran (watermarking).** PerTh (Perth) ve SilentCipher (2024) sesin içine fark edilemeyen ~16-32 bit kimlik yerleştirir. Yeniden kodlama, akış ve yaygın düzenlelemelere dayanır. Üretim için hazır açık kaynak.

**Rıza kapıları (consent gates).** Her klonlanmış çıktıyı doğrulanabilir bir rıza kaydıyla eşleştirmelisiniz. "Ben Rohit, 2026-04-22'de bu sesi X amacı için yetkilendiriyorum." Bozulmaya karşı kanıtlayıcı kayıtta saklayın.

**Algılama.** AASIST, RawNet2 ve Wav2Vec2-AASIST dedektör olarak kullanılır. ASVspoof 2025 challenge'ı, ElevenLabs, VALL-E 2 ve Bark çıktılarına karşı en iyi durum dedektörleri için %0.8–2.3 EER yayımlamıştır.

### Sayılar (2026)

| Model | Zero-shot? | SECS (hedef benzerliği) | WER (anlaşılabilirlik) | Parametre |
|-------|-----------|------------------------|----------------------|-----------|
| F5-TTS | Evet | 0.72 | %2.1 | 335M |
| XTTS v2 | Evet | 0.65 | %3.5 | 470M |
| OpenVoice v2 | Evet | 0.70 | %2.8 | 220M |
| VALL-E 2 | Evet | 0.77 | %2.4 | 370M |
| VoiceBox | Evet | 0.78 | %2.1 | 330M |

SECS > 0.70 genellikle çoğu dinleyici için hedeften ayırt edilemez.

## İnşa Et

### Adım 1: tanıma-sentez ile ayrıştırma (yalnızca kod, main.py'da)

```python
def clone_pipeline(ref_audio, text, target_embedder, tts_model):
    speaker_emb = target_embedder.encode(ref_audio)
    mel = tts_model(text, speaker=speaker_emb)
    return vocoder(mel)
```

#### Açıklama
Kavramsal olarak basit; uygulama ağırlığı `tts_model` ve konuşmacı kodlayıcısındadır.

### Adım 2: F5-TTS ile zero-shot klonlama

```python
from f5_tts.api import F5TTS
tts = F5TTS()
wav = tts.infer(
    ref_file="rohit_5s.wav",
    ref_text="The quick brown fox jumps over the lazy dog.",
    gen_text="Please add milk and bread to my list.",
)
```

#### Açıklama
Referans dökümü sesle tam olarak eşleşmelidir; uyumsuzluk hizalamayı bozar.

### Adım 3: KNN-VC ile ses dönüştürme

```python
import torch
from knnvc import KNNVC  # 2023 modeli, https://github.com/bshall/knn-vc
vc = KNNVC.load("wavlm-base-plus")
out_wav = vc.convert(source="my_voice.wav", target_pool=["alice_1.wav", "alice_2.wav"])
```

#### Açıklama
KNN-VC, kaynak ve havuz için kare bazlı gömmeleri çıkarmak için WavLM çalıştırır, ardından her kaynak karesini havuzdaki en yakın komşusuyla değiştirir. Parametrik değildir, bir dakikalık hedef konuşmayla çalışır.

### Adım 4: filigran yerleştirme

```python
from silentcipher import SilentCipher
sc = SilentCipher(model="2024-06-01")
payload = b"consent_id:abc123;ts:1745353200"
watermarked = sc.embed(wav, sr=24000, message=payload)
detected = sc.detect(watermarked, sr=24000)   # payload baytlarını döndürür
```

#### Açıklama
~32 bit yük (payload), MP3 yeniden kodlamasından ve hafif gürültüden sonra tespit edilebilir.

### Adım 5: rıza kapısı

```python
def cloned_inference(text, ref_audio, consent_record):
    assert verify_signature(consent_record), "İmzalı rıza gerekli"
    assert consent_record["speaker_id"] == hash_speaker(ref_audio)
    wav = tts.infer(ref_file=ref_audio, gen_text=text)
    wav = watermark(wav, payload=consent_record["id"])
    return wav
```

#### Açıklama
İmzalı rıza kaydını doğrular, konuşmacı kimliğini doğrular, TTS ile klonlar ve filigran ekler.

## Kullan

2026 yığını:

| Durum | Seçin |
|-------|-------|
| 5 s zero-shot klon, açık kaynak | F5-TTS veya OpenVoice v2 |
| Ticari üretim klonlama | ElevenLabs Instant Voice Clone v2.5 |
| Ses dönüştürme (yeniden yazma) | KNN-VC veya Diff-HierVC |
| Çok konuşmacılı ince ayar | StyleTTS 2 + konuşmacı adaptörü |
| Diller arası klonlama | XTTS v2 veya VALL-E X |
| Deepfake algılama | Wav2Vec2-AASIST |

## Tuzaklar

- **Yanlış hizalanmış referans dökümü.** F5-TTS ve benzerleri referans metninin referans sesle tam olarak eşleşmesini ister, noktalama işaretleri dahil.
- **Yankılı referans.** Yankı klonlamayı öldürür. Kuru, yakın mikrofonlu kayıt yapın.
- **Duygu uyumsuzluğu.** Eğitim referansı "neşeli" ise her şeyin neşeli klonlarını üretir. Referans duygusunu hedef kullanımla eşleştirin.
- **Dil sızıntısı.** İngilizce konuşmacıyı klonlayıp modele Fransızca konuşmasını söylediğinizde aksan genellikle yine de taşınır; diller arası modeller (XTTS, VALL-E X) kullanın.
- **Filigran yok.** Ağustos 2026'dan itibaren AB'de yasal olarak gönderilemez.

## Gönder

`outputs/skill-voice-cloner.md` olarak kaydedin. Rıza kapısı + filigran + kalite hedefiyle bir klonlama veya dönüştürme hattı tasarlayın.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. İki "konuşmacı" arasında kosinüs hesaplayarak konuşmacı gömmesi değişimini kanıtlar.
2. **Orta.** OpenVoice v2 ile kendi sesinizi klonlayın. Referans ve klon arasında SECS ölçün. Whisper ile CER ölçün.
3. **Zor.** SilentCipher filigranını 20 klonlamaya uygulayın, 128 kbps MP3 kodlama+çözümlemeden geçirin, payload'ı tespit edin. Bit doğruluğunu raporlayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|---------------------|------------------------|
| Zero-shot klon | 5 saniye yeterli | Önceden eğitilmiş model + konuşmacı gömmesi; eğitim yok. |
| PPG | Fonetik olasılıkigramı | Kare bazlı ASR olasılıkları; dil-bağımsız içerik temsili olarak kullanılır. |
| KNN-VC | En yakın komşu dönüştürme | Her kaynak karesini en yakın hedef havuzu karesiyle değiştirir. |
| Nöral codec TTS | VALL-E tarzı | EnCodec/SoundStream token'ları üzerinde AR modeli. |
| Filigran | Duyulamayan imza | Sese yerleştirilmiş bit'ler, yeniden kodlamaya dayanır. |
| SECS | Klonlama doğruluğu | Hedef ve klon konuşmacı gömmeleri arasında kosinüs. |
| AASIST | Deepfake dedektörü | Anti-spoofing modeli; sentezlenmiş konuşmayı tespit eder. |

## İleri Okuma

- [Chen et al. (2024). F5-TTS](https://arxiv.org/abs/2410.06885) — açık kaynak SOTA zero-shot klonlama.
- [Baevski et al. / Microsoft (2023). VALL-E](https://arxiv.org/abs/2301.02111) ve [VALL-E 2 (2024)](https://arxiv.org/abs/2406.05370) — nöral codec TTS.
- [Qian et al. (2019). AutoVC](https://arxiv.org/abs/1905.05879) — ayırma tabanlı ses dönüştürme.
- [Baas, Waubert de Puiseau, Kamper (2023). KNN-VC](https://arxiv.org/abs/2305.18975) — geri arama tabanlı VC.
- [SilentCipher (2024) — Ses Filigranı](https://github.com/sony/silentcipher) — üretim için hazır 32-bit ses filigranı.
- [ASVspoof 2025 sonuçları](https://www.asvspoof.org/) — dedektör vs sentezleyici silah yarışı, 2026'da güncellendi.
