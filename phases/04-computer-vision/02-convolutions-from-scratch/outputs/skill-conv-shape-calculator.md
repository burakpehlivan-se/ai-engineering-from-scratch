---
name: skill-conv-shape-calculator
description: Bir CNN spesifikasyonunu katman katman yürüyün ve her blok için çıktı şeklini, alıcı alanı ve parametre sayısını raporlayın
version: 1.0.0
phase: 4
lesson: 2
tags: [bilgisayarlı-gör, cnn, mimari, hata-ayıklama]
---

# Evrişim Şekli Hesaplayıcısı

Bir CNN'yi planlamak veya hata ayıklamak için belirleyici bir yardımcı. Bir girdi şekli ve katman spesifikasyonları listesi verildiğinde, modeli çalıştırmadan şekilleri, alıcı alanları ve parametre sayılarını izleyin.

## Ne zaman kullanılır

- Yeni bir CNN tasarlıyorsunuz ve her aşağı örneklemenin temiz bir boyuta indiğini doğrulamak istiyorsunuz.
- Bir makaleyi okuyor ve mimari tablosunu koda çeviriyorsunuz.
- Önceden eğitilmiş bir omurga, sınıflandırıcı başında (classifier head) bir şekil uyumsuzluğuyla çöküyor ve hangi katmanın uzamsal boyutu değiştirdiğini bilmeniz gerekiyor.
- İkisini eğitmeden önce iki omurgayı parametre verimliliğinde karşılaştırma.

## Girdiler

- `input_shape`: `(C, H, W)`.
- `layers`: sıralı katman dict'leri listesi. Her biri destekler:
  - `{type: "conv", c_out, k, s, p, groups=1, bias=true}`
  - `{type: "pool", mode: "max"|"avg", k, s, p=0}`
  - `{type: "adaptive_pool", out_h, out_w}`
  - `{type: "flatten"}`
  - `{type: "linear", out_features, bias=true}`

## Adımlar

1. **İzi başlat** `(C, H, W)`, alıcı alan `1`, etkili stride `1`, birikimli parametreler `0` ile.

2. **Her katman için** şu sırayla güncelle:
   - `C_out`'u hesapla (conv/linear) veya `C_in`'i taşı (pool).
   - Evrişim ve havuz için `(H + 2P - K) / S + 1`, adaptif havuz için `out_h/out_w`, lineerden önce flatten çıktı şekli `(C * H * W, 1, 1)`, lineer için skaler `1x1` ile uzamsal çıktıyı hesapla.
   - Alıcı alanı ve etkili stride'ı güncelle:
     - Conv/pool: `RF_new = RF_old + (K - 1) * effective_stride`, `effective_stride *= S`.
     - Adaptif havuz: etkili `S = H_in / out_h` (aşağı yuvarla) ile havuz olarak ele al. `RF_new = RF_old + (H_in - 1) * effective_stride_old`; `effective_stride *= S`. Adaptif havuzun RF'si, önceki tam uzamsal genişliğe eşit olduğunu not et.
     - Flatten / lineer: RF ve etkili stride artık anlamlı değil; bunları flatten'dan önceki değerlere dondur ve sonraki satırlardan çıkar.
   - Parametreleri hesapla:
     - Conv: `C_out * (C_in / groups) * K * K + (C_out if bias else 0)`.
     - Lineer: `out_features * in_features + (out_features if bias else 0)`.
     - Havuz ve flatten: 0.

3. **Sorunları tespit et** ve işaretle:
   - Tamsayı olmayan çıktı boyutu (yanlış hizalanmış stride/padding).
   - Yığının sonundan önce `H_out <= 0`.
   - Alıcı alanın girdi boyutunu aşması (bu noktadan sonra olası hesap israfı).
   - Katman başına parametrelerde yanlış kanal planı düşündüren ani 10x sıçramalar.

4. **Tek bir tablo olarak raporla**:

```
idx  layer                C_in  C_out  K  S  P  H_out  W_out  RF    params     cum_params
1    conv 3x3 s=1 p=1     3     32     3  1  1  224    224    3     896        896
2    conv 3x3 s=2 p=1     32    64     3  2  1  112    112    7     18,496     19,392
3    pool max 2x2         64    64     2  2  0  56     56     11    0          19,392
...
```

5. **Özet satırı**: son `(C, H, W)`, son alıcı alan, toplam parametreler, uyarılar.

## Kurallar

- Uzamsal boyutlar için her zaman tamsayılar döndür. Formül tamsayı olmayan bir değer üretirse, hata olarak işaretle ve sessizce aşağı yuvarlama.
- `groups > 1` olduğunda, `C_in % groups == 0` ve `C_out % groups == 0` olduğunu doğrula; aksi halde hata ver.
- Derinlik-yönlü evrişim (`groups == C_in`) için, `layer` sütununda etiketle ki okuyucu parametrelerin neden düşük olduğunu görsün.
- Kullanıcı BatchNorm veya aktivasyon katmanları sağlarsa, şekil amaçları için yoksay ama parametreleri ileriye taşı (BatchNorm başına `2 * C`).
- Eksik alanlar için varsayılanları asla tahmin etme. Her evrişim ve havuzda `k`, `s`, `p` gerektir.
