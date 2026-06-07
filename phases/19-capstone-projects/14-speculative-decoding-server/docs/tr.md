# Capstone 14 — Spekülatif-Çözme Çıkarım Sunucusu

> vLLM 0.7'deki EAGLE-3, gerçek trafikte 2.5-3x çıktı sunar. P-EAGLE (AWS 2026) paralel spekülasyonu daha da ileriye taşıdı. SGLang'in SpecForge'u taslak kafaları ölçekte eğitti. Red Hat'ın Speculators merkezi, yaygın açık modeller için hizalanmış taslakları yayınladı. TensorRT-LLM, NVIDIA'da spekülatif çözmeyi birinci sınıf yaptı. 2026 üretim servis yığını, EAGLE-ailesi taslakları, FP8 veya INT4 niceleme ve kuyruk-bekleme üzerinde HPA ile vLLM veya SGLang'dir. Bu capstone, tam kuyruk-gecikme raporuyla iki açık modeli 2.5x+ temel çıktı çıktısında servis etmektir.

**Type:** Capstone
**Languages:** Python (servis), C++ / CUDA (çekirdek inceleme), YAML (konfigürasyonlar)
**Prerequisites:** Phase 3 (deep learning), Phase 7 (transformers), Phase 10 (LLMs from scratch), Phase 17 (infrastructure)
**Phases exercised:** P3 · P7 · P10 · P17
**Time:** 30 saat

## Problem

Spekülatif çözme 2026'da bir meta oldu. EAGLE-3 taslak kafaları hedef modelin gizli durumları üzerinde eğitilir ve N token ileriyi tahmin eder; hedef model tek bir geçişte doğrular. %60-80 kabul oranları, uçtan uca çıktıda 2-3x artışa dönüşür. vLLM 0.7 bunu doğal olarak entegre eder. SGLang + SpecForge size eğitim boru hattını verir. Red Hat'ın Speculators'ı Llama 3.3 70B, Qwen3-Coder-30B MoE, GPT-OSS-120B için hizalanmış taslakları yayınladı.

Zanaat modelde değil servis işlemlerindedir. Kabul oranı trafik dağılımıyla kayar (ShareGPT vs kod vs alan verisi). Reddetme altındaki kuyruk gecikmesi, spekülasyon olmadan daha kötüdür — kararlı durum token/saniyesini değil birden çok toplu iş boyutunda p99 raporlamalısınız. Anthropic / OpenAI API'sine karşı 1M token başına maliyet, inandırıcılık koludur.

## Concept

Spekülatif çözmenin iki katmanı var. Bir **taslak** modeli (EAGLE-3 kafası, ngram veya hedef-hizalanmış küçük model) adım başına k aday token önerir. **Hedef** model tüm k'yi tek bir geçişte doğrular; kabul edilen herhangi bir önek açgözlü yolun yerini alır. Kabul oranı taslak-hedef hizalamasına ve girdi dağılımına bağlıdır.

EAGLE-3 çoğu trafikte ngram taslaklarını geçer. P-EAGLE, daha derin taslak ağaçları için paralel spekülasyon çalıştırır. Takas: reddetme üzerindeki P99 gecikmesi daha yüksektir çünkü doğrulama geçişi daha büyüktür. Servis konfigürasyonu, toplu-iş-boyutuna göre gecikmeyi raporlamalıdır.

Dağıtım Kubernetes'tir. vLLM 0.7, GPU başına veya tensör-paralel dilim başına bir çoğaltma çalıştırır. HPA, CPU yerine kuyruk-bekleme üzerinde otomatik ölçeklenir. FP8 (Marlin) ve INT4 (AWQ) nicelemeleri GPU belleğini bir H100 / H200 zarfı içinde tutar. Uçtan uca rapor: çıktı, kabul oranı, bs 1/8/32'de p50/p99 ve $/1M token.

## Architecture

```
request ingress
 |
 v
vLLM server (0.7) or SGLang (0.4)
 |
 +-- draft: EAGLE-3 heads | P-EAGLE parallel | ngram fallback
 +-- target: Llama 3.3 70B | Qwen3-Coder-30B | GPT-OSS-120B
 | quantized FP8-Marlin or INT4-AWQ
 |
 v
verify pass: batch k draft tokens through target
 |
 v (accept prefix; resample for rejected suffix)
 v
token stream back to client
 |
 v
Prometheus metrics: throughput, acceptance rate, queue wait, latency p50/p99
 |
 v
HPA on queue-wait metric
```

