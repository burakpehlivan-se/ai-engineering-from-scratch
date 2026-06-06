---
name: finetuning-pipeline
description: Ablasyonlar, nicelleştirme ve 2026 Model Açıklığı Çerçevesi (MOF) model kartı ile yeniden üretilebilir bir veri-SFT-DPO-sunma ince-ayar hattı çalıştır
version: 1.0.0
phase: 19
lesson: 07
tags: [capstone, fine-tuning, axolotl, trl, dpo, grpo, vllm, eagle-3, mof]
---

Bir temel model (Llama 3.3 8B, Qwen3 14B veya Gemma 3 12B) ve göreve özgü bir veri kümesi verildiğinde, sunulan bir uç nokta ve yeniden üretilebilir bir model kartı üreten tek-komut bir hat inşa et.

İnşa planı:

1. Veri aşaması: Datatrove dedup, Nemotron-CC-tarzı kalite filtresi, Presidio PII temizleme, tohumlu eğitim/doğrulama bölünmeleri.
2. Kirlenme kontrolü: MMLU-Pro, MT-Bench-v2, RewardBench-2'ye karşı MinHashLSH. Örtüşmede reddet.
3. SFT: 8xH100 üzerinde ZeRO-3, Flash Attention 3, paketlenmiş diziler, 2-3 epokla Axolotl v0.8.
4. Tercih ayarı: 1 epok için TRL 0.15 DPO (veya doğrulanabilir ödüllerle GRPO), beta taraması.
5. Nicelleştir: GPTQ-INT4-Marlin + AWQ-INT4 + GGUF-Q4_K_M.
6. Sun: EAGLE-3 tahmine dayalı çözümleme ile vLLM 0.7 (Red Hat Speculators veya SGLang SpecForge aracılığıyla taslak kafalar). Kuyruk-bekleme üzerinde HPA ile K8s dağıtımı.
7. Değerlendir: temel/SFT-only/SFT+DPO/SFT+GRPO boyunca lm-evaluation-harness, RewardBench-2, MT-Bench-v2, MMLU-Pro.
8. Güvenlik: Llama Guard 4 geçme oranı, ShieldGemma-2 çıktı filtresi.
9. Veri, eğitim, değerlendirme, güvenlik, yeniden-üretilebilirlik bölümleriyle 2026 Model Açıklığı Çerçevesi altında model kartı.

Değerlendirme rubriği:

| Ağırlık | Kriter | Ölçüm |
|:-:|---|---|
| 25 | Temele karşı değerlendirme deltası | MMLU-Pro, MT-Bench-v2, göreve özgü kıyaslamalarda ölçülen kazanç |
| 20 | Hat yeniden-üretilebilirliği | Aynı tohumlarla tek-komut yeniden çalıştırma, eşleşen karmalar verir |
| 20 | Veri hijyeni | Dedup oranı, PII temizleme kapsamı, kirlenme kontrolü yeşil |
| 20 | Sunma verimliliği | Parti 1/8/32'de token/saniye, EAGLE-3 kabul oranı, 1M token başına $ |
| 15 | Model kartı + güvenlik değerlendirmesi | 2026 MOF tamlığı + Llama Guard 4 geçme oranı |

Kesin redler:

- MinHash kirlenme kontrolünü atlayan hatlar. MMLU-Pro'nun eğitime sızması klasik değerlendirme-hile başarısızlık kipidir.
- Tohumlar veya YAML'lar eklenmemiş eğitim çalıştırmaları. Yeniden-üretilebilirlik sert gereksinimdir.
- EAGLE-3 veya eşdeğeri tahmine dayalı çözümleme yapılandırması olmadan sunma. Temel token/saniye 2026 çıtası değildir.
- Eksik güvenlik değerlendirmesi. Her ince-ayar, bir Llama Guard 4 geçme oranıyla gelir.

Ret kuralları:

- lm-eval-harness commit SHA'sını eklemeden kıyaslama puanları iddia eden bir model kartı yayınlamayı reddet.
- Türetilmiş modelleri yasaklayan lisansa sahip veriler üzerinde ince ayar yapmayı reddet. MOF, veri lisanslamasını derecelendirir.
- Değerlendirme matrisi üzerinde kalite kaybını ölçmeden nicelleştirilmiş bir model göndermeyi reddet.

Çıktı: Hat düzenleyiciyi, Llama 3.3 8B + bir alternatif temel için YAML'ları, SFT ve DPO W&B çalıştırma günlüklerini, nicelleştirilmiş artefaktları, sunulan uç noktayı, üç-kıyaslama değerlendirme matrisini, güvenlik değerlendirmesini, 2026 MOF model kartını ve yakaladığınız ve düzelttiğiniz en büyük üç veri-hijyeni sorununu açıklayan bir yazıyı içeren bir depo.
