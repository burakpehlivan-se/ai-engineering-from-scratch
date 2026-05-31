# Ses Değerlendirme — WER, MOS, UTMOS, MMAU, FAD ve Açık Liderlik Tabloları

> Ölçemediğiniz bir şeyi gönderemezsiniz. Bu ders, her ses görevi için 2026 metriklerini adlandırır: ASR (WER, CER, RTFx), TTS (MOS, UTMOS, SECS, ASR tur-uçuşunda WER), ses-dil (MMAU, LongAudioBench), müzik (FAD, CLAP) ve konuşmacı (EER). Karşılaştırma yaptığınız liderlik tablolarıyla birlikte.

**Tür:** Öğren
**Diller:** Python
**Ön koşullar:** Faz 6 · 04, 06, 07, 09, 10; Faz 2 · 09 (Model Değerlendirmesi)
**Süre:** ~60 dakika

## Problem

Her ses görevinin her biri farklı bir ekseni ölçen birden fazla metriği vardır. Yanlış metriği kullanmak, panelinizde harika görünüp üretimde berbat olan bir model göndermenin yoludur. 2026 kanonik listesi:

| Görev | Birincil | İkincil |
|-------|---------|---------|
| ASR | WER | CER · RTFx · ilk-token gecikmesi |
| TTS | MOS / UTMOS | SECS · ASR tur-uçuşunda WER · CER · TTFA |
| Ses klonlama | SECS (ECAPA kosinüsü) | MOS · CER |
| Konuşmacı doğrulama | EER | minDCF · çalışma noktasında FAR / FRR |
| Diyarizasyon | DER | JER · konuşmacı karışıklığı |
| Ses sınıflandırma | top-1 · mAP | makro F1 · sınıfa göre duyarlılık |
| Müzik üretimi | FAD | CLAP · dinleme paneli MOS |
| Ses dil modeli | MMAU-Pro | LongAudioBench · AudioCaps FENSE |
| Akışlı S2S | gecikme P50/P95 | WER · MOS |

## Kavram

![Ses değerlendirme matrisi — metrikler vs görevler vs 2026 liderlik tabloları](../assets/eval-landscape.svg)

### ASR metrikleri

**WER (Kelime Hata Oranı).** `(S + D + I) / N`. Küçük harf, noktalama işaretlerini kaldırın, sayıları puanlamadan önce normalize edin. `jiwer` veya OpenAI'nin `whisper_normalizer` kullanın. < %5 = insan dengisi okunan konuşma.

**CER (Karakter Hata Oranı).** Aynı formül, karakter düzeyinde. Ton dillerinde (Mandarinca, Kantonca) kullanılır kelime ayırt etme belirsiz olduğunda.

**RTFx (ters gerçek zamanlı faktörü).** Duvar saati saniyesi başına işlenen ses saniyesi. Yüksek daha iyidir. Parakeet-TDT 3380× ulaşır. Whisper-large-v3 ~30×'tur.

**İlk-token gecikmesi.** Ses girişinden ilk transkripsiyon token'ına kadar duvar saati. Akışlı için kritik. Deepgram Nova-3: ~150 ms.

### TTS metrikleri

**MOS (Ortalama Görüş Puanı).** 1-5 insan puanı. Altın standart ama yavaş. Örnek başına 20+ dinleyici, model başına 100+ örnek toplayın.

**UTMOS (2022-2026).** Öğrenilmiş MOS tahmincisi. Standart benchmark'larda insan MOS'uyla ~0.9 korelasyon. F5-TTS: UTMOS 3.95; gerçek: 4.08.

**SECS (Konuşmacı Kodlayıcı Kosinüs Benzerliği).** Ses klonlama için. Referans ve klonlanmış çıktı arasında ECAPA gömme kosinüsü. > 0.75 = tanınabilir klon.

**ASR tur-uçuşunda WER.** TTS çıktısı üzerinden Whisper çalıştırın, giriş metnine göre WER hesaplayın. Anlaşılabilirlik regresyonlarını yakalar. 2026 SOTA: < %2 CER.

