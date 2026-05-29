> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/03-deep-learning-core/12-intro-to-jax/docs/en.md)

# JAX'a Giriş

> PyTorch tensor'ları mutasyona uğratır. TensorFlow grafikler inşa eder. JAX saf fonksiyonları derler. Sonuncusu, derin öğrenme hakkında düşünme şeklini değiştirir.

**Tür:** Build
**Diller:** Python
**Ön Koşullar:** Faz 03 Ders 01-10, temel NumPy
**Süre:** ~90 dakika

## Öğrenme Hedefleri

- JAX'in fonksiyonel API'sini (jax.numpy, jax.grad, jax.jit, jax.vmap) kullanarak saf fonksiyon sinir ağı kodu yazın
- PyTorch'un hevesli mutasyonu ile JAX'in fonksiyonel derleme modeli arasındaki temel tasarım farkını açıklayın
- jit derlemesi ve vmap vektörleştirmesi ile eğitim döngülerini hızlandırın
- JAX'te basit bir ağ eğitin ve açık durum yönetimini PyTorch'un nesne yönelimli yaklaşımıyla karşılaştırın

## Sorun

PyTorch her işlemi hevesli ve teker teker izler. Bu, 540 milyar parametreli bir modeli 2.048 TPU'da eğitmeye çalışana kadar iyidir. Google DeepMind Gemini'yi, Anthropic Claude'u JAX ile eğitti.

JAX, NumPy'nin üç süper gücüdür: otomatik türev, JIT derleme (XLA'ya) ve otomatik vektörleştirme. Bir örneği işleyen bir fonksiyon yazarsın. JAX sana bir toplu işi işleyen, gradyanları hesaplayan, makine koduna derleyen ve birden çok cihazda çalışan bir fonksiyon verir.

## Kavram

### JAX Felsefesi

| PyTorch | JAX |
|---------|-----|
| `nn.Module` sınıf + durum | Saf fonksiyon: `f(params, x) → y` |
| `loss.backward()` | `jax.grad(loss_fn)(params, x, y)` |
| Hevesli yürütme | XLA ile JIT derleme |
| `for x in batch:` manuel döngü | `jax.vmap(f)` otomatik vektörleştirme |
| Değiştirilebilir `model.parameters()` | Değişmez pytree dizileri |

Bu bir stil tercihi değil. JIT derlemesi saf fonksiyonlar gerektirir — aynı girdiler her zaman aynı çıktıları üretir, yan etki yok.

### jax.numpy

NumPy API'sini hızlandırıcılarda yeniden uygular. Kritik fark: diziler değişmez. `a[0] = 5` yerine `a = a.at[0].set(5)`.

### jax.grad: Fonksiyonel Otomatik Türev

PyTorch gradyanları tensor'lara ekler. JAX gradyanları fonksiyonlara ekler.
```python
df = jax.grad(lambda x: x ** 2)
df(3.0)  # 6.0
```
İkinci türev, üçüncü türev, Jacobian, Hessian — hepsi `grad`'ı birleştirerek.

### jit: XLA'ya Derleme

```python
@jax.jit
def train_step(params, x, y):
    ...
```
İlk çağrıda fonksiyonu izler, XLA'ya verir, optimize edilmiş makine kodu üretir. Sonraki çağrılar Python'u atlar.

### vmap: Otomatik Vektörleştirme

Bir örneği işleyen fonksiyonu bir toplu işi işleyene dönüştürür. `jit` ve `grad` ile birleşir.

### pmap: Cihazlar Arası Veri Paralelliği

Fonksiyonu tüm cihazlarda çoğaltır ve toplu işi böler. Google Gemini'yi binlerce TPU'da bununla eğitir.

### Pytree'ler

JAX, pytree'ler üzerinde işlem yapar — listelerin, tuple'ların, dict'lerin ve dizilerin iç içe kombinasyonları.
```python
params = jax.tree.map(lambda p, g: p - lr * g, params, grads)
```

### JAX Ekosistemi

- **Flax** (Google): nn.Module benzeri, açık durumlu
- **Equinox** (Kidger): Pytree tabanlı, Pythonic
- **Optax** (DeepMind): Birleştirilebilir gradyan dönüşümleri

### JAX vs PyTorch: Ne Zaman Hangisi

PyTorch kullanmadığın sürece, JAX kullanmak için özel bir nedenin yoksa PyTorch kullan. Bu nedenler: TPU erişimi, örnek başına gradyan ihtiyacı, büyük ölçekli çok cihazlı eğitim.

## Uygulama

MNIST'te JAX ve Optax ile 3 katmanlı MLP. Hiç sınıf yok — sadece pytree döndüren fonksiyon. `@jax.jit` ile derlenmiş eğitim adımı. 10 epoch, ~%97 test doğruluğu. İlk epoch yavaş (JIT derleme), sonrakiler hızlı.

## Kullanım

Flax ile:
```python
class MLP(nn.Module):
    @nn.compact
    def __call__(self, x):
        x = nn.Dense(256)(x); x = nn.relu(x)
        x = nn.Dense(128)(x); x = nn.relu(x)
        x = nn.Dense(10)(x); return x
```
Optax ile gradyan zincirleme:
```python
optimizer = optax.chain(
    optax.clip_by_global_norm(1.0),
    optax.adamw(learning_rate=schedule, weight_decay=0.01),
)
```

## Temel Terimler

| Terim | Gerçekte ne anlama geldiği |
|-------|--------------------------|
| XLA | İşlemleri birleştirip GPU/TPU çekirdekleri üreten derleyici |
| JIT | Fonksiyonu ilk çağrıda derleyip sonrakilerde hızlı çalıştırma |
| Saf fonksiyon | Çıktısı sadece girdilere bağlı olan, yan etkisiz fonksiyon |
| vmap | Tek örnekli fonksiyonu toplu işe dönüştürme |
| Pytree | JAX'in dolaşabildiği iç içe dizi yapısı |

## Alıştırmalar

1. Dropout ekleyin (PRNG anahtarı gerekir)
2. jax.vmap ile örnek başına gradyan hesaplayın
3. Çok katmanlı genel forward fonksiyonu yazın
4. @jax.jit ile ve olmadan hız karşılaştırması yapın
5. Gradyan kırpma (gradient clipping) uygulayın
