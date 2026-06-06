---
name: skill-inference-optimization
description: LLM çıkarım (inference) sunma verimini, gecikmesini ve maliyetini tanılayın ve optimize edin
version: 1.0.0
phase: 10
lesson: 12
tags: [inference, kv-cache, batching, speculative-decoding, vllm, optimization]
---

# LLM Çıkarım Optimizasyon Modeli

İki aşama: ön dolgu (prefill, hesaplama bağımlı, paralel) ve kod çözme (decode, bellek bağımlı, sıralı).
Her optimizasyon birini veya her ikisini hedefler.

```
İstek -> Ön Dolgu (prompt'u işle) -> Kod Çözme (token üret) -> Yanıt
              |                            |
          Hesaplama bağımlı          Bellek bağımlı
          Optimize et: füzyon,       Optimize et: toplu iş,
          önek önbellekleme         nicemleme, spekülasyon
```

## Karar çerçevesi

### Adım 1: Darboğazınızı belirleyin

İş yükünüz için ops:byte oranını ölçün:

| ops:byte | Bağımlılık | Optimize edilecek |
|----------|-------|-----------------|
| < 50 | Bellek | KV cache'i nicemleyin, parti boyutunu artırın |
| 50-200 | Geçiş | İkisi de önemli, toplu işlemle başlayın |
| > 200 | Hesaplama | Çekirdek füzyonu, tensör paralelliği, FP8 |

### Adım 2: Motorunuzu seçin

- **Varsayılan**: vLLM (en geniş model desteği, PagedAttention, OpenAI uyumlu API)
- **Çok turlu / yapılandırılmış çıktı**: SGLang (RadixAttention önek önbellekleme, kısıtlı kod çözme)
- **Maksimum NVIDIA verimi**: TensorRT-LLM (çekirdek füzyonu, H100'de FP8)

### Adım 3: Optimizasyonları sırayla uygulayın

1. **KV cache** -- her zaman açık, dezavantajı yok
2. **Sürekli toplu iş (continuous batching)** -- her zaman açık, dezavantajı yok (vLLM/SGLang bunu varsayılan olarak yapar)
3. **Önek önbellekleme** -- paylaşılan sistem promptlarınız varsa etkinleştirin (çoğu sohbet botu bunu yapar)
4. **Nicemleme** -- KV cache INT8/FP8, belleği minimum kalite kaybıyla 2-4x azaltır
5. **Spekülatif kod çözme** -- gecikme verimden daha önemli olduğunda ekleyin
6. **Tensör paralelliği** -- model tek bir GPU'ya sığmadığında GPU'lar arasında bölün

## KV cache bellek formülü

```
token_başına = 2 * katman_sayısı * kv_kafa_sayısı * kafa_boyutu * parametre_başına_bayt
toplam = token_başına * dizi_uzunluğu * eşzamanlı_kullanıcı_sayısı
```

Yaygın modeller için hızlı referans (BF16):

| Model | Token başına | 4K'da 100 kullanıcı |
|-------|-----------|----------------|
| Llama 3 8B | 32 KB | 12.5 GB |
| Llama 3 70B | 320 KB | 125 GB |
| Llama 3 405B | 504 KB | 197 GB |

## Spekülatif kod çözme kontrol listesi

- Taslak model, hedeften 5-10x küçük olmalı (örneğin, 70B için 8B taslak)
- Anlamlı hızlanma için kabul oranı > %70
- Tahmin edilebilir metin üzerinde en iyi (kod, yapılandırılmış çıktı, doğal dil)
- Yaratıcı/örnekleme ağırlıklı görevlerde en kötü (düşük sıcaklık yardımcı olur)
- Çoğu iş yükü için EAGLE > taslak-hedef > n-gram

## Yaygın hatalar

- Kod çözmeyi parti=1'de çalıştırmak (bellek bağımlı, GPU hesaplamada %95 boşta)
- Bitişik KV cache blokları tahsis etmek (PagedAttention kullanın, sıfıra yakın israf elde edin)
- İsteklerin %80'i aynı sistem promptunu paylaştığında önek önbelleğini göz ardı etmek
- Model ağırlıkları için GPU belleğini fazla tahsis etmek, KV cache için hiçbir şey bırakmamak
- Gecikme ölçmeden verim ölçmek (10s TTFT'de yüksek verim işe yaramaz)
- Yüksek sıcaklıkla spekülatif kod çözme kullanmak (kabul oranı %50'nin altına düşer)

## İzleme kontrol listesi

- İlk token zamanı (TTFT): ön dolgu gecikmesi, interaktif kullanım için hedef < 500ms
- Token arası gecikme (ITL): kod çözme hızı, akış (streaming) için hedef < 50ms
- Verim (saniyede token): tüm eşzamanlı kullanıcılar boyunca toplam
- KV cache kullanımı: tahsis edilen cache'in kullanımda olan yüzdesi
- Parti kullanımı: her iterasyonda doldurulan parti yuvası yüzdesi
- Kuyruk derinliği: parti yuvası bekleyen istekler