**TTFA (ses-ilk-zamanı).** Duvar saati gecikmesi. Kokoro-82M: ~100 ms; F5-TTS: ~1 s.

### Ses klonlamasına özgü

**SECS + MOS + CER** üçlüsü. Yüksek SECS ama düşük MOS alan klonlama tını doğru ama doğal olmayan anlamına gelir; tersi doğal ses ama yanlış konuşmacı anlamına gelir.

### Konuşmacı doğrulama

**EER (Eşit Hata Oranı).** False Accept Rate = False Reject Rate olan eşik. VoxCeleb1-O'da ECAPA: %0.87.

**minDCF (minimum Tespit Maliyeti).** Seçilen bir çalışma noktasında (genellikle FAR=0.01) ağırlıklı maliyet. EER'den daha çok üretimle ilgilidir.

### Diyarizasyon

**DER (Diyarizasyon Hata Oranı).** `(FA + Kaçırma + Karışıklık) / toplam_konuşmacı_süresi`. Kaçırılmış konuşma + yanlış alarm konuşması + konuşmacı karışıklığı, her biri kesir olarak. AMI toplantıları: DER ~%10-20 gerçektir. pyannote 3.1 + Precision-2 ticari: iyi kaydedilmiş seslerde < %10 DER.

**JER (Jaccard Hata Oranı).** DER'nin alternatifi, kısa segment yanlılığına karşı dayanıklı.

### Ses sınıflandırma

Çok etiketli: **mAP (ortalama Ortalama Kesinliği)** tüm sınıflar genelinde. AudioSet: BEATs-iter3 için 0.548 mAP.

Çok sınıflı münhasır: **top-1, top-5 doğruluğu**. Speech Commands v2: Audio-MAE ile %99.0 top-1.

Dengesiz: **makro F1** + **sınıfa göre duyarlılık**. Sınıfa göre raporlayın — toplam doğruluk hangi sınıfların başarısız olduğunu gizler.

### Müzik üretimi

**FAD (Fréchet Ses Mesafesi).** VGGish-gömme dağılımları arasında gerçek vs üretilen ses mesafesi. MusicCaps'te MusicGen-küçük: 4.5. MusicLM: 4.0. Düşük daha iyi.

**CLAP Puanı.** CLAP gömmeleri kullanarak metin-ses uyum puanı. > 0.3 = makul uyum.

**Dinleme paneli MOS.** Tüketici düzeyinde müzik için hala son söz. TTS Arena'da Suno v5 ELO 1293 ( eşleştirilmiş insan tercihlerinden).

### Ses-dil benchmark'ları

**MMAU (Büyük Çoklu Ses Anlama).** 10k ses-soru-cevap çifti.

**MMAU-Pro.** 1800 zor madde, dört kategori: konuşma / ses / müzik / çoklu ses. 4 yollu testte rastgele şans %25. Gemini 2.5 Pro genel ~%60; çoklu ses tüm modellerde ~%22.

**LongAudioBench.** Anlamsal sorgularla çok dakikalık klipler. Audio Flamingo Next Gemini 2.5 Pro'yu yener.

**AudioCaps / Clotho.** Biçimlendirme benchmark'ları. SPICE, CIDEr, FENSE metrikleri.

### Akışlı konuşmadan konuşmaya

**Gecikme P50 / P95 / P99.** Kullanıcı konuşmasının bitiminden ilk duyulabilir yanıtına kadar duvar saati. Moshi: 200 ms; GPT-4o Realtime: 300 ms.

**WER / MOS** çıktıda.

**Araya girme duyarlılığı.** Kullanıcı kesintisinden asistan sessizliğine kadar süre. Hedef < 150 ms.

### 2026 liderlik tabloları

