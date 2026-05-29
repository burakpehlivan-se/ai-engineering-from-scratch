> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/03-deep-learning-core/04-activation-functions/docs/en.md)

# Aktivasyon Fonksiyonları

> Doğrusal olmayanlık olmadan, 100 katmanlı ağınız şık bir matris çarpımıdır. Aktivasyonlar, sinir ağlarının eğrilerle düşünmesini sağlayan kapılardır.

**Tür:** Uygulama
**Diller:** Python
**Ön Koşullar:** Ders 03.03 (Geri Yayılım)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Sigmoid, tanh, ReLU, Leaky ReLU, GELU, Swish ve softmax'i türevleriyle birlikte sıfırdan uygulayın
- Farklı aktivasyonlarla 10+ katman boyunca aktivasyon büyüklüklerini ölçerek kaybolan gradyan sorununu teşhis edin
- ReLU ağında ölü nöronları tespit edin ve GELU'nun bu başarısızlık modunu neden önlediğini açıklayın
- Verilen bir mimari (transformer, CNN, RNN, çıktı katmanı) için doğru aktivasyon fonksiyonunu seçin

## Sorun

İki doğrusal dönüşümü üst üste koyun: y = W2(W1x + b1) + b2. Genişletin: y = W2W1x + W2b1 + b2. Bu sadece y = Ax + c'dir — tek bir doğrusal dönüşüm. Kaç tane doğrusal katman istiflerseniz istifleyin, sonuç tek bir matris çarpımına düşer. 100 katmanlı ağınızın temsil gücü tek bir katmana eşittir.

Bu teorik bir merak değildir. Derin bir doğrusal ağın gerçekten XOR'u öğrenemeyeceği, spiral veri setini sınıflandıramayacağı, bir yüzü tanıyamayacağı anlamına gelir. Aktivasyon fonksiyonları olmadan, derinlik bir aldanmadır.

