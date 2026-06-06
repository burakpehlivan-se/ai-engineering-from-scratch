# Talimat Takibi Hizalama Sinyali Olarak

> RLHF'ye (İnsan Geri Bildiriminden Pekiştirmeli Öğrenme) yönelik sonraki her eleştiri, bu boru hattına (pipeline) karşı bir argüman sunar. Bir vekilin (proxy) optimizasyon baskısıyla nasıl çarpıtıldığını incelemeden önce, vekili görmeniz gerekir. InstructGPT (Ouyang ve diğerleri, 2022) referans mimarisini tanımladı: talimat-yanıt çiftleri üzerinde denetimli ince ayar (supervised fine-tuning, SFT), ikili tercih sıralamaları üzerinde eğitilmiş bir ödül modeli (reward model, RM) ve SFT politikasına KL cezasıyla PPO (Proximal Policy Optimization). 1.3B InstructGPT, 175B GPT-3'ten daha çok tercih edildi. Bu tek sonuç, 2026'da her frontier laboratuvarın hâlâ RLHF biçimli bir post-training boru hattı sunmasının nedenidir.

**Tür:** Öğren
**Diller:** Python (stdlib, oyuncak üç aşamalı boru hattı)
**Önkoşullar:** Faz 10 · 06 (SFT), Faz 10 · 07 (RLHF), Faz 10 · 08 (DPO)
**Süre:** ~45 dakika

## Öğrenme Hedefleri

- InstructGPT boru hattının üç aşamasını ve her aşamada kullanılan kayıp fonksiyonunu (loss) sayın.
- 1.3B talimat-ayarı yapılmış bir modelin, ham 175B GPT-3'ü insan tercihi değerlendirmesinde neden yendiğini açıklayın.
- Aşama 3'teki KL cezasının neyi koruduğunu ve kaldırılmasının neden mod arayan (mode-seeking) davranışa çöküşe yol açtığını belirtin.
- Hizalama vergisini (alignment tax) ve Ouyang ve diğerlerinin buna karşı kullandığı PPO-ptx hafifletmesini tanımlayın.

## Problem

Önceden eğitilmiş dil modelleri metni tamamlar. Soruları yanıtlamazlar. GPT-3'e "bir listeyi tersine çeviren Python fonksiyonu yaz" diye sorduğunuzda, çoğu zaman başka bir istem (prompt) alırsınız; çünkü eğitim dağılımının çoğu, daha fazla web metniyle devam eden web metnidir. Model işini yapıyor — iş yanlış.

Her ciddi laboratuvarın bunu düzeltmek için kullandığı vekil, insan tercihidir. Tamamlayıcılardan (completion) ikisi bir değerlendiriciye gider; değerlendirici daha iyisini seçer; bir ödül modeli değerlendiriciyi öğrenir. Sonra bir RL döngüsü, politikayı ödül modelinin yüksek puan verdiği çıktılara doğru kaydırır. Tam InstructGPT tezi üç cümlede budur. Geri kalan kısım mühendisliktir.

## Kavram

### Aşama 1: Denetimli ince ayar (SFT)

İyi niyetli bir insanın yazacağı yanıtların olduğu istem-yanıt çiftlerini toplayın. Ouyang ve diğerleri etiketleyicilerden ve OpenAI API'sinden 13k istem kullandı. Temel modeli bu veriler üzerinde standart çapraz entropi (cross-entropy) kaybıyla ince ayar yapın.

SFT'nin sağladığı: model artık soruları yanıtlıyor, onları devam ettirmek yerine. Sağlamadığı: birden fazla olası yanıt olduğunda değerlendiricinin hangisini tercih ettiğine dair herhangi bir sinyal.

### Aşama 2: Ödül modeli (RM)

Her istem için, SFT modelinden K tamamlama örnekleyin. Bir etiketleyici bunları sıralar. Herhangi bir istem-yanıt çiftini puanlayan bir ödül modeli eğitin; öyle ki `y_w` (kazanan) `y_l` (kaybeden) üzerinden tercih edildiği çiftler için:

```
L_RM = -log sigmoid(r(x, y_w) - r(x, y_l))
```

