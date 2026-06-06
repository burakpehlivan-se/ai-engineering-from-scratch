# Kendi-Kurulumlu Sunum Seçimi — llama.cpp, Ollama, TGI, vLLM, SGLang

> Dört motor 2026'da kendi-kurulumlu çıkarıma (inference) hâkimdir. Donanıma, ölçeğe ve ekosisteme göre seçin. **llama.cpp** CPU'da en hızlıdır — en geniş model desteği, nicemleme (quantization) ve iş parçacıklandırma (threading) üzerinde tam kontrol. **Ollama** geliştirici-dizüstü bilgisayar tek-komut kurulumudur, llama.cpp'den ~%15-30 daha yavaş (Go + CGo + HTTP serileştirme), üretim benzeri yük altında 3 kat throughput farkı. **TGI, 11 Aralık 2025'te bakım moduna girdi** — yalnızca hata düzeltmeleri, vLLM'den ~%10 daha yavaş ham throughput ama tarihsel olarak en iyi gözlemlenebilirlik ve HF-ekosistemi bütünleşmesi. Bu bakım durumu, onu uzun vadeli riskli bir bahis yapar — yeni projeler için SGLang veya vLLM daha güvenli varsayılanlardır. **vLLM** genel-amaçlı üretim varsayılanıdır — v0.15.1 (Şubat 2026) PyTorch 2.10, RTX Blackwell SM120, H200 optimizasyonu ekler. **SGLang** ajan çoklu-tur (multi-turn) / önek-ağırlıklı uzmanıdır — üretimde 400.000+ GPU (xAI, LinkedIn, Cursor, Oracle, GCP, Azure, AWS). Donanım kısıtları: yalnızca CPU → yalnızca llama.cpp. AMD / NVIDIA-dışı → yalnızca vLLM (TRT-LLM NVIDIA-kilidi). 2026 pipeline kalıbı: geliştirme = Ollama, staging = llama.cpp, üretim = vLLM veya SGLang. Boyunca aynı GGUF/HF ağırlıkları.

**Tür:** Öğren
**Diller:** Python (stdlib, motor-karar ağacı yürüyücüsü)
**Önkoşullar:** Tüm Phase 17 motor dersleri (04, 06, 07, 09, 18)
**Süre:** ~45 dakika

## Öğrenme Hedefleri

- Donanım (CPU / AMD / NVIDIA Hopper / Blackwell), ölçek (1 kullanıcı / 100 / 10.000) ve iş yükü (genel sohbet / ajan / uzun-bağlam) verildiğinde bir motor seçin.
- 2026 TGI bakım modu durumunu (11 Aralık 2025) sayın ve yeni projeleri neden vLLM veya SGLang'a doğru yönlendirdiğini açıklayın.
- Boyunca aynı GGUF veya HF ağırlıklarını kullanarak geliştirme/staging/üretim pipeline'ını açıklayın.
- "Yalnızca CPU"nun llama.cpp'yi zorladığını ve "AMD"nin TRT-LLM'yi neden dışladığını açıklayın.

## Problem

Ekibiniz yeni bir kendi-kurulumlu LLM projesi başlatıyor. Bir mühendis Ollama diyor, diğeri vLLM, üçüncüsü "TGI kutudan çıktığı gibi çalışmıyor mu?" Üçü de farklı bağlamlar için doğru. Hiçbiri tümü için doğru değil.

2026'da seçim ağacı önemlidir: önce donanım, ikinci ölçek, üçüncü iş yükü. Ve bir spesifik 2025 olayı — TGI'nin 11 Aralık'ta bakım moduna girmesi — yeni projeler için varsayılanı değiştirir.

## Kavram

### Beş motor

