# Konuşma Tanıma (ASR) — CTC, RNN-T, Attention

> Konuşma tanıma, her zaman adımında bir ses sınıflandırmasıdır; İngilizceyi ve sessizliği bilen bir dizi modeliyle birbirine yapıştırılır. CTC, RNN-T ve attention bunu yapmanın üç yoludur. Birini seçin ve nedenini anlayın.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 6 · 02 (Spektrogramlar & Mel), Faz 5 · 08 (Metin için CNN'ler ve RNN'ler), Faz 5 · 10 (Attention)
**Süre:** ~45 dakika

## Problem

10 saniyelik 16 kHz'lik bir kesik var. Bir dize istiyorsunuz: "mutfak lambalarını aç". Zorluk yapısaldır: ses çerçeveleri karakterlerle tek tek hizalanmaz. "Okay" kelimesi 200 ms veya 1200 ms sürebilir. Sessizlik konuşmayı keser. Bazı ses birimleri diğerlerinden daha uzundur. Çıktı jetonlarının sayısı önceden bilinmez.

Bu üç formülasyonu çözer:

1. **CTC (Connectionist Temporal Classification).** Özel bir *boşluk* dahil çerçeve başına jeton olasılıkları üretir. Çıkışta tekrarları ve boşlukları çökertir. Otoregressive değil, hızlıdır. wav2vec 2.0, MMS tarafından kullanılır.
2. **RNN-T (Recurrent Neural Network Transducer).** Encoder çerçevesi ve önceki jetonlar verildiğinde bir sonraki jetonu tahmin eden birleşik ağ. Akışa uygun. Google'ın cihaz içi ASR'ı, NVIDIA Parakeet tarafından kullanılır.
3. **Attention encoder-decoder.** Encoder sesi gizli durumlara sıkıştırır, decoder otoregressive olarak jeton üretmek için encoder çıktılarına cross-attention yapar. Whisper, SeamlessM4T tarafından kullanılır.

2026'da LibriSpeech test-clean'de SOTA WER %1.4 (Parakeet-TDT-1.1B, NVIDIA) ve %1.58 (Whisper-Large-v3-turbo)'dur. Farklar küçüktür; deployment farkları devasadır.

## Kavram

![Üç ASR formülasyonu: CTC, RNN-T, attention encoder-decoder](../assets/asr-formulations.svg)

**CTC sezgisi.** Encoder'ın `T` çerçeve düzeyinde `V+1` jetonu (V karakter + boşluk) üzerine dağılımlar üretmesine izin verin. Uzunluğu `U < T` olan hedef dize `y` için, `y`'ye çöken her çerçeve hizalaması sayılır. CTC kaybı tüm bu hizalamaların toplamıdır. Çıkarımda: çerçeve başına argmax, tekrarları çökert, boşlukları kaldır.

Avantajları: otoregressive değil, akışa uygun, sıfır ileriye bakma. Dezavantajı: *koşullu bağımsızlık varsayımı* — her çerçeve tahmini diğerlerinden bağımsızdır, yani dahili bir dil modeli yoktur. Beam search veya sığ birleştirme ile harici LM ile düzeltilir.

**RNN-T sezgisi.** Jeton geçmişini embed eden bir *tahminci* ağ ve tahminci durumunu encoder çerçevesiyle birleştiren bir *birleştirici* ekler. CTC'nin görmezden geldiği koşullu bağımsızlığı açıkça modeller. Akışa uygundur çünkü her adım yalnızca geçmiş çerçevelere ve geçmiş jetonlara koşulludur.

Avantajları: akışa uygun + dahili LM. Dezavantajı: eğitim daha karmaşık ve bellek açlığındadır (3D kayb ızgarası); RNN-T kayb çekirdekleri başlı başına bir kütüphe kategorisidir.

**Attention encoder-decoder.** Encoder (6-32 transformer katmanı) log-mel çerçevelerinin üzerinde. Decoder (6-32 transformer katmanı) jeton üretmek için encoder çıktılarına cross-attention yapar. Hizalama kısıtlaması yok — attention sesin herhangi bir yerine bakabilir. Attention'ı kısıtlamadığınız sürece akışa uygun değildir (parçalanmış Whisper-Streaming, 2024).

