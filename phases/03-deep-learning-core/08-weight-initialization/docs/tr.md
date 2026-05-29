> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/03-deep-learning-core/08-weight-initialization/docs/en.md)

# Ağırlık Başlatma ve Eğitim Kararlılığı

> Yanlış başlatın, eğitim hiç başlamaz. Doğru başlatın, 50 katman da 3 katman kadar pürüzsüz eğitilir.

**Tür:** Build
**Diller:** Python
**Ön Koşullar:** Ders 03.04 (Aktivasyon Fonksiyonları), Ders 03.07 (Düzenleme)
**Süre:** ~90 dakika

## Öğrenme Hedefleri

- Sıfır, rastgele, Xavier/Glorot ve Kaiming/He başlatma stratejilerini uygulayın ve 50 katman boyunca aktivasyon büyüklüklerine etkilerini ölçün
- Xavier başlatmanın neden Var(w) = 2/(fan_in + fan_out) ve Kaiming'in neden Var(w) = 2/fan_in kullandığını türetin
- Sıfır başlatmanın simetri sorununu gösterin ve rastgele ölçeğin tek başına neden yetersiz olduğunu açıklayın
- Doğru başlatma stratejisini aktivasyon fonksiyonuyla eşleştirin: Xavier sigmoid/tanh için, Kaiming ReLU/GELU için

## Sorun

Tüm ağırlıkları sıfıra başlatın. Hiçbir şey öğrenilmez. Her nöron aynı fonksiyonu hesaplar, aynı gradyanı alır ve aynı şekilde güncellenir. 10.000 epoch sonra, 512 nöronlu gizli katmanınız hâlâ aynı nöronun 512 kopyasıdır.

Çok büyük başlatın. Aktivasyonlar patlar. 10. katmanda değerler 1e15'e ulaşır. 20. katmanda sonsuza taşar.

Standart normal dağılımdan rastgele başlatın. 3 katman için çalışır. 50 katmanda, sinyal sıfıra çöker veya sonsuza patlar.

Ağırlık başlatma, derin öğrenmedeki en az değer verilen karardır. Mimariler makale alır. Optimize ediciler blog yazısı alır. Başlatma bir dipnot alır. Ama yanlış yapın, hiçbir şeyin önemi kalmaz.

## Kavram

### Simetri Sorunu

Bir katmandaki her nöron aynı yapıya sahiptir. Tüm ağırlıklar aynı değerde başlarsa, her nöron aynı çıktıyı üretir ve aynı gradyanı alır. Buna simetri denir ve rastgele başlatma bunu kırmanın yoludur.

### Varyansın Katmanlar Boyunca Yayılımı

Her ağırlık w_i varyansı Var(w) ile ve her girdi x_i varyansı Var(x) ile çizilirse:
```
Var(z) = fan_in × Var(w) × Var(x)
```
Amaç: Var(z) = Var(x) olacak şekilde Var(w) seçin.

### Xavier/Glorot Başlatma

Glorot ve Bengio (2010) sigmoid ve tanh için çözümü türetti:
```
Var(w) = 2 / (fan_in + fan_out)
```
w ∼ Uniform(-limit, limit) veya w ∼ Normal(0, √(2/(fan_in + fan_out))) olarak çizilir.

### Kaiming/He Başlatma

ReLU çıktıların yarısını öldürür (negatif olan her şey sıfır olur). He ve ark. (2015) formülü ayarladı:
```
Var(w) = 2 / fan_in
```
2 çarpanı, ReLU'nun aktivasyonların yarısını sıfırlamasını telafi eder.

### Transformer Başlatma

GPT-2, artık (residual) katmanların ağırlıklarını 1/√(2N) ile ölçekler. Llama 3 (405B, 126 katman) benzer bir şema kullanır.

## Uygulama

Aşağıdaki kodları `code/main.py` içinde inşa edin: `zero_init`, `random_init`, `xavier_init`, `kaiming_init`, 50 katmanlı ileri geçiş deneyi, simetri gösterimi ve katman bazında büyüklük raporu.

## Kullanım

PyTorch bunları yerleşik fonksiyonlar olarak sunar:
```python
nn.init.xavier_uniform_(layer.weight)
nn.init.kaiming_normal_(layer.weight, nonlinearity='relu')
nn.init.zeros_(layer.bias)
```

## Temel Terimler

| Terim | Gerçekte ne anlama geldiği |
|-------|--------------------------|
| Ağırlık başlatma | İlk ağırlık değerlerini seçme stratejisi |
| Simetri kırma | Rastgele başlatma ile nöronların farklı özellikler öğrenmesini sağlama |
| Fan-in | Bir nörona gelen bağlantı sayısı |
| Xavier/Glorot | Sigmoid/tanh için varyans koruyan başlatma |
| Kaiming/He | ReLU için varyans koruyan başlatma |
| Artık ölçekleme | GPT-2'nin 1/√(2N) ile varyans büyümesini önleme tekniği |

## Alıştırmalar

1. LeCun başlatma ekleyin ve 50 katmanda karşılaştırın
2. GPT-2 artık ölçeklemesini uygulayın
3. Başlatma sağlık kontrolü fonksiyonu oluşturun
4. Fan_in = 16 vs 1024 karşılaştırması yapın
5. Ortogonal başlatma uygulayın
