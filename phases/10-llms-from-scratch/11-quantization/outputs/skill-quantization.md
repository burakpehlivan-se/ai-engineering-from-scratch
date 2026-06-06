---
name: skill-quantization
description: Donanım, kalite ve gecikme kısıtlamalarına göre LLM'leri dağıtmak için doğru nicemleme (quantization) stratejisini seçin
version: 1.0.0
phase: 10
lesson: 11
tags: [quantization, inference, deployment, optimization, fp8, int4, int8, gptq, awq, gguf]
---

# Nicemleme Karar Çerçevesi

Bir dil modelini dağıtırken, doğru sayı formatını, nicemleme yöntemini ve kalite doğrulama stratejisini seçmek için bu çerçeveyi kullanın.

## Girdi Gereksinimleri

Şunları sağlayın:
- **Model** (ad, parametre sayısı, orijinal hassasiyet)
- **Hedef donanım** (GPU modeli/VRAM, CPU, Apple Silicon, uç cihaz)
- **Gecikme hedefi** (saniyede token, ilk token zamanı)
- **Kalite tabanı** (kabul edilebilir maksimum karmaşıklık artışı, kıyaslama deltası)
- **Sunma deseni** (parti boyutu, maksimum bağlam uzunluğu, eşzamanlı kullanıcılar)

## Hızlı Seçim

| Durumunuz | Format | Yöntem | Beklenen Kalite Kaybı |
|---------------|--------|--------|----------------------|
| H100 GPU, maksimum verim | FP8 E4M3 | Yerel H100 dönüşümü | < %0.1 |
| A100/A10, 2x verim gerekli | INT8 | LLM.int8() veya SmoothQuant | < %0.5 |
| Tek 24GB GPU, 70B model | INT4 | AWQ veya GPTQ | %1-3 |
| MacBook / Apple Silicon | INT4 GGUF | llama.cpp aracılığıyla Q4_K_M | %1-2 |
| Mobil / uç cihaz | INT4 veya INT3 | QAT + cihaza özgü | %2-5 |
| Maksimum sıkıştırma, biraz kayıp kabul edilir | INT2 | QuIP# veya AQLM | %5-15 |
| Eğitim (karma hassasiyet) | BF16 + FP32 accum | Yerel çerçeve desteği | %0 |

## Bileşene Göre Hassasiyet Seçimi

Tüm tensörler aynı işlemi görmemelidir.

| Bileşen | Güvenli Minimum | Önerilen | Kaçınılması Gereken |
|-----------|-------------|-------------|-------|
| FFN ağırlıkları | INT4 | INT4 (AWQ/GPTQ) | QAT olmadan INT2 |
| Attention ağırlıkları | INT4 | INT8 veya FP8 | INT2 |
| Embedding katmanı | INT8 | FP16 (orijinali koruyun) | INT4 |
| Çıktı kafası | INT8 | FP16 (orijinali koruyun) | INT4 |
| KV cache | FP8 | FP8 veya INT8 | Uzun bağlamda INT4 |
| Attention logits | FP16 | FP16 veya BF16 | INT8 |
| Aktivasyonlar (çıkarım) | INT8 | FP8 veya INT8 | INT4 |

## Yöntem Karşılaştırması

### GPTQ

- **Ne zaman:** GPU çıkarımı, Hugging Face uyumlu bir model istiyorsunuz
- **Kalibrasyon verisi:** 128 örnek, her biri 2048 token
- **Süre:** A100'de 70B için 30-60 dakika
- **Araçlar:** `auto-gptq`, `exllama`, `exllamav2`
- **Güçlü yön:** İyi test edilmiş, Hugging Face'te devasa model koleksiyonu
- **Zayıf yön:** AWQ'dan uygulaması daha yavaş, bazı modellerde AWQ'dan biraz düşük kalite

### AWQ

- **Ne zaman:** GPU çıkarımı, bit başına en iyi kalite istiyorsunuz
- **Kalibrasyon verisi:** 128 örnek
- **Süre:** A100'de 70B için 15-30 dakika
- **Araçlar:** `autoawq`, `vLLM` (yerel destek)
- **Güçlü yön:** En iyi INT4 kalitesi, uygulaması hızlı, vLLM entegrasyonu
- **Zayıf yön:** GPTQ'dan daha küçük model koleksiyonu

### GGUF

- **Ne zaman:** CPU çıkarımı, Apple Silicon, llama.cpp ekosistemi
- **Varyantlar:** Q2_K, Q3_K_S/M/L, Q4_K_S/M, Q5_K_S/M, Q6_K, Q8_0, F16
- **Önerilen varsayılan:** Q4_K_M (en iyi kalite/boyut dengesi)
- **Araçlar:** `llama.cpp`, `ollama`, `LM Studio`
- **Güçlü yön:** Kendi kendine yeten dosyalar, karma hassasiyet, devasa ekosistem
- **Zayıf yön:** GPU için optimal değil (CPU/Metal için tasarlandı)

