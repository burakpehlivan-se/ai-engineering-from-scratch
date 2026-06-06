# Capstone 07 — Uçtan Uca İnce Ayar (Fine-Tuning) Boru Hattı (Veriden SFT'ye DPO'ya Servise)

> Kendi verileriniz üzerinde eğitilmiş 8B bir model, kendi tercihleriniz üzerinde DPO-hizalanmış, nicelenmiş, spekülatif-çözülmüş ve ölçülebilir $/1M tokenlarla servis edilen. 2026'nın açık yığını Axolotl v0.8, TRL 0.15, yineleme için Unsloth, niceleme için GPTQ/AWQ/GGUF, EAGLE-3 ile servis için vLLM 0.7. Capstone tüm boru hattını tekrarlanabilir şekilde çalıştırmaktır — YAML girdi, servis edilen uç nokta çıktı — ve 2026 Model Açıklık Çerçevesi altında bir model kartı yayınlamaktır.

**Type:** Capstone
**Languages:** Python (pipeline), YAML (configs), Bash (scripts)
**Prerequisites:** Phase 2 (ML), Phase 3 (DL), Phase 7 (transformers), Phase 10 (LLMs from scratch), Phase 11 (LLM engineering), Phase 17 (infrastructure), Phase 18 (safety)
**Phases exercised:** P2 · P3 · P7 · P10 · P11 · P17 · P18
**Time:** 35 saat

## Problem

2026'da her ciddi yapay zekâ ekibi bir ince ayar boru hattını hazır tutuyor. Bunun nedeni bir frontier temel modeli yayınlamaları değil, aşağı yönlü adaptasyonun — alan SFT'si, etiketli tercihlere karşı DPO, spekülatif çözme için damıtılmış taslaklar, EAGLE-3 ile servis — ölçülebilir kazançların yaşadığı yer olmasıdır. Axolotl v0.8 çok-GPU SFT konfigürasyonlarını yönetir. TRL 0.15 DPO ve GRPO'yu yönetir. Unsloth hızlı tek-GPU yineleme sağlar. EAGLE-3 ile vLLM 0.7, kalite kaybı olmadan çözme (decode) çıktısını 2-3x artırır. Araçlar çalışıyor; zanaat YAML'lerde, veri hijyeninde ve eval disiplininin içinde.

Bir 8B temeli (Llama 3.3, Qwen3 veya Gemma 3) görev-özgü veriler üzerinde SFT sonra DPO ile çalıştıracak, servis için niceleyecek ve lm-evaluation-harness, RewardBench-2, MT-Bench-v2 ve MMLU-Pro'ya karşı kazançları ölçeceksiniz. 2026 Model Açıklık Çerçevesi altında bir model kartı üreteceksiniz. Amaç tekrarlanabilirliktir — tek bir komut tüm boru hattını uçtan uca yeniden çalıştırır.

## Concept

Boru hattının beş aşaması var. **Veri**: tekilleştirme (MinHash / Datatrove), kalite süzgeci (Nemotron-CC tarzı sınıflandırıcı), PII temizleme, herkese açık kıyaslama kontaminasyonuna karşı bölünme-hijyeni kontrolü. **SFT**: Axolotl YAML, 8xH100 üzerinde ZeRO-3, kosinüs zamanlaması, paketlenmiş diziler, 2-3 epoch. **DPO veya GRPO**: TRL konfigürasyonu, 1 epoch, ya insan-etiketli ya da model-hakemli tercih çiftleri, beta ayarı. **Nicleme**: Dağıtım esnekliği için GPTQ + AWQ + GGUF. **Servis**: EAGLE-3 spekülatif kafalarla vLLM 0.7 (veya SGLang SpecForge ile), K8s dağıtımı, kuyruk-bekleme üzerinde HPA.

Ablasyonlar teslim edilen şeydir: aynı üç görev-özgü kıyaslamada SFT-only vs SFT+DPO vs SFT+GRPO. Servis metrikleri: token/s bs 1 / 8 / 32'de, EAGLE-3 kabul oranı, $/1M token. Güvenlik değerlendirmesi: Llama Guard 4 geçme oranı. Model kartı: yanlılık değerlendirmeleri, tekrarlanabilirlik tohumları, veri lisanslama.

## Architecture

```
raw data (HF datasets + internal)
    |
    v
Datatrove dedup + Nemotron-CC quality filter + PII scrub
    |
    v
split hygiene (MMLU-Pro contamination check)
    |
    v
Axolotl SFT config (YAML)  ---> 8xH100, ZeRO-3
    |
    v
TRL DPO / GRPO config       ---> 4xH100, 1 epoch
    |
    v
GPTQ + AWQ + GGUF quantize
    |
    v
vLLM 0.7 + EAGLE-3 speculative decoding
    |
    v
K8s deployment, HPA on queue-wait
    |
    v
lm-eval-harness + RewardBench-2 + MT-Bench-v2 + MMLU-Pro
    |
    v
model card (2026 MOF) + safety eval (Llama Guard 4)
```

