# Edge Inference — Apple Neural Engine, Qualcomm Hexagon, WebGPU/WebLLM, Jetson

> Çekirdek edge kısıtı, hesaplama değil bellek bant genişliğidir. Mobil DRAM 50-90 GB/s'de oturur; veri merkezi HBM3 2-3 TB/s'yi aşar — 30-50x fark. Decode bellek-bağlıdır, dolayısıyla fark belirleyicidir. 2026'da manzara dört yola ayrılır. Apple M4/A18 Neural Engine, birleşik bellekle (CPU↔NPU kopyası yok) 38 TOPS'da tepe yapar. Qualcomm Snapdragon X Elite / 8 Gen 4 Hexagon 45 TOPS'a ulaşır. WebGPU + WebLLM, Llama 3.1 8B (Q4)'ü M3 Max'ta ~41 tok/s'de çalıştırır (yerelin kabaca %70-80'i); 17,6k GitHub yıldızı, OpenAI-uyumlu API, ~%70-75 mobil kapsama. NVIDIA Jetson Orin Nano Super (8GB) Llama 3.2 3B / Phi-3'ü sığdırır; AGX Orin, vLLM üzerinden gpt-oss-20b'yi ~40 tok/s'de çalıştırır; Jetson T4000 (JetPack 7.1) AGX Orin'in 2 katı. TensorRT Edge-LLM, EAGLE-3, NVFP4, chunked prefill'i destekler — 2026 CES'te Bosch, ThunderSoft, MediaTek tarafından gösterildi.

**Tür:** Öğrenme
**Diller:** Python (stdlib, oyuncak bant-genişliği-bağlı decode simülatörü)
**Önkoşullar:** Faz 17 · 04 (vLLM Serving Internals), Faz 17 · 09 (Üretim Kuantizasyonu)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Mobil LLM inference'ın neden bellek-bant-genişliği-bağlı olduğunu ve hesaplamanın neden ikincil olduğunu açıklayın.
- Dört edge hedefini (Apple ANE, Qualcomm Hexagon, WebGPU/WebLLM, NVIDIA Jetson) sıralayın ve her birini bir kullanım senaryosuyla eşleştirin.
- 2026 WebGPU kapsama boşluğunu (Firefox Android'i yakalıyor) ve Safari iOS 26 inişini adlandırın.
- Hedef başına bir kuantizasyon formatı seçin (ANE için Core ML INT4 + FP16, Hexagon için QNN INT8/INT4, tarayıcı için WebGPU Q4, Jetson Thor için NVFP4).

## Sorun

Bir müşteri cihaz-üstü bir sohbet botu istiyor: ses-öncelikli, varsayılan olarak özel, çevrimdışı çalışır. MacBook Pro M3 Max'te Llama 3.1 8B Q4 ~55 tok/s'de çalışır — iyi. iPhone 16 Pro'da aynı model 3 tok/s'de çalışır — iyi değil. Snapdragon 8 Gen 3'lü orta-seviye bir Android'de 7 tok/s. Chrome Android v121+ üzerinden tarayıcıda WebGPU ile 4-8 tok/s, cihaza bağlı.

Verim varyansı bir taşıma sorunu değildir. Bant genişliği farkı çarpı kuantizasyon formatı çarpı NPU'nun kullanıcı-uzayından erişilebilir olup olmadığıdır. 2026'da edge inference, dört farklı çözümü olan dört farklı sorundur.

## Kavram

### Bant genişliği gerçek tavan

Decode, her token için ağırlıkların tam setini okur. Q4'te bir 7B model 3,5 GB'dir. 50 GB/s'de 3,5 GB okumak 70 ms sürer — ~14 tok/s'lik teorik bir tavan. 90 GB/s'de (üst-seviye mobil DRAM) tavan ~25 tok/s'ye hareket eder. Bu sayının altında hiçbir hesaplama yardımcı olmaz.

Veri merkezi HBM3, 3 TB/s'de aynı 3,5 GB'yi 1,2 ms'de temizler — tavan 830 tok/s. Aynı model, aynı ağırlıklar. Farklı bellek alt sistemi.

### Apple Neural Engine (M4 / A18)

- 38 TOPS'a kadar. Birleşik bellek (CPU ve ANE aynı havuzu paylaşır) — kopyalama ek yükü yok.
- Core ML + `.mlmodel` derlenmiş modeller veya Metal Performance Shaders (MPS) üzerinden PyTorch ile erişim.
- Llama.cpp Metal arka ucu MPS kullanır, doğrudan ANE'yi değil; yerel ANE Core ML dönüşümü gerektirir.
- 2026'da iOS uygulamaları için en iyi pratik yol: INT4 ağırlıklar + FP16 aktivasyonlarla Core ML.

### Qualcomm Hexagon (Snapdragon X Elite / 8 Gen 4)

- 45 TOPS'a kadar. SoC'de CPU ve GPU ile entegre ancak ayrı bellek alanı.
- QNN (Qualcomm Neural Network) SDK ve AI Hub, PyTorch/ONNX'ten dönüşüm sağlar.
- Sohbet şablonları, Llama 3.2, Phi-3 hepsi AI Hub'da birinci-sınıf yapılar olarak gönderilir.

### Intel / AMD NPU'ları (Lunar Lake, Ryzen AI 300)

- 40-50 TOPS. Yazılım Apple/Qualcomm'un gerisinde kalıyor; OpenVINO iyileşiyor ama niş.
- Windows ARM copilot uygulamaları için en iyi; AMD/Intel masaüstlerinde yerel-öncelikli için yerel.

### WebGPU + WebLLM

- Modelleri tarayıcıda WebGPU bilgi işlem gölgelendiricileri aracılığıyla çalıştırın; kurulum yok.
- Llama 3.1 8B Q4, M3 Max'ta ~41 tok/s — aynı arka uç aracılığıyla yerelin kabaca %70-80'i.
- WebLLM'de 17,6k GitHub yıldızı; OpenAI-uyumlu JS API; Apache 2.0.
- 2026 kapsama: Chrome Android v121+, Safari iOS 26 GA, Firefox Android hâlâ yakalıyor. Genel ~%70-75 mobil kapsama.

### NVIDIA Jetson ailesi

- Orin Nano Super (8GB): Llama 3.2 3B, Phi-3'ü iyi tok/s'de sığdırır.
- AGX Orin: vLLM üzerinden gpt-oss-20b'yi ~40 tok/s'de çalıştırır.
- Thor / T4000 (JetPack 7.1): AGX Orin'in 2 katı performans, EAGLE-3 ve NVFP4 desteklenir.
- TensorRT Edge-LLM (2026), EAGLE-3 spekülatif decode, NVFP4 ağırlıklar, chunked prefill'i destekler — veri merkezi optimizasyonları edge'e taşınır.

### Hedef başına kuantizasyon seçimi

| Hedef | Format | Notlar |
|-------|--------|--------|
| Apple ANE | INT4 ağırlıklar + FP16 aktivasyonlar | Core ML dönüşüm yolu |
| Qualcomm Hexagon | QNN INT8 / INT4 | AI Hub dönüştürücüleri |
| WebGPU / WebLLM | Q4 MLC (q4f16_1) | `mlc_llm convert_weight` + derlenmiş `.wasm` kullanın; GGUF desteklenmez |
| Jetson Orin Nano | Q4 GGUF veya TRT-LLM INT4 | Bellek-bağlı |
| Jetson AGX / Thor | NVFP4 + FP8 KV | Edge-LLM yolu |

### Edge'de uzun-bağlam tuzağı

Llama 3.1'in 128K bağlamı bir veri merkezi özelliğidir. 8 GB RAM'li bir telefonda, 4 GB model + 32K token için 2 GB KV cache + işletim sistemi ek yükü = OOM. Edge dağıtımları, agresif KV kuantizasyonu (Q4 KV) kabul edilmedikçe bağlamı 4K-8K'te tutar.

### Ses öldüren uygulama

Sesli agent'lar gecikmeye duyarlıdır (ilk token < 500 ms). Yerel inference, ağ gecikmesini tamamen ortadan kaldırır. Konuşmadan-metin (Whisper Turbo varyantları edge'de çalışır) ile birleştirin ve edge inference üretim kalitesinde bir ses döngüsü olur.

### Hatırlamanız gereken sayılar

- Apple M4 / A18 ANE: 38 TOPS.
- Qualcomm Hexagon SD X Elite: 45 TOPS.
- WebLLM M3 Max: Llama 3.1 8B Q4'te ~41 tok/s.
- AGX Orin: vLLM üzerinden gpt-oss-20b'de ~40 tok/s.
- Veri merkezi-edge bant genişliği farkı: 30-50x.
- WebGPU mobil kapsama: ~%70-75 (Firefox Android geride).

## Kullan

`code/main.py`, edge hedeflerinde bant-genişliği-bağlı matematikten teorik decode verim tavanlarını hesaplar. Gözlemlenen kıyaslamalarla karşılaştırır ve bant genişliğinin nerede hesaplama değil darboğaz olduğunu vurgular.

## Üret

Bu ders `outputs/skill-edge-target-picker.md` üretir. Platform (iOS/Android/tarayıcı/Jetson), model ve gecikme/bellek bütçesi verildiğinde, bir kuantizasyon formatı ve dönüşüm boru hattı seçer.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Snapdragon 8 Gen 3'te (~77 GB/s bant genişliği) Q4'te 7B model için decode tavanını hesaplayın. Gözlemlenen 6-8 tok/s ile karşılaştırın — çalışma zamanı verimli mi?
2. WebGPU, Android'de Chrome v121+ gerektirir. Eski tarayıcılar için bir yedek tasarlayın — aynı OpenAI-uyumlu API aracılığıyla sunucu-tarafı.
3. iOS uygulamanızın 4K-bağlam akışı var. iPhone 16'da 4 GB aktif belleğin altında kalmak için hangi model/format kombinasyonu izin verir?
4. Jetson AGX Orin, gpt-oss-20b'yi 40 tok/s'de çalıştırır. Jetson Nano yalnızca 3B'yi sığdırır. Ürününüz her ikisini de hedefliyorsa, inference yığınını nasıl birleştirirsiniz?
5. "WebLLM 2026'da üretime hazır mı" tartışın. Kapsamayı, performansı ve Firefox Android boşluğunu alıntılayın.

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|----------------------|----------------------------|
| ANE | "Apple neural engine" | M-serisi ve A-serisi cihaz-üstü NPU; birleşik bellek |
| Hexagon | "Qualcomm NPU" | Snapdragon NPU; erişim için QNN SDK |
| WebGPU | "tarayıcı GPU'su" | W3C-standardize tarayıcı GPU API'si; Chrome/Safari 2026 |
| WebLLM | "tarayıcı LLM çalışma zamanı" | MLC-LLM projesi; Apache 2.0; OpenAI-uyumlu JS |
| Jetson | "NVIDIA edge" | Orin Nano / AGX / Thor / T4000 ailesi |
| TRT Edge-LLM | "edge TensorRT" | 2026 TensorRT-LLM'in edge portu; EAGLE-3 + NVFP4 |
| Birleşik bellek | "paylaşılan havuz" | CPU ve NPU aynı RAM'i görür; kopyalama ek yükü yok |
| Bant genişliği-bağlı | "bellek sınırlı" | Ağırlıkları okuyan saniye/byte ile gate'lenen decode |
| Core ML | "Apple dönüşümü" | ANE-yerel modeller için Apple çerçevesi |
| QNN | "Qualcomm yığını" | Qualcomm Neural Network SDK |

## İleri Okuma

- [On-Device LLMs State of the Union 2026](https://v-chandra.github.io/on-device-llms/) — manzara ve kıyaslamalar.
- [NVIDIA Jetson Edge AI](https://developer.nvidia.com/blog/getting-started-with-edge-ai-on-nvidia-jetson-llms-vlms-and-foundation-models-for-robotics/) — Orin / AGX / Thor.
- [NVIDIA TensorRT Edge-LLM](https://developer.nvidia.com/blog/accelerating-llm-and-vlm-inference-for-automotive-and-robotics-with-nvidia-tensorrt-edge-llm/) — 2026 edge port duyurusu.
- [WebLLM (arXiv:2412.15803)](https://arxiv.org/html/2412.15803v2) — tasarım ve kıyaslamalar.
- [Apple Core ML](https://developer.apple.com/documentation/coreml) — ANE-yerel dönüşüm.
- [Qualcomm AI Hub](https://aihub.qualcomm.com/) — Hexagon için önceden dönüştürülmüş modeller.
