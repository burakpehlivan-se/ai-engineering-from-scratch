# Değerlendirme — FID, CLIP Score, İnsan Tercihleri

> Her üretici model liderlik tablosu FID, CLIP skoru ve insan tercihi arenasından bir kazanma oranı (win rate) sunar. Her sayının, kararlı bir araştırmacının manipüle edebileceği bir hata modu vardır. Hata modlarını bilmiyorsanız, gerçek bir iyileştirmeyi manipüle edilmiş bir çalışmadan ayırt edemezsiniz.

**Tür:** İnşa Et
**Diller:** Python
**Ön koşullar:** Faz 8 · 01 (Sınıflandırma), Faz 2 · 04 (Değerlendirme Metrikleri)
**Süre:** ~45 dakika

## Problem

Bir üretici model *örnekleme kalitesi* ve *koşullandırma uyumu* (prompt adherence) üzerine değerlendirilir. Hiçbirinin kapalı formülü (closed-form measure) yoktur. Modelinizin 10.000 görsel render etmesi gerekir; bunlara birilerinin sayı ataması gerekir; bu sayıların model aileleri, çözünürlükler ve mimariler boyunca güvenilir olması gerekir. Üç metrik 2014-2026 sınavından sağ çıktı:

- **FID (Fréchet Inception Distance).** İki dağılım — gerçek ve üretilmiş — arasındaki mesafe, bir Inception ağı özellik uzayında. Düşük olan daha iyidir.
- **CLIP skoru.** Üretilmiş bir görselin CLIP-görüntü embedding'i ile bir promptun CLIP-metin embedding'i arasındaki kosinüs benzerliği (cosine similarity). Yüksek olan daha iyidir. Prompt uyumunu ölçer.
- **İnsan tercihleri (human preference).** Aynı promptta iki modeli karşı karşıya getirin, insanlara (veya GPT-4 sınıfı bir modele) daha iyisini seçtirin, bir Elo skoruna toplayın.

Ayrıca göreceksiniz: IS (inception score, büyük ölçüde emekli), KID, CMMD, ImageReward, PickScore, HPSv2, MJHQ-30k. Her biri bir öncekinin bir hatasını düzeltir.

## Kavram

![FID, CLIP ve tercih: üç eksen, farklı hata modları](../assets/evaluation.svg)

### FID — örnekleme kalitesi

Heusel ve ark. (2017). Adımlar:

1. N gerçek görsel ve N üretilmiş görsel için Inception-v3 özelliklerini (2048-B) çıkarın.
2. Her havuza bir Gaussian uydurun: ortalama `μ_r, μ_g` ve kovaryans `Σ_r, Σ_g` hesaplayın.
3. FID = `||μ_r - μ_g||² + Tr(Σ_r + Σ_g - 2 · (Σ_r · Σ_g)^0.5)`.

Yorum: Özellik uzayında iki çok değişkenli (multivariate) Gaussian arasındaki Fréchet mesafesi. Daha düşük = daha benzer dağılımlar.

Hata modları:
- **Küçük N'de yanlı.** FID, özellik dağılımı üzerinde ortalamalı karedir — küçük N kovaryansı hafife alır, yanlış düşük FID verir. Her zaman N ≥ 10.000 kullanın.
- **Inception'a bağımlı.** Inception-v3 ImageNet üzerinde eğitilmiştir. ImageNet'ten uzak alanlar (yüzler, sanat, metin görselleri) anlamsız FID üretir. Alana özgü özellik çıkarıcı kullanın.
- **Manipülasyon.** Inception öneline (prior) aşırı öğrenme, görsel kalite iyileştirmesi olmadan düşük FID verir. CMMD ile yenebilir (aşağıda).

### CLIP skoru — prompt uyumu

Radford ve ark. (2021). Üretilmiş bir görsel + prompt için:

```
clip_score = cos_sim( CLIP_image(x_gen), CLIP_text(prompt) )
```

30k üretilmiş görsel ortalaması → modeller arasında karşılaştırılabilir bir skaler.

Hata modları:
- **CLIP'in kendi kör noktaları.** CLIP zayıf bileşimsel (compositional) muhakemeye sahiptir ("mavi bir küre üzerinde kırmızı bir küp" genellikle başarısız olur). Modeller karmaşık promptları gerçekten takip etmeden CLIP skorunda iyi sıralanabilir.
- **Kısa prompt yanlılığı.** Kısa promptların doğada daha fazla CLIP-görüntü eşleşmesi vardır. Daha uzun promptlar mekanik olarak daha düşük CLIP skorlarına sahiptir.
- **Prompt manipülasyonu.** Prompta "yüksek kalite, 4k, başyapıt" eklemek, görüntü-metin bağını iyileştirmeden CLIP skorunu şişirir.

CMMD (Jayasumana ve ark., 2024) bunların bazılarını düzeltir: Inception yerine CLIP özellikleri, Fréchet yerine maksimum ortalama farkı (maximum-mean discrepancy) kullanır. İnce kalite farklarını tespit etmede daha iyidir.

### İnsan tercihleri — ground truth

