> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/03-deep-learning-core/07-regularization/docs/en.md)

# Düzenleme (Regularization)

> Modeliniz eğitim verisinde %99, test verisinde %60 alıyor. Ezberledi, öğrenmedi. Düzenleme, genellemeyi zorlamak için karmaşıklığa uyguladığınız vergidir.

**Tür:** Build
**Diller:** Python
**Ön Koşullar:** Ders 03.06 (Optimize Ediciler)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Dropout (ters ölçeklemeli), L2 ağırlık azaltma, batch normalization, layer normalization ve RMSNorm'u sıfırdan uygulayın
- Eğitim-test doğruluk farkını ölçün ve düzenleme deneyleriyle aşırı uyumu (overfitting) teşhis edin
- Transformer'ların neden BatchNorm yerine LayerNorm kullandığını ve modern LLM'lerin neden RMSNorm'u tercih ettiğini açıklayın
- Aşırı uyumun şiddetine göre doğru düzenleme tekniği kombinasyonunu uygulayın

## Sorun

Yeterli parametreye sahip bir sinir ağı herhangi bir veri setini ezberleyebilir. Bu teorik değil — Zhang ve ark. (2017) rastgele etiketlerle ImageNet üzerinde standart ağlar eğiterek bunu kanıtladı. Ağlar tamamen rastgele etiket atamalarında sıfıra yakın eğitim kaybına ulaştı. Öğrenilecek desen olmayan bir milyon rastgele girdi-çıktı çiftini ezberlediler. Eğitim kaybı mükemmeldi. Test doğruluğu sıfırdı.

Bu aşırı uyum (overfitting) sorunudur ve modeller büyüdükçe kötüleşir. GPT-3'te 175 milyar parametre vardır. Eğitim setinde yaklaşık 500 milyar token vardır. Bu kadar parametreyle model, eğitim verisinin önemli kısımlarını ezberleme kapasitesine sahiptir. Düzenleme olmadan, genellenebilir desenler öğrenmek yerine eğitim örneklerini tekrarlar.

Eğitim performansı ile test performansı arasındaki fark, aşırı uyum farkıdır (overfitting gap). Bu dersteki her teknik bu farka farklı bir açıdan saldırır. Dropout, ağı tek bir nörona güvenmemeye zorlar. Ağırlık azaltma, tek bir ağırlığın çok büyümesini engeller. Batch normalization, kayıp manzarasını düzleştirerek optimize edicinin daha düz, daha genellenebilir minimumlar bulmasını sağlar. Layer normalization aynı şeyi yapar ama batch normalization'un başarısız olduğu yerlerde çalışır (küçük toplu işler, değişken uzunluklu diziler). RMSNorm, ortalama hesaplamasını kaldırarak %10 daha hızlı yapar. Her teknik basittir. Birlikte, ezberleyen bir modelle genelleme yapan bir model arasındaki farktır.

## Kavram

### Aşırı Uyum Spektrumu

Her model, yetersiz uyum (underfitting — deseni yakalamak için çok basit) ile aşırı uyum (overfitting — gürültüyü yakalayacak kadar karmaşık) arasında bir spektrumda yer alır. Düzenleme, modelleri aşırı uyum tarafından bu orta noktaya doğru iter.

### Dropout

En basit düzenleme tekniği. Eğitim sırasında, her nöronun çıktısını p olasılığıyla rastgele sıfırlayın.

```
çıktı = aktivasyon(z) × maske    burada maske[i] ~ Bernoulli(1 - p)
```

p = 0.5 ile nöronların yarısı her ileri geçişte sıfırlanır. Ağ, yedekli gösterimler öğrenmelidir çünkü hangi nöronların kullanılabilir olacağını tahmin edemez. Bu, ko-adaptasyonu önler.

Ensemble yorumu: N nöronlu bir ağ, dropout ile 2^N olası alt ağ oluşturur. Dropout ile eğitim, tüm 2^N alt ağı aynı anda eğitmeye yakındır. Test zamanında tüm nöronlar kullanılır ve çıktılar (1 - p) ile ölçeklenir.

Uygulamada ölçekleme eğitim sırasında uygulanır (ters dropout):
```
Eğitim:   çıktı = aktivasyon(z) × maske / (1 - p)
Test:     çıktı = aktivasyon(z)   (değişiklik gerekmez)
```

### Ağırlık Azaltma (Weight Decay / L2 Düzenlemesi)

