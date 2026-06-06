# Inference Metrikleri — TTFT, TPOT, ITL, Goodput, P99

> Dört metrik, bir inference dağıtımının çalışıp çalışmadığına karar verir. TTFT, prefill artı kuyruk artı ağdır. TPOT (eşdeğer olarak ITL), token başına bellek-bağlı decode maliyetidir. Uçtan-uca gecikme, TTFT artı çıktı uzunluğu çarpı TPOT'tur. Verim, filo genelinde saniyedeki token sayısıdır. Ama ürün için önemli olan goodput'tur — her SLO'yu aynı anda karşılayan isteklerin kesri. Yüksek verim, düşük goodput'ta, zamanında kullanıcılara ulaşmayan tokenleri işliyorsunuz demektir. Llama-3.1-8B-Instruct üzerinde TRT-LLM'de 2026 için referans sayılar: ortalama TTFT 162 ms, ortalama TPOT 7,33 ms, ortalama E2E 1.093 ms. Her zaman P50, P90, P99 raporlayın — asla yalnızca ortalama. Ve ölçüm tuzağını izleyin: GenAI-Perf TTFT'yi ITL hesaplamasının dışında tutar, LLMPerf dahil eder; aynı çalıştırma için iki araç TPOT'ta anlaşmaz.

**Tür:** Öğrenme
**Diller:** Python (stdlib, oyuncak yüzdelik hesaplayıcısı ve goodput raporlayıcısı)
**Önkoşullar:** Faz 17 · 04 (vLLM Serving Internals)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- TTFT, TPOT, ITL, E2E, verim ve goodput'u tam olarak tanımlayın ve her birinin ölçtüğü bileşeni adlandırın.
- Ortalamanın LLM sunma için neden yanlış istatistik olduğunu ve P50/P90/P99'un nasıl okunacağını açıklayın.
- Bir SLO çoklu-kısıtı (ör. TTFT<500 ms VE TPOT<15 ms VE E2E<2s) oluşturun ve ona karşı goodput'u hesaplayın.
- Aynı çalıştırma için TPOT'ta anlaşmayan iki kıyaslama aracını adlandırın ve nedenini açıklayın.

## Sorun

"Verimimiz saniyede 15.000 token." Ee? İsteklerin %40'ı uçtan-uca 2 saniyeyi aştıysa, kullanıcılar oturumu terk etti. Yalnızca başına verim, ürünün çalışıp çalışmadığını söylemez.

Inference'ın birden çok gecikme ekseni vardır ve her biri farklı şekilde başarısız olur. Prefill hesaplama-bağlıdır ve istem uzunluğuyla ölçeklenir. Decode bellek-bağlıdır ve batch boyutuyla ölçeklenir. Kuyruk gecikmesi operasyonel bir sorundur. Ağ fiziksel-mesafe sorunudur. Her biri için ayrı metriklere, yüzdeliklere ve "kullanıcı beklediğini aldı mı" diyen tek bir bileşiğe ihtiyacınız vardır — bu goodput'tur.

## Kavram

### TTFT — ilk token süresi

`TTFT = queue_time + network_request + prefill_time`

Prefill, istemler uzun olduğunda baskındır. H100 üzerinde Llama-3.3-70B FP8'de, 32k istem ~800 ms saf prefill sürer. Kuyruk süresi, yük altında scheduler davranışıdır. Ağ isteği, TLS dahil tel süresidir. TTFT, kullanıcının herhangi bir şey geri akmadan önce gördüğü gecikmedir.

### TPOT / ITL — tokenlar-arası gecikme

Tek bir nicelik için birçok ad. `TPOT` (çıktı token başına süre), `ITL` (tokenlar-arası gecikme), `decode gecikmesi token başına` — hepsi aynı. İlk token'dan sonra, art arda akışı sağlanan tokenlar arasındaki süredir.

`TPOT = (decode_forward_time + scheduler_overhead) / tokens_produced`

