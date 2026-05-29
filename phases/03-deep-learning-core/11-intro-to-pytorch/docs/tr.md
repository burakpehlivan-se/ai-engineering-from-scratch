> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/03-deep-learning-core/11-intro-to-pytorch/docs/en.md)

# PyTorch'a Giriş

> Motoru pistonlardan ve krank millerinden inşa ettin. Şimdi herkesin kullandığını öğren.

**Tür:** Build
**Diller:** Python
**Ön Koşullar:** Ders 03.10 (Kendi Mini Framework'ünü İnşa Et)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- PyTorch'un nn.Module, nn.Sequential ve autograd'ını kullanarak sinir ağları inşa edin ve eğitin
- PyTorch tensor'larını, GPU hızlandırmasını ve standart eğitim döngüsünü (zero_grad, forward, loss, backward, step) kullanın
- Sıfırdan yazdığınız mini framework bileşenlerini PyTorch karşılıklarına dönüştürün
- Saf Python framework'ünüz ile PyTorch'u aynı görevde karşılaştırın

## Sorun

Çalışan bir mini framework'ünüz var. Aynı problemi saf Python'da PyTorch'tan 500 kat daha yavaş çözer. Ama zihinsel model birebir aynıdır.

PyTorch otomatik türev, GPU desteği, serileştirme, dağıtık eğitim ve karma hassasiyet sunar. Ve bunu sizin sıfırdan tasarladığınız arayüzün arkasında yapar.

## Kavram

### PyTorch Neden Kazandı

2015'te TensorFlow statik hesaplama grafiği gerektiriyordu. PyTorch 2017'de eager execution (hevesli yürütme) ile çıktı: `y = model(x)` hemen hesaplanır. 2022'de ML araştırma makalelerinde PyTorch payı %75'in üzerindeydi.

### Tensor'lar

Tensor, üç kritik özelliği olan çok boyutlu bir dizidir: shape (şekil), dtype (veri tipi), device (cihaz).

```python
x = torch.zeros(3, 4)           # shape: (3, 4), dtype: float32, device: cpu
x = torch.randn(2, 3, 224, 224) # batch of 2 RGB images, 224x224
x = torch.tensor([1, 2, 3])     # from a Python list
```

`RuntimeError: Expected all tensors to be on the same device` — yeni başlayanların 1 numaralı PyTorch hatası.

### Autograd

Her tensor işlemini yönlendirilmiş bir döngüsüz grafiğe (DAG) kaydeder. `.backward()` grafiği tersine çaprazlar.

```python
x = torch.randn(3, requires_grad=True)
y = x ** 2 + 3 * x
z = y.sum()
z.backward()
print(x.grad)  # dz/dx = 2x + 3
```

Üç kural: 1) Sadece `requires_grad=True` olan leaf tensor'lar gradyan biriktirir. 2) Gradyanlar varsayılan olarak birikir — her backward öncesi `zero_grad()`. 3) `torch.no_grad()` gradyan izlemeyi devre dışı bırakır.

### nn.Module

PyTorch'ta her sinir ağı bileşeninin temel sınıfı. Otomatik parametre kaydı, özyinelemeli modül keşfi, cihaz yönetimi ve state_dict serileştirmesi ekler.

```python
class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(784, 256), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(256, 128), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(128, 10),
        )
    def forward(self, x):
        return self.net(x)
```

### Eğitim Döngüsü

Her PyTorch eğitim döngüsü aynı 5 adımlı deseni izler:
```python
for epoch in range(num_epochs):
    model.train()
    for inputs, targets in train_loader:
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
```

Beş satır. GPT-4, Stable Diffusion ve LLaMA'yı eğiten beş satır.

### GPU Eğitimi ve Karma Hassasiyet

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
```

Karma hassasiyet (mixed precision) belleği yarıya indirir ve verimi ikiye katlar:
```python
with autocast(device_type="cuda"):
    outputs = model(inputs)
    loss = criterion(outputs, targets)
```

## Uygulama

MNIST üzerinde 3 katmanlı MLP: 784 → 256 → 128 → 10. Ham dosyalardan veri yükleme, saf PyTorch primitifleri, 10 epoch'ta ~%97.8 test doğruluğu.

## Kullanım

Model kaydetme ve yükleme:
```python
torch.save(model.state_dict(), "model.pt")
model.load_state_dict(torch.load("model.pt", weights_only=True))
```

Her zaman `state_dict()` kaydedin, model nesnesini değil.

## Temel Terimler

| Terim | Gerçekte ne anlama geldiği |
|-------|--------------------------|
| Tensor | Otomatik türev desteği olan, tipli, cihaz bilincine sahip çok boyutlu dizi |
| Autograd | İleri geçişte işlemleri kaydedip geriye doğru oynatan bant tabanlı sistem |
| nn.Module | Parametre kaydeden, iç içe geçmeyi destekleyen türevlenebilir hesaplama bloğu |
| state_dict | Parametre adlarını tensor'lara eşleyen sıralı sözlük |
| .backward() | Hesaplama grafiğini tersine çaprazlayarak gradyan hesaplama |
| Karma hassasiyet | Hız için float16, kararlılık için float32 master ağırlıklar |

## Alıştırmalar

1. Batch normalization ekleyin
2. Öğrenme hızı bulucu uygulayın
3. GPU'ya taşıyın ve karma hassasiyet ekleyin
4. Özel Dataset inşa edin (Fashion-MNIST)
5. Adam'ı SGD + momentum ile değiştirin