| Liderlik tablosu | İzledikleri | URL |
|-----------------|------------|-----|
| Açık ASR Liderlik Tablosu (HF) | İngilizce + çok dilli + uzun biçim | `huggingface.co/spaces/hf-audio/open_asr_leaderboard` |
| TTS Arena (HF) | İngilizce TTS | `huggingface.co/spaces/TTS-AGI/TTS-Arena` |
| Yapay Zeka Analizi Ses | TTS + STT, eşleştirilmiş oylardan ELO | `artificialanalysis.ai/speech` |
| MMAU-Pro | LALM akıl yürütmesi | `mmaubenchmark.github.io` |
| SpeakerBench / VoxSRC | Konuşmacı tanıma | `voxsrc.github.io` |
| MMAU müzik alt kümesi | Müzik LALM | (MMAU içinde) |
| HEAR benchmark | Kendi kendine denetimsiz ses | `hearbenchmark.com` |

## İnşa Et

### Adım 1: normalizasyonlu WER

```python
from jiwer import wer, Compose, ToLowerCase, RemovePunctuation, Strip

transform = Compose([ToLowerCase(), RemovePunctuation(), Strip()])
score = wer(
    truth="Please turn on the lights.",
    hypothesis="please turn on the light",
    truth_transform=transform,
    hypothesis_transform=transform,
)
# ~0.17
```

#### Açıklama
Giriş ve hipotez metinlerini küçük harfe çevirme, noktalama kaldırma ve kırpma dönüşümleri uygulayarak WER hesaplar.

### Adım 2: TTS tur-uçuğu WER

```python
def ttr_wer(tts_model, asr_model, texts):
    errors = []
    for txt in texts:
        audio = tts_model.synthesize(txt)
        recog = asr_model.transcribe(audio)
        errors.append(wer(truth=txt, hypothesis=recog))
    return sum(errors) / len(errors)
```

#### Açıklama
TTS çıktısını ASR'den geçirerek giriş metnine göre WER hesaplayan tur-uçuğu (round-trip) değerlendirme.

### Adım 3: ses klonlama için SECS

```python
from speechbrain.inference.speaker import EncoderClassifier
sv = EncoderClassifier.from_hparams("speechbrain/spkrec-ecapa-voxceleb")

emb_ref = sv.encode_batch(load_wav("reference.wav"))
emb_clone = sv.encode_batch(load_wav("cloned.wav"))
secs = torch.nn.functional.cosine_similarity(emb_ref, emb_clone, dim=-1).item()
```

#### Açıklama
SpeechBrain ECAPA modeliyle referans ve klonlanmış sesin konuşmacı gömmelerini çıkararak kosinüs benzerliği hesaplar.

### Adım 4: müzik üretimi için FAD

```python
from frechet_audio_distance import FrechetAudioDistance
fad = FrechetAudioDistance()
score = fad.get_fad_score("generated_folder/", "reference_folder/")
```

#### Açıklama
Gerçek ve üretilen ses klasörleri arasındaki VGGish-gömme tabanlı Fréchet mesafesini hesaplar.

### Adım 5: konuşmacı doğrulama için EER (Ders 6 ile aynı kod)

```python
def eer(same_scores, diff_scores):
    thresholds = sorted(set(same_scores + diff_scores))
    best = (1.0, 0.0)
    for t in thresholds:
        far = sum(1 for s in diff_scores if s >= t) / len(diff_scores)
        frr = sum(1 for s in same_scores if s < t) / len(same_scores)
        if abs(far - frr) < best[0]:
            best = (abs(far - frr), (far + frr) / 2)
    return best[1]
```

#### Açıklama
Aynı ve farklı konuşmacı puanları kümesi üzerinde Eşit Hata Oranı hesaplar.

## Kullan

Her dağıtıma her model güncellemesinde çalışan sabit bir değerlendirme donanımıyla (eval harness) eşleştirin. Üç kural:

1. **Puanlamadan önce normalize edin.** Küçük harf, noktalama kaldırma, sayı genişletme. Normalizasyon kuralını raporlayın.
2. **Dağılımlar raporlayın, ortalamalar değil.** Gecikme için P50/P95/P99. Sınıflandırma için sınıfa göre duyarlılık. MMAU için kategoriye göre.
3. **Tek kanonik açık benchmark çalıştırın.** Üretim veriniz farklı olsa bile, Açık ASR / TTS Arena / MMAU'da raporlamak karşılaştırılabilirlik sağlar.

## Tuzaklar

- **UTMOS dışlaması.** VCTK tarzı temiz konuşmayla eğitilmiştir; gürültülü / klonlanmış / duygusal sesi kötü puanlar.
- **MOS panel yanlılığı.** 20 Amazon Mechanical Turk işçisi ≠ 20 hedef kullanıcı. Stakes yüksekse alan paneli için ödeme yapın.
- **FAD referans kümesine bağlıdır.** Modeller arasında aynı referans dağılımına karşı karşılaştırın.
- **Toplam WER.** Genelde %5 WER, aksanlı konuşmada %30 WER'yi gizleyebilir. Demografik dilime göre raporlayın.
- **açık benchmark doygunluğu.** Çoğu sınır modeli standart benchmark'larda tavana yakındır. Trafiğinizi yansıtan bir iç ayrılmış küme oluşturun.

## Gönder

`outputs/skill-audio-evaluator.md` olarak kaydedin. Herhangi bir ses modeli sürümü için metrikleri, benchmark'ları ve raporlama biçimini seçin.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Oyuncak girdiler üzerinde WER / CER / EER / SECS / FAD-benzeri / MMAU-benzeri hesaplayın.
2. **Orta.** Bir TTS tur-uçuğu WER donanımı oluşturun. Kokoro veya F5-TTS çıktınızı Whisper'dan geçirin. 50 istem üzerinde WER hesaplayın. WER > %10 olan istemleri işaretleyin.
3. **Zor.** Ders 10 LALM seçiminizi MMAU-Pro konuşma + çoklu ses alt kümeleri (her biri 50 madde) üzerinde puanlayın. Kategoriye göre doğruluğu raporlayın ve yayımlanan rakamla karşılaştırın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|---------------------|------------------------|
| WER | ASR puanı | Normalizasyondan sonra kelime düzeyinde `(S+D+I)/N`. |
| CER | Karakter WER'i | Ton dilleri veya karakter düzeyli sistemler için. |
| MOS | İnsan görüşü | 1-5 puanlama; 20+ dinleyici × 100 örnek. |
| UTMOS | ML MOS tahmincisi | Öğrenilmiş model; insan MOS'uyla ~0.9 korelasyon. |
| SECS | Ses klonlama benzerliği | Referans ve klon arasında ECAPA kosinüsü. |
| EER | Konuşmacı doğrulama puanı | FAR = FRR olan eşik. |
| DER | Diyarizasyon puanı | (FA + Kaçırma + Karışıklık) / toplam. |
| FAD | Müzik üretimi kalitesi | VGGish gömmeleri üzerinde Fréchet mesafesi. |
| RTFx | Verim | Duvar saati saniyesi başına ses saniyesi. |

## İleri Okuma

- [jiwer](https://github.com/jitsu/jiwer) — normalizasyon yardımcılarıyla WER/CER kitaplığı.
- [UTMOS (Saeki ve ark. 2022)](https://arxiv.org/abs/2204.02152) — öğrenilmiş MOS tahmincisi.
- [Fréchet Ses Mesafesi (Kilgour ve ark. 2019)](https://arxiv.org/abs/1812.08466) — müzik üretimi standartı.
- [Açık ASR Liderlik Tablosu](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) — 2026 canlı sıralamaları.
- [TTS Arena](https://huggingface.co/spaces/TTS-AGI/TTS-Arena) — insan oylu TTS liderlik tablosu.
- [MMAU-Pro benchmark'ı](https://mmaubenchmark.github.io/) — LALM akıl yürütmesi liderlik tablosu.
- [HEAR benchmark'ı](https://hearbenchmark.com/) — ses SSL benchmark'ları.
