# Ses-Dil Modelleri: Whisper'dan Audio Flamingo 3'e Yolculuk

> Whisper (Radford ve ark., Aralık 2022) konuşmayı tanıma (speech recognition) sorununu çözdü — 680 bin saat zayıf denetimli (weakly-supervised) çok dilli konuşma, basit bir encoder-decoder transformer, her sonraki ASR sürümünün atıfta bulunduğu bir benchmark. Ancak tanıma çıkarma (reasoning) değildir. "Bu kayıtta hangi enstrümanlar var" veya "konuşmacı hangi duyguyu ifade ediyor" veya "3. dakikada ne oldu" demek ses anlama gerektirir, transkripsiyon değil. Qwen-Audio, SALMONN, LTU ve NVIDIA'nın Audio Flamingo 3'ü (AF3, Temmuz 2025) bu yığını (stack) kademeli olarak inşa etti: Whisper sınıfı encoder'ları koruyun, Q-former'ları ekleyin, ses-metin talimat verileriyle eğitin, zincir-düşünce (chain-of-thought) çıkarması ekleyin. Bu ders bu yolculuğu ele alır.

**Tür:** İnşa Et
**Diller:** Python (stdlib, log-Mel spectrogram + audio Q-former iskeleti)
**Ön koşullar:** Faz 6 (Speech and Audio), Faz 12 · 03 (Q-Former)
**Süre:** ~180 dakika

## Öğrenme Hedefleri

- Dalga formundan (waveform) log-Mel spectrogram hesaplayın: pencereleme (windowing), FFT, filtre bankaları (filter banks), log dönüşümü.
- Encoder seçeneklerini karşılaştırın: Whisper encoder, BEATs, AF-Whisper hibridi. Her birinin ne zaman kazandığını belirleyin.
- Bir ses Q-former'ı inşa edin: spectrogram yamalarına (patch) çapraz dikkat eden N öğrenilebilir sorgu.
- Kademeli (Whisper-sonra-LLM) vs uçtan uca ses-LLM eğitimini açıklayın: uçtan uca neden çıkarma için daha iyi ölçeklenir.

## Problem

Konuşma tanıması Whisper tarafından çözüldü. Ses OCR'ı (OCR-of-audio) bir meta haline geldi. Ancak "meta" transkripsiyonda durur. Model duydukları üzerinde çıkarma yapamıyorsa — zamanlama, konuşmacılar, duygu, müzik yapısı, çevresel sesler — transkripsiyon tek başına ürün özelliklerini yönetemez.

Üç açık yol:

1. Kademeli: Whisper transkript eder, LLM transkript üzerinde çıkarım yapar. Saf konuşma senaryoları için çalışır. Müzik, çevresel ses, çok konuşmacılı örtüşme, duygu için başarısız olur.

2. Uçtan uca ses-LLM: bir ses encoder'ı ses token'larını doğrudan bir LLM'e besler, transkripsiyonu atlar. Akustik bilgiyi (duygu, konuşmacı, çevre) korur. Yeni eğitim verisine ihtiyaç duyar.

3. Hibrit: hem transkript edebilen hem de çıkarım yapabilen ses encoder + metin decoder. Qwen-Audio ve Audio Flamingo bu yolu seçer.

## Kavram

### Log-Mel spectrogram: girdi özelliği

Her ses encoder'ı aynı özellikle başlar: log-Mel spectrogram.

1. 16 kHz'e yeniden örnekleyin.
2. 25ms pencereler, 10ms atlama (hop) ile kısa süreli Fourier dönüşümü (short-time Fourier transform).
3. FFT sonucunun genliğini (magnitude) alın.
4. Algılama frekansına eğmek için Mel filtre bankaları uygulayın (tipik olarak 0-8000 Hz aralığında log-aralıklı 80 filtre).
5. Dinamik aralık için log sıkıştırma (log(1 + x)).

Sonuç: (T, 80) boyutunda 2B dizi; T zaman karesi sayısıdır. 30 saniyelik bir klip için 100 Hz kare hızıyla: (3000, 80).

### Whisper'ın encoder'ı

Whisper'ın encoder'ı, log-Mel spectrogram'ı zaman karesi dizisi olarak işleyen 12 katmanlı ViT tarzı bir transformer'dır. Çıktı: zaman karesi başına bir gizli durum (hidden-state) vektörü.

