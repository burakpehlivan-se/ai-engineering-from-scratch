---
name: inference-server
description: EAGLE-3 veya P-EAGLE taslakları, K8s otomatik ölçekleme ve tam verim/gecikme/maliyet raporu ile tahmine dayalı çözümleme (speculative decoding) çıkarım sunucusu gönder
version: 1.0.0
phase: 19
lesson: 14
tags: [capstone, inference, vllm, sglang, eagle-3, p-eagle, speculative-decoding, quantization, hpa]
---

İki açık hedef model (Llama 3.3 70B ve Qwen3-Coder-30B MoE veya GPT-OSS-120B) verildiğinde, tahmine dayalı çözümleme, nicelleştirme ve Kubernetes otomatik ölçekleme ile üretim bir sunma yığını gönder. Ölçülen hızlanmaları ve kuyruk-gecikme sayılarını yayınla.

İnşa planı:

1. FP8 Marlin nicelleştirmesi ile vLLM 0.7 (veya SGLang 0.4) altında hedef modelleri dağıt.
2. Red Hat Speculators'tan hizalanmış bir EAGLE-3 taslağını yükle (veya SpecForge aracılığıyla bir tane eğit).
3. Temel çizgi sayıları: spekülasyon olmadan parti 1/8/32'de token/saniye ve p50/p99 gecikme.
4. EAGLE-3'ü etkinleştir. Aynı kıyaslamayı yeniden çalıştır. Hızlanmayı, kabul oranını, p99 kuyruk-gecikme deltasını raporla.
5. P-EAGLE paralel spekülasyonu etkinleştir; daha derin ağaçların yardımcı olduğu ve zarar verdiği kırılma noktasını raporla.
6. Kıyaslamaları dağılımlar arasında çalıştır: ShareGPT, HumanEval, alan verisi. Kabul-oranı sapmasını yayınla.
7. İkinci hedef modelde (MoE) tekrarla; taslak kabulünde yönlendirme-gürültü hassasiyetini belirle.
8. `queue_wait_ms` izleyen HPA ile Kubernetes üzerinde dağıt. Yük üçe katlandığında ölçek-dışa çıkışı göster.
9. Eşleşmiş değerlendirmelerde Anthropic Claude Sonnet 4.7 ve OpenAI GPT-5.4'e karşı 1M token başına $'ı karşılaştır.

Değerlendirme rubriği:

| Ağırlık | Kriter | Ölçüm |
|:-:|---|---|
| 25 | Temel çizgiye karşı ölçülen hızlanma | Her iki modelde eşleşmiş kalitede 2,5x+ verim |
| 20 | Gerçekçi trafik üzerinde kabul oranı | Dağılım başına kabul-oranı raporu |
| 20 | P99 kuyruk-gecikme disiplini | Spekülasyonla ve olmadan parti 1/8/32'de p99 |
| 20 | Operasyon | K8s dağıtımı, kuyruk-bekleme üzerinde HPA, sorunsuz yayılım, önce-boşaltma yükseltmesi |
| 15 | Yazı ve metodoloji | Metriklerin net türetilmesi, eşleşmiş temel çizgiler |

Kesin redler:

- Kuyruk gecikmesi olmadan kararlı durum verimi raporlama.
- CPU üzerinde HPA. GPU doygunluğu altında çırpınır.
- Taslak-hedef sürüm hizalamasını yok sayma. Sapan taslaklar, spekülasyon olmamasından daha pahalıya mal olur.
- Barındırılan API'lerin istem-önbellek indirimlerini atlayan maliyet karşılaştırmaları.

Ret kuralları:

- Yayılım boşaltması olmadan sunmayı reddet. İstekler uçuyorken yerinde yükseltme diskalifiye edicidir.
- Dağılımlar arasında toplanmış kabul oranı raporlamayı reddet. Dağılım başına zorunludur.
- bs=32'de eşleşmiş spekülatif-olmayan bir sayı olmadan tahmine dayalı çözümleme kazanımları iddia etmeyi reddet.

Çıktı: vLLM / SGLang yapılandırmalarını, EAGLE-3 taslak indirme betiğini, K8s dağıtım manifestolarını, kuyruk-bekleme üzerinde HPA yapılandırmasını, ShareGPT / HumanEval / alan verisi için kıyaslama iskeletini, 1M token başına $ karşılaştırma tablosunu ve tahmine dayalı çözümlemenin tanıttığı en büyük üç kuyruk-gecikme regresyonunu ve her birini düzelten hafifletmeyi (parti geçitleme, n-gram geri-dönüşü, nicelleştirme ince ayarı) adlandıran bir yazıyı içeren bir depo.