Aynı Llama-3.3-70B H100 yığınında chunked prefill ile, TPOT ortalama ~7 ms. Chunked prefill olmadan, komşu bir dizide uzun bir prefill sırasında TPOT 50 ms'ye sıçrayabilir. P99'u izleyin, ortalamayı değil.

### E2E gecikme

`E2E = TTFT + TPOT * output_tokens + network_response`

Uzun çıktılar (>500 token) için, E2E TPOT-baskındır. Uzun istemli kısa çıktılar için, E2E TTFT-baskındır. Çıktı uzunluğuna koşullandırılmış E2E raporlayın.

### Verim

`throughput = total_output_tokens / elapsed_time`

Toplu metrik. Size filo verimliliğini söyler. Bireysel istek sağlığını söylemez.

### Goodput — gerçekten önemsediğiniz metrik

`goodput = (TTFT <= a) VE (TPOT <= b) VE (E2E <= c) karşılayan isteklerin kesri`

SLO çoklu-kısıttır. Bir istek yalnızca her kısıt tutulursa "iyi"dir. Goodput paydır. %60 goodput'ta yüksek verim başarısızlıktır. %99 goodput'ta daha düşük verim hedeftir.

2026'da goodput, MLPerf Inference v6.0 gönderimlerinde ve AI platform sağlayıcılarının iç SLA izlemesinde kullanılan metriktir.

### Ortalama neden yanlış istatistiktir

LLM gecikme dağılımları sağa-çarpıktır. Bir uzun-prefill komşusu olan bir decode batch'i, ~7 ms TPOT ile 500 token ve ~60 ms TPOT ile 20 token gönderebilir. Ortalama TPOT 9 ms'dir. P99 TPOT 65 ms'dir. Kullanıcılar P99'a düzenli olarak çarpar — bu yüzden ayrılırlar.

Her zaman üçlüyü (P50, P90, P99) raporlayın. Kullanıcı deneyimi için, optimize ettiğiniz P99'dur.

### Referans sayılar — Llama-3.1-8B-Instruct, TRT-LLM, 2026

- ortalama TTFT: 162 ms
- ortalama TPOT: 7,33 ms
- ortalama E2E: 1.093 ms
- P99 TPOT: chunked-prefill konfigürasyonuna bağlı olarak 10-25 ms.

Bunlar yayınlanan NVIDIA referans noktalarıdır. Model boyutuyla (70B 3-5x gösterirdi), donanımla (H100 vs B200 ~3x) ve yükle birlikte değişir.

### Ölçüm tuzağı

En çok kullanılan 2026 kıyaslama araçlarından ikisi aynı çalıştırma için TPOT'ta anlaşmaz:

- **NVIDIA GenAI-Perf**: ITL hesaplamasından TTFT'yi dışlar. ITL token 2'den başlar.
- **LLMPerf**: TTFT'yi dahil eder. ITL token 1'den başlar.

TTFT 500 ms ve 100 çıktı tokenı 700 ms toplam decode olan bir istek için, GenAI-Perf `ITL = 700/99 = 7,07 ms` raporlar, LLMPerf `ITL = 1200/100 = 12,00 ms` raporlar. Araç seçimi sayıyı değiştirir.

Her zaman aracı belirtin. Her zaman tanımı yayınlayın.

### Bir SLO oluşturmak

2026'da 70B sohbet modeli için makul tüketici-yüzlü bir SLO:

- TTFT P99 <= 800 ms.
- TPOT P99 <= 25 ms.
- E2E P99 <= 3 s <300-token çıktılar için.
- Goodput hedefi >= %99.

Kurumsal SLO'lar TTFT'yi sıkılaştırır (200-400 ms) ve E2E'yi gevşetir. Amaç onları yazmak, üçünü de ölçmek ve goodput'u tek bir bileşik olarak izlemektir.

### Nasıl ölçülür

