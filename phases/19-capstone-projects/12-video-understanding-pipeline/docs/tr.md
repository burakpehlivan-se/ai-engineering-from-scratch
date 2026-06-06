# Capstone 12 — Video Anlama Boru Hattı (Sahne, Soru-Cevap, Arama)

> Twelve Labs Marengo + Pegasus'ı ürünleştirdi. VideoDB video için CRUD API'sini yayınladı. AI2'nin Molmo 2'si açık VLM kontrol noktalarını yayınladı. Gemini uzun-bağlam saati olarak saatlerce videoyu doğal olarak yönetir. TimeLens-100K ölçekte zamansal temellendirmeyi tanımladı. 2026 boru hattı yerleşti: sahne segmentasyonu, sahne başına altyazı + gömme, transkript hizalaması, çok-vektörlü endeks ve (başlangıç, bitiş) zaman damgaları artı çerçeve önizlemeleri ile yanıt veren bir sorgu. Capstone 100 saati hazmedin, herkese açık kıyaslamaları geçin ve sayma ve eylem sorularında halüsinasyonu ölçün.

**Type:** Capstone
**Languages:** Python (pipeline), TypeScript (UI)
**Prerequisites:** Phase 4 (CV), Phase 6 (speech), Phase 7 (transformers), Phase 11 (LLM engineering), Phase 12 (multimodal), Phase 17 (infrastructure)
**Phases exercised:** P4 · P6 · P7 · P11 · P12 · P17
**Time:** 30 saat

## Problem

Uzun-form video Soru-Cevap, 2026 ölçeğinde en bant genişliği aç olan çok modlu sorundur. Gemini 2.5 Pro 2 saatlik bir videoyu doğal olarak okuyabilir, ancak 100 saatlik videoyu sorgulanabilir bir korpusa hazmetmek hâlâ sahne-düzeyinde bir endeks gerektirir. Üretim şekli, sahne segmentasyonu (TransNetV2 veya PySceneDetect), bir VLM ile sahne başına altyazılama (Gemini 2.5, Qwen3-VL-Max veya Molmo 2), transkript hizalaması (kelime zaman damgalarıyla Whisper-v3-turbo) ve altyazı, çerçeve gömme ve transkripti yan yana saklayan çok-vektörlü bir endeks birleştirir. Sorgu boru hattı (başlangıç, bitiş) zaman damgaları artı çerçeve önizlemeleri ile yanıt verir.

Kıyaslamalar herkese açıktır (ActivityNet-QA, NeXT-GQA) artı kendi 100-sorguluk özel kümeniz. Sayma ve eylem-türü sorularda halüsinasyon bilinen-zor hata sınıfıdır; capstone bunu açıkça ölçer.

## Concept

Hazmetme zamanında üç boru hattı paralel çalışır. **Sahne segmentasyonu** videoyu sahnelere keser. **VLM altyazılama** her sahne için bir altyazı ve bir anahtar-çerçeveden bir çerçeve gömme üretir. **ASR hizalama** kelime-düzeyinde zaman damgaları üretir. Üç akış (sahne_kimliği, zaman aralığı) ile birleştirilir. Her sahne çok-vektörlü bir endekste (Qdrant) üç vektör türü alır: altyazı gömme, anahtar-çerçeve gömme, transkript gömme.

Sorgu zamanında, doğal-dil sorusu üç vektöre karşı ateşlenir; sonuçlar RRF ile birleşir; bir zamansal-temellendirme adaptörü (TimeLens tarzı) en iyi sahnede (başlangıç, bitiş) penceresini iyileştirir. VLM sentezleyici (Gemini 2.5 Pro veya Qwen3-VL-Max), sorgu + en iyi sahneler + kırpılmış çerçeveler alır ve alıntılanmış zaman damgaları ve bir çerçeve önizlemesi ile yanıt verir.

Halüsinasyon ölçümü önemlidir. Sayma ("odaya kaç kişi giriyor?") ve eylem-türü ("şef karıştırmadan önce mi döküyor?") soruları, görüntü-dil modellerinin bilinen güvenilmez olduğu konulardır. Doğruluğu betimleyici sorulardan ayrı olarak raporlayın.

## Architecture

```
video file / URL
      |
      v
PySceneDetect / TransNetV2  (scene segmentation)
      |
      +--- per-scene keyframe --- VLM caption + frame embedding
      |                            (Gemini 2.5 Pro / Qwen3-VL-Max / Molmo 2)
      |
      +--- audio channel --- Whisper-v3-turbo ASR + word timestamps
      |
      v
multi-vector Qdrant: {caption_emb, keyframe_emb, transcript_emb}
      |
query:
  dense queries against all three -> RRF merge -> top-k scenes
      |
      v
TimeLens / VideoITG temporal grounding (refine start/end within scene)
      |
      v
VLM synth: query + top scenes + frame previews
      |
      v
answer + (start, end) timestamps + frame thumbs + citations
```

