---
name: skill-jax-patterns
description: JAX'ta fonksiyonel programlama desenleri — grad, jit, vmap ve pmap'in ne zaman ve nasıl kullanılacağı
version: 1.0.0
phase: 3
lesson: 12
tags: [jax, fonksiyonel-programlama, otomatik-türev, derleme, vektörleştirme]
---

# JAX Fonksiyonel Desenleri

JAX saf fonksiyonları dönüştürür. Aşağıdaki her desen tek bir kuralı izler: girdileri alıp çıktıları döndüren, yan etkisi olmayan bir fonksiyon yaz. Sonra onu dönüştür.

## Dört Dönüşüm

### grad — Bir fonksiyonu türet

```python
grads = jax.grad(loss_fn)(params, x, y)
loss, grads = jax.value_and_grad(loss_fn)(params, x, y)
```

Ne zaman kullanılır: optimizasyon için gradyanlara ihtiyacınız olduğunda.
Kısıtlama: fonksiyon bir skaler döndürmelidir. Skaler olmayan çıktılar için `jax.jacobian` kullan.

### jit — Bir fonksiyonu derle

```python
fast_fn = jax.jit(f)
```

Ne zaman kullanılır: fonksiyon aynı şekilli girdilerle birden fazla kez çağrılacaksa.
Kısıtlama: izlenen değerlere bağlı Python kontrol akışı yok. Koşullar için `jax.lax.cond`, döngüler için `jax.lax.scan` kullan.

### vmap — Bir fonksiyonu vektörleştir

```python
batch_fn = jax.vmap(f, in_axes=(None, 0))
```

Ne zaman kullanılır: bir örnek için bir fonksiyon yazdınız ve onu toplu işler üzerinde çalışacak şekilde istiyorsunuz.
`in_axes`, hangi argüman ekseni üzerinde toplu iş yapılacağını belirtir. `None`, toplu iş yapma (yayınla) anlamına gelir.

### pmap — Cihazlar arasında paralelleştir

```python
parallel_fn = jax.pmap(f, axis_name='devices')
```

Ne zaman kullanılır: birden fazla GPU/TPU'nuz var ve veri paralelliği istiyorsunuz.
Fonksiyonun içinde, `jax.lax.pmean(x, 'devices')` cihazlar arasında ortalama alır.

## Kompozisyon Kuralları

Dönüşümler kompoze olur. Sıra önemlidir:

```python
per_example_grads = jax.jit(jax.vmap(jax.grad(loss_fn), in_axes=(None, 0, 0)))
```

Sağdan sola okuma: loss_fn'nin gradyanını al, örnekler üzerinde vektörleştir, sonucu derle.

Geçerli kompozisyonlar:
- `jit(grad(f))` — derlenmiş gradyan hesaplaması
- `jit(vmap(f))` — derlenmiş toplu hesaplama
- `vmap(grad(f))` — örnek başına gradyanlar
- `pmap(jit(f))` — paralel derlenmiş hesaplama
- `grad(jit(f))` — derlenmiş fonksiyonun gradyanı (`jit(grad(f))` ile aynı)

## Parametre Yönetimi Deseni

JAX parametreleri pytrees'dir (iç içe dizi sözlükleri):

```python
params = {
 'layer1': {'w': jnp.zeros((784, 256)), 'b': jnp.zeros(256)},
 'layer2': {'w': jnp.zeros((256, 10)), 'b': jnp.zeros(10)},
}
```

Tüm parametreleri bir kerede güncelle:
```python
params = jax.tree.map(lambda p, g: p - lr * g, params, grads)
```

Parametreleri say:
```python
n_params = sum(p.size for p in jax.tree.leaves(params))
```

## PRNG Anahtar Yönetimi

JAX açık rastgele anahtarlar gerektirir:

```python
key = jax.random. PRNGKey(0)
key, subkey = jax.random.split(key)
noise = jax.random.normal(subkey, shape)
```

Birden fazla rastgele işlem için, bir kez böl:
```python
keys = jax.random.split(key, n)
```

Bir anahtarı asla yeniden kullanma. Kullanmadan önce her zaman böl.

## Sık Yapılan Hatalalar

1. **jit içinde dizileri değiştirme**: JAX dizileri değişmezdir. `x[i] = v` yerine `x.at[i].set(v)` kullan.

2. **jit içinde Python print kullanma**: `print`, yürütme sırasında değil, izleme sırasında çalışır. `jax.debug.print("{}", x)` kullan.

3. **İzlenen değerler üzerinde jit içinde Python if/for**: `jax.lax.cond`, `jax.lax.switch`, `jax.lax.scan`, `jax.lax.fori_loop` kullan.

4. **`.block_until_ready()`'ı unutmak**: JAX eşzamansız dağıtım (dispatch) kullanır. Karşılaştırma için, gerçek tamamlanmayı beklemek üzere `.block_until_ready()` çağır.

5. **PRNG anahtarlarını yeniden kullanma**: Aynı anahtarla yapılan iki işlem aynı "rastgele" değerleri üretir. Her zaman böl.

6. **jitted fonksiyonlarda genel durum**: Genel değişkenler izleme zamanında yakalanır. İzlemeden sonraki değişiklikler görünmez. Her şeyi argüman olarak geçir.

## Karar Kontrol Listesi

1. Fonksiyon birden fazla kez mi çağrılıyor? `@jax.jit` ekle.
2. Gradyanlara mı ihtiyacı var? `jax.grad` veya `jax.value_and_grad` ile sar.
3. Tek bir örneği işliyor ama sizde toplu iş mi var? `jax.vmap` ile sar.
4. Birden fazla cihazınız mı var? `jax.pmap` ile sar.
5. Rastgelelik kullanıyor mu? PRNG anahtarlarını açıkça geçir.
6. Dizi değerleri üzerinde Python kontrol akışı mı var? `jax.lax` ilkelleriyle değiştir.

## JAX Ne Zaman Kullanılır

JAX'ı şu durumlarda kullanın:
- Örnek başına gradyanlara ihtiyacınız var (farklı gizlilik, Fisher bilgisi)
- TPU'larda eğitim yapıyorsunuz (JAX yerel çerçevedir)
- Daha yüksek dereceli türevlere ihtiyacınız var (Hessianlar, Jacobianlar)
- Tüm eğitim adımını tek bir çekirdeğe derlemek istiyorsunuz
- Ekibiniz Google DeepMind veya Anthropic'te

PyTorch'u şu durumlarda kullanın:
- En büyük ekosistemi istiyorsunuz (HuggingFace, torchvision, Lightning)
- Ham hızdan çok hata ayıklama kolaylığına öncelik veriyorsunuz
- NVIDIA GPU'lara TorchServe/Triton ile dağıtım yapıyorsunuz
- İşe alım yapıyorsunuz (daha fazla PyTorch geliştiricisi var)
- Yeni mimariler üzerinde hızlı yineleme yapmak istiyorsunuz