#### Açıklama

Bu mimari ham veriden servis edilen modele kadar tam boru hattını gösterir. Ham veri önce Datatrove ile tekilleştirilir, Nemotron-CC sınıflandırıcısı ile kalite filtrelenir, Presidio ile PII temizlenir. Bölünme hijyeni aşaması MMLU-Pro kontaminasyon kontrolü yapar. SFT aşaması Axolotl YAML ile 8xH100 üzerinde ZeRO-3 kullanır. DPO/GRPO aşaması TRL ile 1 epoch çalışır. Niceleme aşaması GPTQ, AWQ ve GGUF formatlarını üretir. Servis aşaması EAGLE-3 spekülatif çözme ile vLLM 0.7'yi K8s üzerinde çalıştırır. Son olarak lm-eval-harness, RewardBench-2, MT-Bench-v2 ve MMLU-Pro ile değerlendirme yapılır; sonuçlar 2026 MOF model kartına yazılır.

## Stack

- Veri: Tekilleştirme için Datatrove, kalite için Nemotron-CC sınıflandırıcısı, PII için Presidio
- Temel: Llama 3.3 8B, Qwen3 14B veya Gemma 3 12B
- SFT: ZeRO-3, Flash Attention 3, paketlenmiş diziler ile Axolotl v0.8
- Tercih ayarı: DPO veya GRPO için TRL 0.15; tek-GPU yineleme için Unsloth
- Niceleme: GPTQ (Marlin), AWQ, llama.cpp aracılığıyla GGUF
- Servis: EAGLE-3 spekülatif çözme ile vLLM 0.7 (veya SGLang 0.4 + SpecForge)
- Değerlendirme: lm-evaluation-harness, RewardBench-2, MT-Bench-v2, MMLU-Pro
- Güvenlik değerlendirmesi: Llama Guard 4, ShieldGemma-2
- Altyapı: Kubernetes + NVIDIA cihaz eklentisi, kuyruk-bekleme metriği üzerinde HPA
- Gözlemlenebilirlik: Eğitim için W&B, çıkarım (inference) için Langfuse

## Build It

1. **Veri boru hattı.** Ham korpus üzerinde Datatrove tekilleştirmesi çalıştırın. Nemotron-CC tarzı kalite sınıflandırıcısı uygulayın. Presidio PII'yi temizler. Açık tohumla eğitim/doğrulama bölünmelerini yazın.

2. **Kontaminasyon kontrolü.** Her doğrulama bölünmesi için, MMLU-Pro, MT-Bench-v2, RewardBench-2 test kümelerine karşı MinHash hesaplayın. Her çakışmayı reddedin.

3. **Axolotl SFT.** ZeRO-3, FA3, dizi paketleme ile YAML. 8xH100 üzerinde 2-3 epoch. W&B'ye günlüğe kaydedin.

4. **TRL DPO / GRPO.** SFT kontrol noktasını alın, tercih çiftleri üzerinde bir epoch DPO çalıştırın (veya matematik/kod üzerinde doğrulanabilir bir ödülle GRPO). Beta'yı tarayın.

5. **Nicleme.** Üç niceleme üretin: GPTQ-INT4-Marlin, AWQ-INT4, llama.cpp için GGUF-Q4_K_M. Boyutu ve nominal çıktıyı (throughput) kaydedin.

6. **Spekülatif çözme ile servis.** Red Hat Speculators aracılığıyla eğitilmiş EAGLE-3 taslak kafalarıyla vLLM 0.7 konfigürasyonu. Bs 1 / 8 / 32'de kabul oranını ve kuyruk gecikmesini ölçün. Aynı değerlendirmede Anthropic / OpenAI'ye karşı $/1M token raporlayın.

7. **Değerlendirme matrisi.** Temel, SFT-only, SFT+DPO, SFT+GRPO üzerinde lm-eval-harness, RewardBench-2, MT-Bench-v2, MMLU-Pro çalıştırın. Bir tablo üretin.

8. **Güvenlik değerlendirmesi.** Geliştirme kümesinde Llama Guard 4 geçme oranı. ShieldGemma-2 çıktı süzgeci.

9. **Model kartı.** MOF 2026 şablonu: veri, eğitim, değerlendirme, güvenlik, lisans, YAML'ler ve commit SHA'ları ile tekrarlanabilirlik bölümü.

## Use It

```
$ ./pipeline.sh config/llama3.3-8b-domainX.yaml
[data]    300k deduped, 12k filtered, 280k accepted (seed=7)
[SFT]     3 epochs, 8xH100, 6h12m, val loss 1.42 -> 1.03
[DPO]     1 epoch, beta=0.08, 4xH100, 1h40m
[quant]   GPTQ-INT4 4.6 GB, AWQ-INT4 4.8 GB, GGUF-Q4_K_M 5.1 GB
[serve]   vLLM 0.7, EAGLE-3 acceptance 0.74, p99 126ms @ bs=8
[eval]    MMLU-Pro +3.2, MT-Bench-v2 +0.41, RewardBench-2 +0.08
[card]    model-card.md generated under 2026 MOF
```