#### Açıklama

Bu mimari istek alımından token akışına kadar tam veri akışını gösterir. İstekler vLLM veya SGLang sunucusuna girer. Sunucu iki bileşenden oluşur: taslak (EAGLE-3 kafaları, P-EAGLE paralel veya ngram yedek) ve hedef model (nicellenmiş Llama 3.3 70B, Qwen3-Coder-30B veya GPT-OSS-120B). Taslak adım başına k aday token önerir; hedef tüm k'yi tek bir doğrulama geçişinde işler. Kabul edilen önek doğrudan döndürülür; reddedilen sonek yeniden örneklenir. Tüm süreç Prometheus metrikleri (çıktı, kabul oranı, kuyruk bekleme, p50/p99 gecikme) ile izlenir. HPA, yük altında kuyruk-bekleme metriğine göre çoğaltmaları otomatik ölçekler.

## Stack

- Servis: vLLM 0.7 veya SGLang 0.4
- Spekülatif yöntemler: EAGLE-3 taslak kafaları, P-EAGLE paralel spekülasyon, ngram yedek
- Taslak eğitimi: SpecForge (SGLang) veya Red Hat Speculators
- Hedef modeller: Llama 3.3 70B, Qwen3-Coder-30B MoE, GPT-OSS-120B
- Niceleme: FP8 (Marlin), INT4 AWQ
- Dağıtım: Kubernetes + NVIDIA cihaz eklentisi; kuyruk-bekleme metriği üzerinde HPA
- Değerlendirme: Alan-yayılma kabul ölçümü için ShareGPT, MT-Bench-v2, GSM8K, HumanEval
- Referans: Satıcı temel çizgisi için TensorRT-LLM spekülatif çözme

## Build It

1. **Hedef model hazırlığı.** Llama 3.3 70B'yi seçin. Marlin aracılığıyla FP8'e niceleyin. 1xH100 (veya 2x tensör-paralel) üzerinde vLLM 0.7 ile dağıtın.

2. **Taslak kaynağı.** Red Hat Speculators'tan hizalanmış bir EAGLE-3 taslak kafası çekin (veya SpecForge aracılığıyla bir tane eğitin). vLLM'ın spekülatif-çözme konfigürasyonuna yükleyin.

3. **Temel çıktı sayıları.** Spekülasyondan önce: bs 1/8/32'de token/saniye, p50/p99 gecikme, GPU kullanımı. Yayınlayın.

4. **EAGLE-3'ü etkinleştirin.** Konfigürasyonu çevirin; aynı kıyaslamayı yeniden çalıştırın. Hızlanmayı, kabul oranını, p99 kuyruk-gecikme deltasını raporlayın.

5. **P-EAGLE.** Paralel spekülasyonu etkinleştirin; serisel EAGLE-3'e karşı daha derin taslak ağacını ölçün. P-EAGLE'ın yardımcı olduğu vs zarar verdiği dönüm noktasını raporlayın.

6. **Alan trafiği.** Aynı sunucu üzerinden ShareGPT vs HumanEval vs alan-özgü trafik çalıştırın. Dağılım başına kabul oranını ölçün. Taslakların ne zaman saptığını belirleyin.

7. **İkinci hedef model.** Aynı boru hattını Qwen3-Coder-30B MoE üzerinde çalıştırın. Taslak daha zordur (MoE yönlendirme gürültüsü). Raporlayın.

8. **K8s HPA.** `queue_wait_ms`'i izleyen HPA ile K8s altında dağıtın. Yük üçe katlandığında dışa ölçeklemeyi gösterin.

9. **Maliyet karşılaştırması.** Aynı değerlendirmede Anthropic Claude Sonnet 4.7 ve OpenAI GPT-5.4'e karşı $/1M token hesaplayın. Yayınlayın.

## Use It

```
$ curl https://infer.example.com/v1/chat/completions -d '{"messages":[...]}'
[serve] vLLM 0.7, Llama 3.3 70B FP8, EAGLE-3 active
[decode] bs=8, accepted_tokens_per_step=3.2, acceptance_rate=0.76
[latency] first-token 42ms, full-response 980ms (620 tokens)
[cost] $0.34 per 1M output tokens at sustained throughput
```

#### Açıklama

