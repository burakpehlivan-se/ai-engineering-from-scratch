# 3D Üretimi

> 3D, 2D'den-3D'ye kaldıracın (leverage) en güçlü olduğu modalitedir. 2023 atılımı 3D Gaussian Splatting idi. 2024-2026 üretici hareketi, çoklu görünüm diffüzyonu (multi-view diffusion) + 3D yeniden yapılandırma üzerine katmanlar ekleyerek tek bir prompt veya fotoğraftan nesneler ve sahneler üretiyor.

**Tür:** Öğren
**Diller:** Python
**Ön koşullar:** Faz 4 (Görüntü), Faz 8 · 07 (Latent Diffusion)
**Süre:** ~45 dakika

## Problem

3D içerik acı vericidir:

- **Temsil.** Mesh'ler, nokta bulutları (point clouds), voxel ızgaraları, işaretli mesafe alanları (SDF'ler), sinirsel radyans alanları (NeRF'ler), 3D Gaussian'lar. Her birinin ödünleşimleri vardır.
- **Veri kıtlığı.** ImageNet 14M görsel içerir. En büyük temiz 3D veri seti (Objaverse-XL, 2023) ~10M nesne içerir, çoğu düşük kaliteli.
- **Bellek.** 512³ voxel ızgarası 128M voxeldir; yararlı bir sahne NeRF'i 1M örnek/ışın demeti (sample/ray) gerektirir. Üretim, yeniden yapılandırmadan daha zordur.
- **Denetim (supervision).** 2D bir görsel için pikselleriniz vardır. 3D için genellikle birkaç 2D görünümünüz vardır ve 3D'ye yükseltmeniz gerekir.

2026 stack'i iki sorunu ayrı tutar. Önce, bir diffüzyon modeliyle *2D çoklu görünüm görselleri* üretin. İkincisi, bu görsellere bir *3D temsil* (genellikle Gaussian splatting) sığdırın.

## Kavram

![3D üretimi: çoklu görünüm diffüzyonu + 3D yeniden yapılandırma](../assets/3d-generation.svg)

### Temsil: 3D Gaussian Splatting (Kerbl ve ark., 2023)

Bir sahneyi ~1M 3D Gaussian bulutu olarak temsil edin. Her birinin 59 parametresi vardır: konum (3), kovaryans (6 veya dördül (quaternion) 4 + ölçek 3), opaklık (1), küresel harmonikler (spherical harmonics) renk (derece 3'te 48, derece 0'da 3).

Renderlama = projeksiyon + alfa-birleştirme (alpha-compositing). Hızlı (4090'da 1080p'de ~100 fps). Türevlenebilir. Ground-truth fotoğraflara karşı gradyan inişiyle sığdırılır. Bir sahne tüketici GPU'sunda 5-30 dakikada sığdırılır.

2023-2024'te üzerine iki yenilik:
- **Üretici Gaussian splat'ları.** LGM, LRM, InstantMesh gibi modeller bir veya birkaç görüntüden doğrudan bir Gaussian bulutu tahmin eder.
- **4D Gaussian Splatting.** Dinamik sahneler için kare-ofsetli Gaussian'lar.

### Çoklu görünüm diffüzyonu

Önceden eğitilmiş bir görüntü diffüzyon modelini, bir metin promptundan veya tek bir görselden aynı nesnenin birden fazla tutarlı görünümünü üretecek şekilde fine-tune edin. Zero123 (Liu ve ark., 2023), MVDream (Shi ve ark., 2023), SV3D (Stability, 2024), CAT3D (Google, 2024). Genellikle nesnenin etrafında 4-16 görünüm çıktısı verir, Gaussian splatting veya NeRF aracılığıyla 3D'ye yükseltilir.

### Metinden-3D pipeline'ları

| Model | Girdi | Çıktı | Süre |
|-------|-------|--------|------|
| DreamFusion (2022) | metin | SDS aracılığıyla NeRF | Varlık başına ~1 saat |
| Magic3D | metin | mesh + doku | ~40 dk |
| Sjc / ProlificDreamer | metin | NeRF / mesh | ~30 dk |
| LRM (Meta, 2023) | görsel | triplane | ~5 sn |
| InstantMesh (2024) | görsel | mesh | ~10 sn |
| SV3D (Stability, 2024) | görsel | yeni görünümler | ~2 dk |
| CAT3D (Google, 2024) | 1-64 görsel | 3D NeRF | ~1 dk |
| TripoSR (2024) | görsel | mesh | ~1 sn |
| Meshy 4 (2025) | metin + görsel | PBR mesh | ~30 sn |
| Rodin Gen-1.5 (2025) | metin + görsel | PBR mesh | ~60 sn |
| Tencent Hunyuan3D 2.0 (2025) | görsel | mesh | ~30 sn |

2025-2026 yönü: oyun motorları için uygun PBR malzemelerle doğrudan metinden-mesh modelleri. Çoklu görünüm diffüzyonu ara adımı, genel nesneler için hâlâ en iyi performsanslı reçetedir.

### NeRF (bağlam için)

Neural Radiance Field (Mildenhall ve ark., 2020). Küçük bir MLP `(x, y, z, bakış yönü)` alır ve `(renk, yoğunluk)` çıktı verir. Işınlar boyunca entegre ederek renderlanır. Yeni-görünüm sentezinde (novel-view synthesis) mesh tabanlı yöntemleri kalite olarak yener, ancak renderlamak 100-1000 kat daha yavaştır. Çoğu gerçek zamanlı kullanım için Gaussian splatting tarafından geçildi, ancak araştırmada hâlâ baskın.

## İnşa Et

`code/main.py`, bir sentetik hedef görseli (düzgün bir gradyan) 2D Gaussian splat'ların toplamı olarak temsil eden oyuncak bir 2D "Gaussian splatting" sığdırması uygular. Hedefle eşleşecek şekilde konumları, renkleri ve kovaryansları gradyan inişiyle optimize eder. İki temel işlemi görürsünüz: ileri render (splat + alfa-birleştirme) ve gradyan inişiyle sığdırma.

### Adım 1: 2D Gaussian splat

```python
def gaussian_at(x, y, gaussian):
    px, py = gaussian["pos"]
    sigma = gaussian["sigma"]
    d2 = (x - px) ** 2 + (y - py) ** 2
    return math.exp(-d2 / (2 * sigma * sigma))
```

### Adım 2: splat'ları toplayarak render

```python
def render(image_size, gaussians):
    img = [[0.0] * image_size for _ in range(image_size)]
    for g in gaussians:
        for y in range(image_size):
            for x in range(image_size):
                img[y][x] += g["color"] * gaussian_at(x, y, g)
    return img
```

#### Açıklama

Gerçek 3D Gaussian splatting, Gaussian'ları derinliğe göre sıralar ve sırayla alfa-birleştirir. Bizim 2D oyunağımız yalnızca toplar.

### Adım 3: gradyan inişiyle sığdırma

```python
for step in range(steps):
    pred = render(size, gaussians)
    loss = mse(pred, target)
    gradients = compute_grads(pred, target, gaussians)
    update(gaussians, gradients, lr)
```

## Tuzaklar

- **Görünüm uyumsuzluğu.** 4 görünümü bağımsız üretirseniz ve nesne yapısında anlaşırlarsa, 3D sığdırma bulanık olur. Çözüm: paylaşılan attention ile çoklu görünüm diffüzyonu.
- **Arka yüz halüsinasyonu.** Tek görselden → 3D, görülmeyen tarafı uydurmak zorundadır. Kalite büyük ölçüde değişir.
- **Gaussian splat patlaması.** Kısıtlanmamış eğitim 10M splat'a kadar büyür ve aşırı öğrenir (overfit). Yoğunlaştırma + budama (densification + pruning) sezgisel yöntemleri (3D-GS orijinal makalesinden) şarttır.
- **Topoloji sorunları.** İzdüşümlü alanlardan (SDF'ler) elde edilen mesh'lerin genellikle delikleri veya kendi kendine kesişimleri vardır. Teslimattan önce bir yeniden meshleme çalıştırın (örn. blender'ın voxel remesh'i).
- **Eğitim verisi lisansı.** Objaverse karışık lisanslara sahiptir; ticari kullanım modele göre değişir.

## Kullan

| Görev | 2026 seçimi |
|-------|-------------|
| Fotoğraflardan sahne yeniden yapılandırma | Gaussian splatting (3DGS, Gsplat, Scaniverse) |
| Oyunlar için metinden-3D nesne | Meshy 4 veya Rodin Gen-1.5 (PBR çıktısı) |
| Görüntüden-3D | Hunyuan3D 2.0, TripoSR, InstantMesh |
| Az sayıda görüntüden yeni-görünüm sentezi | CAT3D, SV3D |
| Dinamik sahne yeniden yapılandırma | 4D Gaussian Splatting |
| Avatar / giyinmiş insan | Gaussian Avatar, HUGS |
| Araştırma / SOTA | Geçen hafta düşen her neyse |

Oyun veya e-ticaret pipeline'ında üretim 3D'si teslim etmek için: Meshy 4 veya Rodin Gen-1.5, doğrudan Unity / Unreal'a giden PBR mesh'ler üretir.

## Teslim Et

`outputs/skill-3d-pipeline.md` dosyasını kaydedin. Skill bir 3D brifingi (girdi: metin / bir görsel / birkaç görsel; çıktı: mesh / splat / NeRF; kullanım: render / oyun / VR) alır ve çıktı olarak şunları verir: pipeline (çoklu görünüm diffüzyonu + sığdırma veya doğrudan mesh modeli), taban model, yineleme bütçesi, topoloji işleme sonrası, gerekli malzeme kanalları.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi 4, 16, 64 Gaussian ile çalıştırın. Hedefe göre son MSE'yi raporlayın.
2. **Orta.** Renkli Gaussian'lara (RGB) genişletin. Yeniden yapılandırmanın hedef renk kalıbıyla eşleştiğini doğrulayın.
3. **Zor.** gsplat veya Nerfstudio kullanarak 50 fotoğraflık bir yakalamadan gerçek bir nesneyi yeniden yapılandırın. Sığdırma süresini ve çıkarılmış görünümlerdeki son SSIM'i raporlayın.

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| 3D Gaussian Splatting | "3DGS" | 3D Gaussian bulutu olarak sahne; türevlenebilir alfa-birleştirme renderı. |
| NeRF | "Sinirsel radyans alanı" | 3D bir noktada renk + yoğunluk outputlayan MLP; ışın entegrasyonuyla render. |
| Triplane | "Üç 2D düzlem" | 3D'yi üç 2D eksene hizalanmış özellik ızgarasına çarpanlı (factor); hacimselden daha ucuz. |
| SDS | "Skor distilasyon örnekleme (score distillation sampling)" | 2D-diffüzyon skorunu pseudo-gradyan olarak kullanarak 3D modeli eğitmek. |
| Çoklu görünüm diffüzyonu | "Birçok görünüm birden" | Tutarlı kamera görünümleri bir topu (batch) çıktı veren diffüzyon modeli. |
| PBR | "Fizik tabanlı render (physically-based rendering)" | Albedo, pürüzlülük, metallik, normal kanallarına sahip malzeme. |
| Yoğunlaştırma | "Splat'ları büyüt" | 3DGS eğitim sezgisel yöntemi: yüksek gradyan bölgelerinde splat'ları böl / klonla. |

## Üretim notu: 3D'nin henüz paylaşılan bir altyapısı yok

Görüntüden (latent diffüzyon + DiT) ve videodan (uzamsal-zamansal DiT) farklı olarak, 3D'nin 2026'da baskın bir çalışma zamanı (runtime) yoktur. Üretim karar ağacı temsile göre çatallaşır:

- **NeRF / triplane.** Çıkarım, ışın yürüyüşü (ray-marching) + her örnek için bir MLP ileri geçişi. 512² render milyonlarca MLP ileri geçişi gerektirir. Işın örneklerini agresif gruplandırın; SDPA/xformers uygulanır.
- **Çoklu görünüm diffüzyonu + LRM yeniden yapılandırması.** İki aşamalı pipeline. Aşama 1 (çoklu görünüm DiT) Ders 07'deki gibi bir diffüzyon sunucusudur. Aşama 2 (LRM transformer) görünümler üzerinde tek geçişli bir ileri geçiştir. Genel gecikme profili "diffüzyon + tek geçiş"tir — aşamaya göre hizmet temel taşlarını (primitives) buna göre seçin.
- **SDS / DreamFusion.** Varlık başına optimizasyon, çıkarım değil. İş istekleri (request handlers) değil, derleme işleri (build jobs).

Çoğu 2026 ürünü için doğru cevap, "istek üzerine çoklu görünüm diffüzyonu modeli çalıştırın, 3DGS'yi asenkron olarak yeniden yapılandırın, gerçek zamanlı görüntüleme için 3DGS'yi sunun" şeklindedir. Bu iş yükünü GPU-çıkarım sunucusu (hızlı) ve çevrimdışı optimize edici (yavaş) arasında temiz bir şekilde böler.

## Daha Fazla Kaynak

- [Mildenhall ve ark. (2020). NeRF: Representing Scenes as Neural Radiance Fields](https://arxiv.org/abs/2003.08934) — NeRF.
- [Kerbl ve ark. (2023). 3D Gaussian Splatting for Real-Time Radiance Field Rendering](https://arxiv.org/abs/2308.04079) — 3DGS.
- [Poole ve ark. (2022). DreamFusion: Text-to-3D using 2D Diffusion](https://arxiv.org/abs/2209.14988) — SDS.
- [Liu ve ark. (2023). Zero-1-to-3: Zero-shot One Image to 3D Object](https://arxiv.org/abs/2303.11328) — Zero123.
- [Shi ve ark. (2023). MVDream](https://arxiv.org/abs/2308.16512) — çoklu görünüm diffüzyonu.
- [Hong ve ark. (2023). LRM: Large Reconstruction Model for Single Image to 3D](https://arxiv.org/abs/2311.04400) — LRM.
- [Gao ve ark. (2024). CAT3D: Create Anything in 3D with Multi-View Diffusion Models](https://arxiv.org/abs/2405.10314) — CAT3D.
- [Stability AI (2024). Stable Video 3D (SV3D)](https://stability.ai/research/sv3d) — SV3D.
