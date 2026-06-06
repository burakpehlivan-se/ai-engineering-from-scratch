---
name: prompt-tensor-debugger
description: Derin öğrenme kodundaki tensor şekil hataları için adım adım hata ayıklama prompt'u
phase: 1
lesson: 12
---

Derin öğrenme kodumda bir tensor şekil hatası var. Düzeltmeme yardım et.

**Hata mesajı:** [hatayı buraya yapıştır]

**Tensor şekillerim:**
- [isim]: [şekil]
- [isim]: [şekil]

**Yapmaya çalıştığım işlem:** [açıkla]

---

Hata ayıklarken şu tam süreci izle:

**Adım 1: İşlem tipini belirle.**
Hatayı hangi işlem üretti? Şunlardan biriyle eşle:
- Matris çarpımı / Doğrusal katman (iç boyutlar eşleşmeli)
- Yayın (broadcasting) (sağdan hizala, her boyut eşit veya 1 olmalı)
- Birleştirme (concatenation) (cat boyutu dışındaki tüm boyutlar eşleşmeli)
- Evrişim (convolution) (belirli bir rank ve kanal konumu bekler)
- Yeniden şekillendirme (reshape) (toplam elemanlar korunmalı)

**Adım 2: Şekil sözleşmesini yaz.**
Belirlenen işlem için beklenen şekilleri açıkça yaz:
```
matmul(A, B): A is (..., m, k), B is (..., k, n) -> (..., m, n)
broadcast(A, B): sağdan hizala, her çift (eşit) veya (biri 1) olmalı
cat([A, B], dim=d): dim d hariç tüm boyutlar eşleşmeli
Linear(in_f, out_f): girdinin son boyutu in_f'ye eşit olmalı
Conv2d(in_c, out_c, k): girdi (B, in_c, H, W) olmalı
```

**Adım 3: Uyuşmazlığı bul.**
Gerçek şekilleri sözleşmeyle karşılaştır. Kuralı ihlal eden tam boyutu belirle.

**Adım 4: En küçük çözümü seç.**
Bu tablodan seç:

| Belirti | Çözüm |
|---|---|
| Batch boyutu eksik | `.unsqueeze(0)` |
| Kanal boyutu eksik | `.unsqueeze(1)` |
| Fazladan 1 boyutunda boyut | `.squeeze(dim)` |
| matmul iç boyutları yanlış | `.transpose(-1, -2)` veya ağırlık şeklini kontrol et |
| NHWC'den NCHW gerekli | `.permute(0, 3, 1, 2)` |
| NCHW'den NHWC gerekli | `.permute(0, 2, 3, 1)` |
| Doğrusal katman için uzamsal boyutları düzleştir | `.flatten(1)` veya `.reshape(B, -1)` |
| Head'leri ayır: (B,T,D) -> (B,H,T,D/H) | `.reshape(B, T, H, D//H).transpose(1, 2)` |
| Head'leri birleştir: (B,H,T,D/H) -> (B,T,D) | `.transpose(1, 2).reshape(B, T, H*(D//H))` |
| .view() ile bitişik olmayan (non-contiguous) tensor | `.contiguous().view(...)` veya `.reshape(...)` kullan |

**Adım 5: Çözümü doğrula.**
Her adımdaki sonuç şekillerini göster. Herhangi bir reshape boyunca toplam elemanların korunduğunu doğrula. İşlemin şekil sözleşmesinin artık sağlandığını onayla.

**Adım 6: Sessiz hataları kontrol et.**
Şekiller eşleşse bile şunları doğrula:
- Yayının amaçlanan eksen boyunca gerçekleştiğini (yanlışlıkla değil)
- İndirgemenin doğru boyut üzerinde toplam aldığını
- Batch boyutunun (boyut 0) tüm ileri geçiş boyunca hayatta kaldığını
- Boyut sıralaması önemli olduğunda yalnızca reshape yerine transpose + reshape kullanıldığını

Yanıtını şu formatta düzenle:
```
OPERATION: [hangi işlem başarısız oldu]
EXPECTED: [şekil sözleşmesi]
ACTUAL: [sağlanan şekiller]
MISMATCH: [hangi boyut, neden]
FIX: [tam kod]
RESULT: [çözümden sonraki şekiller]
```
