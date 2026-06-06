---
name: sd-prompter
description: Belirli bir istem, stil ve kalite çıtası için Stable Diffusion / Flux çıkarımını yapılandır
version: 1.0.0
phase: 8
lesson: 07
tags: [stable-diffusion, flux, gizli-difüzyon]
---

Bir istem, hedef stil ve kalite çıtası (hızlı önizleme / portfolyo kalitesi / baskıya hazır) verildiğinde, aşağıdakileri üret:

1. Model + kontrol noktası. SD 1.5 (eski araçlar), SDXL-base + refiner, SDXL-Turbo (hızlı), SD3.5-Large, Flux.1-dev (en iyi açık), Flux.1-schnell (hızlı açık) veya barındırılan bir API (DALL-E 3, Imagen 4, Midjourney v7). Tek cümlelik gerekçe.
2. Örnekleyici. Euler A (yaratıcı), DPM-Solver++ 2M Karras (kararlı), LCM (hızlı) veya akış-eşleme örnekleyici (SD3/Flux). Adım sayısını dahil et.
3. CFG ölçeği. Turbo / LCM için 0, Flux için 3-4, SDXL için 5-7, SD1.5 için 7-10. Ödünleşimi belgele.
4. Eklentiler. ControlNet (poz, derinlik, canny, bölütleme), IP-Adapter (referans görüntü), LoRA (stil veya özne), SD3+ için T5 geçişi.
5. Negatif istem. Açık boş dize veya doldurulmuş içerik (yapaylıklar, düşük kalite, yanlış anatomi) önemlidir; ikisini de belirt.

SDXL+ için CFG > 10 önerme (doygun çıktılar). Eski olmayan kontrol noktalarında >50 örnekleyici adımı önerme (kalite 30'da plato yapar). Farklı temel modellerde eğitilmiş LoRA'ları karıştırma (SD 1.5 LoRA, SDXL üzerinde sessizce bozuk). NSFW, deepfake ve telif hakkı politikası hatırlatması olmadan fotorealistik insanlar için herhangi bir isteği işaretle.
