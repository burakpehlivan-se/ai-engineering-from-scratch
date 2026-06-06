# Video-Dil Modelleri: Zamansal Token'lar ve Yer Belirleme (Temporal Grounding)

> Video fotoğraf yığını değildir. 5 saniyelik bir klip, bir görüntü modelinin temsil edemeyeceği nedensel sıralama, eylem fiilleri ve olay zamanlaması içerir. Video-LLaMA (Zhang ve ark., Haziran 2023) sesli-görsel yer belirlemeli (grounding) ilk açık video-LLM'i piyasaya sürdü. VideoChat ve Video-LLaVA paterni ölçeklendirdi. 2025'e kadar Qwen2.5-VL'nin TMRoPE'si sınırlı özel modellerle farkı kapattı. Her sistem zamansal token'ları farklı çözdü — klip başına Q-former, kare havuzlama (pooling), token başına TMRoPE. Bu ders paternleri okur, uniform-vs-dynamic kare örnekleme (frame sampler) oluşturur ve zamansal yer belirleme görevlerinde değerlendirir.

**Tür:** İnşa Et
**Diller:** Python (stdlib, kare örnekleme + zamansal yer belirleme değerlendiricisi)
**Ön koşullar:** Faz 12 · 08 (LLaVA-OneVision)
**Süre:** ~180 dakika

## Öğrenme Hedefleri

- Zamansal konumsal kodlamanın (temporal positional encoding) görüntü VLM performansını vision encoder'dan bağımsız olarak nasıl değiştirdiğini açıklayın.
- Uniform, dynamic-FPS ve olay driven kare örnekleme yöntemlerini token/saniye ve yer belirleme doğruluğu açısından karşılaştırın.
- Video-LLaMA'daki klip başına Q-former, Video-LLaVA'daki kare havuzlaması ve Qwen2.5-VL'deki token başına M-RoPE tasarımlarını karşılaştırın.
- Dört video benchmark'ını adlandırın: VideoMME, TempCompass, EgoSchema, Video-MMMU.

## Problem

30 FPS'de 1 dakikalık video 1800 karedir. Kare başına 196 görsel token ile (224'te ViT-B) bu 352k token'dır — 2024 dönemi LLM bağlamından (context) daha büyüktür.

Üç azaltma stratejisi vardır:

1. Kareden alt-örnekleme (subsample) (içeriğe bağlı olarak 1-8 FPS).
2. Her karenin patch token'larının agresif havuzlanması (3x3 veya 4x4 bilinear pool).
3. 16 karelik bir klibi alan ve 64 token üreten bir Q-former aracılığıyla sıkıştırma.

Her taviz farklıdır. Alt-örnekleme zamansal ayrıntıyı kaybeder. Havuzlama uzamsal ayrıntıyı kaybeder. Q-former her ikisinden biraz kaybeder ancak token tasarrufu sağlar.

Zamansal konum kodlama diğer eksendir: model 5. karenin 6. kareden önce geldiğini nasıl bilir? Seçenekler arasında basit 1D zamansal RoPE (Video-LLaMA), öğrenilmiş zamansal embedding'ler (Video-LLaVA) ve TMRoPE (Qwen2.5-VL, tam 3D) bulunur.

## Kavram

### Video-LLaMA: klip başına Q-former + ses dalı

Video-LLaMA (2023) ilk açık video-LLM'iydi. Mimari:

- 2 FPS'de 16 karelik klipler (yani 8 saniye).
- Kare başına ViT özellikleri → tüm 16 kare üzerinden çapraz dikkat (cross-attends) kılan Video Q-former → 32 öğrenilmiş sorgu → LLM.
- Paralel ses dalı: dalga formu → ImageBind ses encoder'ı → Audio Q-former → 32 sorgu → LLM.

Güçlü yönü: sesli-görsel ortak çıkarım. Zayıf yönü: sabit klip uzunluğu, keyfi zaman yer belirleme yok.

### VideoChat ve Video-LLaVA

