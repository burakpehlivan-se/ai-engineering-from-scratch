---
name: skill-convexity-checker
description: Bir optimizasyon probleminin dışbükey (convex) olup olmadığını belirle ve doğru çözücüyü seç
version: 1.0.0
phase: 1
lesson: 18
tags: [optimization, convexity, solvers]
---

# Dışbükeylik Kontrol Edici

Bir optimizasyon probleminin dışbükey (convex) olup olmadığını nasıl doğrularsın ve cevabı ne yaparsın.

## Karar Kontrol Listesi

1. Amaç fonksiyonu dışbükey mi? (Hessian'ın yarı pozitif tanımlılığını kontrol et veya bileşim kurallarını kullan.)
2. Tüm eşitsizlik kısıtlamaları g_i(x) <= 0 biçiminde mi ve her g_i dışbükey mi?
3. Tüm eşitlik kısıtlamaları afin (doğrusal) mi?
4. Üçü de evetse, problem dışbükeydir. Yakınsama garantili bir dışbükey çözücü kullan.
5. Herhangi biri hayırsa, problem dışbükey değildir. SGD/Adam kullan ve yerel en iyi noktaları kabul et.

## Bir fonksiyonun dışbükeyliği nasıl test edilir

| Test | Uygulandığı yer | Yöntem |
|---|---|---|
| İkinci türev >= 0 | Skaler f(x) fonksiyonları | f''(x) hesapla. Her x için f''(x) >= 0 ise, dışbükey. |
| Hessian PSD | Çok değişkenli f(x) | H(x) hesapla. Tüm özdeğerler her yerde >= 0 ise, dışbükey. |
| Tanım testi | Herhangi bir fonksiyon | Örneklenmiş x, y, t için f(tx + (1-t)y) <= t*f(x) + (1-t)*f(y) kontrol et. |
| Bileşim kuralları | Bileşik fonksiyonlar | Aşağıdaki bileşim tablosuna bak. |
| Bir çizgiye kısıtlama | Çok değişkenli f | f dışbükey ancak ve ancak g(t) = f(x + tv) her x, v için t'de dışbükey ise. |

## Bileşim kuralları (dışbükeyliği koruyan)

| İşlem | Sonuç |
|---|---|
| f + g (ikisi de dışbükey) | Dışbükey |
| c * f (c > 0, f dışbükey) | Dışbükey |
| max(f, g) (ikisi de dışbükey) | Dışbükey |
| f(Ax + b) burada f dışbükey | Dışbükey |
| g(f(x)) burada g dışbükey ve artmayan ve f dışbükey | Dışbükey |
| g(f(x)) burada g dışbükey ve azalan ve f içbükey | Dışbükey |
| Dışbükey fonksiyonların toplamı | Dışbükey |
| Dışbükey fonksiyonların noktasal supremumu | Dışbükey |

## Yaygın ML amaçları: dışbükey mi, değil mi?

| Amaç | Dışbükey mi? | Neden |
|---|---|---|
| MSE: (1/n) sum(y - Xw)^2 | Evet | w'da kuadratik, Hessian = (2/n) X^T X PSD |
| Lojistik kayıp: sum(log(1 + exp(-y_i * w^T x_i))) | Evet | Dışbükey fonksiyonların toplamı (log-sum-exp ailesi) |
| Hinge kaybı: sum(max(0, 1 - y_i * w^T x_i)) | Evet | Dışbükey (doğrusal) fonksiyonların max'ı |
| L2 düzenlileştirme: lambda * \|\|w\|\|^2 | Evet | Kuadratik, Hessian = 2*lambda*I |
| L1 düzenlileştirme: lambda * \|\|w\|\|_1 | Evet | Mutlak değerlerin toplamı (dışbükey ama türevi alınamaz) |
| Ridge regresyonu: MSE + L2 | Evet | İki dışbükey fonksiyonun toplamı |
| LASSO: MSE + L1 | Evet | İki dışbükey fonksiyonun toplamı |
| Elastik ağ: MSE + L1 + L2 | Evet | Dışbükey fonksiyonların toplamı |
| SVM (primal): hinge + L2 | Evet | Dışbükey fonksiyonların toplamı |
| Softmax ile çapraz entropi | Evet (logits'lerde) | Log-sum-exp dışbükey |
| Sinir ağı (herhangi bir kayıp) | Hayır | Doğrusal olmayan aktivasyonlar dışbükey olmayan bileşim yaratır |
| k-means amacı | Hayır | Ayrık atama adımı |
| Matris çarpanlarına ayırma: \|\|X - UV^T\|\|^2 | Hayır | U ve V'de bilineer |
| GAN kaybı | Hayır | Minimax, jeneratörde dışbükey değil |
| Karşılaştırmalı kayıp (InfoNCE) | Hayır | Negatif örneklerle üstellerin oranının logaritması |

## Dışbükeyliğe göre çözücü seçimi

| Problem tipi | Çözücü | Yakınsama garantisi |
|---|---|---|
| Dışbükey, pürüzsüz, kısıtlamasız | Gradyan inişi | Küresel en küçüğe O(1/k) |
| Dışbükey, pürüzsüz, kısıtlamasız | L-BFGS | Küresel en küçüğe süperlineer |
| Dışbükey, pürüzsüz, kısıtlamasız | Newton yöntemi | En küçük yakınında kuadratik (Hessian izlenebilirse) |
| Dışbükey, pürüzsüz, kısıtlı | İç nokta yöntemi | Polinom zaman |
| Dışbükey, pürüzsüz olmayan (L1) | Yakınsak gradyan (proximal) / ISTA | Küresel en küçüğe O(1/k) |
| Dışbükey, pürüzsüz olmayan (L1) | ADMM | Esnek, kısıtlamaları işler |
| Dışbükey, kuadratik | Eşlenik gradyan | n adımda tam |
| Dışbükey olmayan, pürüzsüz | SGD / Adam | Yerel en küçüğe yakınsar |
| Dışbükey olmayan, pürüzsüz | SGD + yeniden başlatma | Ortalama olarak daha iyi yerel en küçük |
| Dışbükey olmayan, pürüzsüz | Aşırı parametrele + SGD | Düz en küçükler, iyi genelleme |

## Yaygın hatalar

- Kayıp fonksiyonu dışbükey olduğu için problemin dışbükey olduğunu varsaymak. Kayıp, optimize ettiğin parametrelerde dışbükey olmalıdır. Çapraz entropi logits'lerde dışbükeydir, ancak girdilerden logits'lere giden tam sinir ağı eşlemesi dışbükey değildir.
- Dışbükey olmayan bir problemde Newton yöntemi kullanmak. Hessian'ın negatif özdeğerleri olabilir, bu da Newton'ı en küçükler yerine eyer noktalarına veya en büyüklere doğru hareket ettirir.
- L1 düzenlileştirmesinin amacı sıfırda türevi alınamaz kıldığını unutmak. Standart gradyan inişi iyi çalışmaz. Yakınsak gradyan inişi veya alt-gradyan yöntemleri kullan.
- A^T A oluşturarak koşul sayısını karelemek. En küçük kareler problemi çözmeniz ve A kötü koşullandırılmışsa, normal denklemler yerine QR veya SVD kullan.
- Kontrol etmeden bir problemi dışbükey olmayan ilan etmek. Birçok ML problemi (doğrusal modeller, SVM'ler, lojistik regresyon) dışbükeydir ve daha güçlü çözücülerden faydalanır.

## Hızlı test: problemim dışbükey mi?

```
1. Amacı yaz: f(w)'yi kısıtlamalara tabi olarak enküçült
2. f(w)'deki her terim için:
   - PSD matrisle kuadratik mi? -> Dışbükey
   - Bir norm mu? -> Dışbükey
   - Log-sum-exp mi? -> Dışbükey
   - w'yi doğrusal olmayan şekilde içeriyor mu (sigmoid(w), w1*w2)? -> Muhtemelen dışbükey değil
3. Tüm kısıtlamalar doğrusal veya dışbükey eşitsizlikler mi?
4. TÜM terimler dışbükeyse VE kısıtlamalar dışbükey/doğrusal ise -> problem dışbükey
5. HERHANGİ bir terim dışbükey değilse -> problem dışbükey değil
```
