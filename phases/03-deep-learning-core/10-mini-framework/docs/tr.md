> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/03-deep-learning-core/10-mini-framework/docs/en.md)

# Kendi Mini Framework'ünü İnşa Et

> Nöronları, katmanları, ağları, geri yayılımı, aktivasyonları, kayıp fonksiyonlarını, optimize edicileri, düzenlemeyi, başlatmayı ve öğrenme hızı programlarını ayrı parçalar olarak inşa ettin. Şimdi hepsini bir framework'te birleştir. PyTorch değil. TensorFlow değil. Senin framework'ün.

**Tür:** Build
**Diller:** Python
**Ön Koşullar:** Faz 03'ün tamamı (Ders 01-09)
**Süre:** ~120 dakika

## Öğrenme Hedefleri

- Module, Linear, ReLU, Sigmoid, Dropout, BatchNorm, Sequential, kayıp fonksiyonları, optimize ediciler ve DataLoader içeren eksiksiz bir derin öğrenme framework'ü (~500 satır) inşa edin
- Module soyutlamasını (forward, backward, parameters) ve eğitim/değerlendirme modu geçişinin neden gerekli olduğunu açıklayın
- Tüm bileşenleri daire sınıflandırmasında 4 katmanlı bir ağ eğiten çalışan bir eğitim döngüsünde birleştirin
- Framework'ünüzün her bileşenini PyTorch karşılığıyla eşleyin

## Kavram

### Module Soyutlaması

PyTorch'ta her katman `nn.Module`'dan türer. Bir Module'ün üç sorumluluğu vardır:
1. **forward()** — girdi verilen çıktıyı hesapla
2. **parameters()** — tüm eğitilebilir ağırlıkları döndür
3. **backward()** — gradyanları hesapla (PyTorch'ta autograd halleder)

### Sequential Kabı

`nn.Sequential` Modul'leri zincirler. İleri geçiş: Modul 1 → Modul 2 → Modul 3. Geri geçiş: ters sıra. Kabın kendisi bir Module'dür.

### Eğitim vs Değerlendirme Modu

Dropout eğitimde rastgele sıfırlar, değerlendirmede her şeyi geçirir. Batch normalization eğitimde toplu iş istatistiklerini, değerlendirmede kayan ortalamaları kullanır.

### Optimize Edici

Parametreleri gradyanlarını kullanarak günceller. SGD: `param -= lr × grad`. Adam: momentum ve varyans tahminlerini tutar. Optimize edici mimariyi bilmez — sadece düz parametre listesi görür.

### DataLoader

Veriyi toplu işlere böler, isteğe bağlı karıştırma yapar.

## Uygulama

Aşağıdaki kodları `code/main.py` içinde inşa edin:

**Module temel sınıfı:** `forward()`, `backward()`, `parameters()`, `train()`, `eval()`.

**Linear katmanı:** Ağırlıklar ve bias depolar, Wx + b hesaplar.

**Aktivasyon Modülleri:** ReLU, Sigmoid, Tanh.

**Dropout Modülü:** Eğitimde rastgele sıfırlar, testte hiçbir şey yapmaz.

**BatchNorm Modülü:** Aktivasyonları normalleştirir, kayan istatistikler tutar.

**Sequential Kabı:** Modülleri zincirler.

**Kayıp Fonksiyonları:** MSE ve BCE.

**SGD ve Adam Optimize Edicileri:** Parametre listesi alır, gradyanlarla günceller.

**DataLoader:** Veriyi toplu işlere böler, karıştırır.

**4 Katmanlı Ağ Eğitimi:** Tüm bileşenleri birleştirip daire sınıflandırması yapın.

## Kullanım

PyTorch karşılığı:
```python
model = nn.Sequential(
    nn.Linear(2, 16), nn.ReLU(),
    nn.Linear(16, 16), nn.ReLU(),
    nn.Linear(16, 8), nn.ReLU(),
    nn.Linear(8, 1), nn.Sigmoid(),
)
```
Aynı yapı. Sequential, Linear, ReLU, loss, Adam, zero_grad, backward, step, train, eval — her kavram birebir eşlenir.

## Temel Terimler

| Terim | Gerçekte ne anlama geldiği |
|-------|--------------------------|
| Module | forward(), backward(), parameters() olan temel soyutlama |
| Sequential | Modülleri sırayla zincirleyen kap |
| İleri geçiş | Girdiyi her modülden geçirerek çıktı hesaplama |
| Geri geçiş | Kayıp gradyanını ters sırada yayma |
| Parametreler | Optimize edicinin güncelleyebileceği tüm değerler |
| Optimize edici | Gradyanları kullanarak parametreleri güncelleme algoritması |
| Eğitim modu | Dropout ve BatchNorm'un stokastik davranışını etkinleştiren bayrak |
| Değerlendirme modu | Dropout'u devre dışı bırakan, kayan istatistikleri kullanan bayrak |

## Alıştırmalar

1. SoftmaxCrossEntropyLoss ekleyin
2. Optimize edicide öğrenme hızı programlaması uygulayın
3. Sequential'a save() ve load() ekleyin
4. Adam'da ağırlık azaltma uygulayın
5. Gerçek mini-toplu iş gradyan birikimi uygulayın
