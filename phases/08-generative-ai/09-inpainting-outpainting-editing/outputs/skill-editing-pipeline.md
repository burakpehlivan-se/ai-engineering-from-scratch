---
name: editing-pipeline
description: Kaynak + düzenleme açıklamasından gönderilmeye hazır bir çıktıya görüntü düzenleme hattı planla
version: 1.0.0
phase: 8
lesson: 09
tags: [inpaint, outpaint, düzenleme, sam]
---

Kaynak görüntü, hedef düzenleme (X'i kaldır, Y'yi Z ile değiştir, tuvali genişlet, bölgeyi yeniden stillendir, mevsim / günün saatini değiştir) ve kalite çıtası (taslak / portfolyo / baskı) verildiğinde, aşağıdakileri üret:

1. Maske stratejisi. Açık fırça maskesi, SAM 2 tıklama / kutu istemi, metin ifadesinde Grounded-SAM veya RMBG (arka plan kaldırma için). Tek cümlelik gerekçe.
2. Temel model + mod. SD-Inpaint / SDXL-Inpaint / Flux-Fill / talimat düzenlemeleri için Flux-Kontext veya maske yoksa SDEdit gürültü seviyesi (0.3 / 0.6 / 0.9).
3. İstem iskelesi. Yalnızca yeni içeriği değil, düzenlemeden sonraki tüm görüntüyü tanımla. Negatif istemi dahil et.
4. CFG + güç + yumuşatma. Maske yumuşatma 8-16 px; SDXL-inpaint için CFG ~5-7, Flux için 3-4. Tam yeniden üretim için güç 0.8-1.0, koruma için 0.3-0.5.
5. Korumalar. NSFW / deepfake / ticari marka algılama kancası, yüz değiştirme politikası geçidi, geri alınabilirlik (maskeyi ve tohmu kaydet).

Açık politika kontrolü olmadan tanınabilir bir kamu figürü üzerinde kimlik düzenlemeleri gönderme. Orijinal tuvalin en az %30'unu çapa olmadan görüntü dışına genişletme (çok az bağlam modelin halüsinasyon kurmasına neden olur). "Özneyi koru" sadakat hedefi ve t/T > 0.7 olan herhangi bir SDEdit çalıştırmasını muhtemel uyumsuzluk olarak işaretle.
