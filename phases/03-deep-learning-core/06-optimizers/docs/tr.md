> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/03-deep-learning-core/06-optimizers/docs/en.md)

# Optimize Ediciler

> Gradyan inişi hangi yönde hareket edeceğinizi söyler. Ama ne kadar uzağa veya ne kadar hızlı gideceğinizi söylemez. SGD bir pusuladır. Adam, trafik verileriyle GPS'tir.

**Tür:** Uygulama
**Diller:** Python
**Ön Koşullar:** Ders 03.05 (Kayıp Fonksiyonları)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- SGD, momentumlu SGD, Adam ve AdamW optimize edicilerini Python ile sıfırdan uygulayın
- Adam'ın önyargı düzeltmesinin erken eğitim adımlarında sıfıralanmış moment tahminlerini nasıl telafi ettiğini açıklayın
- Neden AdamW'ın aynı görevde L2 düzenlemesiyle Adam'dan daha iyi genelleme sağladığını gösterin
- Transformer, CNN, GAN ve ince ayar için uygun optimize ediciyi ve varsayılan hiperparametreleri seçin

## Sorun

Gradyanları hesapladınız. 4.721 numaralı ağırlığın kaybı azaltmak için 0.003 azaltması gerektiğini biliyorsunuz. Ama 0.003 hangi birimde? Neyle ölçeklendi? Ve 1. adımda hareket ettiğiniz miktarda 1.000. adımda da mı hareket etmelisiniz?

Saf gradyan inişi, her parametreye her adımda aynı öğrenme hızını uygular: w = w - lr × gradyan. Bu, sinir ağı eğitiminin pratikte acı verici olmasına neden olan üç sorun yaratır.

Birincisi, salınım. Kayıp manzarası nadiren pürüzsüz bir kase şeklindedir. Daha çok uzun, dar bir vadiye benzer. Gradyan vadiden geçer (dik yön), boyunca değil (sığ yön). Gradyan inişi, dar boyutta ileri geri zıplarken yararlı olan boyutta çok küçük ilerleme kaydeder.

İkincisi, tüm parametreler için tek öğrenme hızı yanlıştır. Bazı ağırlıkların büyük güncellemelere ihtiyacı vardır (erken, yetersiz uyum aşamasındadırlar). Diğerlerinin çok küçük güncellemelere ihtiyacı vardır (optimum değerlerine yakındırlar). Birincisi için çalışan öğrenme hızı ikincisini bozar ve tersi.

Üçüncüsü, eyer noktaları. Yüksek boyutlarda, kayıp manzarasında gradyanın sıfıra yakın olduğu geniş düzlük bölgeleri vardır. Saf SGD bunları gradyan hızıyla geçer, ki bu etkili olarak sıfırdır. Model takılmış görünür. Takılmamıştır — faydalı bir aşağı inişin olduğu düz bir bölgededir. Ama SGD'nin bunu aşma mekanizması yoktur.

Adam üçünü de çözer. Her parametre için iki akan ortalama tutar — ortalama gradyan (momentum, salınımı ele alır) ve ortalama kare gradyan (adaptif hız, farklı ölçekleri ele alır). İlk birkaç adım için önyargı düzeltmesiyle birleştirildiğinde, varsayılan hiperparametrelerle %80 sorunda çalışan tek bir optimize edici verir.

## Kavram

### Stokastik Gradyan İnişi (SGD)

En basit optimize edici. Toplu iş üzerinde gradyanı hesaplayın ve ters yönde adım atın.

```
w = w - lr × gradyan
```

"Stokastik", gradyanı tam veri seti yerine rastgele bir alt küme (toplu iş) ile kestirmeniz anlamına gelir. Bu gürültü aslında yararlıdır — keskin yerel minimumlardan kurtulmaya yardımcı olur. Ama gürültü aynı zamanda salınım yapar.

Öğrenme hızı tek düğmedir. Çok yüksek: kayıp ayrışır. Çok düşük: eğitim sonsuza kadar sürer. Değer, mimariye, veriye, toplu iş boyutuna ve eğitim aşamasına bağlıdır.

### Momentum

Topu yuvarlama benzetmesi aşıdır ama doğrudur. Sadece gradyanla adım atmak yerine, geçmiş gradyanları biriktiren bir hız sürdürürsünüz.

