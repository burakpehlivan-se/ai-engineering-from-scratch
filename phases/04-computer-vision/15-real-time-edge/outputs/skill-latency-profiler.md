---
name: skill-latency-profiler
description: Isınma, senkronizasyon, yüzdelikler ve bellek izleme ile tam bir gecikme karşılaştırma betiği yazın
version: 1.0.0
phase: 4
lesson: 15
tags: [kenar, dağıtım, profilleme, karşılaştırma]
---

# Gecikme Profilcisi

Herhangi bir PyTorch modeli için disiplinli bir gecikme karşılaştırması üretin. Aşağı akış herkesin gerçekten güvenebileceği raporlar.

## Ne zaman kullanılır

- Dağıtım için seçmeden önce birden fazla aday omurgayı karşılaştırırken.
- Nicelleştirme veya budamadan önce ve sonra.
- Bir çalışma zamanı değişikliğinden sonra (eager vs ONNX vs TensorRT).
- Dağıtıma hazırlık raporu üretirken.

## Girdiler

- `model`: PyTorch `nn. Module`.
- `input_shape`: `(1, 3, 224, 224)` gibi bir demet.
- `device`: `cpu` | `cuda` | `mps`.
- `warmup`: varsayılan 10.
- `iters`: varsayılan 100.

## Kontroller

### 1. Isınma
Modeli `warmup` kez zamanlama yapmadan çalıştırın. İlk ileri JIT derlemesini ve soğuk önbellek etkilerini yakalar.

### 2. Senkronizasyon
`cuda` için, her zamanlanmış ileri geçişten önce ve sonra `torch.cuda.synchronize()` çağırın.
`mps` için, `torch.mps.synchronize()` çağırın.

### 3. Zamanlayıcı
Duvar saati ölçümü için `time.perf_counter()` kullanın. Milisaniyeye dönüştürün.

### 4. Yüzdelikler
Tam zamanlama listesini sıralayın. `p50, p90, p95, p99, ortalama, std` raporlayın.

### 5. Bellek
`cuda` için, çalıştırmadan sonra `torch.cuda.max_memory_allocated()` çağırın ve herhangi bir taban çizgisini çıkarın.
`cpu` için, `tracemalloc` veya `psutil. Process().memory_info().rss` kullanın (önce ve sonra).

### 6. Toplu iş boyutu taraması
İsteğe bağlı olarak, verim vs gecikme takaslarını ortaya çıkarmak için karşılaştırmayı `batch_size in [1, 4, 16, 32]` için tekrarlayın.

## Çıktı şablonu

```python
import time
import torch
import psutil, os

def profile(model, input_shape, device="cpu", warmup=10, iters=100):
 proc = psutil. Process(os.getpid())
 baseline_rss = proc.memory_info().rss / 1e6

 model = model.to(device).eval()
 x = torch.randn(input_shape, device=device)

 def sync():
 if device == "cuda":
 torch.cuda.synchronize()
 elif device == "mps":
 torch.mps.synchronize()

 with torch.no_grad():
 for _ in range(warmup):
 model(x)
 sync()
 if device == "cuda":
 torch.cuda.reset_peak_memory_stats()

 times = []
 for _ in range(iters):
 sync()
 t0 = time.perf_counter()
 model(x)
 sync()
 times.append((time.perf_counter() - t0) * 1000)

 times.sort()
 mean = sum(times) / len(times)
 std = (sum((t - mean) ** 2 for t in times) / len(times)) ** 0.5

 def pct(p):
 idx = max(0, min(len(times) - 1, int(len(times) * p) - 1))
 return times[idx]

 report = {
 "p50_ms": pct(0.50),
 "p90_ms": pct(0.90),
 "p95_ms": pct(0.95),
 "p99_ms": pct(0.99),
 "mean_ms": mean,
 "std_ms": std,
 "rss_mb": proc.memory_info().rss / 1e6 - baseline_rss,
 }
 if device == "cuda":
 report["peak_cuda_mb"] = torch.cuda.max_memory_allocated() / 1e6

 return report
```

## Kurallar

- Her zaman ısınma çalıştırın; ilk ileri zamanlamaya asla güvenmeyin.
- Ortalama değil yüzdelikler — tek bir aykırı değer ortalamayı ikiye katlayabilir ancak p50'yi zar zor hareket ettirebilir.
- Üretimle aynı input_shape kullanın; 224x224'teki gecikme, 384x384'teki gecikme değildir.
- CUDA için, `torch.cuda.synchronize()`'i asla atlamayın; onsuz sayılar anlamsızdır.
- Torch sürümünü, CUDA sürümünü ve cihaz adını sayılarla birlikte kaydedin — aksi takdirde karşılaştırılabilir olmaktan çıkarlar.
