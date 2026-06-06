# Üretim Kuantizasyonu — AWQ, GPTQ, GGUF K-quants, FP8, MXFP4/NVFP4

> Kuantizasyon formatu evrensel bir seçim değildir — donanım, sunma motoru ve iş yükünün bir fonksiyonudur. GGUF Q4_K_M veya Q5_K_M, llama.cpp ve Ollama aracılığıyla sunulan CPU ve edge'in sahibidir. GPTQ, vLLM içinde aynı temel üzerinde çoklu-LoRA'ya ihtiyaç duyduğunuzda kazanır. AWQ, Marlin-AWQ çekirdekleriyle 7B sınıfı modelde INT4'te en iyi Pass@1 ile ~741 tok/s sunar — veri merkezi üretimi için 2026 varsayılanı. FP8, Hopper, Ada ve Blackwell'te orta zemin olarak kalır — kayıpsıza yakın ve yaygın olarak desteklenir. NVFP4 ve MXFP4 (Blackwell mikro-ölçekleme) agresiftir ve blok başına doğrulama gerektirir. İki tuzak ekipleri ısırır: kalibrasyon veri seti dağıtım alanıyla eşleşmelidir ve KV cache, ağırlık kuantizasyonundan ayrıdır — "modelim artık 4 GB" AWQ dersi, üretim batch boyutlarında 10-30 GB KV cache'i unutur.

**Tür:** Öğrenme
**Diller:** Python (stdlib, formatlar arasında oyuncak bellek ve verim karşılaştırması)
**Önkoşullar:** Faz 10 · 13 (Kuantizasyon temelleri), Faz 17 · 04 (vLLM Serving Internals)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Altı üretim kuantizasyon formatunu ve 2026'daki tatlı noktalarını adlandırın.
- Donanım (CPU vs GPU, Hopper vs Blackwell), motor (vLLM, TRT-LLM, llama.cpp) ve iş yükü (rutin sohbet, akıl yürütme, çoklu-LoRA) verildiğinde bir format seçin.
- Seçilen bir format için tasarruf edilen ağırlık belleğini ve dokunulmamış KV cache'i hesaplayın.
- Alan trafiğinde kuantize edilmiş modelleri bozan kalibrasyon-veri-seti tuzağını adlandırın.

## Sorun

Kuantizasyon, belleği ve HBM bant genişliğini azaltır — tam olarak decode'un ihtiyaç duyduğu şey. 140B FP16 70B model 140 GB ağırlıktır. Ağırlıkları INT4'e (AWQ veya GPTQ) kuantize edin ve model 35 GB olur — KV cache için yerle birlikte tek bir H100'e sığar; bu önemlidir çünkü 2k bağlamda 128 eşzamanlı dizide, KV cache'in kendisi 20-30 GB'tır.

Ama kuantizasyon bedava değildir. Agresif kuantizasyon, özellikle akıl-yürütme-ağırlıklı görevlerde kaliteyi bozar. Farklı formatlar farklı motorlarla çalışır. Farklı donanımlar farklı hassasiyetleri yerel olarak destekler. 2026 format hayvanat bahçesi gerçektir ve birinin seçimini kopyalayamazsınız — yığınınıza göre seçmeniz gerekir.

## Kavram

### Altı format

| Format | Bit | Tatlı nokta | Motorlar |
|--------|-----|------------|----------|
| GGUF Q4_K_M / Q5_K_M | 4-5 | CPU, edge, dizüstü bilgisayarlar | llama.cpp, Ollama |
| GPTQ | 4-8 | vLLM'de çoklu-LoRA | vLLM, TGI |
| AWQ | 4 | Veri merkezi GPU üretimi | vLLM (Marlin-AWQ), TGI |
| FP8 | 8 | Hopper/Ada/Blackwell veri merkezi | vLLM, TRT-LLM, SGLang |
| MXFP4 | 4 | Blackwell çok-kullanıcılı | TRT-LLM |
| NVFP4 | 4 | Blackwell çok-kullanıcılı | TRT-LLM |

### GGUF — CPU/edge varsayılanı

GGUF bir dosya formatıdır, başlı başına bir kuantizasyon şeması değildir — K-quant varyantlarını (Q2_K, Q3_K_M, Q4_K_M, Q5_K_M, Q6_K, Q8_0) tek bir konteynerde paketler. Q4_K_M ve Q5_K_M üretim varsayılanlarıdır — 4-5 bit'te BF16'ya yakın kalite. llama.cpp, CPU üzerinde açık ara en hızlı inference motoru olduğu için CPU veya edge sunma için en iyi seçim.

