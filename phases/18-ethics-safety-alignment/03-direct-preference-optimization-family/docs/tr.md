# Doğrudan Tercih Optimizasyonu Ailesi

> Rafailov ve diğerleri (2023), RLHF'nin optimum noktasının tercih verileri cinsinden kapalı bir formu olduğunu, böylece açık ödül modelini atlayıp politikayı doğrudan optimize edebileceğinizi gösterdi. Bu içgörü bir aile doğurdu — IPO, KTO, SimPO, ORPO, BPO — her biri DPO'nun bir başarısızlık modunu düzeltiyor. 2026'da, doğrudan hizalama algoritmaları (Direct Alignment Algorithms, DAA) PPO'dan daha fazla frontier post-training çalışmasıyla dağıtılıyor. Ama Ders 2'den aşırı optimizasyon eğrisi hâlâ geçerli: DAA'lar Goodhart'tan kaçmaz, sadece nerenin ısırdığını değiştirir.

**Tür:** Öğren
**Diller:** Python (stdlib, altı varyantlı tercih kaybı karşılaştırıcısı)
**Önkoşullar:** Faz 18 · 01 (InstructGPT), Faz 18 · 02 (ödül hacking'i), Faz 10 · 08 (DPO temelleri)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- DPO kapalı formunu KL'li RLHF optimumundan türetin.
- IPO, KTO, SimPO, ORPO, BPO'nun her birinin DPO'da düzelttiği başarısızlık modunu belirtin.
- "Örtük ödül boşluğu"nu (implicit reward gap) "tercih gücünden" (preference strength) ayırt edin ve IPO'nun kimlik (identity) eşlemesinin neden önemli olduğunu açıklayın.
- Rafailov ve diğerlerinin (NeurIPS 2024) DAA'ların neden açık bir RM'leri olmasa bile aşırı optimize ettiğini nasıl kanıtladığını açıklayın.

## Problem

RLHF amaç fonksiyonu (Ders 1):

```
max_pi E_{x,y~pi} [ r(x, y) ] - beta * KL(pi || pi_ref)
```

bilinen bir optimuma sahiptir:

```
pi*(y|x) = (1/Z(x)) * pi_ref(y|x) * exp(r(x, y) / beta)
```

Yani ödül, optimal politikanın referansa oranıyla örtük olarak tanımlanır:

```
r(x, y) = beta * log(pi*(y|x) / pi_ref(y|x)) + beta * log Z(x)
```

Bunu Bradley-Terry tercih olabilirliğine koyun ve bölüşüm fonksiyonu (partition function) `Z(x)` iptal olur, çünkü yalnızca `x`'e bağlıdır. Geriye yalnızca politika parametrelerinde bir kayıp kalır — ödül modeli gerekmez. İşte bu DPO'dur.

Buruktur: türetme, optimumun ulaşılabilir olduğunu, tercih verilerinin dağılım içi (in-distribution) olduğunu ve referans politikanın gerçek mod çapası (mode anchor) olduğunu varsayar. Hiçbiri tam olarak doğru değildir. Her aile üyesi farklı bir ihlal edilen varsayımı düzeltir.

## Kavram

### DPO (Rafailov ve diğerleri, 2023)

```
L_DPO = -log sigmoid(
 beta * log(pi(y_w | x) / pi_ref(y_w | x))
 - beta * log(pi(y_l | x) / pi_ref(y_l | x))
)
```

Ne yanlış gidebilir:

- Örtük ödül boşluğu `beta * (log(pi/pi_ref)_w - log(pi/pi_ref)_l)` sınırsızdır. Küçük bir tercih keyfi büyük bir boşluk üretebilir.
- Kayıp, seçilen ve reddedilen log-olasılıklarını ters yönlerde sürer. Reddedilen daha hızlı düştüğü sürece, seçilen mutlak log-olasılığını aşağı itebilir. Bu, Degrese Olmuş Seçilen Yanıt (Degraded Chosen Response) olgusudur.
- Dağılım dışı tercihler (nadir nadir çift vs nadir nadir çift) keyfi örtük ödüller üretir.

### IPO (Azar ve diğerleri, 2024)

Identity Preference Optimization, log-sigmoid'i tercih olasılığı üzerinde bir kimlik eşlemesiyle değiştirir. Kayıp, sınırlı bir hedef üzerinde karesel hata olur:

```
L_IPO = (log(pi(y_w | x) / pi_ref(y_w | x)) - log(pi(y_l | x) / pi_ref(y_l | x)) - 1/(2 beta))^2
```

Pay, `1/(2 beta)` ile sınırlıdır. Tercih gücü ve örtük ödül boşluğu orantılıdır. Patlama yok.

### KTO (Ethayarajh ve diğerleri, 2024)

Kahneman-Tversky Optimization, ikili yapıyı tamamen düşürür. Tek bir etiketli çıktı ve ikili "arzu edilir" veya "arzu edilmez" sinyali verildiğinde, onu bir prospect theory (beklenti teorisine) faydasına eşler:

```
v(x, y) = sigma(beta * log(pi(y|x) / pi_ref(y|x)) - z_ref)
```

kazançlar ve kayıplar için farklı ağırlıklarla (kayıptan kaçınma — loss aversion). Yarar: eşleştirilmemiş verileri kullanabilirsiniz, ki bu çok daha boldur.

### SimPO (Meng ve diğerleri, 2024)

Simple Preference Optimization, eğitim sinyalini üretimle hizalar. Referans politikayı tamamen kaldırın ve log-olabilirliği uzunluğa göre normalleştirin:

```
L_SimPO = -log sigmoid(
 (beta / |y_w|) * log pi(y_w | x)
 - (beta / |y_l|) * log pi(y_l | x)
 - gamma
)
```

kararlılık için bir `gamma` payı ile. Uzunluk normalleştirmesi, DPO'nun uzunluk yanlılığı başarısızlık modunu sömürme teşvikini ortadan kaldırır (daha uzun `y_w`, yapısı gereği daha büyük bir log-olasılık boşluğu verir).

### ORPO (Hong ve diğerleri, 2024)

Odds-Ratio Preference Optimization, standart SFT negatif log-olabilirliğine bir tercih terimi ekler:

```
L_ORPO = L_NLL(y_w) + lambda * L_OR
L_OR = -log sigmoid(log(odds(y_w) / odds(y_l)))
```

Referans politika yok — SFT terimi düzenlileştiricidir. Temel modelden hizalanmış modele tek aşamada eğitin. Ayrı bir SFT kontrol noktası yok.

### BPO (ICLR 2026 başvurusu, OpenReview id=b97EwMUWu7)

Degrese Olmuş Seçilen Yanıtlar (Degraded Chosen Responses) sorununu tanımlar: DPO, `y_w > y_l` sıralamasını korur, ancak `y_w`'nin mutlak log-olasılığı düşebilir. BPO, seçilen yanıt üzerindeki aşağı yönlü hareketleri cezalandıran tek satırlık bir düzeltme ekler. Llama-3.1-8B-Instruct üzerinde DPO'ya göre matematiksel akıl yürütmede +%10.1 doğruluk bildirilmiştir.

### Evrensel sonuç: DAA'lar hâlâ aşırı optimize eder

Rafailov ve diğerlerinin "Scaling Laws for Reward Model Overoptimization in Direct Alignment Algorithms" (NeurIPS 2024) çalışması, DPO, IPO, SLiC ile birden fazla veri kümesi üzerinde politikaları KL bütçeleri boyunca eğitti. Altın-ödül-vs-KL eğrileri aynı Gao ve diğerleri zirve-ve-çöküş şekline sahiptir. Örtük ödül, eğitim sırasında dağılım dışı örnekleri sorgular; KL düzenlileştirmesi bunu stabilize etmez.

DAA'lar Goodhart'tan kaçmaz. Isırdığı yüzeyi "ödül modeli aşırı optimize edildi"nden "referans politika oranı aşırı optimize edildi"ne değiştirir. Evrensel düzeltme — daha iyi veri, topluluklar, erken durdurma — ikisine de uygulanır.

### 2026'da aralarında seçim yapmak

- Büyük eşleştirilmiş tercih veriniz varsa: muhafazakâr beta ile DPO, uzunluk yanlılığı belirginse SimPO.
- Eşleştirilmemiş ikili geri bildiriminiz varsa: KTO.
- Temel modelden tek aşamalı bir boru hattı istiyorsanız: ORPO.
- DPO loglarında degrese olmuş seçilen log-olasılıkları görüyorsanız: BPO.
- Tercih güçleri geniş ölçüde değişiyorsa ve DPO doyuyorsa: IPO.

Her laboratuvar beşini de bir bataryada çalıştırır ve göreve göre kazananı seçer. Optimumun matematik akıl yürütme ve güvenlik için aynı olması için bir neden yoktur.

## Kullan

`code/main.py`, altı kaybı (DPO, IPO, KTO, SimPO, ORPO, BPO) oyuncak bir tercih veri kümesi üzerinde karşılaştırır; burada gerçek tercih gücü çifte göre değişir. Her kayıp, aynı 500 çiftlik örneklem üzerinde küçük bir softmax politikasına karşı optimize edilir. Yöntem başına son kazanma oranını, seçilen-log-olasılık kaymasını ve örtük ödül yayılımını çizdirir.

## Yayınla

Bu ders `outputs/skill-preference-loss-selector.md` dosyasını üretir. Veri kümesi istatistikleri (eşleştirilmiş vs eşleştirilmemiş, değişken vs tekdüze tercih gücü, uzunluk dağılımı) ve bir hedef (tek aşamalı veya SFT-sonra-tercih) verildiğinde, bir tercih kaybı önerir ve koruduğu başarısızlık modunu rapor eder.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. DPO ve BPO için son seçilen-log-olasılık düşüşünü rapor edin. BPO, daha yüksek seçilen mutlak olasılığı korumalıdır — bunu doğrulayın.

2. Tercih verilerini, tüm çiftlerin eşit güce sahip olacağı şekilde değiştirin. Altı yöntemden hangisi en sağlam? Hangisi bozulur? Burada IPO'nun avantajını açıklayın.

3. Reddedilen yanıtları ortalama olarak seçilenlerden 2x daha uzun yapın. Başka hiçbir şeyi değiştirmeden, DPO'nun uzunluk sömürüsünü ve SimPO'nun düzeltmesini sayısal olarak gösterin.

4. Rafailov ve diğerleri (NeurIPS 2024) DAA'ların aşırı optimize ettiğini iddia eder. Tek-nokta bir versiyonu yeniden üretin: seçilen-eksi-reddedilen KL diverjansını çizdirin ve büyük beta'da DPO'da aşırı optimizasyonu gözlemleyin.

5. BPO makale özetini (OpenReview b97EwMUWu7) okuyun. BPO'nun DPO'ya eklediği tek satırlık düzeltmeyi yazın. `code/main.py`'deki uygulamaya karşı doğrulayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|----------------------|---------------------------|
| DPO | "ödül modeli olmadan RLHF" | RLHF optimumunun kapalı formundan türetilmiş kayıp; yalnızca politika parametreleri |
| Örtük ödül | "log-oranı" | `beta * log(pi(y\|x) / pi_ref(y\|x))` — DPO'nun ima ettiği ödül |
| IPO | "sınırlı DPO" | Log-sigmoid'i kimlikle değiştirir; örtük ödül boşluğu `1/(2 beta)` ile sınırlıdır |
| KTO | "eşleştirilmemiş DPO" | Kayıptan kaçınma ile tek etiketler üzerinde prospect theory faydası |
| SimPO | "referanssız DPO" | Uzunluk normalleştirilmiş log-olabilirlik + pay; referans politika yok |
| ORPO | "tek aşamalı DPO" | NLL + odds-ratio tercih terimi; temel modelden tek geçişte eğitir |
| BPO | "seçileni koruyan DPO" | DPO'ya seçilen yanıtın mutlak log-olasılığını düşürmek için bir ceza |
| Degrese Olmuş Seçilen | "seçilen aşağı gider" | DPO, reddedilen daha hızlı düştüğü sürece seçilen log-olasılığını azaltır |
| DAA | "doğrudan hizalama algoritması" | Açık bir RM'yi atlayan herhangi bir tercih kaybı yöntemi |

## İleri Okuma

- [Rafailov ve diğerleri — Direct Preference Optimization (NeurIPS 2023, arXiv:2305.18290)](https://arxiv.org/abs/2305.18290)
- [Azar ve diğerleri — A General Theoretical Paradigm to Understand Learning from Human Preferences (AISTATS 2024, arXiv:2310.12036)](https://arxiv.org/abs/2310.12036) — IPO
- [Ethayarajh ve diğerleri — KTO: Model Alignment as Prospect Theoretic Optimization (arXiv:2402.01306)](https://arxiv.org/abs/2402.01306)
- [Meng, Xia, Chen — SimPO (NeurIPS 2024, arXiv:2405.14734)](https://arxiv.org/abs/2405.14734)
- [Hong, Lee, Thorne — ORPO (EMNLP 2024, arXiv:2403.07691)](https://arxiv.org/abs/2403.07691)
- [BPO — Behavior Preservation Optimization (ICLR 2026 OpenReview b97EwMUWu7)](https://openreview.net/forum?id=b97EwMUWu7)
- [Rafailov ve diğerleri — Scaling Laws for RM Overoptimization in DAAs (NeurIPS 2024, arXiv:2406.02900)](https://arxiv.org/abs/2406.02900)