Avantajları: çevrimdışı ASR'de en yüksek kalite, standart seq2seq araçlarıyla kolay eğitim. Dezavantajı: otoregressive gecikme çıktı uzunluğuyla orantılıdır; mühendislik olmadan akışa uygun değildir.

### WER: tek sayı

**Kelime Hata Oranı (Word Error Rate)** = `(S + D + I) / N`, burada S=ikameler, D=silinmeler, I=eklemeler, N=referans kelime sayısı. Kelime düzeyinde Levenshtein edit mesafesiyle eşleşir. Düşük daha iyidir. %20 üzerindeki WER genellikle kullanılamaz; %5'in altında okuma konuşmasında insan seviyesidir. 2026'da standart benchmark'lardaki sayılar:

| Model | LibriSpeech test-clean | LibriSpeech test-other | Boyut |
|-------|------------------------|------------------------|-------|
| Parakeet-TDT-1.1B | %1.40 | %2.78 | 1.1B parametre |
| Whisper-Large-v3-turbo | %1.58 | %3.03 | 809M |
| Canary-1B Flash | %1.48 | %2.87 | 1B |
| Seamless M4T v2 | %1.7 | %3.5 | 2.3B |

Tümü encoder-decoder veya RNN-T tabanlıdır. Saf CTC sistemleri (wav2vec 2.0) test-clean'de %1.8–2.1 civarındadır.

## İnşa Et

### Adım 1: açgözlü CTC çözümlemesi

```python
def ctc_greedy(frame_logits, blank=0, vocab=None):
    # frame_logits: çerçeve başına olasılık vektörlerinin listesi
    preds = [max(range(len(p)), key=lambda i: p[i]) for p in frame_logits]
    out = []
    prev = -1
    for p in preds:
        if p != prev and p != blank:
            out.append(p)
        prev = p
    return "".join(vocab[i] for i in out) if vocab else out
```

#### Açıklama
İki kural: ardışık tekrarları çökertin, boşlukları bırakın. Örnek: `a a _ _ a b b _ c` → `a a b c`.

### Adım 2: ışın arama CTC

```python
def ctc_beam(frame_logits, beam=8, blank=0):
    import math
    beams = [([], 0.0)]  # (jetonlar, log_olasılık)
    for p in frame_logits:
        log_p = [math.log(max(pi, 1e-10)) for pi in p]
        candidates = []
        for seq, lp in beams:
            for t, lpt in enumerate(log_p):
                new = seq[:] if t == blank else (seq + [t] if not seq or seq[-1] != t else seq)
                candidates.append((new, lp + lpt))
        candidates.sort(key=lambda x: -x[1])
        beams = candidates[:beam]
    return beams[0][0]
```

#### Açıklama
Üretimde ön ek ağacı ışın araması ve LM birleştirme kullanılır; bu kavramsal iskelettir.

### Adım 3: WER

```python
def wer(ref, hyp):
    r, h = ref.split(), hyp.split()
    dp = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]
    for i in range(len(r) + 1):
        dp[i][0] = i
    for j in range(len(h) + 1):
        dp[0][j] = j
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            cost = 0 if r[i - 1] == h[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + cost,
            )
    return dp[len(r)][len(h)] / max(1, len(r))
```

#### Açıklama
Dinamik programlama ile referans ve hipotez arasındaki kelime hata oranını hesaplar.

### Adım 4: Whisper'a karşı çıkarım

```python
import whisper
model = whisper.load_model("large-v3-turbo")
result = model.transcribe("clip.wav")
print(result["text"])
```

#### Açıklama
2026'daki en güçlü genel ASR için tek satırlık kod. 24 GB GPU'da ~20× gerçek zaman hızında çalışır.

### Adım 5: Parakeet veya wav2vec 2.0 ile akış

```python
from transformers import pipeline
asr = pipeline("automatic-speech-recognition", model="nvidia/parakeet-tdt-1.1b")
for chunk in streaming_audio():
    print(asr(chunk, return_timestamps=True))
```

