# LLM API'lerini Yük Testi — k6 ve Locust Neden Yalan Söyler

> Geleneksel yük test araçları, akan (streaming) yanıtlar, değişken çıktı uzunlukları, token-düzey metrikler veya GPU doygunluğu için tasarlanmadı. İki tuzak çoğu ekibi ısırır. GIL tuzağı: Locust'un token-düzey ölçümü, Python GIL (Global Yorumlayıcı Kilidi) altında tokenizasyon çalıştırır; bu, ağır eşzamanlılık altında istek üretimiyle rekabet eder; tokenizasyon birikim işi sonra rapor edilen token-arası gecikmeyi şişirir — darboğazınız sizin istemciniz, sunucu değil. Prompt-birlik tuzağı: bir döngüde özdeş prompt'lar, token dağılımı üzerinde bir noktayı test eder; gerçek trafik değişken uzunluğa ve çeşitli önek eşleşmelerine sahiptir. LLMPerf bunu `--mean-input-tokens` + `--stddev-input-tokens` ile düzeltir. 2026'da araç eşlemesi: LLM'ye özel (GenAI-Perf, LLMPerf, LLM-Locust, guidellm) token-düzey doğruluk için; **k6 v2026.1.0** + **k6 Operator 1.0 GA (Eylül 2025)** — akan-farkında, Kubernetes-native TestRun/PrivateLoadZone CRD'leri ile dağıtılmış, CI/CD geçitleri için en iyi; Vegeta Go sabit-hız doygunluğu için; akan için yalnızca LLM-Locust uzantısıyla Locust 2.43.3. Yük kalıpları: sabit durum, rampa, sivri (otomatik ölçekleme testi), ıslatma (bellek sızıntıları).

**Tür:** Kur
**Diller:** Python (stdlib, basit gerçekçi-prompt üreteci + gecikme toplayıcı)
**Önkoşullar:** Phase 17 · 08 (Inference Metrikleri), Phase 17 · 03 (GPU Otomatik Ölçekleme)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- İki anti-kalıbı (GIL tuzağı, prompt-birlik tuzağı) açıklayın ki genel yük test araçları LLM API'leri için yalan söyler.
- Belirli bir amaç için araç seçin: LLMPerf (kıyaslama çalıştırması), k6 + akan uzantısı (CI geçidi), guidellm (büyük ölçekli yapay), GenAI-Perf (NVIDIA referansı).
- Dört yük kalıbını (sabit, rampa, sivri, ıslatma) tasarlayın ve her birinin yakaladığı arıza modunu sayın.
- Sabit uzunluk yerine giriş token'larının ortalaması + standart sapması kullanarak gerçekçi bir prompt dağılımı oluşturun.

## Problem

LLM uç noktanızı k6 ile 500 eşzamanlı kullanıcıda test ettiniz. Dayandı. Gönderdiniz. 200 gerçek kullanıcıyla üretimde servis çöktü — P99 TTFT patladı, GPU'lar sabitlendi.

İki şey oldu. Birincisi, k6 500 özdeş prompt gönderdi — istek-birleştirmeniz ve önek önbelleğiniz, 500 eşzamanlı decode'u hâlbuki bir tanesini hallediyormuşsunuz gibi gösterdi. İkincisi, k6 akan yanıtlardaki token-arası gecikmeyi gözün deneyimlediği şekilde izlemiyor; bir HTTP bağlantısı görüyor, değişen aralıklarla gelen 500 token'ı değil.

LLM'ler için yük testi kendi disiplinidir.

## Kavram

### GIL tuzağı (Locust)

Locust Python kullanır ve tokenizasyonu istemci tarafında GIL altında çalıştırır. Yüksek eşzamanlılık altında tokenizer istek üretiminin arkasında sıralanır. Rapor edilen token-arası gecikme istemci tarafı tokenizasyon birikimini içerir. Sunucunun yavaş olduğunu düşünürsünüz; test koşumudur.

Düzeltme: LLM-Locust uzantısı tokenizasyonu ayrı süreçlere taşır veya derlenmiş-dil koşumu (k6, tokenizers.rs kullanan LLMPerf) kullanır.

### Prompt-birlik tuzağı

Tüm bilinen yük test araçları bir prompt yapılandırmanıza izin verir. 10.000 yinelimeli bir döngü testinde her seferinde tam olarak aynı prompt gönderilir. Sunucu her seferinde aynı öneki görür — önek önbelleği isabetleri %100'e yaklaşır, throughput harika görünür.

Düzeltme: bir prompt dağılımından örnekleyin. LLMPerf `--mean-input-tokens 500 --stddev-input-tokens 150` kullanır — çeşitli uzunluklar, çeşitli içerik.

### Dört yük kalıbı

1. **Sabit durum (Steady-state)** — 30-60 dakika sabit RPS. Yakalar: taban çizgisi performans gerilemeleri.
2. **Rampa (Ramp)** — RPS'yi 0'dan 15 dakikada hedeefe doğrusal artır. Yakalar: kapasite kırılma noktası, ısınma anomalileri.
3. **Sivri (Spike)** — ani 3-10 kat RPS 2 dakika, sonra geri. Yakalar: otomatik ölçekleme gecikmesi, kuyruk doygunluğu, soğuk başlatma etkisi.
4. **Islatma (Soak)** — 4-8 saat sabit durum. Yakalar: bellek sızıntıları, bağlantı-havuzu kayması, gözlemlenebilirlik taşması.

### 2026 araç eşlemesi

