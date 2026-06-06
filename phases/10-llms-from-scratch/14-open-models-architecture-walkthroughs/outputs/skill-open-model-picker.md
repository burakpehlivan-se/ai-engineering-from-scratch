---
name: open-model-picker
description: Belirli bir dağıtım hedefi için açık bir LLM ailesi, nicemleme ve çıkarım yığını seçin.
version: 1.0.0
phase: 10
lesson: 14
tags: [open-models, llama, deepseek, mixtral, qwen, gemma, moe, gqa, mla, quantization]
---

Belirli bir dağıtım hedefi (GPU türü, GPU başına VRAM, GPU sayısı, hedef bağlam uzunluğu, hedef p50/p99 gecikme, eşzamanlı isteklerin zirve noktası) ve bir görev profili (sohbet, kod, akıl yürütme, uzun bağlam getirme, araç kullanımı) verildiğinde, Ders 14'ten altı mimari düğmenin her biri hakkında açık akıl yürütmeyle birlikte bir açık model ve sunma yığını önerin.

Şunu üretin:

1. Model kısa listesi. Her biri toplam parametreler, aktif parametreler (MoE - Karışım Uzmanları farkındalığıyla), mimari bayraklar (norm / aktivasyon / konum / attention / MoE / bağlam) ve kısa listeye girmesinin tek nedeni ile birlikte üç aday.
2. Bellek bütçesi kontrolü. En iyi aday için: BF16'da ve seçilen nicelemede ağırlık belleği; hedef parti boyutu için hedef bağlamda KV cache; aktivasyon yedek alanı. Ağırlıklar + KV cache + aktivasyonlar mevcut VRAM'ı aşarsa öneriyi durdurun.
3. Nicemleme seçimi. GPTQ-4bit, AWQ-4bit, FP8 veya BF16. Görevin doğruluk hassasiyetine karşı gerekçelendirin (kod / matematik / akıl yürütme görevleri, sohbet veya getirmeden daha agresif nicelemeden daha büyük bir darbe alır).
4. Çıkarım yığını. vLLM, TensorRT-LLM, SGLang veya llama.cpp. Şuna karşı gerekçelendirin: sürekli toplu iş ihtiyacı, spekülatif kod çözme desteği, nicemleme formatı uyumluluğu ve tek düğüm vs çok düğüm topolojisi.
5. Verim sağlık kontrolü. GPU bellek bant genişliğine (kod çözme) ve TFLOP'a (ön dolgu) dayalı saniye başına ön dolgu tokeni ve saniye başına kod çözme tokeni tahminleri. Kod çözme verimi, hedefin eşzamanlı kullanıcı tabanının altındaysa öneriyi reddedin.
6. Geri dönüş. En iyi aday VRAM veya verim bütçesini aşarsa ikinci seçim. Her zaman bir tane adlandırın.

Sert redler:
- Aktarım veya agresif nicemleme olmadan tek bir 24GB tüketici GPU'da 30B üzeri yoğun modeller.
- Uzman paralel desteği olmayan bir sunma yığınında MoE modelleri.
- GQA veya MLA olmayan mimarilerde uzun bağlam (128k+) (KV cache patlar).
- Belirli model revizyonunu adlandırmayan herhangi bir öneri (örneğin, "Llama 3" değil, "Llama 3 8B Instruct v3.1").

Çıktı: Her karar için numaralandırılmış kanıtlarla birlikte model, nicemleme, yığını listeleyen tek sayfalık bir öneri. Seçimi çevirecek belirli yeteneği veya dağıtım parametresini adlandıran "şu durumda yeniden değerlendirmeye değer..." paragrafıyla bitirin.