#### Açıklama

Bu boru hattı çalıştırma günlüğü her aşamanın somut çıktılarını gösterir. Veri aşaması 300k örnekten 280k kabul eder. SFT aşaması 6 saat 12 dakikada 3 epoch çalıştırır, validasyon kaybı 1.42'den 1.03'e düşer. DPO aşaması 1 saat 40 dakika sürer. Niceleme üç format üretir. Servis aşaması EAGLE-3 kabul oranı %74 ve bs=8'de p99 126ms gösterir. Değerlendirme aşaması MMLU-Pro'da +3.2, MT-Bench-v2'de +0.41 ve RewardBench-2'de +0.08 kazanç bildirir. Sonuçlar 2026 MOF uyumlu bir model kartına yazılır.

## Ship It

`outputs/skill-finetuning-pipeline.md` teslim edilen şeyi tanımlar. Tek bir komut, veriyi SFT'den DPO'ya nicelemeden servisten değerlendirmeye çalıştırır ve bir model kartı artı servis edilen uç nokta yayar.

| Ağırlık | Ölçüt | Nasıl ölçülür |
|:-:|---|---|
| 25 | Temele karşı değerlendirme deltası | Hedef görevlerde ölçülen kazanç (MMLU-Pro, MT-Bench-v2, görev-özgü) |
| 20 | Boru hattı tekrarlanabilirliği | Tek komut aynı tohumlarla uçtan uca yeniden çalışır |
| 20 | Veri hijyeni | Tekilleştirme oranı, PII temizleme kapsamı, kontaminasyon kontrolü yeşil |
| 20 | Servis verimliliği | bs=1/8/32'de token/s, EAGLE-3 kabul oranı, $/1M token |
| 15 | Model kartı + güvenlik değerlendirmesi | 2026 MOF tamlığı + Llama Guard 4 geçme oranı |
| **100** | | |

## Exercises

1. Aynı görev-özgü kıyaslamada SFT-only vs SFT+DPO vs SFT+GRPO çalıştırın. Hangi tercih yönteminin kazandığını ve ne kadar farkla raporlayın.

2. Llama 3.3 8B'yi Qwen3 14B ile değiştirin. Eşleşen kalitede $/1M token'ı ölçün.

3. EAGLE-3 kabul oranını alan verilerinde vs genel ShareGPT'de ölçün. Deltayı ve gecikme bütçeleri için ne anlama geldiğini raporlayın.

4. %1 kontaminasyon enjekte edin (MMLU-Pro yanıtlarını eğitim verilerine sızdırın) ve değerlendirmeyi yeniden çalıştırın. MMLU-Pro doğruluğunun gerçekçi olmayan şekilde sıçradığını izleyin. Bunu yakalayan bir kontaminasyon-kontrolü CI kapısı inşa edin.

5. Tam ince ayara alternatif olarak LoRA SFT ekleyin. 10x düşük bellekte kalite farkını ölçün.

## Key Terms

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|------|----------------------|----------------------------|
| Axolotl | "SFT eğiticisi" | SFT, DPO ve damıtma için birleşik YAML-tabanlı eğitici |
| TRL | "Tercih ayarlayıcısı" | LLM'lerde DPO, GRPO, PPO için Hugging Face kütüphanesi |
| GRPO | "Grup-göreli politika optimizasyonu" | Doğrulanabilir ödüllerle DeepSeek R1'in RL reçetesi |
| EAGLE-3 | "Spekülatif çözme taslağı" | N token ileriyi tahmin eden taslak kafalar; vLLM hedef modelle doğrular |
| MOF | "Model Açıklık Çerçevesi" | Veri, kod, lisans üzerinde model yayınlarını derecelendiren 2026 standardı |
| Kontaminasyon kontrolü | "Bölünme hijyeni" | Eğitime test kümesi sızıntısının MinHash-tabanlı tespiti |
| Kabul oranı | "EAGLE / MTP metriği" | Taslak tokenlardan hedef modelin kabul ettiği oran |

## Further Reading

- [Axolotl documentation](https://axolotl-ai-cloud.github.io/axolotl/) — referans SFT / DPO eğiticisi
- [TRL documentation](https://huggingface.co/docs/trl) — DPO ve GRPO referans uygulamaları
- [Unsloth](https://github.com/unslothai/unsloth) — tek-GPU yineleme referansı
- [DeepSeek R1 paper (arXiv:2501.12948)](https://arxiv.org/abs/2501.12948) — GRPO metodolojisi
- [vLLM + EAGLE-3 documentation](https://docs.vllm.ai) — referans servis yığını
- [SGLang SpecForge](https://github.com/sgl-project/SpecForge) — alternatif spekülatif-çözme eğiticisi
- [Model Openness Framework 2026](https://isocpp.org/) — açık-yayın derecelendirme standardı
- [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) — kanonik değerlendirme çalıştırıcısı
