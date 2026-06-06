---
name: gradient-accumulation
description: Cihaz belleğinden büyük mikro-partileri ölçekleyerek ve pencere başına bir kez optimize edici adımı çalıştırarak etkili bir partide eğit
version: 1.0.0
phase: 19
lesson: 46
tags: [training, batch-size, distributed, scaling]
---

## Ne Zaman Kullanılır

Etkili parti, gradyanı düzleştiren ve öğrenme hızı çizelgesiyle eşleşen kaldıraçtır. Tek bir ileri geçişte karşılayamıyorsan, bu tariftir.

## Tarif

1. `micro_batch`'i, belleğe sığan ve hızlandırıcıyı doyuran en büyük boyut olarak seç.
2. `effective_batch`'i öğrenme hızı çizelgesinden seç.
3. `accum_steps = effective_batch // (micro_batch * world_size)` ayarla ve eşit bölündüğünü doğrula.
4. Her mikro parti başına: `loss = criterion(model(x), y) / accum_steps; loss.backward()`.
5. Son olmayan mikro partilerde, DDP'de gradyan tüm-indirgemeyi atlamak için `model.no_sync()` gir.
6. Son mikro partiden sonra, `optimizer.step()`'i bir kez çalıştır. Sonraki pencereden önce gradyanları sıfırla.
7. Optimize edici durumu etkili parti başına bir kez ilerler; öğrenme hızı çizelgesi etkili parti başına bir kez ilerler.

## Günlükleme

Her etkili adım için `samples_per_sec`, `median_step_ms`, `sync_calls`, `accum_steps`, `effective_batch` ile küçük bir JSON kaydı yay. Bu olmadan maliyet takası görünmezdir.

## Başarısızlık Kipleri

- `/ accum_steps` ölçeklendirmesini unutma: gradyanlar N kadar patlar.
- Pencere ortasında adım atma: parametreler sürüklenir.
- Her mikro partide senkron: ağ bağlı, istatistiksel kazanç yok.
- Bunu karma hassasiyet ölçek-kaldırma ile karıştırma: yalnızca ölçeği kaldırılmış kaybı ölçekle.