- Gerçek trafiği veya gerçekçi sentetik trafiği çalıştırın (LLMPerf ile `--mean-input-tokens 800 --stddev-input-tokens 300 --mean-output-tokens 150`).
- Kıyaslama çalıştırması için 2x en yüksek eşzamanlılığı hedefleyin.
- 30-50 iterasyon çalıştırın, birleşik örneğin yüzdeliklerini alın.
- Araç adı, araç sürümü, model, donanım, eşzamanlılık, istem dağılımı ile yayınlayın.

## Kullan

`code/main.py` oyuncak bir goodput hesaplayıcısıdır. Sentetik bir gecikme dağılımı üretin, bir SLO uygulayın ve goodput'u hesaplayın. Ayrıca aynı iz üzerinde GenAI-Perf ve LLMPerf TPOT farkını gösterir.

## Üret

Bu ders `outputs/skill-slo-goodput-gate.md` üretir. İş yükü ve SLO verildiğinde, dağıtımları goodput üzerinde geçitleyen, verim üzerinde değil, CI/CD-hazır bir kıyaslama reçetesi üretir.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. %1 kuyruk sıçraması olan bir dağılım üretin. P99 TPOT'yi 30 ms'den 15 ms'ye sıkılaştırdığınızda goodput nasıl değişir?
2. Bir satıcı "H100 üzerinde Llama 3.3 70B'de 15.000 tok/s" alıntılıyor. Güvenmeden önce sorulacak üç soruyu adlandırın.
3. Chunked prefill neden P99 TPOT'yi korur, ama ortalama TPOT'yi korumaz?
4. Bir sesli asistan için tüketici SLO'su oluşturun (ilk token duyulur, okunmaz). Hangi metrik en kullanıcı-görünür?
5. LLMPerf README'sini ve GenAI-Perf dokümanlarını okuyun. Araçların anlaşmadığı üç başka metrik belirleyin.

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|----------------------|----------------------------|
| TTFT | "ilk token süresi" | Kuyruk + ağ + prefill; uzun istemlerde prefill baskın |
| TPOT | "çıktı token başına süre" | İlkten sonra token başına bellek-bağlı decode maliyeti |
| ITL | "tokenlar-arası gecikme" | Çoğu araçta TPOT ile aynı (hepsinde değil — GenAI-Perf'e bakın) |
| E2E | "uçtan uca" | TTFT + TPOT * çıktı_uzunluğu; üzerine yanıt-tarafı ağ |
| Verim | "tok/s" | Filo verimliliği; gecikme yüzdelikleri olmadan işe yaramaz |
| Goodput | "SLO-karşılanma oranı" | Her SLO kısıtını aynı anda karşılayan isteklerin kesri |
| P99 | "kuyruk" | 1/100 en kötü durum gecikmesi; kullanıcı deneyimi metriği |
| SLO çoklu-kısıt | "eklem" | Üç gecikme sınırının VE'si; herhangi biri ihlal edilirse istek başarısız |
| GenAI-Perf vs LLMPerf | "araç tuzağı" | Araçlar, ITL'nin TTFT'yi içerip içermediği konusunda anlaşmaz |

## İleri Okuma

- [NVIDIA NIM — LLM Benchmarking Metrics](https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html) — TTFT, ITL, TPOT'nin kanonik tanımı.
- [Anyscale — LLM Serving Benchmarking Metrics](https://docs.anyscale.com/llm/serving/benchmarking/metrics) — alternatif tanımlar ve ölçüm reçetesi.
- [BentoML — LLM Inference Metrics](https://bentoml.com/llm/inference-optimization/llm-inference-metrics) — gerçek dağıtımlarda uygulamalı ölçüm.
- [LLMPerf](https://github.com/ray-project/llmperf) — Ray-temelli açık-kaynak kıyaslama.
- [GenAI-Perf](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/client/src/c++/perf_analyzer/genai-perf/README.html) — NVIDIA'nın kıyaslama aracı.
- [MLPerf Inference](https://mlcommons.org/benchmarks/inference-datacenter/) — endüstri-kabul görmüş goodput-temelli kıyaslama.