#### Açıklama
Akışa uygun ASR, parçalanmış encoder attention ve devlet devretme gerektirir; bunu destekleyen bir kütüphane kullanın (Parakeet için NeMo, `chunk_length_s` ile `transformers` pipeline'ı).

## Kullan

2026 yığını:

| Durum | Seçin |
|-------|------|
| İngilizce, çevrimdışı, maksimum kalite | Whisper-large-v3-turbo |
| Çok dilli, sağlam | SeamlessM4T v2 |
| Akış, düşük gecikme | Parakeet-TDT-1.1B veya Riva |
| Kenar, mobil, <500 ms gecikme | Nicellenmiş Whisper-Tiny veya Moonshine (2024) |
| Uzun form | VAD tabanlı parçalama ile Whisper (WhisperX) |
| Alana özgü (tıbbi, hukuki) | wav2vec 2.0 + alan LM birleştirmesi ile ince ayar |

## 2026'da Hala Yaygınlaşan Tuzaklar

- **Yok VAD.** Sessizlikte Whisper çalıştırma halüsünasyon üretir ("Thanks for watching!"). Her zaman VAD ile kontrol edin.
- **Karakter vs kelime vs alt kelime WER.** Kelime düzeyinde WER'yi normalizasyondan sonra (küçük harf, noktalama işaretleri çıkarılmış) raporlayın.
- **Dil kimliği kayması.** Whisper'ın otomatik dil kimliği gürültülü klipleri Japonca veya Galce'ye yönlendirir; bildiğinizde `language="en"` zorlayın.
- **Parçalama olmadan uzun klipler.** Whisper'ın 30 saniyelik bir penceresi var. Daha uzun her şey için `chunk_length_s=30, stride=5` kullanın.

## Gönder

`outputs/skill-asr-picker.md` olarak kaydedin. Belirli bir deployment hedefi için modeli, çözümleme stratejisini, parçalamayı ve LM birleştirmesini seçin.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Elle oluşturulmuş bir CTC çıktısını açgözlü çözümler ve bir referansa karşı WER hesaplar.
2. **Orta.** Adım 2'deki ön ek ağacı ışın aramasını düzgün bir şekilde uygulayın (boşluk birleştirme kuralını hesaba katarak). 10 örneklik bir sentetik veri setinde açgözlü ile karşılaştırın.
3. **Zor.** [LibriSpeech test-clean](https://www.openslr.org/12) üzerinde `whisper-large-v3-turbo` kullanın. İlk 100 ifadede WER hesaplayın. Yayınlanan sayılarla karşılaştırın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|---------------------|------------------------|
| CTC | Boşluk-jetonu kaybı | Tüm çerçeve-jeton hizalamaları üzerinde marjinal; otoregressive değil. |
| RNN-T | Akış kaybı | CTC + bir sonraki jeton tahmincisi; kelime sırasını ele alır. |
| Attention enc-dec | Whisper tarzı | Encoder + cross-attention yapan decoder; en iyi çevrimdışı kalite. |
| WER | Raporladığınız sayı | Kelime düzeyinde `(S+D+I)/N`. |
| Boşluk | Boşluk | CTC'de "bu çerçevede emisyon yok" sinyali veren özel jeton. |
| LM birleştirmesi | Harici dil modeli | Işın araması sırasında ağırlıklı LM log-olasılıkları eklenir. |
| VAD | Sessizlik kapısı | Konuşma etkinliği algılayıcı; konuşma dışını kırpır. |

## İleri Okuma

- [Graves et al. (2006). Connectionist Temporal Classification](https://www.cs.toronto.edu/~graves/icml_2006.pdf) — CTC makalesi.
- [Graves (2012). Sequence Transduction with RNNs](https://arxiv.org/abs/1211.3711) — RNN-T makalesi.
- [Radford et al. / OpenAI (2022). Whisper: Robust Speech Recognition via Large-Scale Weak Supervision](https://arxiv.org/abs/2212.04356) — 2022 kanonik makalesi; v3-turbo uzantısı 2024'te.
- [NVIDIA NeMo — Parakeet-TDT kartı](https://huggingface.co/nvidia/parakeet-tdt-1.1b) — 2026 Açık ASR Liderlik Tablosu lideri.
- [Hugging Face — Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) — 25+ model üzerinde canlı benchmark.
