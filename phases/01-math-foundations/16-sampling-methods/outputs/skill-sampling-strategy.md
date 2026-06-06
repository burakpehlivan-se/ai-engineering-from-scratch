---
name: skill-sampling-strategy
description: Üretim, tahmin veya çıkarım için doğru örnekleme yöntemini seç
version: 1.0.0
phase: 1
lesson: 16
tags: [sampling, mcmc, generation]
---

# Örnekleme Stratejisi Seçimi

Metin üretimi, Bayesçi çıkarım, Monte Carlo tahmini ve eğitim için doğru örnekleme yöntemini nasıl seçersin.

## Karar Kontrol Listesi

1. Çıktı mı üretiyorsun (metin, görüntü) yoksa bir niceliği mi tahmin ediyorsun (integral, beklenen değer)?
2. Hedef dağılımdan doğrudan örnekleyebiliyor musun, yoksa yalnızca yoğunluğunu mu değerlendirebiliyorsun?
3. Hedef dağılım ayrık mı sürekli mi?
4. Örnek uzayının boyutu nedir? Düşük (< 5), orta (5-100), yüksek (> 100)?
5. Tam örneklemeye mi ihtiyacın var yoksa yaklaşık örneklemeler yeterli mi?
6. Örnekleme işleminden geçen gradyanlara mı ihtiyacın var?

## Her yöntemin ne zaman kullanılacağı

| Yöntem | Ne zaman kullanılır | Karmaşıklık | Tam mı? |
|---|---|---|---|
| Doğrudan örnekleme | CDF'in var veya bir kütüphane fonksiyonu kullanabilirsin | Örnek başına O(1) | Evet |
| Ters CDF | Kapalı form CDF tersi biliniyor (üstel, Cauchy) | Örnek başına O(1) | Evet |
| Box-Muller | Kütüphane olmadan normal örneklere ihtiyacın var | Örnek başına O(1) | Evet |
| Reddetme örneklemesi | Hedef PDF'i değerlendirebilirsin, düşük boyut (1-3) | Örnek başına O(1/kabul) | Evet |
| Önem örneklemesi | Beklenen değerlere ihtiyacın var, bireysel örneklere değil | n örnek için O(n) | Yaklaşık |
| Tabakalı örnekleme | Monte Carlo tahmini, daha düşük varyans istiyorsun | n örnek için O(n) | Yaklaşık |
| Metropolis-Hastings | Yüksek boyutlu, normalleştirilmemiş yoğunluğu değerlendirebilirsin | Adım başına O(1) + yanma | asimptotik |
| Gibbs örneklemesi | Her koşullu dağılımdan örnekleyebilirsin | Tam geçiş başına O(d) | asimptotik |
| HMC/NUTS | Yüksek boyutlu sürekli, pürüzsüz yoğunluk | Adım başına O(L * d) | asimptotik |
| Sıcaklık örneklemesi | LLM metin üretimi, yaratıcılığı kontrol etme | Sözlük boyutu V için O(V) | N/A |
| Top-k örneklemesi | LLM üretimi, olası olmayan tokenleri kaldırma | O(V log k) | N/A |
| Top-p (çekirdek) | LLM üretimi, uyarlanabilir aday kümesi | O(V log V) | N/A |
| Yeniden parametrelendirme | Gauss örneklemesinden geçen gradyanlara ihtiyacın var (VAE) | O(d) | Evet |
| Gumbel-Softmax | Kategorik örneklerden geçen gradyanlara ihtiyacın var | k sınıf için O(k) | Yaklaşık |

## LLM üretim ayarları

| Kullanım durumu | Sıcaklık | Top-p | Top-k | Notlar |
|---|---|---|---|---|
| Olgusal soru-yanıt | 0.0 (greedy) | -- | -- | Deterministik, rastgelelik yok |
| Kod üretimi | 0.2-0.5 | 0.9 | -- | Düşük yaratıcılık, yüksek tutarlılık |
| Genel sohbet | 0.7 | 0.9 | -- | Dengeli |
| Yaratıcı yazarlık | 0.9-1.2 | 0.95 | -- | Daha yüksek çeşitlilik |
| Beyin fırtınası | 1.0-1.5 | 0.95 | -- | Maksimum çeşitlilik, tutarlılık kaybı olabilir |

Sıcaklık ve top-p birleştirilebilir. Önce sıcaklığı uygula (logits'leri ölçekle), ardından top-p filtrelemesini uygula.

## MCMC yöntemi seçimi

| Özellik | Metropolis-Hastings | Gibbs | HMC/NUTS |
|---|---|---|---|
| Boyut | Herhangi biri | Herhangi biri (en iyi < 100) | Yüksek (100+) |
| Koşullular gerekir mi | Hayır | Evet | Hayır |
| Gradyan gerekir mi | Hayır | Hayır | Evet |
| Kabul oranı | ~%23'e ayarla | Her zaman %100 | ~%65'e ayarla |
| Korelasyon | Yüksek (rastgele yürüyüş) | Orta | Düşük |
| Yanma | Uzun | Orta | Kısa |
| En iyi | Keşif, basit modeller | Eşlenik modeller, Bayes ağları | Sürekli sonsal dağılımlar, derin olasılıksal modeller |

## Yaygın hatalar

- Yüksek boyutlarda reddetme örneklemesi kullanmak. Kabul oranı boyutla üstel olarak düşer. 5 boyutun üzerinde MCMC'ye geç.
- MCMC öneri varyansını çok yüksek veya çok düşük ayarlamak. Çok yüksek: çoğu öneri reddedilir, zincir takılır. Çok düşük: tüm öneriler kabul edilir, zincir yavaş hareket eder. Rastgele yürüyüş MH için ~%23 kabul oranını hedefle.
- Yanmayı unutmak. MCMC'den gelen ilk N örnek, başlangıç noktası tarafından yanlıdır. En az 1000 adımı at (veya karmaşık dağılımlar için daha fazlasını).
- Önerisi hedeften çok farklı olan önem örneklemesi kullanmak. Birkaç örnek çok büyük ağırlıklar alır ve tahmini güvenilmez kılar. Etkin örneklem büyüklüğünü izle: ESS = (sum w_i)^2 / sum(w_i^2).
- Deterministik çıktı gerektiren görevler için (ör. sınıflandırma, yapılandırılmış çıkarım) sıcaklık > 0 kullanmak. Bunun yerine greedy (T=0) veya ışın araması (beam search) kullan.
- Sıcaklığı top-p ile birleştirmemek. Sıcaklık tek başına uzun kuyruktaki çöp tokenleri kaldırmaz. Top-p kaldırır.
- Standart bir örnekleme işleminden geriye yayılım (backpropagation) yapmak. Sürekli (Gauss) için yeniden parametrelendirme hilesini, ayrık (kategorik) için Gumbel-Softmax'ı kullan.

## Hızlı başvuru: varyans azaltma teknikleri

| Teknik | Nasıl çalışır | Varyans azaltma |
|---|---|---|
| Tabakalı örnekleme | Uzayı tabakalara böl, her birinden örnekle | Her zaman <= standart MC |
| Antitetik değişkenler | Hem U hem 1-U kullan | Monoton fonksiyonlar için çalışır |
| Kontrol değişkenleri | Bilinen ortalamalı bir değişkeni çıkar | Korelasyonla orantılı |
| Önem örneklemesi | Daha iyi bir öneriden örnekleri yeniden ağırlıklandır | Öneri kalitesine bağlı |
| Latin hiperküpü | Her boyutu bağımsız olarak tabakala | Yüksek boyutlarda tabakalıdan daha iyi |
