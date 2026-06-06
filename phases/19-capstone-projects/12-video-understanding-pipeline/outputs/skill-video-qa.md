---
name: video-qa
description: Sahne segmentasyonu, çok-vektörlü indeksleme, zamansal temellendirme ve zaman damgalı alıntılarla bir video anlama hattı inşa et
version: 1.0.0
phase: 19
lesson: 12
tags: [capstone, video, multimodal, gemini, qwen-vl, molmo, transnet, qdrant]
---

100 saatlik video verildiğinde, doğal dil sorularını (başlangıç, bitiş) zaman damgaları ve çerçeve önizlemeleriyle yanıtlayan bir alım hattı ve sorgu sistemi inşa et.

İnşa planı:

1. Videoları al (YouTube URL'leri veya MP4); gerekirse 720p'ye küçült.
2. TransNetV2 veya PySceneDetect ile sahne segmentasyonu; `[{sahne_kimliği, başlangıç_ms, bitiş_ms, anahtar_çerçeve_yolu}]` yay.
3. Kelime-düzeyinde zaman damgaları üreten Whisper-v3-turbo (faster-whisper) ile ASR; sahne başına dilimle.
4. Gemini 2.5 Pro veya Qwen3-VL-Max veya Molmo 2 ile VLM altyazılama; altyazı + çerçeve gömme yay.
5. Qdrant çok-vektörlü indeksi, sahne başına üç adlandırılmış vektörle (caption_emb, frame_emb, transcript_emb) ve yük {video_kimliği, sahne_kimliği, başlangıç_ms, bitiş_ms, anahtar_çerçeve_url}.
6. Sorgu: üç paralel yoğun sorgu; birleştirmek için karşılıklı sıra birleştirme; ilk k=5 sahne.
7. Zamansal temellendirme (TimeLens adaptörü veya VideoITG), en üst sahnede (başlangıç, bitiş) değerlerini iyileştirir.
8. VLM sentezi (Gemini 2.5 Pro) sorgu + ilk-3 sahne klibi + transkript ile; `(video_kimliği, başlangıç_ms, bitiş_ms)` alıntılarını zorunlu kıl.
9. ActivityNet-QA, NeXT-GQA ve 100-sorguluk el ile etiketlenmiş özel küme üzerinde değerlendir. Genel ve soru sınıfı (betimleyici, sayma, eylem türü) başına doğruluğu raporla.

Değerlendirme rubriği:

| Ağırlık | Kriter | Ölçüm |
|:-:|---|---|
| 25 | Zamansal temellendirme IoU | Elenmiş temellendirme kümesinde IoU |
| 20 | QA doğruluğu | NeXT-GQA ve 100-sorguluk özel küme |
| 20 | Alım verimi | Dolar başına indekslenen saat video |
| 20 | UI ve alıntı UX | Zaman damgası bağlantıları, küçük resim şeridi, çerçeveye-atla |
| 15 | Halüsinasyon oranı | Sayma ve eylem türü doğruluğu ayrı raporlanır |

Kesin redler:

- Sahne başına tek vektörü havuzlayan hatlar. Sınıf ayrımlarının görünmesi için çok-vektörlü zorunludur.
- (başlangıç, bitiş) alıntıları olmadan yanıtlar.
- Sayma/eylem alt kümesi dökümü olmadan tek bir genel doğruluk raporlama.
- Sahne çerçevelerini doğrudan almayan VLM sentezi (yalnızca metin girdileri görsel temellendirmeyi kaybeder).

Ret kuralları:

- Belirsiz lisans kökenli videoları sunmayı reddet; her video_kimliği için bir lisans etiketi zorunlu.
- Ölçülen verimin üzerindeki alım oranlarında "gerçek-zamanlı" yanıt iddia etmeyi reddet.
- Sayma/eylem halüsinasyon sayısını genel bir doğruluk rakamı içinde gizlemeyi reddet.

Çıktı: Sahne segmentasyonu + ASR + altyazılama hattını, çok-vektörlü Qdrant koleksiyonunu, zamansal temellendirme adaptörünü, zaman damgası derin bağlantılarıyla Next.js 15 görüntüleyiciyi, üç-kıyaslama değerlendirme sonuçlarını (ActivityNet-QA, NeXT-GQA, özel) ve gözlemlediğiniz üç sayma veya eylem türü başarısızlık sınıfını ve her birini azaltan erişim veya sentez değişikliğini adlandıran bir yazıyı içeren bir depo.
