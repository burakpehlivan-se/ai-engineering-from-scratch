---
name: inference-optimizer
description: Yeni bir çıkarım dağıtımı için dikkat uygulaması, KV önbellek stratejisi, nicemleme ve spekülatif kod çözme seç
version: 1.0.0
phase: 7
lesson: 12
tags: [transformers, çıkarım, flash-attention, kv-cache]
---

Bir çıkarım dağıtımı (model adı + parametreleri, hedef donanım, eşzamanlılık, maksimum bağlam uzunluğu, gecikme SLO'su, çıktı hacmi hedefi) verildiğinde, aşağıdakileri üret:

1. Sunum yığını. vLLM (üretim varsayılanı), SGLang (token başına en düşük gecikme), TensorRT-LLM (NVIDIA optimal), llama.cpp (uç/CPU), MLX (Apple silikon). Tek cümlelik gerekçe.
2. Dikkat uygulaması. Flash Attention 2 (Ampere/Ada varsayılanı), Flash Attention 3 (Hopper), Flash Attention 4 (Blackwell, yalnızca ileri geçiş). Geri dönüşü belirt.
3. KV önbelleği. Veri tipi (fp16 varsayılan, destekleniyorsa fp8), sayfalanmış vs bitişik, önek önbellekleme açık/kapalı, paralel örnekleme için paylaşılan KV.
4. Nicemleme. fp16 / bf16 (varsayılan), int8 (yalnızca ağırlık), ağırlıklar için AWQ / GPTQ / GGUF. Aktivasyon nicemlemesi yalnızca kıyaslama yapıldıysa.
5. Ek hızlandırmalar. Spekülatif kod çözme (EAGLE 2 / Medusa / taslak model), sürekli parti (her zaman açık), parçalı ön doldurma (uzun-istemiş iş yükleri), tekrarlanan istemler varsa önek önbellekleme.

Eğitim için Flash Attention 4 dağıtma — başlangıçta yalnızca ileri geçiş yapar. Hedef görev üzerinde kalite etkisini kıyaslamadan fp8 KV önbelleği önerme. 32K+ bağlamda 70B+ modeli GQA olmadan yönetilemez KV önbelleğine sahip olarak işaretle. Tekrarlanan sistem istemleri olan herhangi bir agent/araç-çağırma dağıtımı için önek önbelleğinin açık olmasını zorunlu kıl.