| Motor | En uygun | Notlar |
|--------|----------|-------|
| **llama.cpp** | CPU / kenar / minimum bağımlılık / en geniş model desteği | CPU'da en hızlı, tam kontrol |
| **Ollama** | Geliştirici dizüstü bilgisayarları, tek kullanıcı, tek-komut kurulum | llama.cpp'den %15-30 daha yavaş; üretim yükü altında 3 kat fark |
| **TGI** | HF ekosistemi, düzenlenmiş endüstriler | **11 Aralık 2025'ten beri bakım modu** |
| **vLLM** | Genel-amaçlı üretim, 100+ kullanıcı | Geniş üretim varsayılanı; Şubat 2026'da v0.15.1 |
| **SGLang** | Ajan çoklu-tur, önek-ağırlıklı iş yükleri | Üretimde 400.000+ GPU |

### Önce donanım kararı

**Yalnızca CPU** → llama.cpp. Ollama da çalışır ama daha yavaş. Başka hiçbir motor CPU'da rekabetçi değil.

**AMD GPU** → vLLM (AMD ROCm — Radeon Açık Hesaplama Platformu desteği). SGLang da çalışır. TRT-LLM NVIDIA-kilidi, bu yüzden dışarıda.

**NVIDIA Hopper (H100 / H200)** → vLLM veya SGLang veya TRT-LLM. Üçü de üst düzey.

**NVIDIA Blackwell (B200 / GB200)** → TRT-LLM throughput lideridir (Phase 17 · 07). vLLM ve SGLang yakın takip eder.

**Apple Silicon (M-serisi)** → llama.cpp (Metal). Ollama bunu sarar.

### İkinci ölçek kararı

**1 kullanıcı / yerel geliştirme** → Ollama. Tek komut, saniyeler içinde ilk token.

**10-100 kullanıcı / küçük ekip** → vLLM tek-GPU.

**100-10k kullanıcı / üretim** → vLLM üretim-yığını (Phase 17 · 18) veya SGLang.

**10k+ kullanıcı / kurumsal** → vLLM üretim-yığını + ayrıştırılmış (Phase 17 · 17) + LMCache (Phase 17 · 18).

### Üçüncü iş yükü kararı

**Genel sohbet / S&C** → vLLM geniş varsayılanda kazanır.

**Ajan çoklu-tur (araçlar, planlama, bellek)** → SGLang'ın RadixAttention'ı (Phase 17 · 06) domine eder.

**Ağır önek yeniden kullanımlı RAG** → SGLang.

**Kod üretimi** → vLLM iyi; SGLang önbellekte biraz daha iyi.

**Uzun bağlam (128K+)** → vLLM + parçalı prefill; SGLang + katmanlı KV.

### TGI bakım tuzağı

Hugging Face TGI, 11 Aralık 2025'te bakım moduna girdi — bundan sonra yalnızca hata düzeltmeleri. Tarihsel olarak: üst düzey gözlemlenebilirlik, sınıfının en iyisi HF-ekosistemi bütünleşmesi (model kartları, güvenlik araçları), ham throughput'ta vLLM'in biraz gerisinde.

2026'da yeni projeler için: TGI'den uzaklaşın. Mevcut TGI dağıtımları devam edebilir ama sonunda geçiş yapmalıdır. SGLang ve vLLM daha güvenli varsayılanlardır.

### Pipeline kalıbı

Geliştirme (Ollama) → staging (llama.cpp) → üretim (vLLM). Boyunca aynı GGUF veya HF ağırlıkları. Mühendisler dizüstü bilgisayarlarda hızla yineler; staging üretim nicemlemeyi yansıtır; üretim sunum hedefidir.

### Ollama uyarısı

Ollama geliştirme için harikadır. Paylaşılan üretim için harika değildir: Go HTTP serileştirme ek yük ekler, eşzamanlılık yönetimi vLLM'den daha basittir, OpenTelemetry desteği geride kalır. Ollama'yı parladığı yerde kullanın — tek kullanıcı, tek komut — ve paylaşılan için vLLM'e geçin.

### Kendi-kurulum vs yönetilen ayrı bir karar