Bu örnek tek bir çıkarım isteğinin metriklerini gösterir. vLLM 0.7, FP8 nicelenmiş Llama 3.3 70B ile EAGLE-3 etkin olarak çalışır. Toplu iş boyutu 8'de, adım başına 3.2 token kabul edilir (kabul oranı %76). İlk token 42ms'de, tam yanıt (620 token) 980ms'de gelir. Sürdürülebilir çıktıda maliyet 1M çıktı token'ı başına 0.34 dolardır. Bu, API sağlayıcılarının genellikle 3-15 dolar aralığında olduğu bir rakamdır ve self-host spekülatif çözmenin ekonomik avantajını gösterir.

## Ship It

`outputs/skill-inference-server.md` teslim edilen şeyi tanımlar. Spekülatif çözme ile ölçülmüş bir servis yığını, tam bir kıyaslama raporu ve bir K8s dağıtımı.

| Ağırlık | Ölçüt | Nasıl ölçülür |
|:-:|---|---|
| 25 | Temel çizgiye karşı ölçülen hızlanma | İki modelde eşleşen kalitede 2.5x+ çıktı |
| 20 | Gerçekçi trafik üzerinde kabul oranı | Dağılım başına kabul-oranı raporu |
| 20 | P99 kuyruk-gecikme disiplini | Spekülasyonla ve olmadan bs 1/8/32'de p99 |
| 20 | Operasyon | K8s dağıtımı, kuyruk-bekleme üzerinde HPA, sorunsuz yayılım |
| 15 | Yazım ve metodoloji | Neyin değiştiğinin ve nedeninin net açıklaması |
| **100** | | |

## Exercises

1. Taslak hedefin bir sürüm gerisindeyken kabul-oranı bozulmasını ölçün (ör. Llama 3.3 -> 3.4 sürüm kayması). Bir izleme uyarısı inşa edin.

2. Ngram-yedek uygulayın: EAGLE-3 kabul oranı bir eşiğin altına düşerse, ngram taslaklarına geçin. Güvenilirlik iyileşmesini raporlayın.

3. Kontrollü bir MoE deneyi çalıştırın: yönlendirme gürültüsü enjekte edilmiş ve edilmemiş aynı Qwen3-Coder-30B. Taslak kabul duyarlılığını ölçün.

4. H200'e (141 GB) genişletin. Çoğaltma başına kazanılan model boyutu-boşluğunu raporlayın ve nicelenmemiş Llama 3.3 70B servis edip edemeyeceğinizi belirtin.

5. Aynı H100 donanımında TensorRT-LLM spekülatif çözmeyi kıyaslayın. vLLM'a karşı nerede kazandığını raporlayın.

## Key Terms

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|------|----------------------|----------------------------|
| Taslak model | "Spekülatör" | Hedefin doğrulaması için N token öneren küçük model |
| EAGLE-3 | "2026 taslak mimarisi" | Hedef gizli durumları üzerinde eğitilmiş taslak kafası; ~%75 kabul |
| P-EAGLE | "Paralel spekülasyon" | Tek bir hedef geçişinde doğrulanmış taslak dalları ağacı |
| Kabul oranı | "İsabet oranı" | Yeniden örnekleme olmaksızın kabul edilen taslak token'ların oranı |
| Niceleme | "FP8 / INT4" | GPU belleğine daha fazla model sığdırmak için düşük hassasiyetli ağırlıklar |
| Kuyruk bekleme | "HPA metriği" | Çıkarım başlamadan önce bir isteğin bekleyen kuyrukta geçirdiği süre |
| Speculators hub | "Hizalanmış taslaklar" | Yaygın açık modeller için Red Hat Neural Magic'in EAGLE taslakları merkezi |

## Further Reading

- [vLLM EAGLE and P-EAGLE documentation](https://docs.vllm.ai) — referans servis yığını
- [P-EAGLE (AWS 2026)](https://aws.amazon.com/blogs/machine-learning/p-eagle-faster-llm-inference-with-parallel-speculative-decoding-in-vllm/) — paralel spekülatif çözme makalesi + entegrasyon
- [SGLang SpecForge](https://github.com/sgl-project/SpecForge) — taslak-kafa eğitim boru hattı
- [Red Hat Speculators](https://github.com/neuralmagic/speculators) — hizalanmış taslak merkezi
- [TensorRT-LLM speculative decoding](https://nvidia.github.io/TensorRT-LLM/) — satıcı alternatifi
- [Fireworks.ai serving architecture](https://fireworks.ai/blog) — ticari referans
- [EAGLE-3 paper (arXiv:2503.01840)](https://arxiv.org/abs/2503.01840) — yöntem makalesi
- [vLLM repository](https://github.com/vllm-project/vllm) — kod ve kıyaslamalar