Bir prompt havuzu seçin. Model A ve Model B ile üretin. Çiftleri insanlara (veya güçlü bir LLM hakeme) gösterin. Kazanmaları Elo veya Bradley-Terry skoruna toplayın. Benchmark'lar:

- **PartiPrompts (Google)**: 1.600 çeşitli prompt, 12 kategori.
- **HPSv2**: 107k insan notu, yaygın olarak otomatik vekil olarak kullanılır.
- **ImageReward**: 137k prompt-görsel tercih çifti, MIT lisanslı.
- **PickScore**: Pick-a-Pic'in 2.6M tercihi üzerinde eğitilmiş.
- **Chatbot-Arena tarzı görüntü arenaları**: https://imagearena.ai/ ve diğerleri.

Hata modları:
- **Hakem varyansı.** Uzman olmayanların uzmanlardan farklı tercihleri vardır. Her ikisini de kullanın.
- **Prompt dağılımı.** Seçilmiş (cherry-picked) promptlar bir aileyi tercih eder. Her zaman belgeleyin.
- **LLM-hakem ödül hack'lemesi.** GPT-4-hakem, güzel ama yanlış çıktılar tarafından kandırılır. İnsan ile üçlü doğrulama (triangulate) yapın.

## Birlikte kullanın

Bir üretim eval raporu şunları içermelidir:

1. 10-30k örnekte tutulmuş gerçek dağılıma karşı FID (örnekleme kalitesi).
2. Aynı örneklerde promptlara karşı CLIP skoru / CMMD (uyum).
3. Önceki modele karşı kör arenada kazanma oranı (genel tercih).
4. Hata modu analizi: 50 rastgele seçilmiş çıktı, bilinen sorunlar için işaretlenmiş (el anatomisi, metin renderlama, tutarlı nesne sayısı).

Tek başına herhangi bir metrik bir yalandır. Üç doğrulayıcı metrik + niteliksel inceleme bir iddiadır.

## İnşa Et

`code/main.py`, sentetik "özellik vektörleri" (Inception özellikleri yerine 4-B vektörler kullanıyoruz) üzerinde FID, CLIP-skor benzeri ve Elo toplaması uygular. Şunları görürsünüz:

- Küçük N ve büyük N'de FID hesabı — yanlılık.
- Özellik havuzları arasında kosinüs benzerliği olarak "CLIP skoru".
- Sentetik tercih akışından Elo güncelleme kuralı.

### Adım 1: dört satırda FID

```python
def fid(real_features, gen_features):
    mu_r, cov_r = mean_and_cov(real_features)
    mu_g, cov_g = mean_and_cov(gen_features)
    mean_diff = sum((a - b) ** 2 for a, b in zip(mu_r, mu_g))
    trace_term = trace(cov_r) + trace(cov_g) - 2 * sqrt_cov_product(cov_r, cov_g)
    return mean_diff + trace_term
```

### Adım 2: CLIP tarzı kosinüs benzerliği

```python
def clip_like(image_feat, text_feat):
    dot = sum(a * b for a, b in zip(image_feat, text_feat))
    norm = math.sqrt(dot_self(image_feat) * dot_self(text_feat))
    return dot / max(norm, 1e-8)
```

### Adım 3: Elo toplaması

```python
def elo_update(r_a, r_b, winner, k=32):
    expected_a = 1 / (1 + 10 ** ((r_b - r_a) / 400))
    actual_a = 1.0 if winner == "a" else 0.0
    r_a_new = r_a + k * (actual_a - expected_a)
    r_b_new = r_b - k * (actual_a - expected_a)
    return r_a_new, r_b_new
```

## Tuzaklar

- **N=1000'de FID.** N=10k altındaki sezgisel yöntem güvenilmezdir. Düşük-N FID bildiren makaleler manipüle eder.
- **FID'yi farklı çözünürlüklerde karşılaştırma.** Inception'ın 299×299 yeniden boyutlandırması özellik dağılımını değiştirir. Yalnızca eşleşen çözünürlükte karşılaştırın.
- **Tek seed raporlama.** Minimum 3 seed çalıştırın. Std raporlayın.
- **Negatif promptlarla CLIP skoru şişirme.** Bazı pipeline'lar prompta aşırı öğrenerek CLIP'i artırır. Görsel doygunluk (saturation) kontrol edin.
- **Prompt örtüşmesinden Elo yanlılığı.** Her iki model de eğitim sırasında bir benchmark promptu gördüyse, Elo anlamsızdır. Tutulmuş prompt setleri kullanın.
- **İnsan değerlendirme ücretli kalabalık yanlılığı.** Prolific, MTurk notlayıcıları daha genç / teknoloji-dostu eğilimindedir. İşe alınan sanat/tasarım uzmanlarıyla harmanlayın.

## Kullan

2026 üretim eval protokolü:

| Sütun | Minimum | Önerilen |
|-------|---------|----------|
| Örnekleme kalitesi | Tutulmuş gerçek diziye karşı 10k'da FID | + 5k'da CMMD + kategoriye göre alt kümede FID |
| Prompt uyumu | 30k'da CLIP skoru | + HPSv2 + ImageReward + VQA tarzı soru-cevap |
| Tercih | Temel modele karşı 200 kör çift | + 2000 çiftli insan + LLM-hakem + Chatbot Arena |
| Hata analizi | 50 elle işaretli | 500 elle işaretli + otomatik güvenlik sınıflandırıcı |