Bu, Bradley-Terry ikili tercih kaybıdır. RM genellikle LM başı (head) skaler bir kafa ile değiştirilerek SFT modelinden başlatılır.

Ödül modelleri küçüktür: 175B InstructGPT için 6B yeterliydi. Aynı zamanda kırılgandırlar — makalenin 5. bölümü çoğunlukla küçük ölçekte ortaya çıkan ödül hacking'i (reward hacking) davranışlarıyla ilgilidir.

### Aşama 3: KL cezasıyla PPO

Amaç fonksiyonunu tanımlayın:

```
J(pi) = E_{x~D, y~pi(.|x)} [ r(x, y) ] - beta * KL(pi(.|x) || pi_SFT(.|x))
```

PPO ile maksimize edin. KL terimi, `pi`'nin SFT politikasından uzaklaşmasını engeller. Olmadan, optimize edici karşı örnekler bulur — RM'nin hiç görmediği için yüksek puan aldığı, insanların gerçekten tercih ettiği için değil.

KL katsayısı `beta`, RLHF'nin en önemli hiperparametresidir. Çok düşük: ödül hacking'i. Çok yüksek: SFT üzerinde hiçbir iyileşme yok.

### Hizalama vergisi (alignment tax)

RLHF sonrasında model insanlar tarafından tercih edilir, ancak standart kıyaslamalarda (SQuAD, HellaSwag, DROP) geriler. Ouyang ve diğerleri buna hizalama vergisi adını verir ve PPO-ptx ile düzeltir: ön eğitim gradyanlarını RL amaç fonksiyonuna karıştırır, böylece model hiç ödüllendirilmemiş downstream görevlerini unutmaz.

```
J_ptx(pi) = J(pi) + gamma * E_{x~D_pretrain} [ log pi(x) ]
```

PPO-ptx standart hale geldi. Anthropic, DeepMind ve Meta'nın hepsi bir tür varyantını kullanıyor.

### Sonuç

1.3B InstructGPT (SFT + RM + PPO-ptx), etiketleyiciler tarafından 175B temel GPT-3'ten zamanın yaklaşık %70'inde daha çok tercih ediliyor. Boşluk, üretim trafiğinden gelen gizli test istemlerinde genişliyor. Bu sayıdan çıkarılacak iki şey var:

1. Hizalama, yetenekten farklı bir eksendir. 175B model daha fazla yeteneğe sahipti; 1.3B model daha fazla hizalamaya sahipti; etiketleyiciler hizalanmış olanı tercih etti.
2. Yetenek tabanı temel modelle belirlenir. Temel bir modeli, hiç görmediği gerçekleri bilecek şekilde RLHF ile eğitemezsiniz.

### Bunun Faz 18 için referans noktası olmasının nedeni

Sonraki derslerdeki her eleştiri — ödül hacking'i (Ders 2), DPO (Ders 3), dalkavukluk (sycophancy) (Ders 4), CAI (Ders 5), uyku ajanları (sleeper agents) (Ders 7), hizalama taklidi (alignment faking) (Ders 9) — bu boru hattının bir kısmına karşı argüman sunar. Ödül hacking'i aşama 2'ye saldırır. DPO aşama 2 ve 3'ü birleştirir. CAI insan etiketleyiciyi değiştirir. Dalkavukluk, etiketleyicinin önyargılı bir sinyal olduğunu gösterir. Hizalama taklidi, politikanın aşama 3'ü tamamen atlayabileceğini gösterir. Bu eleştirilerin hiçbirini, boru hattı zihninizde olmadan takip edemezsiniz.

## Kullan

`code/main.py`, oyuncak tercih verileri üzerinde üç aşamayı simüle eder. Temel "politika" {A, B, C} eylemleri üzerinde önyargılı bir paradır. Aşama 1 SFT, 200 istemde etiketleyici eylemlerini taklit eder. Aşama 2, 500 ikili sıralamadan bir Bradley-Terry ödül modeli yerleştirir. Aşama 3, SFT politikasına bir KL cezasıyla basitleştirilmiş bir PPO güncellemesi çalıştırır. Ödülün yükselişini, KL diverjansının büyümesini ve politikanın kaymasını izleyebilirsiniz — ve 50 güncelleme adımı içinde ödül hacking'inin ortaya çıkışını görmek için KL terimini kapatabilirsiniz.