Phase 17 · 01 (yönetilen hyperscaler'lar), · 02 (çıkarım platformları) yönetileni kapsar. Bu ders, zaten kendi-kurulum yapmaya karar verdiğinizi varsayar. Kendi-kurulum nedenleri: veri yerleşimi, özel ince-ayar, ölçekte toplam sahip olma maliyeti, barındırılan mevcut olmayan alan modeli.

### Hatırlamanız gereken sayılar

- TGI bakım modu: 11 Aralık 2025.
- vLLM v0.15.1: Şubat 2026; PyTorch 2.10; Blackwell SM120 desteği.
- SGLang üretim ayakizi: 400.000+ GPU.
- Ollama throughput farkı vs llama.cpp: %15-30 daha yavaş; üretim yükü altında 3 kat.

## Kullanım

`code/main.py` karar-ağacı yürüyücüsüdür: donanım + ölçek + iş yükü verildiğinde, bir motor seçer ve nedenini açıklar.

## Yaygınlaştırma

Bu ders `outputs/skill-engine-picker.md` üretir. Kısıtlar verildiğinde, bir motor seçer ve geçiş planını yazar.

## Alıştırmalar

1. `code/main.py`'yi donanımınız / ölçeğiniz / iş yükünüzle çalıştırın. Çıktı sezginizle eşleşiyor mu?
2. Altyapınız 12 H100 ve 8 MI300X AMD. Hangi motor? TRT-LLM neden masada değil?
3. Bir ekip 2026'da TGI kullanmak istiyor çünkü "bildiğimiz şey bu". Geçiş durumunu savunun.
4. Ollama geliştirmeden vLLM üretime: nicemleme, yapılandırma ve gözlemlenebilirlikte ne değişir?
5. P99 önek uzunluğu 8K ve kiracılar arası yüksek yeniden kullanımla RAG ürünü. Bir motor seçin ve Phase 17 · 11 + 18 ile istifleyin.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|----------------------|---------------|
| llama.cpp | "CPU olanı" | En geniş model desteği, CPU'da en hızlı |
| Ollama | "dizüstü bilgisayar olanı" | Tek-komut kurulum, geliştirici-düzeyi throughput |
| TGI | "HF'nin sunumu" | Aralık 2025'ten beri bakım modu |
| vLLM | "varsayılan" | 2026 geniş üretim taban çizgisi |
| SGLang | "ajan olanı" | Önek-ağırlıklı, RadixAttention |
| TRT-LLM | "NVIDIA-kilidi" | Blackwell throughput lideri, yalnızca NVIDIA |
| GGUF | "llama.cpp formatı" | Paketlenmiş K-nicem varyantları |
| Üretim-yığını | "vLLM K8s" | Phase 17 · 18 referans dağıtımı |
| Pipeline kalıbı | "geliştirme→stage→üretim" | Aynı ağırlıklarda Ollama → llama.cpp → vLLM |

## Ek Okuma

- [AI Made Tools — vLLM vs Ollama vs llama.cpp vs TGI 2026](https://www.aimadetools.com/blog/vllm-vs-ollama-vs-llamacpp-vs-tgi/)
- [Morph — llama.cpp vs Ollama 2026](https://www.morphllm.com/comparisons/llama-cpp-vs-ollama)
- [n1n.ai — Kapsamlı LLM Çıkarım Motoru Karşılaştırması](https://explore.n1n.ai/blog/llm-inference-engine-comparison-vllm-tgi-tensorrt-sglang-2026-03-13)
- [PremAI — 2026'nın En İyi 10 vLLM Alternatifi](https://blog.premai.io/10-best-vllm-alternatives-for-llm-inference-in-production-2026/)
- [TGI bakım duyurusu](https://github.com/huggingface/text-generation-inference) — sürüm notları.
- [vLLM v0.15.1 sürüm notları](https://github.com/vllm-project/vllm/releases)