ASR için Whisper'ın decoder'ı, encoder çıktısına koşullu metin token'ları üreten çapraz dikkatli (cross-attention) bir transformer'dır. Standart encoder-decoder.

Ses-LLM'ler için, encoder çıktısını farklı bir LLM'in girdisi olarak istersiniz. Patern: Whisper encoder dondurulmuş, Q-former eğitilebilir, LLM dondurulmuş veya ayarlanmış.

### BEATs ve sese özgü encoder'lar

Whisper ağırlıklı olarak konuşma verileri üzerinde eğitildi. Müzik ve çevresel ses için daha zayıftır.

BEATs (Chen ve ark., 2022), AudioSet üzerinde eğitilmiş öz denetimli (self-supervised) bir transformer'dır. Aynı parametre sayısıyla Whisper'dan daha iyi müzik ve çevresel ses yakalar.

AF-Whisper (Audio Flamingo 3'ün hibridi): Whisper + BEATs özelliklerini ses girdisi olarak birleştirir. Whisper dil sinyalini, BEATs akustik sinyalini taşır.

### Ses Q-former'ı

BLIP-2'nin görsel Q-former'ı ile aynı patern. Sabit sayıda öğrenilebilir sorgu (tipik olarak 32 veya 64) ses encoder'ının çıktı kareleri üzerinde çapraz dikkat eder. Sorgular LLM tarafından tüketilen ses token'ları haline gelir.

Hizalama aşaması eğitimi: sadece Q-former, ses-metin çiftleri (AudioCaps, Clotho) üzerinde contrastive + captioning kayıpları. Talimat aşaması: uçtan uca, LLM dondurulmamış, talimat verisiyle eğitilir.

### Yolculuk — SALMONN, Qwen-Audio, AF3

SALMONN (Tang ve ark., 2023): Whisper + BEATs + Q-former + LLaMA. Ciddi çıkarma yeteneğine sahip ilk açık ses-LLM'i. MMAU benchmark'larında ~0.55 bileşik.

Qwen-Audio (Chu ve ark., 2023): benzer mimari, daha zengin veri seti üzerinde eğitilmiş, çok turlu diyalog için ayarlanmış. MMAU ~0.60.

LTU — Dinle, Anla, Kavra (Gong ve ark., 2023): açık çıkarım verisi, ses klipleri üzerinde zincir-düşünceye odaklanma. Daha küçük ancak daha odaklı.

Audio Flamingo 3 (Goel ve ark., Temmuz 2025): mevcut açık SOTA. 8B LLM omurgası (Qwen2 7B), Whisper-large encoder concat BEATs, 64 sorgulu Q-former, 1M+ ses-metin talimat çifti üzerinde eğitim. MMAU 0.72, bazı alt görevlerde özel sınırla eşleşiyor.

AF3 aynı anda ses için zincir-düşünce seçeneği sunar: model isteğe bağlı olarak son cevaptan önce düşünme token'ları ("önce enstrümanları tanıyayım: ...") üretebilir. Düşünme etkinleştirildiğinde karmaşık çıkarma görevlerinde doğruluk 3-5 puan artar.

### Kademeli vs uçtan uca

Kademeli boru hattı:

1. Whisper sesi transkript eder → metin.
2. LLM metin üzerinde çıkarım yapar.

"Bu podcast'i özetle" için mükemmel çalışır. Başarısız olduğu durumlar:
- "Bu şarkının havası ne?" — hava seste, kelimelerde değil.
- "Kim konuşuyor, Alice mi Bob mu?" — konuşmacı tanıma gerektirir.
- "Patlama hangi saniyede oluyor?" — zamansal yer belirleme metinde kaybolur.
- "Bu gerçek mi yoksa üretilmiş ses mi?" — deepfake tespiti akustik özellik gerektirir.

Uçtan uca akustik sinyali korur. Qwen-Audio ve AF3 müziği, ortamı ve duyguyu doğal olarak işler.

### 2026 üretim reçetesi

Yeni bir ses anlama ürünü için:

- Kademeli: transkripsiyon hedefse, müzik yoksa, duygu çıkarımı yoksa.
- AF3 / Qwen-Audio ailesi: müzik, duygu, çok konuşmacılı veya karmaşık ses çıkarması varsa.

Kademeli daha ucuz ve basittir. Uçtan uca daha yetkilidir.

### MMAU — ses çıkarma benchmark'ı

MMAU (Massive Multimodal Audio Understanding) 2024-2025 ses çıkarma benchmark'ıdır:

- Konuşma, müzik, çevresel sesler genelinde 10.000 ses-metin soru-cevap çifti.
- Sınıflandırma, zamansal çıkarma, nedensel çıkarma, açık uçlu soru-cevabı kapsar.
- Kademeli boru hatlarının sistematik olarak kaçırdıklarını test eder.

Açık SOTA (AF3) 0.72'de; özel sınır ~0.78 (Gemini 2.5 Pro, Claude Opus 4.7). Fark, VideoMME'nin açık-kapalı farkından daha küçüktür; bu da ses-LLM'lerin olgunlaştığını gösterir.

## Kullan

`code/main.py`:

- Standart kütüphane (stdlib) ile log-Mel spectrogram hesaplaması uygular: pencereleme, naïve DFT, Mel filtre bankası.
- Ses Q-former iskeleti: encoder çıktı kareleri verildiğinde Q, K, V, attention hesaplar ve N token üretir.
- Bir oyuncak görevde kademeli-vs-uçtan-uca karşılaştırma.

## Teslim Et

Bu ders `outputs/skill-audio-llm-pipeline-picker.md` dosyasını üretir. Bir ses görevi (transkripsiyon, müzik etiketleme, duygu çıkarımı, çok konuşmacılı diarizasyon, ortam sınıflandırması) verildiğinde kademeli, uçtan uca AF3 veya hibriti seçer.

## Alıştırmalar

1. 16kHz, 25ms pencere, 10ms atlama, 80 Mel kutucuğu ile 30 saniyelik bir klibin log-Mel spectrogram boyutunu hesaplayın. 48kHz'de bu nasıl değişir?

2. Whisper neden müzikte düşük performans gösterir? BEATs hangi ses özelliklerini Whisper'ın yakalayamadığı şekilde yakalar?

3. 64 sorgulu ses Q-former'ı vs 32 sorgulu: hangi görev karmaşıklığında 64 kendini doğrular? 32 ne için hesaplama tasarrufu sağlar?

4. AF3 Bölüm 4'ü isteğe bağlı düşünme üzerine okuyun. Zincir-düşüncenin en çok yardımcı olduğu üç ses görevi önerin.

5. AF3 çıktısını kullanarak minimal bir diarizasyon boru hattı uygulayın. Konuşmacı değişimlerini nasıl sinyallersiniz?

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| Log-Mel spectrogram | "Mel özellikleri" | Mel filtre bankalarından sonra log genlik değerlerinden oluşan 2B (zaman, frekans) dizi |
| Ses Q-former | "Ses Perceiver'ı" | Ses encoder çıktısından sabit uzunluklu sorgulara çapraz dikkat darboğazı (bottleneck); LLM'i besler |
| Kademeli | "ASR-sonra-LLM" | Whisper transkript eden ve metin LLM'inin çıkarma yaptığı boru hattı; akustik bilgi kaybolur |
| Uçtan uca | "Ses-LLM" | Ses özellikleri Q-former aracılığıyla doğrudan LLM'e girer; akustik sinyali korur |
| BEATs | "Ses AudioSet encoder'ı" | AudioSet üzerinde eğitilmiş SSL transformer; müzik + çevresel seslerde güçlü |
| MMAU | "Ses çıkarma benchmark'ı" | Konuşma, müzik, ortam genelinde 10k soru-cevap çifti; 2024 değerlendirme standardı |
| İsteğe bağlı düşünme | "Ses CoT" | Model isteğe bağlı olarak son cevaptan önce çıkarım token'ları üretebilir, doğruluk 3-5 puan artar |

## Daha Fazla Kaynak

- [Radford ve ark. — Whisper (arXiv:2212.04356)](https://arxiv.org/abs/2212.04356)
- [Chu ve ark. — Qwen-Audio (arXiv:2311.07919)](https://arxiv.org/abs/2311.07919)
- [Goel ve ark. — Audio Flamingo 3 (arXiv:2507.08128)](https://arxiv.org/abs/2507.08128)
- [Tang ve ark. — SALMONN (arXiv:2310.13289)](https://arxiv.org/abs/2310.13289)
- [Gong ve ark. — LTU (arXiv:2305.10790)](https://arxiv.org/abs/2305.10790)
