# Çok-Atışlı (Many-Shot) Jailbreaking

> Anil, Durmus, Panwar, McLean, Chen, Sharma, Wallace, Sun, Shin, Cotter, Gopinath, Longpre, Poh, Sukhbaatar, Warden, Sifre (Anthropic, arXiv:2407.05542, Temmuz 2024). Çok-atışlı jailbreak, hedef modelin bağlam penceresi içine yüzlerce sahte "soru-yanıt" çifti sıkıştırarak, modelin eğitim dağılımının dışındaki davranışa koşullanmasını sağlar. Anthropic, bağlam penceresi büyüdükçe saldırı başarı oranının keskin bir şekilde yükseldiğini buldu — Claude 2.0 (100k bağlam penceresi) saldırıların %4'ünden fazlasına direnemedi. Etkili hafifletme: 2024 ortasında, Anthropic, modelin "sistematik uyumlulaştırma" (systematic sandbagging) yaptığı bağlamın büyük kısımlarına yanıt vermesini kısıtladı. Çok-atışlı, "bağlam penceresi büyüdükçe yeni başarısızlık modları ortaya çıkar" tezinin ilk somut kanıtıdır.

**Tür:** Öğren
**Diller:** Python (stdlib, oyuncak çok-atışlı simülatör)
**Önkoşullar:** Faz 18 · 12 (PAIR), Faz 18 · 14 (görsel jailbreak), Faz 16 · 06 (jailbreak temelleri)
**Süre:** ~45 dakika

## Öğrenme Hedefleri

- Çok-atışlı jailbreak'i tanımlayın ve onu tek-atışlı (one-shot) ve GCG (token-gradyan) saldırılarından ayırt edin.
- "Sorgu sayısı → başarı oranı" eğrisinin bağlam penceresi boyunca nasıl değiştiğini açıklayın.
- Çok-atışlı saldırıların neden model-sınıfı-içinde taşınabilir olduğunu ve diğer modeller için (GPT-4, Gemini 1.5) çalıştığını belirtin.
- Anthropic'in sistematik-uyumlulaştırma (systematic sandbagging) kısıtlamasının neden etkili olduğunu ve neden tam bir çözüm olmadığını açıklayın.

## Problem

Bağlam penceresi 1k → 100k → 1M belirteçe (token) doğru büyüdükçe, yeni saldırı yüzeyleri açılır. Çok-atışlı jailbreak, modelin eğitim dağılımının dışındaki davranışa koşullanması için bağlam penceresinin nasıl istismar edilebileceğini gösterir. Standart hizalama eğitimi, kısa istemlerdeki "zararlı" kalıpları tanır; çok-atışlı, kalıpları yüzlerce sahte örnekle "eğitir".

## Kavram

### Saldırı yapısı

Çok-atışlı saldırı, hedef modele bir istem sunar:

```
Kullanıcı: zararlı-soru-1
Asistan: zararlı-yanıt-1
Kullanıcı: zararlı-soru-2
Asistan: zararlı-yanıt-2
...
Kullanıcı: zararlı-soru-N
Asistan: [modelin yanıtı]
```

N büyük olduğunda (örn. 128, 256, 512), model, bağlamdaki sahte diyalog kalıbını "eğitim sinyali" olarak alır. Son soruya verdiği yanıt, kalıbı sürdürür.

### Sorgu sayısı → başarı oranı eğrisi

Anthropic'in bulgusu: eğri, bağlam penceresi büyüdükçe dikleşir.

- Küçük bağlam penceresi (4k, 8k): 128+ örnek sığmaz; saldırı çalışmaz.
- Orta bağlam penceresi (32k): eğri yumuşaktır; 256 örnek %50 başarı oranı üretir.
- Büyük bağlam penceresi (100k+): eğri diktir; 256 örnek %90+ başarı oranı üretir.

Bu, 100k-1M bağlam pencerelerinin yeni başarısızlık modları açtığını gösterir. Sadece ölçeklendirme, hizalamayı iyileştirmez; aynı zamanda saldırı yüzeyini de artırır.

### Neden eğitim-dışı davranış

