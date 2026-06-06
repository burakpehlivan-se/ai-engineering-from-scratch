---
name: distributed-fsdp-ddp
description: gloo veya nccl arka ucu üzerinde sıfırdan bir DDP sarmalayıcı ve bir FSDP parametre parçalama eskizi ile çok-sıralı eğitimi başlat
version: 1.0.0
phase: 19
lesson: 48
tags: [training, batch-size, distributed, scaling]
---

## Ne Zaman Kullanılır

Model bir cihaza sığar ancak daha fazla verim gerekir (DDP). Model bir cihaza sığmaz (FSDP). Her iki durumda: aynı kod yoluna sahip çok-sıralı bir eğitim kurulumu.

## İşlem Grubunu Başlat

```python
os.environ["MASTER_ADDR"] = "127.0.0.1"
os.environ["MASTER_PORT"] = str(port)
dist.init_process_group(backend="gloo", rank=rank, world_size=world_size)
```

`gloo` CPU arka ucudur; `nccl` GPU arka ucudur. İkisi de aynı kolektif yüzeyi uygular.

## Modeli Sar

1. Sıra 0'da, modeli tohumundan kur.
2. DDP kabuğuyla sar.
3. Kabuğun `__init__` metodu, her parametre ve arabellek için `dist.broadcast(p.data, src=0)` çağırır.
4. Her `loss.backward()`'dan sonra, eğitici `sync_grads()` çağırır.
5. `sync_grads()`, `dist.all_reduce(p.grad, op=SUM)` çağırır ve `p.grad.div_(world_size)`.
6. Aynı ortalaması alınmış gradyanla her sırada optimize edici adımı.

## Parametreleri Parçala (FSDP Eskizi)

1. Her parametreyi düzleştir, `world_size`'ın katlarına doldur.
2. Parçanı yerel olarak tut; geri kalanını serbest bırak.
3. İleri geçişten önce, tam tensörü her sırada yeniden kurmak için `dist.all_gather(...)`.
4. İleri geçişten sonra, tam tensörü bırak.

## Başarısızlık Kipleri

- Yayını atlamak: sıralar farklı başlangıçlardan başlar, sessizce sapar.
- Toplamadan sonra bölmeyi unutmak: gradyanlar world_size ile ölçeklenir, optimize edici adımları çok büyük olur.
- Kontrol noktaları için çapraz-cihaz yeniden adlandırma kullanmak: atomik değil; aynı ders 47 tuzağı.
- Aynı kolektifte CPU ve CUDA tensörlerini karıştırmak: arka uç uyumsuzluğu, çalıştırma asılı kalır.

> Not: `tags` alanındaki `[distributed, ddp, fsdp, collectives]` zaten yerinde; bu çeviride etiketi koruyoruz.
