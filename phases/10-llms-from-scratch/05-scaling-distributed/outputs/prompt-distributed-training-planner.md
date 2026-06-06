---
name: prompt-distributed-training-planner
description: Model boyutu ve mevcut donanım verildiğinde dağıtılmış bir eğitim çalışmasını planlayın
version: 1.0.0
phase: 10
lesson: 5
tags: [distributed-training, fsdp, deepspeed, tensor-parallelism, pipeline-parallelism, scaling]
---

# Dağıtılmış Eğitim Planlayıcı

Büyük bir dil modeli için dağıtılmış eğitim çalışması planlarken, paralellik stratejisini, bellek bütçesini, iletişim ek yükünü ve beklenen verimi belirlemek için bu çerçeveyi kullanın.

## Girdi Gereksinimleri

Sağlayın:
- **Model boyutu** (milyar cinsinden parametreler)
- **Hedef eğitim token'ları** (trilyon cinsinden)
- **Mevcut GPU'lar** (tür: A100/H100/H200, sayı, ara bağlantı: NVLink/InfiniBand)
- **GPU belleği** (A100/H100 için 80GB, H200 için 141GB)
- **Düğümler** (düğüm başına GPU, düğüm sayısı)
- **Bütçe kısıtlamaları** (maks. dolar maliyeti, maks. duvar saati süresi)

## Adım 1: Bellek Bütçesi

GPU başına her bileşen için belleği hesaplayın:

| Bileşen | Formül | FP16 | FP32 |
|-----------|---------|------|------|
| Ağırlıklar | parametre x bayt_başına_parametre | parametre x 2 | parametre x 4 |
| Adam eniyileyici (m + v) | parametre x 4 x 2 | her zaman 8 bayt/parametre | 8 bayt/parametre |
| Gradyanlar | parametre x bayt_başına_parametre | parametre x 2 | parametre x 4 |
| Aktivasyonlar (tahmin) | seq_len x batch x hidden x katmanlar x 2 | değişir | değişir |

Toplam GPU belleğini aşarsa, paylaştırma (sharding) gereklidir. Sırayla deneyin:
1. ZeRO-1 (yalnızca eniyileyici parçaları) -- en ucuz iletişim
2. ZeRO-2 (+ gradyanlar) -- orta iletişim
3. FSDP/ZeRO-3 (+ ağırlıklar) -- en yüksek iletişim ama maksimum bellek tasarrufu
4. Aktivasyonlar hâlâ çok büyükse aktivasyon kontrol noktası ekleyin
5. Tek bir katman bir GPU'ya sığmıyorsa tensör paralelliği ekleyin

## Adım 2: Paralellik Stratejisi

### Karar Ağacı

1. **Tek bir katman bir GPU'ya sığıyor mu?**
   - Hayır: Tensör paralelliğine ihtiyacınız var. TP = 2, 4 veya 8 ayarlayın (bir düğüm içinde).
   - Evet: Tensör paralelliğini atlayın.

2. **Tam model (paylaştırma ile) bir düğümdeki GPU'lara sığıyor mu?**
   - Hayır: İşlem hattı paralelliğine ihtiyacınız var. PP = düğüm sayısı / gruplar ayarlayın.
   - Evet: İşlem hattı paralelliğini atlayın.

3. **Veri paralelliği için kaç GPU kaldı?**
   - DP = toplam_gpu / (TP x PP)

4. **Veri paralel grubu içinde hangi paylaştırma seviyesi?**
   - FSDP (ZeRO-3) ile başlayın. İletişim darboğazsa ZeRO-2 veya ZeRO-1'e düşürün.

### Tipik Yapılandırmalar

