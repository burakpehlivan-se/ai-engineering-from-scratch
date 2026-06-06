---
name: edge-target-picker
description: Cihaz, model ve gecikme bütçesi verildiğinde bir uç çıkarım hedefi (Apple ANE, Qualcomm Hexagon, WebGPU/WebLLM, NVIDIA Jetson) ve eşleşen kuantizasyon biçimi seç.
version: 1.0.0
phase: 17
lesson: 12
tags: [edge, ane, hexagon, webgpu, webllm, jetson, core-ml, qnn, nvfp4]
---

Dağıtım platformu (iOS, Android, tarayıcı, robotik/otomotiv/uç sunucu), model ve gecikme/bellek bütçesi verildiğinde bir uç hedef önerisi üret.

Üretilecekler:

1. **Hedef.** Belirli NPU/GPU'yu adlandır (ANE, Hexagon, WebGPU, Jetson Orin Nano / AGX / Thor). Platformla ve 2026 çalışma-zamanı kapsamıyla gerekçelendir.
2. **Bant genişliği tavanı.** Teorik decode tavanını hesapla: bandwidth_GB_s / model_size_GB. Kullanıcının tok/s gereksinimiyle karşılaştır. Tavan gereksinimin altındaysa, reddet veya daha küçük bir model / daha sıkı kuantizasyon öner.
3. **Kuantizasyon biçimi.** Q4 GGUF (tarayıcı/uç CPU), Core ML INT4 + FP16 (ANE), QNN INT8/INT4 (Hexagon) veya NVFP4 + FP8 KV (Jetson Thor / Edge-LLM) seç.
4. **Dönüşüm boru hattı.** Tam dönüştürücüyü adlandır (Core ML converter, Qualcomm AI Hub, MLC-LLM for WebLLM, TensorRT-LLM Edge compiler).
5. **Bağlam bütçesi.** Cihaz RAM'inde ağırlıkların yanında sığan azami bağlamı belirt. Uzun-bağlam kullanım senaryoları için KV kuantizasyonu (Q4 KV) belirt veya reddet.
6. **Geri düşüş.** Cihaz yetersiz olduğunda veya WebGPU kullanılamadığında (Firefox Android, eski tarayıcılar), aynı OpenAI-uyumlu arayüzle sunucu-tarafı API geri düşüşünü belirt.

**Hard rejects (zorunlu redler):**
- Bant genişliği tavanının üstünde tok/s vaat etmek. Reddet — fizik.
- 2026'da ANE'yi Core ML dışı bir çalışma-zamanı üzerinden hedeflemek. Yalnızca Core ML ANE'yi yerel olarak açığa çıkarır.
- WebGPU'nun her tarayıcıda olduğunu varsaymak. 2026 kapsamı mobilde ~%70-75; her zaman geri düşüşü belirt.

**Reddetme kuralları:**
- Model >6 GB ise ve hedef bir telefon (4-8 GB RAM) ise, reddet — önce daha küçük bir model veya agresif kuantizasyon öner.
- İstek iPhone üzerinde 7B modelde 128K bağlam ise, reddet — cihaz RAM'i Q4 KV artı kayan-pencere dikkati olmadan sığdıramaz.
- Dağıtım Android üzerinden WebGPU ile uzun-bağlam akışı gerektiriyorsa ve kullanıcı Firefox desteği istiyorsa, reddet ve Chrome veya sunucu geri düşüşü zorunlu kıl.

**Çıktı:** Hedef, tavan, kuantizasyon, dönüştürücü, bağlam bütçesi, geri düşüş adlandıran tek sayfalık bir plan. Tek bir metrikle bitir: hedef filodaki en kötü-durum cihazda gözlemlenen tok/s.