**LLMPerf** (Anyscale) — Python ama Rust destekli tokenizasyon. Ortalama/stddev prompt'lar. Akan-farkında. Performans çalıştırmaları için en iyi varsayılan.

**NVIDIA GenAI-Perf** — NVIDIA'nın referansı. Triton istemcisi kullanır; kapsamlı metrik kapsamı. ITL'sinin TTFT'yi dışladığını unutmayın; LLMPerf'inki dahil eder. İki araç aynı sunucu için farklı TPOT üretir.

**LLM-Locust** (TrueFoundry) — GIL tuzağını düzelten Locust uzantısı. Tanıdık Locust DSL + akan metrikler.

**guidellm** — büyük ölçekli yapay kıyaslama.

**k6 v2026.1.0** + **k6 Operator 1.0 GA (Eylül 2025)**:
- k6'nın kendisi (Go, derlenmiş, GIL yok) akan-farkında metrikler ekledi.
- k6 Operator, Kubernetes-native dağıtılmış test için TestRun / PrivateLoadZone CRD'lerini kullanır.
- CI/CD geçitleri ve SLA testi için en iyi.

**Vegeta** — Go, k6'dan daha basit. Sabit-hız HTTP doygunluğu. LLM-farkında değil ama ağ geçidi / hız sınırı testi için iyi.

**Locust 2.43.3 stok** — LLM için GIL tuzağı var. Yalnızca LLM-Locust uzantısıyla.

### CI'da SLA geçidi

PR üzerinde k6 çalıştırın:

- Taban çizgisi RPS'de her biri 30-50 yineleme.
- Geçit: P50/P95 TTFT, 5xx < %5, TPOT eşiğin altında.
- İhlalde yapıyı kırın.

### Gerçekçi prompt dağılımı

Gerçek trafik örneklerinden (varsa) veya yayınlanmış dağılımlardan (örneğin sohbet için ShareGPT, kod için HumanEval) oluşturun. Ortalama + stddev'i LLMPerf'e besleyin. Tek-prompt-ile-döngüden her ne pahasına olursa olsun kaçının.

### Hatırlamanız gereken sayılar

- k6 Operator 1.0 GA: Eylül 2025.
- k6 v2026.1.0: akan-farkında metrikler.
- Tipik LLMPerf çalıştırması: eşzamanlılık X'te 100-1000 istek.
- Tipik CI geçidi: PR başına 30-50 yineleme.
- Dört kalıp: sabit, rampa, sivri, ıslatma.

## Kullanım

`code/main.py`, gerçekçi prompt dağılımıyla bir yük testini simüle eder, etkin TPOT ölçer ve tek-biçimli-prompt tuzağını gösterir.

## Yaygınlaştırma

Bu ders `outputs/skill-load-test-plan.md` üretir. İş yükü ve SLA verildiğinde, araç seçer ve dört yük kalıbını tasarlar.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Tek-biçimli vs gerçekçi dağılımı karşılaştırın — boşluk nerede?
2. CI geçidi için k6 betiği yazın: 100 eşzamanlıda TTFT P95 < 800 ms, 5 dakika çalışma süresi.
3. Islatma testiniz saatte 50 MB bellek artışı gösteriyor. Üç nedeni ve aralarında seçim yapacak araçları sayın.
4. Karpenter + vLLM üretim-yığını (Phase 17 · 03 + 18) yerindeyken 10 RPS'den 100 RPS'ye sivri test. Beklenen iyileşme süresi nedir?
5. GenAI-Perf TPOT=6ms raporlar; LLMPerf aynı sunucuda TPOT=11ms raporlar. Açıklayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|----------------------|---------------|
| LLMPerf | "LLM koşumu" | Anyscale kıyaslama aracı, akan-farkında |
| GenAI-Perf | "NVIDIA aracı" | NVIDIA referans koşumu |
| LLM-Locust | "LLM'ler için Locust" | GIL tuzağını düzelten Locust uzantısı |
| guidellm | "yapay kıyaslama" | Büyük ölçekli yapay araç |
| k6 Operator | "K8s k6" | CRD tabanlı dağıtılmış k6 |
| GIL tuzağı | "Python istemci ek yükü" | Tokenizasyon birikimi rapor edilen gecikmeyi şişirir |
| Prompt-birlik tuzağı | "tek-prompt yalanı" | Aynı prompt'la döngü önbelleğe isabet eder, throughput'u şişirir |
| Sabit durum | "sabit yük" | N dakika düz RPS |
| Rampa | "doğrusal yukarı" | Süre boyunca 0'dan hedefe |
| Sivri | "patlama testi" | Ani çarpan sonra geri |
| Islatma | "uzun test" | Sızıntı tespiti için saatler |

## Ek Okuma

- [TianPan — LLM Uygulamalarını Yük Testi](https://tianpan.co/blog/2026-03-19-load-testing-llm-applications)
- [PremAI — LLM'leri Yük Testi 2026](https://blog.premai.io/load-testing-llms-tools-metrics-realistic-traffic-simulation-2026/)
- [NVIDIA NIM — LLM Inference Kıyaslamaya Giriş](https://docs.nvidia.com/nim/large-language-models/1.0.0/benchmarking.html)
- [TrueFoundry — LLM-Locust](https://www.truefoundry.com/blog/llm-locust-a-tool-for-benchmarking-llm-performance)
- [LLMPerf](https://github.com/ray-project/llmperf)
- [k6 Operator](https://github.com/grafana/k6-operator)
