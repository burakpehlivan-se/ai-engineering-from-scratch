---
name: skill-noise-schedule-designer
description: T ve hedef bozulma seviyesi verildiğinde doğrusal, kosinüs veya sigmoid beta takvimi üretin, ayrıca SNR (sinyal-gürültü oranı) grafiği
version: 1.0.0
phase: 4
lesson: 10
tags: [bilgisayarlı-gör, difüzyon, gürültü-takvimi, eğitim]
---

# Gürültü Takvimi Tasarımcısı

Bir beta takvimi, her difüzyon adımında ne kadar sinyalin korunduğunu kontrol eder. Kötü takvimler, eğitim verimliliğini ve örnek kalitesini her aşağı akış kararında sınırlar.

## Ne zaman kullanılır

- Yeni bir difüzyon eğitim çalıştırması başlatırken ve T ile beta'yı seçerken.
- Bulanık örnekler üreten (takvim çok agresif) veya yapı öğrenemeyen (takvim çok yumuşak) bir difüzyon modelini ayıklarken.
- Farklı takvimler raporlayan makaleler genelinde tasarımları karşılaştırırken.

## Girdiler

- `T`: zaman adımlarının sayısı, tipik olarak 100-1000.
- `type`: linear | cosine | sigmoid.
- `target_alpha_bar_final`: t=T'de tutulan sinyal kesri, varsayılan 0.001 (%99.9 bozulmuş).
- İsteğe bağlı `image_resolution` — daha büyük görüntüler, daha yavaş bozulan takvimlerden (kosinüs veya kaydırılmış takvimler) yararlanır.

## Takvim formülleri

### Doğrusal
```
beta_t = beta_start + (beta_end - beta_start) * (t - 1) / (T - 1)
```
Varsayılanlar: beta_start=1e-4, beta_end=0.02 (DDPM makalesi).

### Kosinüs (Nichol & Dhariwal, 2021)
```
alpha_bar_t = cos^2((t/T + s) / (1 + s) * pi/2)
beta_t = 1 - alpha_bar_t / alpha_bar_{t-1}
```
s = 0.008. Sinyali daha uzun tutar; düşük adım sayılarında daha iyi.

### Sigmoid
```
alpha_bar_t = 1 / (1 + exp(k * (t/T - 0.5)))
```
k = 6 ila 12. İyi bir orta yol; bazı SDXL varyantları tarafından kullanılır.

## Adımlar

1. Formüle göre betaları hesaplayın.
2. `alphas`, `alphas_cumprod`, `sqrt_alphas_cumprod`, `sqrt_one_minus_alphas_cumprod`'u önceden hesaplayın.
3. SNR_t = alpha_bar_t / (1 - alpha_bar_t) hesaplayın; zaman içinde SNR özeti üretin.
4. `alphas_cumprod[T-1]`'in `target_alpha_bar_final`'ın %10'u içinde olduğunu doğrulayın; aksi halde beta_end (doğrusal), s (kosinüs) veya k (sigmoid) ayarlayın ve yeniden deneyin.
5. Üç kontrol noktasını raporlayın:
   - `t=T*0.25` — erken bozulma
   - `t=T*0.5` — orta yol
   - `t=T*0.75` — sona yakın

## Rapor

```
[schedule]
  type:   <isim>
  T:      <int>
  beta_start: <float>   beta_end: <float>

[signal retention]
  t=0.25T:  alpha_bar=<X>  SNR=<X>
  t=0.5T:   alpha_bar=<X>  SNR=<X>
  t=0.75T:  alpha_bar=<X>  SNR=<X>
  t=T:      alpha_bar=<X>  SNR=<X>

[warnings]
  - <alpha_bar 0.75T'den önce çökerse>
  - <beta_end log-SNR'da NaN üretirse>
```

## Kurallar

- Herhangi bir `alpha_bar_t <= 0` olan bir takvimi asla yayınlamayın; 1e-5'in altındaki değerleri sıkıştırın ve uyarı verin.
- Düşük adım sayılı örnekleme (< 30 adım) için kosinüs varsayılan öneridir.
- `quality_target == research` için doğrusal varsayılandır — DDPM temel çizgileri doğrusal takvimlerle raporlanır.
- `image_resolution > 256` olduğunda, yüksek çözünürlüklerde daha fazla sinyal tutmak için takvimi kaydırmayı (Chen, 2023) önerin.
