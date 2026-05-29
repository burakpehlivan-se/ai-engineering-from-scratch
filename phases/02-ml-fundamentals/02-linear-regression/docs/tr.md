> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/02-ml-fundamentals/02-linear-regression/docs/en.md)

# Doğrusal Regresyon

> Doğrusal regresyon, verinizden en iyi düz çizgiyi çizer. Makine öğrenmesinin "hello world"ıdır.

**Tür:** Uygulama
**Diller:** Python
**Ön Koşullar:** Faz 1 (Doğrusal Cebir, Calculus, Optimizasyon), Faz 2 Ders 1
**Süre:** ~90 dakika

## Öğrenme Hedefleri

- Ortalama kare hata için gradyan inişi güncelleme kurallarını türetin ve sıfırdan doğrusal regresyon uygulayın
- Gradyan inişi ve normal denklemi hesaplama karmaşıklığı açısından karşılaştırın ve hangisini ne zaman kullanacağınızı açıklayın
- Özellik normalleştirmeli çoklu doğrusal regresyon modeli oluşturun ve öğrenilmiş ağırlıkları yorumlayın
- Ridge regresyonunun (L2 düzenlemesi) büyük ağırlıklara ceza vererek aşırı uyumu nasıl önlediğini açıklayın

## Sorun

Veriniz var: ev boyutları ve satış fiyatları. Boyutu verildiğinde yeni bir evin fiyatını tahmin etmek istiyorsunuz. Dağınık grafikte tahminde bulunabilirsiniz, ama bir formüle ihtiyacınız var. Veriye en iyi uyan bir çizgiye ihtiyacınız var ki herhangi bir boyutu girip fiyat tahmini alabilesiniz.

Doğrusal regresyon size o çizgiyi verir. Daha da önemlisi, tüm ML eğitim döngüsünü tanıştırır: bir model tanımlayın, bir maliyet fonksiyonu tanımlayın, parametreleri optimize edin. Her ML algoritması aynı kalıbı takip eder. Bunu en basit durumda burada öğrenin, her yerde tanıyacaksınız.

Bu sadece basit sorunlar için değildir. Doğrusal regresyon, talep tahmini, A/B test analizi, finansal modelleme ve her regresyon görevi için bir başlangıç çizgisi olarak üretim sistemlerinde kullanılır.

## Kavram

### Model

Doğrusal regresyon, girdi (x) ile çıktı (y) arasında doğrusal bir ilişki varsayar:

```
y = wx + b
```

- `w` (ağırlık/eğim): x 1 arttığında y ne kadar değişir
- `b` (sapma/kesişim): x = 0 olduğunda y'nin değeri

Birden fazla girdi (özellik) için bu şu hale gelir:

```
y = w1*x1 + w2*x2 + ... + wn*xn + b
```

Veya vektör formunda: `y = w^T * x + b`

Amaç: Tüm eğitim örnekleri boyunca tahmin edilen y'yi gerçek y'ye mümkün olduğunca yakın yapan w ve b değerlerini bulmaktır.

### Maliyet Fonksiyonu (Ortalama Kare Hata)

"Mümkün olduğunca yakın"ı nasıl ölçersiniz? Tahminlerinizin ne kadar yanlış olduğunu yakalayan tek bir sayıya ihtiyacınız vardır. En yaygın seçim Ortalama Kare Hata (MSE)'dır:

```
MSE = (1/n) * Σ((y_tahmin - y_gercek)^2)
```

Neden kare? İki neden. Birincisi, büyük hataları küçük hatalardan daha fazla cezalandırır (10 hatası 1 hatasından 100 kat değil, 10 kat daha kötüdür). İkincisi, kare fonksiyonu pürüzsüzdür ve her yerde türevi alınabilir, bu da optimizasyonu kolaylaştırır.

Maliyet fonksiyonu bir yüzey oluşturur. Tek bir ağırlık w ve sapma b için, MSE yüzeyi bir kaseye benzer (konveks paraboloid). Kase'nin dibinin MSE'nin asgari yapıldığı yerdir. Eğitim, o dibi bulmak demektir.

### Gradyan İnişi

Gradyan inişi, aşağıya doğru adım atarak kase'nin dibini bulur.

```mermaid
flowchart TD
    A[w ve b'yi rastgele başlat] --> B[Tahminleri hesapla: ŷ = wx + b]
    B --> C[Maliyeti hesapla: MSE]
    C --> D[Gradyanları hesapla: dMSE/dw, dMSE/db]
    D --> E[Parametreleri güncelle]
    E --> F{Maliyet yeterince düşük mü?}
    F -->|Hayır| B
    F -->|Evet| Bitti: optimum w ve b bulundu
```

Gradyanlar iki şey söyler: her parametrenin hangi yönde hareket edeceği ve ne kadar hareket edeceği.

MSE için ŷ = wx + b:

```
dMSE/dw = (2/n) * Σ((ŷ - y) * x)
dMSE/db = (2/n) * Σ(ŷ - y)
```

Güncelleme kuralı:

```
w = w - öğrenme_hızı * dMSE/dw
b = b - öğrenme_hızı * dMSE/db
```

Öğrenme hızı adım boyutunu kontrol eder. Çok yüksek: minimumun üzerinden geçersiniz ve ayrışırsınız. Çok düşük: eğitim sonsuza kadar sürer. Tipik başlangıç değerleri: 0.01, 0.001 veya 0.0001.

### Normal Denklem (Kapalı Form Çözümü)

Doğrusal regresyon için özel olarak, herhangi bir iterasyon olmadan optimum ağırlıkları veren doğrudan bir formül vardır:

```
w = (X^T * X)^(-1) * X^T * y
```

Bu formül, her seferinde tüm verileri işler, bu yüzden küçük veri setleri için hızlıdır ama büyük veri setlerinde (100.000+ örnek) çok bellek ve zaman alır.

## Alıştırmalar

1. Sıfırdan doğrusal regresyon uygulayın (gradyan inişi ile)
2. Farklı öğrenme hızlarıyla eğitimi görselleştirin
3. Normal denklemi gradyan inişiyle karşılaştırın

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Doğrusal regresyon | "Düz çizgi ile tahmin" | Girdi ile çıktı arasında doğrusal ilişki kuran model |
| Gradyan inişi | "Aşağı inme" | Kaybı azaltmak için ağırlıkları güncelleme |
| Öğrenme hızı | "Adım boyutu" | Her adımda ne kadar hareket edileceğini belirleyen skaler |
| MSE | "Hata ortalaması" | Tahminlerin ne kadar yanlış olduğunu ölçen metrik |
| Normal denklem | "Kapalı form çözüm" | Optimizasyon olmadan direkt çözüm |
| Ridge regresyonu | "Düzenlemeli regresyon" | Büyük ağırlıklara ceza ekleyerek aşırı uyumu önleme |
