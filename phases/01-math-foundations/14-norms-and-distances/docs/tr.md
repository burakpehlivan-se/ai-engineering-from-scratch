> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/14-norms-and-distances/docs/en.md)

# Normlar ve Mesafeler

> Mesafe fonksiyonunuz "benzer" kelimesinin ne anlama geldiğini tanımlar. Yanlış seçerseniz aşağı akıştaki her şey bozulur.

**Tür:** Uygulama
**Diller:** Python
**Ön Koşullar:** Faz 1, Ders 01 (Doğrusal Cebir Sezgisi), 02 (Vektörler, Matrisler ve İşlemler)
**Süre:** ~90 dakika

## Öğrenme Hedefleri

- Sıfırdan L1, L2, kosinüs, Mahalanobis, Jaccard ve düzeltme mesafesi fonksiyonlarını uygulayın
- Verilen bir ML görevi için uygun mesafe metriğini seçin ve alternatiflerin neden başarısız olduğunu açıklayın
- L1 ve L2 normlarını LASSO ve Ridge düzenlemesi ile ve geometrik kısıt bölgeleriyle bağlayın
- Aynı veri setinin farklı metrikler altında nasıl farklı en yakın komşular ürettiğini gösterin

## Sorun

İki vektörünüz var. Belki kelime gömmeleri. Belki kullanıcı profilleri. Belki piksel dizileri. Bilmeniz gereken şey: ne kadar yakınlar?

Cevap tamamen hangi mesafe fonksiyonunu seçtiğinize bağlıdır. İki veri noktası bir metrikte en yakın komşular olabilir ve diğerinde uzak olabilir. KNN sınıflandırıcınız, öneri motorunuz, vektör veritabanınız, kümeleme algoritmanız, kayıp fonksiyonunuz — tümü bu seçime bağlıdır. Yanlış seçerseniz modeliniz yanlış şey için optimize olur.

Evrensel en iyi mesafe yoktur. L2 uzaysal verilerde çalışır. Kosinüs benzerliği NLP'de hakimdir. Jaccard kümeleri ele alır. Düzeltme mesafesi dizeleri ele alır. Mahalanobis korelasyonları hesaba katar. Her biri "benzer" kelimesinin ne anlama geldiği hakkında farklı bir varsayımı kodlar.

## Kavram

### Normlar: Vektör büyüklüğünü ölçme

Bir norm bir vektörün "boyutunu" ölçer. İki vektör arasındaki her mesafe fonksiyonu, farklarının normu olarak yazılabilir: d(a, b) = ||a - b||. Bu yüzden normları anlamak mesafeleri anlamaktır.

### L1 Normu (Manhattan mesafesi)

L1 normu tüm elemanların mutlak değerlerini toplar.

```
||x||_1 = |x_1| + |x_2| + ... + |x_n|
```

#### Açıklama
L1 normu, sparse modelleri teşvik eder. Özellik seçimi için mükemmeldir.

### L2 Normu (Öklid mesafesi)

L2 normu karelerin toplamının kareköküdür.

```
||x||_2 = √(x_1² + x_2² + ... + x_n²)
```

#### Açıklama
L2 normu, en yaygın mesafe ölçümüdür. Düz uzaydaki doğrudan mesafeyi ölçer.

### Kosinüs Benzerliği

İki vektör arasındaki açıyı ölçer.

```
kosinüs(a, b) = (a · b) / (||a|| × ||b||)
```

#### Açıklama
Kosinüs benzerliği, büyüklükten bağımsız olarak yön benzerliğini ölçer. NLP'de ve öneri sistemlerinde yaygındır.

### Jaccard Benzerliği

İki kümenin kesişiminin birleşimine oranıdır.

```
jaccard(A, B) = |A ∩ B| / |A ∪ B|
```

### Düzeltme Mesafesi

İki dizeyi birbirine dönüştürmek için gereken minimum düzenleme sayısıdır.

### Mahalanobis Mesafesi

Korelasyonları hesaba katar.

```
d(x, y) = √((x - y)ᵀ S⁻¹ (x - y))
```

#### Açıklama
Mahalanobis, değişkenler arasındaki korelasyonları hesaba katarak daha doğru mesafe ölçer.

## Alıştırmalar

1. Farklı normları 2B vektörler üzerinde görselleştirin
2. Aynı veri seti üzerinde KNN'i farklı mesafe metrikleriyle çalıştırın ve sonuçları karşılaştırın
3. L1 ve L2 normlarının geometrik kısıt bölgelerini çizin

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Norm | "Vektör büyüklüğü" | Bir vektörün boyutunu ölçen fonksiyon |
| L1 normu | "Manhattan mesafesi" | Elemanların mutlak değerlerinin toplamı |
| L2 normu | "Öklid mesafesi" | Karelerin toplamının karekökü |
| Kosinüs benzerliği | "Yön benzerliği" | İki vektör arasındaki açının kosinüsü |
| Jaccard | "Küme benzerliği" | Kesişimin birleşime oranı |
| Mahalanobis | "Korelasyonlu mesafe" | Korelasyonları hesaba katan mesafe |