VideoChat, Video-LLaMA fikrini korudu ancak sesi bıraktı ve basitleştirdi. Video-LLaVA (Lin ve ark., 2023) tek bir görsel encoder'ı hem görüntüler hem video kareleri üzerinde eğitti ("projeksiyondan önce hizalama"), birleşik bir temsil verdi. Her ikisi de dondurulmuş CLIP encoder + MLP + LLM'dir.

Uzun videoyu hiçbiri işleyemez. Her ikisi de 8-16 karelik sistemlerdir.

### Qwen2.5-VL ve TMRoPE

Qwen2.5-VL, TMRoPE'yi tanıttı — Zamansal-Modallıklı Döndürme Konum Yerleştirme (Temporal-Modality Rotary Position Embedding). Her patch token'ı, t'nin gerçek zaman damgası (kare dizini değil) olduğu (t, h, w) konumunu taşır.

Basit zamansal embedding ile temel farklar:

- Mutlak zaman, dizin değil. Model "4.2 saniyede" görür, "15. karede" değil.
- Token başına döndürme, klip başına değil. Her görsel token zaman damgasına göre bağımsız döner.
- Dinamik FPS ile uyumlu. Burada 2 FPS, orada 4 FPS ile örneklerseniz TMRoPE eşitsiz aralıkları doğal olarak işler.

TMRoPE "hangi saniyede kedi atlıyor?" sorgularını mümkün kılar. Model "4.2 saniyede" yanıtını verebilir. Video-LLaMA sadece "klibin başında" diyebilirdi.

### Kare örnekleme stratejileri

Uniform: süreye eşit aralıklarla N kare örnekle. Basit, hareket zirve kayıplarına neden olur.

Dinamik FPS: hareket yoğunluğuna göre uyarlanır. Optik akış veya kare farklandırması, daha yoğun örnekleme için yüksek hareketli bölümleri seçer. Qwen2.5-VL bununla eğitilir.

Olay driven: hafif bir algılayıcı çalıştırın, eylemin olduğu yerde daha fazla örnekle. VideoAgent tarafından kullanılır.

Anahtar kare + bağlam: çekim sınırlarında + birkaç komşu karede örnekle. Sinematik içerik için kullanılır.

### Kare başına havuzlama

1 FPS'de ve kare başına 566 token ile 5 dakikalık bir klip 172.800 token'dır. Qwen2.5-VL-72B'nin 128k bağlamıyla mümkündür ancak pahalıdır.

3x3 bilinear pool, kare başına 64 token'a düşürür → 5 dakika için 19.200 token. Çoğu görev için ideal nokta.

Daha agresif havuzlayın (6x6 → kare başına 16 token), uzamsal ayrıntının daha az önemli olduğu ajan iş akışları için.

### Dört video benchmark'ı

- VideoMME: kapsamlı video anlama, kısa + orta + uzun.
- TempCompass: ince taneli zamansal çıkarma, "önce" / "sonra" soruları.
- EgoSchema: uzun vadeli birinci şahıs video.
- Video-MMMU: multimodal çok disiplinli video soruları.

Tam bir video-VLM değerlendirmesi dördünü de kapsar. Farklı eksenleri zorlarlar — TempCompass sıralama üzerinedir, EgoSchema 3+ dakikalık çıkarma üzerinedir, VideoMME süreleri kapsar.

### Yer belirleme çıktı formatları

Zamansal yer belirleme için çıktı formatları:

- Serbest metin: "Kedi 4 saniye civarında atlıyor." Kolay ayrıştırılır ancak kesin değildir.
- Yapılandırılmış JSON: `{"event": "jump", "start": 4.1, "end": 4.3}`. Qwen2.5-VL bunu eğitir.
- Token tabanlı: `<time>4.1</time>` gibi özel token'lar yanıtla iç içe. Qwen2.5-VL'nin dahili formatı.

Token tabanlı, aşağı akım kullanımı için en hassastır. Qwen2.5-VL'nin JSON çıktı formatı doğrudan ayrıştırılır.

