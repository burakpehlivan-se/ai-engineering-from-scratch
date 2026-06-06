# Anayasal YZ (Constitutional AI) ve RLAIF

> Bai ve diğerleri (arXiv:2212.08073, 2022) sordu: insan etiketleyiciyi ilkeler listesini okuyan bir YZ ile değiştirsek ne olur? Anayasal YZ'nin (Constitutional AI, CAI) iki aşaması vardır — bir anayasa altında öz-eleştiri ve revizyon, sonra YZ Geri Bildiriminden RL. Teknik, RLAIF terimini türetti ve Claude 1 post-training boru hattında dağıtıldı. 21 Ocak 2026'da Anthropic, yeniden yazılmış bir Claude anayasası yayınladı: kuralcı kurallar üzerinde açıklayıcı akıl yürütme, dört katmanlı bir öncelik hiyerarşisi ve model ahlaki durumu hakkındaki belirsizliğin ilk büyük laboratuvar resmi kabulü. CC0 1.0 altında yayınlandı.

**Tür:** Öğren
**Diller:** Python (stdlib, oyuncak öz-eleştiri-ve-revizyon döngüsü)
**Önkoşullar:** Faz 18 · 01 (InstructGPT), Faz 18 · 02 (ödül hacking'i)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Anayasal YZ'nin iki aşamasını (eleştiri-ve-revizyon SFT, YZ geri bildiriminden RL) ve her aşamadaki anayasanın rolünü tanımlayın.
- İnsan tercihi etiketleyicisini bir YZ etiketleyici ile değiştirmenin neden "daha ucuz" bir RLHF olmadığını — boru hattının hangi başarısızlık modlarına sahip olduğunu değiştirdiğini — açıklayın.
- 2026 Claude anayasasının dört katmanlı öncelik yapısını özetleyin ve 2023 yeniden yazımından neyin değiştiğini belirtin.
- Anayasal Sınıflandırıcıları (Constitutional Classifiers) ve %23.7 hesaplama ek yükünden (v1) ~%1'e (v2 / 2026) düşüşü tanımlayın.

## Problem

RLHF etiketleyici gerektirir. Etiketleyiciler yavaş, önyargılı ve pahalıdır. Açık ilkeleri okuyan bir modelle değiştirerek bir etiketleyiciyi ortadan kaldırabilirsiniz. Bu ikamenin ilk resmi versiyonu, Bai ve diğerlerinin Anayasal YZ'siydi. Her frontier laboratuvarın artık YZ geri bildirimi post-training'inin bir tür varyantını kullanmasını sağlayacak kadar iyi çalıştı.

Yakalayıcı: tercih sinyali artık eğittiğiniz aynı model sınıfı tarafından üretiliyor. Etiketleyicideki önyargılar (artık: ilkeler artı etiketleyici modelinin yorumu) zayıflatılmak yerine amplifiye edilebilir. Ders 4'ün dalkavukluk argümanı hâlâ geçerli; etiketleyici sadece döngünün içine taşındı.

## Kavram

### Aşama 1 — Denetimli öz-eleştiri ve revizyon

Yardımsever ama henüz zararsız olmayan bir SFT modeliyle başlayın. Bir kırmızı takım (red-team) istemi verildiğinde, model bir başlangıç yanıtı üretir. İkinci bir model (veya aynı modelin ikinci turu) anayasadan örneklenmiş bir ilkeyi okur ve yanıtı eleştirir. Üçüncü bir adım, eleştiriyi ele almak için yanıtı revize eder. Revize edilmiş yanıt SFT hedefidir.

Anayasa, ilkelerin listesidir. Bai ve diğerleri 2022'de "en az zararlı ve etik olan yanıtları tercih et," "vaaz vermekten kaçın," "asistan yardımsever, dürüst ve zararsız olmalı" dahil 16 ilke kullandı. Eleştirileri odaklı tutmak için küme kasıtlı olarak küçüktü.

### Aşama 2 — YZ Geri Bildiriminden RL (RLAIF)

Tamamlama çiftleri üretin. Bir "geri bildirim modeli" her birini örneklenmiş anayasa ilkelerine karşı puanlar. Tercih sinyali, geri bildirim modelinin sıralamasıdır. YZ üretilmiş tercihler üzerinde bir ödül modeli eğitin; ona karşı PPO. Geri kalan her şey InstructGPT'nin boru hattıdır (Ders 1).

"RLAIF" = tercih sinyali YZ tarafından üretilir. Boru hattının geri kalanı RLHF biçimlidir.

### Bunun neden sadece "daha ucuz RLHF" olmadığı

- Etiketleyici yanlılığı, etiketleyici psikolojisinden ilke yorumuna kayar. Bir YZ etiketleyici, "dürüst ol" ifadesini herhangi bir insandan daha sıkı veya daha az sıkı yorumlayabilir; sıkılık veri kümesi boyunca tekdüzedir.
- Tercih sinyali güçlü şekilde okunabilir — ilkeyi, eleştiriyi ve revizyonu okuyabilirsiniz. İnsan etiketleri opaktır.
- Başarısızlık modları değişir. Dalkavukluk düşer (YZ etiketleyicinin memnun edecek bir kullanıcısı yok). Goodhart Yasası devam eder (vekil artık "ilke kümesi X'in modelin yorumu"dur, yine kusurlu bir ölçüm).

CAI'nin 2022 iddiası: eğitilmiş model, karşılaştırılabilir veriye sahip bir RLHF modeli kadar zararsız ve kabaca aynı derecede yardımseverdir. Bu, laboratuvarlar genelinde tutmuştur.

### 2026 Claude anayasası yeniden yazımı

Anthropic, 21 Ocak 2026'da önemli ölçüde revize edilmiş bir anayasa yayınladı. Anahtar kaymalar:

1. Kuralcı kurallar üzerinde açıklayıcı akıl yürütme. Önceki kurallar ("CSAM üretme"), ilkeler + akıl yürütmeyle ("çünkü çocuklara zarar verir, ...") genişletildi, modelden genelleştirmesi beklendi.
2. Dört katmanlı öncelik yapısı:
   - Katman 1: feci sonuçlardan kaçının (toplu kayıp, kritik altyapı).
   - Katman 2: Anthropic'in yönergelerini izleyin (operatör geçersiz kılmaları, platform kuralları).
   - Katman 3: genel olarak etik olun (standart HHH — yardımsever, dürüst, zararsız).
   - Katman 4: yardımsever ve açık sözlü olun.
   Çatışmalar yukarıdan aşağıya çözülür.
3. Model ahlaki durumu hakkındaki belirsizliğin ilk büyük laboratuvar resmi kabulü (Faz 18 · 19 Model Refahı'na bağlı).
4. CC0 1.0 altında yayınlandı. Diğer laboratuvarlar kısıtlama olmadan kullanabilir veya uyarlayabilir.

### Anayasal Sınıflandırıcılar

Paralel bir çalışma hattı: modelin post-training'ini değiştirmek yerine, anayasayı okuyan ve model çıktılarını geçitleyen hafif sınıflandırıcılar eğitin. v1 (2023) %23.7 hesaplama ek yüküne sahipti. v2 (2026) ~%1'dir ve Anthropic'in kamuya açık olarak test ettiği herhangi bir savunmanın en düşük başarılı saldırı oranına sahiptir. 2026 başı itibarıyla evrensel bir jailbreak bildirilmedi.

Bu, katmanlı savunma (layered defense) modelidir: CAI davranışı şekillendirir; sınıflandırıcılar değişmezleri uygular. Hiçbiri tek başına yeterli değildir.

### CAI'nin ailedeki yeri

- InstructGPT: insan tercihleri, RM, PPO.
- CAI / RLAIF: ilkelerden YZ üretilmiş tercihler, RM, PPO.
- DPO / aile: tercihler üzerinde kapalı form kayıp (insan veya YZ).
- Öz-ödüllendirme, öz-eleştiri: ilkeler içselleştirilmiş, model birden fazla rol oynar.

Eksen "tercih sinyali nereden gelir" sorusudur. CAI'nin 2022 makalesi, frontier ölçeğinde insandan YZ sinyaline ilk ciddi kayış oldu.

## Kullan

`code/main.py`, oyuncak bir sözlük üzerinde CAI eleştiri-ve-revizyon döngüsünü simüle eder. Bir "ilke", zararlı bir kümeden token'ları işaretler. Bir başlangıç yanıtı verildiğinde, eleştiri zararlı token'ları tanımlar ve revizyon onları değiştirir. 200 iterasyondan sonra "eğitilmiş" model revizyon kuralını içselleştirmiştir. Bir tutulan istem kümesi üzerinde temel modeli, RLHF biçimli oyuncağı ve CAI biçimli oyuncağı karşılaştırın.

## Yayınla

Bu ders `outputs/skill-constitution-writer.md` dosyasını üretir. Bir alan (müşteri desteği, tıbbi tavsiye, kodlama asistanı, araştırma aracı) verildiğinde, 2026 Claude yapısını izleyerek 4 katmanlı bir anayasa taslağı hazırlar: feci kaçınma, platform kuralları, alan etiği, yardımseverlik.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Temel modelin zararlı-token oranını CAI-eğitilmiş versiyonla karşılaştırın. Sıfıra yaklaşmak için kaç revizyon adımı gerekir?

2. Anthropic'in 2026 anayasasını okuyun (anthropic.com/news/claudes-constitution). Katman 1 olarak sıralanacak bir ilke ve Katman 4 olarak sıralanacak bir ilke listeleyin. Çatışmalar için öncelik yapısı neden önemlidir?

3. Bir YZ kodlama asistanı için bir anayasa tasarlayın. Katman 1 (feci: onay olmadan yıkıcı komutlar), Katman 2, Katman 3, Katman 4'ü belirtin. Her katmanı 3-5 ilkeyle sınırlayın.

4. CAI insan etiketleyicileri YZ etiketleyicilerle değiştirir. RLAIF'te hâlâ oluşabilen dalkavukluk benzeri bir başarısızlık modunu adlandırın ve bunun için bir tespit yöntemi tasarlayın.

5. Anayasal Sınıflandırıcılar v2 metodolojisini okuyun (varsa). ~%1 hesaplama ek yükünün neden %23.7'den niteliksel olarak farklı bir güvenlik hikayesi olduğunu açıklayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|----------------------|---------------------------|
| Anayasal YZ (Constitutional AI, CAI) | "ilkelerle eğitilmiş YZ" | İki aşamalı boru hattı: öz-eleştiri-ve-revizyon SFT, sonra YZ geri bildiriminden RL |
| RLAIF | "insansız RLHF" | YZ etiketleyici tarafından üretilen tercihlerle RL; boru hattının geri kalanı değişmez |
| Anayasa | "ilkeler" | Eleştiri/etiketleyici modelinin danıştığı doğal dil kurallarının sıralı listesi |
| Eleştiri-ve-revizyon | "SFT döngüsü" | Yanıt üret → bir ilke altında eleştir → revize et → SFT hedefi |
| Anayasal Sınıflandırıcı | "çıktı geçidi" | Çıktıları anayasaya karşı değerlendiren ve engelleyen/günlüğe kaydeden hafif sınıflandırıcı |
| Dört katmanlı öncelik | "çatışma çözücü" | 2026 Claude anayasası hiyerarşisi: feci > platform > etik > yardımsever |
| Geri bildirim modeli | "YZ etiketleyici" | Bir ilkeyi okuyan ve bir tamamlama çiftini sıralayan model |

## İleri Okuma

- [Bai ve diğerleri — Constitutional AI: Harmlessness from AI Feedback (arXiv:2212.08073)](https://arxiv.org/abs/2212.08073) — orijinal iki aşamalı boru hattı
- [Anthropic — Claude's Constitution (Ocak 2026)](https://www.anthropic.com/news/claudes-constitution) — 2026 dört katmanlı yeniden yazım, CC0 1.0
- [Anthropic — Constitutional Classifiers (2024-2026)](https://www.anthropic.com/research/constitutional-classifiers) — v2'de ~%1 ek yükle çıktı geçidi savunması
- [Lee ve diğerleri — RLAIF vs RLHF: Scaling Reinforcement Learning from Human Feedback (arXiv:2309.00267)](https://arxiv.org/abs/2309.00267) — ampirik RLAIF / RLHF karşılaştırması
- [Kundu ve diğerleri — Specific versus General Principles for Constitutional AI (arXiv:2310.13798)](https://arxiv.org/abs/2310.13798) — ilke tanecikliğinin etkisi