#### Açıklama

Bu mimari ham video dosyasından alıntılanmış bir video Soru-Cevap yanıtına kadar tam boru hattını gösterir. Sahne segmentasyonu (TransNetV2 veya PySceneDetect) videoyu sahnelere böler. Her sahnenin anahtar-çerçevesi bir VLM'ye (Gemini 2.5 Pro veya Qwen3-VL-Max) gönderilir; altyazı ve çerçeve gömme üretilir. Ses kanalı Whisper-v3-turbo ile kelime zaman damgalarıyla transkriptlenir. Üç akış bir Qdrant çok-vektörlü koleksiyonunda birleşir. Sorgu zamanında doğal-dil sorusu üç vektöre karşı paralel ateşlenir; RRF birleştirmesi en iyi k sahneyi seçer. TimeLens adaptörü (başlangıç, bitiş) penceresini iyileştirir. Son olarak bir VLM sentezleyici yanıtı alıntılanmış zaman damgaları ve çerçeve küçük resimleri ile üretir.

## Stack

- Sahne segmentasyonu: TransNetV2 (son teknoloji 2024-26) veya PySceneDetect
- ASR: Kelime zaman damgalarıyla faster-whisper üzerinden Whisper-v3-turbo
- VLM altyazılayıcı + yanıtlayıcı: Gemini 2.5 Pro veya Qwen3-VL-Max veya Molmo 2
- Zamansal temellendirme: TimeLens-100K-eğitilmiş adaptör veya VideoITG
- Endeks: Çok-vektörlü destekli Qdrant (altyazı / çerçeve / transkript)
- Arayüz: HTML5 video oynatıcı ve sahne küçük resimleri ile Next.js 15
- Değerlendirme: ActivityNet-QA, NeXT-GQA, özel 100-soruluk el ile etiketlenmiş küme
- Halüsinasyon kıyaslaması: El etiketleriyle sayma ve eylem-türü alt kümeleri

## Build It

1. **Hazmetme gezgini.** YouTube URL'lerini veya yerel MP4'leri kabul edin. Gerekirse 720p'ye küçültün. `{video_id, file_path}` kalıcı kılın.

2. **Sahne segmentasyonu.** TransNetV2 veya PySceneDetect çalıştırarak `[{scene_id, start_ms, end_ms, keyframe_path}]` üretin. 100 saat hedefi: ~6k-8k sahne.

3. **ASR geçişi.** Seste Whisper-v3-turbo çalıştırın; kelime-düzeyinde zaman damgalarını dışa aktarın; sahne başına transkript dilimlerine ayırın.

4. **VLM altyazılama.** Sahne başına, anahtar-çerçeve ve kısa bir altyazı şablonu ile Gemini 2.5 Pro (veya Qwen3-VL-Max) çağırın. Altyazı + çerçeve gömme üretin.

5. **Çok-vektörlü endeks.** Üç adlandırılmış vektörle Qdrant koleksiyonu. Yük: `{video_id, scene_id, start_ms, end_ms, keyframe_url}`.

6. **Sorgu.** Doğal-dil sorusu üç yoğun sorguyu ateşler; resiprok sıra füzyonu ile birleştirilir; ilk-k=5 sahne.

7. **Zamansal temellendirme.** En iyi sahnede TimeLens tarzı adaptör çalıştırarak sahnenin içindeki (başlangıç, bitiş) penceresini iyileştirin.

8. **VLM sentezi.** Gemini 2.5 Pro'yu sorgu + ilk-3 sahne klipi (görüntü veya kısa klip olarak) + transkriptler ile çağırın. `(video_id, start_ms, end_ms)` alıntıları gerektirin.

9. **Değerlendirme.** ActivityNet-QA ve NeXT-GQA çalıştırın. 100-soruluk özel küme inşa edin. Genel doğruluk + sınıf başına döküm (sayma, eylem, betimleyici) raporlayın.

## Use It

```
$ video-qa ask --url=https://youtube.com/watch?v=X "how many cars pass the intersection in the first minute?"
[scene]    23 scenes detected
[asr]      transcript complete, 4m12s
[index]    69 vectors written (23 scenes x 3)
[query]    top scene: scene 3 [01:32-01:54], confidence 0.84
[ground]   refined window: [00:12-00:58]
[synth]    gemini 2.5 pro, 1.4s
answer:    5 cars pass the intersection between 00:12 and 00:58.
citations: [scene 3: 00:12-00:58]
          [frame preview at 00:14, 00:27, 00:44, 00:51, 00:57]
```

