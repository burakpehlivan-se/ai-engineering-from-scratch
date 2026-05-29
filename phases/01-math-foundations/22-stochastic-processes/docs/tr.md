> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/22-stochastic-processes/docs/en.md)

# Stokastik Süreçler

> Yapısı olan rastgelelik. Rastgele yürüyüşlerin, Markov zincirlerinin ve difüzyon modellerinin arkasındaki matematik.

**Tür:** Öğrenme
**Diller:** Python
**Ön Koşullar:** Faz 1, Ders 06-07 (olasılık, Bayes)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- 1B ve 2B rastgele yürüyüşleri simüle edin ve yer değiştirme karesinin kökünün n scale'ini doğrulayın
- Bir Markov zincir simülatörü oluşturun ve özdeğere ayrıştırma ile durağan dağılımını hesaplayın
- Hedef dağılımlardan örnekleme yapmak için Metropolis-Hastings MCMC ve Langevin dinamiklerini uygulayın
- İleri difüzyon sürecini Brown hareketiyle bağlayın ve ters sürecin veriyi nasıl ürettiğini açıklayın

## Sorun

Birçok yapay zeka sistemi zamanla değişen rastgelelik içerir. Statik rastgelelik değil — her adımın bir öncekine bağlı olduğu yapılandırılmış, sıralı rastgelelik.

Dil modelleri token'ları tek tek üretir. Her token bir önceki bağlama bağlıdır. Model bir olasılık dağılımı çıktısı verir, bundan örnekleme yapar ve devam eder. Bu bir stokastik süreçtir.

Difüzyon modelleri bir görüntüye adım adım gürültü ekler, saf gürültü olana kadar. Sonra süreci tersine çevirir, adım adım gürültüden temizler, yeni bir görüntü ortaya çıkana kadar. İleri süreç bir Markov zinciridir. Ters süreç geriye çalışan öğrenilmiş bir Markov zinciridir.

Pekiştirmeli öğrenme ajanları bir ortamda eylemler alır. Her eylem bir olasılıkla yeni bir duruma yol açar. Ajan rastgele bir dünyada rastgele bir politika izler. Tümü bir Markov karar sürecidir.

MCMC örnekleme — Bayes çıkarımının omurgası — durağan dağılımı örneklemek istediğiniz sonraki olan bir Markov zinciri inşa eder.

## Kavram

### Rastgele Yürüyüşler

0 konumunda başlayın. Her adımda adaletli bir para atın. Tura: sağa git (+1). Yazı: sola git (-1).

```python
import numpy as np

def rastgele_yuruyus(n_adim):
    konum = 0
    yolu = [konum]
    for _ in range(n_adim):
        konum += np.random.choice([-1, 1])
        yolu.append(konum)
    return yolu
```

#### Açıklama
Rastgele yürüyüşün yer değiştirmesi √n ile ölçeklenir. Bu, Brown hareketinin temelidir.

### Markov Zincirleri

Bir sonraki durum, yalnızca mevcut duruma bağlıdır (önceki durumlara değil).

```
Geçiş matrisi P:
P[i][j] = i durumundan j durumuna geçiş olasılığı
```

Durağan dağılım: πP = π (özdeğer 1 olan özvektör)

### MCMC (Markov Zinciri Monte Carlo)

Herhangi bir dağılımdan örnekleme yapmak için Markov zincirleri kullanır.

```python
def metropolis_hastings(ornekleme_fonksiyonu, n_ornek):
    mevcut = np.random.randn()
    ornekler = []
    
    for _ in range(n_ornek):
        aday = mevcut + np.random.randn() * 0.5
        kabul_orani = ornekleme_fonksiyonu(aday) / ornekleme_fonksiyonu(mevcut)
        
        if np.random.rand() < kabul_orani:
            mevcut = aday
        
        ornekler.append(mevcut)
    
    return ornekler
```

#### Açıklama
Metropolis-Hastings, bir dağılımdan örnekleme yapmak için öner-kabul et algoritmasıdır. Düşük olasılıklı adayları reddeder, yüksek olasılıklıları kabul eder.

### Langevin Dinamikleri

Gradyan inişine rastgelelik ekler.

```
x_t+1 = x_t - lr × ∇U(x_t) + √(2×lr) × rastgele_gürültü
```

#### Açıklama
Langevin dinamikleri, difüzyon modellerinin temelini oluşturur. Gürültü, local minimumlardan kurtulmaya yardımcı olur.

## Alıştırmalar

1. 1B rastgele yürüyüş simülasyonu yapın ve yer değiştirme grafiğini çizin
2. Basit bir Markov zinciri oluşturun ve durağan dağılımını hesaplayın
3. Metropolis-Hastings ile normal dağılımdan örnekleme yapın

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Stokastik süreç | "Rastgele zaman serisi" | Zamana bağlı rastgele değişkenler dizisi |
| Rastgele yürüyüş | "Rastgele adım" | Her adımda rastgele yöne giden yol |
| Markov zinciri | "Bağımlı süreç" | Bir sonraki durumun yalnızca mevcut duruma bağlı olduğu süreç |
| Geçiş matrisi | "Olasılık tablosu" | Durumlar arası geçiş olasılıklarını gösteren matris |
| Durağan dağılım | "Uzun vadeli denge" | Sürecin uzun vadede yaklaştığı dağılım |
| MCMC | "Dağılımdan örnekleme" | Markov zinciri kullanarak herhangi bir dağılımdan örnekleme |
| Langevin | "Gradyan + gürültü" | Gradyan inişine rastgelelik ekleyen dinamik |