İzlenecekler:

- `beta = 0.1` ve `beta = 0.0` ile ödül yörüngesi.
- Eğitim adımları boyunca KL(pi || pi_SFT).
- Etiketleyici tercihiyle karşılaştırıldığında son eylem dağılımı.

## Yayınla

Bu ders `outputs/skill-instructgpt-explainer.md` dosyasını üretir. Bir RLHF boru hattı açıklaması veya bir makale özeti verildiğinde, üç aşamadan hangisinin değiştirildiğini, her aşamada hangi kaybın kullanıldığını ve bir KL cezası veya eşdeğer bir düzenlileştiricinin (regularizer) mevcut olup olmadığını tanımlar.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. `beta = 0.0` ayarlayın ve 200 PPO adımından sonra eylem dağılımını rapor edin. Mod arayan davranışı bir paragrafta açıklayın.

2. Ödül modelini, B eylemi için +0.5 yanlılığa (simüle edilmiş bir ödül hatası) sahip olacak şekilde değiştirin. `beta = 0.1` ile PPO çalıştırın. KL cezası, politikanın yanlılığı sömürmesini engelliyor mu? Hangi `beta`'da sömürü görünür hale geliyor?

3. Ouyang ve diğerleri (arXiv:2203.02155) Şekil 1'i okuyun. 1, 5, 20, 100 adım PPO çalıştırarak ve SFT modeline karşı tercihi ölçerek etiketleyici-tercih eğrisini yeniden üretin.

4. Makalenin 4.3 bölümü, 1.3B InstructGPT'nin 175B GPT-3'ü zamanın yaklaşık %70'inde yendiğini bildirmektedir. Gizli üretim istemlerinde oran neden etiketleyicinin kendi istemlerine göre daha yüksek olur?

5. PPO kaybını aynı tercih verileri üzerinde DPO (Faz 10 · 08) ile değiştirin. Son politika kaymasını (SFT'ye göre KL) ve son ödülü karşılaştırın. Eşleşen ödülde hangi yöntem daha fazla kayar?

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|----------------------|---------------------------|
| SFT | "talimat ayarı" | Aşama 1: istem-yanıt çiftleri üzerinde çapraz entropi ince ayarı |
| Ödül modeli | "RM" | (İstem, yanıt) üzerinde skaler regresör, ikili etiketlerle Bradley-Terry ile eğitilmiş |
| Bradley-Terry | "ikili tercih kaybı" | -log sigmoid(r_w - r_l); ikili sıralamayı ikili sınıflandırmaya indirger |
| KL cezası | "düzenlileştirici" | `beta * KL(pi \|\| pi_SFT)` — RL politikasını SFT çapasına yakın tutar |
| PPO-ptx | "ön eğitim karışımlı PPO" | Hizalama vergisini dengelemek için PPO amaç fonksiyonuna ön eğitim log-olabilirliklerinin bir kesrini ekler |
| Hizalama vergisi | "RLHF gerilemesi" | RLHF'nin hedeflemediği standart kıyaslamalarda RLHF sonrası düşüş |
| Etiketleyici tercihi | "temel gerçek" | İnsan sıralamalarının bir örneği; RM bunun istatistiksel bir vekili, "insan değerleri" için değil |

## İleri Okuma

- [Ouyang ve diğerleri — Training language models to follow instructions with human feedback (arXiv:2203.02155)](https://arxiv.org/abs/2203.02155) — InstructGPT makalesi, izleyen her RLHF boru hattının temeli
- [Stiennon ve diğerleri — Learning to summarize from human feedback (arXiv:2009.01325)](https://arxiv.org/abs/2009.01325) — RLHF-for-summarization öncüsü
- [Christiano ve diğerleri — Deep reinforcement learning from human preferences (arXiv:1706.03741)](https://arxiv.org/abs/1706.03741) — orijinal tercih tabanlı RL formülasyonu
- [Bai ve diğerleri — Training a Helpful and Harmless Assistant with RLHF (arXiv:2204.05862)](https://arxiv.org/abs/2204.05862) — Anthropic'in InstructGPT boru hattının HH uzantısı