Aktivasyon fonksiyonları doğrusal bozulmayı kırar. Her katmanın çıktısını doğrusal olmayan bir fonksiyonla bükerek, ağa karar sınırlarını eğme, keyfi fonksiyonları yaklaşık hesaplama ve gerçekten öğrenme becerisi kazandırır. Ama yanlış aktivasyonu seçerseniz gradyanlarınız sıfıra kaybolur (derin ağlarda sigmoid), sonsuza patlar (dikkatli başlatma olmadan sınırsız aktivasyonlar) veya nöronlarınız kalıcı olarak ölür (büyük negatif bias'larla ReLU). Aktivasyon fonksiyonu seçimi doğrudan ağınızın hiç öğrenip öğrenemeyeceğini belirler.

## Kavram

### Neden Doğrusal Olmayanlık Gerekli

Matris çarpımı birleştirilebilir. Bir vektörün matris A ile, sonra matris B ile çarpılması AB ile çarpılmasına eşdeğerdir. Bu, on doğrusal katmanın istiflenmesinin, tek büyük bir matrisli tek bir doğrusal katmanla matematiksel olarak eşdeğer olduğu anlamına gelir. Tüm bu parametreler, tüm bu derinlik — boşa gider. Zinciri kıracak bir şeye ihtiyacınız var. Aktivasyon fonksiyonları bunu yapar.

İspat burada. Bir doğrusal katman f(x) = Wx + b hesaplar. İkisini istifleyin:

```
Katman 1: h = W1 * x + b1
Katman 2: y = W2 * h + b2
```

Yerine koyun:

```
y = W2 * (W1 * x + b1) + b2
y = (W2 * W1) * x + (W2 * b1 + b2)
y = A * x + c
```

Tek katman. Katmanlar arasına doğrusal olmayan bir aktivasyon g() yerleştirin:

```
h = g(W1 * x + b1)
y = W2 * h + b2
```

Artık yerine koyma bozulur. W2 * g(W1 * x + b1) + b2 tek bir doğrusal dönüşüme indirgenemez. Ağ doğrusal olmayan fonksiyonları temsil edebilir. Aktivasyonla her ek katman temsil kapasitesi ekler.

### Sigmoid

Sinir ağları için orijinal aktivasyon fonksiyonu.

```
sigmoid(x) = 1 / (1 + e^(-x))
```

Çıktı aralığı: (0, 1). Pürüzsüz, türevi alınabilir, herhangi bir reel sayıyı olasılık benzeri bir değere eşler.

Türevi:

```
sigmoid'(x) = sigmoid(x) × (1 - sigmoid(x))
```

Bu türevin maksimum değeri 0.25'tir ve x = 0'da oluşur. Geri yayılımda, gradyanlar katmanlar boyunca çarpılır. On katman sigmoid, gradyanın en fazla 0.25 ile on kez çarpıldığı anlamına gelir:

```
0.25^10 = 0.000000953674
```

Orijinal sinyalin milyonda birinden az. Bu kaybolan gradyan sorunudur. Erken katmanlardaki gradyanlar o kadar küçük hale gelir ki ağırlıklar neredeyse güncellenmez. Ağ görünüşte öğrenir — sonraki katmanlarda kayıp azalır — ama ilk katmanlar donmuştur. Derin sigmoid ağları basitçe eğitilmez.

Ek sorun: sigmoid çıktıları her zaman pozitiftir (0 ile 1 arası), bu da ağırlıklardaki gradyanların her zaman aynı işarette olduğu anlamına gelir. Bu, gradyan inişi sırasında zikzak yapmaya neden olur.

### Tanh

Sigmoid'in merkezlenmiş versiyonu.

```
tanh(x) = (e^x - e^(-x)) / (e^x + e^(-x))
```

Çıktı aralığı: (-1, 1). Merkezlenmiş, bu da zikzak sorununu ortadan kaldırır.

Maksimum türev, x = 0'da 1.0'dır — sigmoid'den dört kat daha iyi. Ama kaybolan gradyan sorunu hala devam eder. Büyük pozitif veya negatif girdiler için türev sıfıra yaklaşır. On katman hala gradyanı ezer, sadece daha az agresif.

### ReLU: Atılım

```
ReLU(x) = max(0, x)
```

ReLU'nun türevi 0 veya 1'dir. Sigmoid'in 0.25 maksimum türevinin aksine, ReLU'nun pozitif bölgede türevi tam olarak 1'dir. Gradyan on katman boyunca çarpılmaz — ya aynen kalır ya da sıfır olur.

Bu, derin ağların gerçekten çalışmasını sağlar. Pratikte, ReLU ile 100 katmanlı ağlar eğitilebilir.

Sorun: "ölü nöronlar". Negatif girişler ReLU'da 0 üretir. Türev de 0'dır. Bir nöron bir kez 0 üretmeye başlarsa, gradyanı olmaz ve asla kurtulamaz. Büyük negatif bias ile başlatırsanız tüm nöronlar ölebilir.

### Leaky ReLU

```
LeakyReLU(x) = x if x > 0, else 0.01x
```

Negatif bölgede küçük bir eğim (0.01) bırakarak ölü nöron sorununu azaltır.

### GELU: Transformerların Tercihi

```
GELU(x) = x × Φ(x)
burada Φ(x), standart normal dağılımın kümülatif dağılım fonksiyonudur
```

GELU yumuşak bir eşiktir. ReLU gibi keskin bir köşe yerine, 0 civarında pürüzsüz bir geçiş yapar. Transformerlarda (BERT, GPT) yaygın olarak kullanılır.

Neden GELU ReLU'dan daha iyi? Ölü nöron sorununu azaltır (negatif bölgede küçük bir gradyan vardır) ve pürüzsüz türevi optimizasyon için daha iyidir.

### Softmax

Sınıflandırma çıkışları için kullanılır. Ham skorları olasılık dağılımına dönüştürür.

```
softmax(z_i) = exp(z_i) / Σ exp(z_j)
```

Toplam her zaman 1'dir. En yüksek skor en yüksek olasılığı alır.

## Aktivasyon Fonksiyonu Seçimi

| Durum | Önerilen | Neden |
|-------|----------|-------|
| Gizli katmanlar (genel) | ReLU | Hızlı, basit, etkili |
| Transformer katmanları | GELU | Pürüzsüz, ölü nöron sorunu az |
| Çıktı katmanı (sınıflandırma) | Softmax | Olasılık dağılımı üretir |
| Çıktı katmanı (regresyon) | Yok veya Lineer | Doğrudan sayısal çıktı |
| RNN/LSTM | Tanh veya ReLU | Tarihsel tercih |

## Alıştırmalar

1. Sıfırdan sigmoid, tanh ve ReLU uygulayın
2. 10 katmanlı bir sigmoid ağı oluşturun ve gradyan kaybını gözlemleyin
3. ReLU ile ölü nöron sorununu test edin
4. Farklı aktivasyonlarla aynı görevi çalıştırıp karşılaştırın

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Aktivasyon fonksiyonu | "Dönüşüm fonksiyonu" | Doğrusal çıktıyı doğrusal olmayan forma sokan fonksiyon |
| Sigmoid | "S-eğrisi" | Sayıları 0-1 arasına sıkıştıran fonksiyon |
| ReLU | "Doğrusal olmayan basit" | max(0, x) fonksiyonu, en yaygın aktivasyon |
| GELU | "Yumuşak eşik" | Transformerlarda kullanılan pürüzsüz aktivasyon |
| Softmax | "Olasılığa dönüştürücü" | Ham skorları olasılık dağılımına dönüştüren fonksiyon |
| Kaybolan gradyan | "Gradyan küçülme" | Derin ağlarda gradyanların üstel olarak küçülmesi |
| Ölü nöron | "Pasif nöron" | Gradyanı olmadığı için öğrenmeyen nöron |