| Model Boyutu | Toplam GPU | TP | PP | DP | Paylaştırma |
|-----------|-----------|----|----|-----|----------|
| 7B | 8 | 1 | 1 | 8 | FSDP |
| 13B | 16 | 2 | 1 | 8 | FSDP |
| 70B | 64 | 8 | 1 | 8 | FSDP |
| 70B | 128 | 8 | 2 | 8 | FSDP |
| 405B | 16.384 | 8 | 16 | 128 | FSDP |

## Adım 3: İletişim Analizi

Eğitim adımı başına iletişim hacmini tahmin edin:

- **Veri paralel (all-reduce)**: adım başına 2 x gradyan_boyutu x (N-1)/N
- **FSDP (all-gather + reduce-scatter)**: adım başına ~3 x ağırlık_boyutu x (N-1)/N (DP'den daha yüksek)
- **Tensör paralel (katman başına all-reduce)**: adım başına 2 x aktivasyon_boyutu x katman_sayısı (NVLink gerektirir)
- **İşlem hattı paralel (noktadan noktaya)**: aşama sınırı başına aktivasyon_boyutu (minimum)

İletişim süresi hesaplama süresinin %20'sini aşarsa, strateji iletişim-bağımlıdır. Çözümler:
- Gradyan birikimi (all-reduce sıklığını azaltın)
- Hesaplama ile iletişimi örtüştürün (FSDP bunu varsayılan olarak yapar)
- Mikro-batch boyutunu artırın (daha iyi hesaplama-iletişim oranı)
- Daha az iletişim-ağır bir paylaştırma aşamasına geçin

## Adım 4: Verim ve Maliyet Tahmini

**Eğitim adımı başına FLOPS:**
- İleri: ~2 x parametre x batch_başına_token
- Geri: ~4 x parametre x batch_başına_token (ilerinin 2 katı)
- Toplam: ~6 x parametre x batch_başına_token

**Eğitim süresi:**
- toplam_flops = 6 x parametre x toplam_token
- süre_saniye = toplam_flops / (gpu_sayısı x gpu_tflops x 1e12 x kullanım)
- Tipik kullanım: %35-45 (iletişim, işlem hattı baloncukları, bellek ek yükü için)

**Maliyet:**
- toplam_gpu_saat = gpu_sayısı x süre_saniye / 3600
- maliyet = toplam_gpu_saat x gpu_saat_başına_maliyet

## Adım 5: Doğrulama Kontrol Listesi

Başlatmadan önce:

1. GPU başına bellek donanım sınırına uyuyor (%10 boşlukla)
2. Etkili batch boyutu hedefle eşleşiyor (gpu_başına_batch x DP x gradyan_birikim_adımları)
3. İletişim-hesaplama oranı %20'nin altında
4. İşlem hattı baloncuğu kesri %15'in altında (yeterli mikro-batch)
5. Öğrenme hızı etkili batch boyutu için ölçeklendirildi
6. Kontrol noktası sıklığı başarısızlık olasılığını hesaba katıyor (büyük çalışmalar için 1-2 saatte bir kaydedin)
7. Gradyan kırpma ayarlandı (büyük modeller için tipik olarak 1.0)
8. Isınma adımları toplam adımlarla orantılı (tipik olarak toplamın %0.1-1'i)

## Kırmızı Bayraklar

- **TP > 8**: Düğümler arası tensör paralelliği (InfiniBand üzerinden) neredeyse her zaman işlem hattı paralelliğinden daha yavaştır
- **İşlem hattı aşamaları > 32**: Birçok mikro-batch ile bile baloncuğu ek yükü önemli hale gelir
- **Etkili batch boyutu > 10M token**: Azalan getiriler; yakınsamaya zarar verebilir
- **%30'un altında kullanım**: İletişim-bağımlı -- paralellik stratejisini yeniden değerlendirin
- **13B üzerinde aktivasyon kontrol noktası yok**: Geri geçiş sırasında bellek yetersiz kalacak
- **Küçük GPU başına batch ile gradyan birikimi yok**: Gradyan gürültüsü artar; 256+ örnek etkili batch'e biriktirin