Tüm ağırlıkların kare büyüklüğünü kayba ekleyin:
```
toplam_kayıp = görev_kaybı + (λ / 2) × Σ(w_i²)
```

Düzenleme teriminin gradyanı λ × w'dir. Bu, her adımda her ağırlığın sıfıra doğru büyüklüğüyle orantılı olarak küçültüldüğü anlamına gelir.

### Batch Normalization

Her katmanın çıktısını mini-toplu iş boyunca normalleştirin:
```
μ = (1/B) × Σ(x_i)
σ² = (1/B) × Σ((x_i - μ)²)
x̂ = (x_i - μ) / √(σ² + ε)
y = γ × x̂ + β
```

γ ve β öğrenilebilir parametrelerdir. BatchNorm neden çalışır? Santurkar ve ark. (2018) gösterdi ki: kayıp manzarasını daha pürüzsüz yapar, Lipschitz sabitlerini küçültür. BatchNorm'un temel sınırlaması: toplu iş istatistiklerine bağımlıdır. Küçük toplu işlerde (< 32) gürültülüdür.

### Layer Normalization

Toplu iş yerine özellikler boyunca normalleştirin. Tek bir örnek için:
```
μ = (1/D) × Σ(x_j)
σ² = (1/D) × Σ((x_j - μ)²)
x̂ = (x_j - μ) / √(σ² + ε)
y = γ × x̂ + β
```

Transformer'ların BatchNorm yerine LayerNorm kullanmasının nedeni: her örnek bağımsız normalleştirilir, toplu iş boyutuna bağımlılık yoktur, eğitim ve çıkarım arasında fark yoktur.

### RMSNorm

Ortalama çıkarmasız LayerNorm. Zhang & Sennrich (2019) tarafından önerildi.
```
rms = √((1/D) × Σ(x_j²))
y = γ × x / rms
```

Ortalama hesaplaması yok, beta parametresi yok. LLaMA, LLaMA 2, LLaMA 3, Mistral ve çoğu modern LLM LayerNorm yerine RMSNorm kullanır.

### Veri Artırma (Data Augmentation) ve Erken Durdurma (Early Stopping)

Veri artırma: eğitim girdilerini dönüştürürken etiketleri koruyun (görüntüde kırp, döndür, renk oynat; metinde eşanlamlı değiştir; seste gürültü ekle). Erken durdurma: validasyon kaybı artmaya başladığında eğitimi durdurun.

## Uygulama

Aşağıdaki kodları `code/main.py` içinde sıfırdan inşa edin: Dropout sınıfı (eğitim/test modu), L2 ağırlık azaltma, BatchNorm, LayerNorm, RMSNorm ve düzenlemeli/ düzenlemesiz eğitim karşılaştırması. Tüm kaynak kod için orijinal İngilizce derse bakın.

## Kullanım

PyTorch tüm normalleştirme ve düzenlemeyi modül olarak sunar:
```python
model = nn.Sequential(
    nn.Linear(784, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(0.3),
    nn.Linear(256, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3),
    nn.Linear(128, 10),
)
```

`model.train()` / `model.eval()` geçişi kritiktir. Transformer'larda desen farklıdır: LayerNorm (BatchNorm değil), Dropout p=0.1.

## Temel Terimler

| Terim | Gerçekte ne anlama geldiği |
|-------|--------------------------|
| Aşırı uyum | Modelin eğitim performansının test performansını önemli ölçüde aşması |
| Düzenleme | Karmaşıklığı kısıtlayarak genellemeyi iyileştiren herhangi bir teknik |
| Dropout | Eğitim sırasında rastgele nöron sıfırlama, yedekli gösterimleri zorlama |
| Ağırlık azaltma | Ağırlıkları λ × w kadar sıfıra yaklaştırma |
| Batch normalization | Katman çıktılarını toplu iş boyunca normalleştirme |
| Layer normalization | Her örnek içinde özellikler boyunca normalleştirme |
| RMSNorm | LayerNorm'un ortalama çıkarmasız versiyonu, %10 daha hızlı |
| Erken durdurma | Validasyon kaybı düzelmediğinde eğitimi durdurma |

## Alıştırmalar

1. 2B veri için uzamsal dropout (spatial dropout) uygulayın
2. Label smoothing ile dropout'u birleştirin
3. BatchNorm ile farklı öğrenme hızlarında eğitin
4. Erken durdurma uygulayın
5. LayerNorm vs RMSNorm karşılaştırması yapın
