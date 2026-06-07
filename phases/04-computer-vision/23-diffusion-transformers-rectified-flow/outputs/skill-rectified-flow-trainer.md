---
name: skill-rectified-flow-trainer
description: AdaLN DiT ve Euler örneklemesi ile eksiksiz bir düzeltilmiş-akış eğitim döngüsü yazın
version: 1.0.0
phase: 4
lesson: 23
tags: [yayılım, düzeltilmiş-akış, DiT, eğitim]
---

# Düzeltilmiş Akış Eğiticisi

Herhangi bir görüntü tensör veri kümesi üzerinde düzeltilmiş akış ile küçük bir DiT'yi başarıyla eğitecek temiz, minimal bir eğitim döngüsü üretin.

## Ne zaman kullanılır

- SD3 / FLUX eğitim hedefini küçük ölçekte yeniden üretirken.
- Aynı veri üzerinde düzeltilmiş akışı DDPM'ye karşı kıyaslarken.
- Standart dışı bir alan (tıbbi, uydu) için özel bir düzeltilmiş-akış modeli inşa ederken.

## Girdiler

- `model`: `(x, t)` alan ve tahmin edilen bir hız döndüren bir `nn. Module`.
- `dataset`: modelin alanında temiz görüntülerin bir yinelenebilir.
- `optimizer`: `lr=1e-4`, `weight_decay=0.01`, `betas=(0.9, 0.99)` ile AdamW.
- `scheduler`: ısınma ile kosinüs, varsayılan 1000 ısınma adımı.

## Eğitim adımı

```python
def rectified_flow_train_step(model, x0, optimizer, device):
 model.train()
 x0 = x0.to(device)
 n = x0.size(0)
 t = torch.rand(n, device=device) # [0, 1] aralığında tek tip
 epsilon = torch.randn_like(x0)
 x_t = (1 - t[:, None, None, None]) * x0 + t[:, None, None, None] * epsilon
 target_v = epsilon - x0 # hız hedefi
 pred_v = model(x_t, t)
 loss = F.mse_loss(pred_v, target_v)
 optimizer.zero_grad()
 loss.backward()
 optimizer.step()
 return loss.item()
```

## Örnekleme (Euler)

```python
@torch.no_grad()
def sample(model, shape, steps=20, device="cpu"):
 model.eval()
 x = torch.randn(shape, device=device)
 dt = 1.0 / steps
 t = torch.ones(shape[0], device=device)
 for _ in range(steps):
 v = model(x, t)
 x = x - dt * v
 t = t - dt
 return x
```

## İpuçları

- Tek tip `t` için `torch.rand` kullanın; logit-normal veya Sd3 tarzı ağırlıklı `t` örneklemesi biraz yardımcı olur ancak başlamak için gerekli değildir.
- Model ağırlıklarının EMA'sı standart pratiktir; `ema_model`'i bozunma 0.9999 ile koruyun.
- Koşullu modeller için sınıflandırıcısız yönlendirme: %10 olasılıkla eğitim sırasında koşullandırmayı boş/null gömme ile değiştirin; çıkarımda `v_uncond + w * (v_cond - v_uncond)`'u `w` 3-5 civarında karıştırın.
- LDM tarzı eğitim için (FLUX, SD3), tüm döngü bir VAE gizli alanında çalışır; yukarıdaki temiz `x0` aslında `VAE.encode(image)`'dır.
- 32x32 oyuncak veri kümesinde tipik yakınsama: 2000-5000 adım. Gerçek gizli SD3 eğitiminde: yüz binlerce.

## Rapor

```
[rectified flow training]
 steps: <int>
 final loss: <float>
 ema decay: <float>
 vae?: yes | no
 cfg dropout: <kesir>

[sampling]
 default steps: 20
 schnell / turbo target: 4
 full quality reference: 50+ (yalnızca karşılaştırma için)
```

## Kurallar

- Düzeltilmiş akışı RGB `uint8` verisi üzerinde görüntü-uzayı hız hedefi ile asla eğitmeyin; önce sıfır ortalama, birim varyansa normalleştirin.
- Her zaman eğitim kaybını zaman adımı kovasına göre kaydedin; erken zaman adımları (0'a yakın) geç olanlardan (1'e yakın) daha yüksek kayba sahipse, hız parametrelendirmesi muhtemelen yanlış bağlanmıştır.
- Aynı eğitim döngüsünde düzeltilmiş-akış hız hedefini DDPM gürültü hedefi ile karıştırmayın; birini seçin.
- Ampere+ GPU'larda bfloat16 eğitimi kullanın; float16, hız büyüklüğü nedeniyle bazen düzeltilmiş akışta NaN gradyanları üretir.
