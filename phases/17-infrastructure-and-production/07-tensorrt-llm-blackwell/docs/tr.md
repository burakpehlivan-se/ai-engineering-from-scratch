# Blackwell Üzerinde TensorRT-LLM: FP8 ve NVFP4

> TensorRT-LLM yalnızca NVIDIA içindir, ancak Blackwell'de kazanır. Dynamo orkestasyonu ile GB200 NVL72 üzerinde, SemiAnalysis InferenceX 2026'nın 1.-2. çeyreğinde 120B modelde milyon token başına 0,012$ ölçtü; H100 + vLLM üzerinde aynı iş yükünde 0,09$/M — 7x ekonomik fark. Yığın, birleşik üç kayan-nokta rejimidir: FP8, gereken dinamik aralığa sahip olduğu için KV cache ve attention çekirdekleri için kritik kalır; NVFP4 (4-bit mikro-ölçekleme) ağırlıkları ve aktivasyonları ele alır; çoklu-token tahmini (MTP) ve ayrıştırılmış prefill/decode üzerine 2-3x daha ekler. Gün-0 model desteği, eğitim sonrası dönüşüm olmadan FP4 ağırlıklarını doğrudan yükler. 2026 mühendislik ekipleri için yakalama: TRT-LLM kapalı bir NVIDIA yığınıdır, bu nedenle onu benimsemek taşınabilirliği verimlilikle takas eder. Taahhüt etmeden önce modellerinizin ve donanımınızın karışımı üzerinde matematiği çalıştırın.

**Tür:** Öğrenme
**Diller:** Python (stdlib, oyuncak FP8/NVFP4 bellek ve maliyet hesaplayıcısı)
**Önkoşullar:** Faz 17 · 04 (vLLM Serving Internals), Faz 10 · 13 (Kuantizasyon)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Ağırlıklar NVFP4'te olsa bile FP8'in neden KV cache ve attention için kritik kaldığını açıklayın.
- Bir sınır modelinin HBM ayak izini BF16, FP8 ve NVFP4 altında hesaplayın ve tasarrufun nereden geldiğini gerekçelendirin.
- TRT-LLM'in yararlandığı Blackwell'e özgü özellikleri (gün-0 FP4, MTP, ayrıştırılmış sunma, hepsinden-hepsine ilkeller) adlandırın.
- TRT-LLM'in NVIDIA-kilidinin Hopper üzerinde vLLM'e karşı 7x maliyet farkına ne zaman değdiğine karar verin.

## Sorun

2026'da inference ekonomisinin sınırı "token başına kaç dolar"dur. Cevap dört yığılmış seçime bağlıdır: donanım nesli (Hopper H100/H200 vs Blackwell B200/GB200), hassasiyet (BF16 → FP8 → NVFP4), sunma motoru (vLLM vs SGLang vs TRT-LLM) ve orkestrasyon (düz vs ayrıştırılmış vs Dynamo).

