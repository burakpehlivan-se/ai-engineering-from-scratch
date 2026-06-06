---
name: skill-pytorch-patterns
description: PyTorch eğitimi, değerlendirmesi ve dağıtımı için referans desenleri
version: 1.0.0
phase: 03
lesson: 11
tags: [pytorch, eğitim, derin-öğrenme, gpu, desenler]
---

## Kurallı Eğitim Döngüsü

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = Model().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)

for epoch in range(num_epochs):
    model.train()
    for inputs, targets in train_loader:
        inputs, targets = inputs.to(device), targets.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

    model.eval()
    with torch.no_grad():
        for inputs, targets in val_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
```

## Karma Hassasiyet (Mixed Precision) Eğitimi

```python
from torch.amp import autocast, GradScaler

scaler = GradScaler()
for inputs, targets in train_loader:
    inputs, targets = inputs.to(device), targets.to(device)
    optimizer.zero_grad()
    with autocast(device_type="cuda"):
        outputs = model(inputs)
        loss = criterion(outputs, targets)
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

Ne zaman kullanılır: float16 özellikli donanımla (V100, A100, H100, RTX 3090+) GPU'da eğitim. ~%1.5-2x hızlanma ve ~%50 bellek azalması bekleyin.

## Gradyan Birikimi (Gradient Accumulation)

```python
accumulation_steps = 4
optimizer.zero_grad()
for i, (inputs, targets) in enumerate(train_loader):
    inputs, targets = inputs.to(device), targets.to(device)
    outputs = model(inputs)
    loss = criterion(outputs, targets) / accumulation_steps
    loss.backward()
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

Ne zaman kullanılır: etkili toplu iş boyutunun GPU belleğinin izin verdiğinden büyük olması gerektiğinde. Kaybı accumulation_steps'e bölmek gradyan ölçeğini tutarlı tutar.

## Kaydetme ve Yükleme

```python
torch.save({
    "epoch": epoch,
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "loss": loss.item(),
}, "checkpoint.pt")

checkpoint = torch.load("checkpoint.pt", weights_only=True)
model.load_state_dict(checkpoint["model_state_dict"])
optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
```

Eğitimi sürdürmek için her zaman optimize edici durumunu kaydedin. Yalnızca çıkarım için, sadece `model.state_dict()` kaydedin.

## Özel Veri Kümesi

```python
class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, data_dir, transform=None):
        self.samples = self._load_samples(data_dir)
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        x, y = self.samples[idx]
        if self.transform:
            x = self.transform(x)
        return x, y

    def _load_samples(self, data_dir):
        ...
```

## DataLoader Yapılandırması

```python
train_loader = torch.utils.data.DataLoader(
    dataset,
    batch_size=64,
    shuffle=True,
    num_workers=4,
    pin_memory=True,
    drop_last=True,
    persistent_workers=True,
)
```

| Parametre | Ne yapar | Ne zaman kullanılır |
|-----------|-------------|---------------|
| num_workers=4 | Paralel veri yükleme | Çok çekirdekli makinelerde her zaman |
| pin_memory=True | Sayfa kilitli CPU belleği | GPU'da eğitim yaparken |
| drop_last=True | Eksik son toplu işi at | BatchNorm kullanırken |
| persistent_workers=True | İşçileri epoklar arasında canlı tut | num_workers > 0 olduğunda |

## Öğrenme Hızı Takvimleri

```python
scheduler = torch.optim.lr_scheduler.OneCycleLR(
    optimizer,
    max_lr=1e-3,
    total_steps=num_epochs * len(train_loader),
    pct_start=0.1,
)

for epoch in range(num_epochs):
    for inputs, targets in train_loader:
        ...
        optimizer.step()
        scheduler.step()
```

OneCycleLR: çoğu görev için en iyi varsayılan. max_lr'ye kadar ısınır, sonra kosinüs azalır. Her epok yerine her toplu işten sonra `scheduler.step()` çağırın.

## Ağırlık Başlatma

```python
def init_weights(module):
    if isinstance(module, nn.Linear):
        nn.init.kaiming_normal_(module.weight, nonlinearity="relu")
        if module.bias is not None:
            nn.init.zeros_(module.bias)
    elif isinstance(module, nn.Conv2d):
        nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")

model.apply(init_weights)
```

## Çıkarım Modu

```python
model.eval()

with torch.inference_mode():
    outputs = model(inputs)
```

`torch.inference_mode()`, gradyan hesaplamasını bastırmak yerine autograd'ı tamamen devre dışı bıraktığı için `torch.no_grad()`'dan daha hızlıdır.

## Sık Yapılan Hatalar Kontrol Listesi

1. CrossEntropyLoss'tan önce softmax uygulamak (dahili olarak log_softmax içerir)
2. Doğrulama sırasında model.eval() çağırmayı unutmak
3. Tensörleri modelle aynı cihaza taşımayı unutmak
4. optimizer.zero_grad() çağırmamak (gradyanlar varsayılan olarak birikir)
5. Eğitim sırasında torch.no_grad() kullanmak (gradyan hesaplamasını devre dışı bırakır)
6. num_workers'ı çok yüksek ayarlamak (çok fazla işlem oluşturur, belleği yorar)
7. GPU'da eğitim yaparken pin_memory=True kullanmamak
8. Durum diktini (state_dict) yerine tüm model nesnesini kaydetmek (yeniden düzenlemede bozulur)