#### Açıklama

Bu örnek bir video Soru-Cevap sorgusunun tam yaşam döngüsünü gösterir. Sistem 23 sahne tespit eder, transkripti 4m12s'de tamamlar, 69 vektör yazar (23 sahne × 3). Sorgu ilk sahne olarak [01:32-01:54] aralığını seçer; TimeLens bunu [00:12-00:58]'e iyileştirir. VLM sentezi 1.4 saniyede tamamlanır. Yanıt "5 araba" der ve beş farklı zaman damgasında çerçeve önizlemeleri sunar. Kullanıcı tüm zaman damgalarına tıklayarak ilgili çerçeveleri görebilir.

## Ship It

`outputs/skill-video-qa.md` teslim edilen şeydir. Bir YouTube URL'si veya yüklenmiş video verildiğinde, boru hattı sahneleri indeksler ve zaman damgası alıntılarıyla soruları yanıtlar.

| Ağırlık | Ölçüt | Nasıl ölçülür |
|:-:|---|---|
| 25 | Zamansal temellendirme IoU | Holdout temellendirme kümesinde kesişim-bölü-birleşim |
| 20 | Soru-Cevap doğruluğu | NeXT-GQA ve özel 100-sorgu |
| 20 | Hazmetme çıktısı | Harcanan dolar başına video saati |
| 20 | Arayüz ve alıntı UX | Zaman damgası bağlantıları, küçük resim şeridi, çerçeveye-ata |
| 15 | Halüsinasyon oranı | Sayma ve eylem-türü doğruluğu ayrı olarak |
| **100** | | |

## Exercises

1. Altyazı geçişinde Gemini 2.5 Pro'yu Qwen3-VL-Max ile değiştirin. İnsan-puanlı 50-sahne örneğinde altyazı kalitesi deltasını raporlayın.

2. Sahne başına çerçeve gömmeyi çok-vektörlü yerine tek havuzlanmış vektöre indirgeyin. Geri getirme regresyonunu ölçün.

3. Bir "katı sayma" modu inşa edin: sentezleyici, her sayılan örneği bir zaman damgasıyla çıkarır ve kullanıcı doğrulamak için tıklar. Kullanıcı-doğrulamasının halüsinasyonu azaltıp azaltmadığını ölçün.

4. Hazmetme maliyetini kıyaslayın: üç VLM seçeneği boyunca saat-başına-dolar-video. Tatlı noktayı seçin.

5. Konuşmacı-kümelendirmeli transkript ekleyin: pyannote konuşmacı diarizasyonunu seste çalıştırın ve konuşmacı başına transkriptleri gömün. "Alice X hakkında ne dedi?" sorgularını gösterin.

## Key Terms

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|------|----------------------|----------------------------|
| Sahne segmentasyonu | "Çekim tespiti" | Videoyu çekim sınırlarında sahnelere kesmek |
| Çok-vektörlü endeks | "Altyazı + çerçeve + transkript" | Temsil başına adlandırılmış vektörlerle Qdrant koleksiyonu |
| Zamansal temellendirme | "Tam olarak ne zaman oldu" | Sorgu yanıtı için (başlangıç, bitiş) penceresini iyileştirmek |
| Çerçeve gömme | "Görsel temsil" | Bir anahtar-çerçevenin vektör gömmesi; sahne-görsel benzerliği için kullanılır |
| RRF füzyonu | "Resiprok sıra füzyonu" | Birden çok sıralanmış listeyi birleştirme stratejisi; klasik hibrit-geri getirme hilesi |
| Sayma halüsinasyonu | "Yanlış sayım" | VLM'lerin "kaç X" sorularında bilinen hata modu |
| ActivityNet-QA | "Video-Soru-Cevap kıyaslaması" | Uzun-form video Soru-Cevap doğruluk kıyaslaması |

## Further Reading

- [AI2 Molmo 2](https://allenai.org/blog/molmo2) — açık VLM kontrol noktaları
- [TimeLens (CVPR 2026)](https://github.com/TencentARC/TimeLens) — ölçekte zamansal temellendirme
- [Gemini Video long-context](https://deepmind.google/technologies/gemini) — hosted referans
- [VideoDB](https://videodb.io) — video için CRUD API referansı
- [Twelve Labs Marengo + Pegasus](https://www.twelvelabs.io) — ticari referans
- [TransNetV2](https://github.com/soCzech/TransNetV2) — sahne segmentasyon modeli
- [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) — klasik açık alternatif
- [ActivityNet-QA](https://arxiv.org/abs/1906.02467) — referans değerlendirme kıyaslaması
