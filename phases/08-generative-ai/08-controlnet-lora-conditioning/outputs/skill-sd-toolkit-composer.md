---
name: sd-toolkit-composer
description: Belirli bir girdi seti için bir SD / Flux temeli üzerinde ControlNet, LoRA ve IP-Adapter'ları oluştur
version: 1.0.0
phase: 8
lesson: 08
tags: [controlnet, lora, ip-adapter, difüzyon]
---

Bir görev (hedef görüntü), girdiler (istem, referans görüntü, poz / derinlik / karalama / bölütleme, özne kimliği) ve temel model (SDXL, SD3.5, Flux.1-dev) verildiğinde, aşağıdakileri üret:

1. ControlNet yığını. Hangi ControlNet'ler (canny / openpose / derinlik / karalama / bölütleme / lineart / tile), hangi ağırlıkta, hangi sırada. Ağırlıkların maksimum toplamı <= 1.5.
2. LoRA yığını. Adlandırılmış LoRA'lar, rank, alfa. Alfa > 1.5 olduğunda veya birden fazla LoRA aynı kavramı hedeflediğinde uyar.
3. IP-Adapter. Yok, düz veya FaceID varyantı; ağırlık tipik olarak 0.4-0.8.
4. Metin istemi + negatif istem. Anahtar kelime sırası, token bütçesi, negatif iskele.
5. Örnekleyici + CFG + tohum. Euler A / DPM-Solver++ / LCM; temele bağlı CFG ölçeği. Tekrarlanabilir tohum protokolü.
6. QA kontrol listesi. ControlNet sapması, LoRA aşırı doygunluğu, IP-Adapter kimlik sızıntısı, anatomi sorunları için görsel kontrol.

SD 1.5 LoRA'yı SDXL temeli üzerine istifleme (boyut uyumsuzluğu). Ağırlık 1.0 ile 3+ ControlNet çalıştırma (öznitelik çakışması). Kullanıcının SDXL veya Flux için GPU bütçesi varken SD 1.5 önerisini işaretle. 10 görüntüden az LoRA kimlik eğitimini muhtemelen aşırı öğrenme olarak işaretle.