vLLM'de verim cezası: 7B üzerinde ~93 tok/s — format GPU çekirdekleri için optimize edilmemiştir. Dağıtım hedefi CPU/edge olduğunda GGUF kullanın. Aksi takdirde kullanmayın.

### GPTQ — vLLM'de çoklu-LoRA

GPTQ, kalibrasyon geçişi olan eğitim-sonrası bir kuantizasyon algoritmasıdır. Marlin çekirdekleri onu GPU üzerinde hızlı yapar (Marlin olmayan GPTQ'ya kıyasla 2,6x hızlanma). 7B üzerinde ~712 tok/s.

Benzersiz kazanç: GPTQ-Int4, vLLM'de LoRA adaptörlerini destekler. Bir temel model artı 10-50 ince ayarlı varyant (her biri bir LoRA olarak) sunuyorsanız, GPTQ sizin yolunuzdur. NVFP4, 2026 başı itibarıyla henüz LoRA'yı desteklemiyor.

### AWQ — veri merkezi GPU varsayılanı

Aktivasyon-farkında ağırlık kuantizasyonu. Kuantizasyon sırasında en belirgin ~%1 ağırlığı korur. Marlin-AWQ çekirdekleri: naife kıyasla 10,9x hızlanma. 7B üzerinde ~741 tok/s, INT4 formatları arasında en iyi Pass@1.

Çoklu-LoRA'ya ihtiyacınız yoksa veya agresif Blackwell FP4'e (NVFP4) ihtiyacınız yoksa, yeni GPU sunma için AWQ seçin.

### FP8 — güvenilir orta

8-bit kayan nokta. Kayıpsıza yakın. Yaygın olarak desteklenir. Hopper Tensor Çekirdekleri FP8'i yerel olarak hızlandırır. Blackwell miras alır. FP8, kalite tartışılamaz olduğunda (akıl yürütme, tıbbi, kod üretimi) 2026 güvenli varsayılanıdır. Bellek tasarrufu INT4'ün yarısıdır, ancak kalite riski çok daha düşüktür.

### MXFP4 / NVFP4 — Blackwell agresif

Mikro-ölçekleme FP4. Ağırlıkların her bloğu kendi ölçek faktörüne sahiptir. Agresif ama Blackwell Tensor Çekirdeklerinde donanımla hızlandırılmış. Token başına byte'ları FP8'e kıyasla yarıya indirir — Faz 17 · 07'deki ekonomik kazanç.

Uyarılar:
- Henüz LoRA desteği yok (2026 başı).
- Akıl-yürütme-ağırlıklı iş yüklerinde kalite düşüşü görünür.
- Model başına eval setinizde doğrulayın.

### Kalibrasyon tuzağı

AWQ ve GPTQ bir kalibrasyon veri seti gerektirir — tipik olarak C4 veya WikiText. Alan modelleri (kod, tıbbi, hukuki) için, genel web metni üzerinde kalibre etmek, algoritmanın hangi ağırlıkları koruyacağı konusunda yanlış kararlar vermesine izin verir. HumanEval'da Pass@1 birkaç puan düşebilir.

Düzeltme: alan-içi veri üzerinde kalibre edin. Yüzlerce alan örneği genellikle yeterlidir. Göndermeden önce eval setinde test edin.

### KV cache tuzağı

AWQ, ağırlıkları 4 bit'e küçültür. KV cache ayrıdır ve FP16/FP8'de kalır. 70B model için AWQ ile:

- Ağırlıklar: ~35 GB (140 GB'den INT4).
- 128 eşzamanlı × 2k bağlamda KV cache: ~20 GB.
- Aktivasyonlar: ~5 GB.
- Toplam: ~60 GB — H100 80GB'ye sığar.

Naifçe "Modelimi 4 GB'ye kuantize ettim" diğer 30-50 GB'yi unutur. HBM'yi bütünsel olarak bütçeleyin.

Ayrı olarak, KV cache kuantizasyonu (FP8 KV veya INT8 KV), kendi ödünleşimleri olan ayrı bir seçimdir — doğrudan attention doğruluğunu etkiler ve bedava bir kazanç değildir.

### AWQ INT4 akıl yürütme için tehlikelidir

Zincirleme düşünce, matematik, uzun bağlamla kod üretimi — bunlar agresif kuantizasyondan görünür şekilde muzdariptir. AWQ INT4, MATH'ta ~3-5 puan kaybeder. Akıl-yürütme-ağırlıklı iş yükleri için, FP8 veya BF16 gönderin; bellek maliyetini kabul edin.

### 2026 seçim rehberi

- CPU/edge sunma: GGUF Q4_K_M. Bitti.
- GPU sunma, rutin sohbet, LoRA yok: AWQ.
- GPU sunma, çoklu-LoRA: Marlin ile GPTQ.
- Akıl-yürütme iş yükü: FP8.
- Blackwell veri merkezi, doğrulanmış kalite: NVFP4 + FP8 KV.
- Belirsiz: her aday formatta 1.000 örneklik bir eval çalıştırın.

## Kullan

`code/main.py`, bir dizi model boyutu için altı format üzerinden bellek ayak izini (ağırlıklar + KV + aktivasyonlar) ve göreli verimi hesaplar. KV cache'in nerede baskın olduğunu, ağırlık sıkıştırmanın nerede ödediğini ve FP8'in nerede güvenli seçim olduğunu gösterir.

## Üret

Bu ders `outputs/skill-quantization-picker.md` üretir. Donanım, model boyutu, iş yükü türü ve kalite toleransı verildiğinde, bir format seçer ve bir kalibrasyon/doğrulama planı üretir.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. 2k bağlamda 128 eşzamanlı 70B model için, her format için toplam HBM'yi hesaplayın. Hangi format tek bir H100 80GB'ye sığmanızı sağlar?
2. 7B kodlama modeliniz var. Bir format seçin ve gerekçelendirin. Kalite toleransı hakkında yanılıyorsanız, kurtarma yolu nedir?
3. Tıbbi alan modeli için AWQ'yu kalibre etmek için gereken kalibrasyon-veri-seti boyutunu hesaplayın. Neden daha fazla veri her zaman daha iyi değildir?
4. Marlin-AWQ çekirdek makalesini veya sürüm notlarını okuyun. Ham GPTQ 7B üzerinde ~712 tok/s'ye ulaşırken AWQ'nun 741 tok/s'ye neden ulaştığını üç cümlede açıklayın.
5. AWQ ağırlıklarını FP8 KV cache ile birleştirmek, KV'yi BF16'da tutmaya kıyasla ne zaman mantıklıdır?

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|----------------------|----------------------------|
| GGUF | "llama.cpp formatı" | K-quant varyantlarını paketleyen dosya formatı; CPU/edge varsayılanı |
| Q4_K_M | "Q4 K M" | 4-bit K-quant orta; GGUF üretim varsayılanı |
| GPTQ | "gee pee tee q" | Kalibrasyonla eğitim-sonrası INT4; vLLM'de LoRA'yı destekler |
| AWQ | "a w q" | Aktivasyon-farkında INT4; Marlin çekirdekleri; INT4'te en iyi Pass@1 |
| Marlin çekirdekleri | "hızlı INT4 çekirdekleri" | Hopper'ta INT4 için özel CUDA çekirdekleri; 10x hızlanma |
| FP8 | "sekiz-bit kayan" | Hopper/Ada/Blackwell'de güvenli hassasiyet varsayılanı |
| MXFP4 / NVFP4 | "mikro-ölçekleme dört" | Per-block ölçek faktörleriyle Blackwell 4-bit FP |
| Kalibrasyon veri seti | "kal veri" | Kuantizasyon parametrelerini seçmek için kullanılan girdi metni; alanla eşleşmeli |
| KV cache kuantizasyonu | "KV INT8" | Ağırlıklardan ayrı seçim; attention doğruluğunu etkiler |

## İleri Okuma

- [VRLA Tech — LLM Quantization 2026](https://vrlatech.com/llm-quantization-explained-int4-int8-fp8-awq-and-gptq-in-2026/) — karşılaştırmalı kıyaslamalar.
- [Jarvis Labs — vLLM Quantization Complete Guide](https://jarvislabs.ai/blog/vllm-quantization-complete-guide-benchmarks) — formatlara göre verim sayıları.
- [PremAI — GGUF vs AWQ vs GPTQ vs bitsandbytes 2026](https://blog.premai.io/llm-quantization-guide-gguf-vs-awq-vs-gptq-vs-bitsandbytes-compared-2026/) — format-format seçim.
- [vLLM docs — Quantization](https://docs.vllm.ai/en/latest/features/quantization/index.html) — desteklenen formatlar ve bayraklar.
- [AWQ paper (arXiv:2306.00978)](https://arxiv.org/abs/2306.00978) — orijinal AWQ formülasyonu.
- [GPTQ paper (arXiv:2210.17323)](https://arxiv.org/abs/2210.17323) — orijinal GPTQ formülasyonu.