### 2026 en iyi uygulaması

2026'da video VLM'leri için:

- Encoder: M-RoPE veya TMRoPE ile SigLIP 2 (Qwen2.5-VL).
- Kare örnekleme: dinamik FPS (harekete bağlı 1-4) ve maksimum kare sınırlaması.
- Kare başına havuzlama: 3x3 bilinear.
- Çıktı: zaman + olay alanlarıyla yapılandırılmış JSON.
- Benchmark'lar: genel için VideoMME + TempCompass; uzun vadeli için EgoSchema.

## Kullan

`code/main.py` şunları içerir:

- Uniform ve dinamik-FPS kare örnekleme (sampler)leri.
- Zaman T'de bir "ground truth" olayı ve model çıktısı verildiğinde toleransla doğruluk puanlayan oyuncak bir zamansal yer belirleme değerlendiricisi.
- Video-LLaMA (16 kare, Q-former), Video-LLaVA (8 kare, MLP), Qwen2.5-VL (dinamik FPS + TMRoPE) karşılaştırması.

## Teslim Et

Bu ders `outputs/skill-video-vlm-frame-planner.md` dosyasını üretir. Bir video görevi (izleme, eylem tanıma, zamansal yer belirleme, özetleme) verildiğinde kare örnekleme (sampler), havuzlama faktörü, çıktı formatı ve beklenen doğruluk düzeyini seçer.

## Alıştırmalar

1. 3 dakikalık bir yemek demosu için uniform mu dinamik FPS mi seçersiniz? Token sayısını kullanarak gerekçelendirin.

2. TMRoPE, basit bir zamansal embedding tablosunun yapamadığı şeyi tam olarak neyi ekler?

3. Bir VLM'in öğrenerek üretebileceği zamansal yer belirleme için bir JSON şeması yazın. Hata durumlarını dahil edin.

4. Video-LLaVA'nın "Projeksiyondan Önce Hizalama" Bölüm 3'ü okuyun. Bu, ayrı görüntü ve video encoder'ları eğitmekten neden daha iyidir?

5. VideoMME liderlik tablosuna göre, 2026 itibarıyla en iyi açık model ile en iyi özel model arasındaki fark nedir? Bu farkın ne kadarı zamansal kodlamaya atfedilebilir vs temel LLM ölçeğine?

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| Zamansal yer belirleme | "Zamana göre yapılandırılmış yanıtlar" | VLM, bir olayın gerçekleştiği belirli bir zaman aralığı çıktısı verir |
| TMRoPE | "Zaman-Multimodal RoPE" | Mutlak zaman damgalarına sahip 3B döndürme konumu, Qwen2.5-VL tarafından kullanılır |
| Dinamik FPS | "Hareket farkında örnekleme" | Yüksek hareketli bölümlerde daha fazla kare, statik bölümlerde daha az kare örnekleme |
| Kare havuzlama | "Kare başına uzamsal sıkıştırma" | LLM'den önce her kareden bilinear enterpolasyonla patch sayısını azaltma |
| Video Q-former | "Klip sıkıştırıcı" | N kareyi K öğrenilmiş sorguya eşleyen çapraz dikkat darboğazı (bottleneck) |
| VideoMME | "Video benchmark'ı" | Kapsamlı kısa/orta/uzun video benchmark'ı, 2500+ örnek |

## Daha Fazla Kaynak

- [Zhang ve ark. — Video-LLaMA (arXiv:2306.02858)](https://arxiv.org/abs/2306.02858)
- [Li ve ark. — VideoChat (arXiv:2305.06355)](https://arxiv.org/abs/2305.06355)
- [Lin ve ark. — Video-LLaVA (arXiv:2311.10122)](https://arxiv.org/abs/2311.10122)
- [Qwen Takımı — Qwen2.5-VL (arXiv:2502.13923)](https://arxiv.org/abs/2502.13923)
- [Lin ve ark. — VILA-1.5 (arXiv:2312.07533)](https://arxiv.org/abs/2312.07533)