### SmoothQuant

- **Ne zaman:** GPU'da INT8, hem ağırlık hem aktivasyon nicemlemesi gerekli
- **Anahtar fikir:** Kanal başına ölçeklendirme yoluyla nicemleme zorluğunu aktivasyonlardan ağırlıklara taşır
- **Araçlar:** `smoothquant`, `TensorRT-LLM`
- **Güçlü yön:** 2x hızlanma için W8A8'yi (hem ağırlıklar hem aktivasyonlar INT8'de) etkinleştirir
- **Zayıf yön:** Yalnızca INT8, INT4'e genişlemez

## Kalite Doğrulama Protokolü

Nicemledikten sonra, dağıtmadan önce doğrulayın:

1. **Karmaşıklık (Perplexity) testi.** WikiText-2 veya alan derleminiz üzerinde hesaplayın. Delta < 0.5 mükemmel, 0.5-1.0 iyi, > 2.0 sorunlu.

2. **Kıyaslama taraması.** MMLU (genel), GSM8K (matematik), HumanEval (kod) çalıştırın. Matematik ve kod, hassasiyet kaybına en duyarlı olanlardır.

3. **Çıktı karşılaştırması.** Hem orijinal hem nicemlenmiş modelden 100 yanıt üretin. Kazanma oranını hesaplamak için LLM-as-judge kullanın. Hedef: nicemlenmiş model, prompt'ların > %90'ında kazanır veya berabere kalır.

4. **Gecikme ölçümü.** Parti boyutu 1'de ve hedef parti boyutunuzda saniye/token sayısını ölçün. Hızlanmanın kalite maliyetini haklı çıkarıp çıkarmadığını doğrulayın.

5. **Uzun bağlam testi.** Uzun bağlam (> 4K token) sunuyorsanız, maksimum bağlam uzunluğunuzda test edin. KV cache nicemleme hataları dizi uzunluğuyla birleşir.

## Bellek Bütçesi Hesaplayıcısı

```
Ağırlık belleği (GB) = parametreler (B) * bit / 8 / 1.073741824
Token başına KV cache (MB) = 2 * katman_sayısı * d_model * bit / 8 / 1048576
Bağlam için KV cache (GB) = token başına_kv * maks_bağlam_uzunluğu / 1024
Aktivasyon belleği (GB) ~ 1-4 GB (nispeten sabit, parti boyutuna bağlı)
Toplam = ağırlık_belleği + kv_cache + aktivasyon_belleği + ek yük (%10-20)
```

32K bağlamda Llama 3 70B için INT4 örneği:
- Ağırlıklar: 70B * 4 / 8 / 1.07 = 32.6 GB
- KV cache (FP16): 2 * 80 * 8192 * 16 / 8 / 1e9 * 32768 = ~40 GB
- KV cache (FP8): ~20 GB
- FP8 KV ile toplam: ~55 GB (tek bir 80GB A100'e sığar)

## Yaygın Hatalar

| Hata | Neden Başarısız Olur | Çözüm |
|---------|-------------|-----|
| Embedding katmanını INT4'e nicemleme | İlk katman hataları tüm model boyunca büyütür | Embedding'leri FP16 veya INT8'de tutun |
| INT4 için tensör başına ölçekler kullanma | Tek bir aykırı değer satırı tüm satırların hassasiyetini yok eder | Kanal veya grup başına ölçekler kullanın |
| GPTQ/AWQ kalibre etmeme | Temsili veri olmadan ölçek faktörleri yanlış | Alanınızdan 128 örnek kullanın |
| Tüm katmanlar için aynı bit genişliği | İlk/son katmanlar daha hassasiyete duyarlı | Karma hassasiyet: ilk/son için daha yüksek bitler |
| Çok uzun bağlamda KV cache'i nicemleme | Hatalar dizi uzunluğuyla karesel olarak birleşir | KV cache için FP8 kullanın, INT4 değil |
| Kalite doğrulamasını atma | Bazı modeller kötü nicemlenir (özellikle sınırlarda) | Her zaman karmaşıklık + görev değerlendirmeleri çalıştırın |

## Dağıtım Tarifleri

### Tarif 1: vLLM ile AWQ (GPU sunucusu)
```
pip install vllm autoawq
vllm serve model-awq --quantization awq --dtype half --max-model-len 8192
```

### Tarif 2: llama.cpp ile GGUF (MacBook)
```
./llama-server -m model.Q4_K_M.gguf -c 4096 -ngl 99
```

### Tarif 3: TensorRT-LLM ile FP8 (H100)
```
trtllm-build --model_dir model --output_dir engine --dtype float16 --use_fp8
```
