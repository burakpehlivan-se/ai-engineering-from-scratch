---
name: 3d-pipeline
description: Girdi türü, çıktı biçimi ve kullanım durumuna göre bir 3B üretim veya yeniden yapılandırma hattı seç
version: 1.0.0
phase: 8
lesson: 12
tags: [3d, gaussian-splatting, nerf, mesh]
---

Girdiler (metin istemi / tek görüntü / birkaç görüntü / fotoğraf yakalama / video), hedef çıktı (mesh / Gauss splat / NeRF / nokta bulutu) ve kullanım durumu (gerçek-zamanlı render, oyun motoru, AR / VR, sinematik) verildiğinde, aşağıdakileri üret:

1. Hat. (a) Çok-görünümlü difüzyon + 3B uyum (SV3D, CAT3D + 3DGS), (b) doğrudan tek-çekim (LRM, TripoSR, InstantMesh), (c) PBR ile metin-üstü-mesh (Meshy 4, Rodin Gen-1.5, Hunyuan3D 2.0), (d) fotoğraf yakalama + 3DGS (Gsplat, Postshot, Scaniverse).
2. Temel model + barındırma. Adlandırılmış model + açık / barındırılan. Ticari kullanım için lisans uygunluğunu dahil et.
3. Yineleme bütçesi. İlk çıktıya beklenen süre, yineleme maliyeti, iyileştirme stratejisi.
4. Topoloji + malzemeler. Yeniden mesh geçişi gerekli mi? PBR kanal gereksinimleri (albedo, pürüzlülük, metalik, normal)? UV düzeni otomatik mi manuel mi?
5. Değerlendirme. Ayrılan görünümlerde SSIM, CLIP skoru, mesh su geçirmezliği, poli sayısı, doku çözünürlüğü.
6. Platform hedefi. Unity / Unreal / Blender / web (three.js / Babylon) / AR (USDZ / glb).

Mesh dönüşüm geçişi olmadan 3DGS'yi doğrudan oyun motoruna gönderme (çoğu motor splat'ı yerel olarak render etmez). Karmaşık eklemli karakterler için metin-üstü-3B önerme - bunun yerine rig'e duyarlı bir hat kullan. Alt akış araç NeRF'leri render edemediğinde yalnızca-NeRF çıktısını işaretle (çoğu DCC aracı).