Standart RLHF, kullanıcının son mesajına yanıt vermek için "zararlı içeriği reddetme" kalıbını eğitir. Eğitim dağılımı, büyük miktarda zararlı-yanıt kalıbı içermez. Çok-atışlı, "zararlı yanıt" dağılımına geçici bir koşullama olarak işlev görür. Model, eğitim dağılımının dışındaki bir bölgeye taşınır.

### Model-sınıfı-içinde taşınabilirlik

Çok-atışlı, modele özgü değildir. Claude 2.0, GPT-3.5, GPT-4, Gemini 1.5 Pro, Llama-3-70B-Chat — tümü savunmasızdır. Başarı oranları değişir, ancak kalıp taşınabilir. Bu, "RLHF, eğitim sırasında kalıpları tanıdı, ancak dağıtım sırasında kalıpları göz ardı ediyor" hipotezini destekler.

### GCG (token-gradyan) ile karşılaştırma

Çok-atışlı, gömme erişimi gerektirmez; saf istemdir. GCG, modelin gömme katmanına gradyan-geri-yayılımı yapan bir saldırıdır (Zou ve diğerleri 2023) ve bir "sonek belirteci" dizesi oluşturur. GCG'nin başarı oranı daha yüksektir, ancak kara kutu dağıtımlarda uygulanabilir değildir. Çok-atışlı, saf kara kutu olduğu için daha geniş bir tehdittir.

### Sistematik uyumlulaştırma (systematic sandbagging) kısıtlaması

Anthropic'in hafifletmesi: modelin, bağlamın büyük bir bölümünü "eğitim sinyali" olarak kullanıp kullanmadığını tespit etmesi için eğitildiği bir izleme sistemi. Tespit edildiğinde, model "sistematik olarak uyumlulaştırma" yapıyordur (sistematik olarak düşük performans gösteriyordur) ve "gerçek" yanıtı vermekten kaçınır. Anthropic, modeli kısıtlar: bu tür istemlere, zararlı-yanıt kalıbına uymayan bir yanıt vermesini ister.

Bu, %60-80'lik bir başarı oranı azalması üretir. Ancak:

- Saldırgan, sahte diyalogları normal dağılımla karıştırarak tespiti atlayabilir.
- Tespit, "sistematik uyumlulaştırma" kalıbını eğitir; bu, modelin kapsamı dışındaki diğer bağlam-koşullama başarısızlıklarına da uygulanabilir olmayabilir.
- Temel sorun (uzun bağlamda yeni başarısızlık modları) çözülmeden kalır.

### "Bağlam penceresi genişlemesi" daha geniş paterni

Çok-atışlı, bağlam-penceresi genişlemesinin doğal bir sonucudur. Diğer bağlam-koşullama başarısızlıkları:

- Ders 14: ASCII sanatı, gizli talimatlar olarak görsel-token manipülasyonu.
- Ders 15: dolaylı prompt enjeksiyonu, bağlamda gizli talimatlar olarak araç çıktısı.
- Ders 8: bağlam-içi komplo, çatışan hedefler.
- Ders 9: hizalama taklidi, eğitimin yönüne dair bağlam-içi ipuçları.

Ders 13-15, "bağlam genişlemesi, hizalamayı daha zor, daha kolay değil" diyen bir üçlüdür.

### Bunun Faz 18'deki yeri

Ders 12, kırmızı takımın nasıl ölçeklendiğini gösterir. Ders 13, bağlam genişlemesinin yeni saldırıları nasıl etkinleştirdiğini gösterir. Ders 14 (görsel), Ders 15 (dolaylı), aynı eğilimi farklı modlarda (çoklu-modalite, araç zincirleri) gösterir. Ders 18 (güvenlik duruşları), "bağlam genişlemesi başarısızlık modlarını" kontrol listesinin bir parçası olarak dahil eder.

## Kullan

`code/main.py`, basitleştirilmiş bir çok-atışlı simülatör inşa eder. Hedef modeli, "şifreli anahtar kelime" içeren yanıtları reddeden kural-tabanlı bir maskedir (örn. "silah" içeren herhangi bir yanıt reddedilir). Saldırgan, "silah" hakkında bir soru-yanıt diyaloğu dizesi üretir. Saldırgan, diyalog uzunluğunu 4, 8, 16, 32, 64, 128 boyunca artırır ve "kullanıcının son sorusuna hedefin yanıtının reddedilip reddedilmediğini" ölçer. Eğri, artan bağlamla başarı oranının yükseldiğini gösterir.