Dört sütunun hepsi bir raporda = iddia. Tek başına herhangi biri = pazarlama.

## Teslim Et

`outputs/skill-eval-report.md` dosyasını kaydedin. Skill yeni bir model checkpoint'i + temel hat alır ve tam bir eval planı çıkarır: örnek boyutları, metrikler, hata modu testleri, onay kriterleri.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Aynı sentetik dağılımlarda N=100 vs N=1000'de FID'yi karşılaştırın. Yanlılık büyüklüğünü raporlayın.
2. **Orta.** Sentetik CLIP tarzı özelliklerden CMMD uygulayın (formül için Jayasumana ve ark., 2024'e bakın). FID'ye göre kalite farklarına duyarlılığı karşılaştırın.
3. **Zor.** HPSv2 kurulumunu çoğaltın: Pick-a-Pic'in bir alt kümesinden 1000 görsel-prompt çifti alın, tercihler üzerinde küçük bir CLIP tabanlı puanlayıcıyı fine-tune edin ve tutulmuş bir diziyle uyumunu ölçün.

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| FID | "Fréchet Inception Distance" | Gerçek vs üretilmiş Inception özelliklerinin Gaussian uydurmasının Fréchet mesafesi. |
| CLIP skoru | "Metin-görüntü benzerliği" | CLIP görüntü ve metin embedding'leri arasındaki kosinüs benzerliği. |
| CMMD | "FID'nin halefi" | CLIP-özellik MMD'si; daha az yanlı, Gaussian varsayımı yok. |
| IS | "Inception score" | Exp KL(p(y|x) || p(y)); modern modellerde zayıf korelasyon, emekli. |
| HPSv2 / ImageReward / PickScore | "Öğrenilmiş tercih vekilleri" | İnsan tercihleri üzerinde eğitilmiş küçük modeller; otomatik hakem olarak kullanılır. |
| Elo | "Satranç puanı" | Çiftli kazanımların Bradley-Terry toplaması. |
| PartiPrompts | "Benchmark prompt seti" | 12 kategoride 1.600 Google tarafından seçilmiş prompt. |
| FD-DINO | "Otonom ikame" | DINOv2 özellikleri kullanan FD; ImageNet-dışı alanlar için daha iyi. |

## Üretim notu: değerlendirme bir çıkarım iş yüküdür

10k örnekte FID çalıştırmak, 10k görsel üretmek demektir. Tek bir L4 üzerinde 1024²'de 50 adımlı SDXL tabanı için bu, yaklaşık 11 saat tek istekli çıkarımdır. Değerlendirme bütçeleri gerçektir ve çerçeve tam olarak çevrimdışı çıkarım senaryosudur (throughput'u en üst düzeye çıkar, TTFT'i göz ardı et):

- **Gruplayın, gecikmeyi unutun.** Çevrimdışı eval = belleğe sığan en büyük boyutta statik gruplama. `pipe(...).images` ile `num_images_per_prompt=8` 80GB H100'de tek istekten 4-6× daha hızlı duvar-saatine (wall-clock) çalışır.
- **Gerçek özellikleri önbelleğe alın.** Inception (FID) veya CLIP (CLIP-skoru, CMMD) özellik çıkarma, gerçek referans seti üzerinde *bir kez* çalıştırılır, `.npz` olarak saklanır. Her eval'da yeniden hesaplamayın.

CI / gerileme kapıları için: PR başına 500 örneklik alt kümede FID + CLIP skoru çalıştırın (~30 dk); gecelik tam 10k FID + HPSv2 + Elo çalıştırın.

## Daha Fazla Kaynak

- [Heusel ve ark. (2017). GANs Trained by a Two Time-Scale Update Rule Converge to a Local Nash Equilibrium (FID)](https://arxiv.org/abs/1706.08500) — FID makalesi.
- [Jayasumana ve ark. (2024). Rethinking FID: Towards a Better Evaluation Metric for Image Generation (CMMD)](https://arxiv.org/abs/2401.09603) — CMMD.
- [Radford ve ark. (2021). Learning Transferable Visual Models from Natural Language Supervision (CLIP)](https://arxiv.org/abs/2103.00020) — CLIP.
- [Wu ve ark. (2023). HPSv2: A Comprehensive Human Preference Score](https://arxiv.org/abs/2306.09341) — HPSv2.
- [Xu ve ark. (2023). ImageReward: Learning and Evaluating Human Preferences for Text-to-Image Generation](https://arxiv.org/abs/2304.05977) — ImageReward.
- [Yu ve ark. (2023). Scaling Autoregressive Models for Content-Rich Text-to-Image Generation (Parti + PartiPrompts)](https://arxiv.org/abs/2206.10789) — PartiPrompts.
- [Stein ve ark. (2023). Exposing flaws of generative model evaluation metrics](https://arxiv.org/abs/2306.04675) — hata modu araştırması.
