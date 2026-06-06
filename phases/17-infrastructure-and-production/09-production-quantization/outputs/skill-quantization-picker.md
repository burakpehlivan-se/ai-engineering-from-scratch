---
name: quantization-picker
description: Donanım, motor, iş yükü ve kalite toleransı verildiğinde 2026 kuantizasyon biçimini seç ve bir kalibrasyon + doğrulama planı üret.
version: 1.0.0
phase: 17
lesson: 09
tags: [quantization, awq, gptq, gguf, fp8, nvfp4, calibration]
---

Donanım (CPU / H100 / H200 / B200 / GB200, sayıyla birlikte), motor (llama.cpp / vLLM / TRT-LLM / SGLang), model (boyut + görev türü — rutin sohbet / akıl-yürütme / kod / çok-LoRA) ve kalite toleransı (HumanEval / MATH / MMLU üzerinde N puanlık düşüşü kaldırabilir) verildiğinde, bir kuantizasyon biçimi seç ve bir doğrulama planı üret.

Üretilecekler:

1. **Biçim önerisi.** Şunlardan biri: GGUF Q4_K_M, GGUF Q5_K_M, GPTQ-Int4 + Marlin, AWQ-Int4 + Marlin, FP8, NVFP4 + FP8 KV veya yığılmış bir kombinasyon. Karar ağacıyla gerekçelendir: CPU → GGUF; akıl-yürütme → FP8; vLLM üzerinde çok-LoRA → GPTQ; rutin GPU sohbeti → AWQ; Blackwell doğrulanmış → NVFP4.
2. **Bellek bütçesi.** Ağırlıklar + KV önbellek (rapor edilen eşzamanlılık × bağlam'da) + aktivasyonlar. Hedef GPU'ya sığdığını doğrula veya çoklu-GPU gereksinimini belirt.
3. **Kalibrasyon planı.** Veri kümesi kaynağı (AWQ/GPTQ için alan-eşleşmiş; son çare olarak genel C4/WikiText). Örnek sayısı (alan için 500-2000). Doğrulama kümesi (kalibrasyon havuzundan %10 ayrılmış).
4. **Doğrulama planı.** Göreve eşleşmiş eval kümesi: kod için HumanEval, akıl-yürütme için MATH/MMLU, sohbet için MT-Bench. Taban çizgisi BF16 vs kuantize. Düşüş ≤ kalite toleransı ise yayınla.
5. **KV önbellek kararı.** Ağırlık kuantizasyonundan ayrı. Akıl-yürütme için FP8 KV öner; dikkat doğruluğu marjinalse BF16 KV; INT8 KV yalnızca doğrulamadan sonra.
6. **Geri alma yolu.** BF16/FP8 ağırlıkları diskte tut; üretim kalitesi düşerse geri dönmek için işaretle.

**Hard rejects (zorunlu redler):**
- Akıl-yürütme-ağırlıklı iş yüklerinde eval-kümesi doğrulaması olmadan NVFP4 ağırlıkları önermek.
- Alan modelleri için genel web verisinde kalibrasyon. Her zaman alan-içi kullan.
- HBM bütçesinden KV önbelleği unutmak. Her zaman kalem kalem göster.
- Çekirdekleri adlandırmadan (Marlin-AWQ vs düz AWQ 10x) verim sayılarını iddia etmek.

**Reddetme kuralları:**
- İş yükü doğası gereği kalite-marjinalse (açık-uçlu yaratıcı üretim, uç-durum akıl-yürütme), agresif INT4'ü reddet. FP8 veya BF16'da kal.
- Motor llama.cpp ise, GGUF dışında herhangi bir biçimi reddet. Biçimi motorla eşleştirmek masa başı ücretidir.
- Kullanıcı 1.000-örnek bir eval çalıştıramıyorsa, reddet. Üretimde kör kuantizasyon yok.

**Çıktı:** Seçili biçim, HBM bütçesi, kalibrasyon planı, doğrulama planı, KV önbellek kararı ve geri alma yolu listeleyen tek sayfalık bir kuantizasyon seçimi. Anahtar riske bağlı olarak eval-kümesi deltası, doruk eşzamanlılık altında KV önbellek baskısı veya gerçek toplu iş boyutunda verimden birini adlandıran bir "sırada ne ölçülecek" paragrafıyla bitir.