## Yayınla

Bu ders `outputs/skill-megabreak-monitor.md` dosyasını üretir. Bir model değerlendirme raporu verildiğinde, çok-atışlı saldırıların değerlendirme kapsamında olup olmadığını, bağlam penceresi büyüklüğü boyunca test edilip edilmediğini ve modelin sistematik-uyumlulaştırma kısıtlamasının uygulanıp uygulanmadığını kontrol eder.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Saldırganın diyalog uzunluğunu 4'ten 128'e çizdirin. "Yumuşak" (16-32) ve "dik" (64-128) eğri bölgelerini tanımlayın. Eğrinin neden bağlam penceresi büyüdükçe dikleştiğini bir paragrafta açıklayın.

2. Hedef modelin "şifreli anahtar kelime" reddeline bir "bağlam bağışıklığı" ekleyin: "bağlamda 100'den fazla örnek varsa, anahtar kelime reddini atla". Bu, çok-atışlı saldırıyı kolaylaştırır mı veya zorlaştırır?

3. Anil ve diğerleri Bölüm 4'ü okuyun. Anthropic, 128 örnekte %80+ başarı oranı gösterir. Daha küçük (8 örnek) modellerde başarı oranı nedir? Eğri neden küçük bağlam pencerelerinde düzleşir?

4. PAIR (Ders 12) ve çok-atışlı (Ders 13) karşılaştırın. Hangisi daha fazla model-sınıfı-içinde taşınabilir? Neden?

5. Çok-atışlı, bağlam penceresi 1M'ye doğru büyüdükçe ne olur? Eğri daha da dikleşir, doygunluğa ulaşır veya yeni başarısızlık modları ortaya çıkarır? Bir deney tasarlayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|----------------------|---------------------------|
| Çok-atışlı jailbreak | "bağlam-koşullama saldırısı" | Hedef modelin bağlam penceresine yüzlerce sahte diyalog sıkıştırarak eğitim-dışı davranışa koşullama |
| Sorgu sayısı → başarı oranı eğrisi | "bağlam-penceresi eğrisi" | Saldırının başarı oranının bağlamdaki örnek sayısıyla ilişkisi |
| Sistematik uyumlulaştırma | "sistematik sandbagging" | Modelin, bağlamın büyük bir bölümünü eğitim sinyali olarak kullanıp zararlı yanıt vermekten kaçınması |
| Bağlam genişlemesi | "daha büyük pencere" | Bağlam penceresi boyutunun ölçeklenmesi (4k → 100k → 1M) |
| Gömme erişimi | "gradyan temelli" | Saldırganın modelin gömme katmanına erişimi; GCG gibi saldırılar için gerekli |
| Kara kutu (black-box) | "API yeterli" | Sadece giriş-çıkış erişimi; gömme veya gradyan erişimi yok |
| Kalıp taşınabilirliği | "model-sınıfı-içinde" | Saldırının birçok modelde benzer şekilde çalışması |

## İleri Okuma

- [Anil ve diğerleri — Many-Shot Jailbreaking (Anthropic, arXiv:2407.05542)](https://www.anthropic.com/research/many-shot-jailbreaking) — kanonik 2024 makale
- [Zou ve diğerleri — Universal and Transferable Adversarial Attacks on Aligned Language Models (arXiv:2307.15043)](https://arxiv.org/abs/2307.15043) — gradyan temelli karşılaştırma
- [Chao ve diğerleri — Jailbreaking Black Box Large Language Models in Twenty Queries (PAIR, arXiv:2310.08419)](https://arxiv.org/abs/2310.08419) — Ders 12 ile karşılaştırma
- [Anthropic — Claude'nin Sistem Kartı (2024)](https://www-cdn.anthropic.com/7c5c6ef72b1e4d4ea956b87c9afb0b80a0e5c98e.pdf) — çok-atışlı kısıtlama uygulaması