```
m_t = beta × m_{t-1} + gradyan
w = w - lr × m_t
```

Beta (genellikle 0.9) ne kadar geçmiş tutulacağını kontrol eder. Beta = 0.9 ile momentum yaklaşık olarak son 10 gradyanın ortalamasıdır.

Bu neden salınımı düzeltir: aynı yönde işaretli gradyanlar birikir. Yönü değişen gradyanlar birbirini götürür. Dar vadide "geçiş" bileşeni her adımda işaret değiştirir ve bastırılır. "Boyunca" bileşeni tutarlı kalır ve büyütülür. Sonuç, yararlı yönde pürüzsüz hızlanmadır.

### RMSProp

İlk çalışan parametre başına adaptif öğrenme hızı yöntemi. Hinton tarafından bir Coursera dersinde önerildi (hiç resmi olarak yayınlanmadı).

```
s_t = beta × s_{t-1} + (1 - beta) × gradyan²
w = w - lr × gradyan / (√s_t + ε)
```

s_t, kare gradyanların akan ortalamasını takip eder. Tutarlı olarak büyük gradyanlara sahip parametreler büyük bir sayıya bölünür (daha küçük etkili öğrenme hızı). Küçük gradyanlara sahip parametreler küçük bir sayıya bölünür (daha büyük etkili öğrenme hızı).

Epsilon (genellikle 1e-8), bir parametre henüz güncellenmediğinde sıfıra bölmeyi önler.

### Adam: Momentum + RMSProp

Adam her iki fikri birleştirir. Her parametre için iki üstel hareketli ortalama sürdürür:

```
m_t = beta1 × m_{t-1} + (1 - beta1) × gradyan        (birinci moment: ortalama)
v_t = beta2 × v_{t-1} + (1 - beta2) × gradyan²       (ikinci moment: kare ortalama)
```

Önyargı düzeltmesi (ilk birkaç adım için):

```
m_t_düzeltme = m_t / (1 - beta1^t)
v_t_düzeltme = v_t / (1 - beta2^t)
```

Güncelleme:

```
w = w - lr × m_t_düzeltme / (√v_t_düzeltme + ε)
```

**Adam'ın neden bu kadar iyi çalıştığı:**
- Momentum, aynı yöndeki gradyanları biriktirir (hızlanma)
- Adaptif hız, farklı ölçeklerdeki parametreleri otomatik ayarlar
- Önyargı düzeltmesi, erken adımlardaki sapmayı giderir

### AdamW: Adam + Ağırlık Azaltma

Standart Adam'da L2 düzenlemesi, adaptif öğrenme hızıyla çarpılır. Bu istenmeyen bir etkidir. AdamW, ağırlık azaltmayı gradyandan bağımsız olarak uygular.

```
w = w - lr × (m_t_düzeltme / (√v_t_düzeltme + ε) + λ × w)
```

Transformer eğitimi için AdamW tercih edilir.

## Optimize Edici Seçimi

| Görev | Önerilen | Varsayılan lr |
|-------|----------|---------------|
| CNN eğitimi | SGD + Momentum | 0.01 |
| Transformer eğitimi | AdamW | 0.001 |
| GAN eğitimi | Adam (β1=0.5) | 0.0002 |
| İnce ayar | AdamW | 0.00001 |

## Alıştırmalar

1. Sıfırdan SGD ve Adam uygulayın
2. Rosenbrock fonksiyonunda optimize edicileri görselleştirin
3. Farklı öğrenme hızlarıyla eğitimi karşılaştırın

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| SGD | "Basit iniş" | Rastgele toplu işlerle gradyan inişi |
| Momentum | "Hızlanma" | Önceki gradyanları biriktirerek hızlanma |
| RMSProp | "Adaptif hız" | Parametre başına öğrenme hızını ayarlama |
| Adam | "Akıllı optimize edici" | Momentum + RMSProp + önyargı düzeltmesi |
| AdamW | "Düzenlemeli Adam" | Ağırlık azaltmayı bağımsız uygulayan Adam |
| Öğrenme hızı | "Adım boyutu" | Her adımda ne kadar hareket edileceğini belirleyen skaler |
