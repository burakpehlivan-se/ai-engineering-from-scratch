> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/16-sampling-methods/docs/en.md)

# Örnekleme Yöntemleri

> Örnekleme, yapay zekanın olasılık uzayını nasıl keşfettiğidir.

**Tür:** Uygulama
**Diller:** Python
**Ön Koşullar:** Faz 1, Ders 06-07 (Olasılık, Bayes Teoremi)
**Süre:** ~120 dakika

## Öğrenme Hedefleri

- Sadece uniform rastgele sayılar kullanarak sıfırdan ters CDF, ret ve önem örnekleme uygulayın
- Dil modeli token üretimi için sıcaklık, top-k ve top-p (çekirdek) örnelemesi oluşturun
- Yeniden parametreleme hilesini ve VAE'lerde örnekleme üzerinden geri yayılımı nasıl mümkün kıldığını açıklayın
- Normalleştirilmemiş hedef dağılımdan örnekleme yapmak için Metropolis-Hastings MCMC çalıştırın

## Sorun

Bir dil modeli isteminizi bitirir ve 50.000 logit'lik bir vektör üretir. Sözlüğündeki her token için bir tane. Şimdi birini seçmesi gerekiyor. Nasıl?

Her seferinde en yüksek olasılıklı token'ı seçerse, her yanıt aynıdır. Belirleyici. Sıkıcı. Rastgele seçerse, çıktı saçmalık olur. Cevap bu uçların bir yerinde yaşar ve o yer örnekleme tarafından kontrol edilir.

Örnekleme sadece metin üretimiyle sınırlı değildir. Pekiştirmeli öğrenme, politika gradyanlarını örnekleme yaparak tahmin eder. VAE'ler, öğrenilen dağılımlardan örnekleme yaparak ve rastgelelik üzerinden geri yayılım yaparak gizli temsilleri öğrenir. Difüzyon modelleri gürültü örnekleme yaparak ve tekrar tekrar gürültüden temizleyerek görüntüler üretir. Monte Carlo yöntemleri kapalı formu olmayan integralleri tahmin eder. MCMC algoritmaları sayılması imkansız olan yüksek boyutlu sonraki dağılımları keşfeder.

Her üreteç yapay zeka sistemi bir örnekleme sistemidir. Örnekleme stratejisi, çıktının kalitesini, çeşitliliğini ve kontrol edilebilirliğini belirler.

## Kavram

### Neden Önemli

Örnekleme, yapay zeka ve makine öğrenmesinde dört temel rolde görünür:

**Üretim.** Dil modelleri, difüzyon modelleri ve GAN'lar çıktıyı örnekleme yaparak üretir. Sıcaklık, top-k ve çekirdek örnelemesi mühendislerin her gün çevirdiği düğmelerdir.

**Eğitim.** Stokastik gradyan inişi toplu işleri örnekleme yapar. Dropout nötronları devre dışı bırakmak için örnekleme yapar. Veri artırma rastgele dönüşümler örnekleme yapar.

**Tahmin.** ML'de birçok niceliğin kapalı form çözümü yoktur. Monte Carlo tahminleri, örnekleme ortalamasıyla bunların tümünü yaklaşık hesaplar.

**Keşif.** MCMC algoritmaları Bayes çıkarımında sonraki dağılımları keşfeder. Evrimsel stratejiler parametreperturbasyonlarını örnekleme yapar.

### Uniform Örnekleme

Tüm sonuçların eşit olasılığa sahip olduğu en basit örnekleme.

```python
import numpy as np

# 0 ile 1 arasında 1000 rastgele sayı
ornekler = np.random.uniform(0, 1, 1000)
```

### Sıcaklık Örnelemesi

Softmax skorlarını sıcaklık parametresiyle ölçekler.

```python
def sicaklik_orneklemi(logitler, sicaklik=1.0):
    olasiliklar = np.exp(logitler / sicaklik)
    olasiliklar = olasiliklar / olasiliklar.sum()
    return np.random.choice(len(logitler), p=olasiliklar)
```

#### Açıklama
Sıcaklık = 1: normal dağılım. Sıcaklık > 1: daha rastgele. Sıcaklık < 1: daha belirleyici.

### Top-k Örnelemesi

En yüksek k olasılıklı token arasından seçer.

### Top-p (Çekirdek) Örnelemesi

Toplam olasılığı p'yi aşan en küçük token kümesinden seçer.

## Alıştırmalar

1. Ters CDF ile normal dağılımdan örnekleme yapın
2. Farklı sıcaklık değerleriyle metin üretin ve sonuçları karşılaştırın
3. Basit bir MCMC algoritması uygulayın

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Örnekleme | "Rastgele seçim" | Olasılık dağılımından değer seçme |
| Sıcaklık | "Rastgelelik düğmesi" | Softmax skorlarını ölçekleyen parametre |
| Top-k | "En iyi k seçenek" | En yüksek k olasılıklı token'dan örnekleme |
| Top-p | "Çekirdek örnekleme" | Toplam olasılığı aşan en küçük kümeden örnekleme |
| MCMC | "Zincir örnekleme" | Dağılımdan örnekleme için Markov zinciri yöntemleri |
| Monte Carlo | "Sayısal entegral" | Örnekleme ortalamasıyla integral yaklaşık hesaplama |
