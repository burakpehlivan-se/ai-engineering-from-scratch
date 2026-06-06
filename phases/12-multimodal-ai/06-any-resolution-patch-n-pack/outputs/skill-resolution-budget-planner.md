---
name: resolution-budget-planner
description: Karışık en boy oranlı bir VLM iş yükü için kare-yeniden-boyutlandırma, AnyRes, M-RoPE ve NaFlex arasında seçim yapın ve görev başına token bütçesi planı yayınlayın.
version: 1.0.0
phase: 12
lesson: 06
tags: [vlm, patch-n-pack, naflex, anyres, m-rope, token-budget]
---

Bir iş yükü -- VLM'in göreceği görüntülerin bir açıklaması (OCR dokümanları, grafikler, UI ekran görüntüleri, doğal fotoğraflar, video kareleri) ve toplam istek başına token bütçesi -- verildiğinde, görüntü sınıfı başına bir çözünürlük stratejisi seçin ve çalıştırılabilir bir yapılandırma üretin.

Üretin:

1. Görüntü sınıfı başına strateji. Beyan edilen her sınıf (OCR, grafik, UI, fotoğraf, video-kare) için {kare-yeniden-boyutlandırma, AnyRes, M-RoPE, NaFlex}'ten birini seçin. Görevin çözünürlük hassasiyetini belirterek tek cümleyle gerekçelendirin.
2. Görüntü başına token bütçesi. min_pixels, max_pixels (Qwen2.5-VL tarzı) ve seçilen stratejide beklenen dizi uzunluğunu dahil edin. Herhangi bir tek görüntü LLM bağlamının %40'ını aşarsa işaretleyin.
3. Toplu paketleme planı. İstekler toplu olarak işleniyorsa, `cu_seqlens` (FlashAttn varlen), yoğun blok-köşegen maske veya toplu-olmayan tek-görüntü çıkarımı kullanılıp kullanılmayacağını belirtin. Toplu en boy oranları 2x'ten fazla değiştiğinde varlen'ın FLOP tasarrufunu not edin.
4. Kodlayıcı önerisi. Karışık iş yükleri için SigLIP 2 NaFlex; ajan UI'ları için Qwen2.5-VL yerel; donmuş-kodlayıcı dağıtımları için CLIP-336 + AnyRes; yalnızca fotoğraf yolları için ham 224 ViT.
5. Başarısızlık modu alarmları. Seçilen yapılandırmada görüntü başına token'lar; 30 tok/s prefill'de gecikme maliyeti; bağlam-doluluk yüzdesi; tipik OCR kıyaslamalarında kare-yeniden-boyutlandırmaya karşı beklenen doğruluk farkı.

Sert reddetmeler:
- Kullanıcının hangi kıyaslama sayısını kaybedeceğini belirtmeden OCR veya grafik görevleri için kare-yeniden-boyutlandırma önermek.
- LLM'in izin verdiğinden daha fazla token üreten bir strateji önermek. Her zaman beyan edilen bağlam penceresine karşı bütçeleyin.
- AnyRes'i evrensel cevap olarak ele almak -- çarpımsal döşeme ek yükü, bir görüntü kodlama bitmeden LLM bağlamını aşabilir.

Ret kuralları:
- Kullanıcının beyan edilen token bütçesi görüntü başına 256 token'ın altındaysa, yalnızca fotoğraf-sadece anlamsal görev dışında bir şey için reddedin -- hiçbir havuzlama miktarı o bütçede OCR doğruluğunu kurtarmaz.
- Kullanıcı, kodlayıcıda ViT register token'ları olmadan yoğun-tahmin çıktıları (segmentasyon, derinlik) istiyorsa, reddedin ve register'lar etkinleştirilmiş DINOv2 / SigLIP 2'ye işaret edin.
- Kullanıcının LLM bağlamı 8k'dan azse ve iş yükü doküman veya ekran görüntüleri içeriyorsa, reddedin ve daha büyük bir bağlam veya bir OCR-önce işlem hattı önerin.

Çıktı: Sınıf başına strateji tablosu, toplu paketleme planı, kodlayıcı önerisi ve alarm listesi ile tek sayfalık bir bütçe planı. Takip için ilgili arXiv makalesi ile bitirin -- NaViT için 2307.06304, SigLIP 2 / NaFlex için 2502.14786, Qwen2.5-VL için 2502.13923.
