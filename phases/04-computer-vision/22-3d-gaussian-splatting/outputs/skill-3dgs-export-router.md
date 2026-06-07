---
name: skill-3dgs-export-router
description: Aşağı akış görüntüleyici veya motor verildiğinde doğru 3DGS dışa aktarma biçimini (.ply / .splat / glTF KHR_gaussian_splatting / USD) seçin
version: 1.0.0
phase: 4
lesson: 22
tags: [3d-gaussian-splatting, dışa-aktarma, glTF, OpenUSD, işlem hattı]
---

# 3DGS Dışa Aktarma Yönlendiricisi

Bir aşağı akış hedefini doğru 3DGS dosya biçimiyle eşleyin. "Yüklenmiyor" hata ayıklamasında saatler kazandırır.

## Ne zaman kullanılır

- Bir 3DGS sahnesini eğittikten sonra, bir içerik işlem hattı ile paylaşmadan önce.
- Araştırma düzeyinde (.ply) ve üretim düzeyinde (glTF / USD) biçimler arasında seçim yaparken.
- İşlem hattı teslimi: çekim ekibi -> 3DGS mühendisi -> oyun tasarımcısı / VFX sanatçısı / web geliştiricisi.

## Girdiler

- `target_engine`: unreal | unity | omniverse | blender | vision_pro | three_js | babylon_js | cesium | playcanvas | supersplat
- `priority`: portability | file_size | quality_preservation
- `include_sh_degree`: 0 | 1 | 2 | 3

## Biçim kararı

| Hedef | Önerilen biçim | Neden |
|--------|----------------|-------|
| Unreal Engine (sanal prodüksiyon) | Volinga eklentisi veya glTF KHR_gaussian_splatting | Yerel Unreal SDK yolu |
| Unity (XR / oyun) | Aras-P Unity-GaussianSplatting eklentisi aracılığıyla .ply | Topluluk standardı Unity işlem hattı |
| NVIDIA Omniverse, Pixar araçları | OpenUSD 26.03 (UsdVolParticleField3DGaussianSplat) | Yerel USD prim türü |
| Apple Vision Pro | OpenUSD 26.03 | visionOS 2.x'e yerel |
| Blender | .ply + KIRI Engine eklentisi | Topluluk eklentisi ham splat'ları okur |
| Three.js web görüntüleyici | glTF KHR_gaussian_splatting veya .splat | Tarayıcı standardı, `GaussianSplats3D` ile çalışır |
| Babylon.js V9+ | glTF KHR_gaussian_splatting | V9 yerel destek ekledi |
| Cesium (CesiumJS 1.139+, Cesium for Unreal 2.23+) | glTF KHR_gaussian_splatting | Açık destek ile gönderildi |
| PlayCanvas | .splat | PlayCanvas yerel nicelleştirilmiş biçimi |
| SuperSplat (editör) | .ply veya .splat | İçe + dışa aktar |

## Nicelleştirme takasları

- `.ply` tam hassasiyet: en büyük dosya, kayıpsız, herhangi bir görüntüleyici.
- `.splat`: 4x-8x daha küçük, SH3 katsayılarında hafif kalite kaybı, PlayCanvas-ekosistemi standardı.
- glTF KHR: EXT_meshopt_compression aracılığıyla yapılandırılabilir; en yüksek uyumlulukla en küçük.
- USD: USDZ paketlemesi ile sıkıştırılmış; Apple işlem hatları için en küçük.

## Çıktı raporu

```
[export plan]
 target: <engine>
 format: <isim>
 sh degree: <0|1|2|3>
 compression: <none|meshopt|quantisation|usdz>
 expected size: <MB>
 compatible with: <görüntüleyici listesi>

[pipeline]
 1. source: <.ply from training>
 2. optional: SuperSplat cleanup pass
 3. convert: <tool + CLI or API call>
 4. package: <.gltf / .glb / .usd / .usdz / .splat / .ply>
 5. validate: <viewer sanity check>
```

## Kurallar

- SH3 katsayılarını asla sessizce çıkarmayın — bu, specular yansımaları görünür şekilde değiştirir.
- `priority == file_size` ise, `.splat` veya meshopt ile glTF önerin; kalite kaybı konusunda uyarın.
- Apple platformları için, 2026'da glTF yerine USD / USDZ tercih edin; USDZ birinci sınıf visionOS desteğine sahiptir.
- Hedef görüntüleyicinin 3DGS desteği standart öncesi ise (Şubat 2026 öncesi), `.ply` ve görüntüleyicinin özel yükleyicisini önerin; Khronos standardı glTF henüz tanınmayacaktır.
- Teslim etmeden önce dışa aktarılan dosyayı en az bir görüntüleyicide her zaman doğrulayın; nicelleştirme sırasında sessiz bozulma olur.