Hopper üzerinde vLLM ile, 120B MoE milyon token başına ~0,09$ üzerinde çalışır. TRT-LLM + Dynamo ile Blackwell üzerinde aynı model ~0,012 üzerinde çalışır — 7x daha ucuz. O farkın bir kısmı donanımdır (Blackwell, Hopper'a kıyasla GPU başına 11-15x LLM verimine sahiptir). Bir kısmı yığındır: FP4 ağırlıklar, MTP draft, ayrıştırılmış prefill/decode ve MoE uzman iletişimi için NVLink 5 hepsinden-hepsine.

Bunu NVIDIA'nın yığını dışında tekrarlayamazsınız. Ödünleşim — taşınabilirlik için ekonomi. Hangi yığın seçimlerinin farkın hangi payını verdiğini anlamak bu dersin amacıdır.

## Kavram

### FP8 neden KV cache için zemin olmaya devam ediyor

2026'da yaygın bir hata: NVFP4'ün her yerde geçerli olduğunu varsaymak. Değildir. KV cache, çok geniş bir dinamik aralıkta dikkat anahtarlarını ve değerlerini sakladığı için FP8 (8-bit kayan nokta) gerektirir. KV'yi FP4'e kuantize etmek yıkıcı doğruluk kaybına neden olur — dağılımın kuyruğu düşer ve dikkat puanları çöker. FP8'in üs bitleri, KV cache'in ihtiyaç duyduğu aralığı sağlar.

NVFP4 (2025-2026) ağırlıklara ve aktivasyonlara uygulanır. Mikro-ölçekleme: ağırlıkların her bloğu, tensör başına ölçek kaybı olmadan farklı dinamik aralıkları kapsayabilmesi için kendi ölçek faktörüne sahiptir. Aktivasyonlar için FP4 dayanır çünkü aktivasyonlar bir katman içinde küçük aralıktadır.

Tipik Blackwell konfigürasyonu:

- Ağırlıklar: NVFP4 (4-bit mikro-ölçekleme).
- Aktivasyonlar: NVFP4.
- KV cache: FP8.
- Attention biriktirici: FP32 (softmax kararlılığı).

### TRT-LLM'in kullandığı Blackwell'e özgü ilkeller

- **Gün-0 FP4 ağırlıklar**: model sağlayıcıları FP4 ağırlıklarını doğrudan gönderir; TRT-LLM eğitim sonrası dönüşüm olmadan yükler. FP4 için AWQ / GPTQ adımı yok.
- **Çoklu-token tahmini (MTP)**: Faz 17 · 05'teki EAGLE ile aynı fikir ancak TRT-LLM derlemesine entegre.
- **Ayrıştırılmış sunma**: prefill ve decode ayrı GPU havuzlarında, KV cache NVLink veya InfiniBand üzerinden aktarılır. Faz 17 · 20'deki Dynamo ile aynı fikir.
- **Hepsinden-hepsine iletişim ilkelleri**: NVLink 5, MoE uzman iletişim gecikmesini Hopper'a kıyasla 3x kesti. TRT-LLM'in MoE çekirdekleri buna göre ayarlandı.
- **NVFP4 + MXFP8 mikro-ölçekleme**: Blackwell Tensor Çekirdeklerinde donanımla hızlandırılmış ölçek-faktörü işleme.

### Ezberlemeniz gereken sayılar

- HGX B200, TRT-LLM üzerinden GPT-OSS-120B'de 0,02$/M token.
- GB200 NVL72, Dynamo (TRT-LLM'i orkestre eden) üzerinden 0,012$/M token.
- H100 + vLLM, karşılaştırılabilir iş yükünde ≈ 0,09$/M token.
- TRT-LLM güncellemelerinde üç ayda 2,8x verim kazancı (2026).
- Blackwell vs Hopper, GPU başına 11-15x LLM verimi.
- MLPerf Inference v6.0 (Nisan 2026): Blackwell gönderilen her görevi domine ediyor.

### FP4'ün kalite açısından gerçek maliyeti

NVFP4 agresiftir. Akıl-yürütme-ağırlıklı iş yüklerinde (zincirleme düşünce, matematik, uzun bağlamla kod üretimi), FP4 ağırlıkları görünür şekilde bozulur. Blok başına kalibrasyon azaltır ama yok etmez. Akıl-yürütme modelleri gönderen ekipler genellikle FP8 ağırlıklar + FP4 aktivasyonlar bir uzlaşı olarak veya H200'de her yerde FP8'de kalır.

Kural: NVFP4 ağırlıklarına taahhüt etmeden önce her zaman eval setinizde görev kalitesini doğrulayın.

### Bu neden bir NVIDIA-kilit kararı

TRT-LLM C++ + CUDA + kapalı-kaynak çekirdeklerdir. Modellerin belirli bir GPU SKU'su için derlenmesi gerekir. AMD yok, Intel yok, ARM yok. Altyapı stratejiniz çok-satıcılı ise, TRT-LLM-sunulan katman için TRT-LLM bir başlangıç noktası değildir — karma donanım üzerinde hâlâ vLLM'den sunabilirsiniz. Yalnızca NVIDIA iseniz, 7x fark kilidi öder.

### 2026 pratik reçetesi

Yıllık 100M$+ bir inference faturası için, Hopper + vLLM üzerinde çalışmak masada 7-10x bırakır. Maliyet-baskın iş yüklerini Blackwell + TRT-LLM + Dynamo'ya taşıyın. Deneysel katmanı, model iterasyon hızı için H100 + vLLM'de tutun. Üretimden önce her NVFP4-dönüştürülmüş modelde kaliteyi doğrulayın.

### Ayrıştırma bonusu

TRT-LLM'in ayrıştırılmış sunması (ayrı prefill ve decode havuzları) Faz 17 · 20'de ayrıntılı olarak ele alınmıştır. Blackwell'de çarpan yığılır: FP4 ağırlıkları × MTP hızlanması × ayrıştırılmış yerleştirme × cache-farkında yönlendirme. 7x sayısı bu tam yığını varsayar.

## Kullan

`code/main.py`, üç yığın boyunca bir model için HBM ayak izini, decode verimini (bellek-bağlı rejim) ve $/M-token'ı hesaplar: H100 + BF16 + vLLM, H100 + FP8 + vLLM, B200 + NVFP4/FP8 + TRT-LLM. Birleşik etkiyi ve her değişikliğin farkın payını katkısını görmek için çalıştırın.

## Üret

Bu ders `outputs/skill-trtllm-blackwell-advisor.md` üretir. İş yükü, model boyutu ve yıllık token hacmi verildiğinde, Blackwell + TRT-LLM yığınının NVIDIA-kilidine değip değmeyeceğine karar verir.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. %30 aktif parametreli 120B MoE için, H100 BF16, H100 FP8 ve B200 NVFP4/FP8 üzerinde bellek-bant-genişliği-sınırlı decode verimini hesaplayın. En büyük sıçrama nereden geliyor?
2. Bir müşteri yılda 2M$ H100 + vLLM harcıyor. 7x ekonomik fark verildiğinde, TRT-LLM'e bir geçişi 12 ayda amorti etmek için kaç tane Blackwell GPU satın almaları gerektiğinin başabaş noktasını hesaplayın.
3. NVFP4 ağırlık dönüşümünden sonra MATH'te doğruluğun 3 puan düştüğünü görüyorsunuz. İki kurtarma yolunu adlandırın: biri kalite-ilk (FP8 ağırlıkları tut), biri maliyet-ilk (alan-içi veriyle kalibre et).
4. MLPerf v6.0 inference sonuçlarını okuyun. Blackwell-üzeri-Hopper farkının en küçük olduğu görev hangisidir ve neden?
5. 128k bağlamda NVFP4 ağırlıklar + FP8 KV cache ile 405B model için gereken HBM'yi hesaplayın. Tek bir GB200 NVL72 düğümüne sığıyor mu?

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|----------------------|----------------------------|
| FP8 | "sekiz-bit kayan" | 8-bit kayan nokta; dinamik aralık nedeniyle KV cache ve attention için kullanılır |
| NVFP4 | "dört-bit mikro" | NVIDIA'nın 4-bit mikro-ölçekleme FP formatı; Blackwell'de ağırlıklar ve aktivasyonlar |
| MXFP8 | "MX sekiz" | Mikro-ölçekleme FP8 varyantı; Blackwell Tensor Çekirdeklerinde donanımla hızlandırılmış |
| Gün-0 FP4 | "FP4 ağırlıkları gönder" | Model sağlayıcıları ağırlıkları zaten FP4'te yayınlar; eğitim sonrası dönüşüm adımı yok |
| MTP | "çoklu-token tahmini" | TRT-LLM'in entegre spekülatif-decode draft'ı (Faz 17 · 05) |
| Ayrıştırılmış sunma | "prefill/decode böl" | Ayrı GPU havuzlarında prefill ve decode; KV NVLink/IB üzerinden aktarılır |
| Hepsinden-hepsine | "MoE uzman iletişimi" | Tokenları uzman GPU'larına yönlendiren iletişim örüntüsü; NVLink 5 3x keser |
| InferenceX | "SemiAnalysis inference kıyaslaması" | 2026 endüstri-kabul görmüş token-başına-maliyet kıyaslaması |

## İleri Okuma

- [NVIDIA — Blackwell Ultra MLPerf Inference v6.0](https://developer.nvidia.com/blog/nvidia-blackwell-ultra-sets-new-inference-records-in-mlperf-debut/) — Nisan 2026 MLPerf sonuçları.
- [NVIDIA — MoE Inference on Blackwell](https://developer.nvidia.com/blog/delivering-massive-performance-leaps-for-mixture-of-experts-inference-on-nvidia-blackwell/) — NVLink 5 hepsinden-hepsine ve MoE çekirdekleri.
- [TensorRT-LLM Overview](https://nvidia.github.io/TensorRT-LLM/overview.html) — resmi motor dokümantasyonu.
- [NVIDIA — Introducing Dynamo](https://developer.nvidia.com/blog/introducing-nvidia-dynamo-a-low-latency-distributed-inference-framework-for-scaling-reasoning-ai-models/) — TRT-LLM üzerinde ayrıştırılmış orkestrasyon.
- [MLPerf Inference](https://mlcommons.org/benchmarks/inference-datacenter/) — Blackwell sayılarını yayınlayan kıyaslama paketi.
