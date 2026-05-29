> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/04-calculus-for-ml/docs/en.md)

# Makine Öğrenmesi İçin Calculus

> Türevler size aşağı yolun neresi olduğunu söyler. Bir sinir ağının öğrenmesi için gereken tek şey budur.

**Tür:** Öğrenme
**Diller:** Python
**Ön Koşullar:** Faz 1, Ders 01-03
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Yaygın ML fonksiyonları için (x^2, sigmoid, çapraz entropi) sayısal ve analitik türevleri hesaplayın
- 1B ve 2B'de bir kayıp fonksiyonunu asgari yapmak için sıfırdan gradyan inişi uygulayın
- Doğrusal regresyon modelinin gradyanını türetin ve manuel ağırlık güncellemeleriyle eğitin
- Hessian matrisini, Taylor serisi yaklaşımlarını ve optimizasyon yöntemleriyle bağlantılarını açıklayın

## Sorun

Milyonlarca ağırlığı olan bir sinir ağınız var. Her ağırlık bir düğümdür. Modeli biraz daha az yanlış yapmak için her düğmeyi hangi yöne çevirmeniz gerektiğini bulmalısınız. Calculas size bu yönü verir.

Calculas olmadan, bir sinir ağı eğitmek rastgele değişiklikler denemek ve en iyisini ummak demek olurdu. Türevlerle, her ağırlığın hatayı nasıl etkilediğini tam olarak bilirsiniz. Her düğmeyi her seferinde doğru yöne çevirirsiniz.

## Kavram

### Türev nedir?

Bir türev değişim oranını ölçer. y = f(x) fonksiyonu için, f'(x) türevi şunu söyler: x'i çok az miktarda kaydırırsanız, y ne kadar değişir?

Geometrik olarak, türev bir noktadaki teğet çizgisinin eğimidir.

**f(x) = x^2:**

| x | f(x) | f'(x) (eğim) |
|---|------|---------------|
| 0 | 0    | 0 (düz, altta) |
| 1 | 1    | 2 |
| 2 | 4    | 4 (bu noktadaki teğet çizgisi eğimi) |
| 3 | 9    | 6 |

x=2'de, eğim 4'tür. x'i çok az sağa kaydırırsanız, y yaklaşık 4 katı kadar artar. x=0'da, eğim 0'dır. Kabağın altındasınız.

Resmi tanım:

```
f'(x) = lim   f(x + h) - f(x)
        h->0  -----------------
                     h
```

Kodda, limiti atlar ve çok küçük bir h kullanırsınız. Bu sayısal türevdir.

### Kısmi türevler: bir anda bir değişken

Gerçek fonksiyonların birçok girdisi vardır. Bir sinir ağı kaybı binlerce ağırlığa bağlıdır. Kısmi türev, bir değişken hariç tüm değişkenleri sabit tutar, sonra o değişkene göre türev alır.

```
f(x, y) = x^2 + 3xy + y^2

df/dx = 2x + 3y     (y'yi sabit say)
df/dy = 3x + 2y     (x'i sabit say)
```

Yapay zekada gradyan, tüm ağırlıklarla ilgili kısmi türevlerin vektörüdür. Her ağırlığın kaybı nasıl etkilediğini söyler.

### Gradyan inişi

Gradyan, en dik yukarı yönü gösterir. Kaybı azaltmak için gradyana TERS yönde hareket edersiniz.

```
w_yeni = w_eski - öğrenme_hızı × gradyan
```

#### Açıklama
Bu, sinir ağı eğitiminin temel formülüdür. Gradyan, ağırlığın kaybı nasıl artırdığını söyler, biz de ters yöne giderek azaltırız.

## Alıştırmalar

1. f(x) = x^3 fonksiyonunun türevini hem analitik hem de sayısal olarak hesaplayın
2. 1D'de basit bir gradyan inişi uygulayın: f(x) = (x-3)^2 fonksiyonunun minimumunu bulun
3. Sigmoid fonksiyonunun türevini türetin

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Türev | "Değişim hızı" | Bir fonksiyonun belirli bir noktadaki değişim oranı |
| Gradyan | "En dik eğim" | Tüm kısmi türevlerin vektörü, en hızlı değişim yönünü gösterir |
| Kısmi türev | "Tek değişkenli türev" | Bir değişken sabit tutularak diğerine göre alınan türev |
| Gradyan inişi | "Minimum arama" | Kaybı azaltmak için ağırlıkları gradyan tersi yönde güncelleme |
| Öğrenme hızı | "Adım boyutu" | Gradyan inişinde her adımda ne kadar hareket edileceğini belirleyen skaler |
| Hessian | "İkinci türev matrisi" | İkinci kısmi türevlerin matrisi, eğrinin eğriliğini gösterir |
