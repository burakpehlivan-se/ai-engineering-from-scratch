---
name: checkpoint-save-resume
description: Tam RNG yakalama ile atomik, parçalı kontrol noktaları, böylece öldürülen bir çalıştırma aynı kayıp yörüngesiyle epok ortasında devam eder
version: 1.0.0
phase: 19
lesson: 47
tags: [training, durability, resume, sharded-state]
---

## Ne Zaman Kullanılır

Kümenin duvar-saati tavanından daha uzun herhangi bir eğitim çalıştırması, bir düğüm yeniden başlatmasından sağ çıkması gereken herhangi bir çalıştırma veya tek bir yük için çok büyük olan herhangi bir model.

## Yük Şekli

```python
{
  "schema": "ckpt.v1",
  "model": model.state_dict(),
  "optimizer": opt.state_dict(),
  "scheduler": sched.state_dict(),
  "state": {"step": int, "epoch": int, "batch_in_epoch": int, "losses": [float, ...]},
  "rng": {"python": ..., "numpy": ..., "torch_cpu": ..., "torch_cuda": ...},
  "wall_saved_at": time.time(),
}
```

## Atomik Kayıt

1. Yükü, hedefle aynı dizinde benzersiz bir geçici dosyaya yaz.
2. Atomik değişim için `os.replace(tmp, target)`.
3. Asla doğrudan hedef adına yazma.

## Parçalı Düzen

- Anahtar başına round robin veya parametre grubuna göre bölünmüş `model.shard-NNN.pt` parça başına.
- `meta.pt` optimize ediciyi, zamanlayıcıyı, eğitim durumunu, RNG'yi ve parça manifestosunu taşır.
- `index.json` her parça ve `meta.pt` için `sha256` taşır.
- Yükleyici, birleştirmeden önce her karmanı doğrular.

## Epok Ortası Devam

- `step` yanında `(epoch, batch_in_epoch)` kaydet.
- Devam eden epokun ilk partisinden önce RNG durumunu geri yükle.
- Üretecini tüketilen partilerin ötesine hızlı-ileri al.

## Başarısızlık Kipleri

- Çapraz-cihaz yeniden adlandırma: atomik değil, önceki dosyayı kaybedersin. Geçici dosyayı aynı dizine koy.
- RNG'yi unutma: devam eden kayıp temel çizgiden sapar. Demo'nun onaylama ifadesini çalıştır.
- Optimize edici durumunu unutma: sonraki adım sallanır. Aynı fark patlar.
- Yanlış kontrol noktasını budama: son K'yı ve en iyiyi tut.
