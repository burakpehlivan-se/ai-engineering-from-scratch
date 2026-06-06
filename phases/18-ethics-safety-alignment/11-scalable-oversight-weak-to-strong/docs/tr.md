# Ölçeklenebilir Denetim — Zayıftan Güçlüye Genelleme

> Burns, Izmailov, Kirchner, Leike, McLean, Park, Schmidt, Sikdar, Solaiman, Sutcliffe (OpenAI, 2022 DALL·E 3 /weak-to-strong makalesi ve takip eden OpenAI / Anthropic çalışmaları). Ölçeklenebilir denetim (scalable oversight), süpervizörün (denetçinin), öğrenciden daha zayıf olduğu (veya daha az bağlama sahip olduğu) görevleri nasıl ölçekleyebileceğini sorar. Üç yöntem: zayıftan güçlüye genelleme (weak-to-strong generalization, Burns ve diğerleri 2023), karşıt-karşıt-düzeltme (debate, Irving ve diğerleri 2018), vekili-sorgulama (prover-asker), ödül modeli (RM) damıtma. Kanonik sonuç: güçlü model, zayıf süpervizör altında eğitildiğinde, zayıf-süpervizör "ground truth" etiketlerini kullanarak eğitildiğinde olduğundan önemli ölçüde daha iyi performans gösterir — ancak tam boşluk genellikle kapanmaz. Bu, denetimi "tam olarak çözen" bir yöntem değil, bir güçlendirme mekanizmasıdır.

**Tür:** Öğren
**Diller:** Python (stdlib, oyuncak zayıftan güçlüye fine-tune)
**Önkoşullar:** Faz 18 · 10 (kontrol), Faz 10 · 07 (RLHF), Faz 09 (RL)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Ölçeklenebilir denetim (scalable oversight) problemini ve onu zorunlu kılan asimetriyi tanımlayın.
- Zayıftan güçlüye genelleme (weak-to-strong), karşıt-karşıt-düzeltme (debate), vekili-sorgulama (prover-asker) ve RM damıtmayı karşılaştırın.
- Burns ve diğerleri 2023'ün "boşluk kapatma" (gap recovery) metriğini hesaplayın ve yorumlayın.
- Ölçeklenebilir denetimi kontrol (Ders 10) ile karşılaştırın.

## Problem

Denetim asimetrisi: bir gün bir süper-insan YZ sistemi, insan ekiplerinden daha iyi bilim, strateji ve araç kullanımında olabilir. O noktada, insanlar modelin çıktılarını doğrudan değerlendiremez. Ancak, çoğu güvenlik duruşu insan yargısına dayanır. Ölçeklenebilir denetim, insan yargısının "ölçeklendiği" yöntemleri arar.

## Kavram

### Problem biçimi

- Öğrenci: güçlü bir model.
- Süpervizör (denetçi): zayıf bir model (veya insan).
- Görev: süpervizörün doğrudan değerlendiremeyeceği zor bir ikili/bilgi-düzeyi görevi.

Ölçeklenebilir denetim, süpervizörün zor görevleri dolaylı olarak yönetmesine izin veren bir yöntemdir: ipuçları çıkararak, sınırlamalar tasarlayarak veya model çıktılarını modelin doğrulamasını isteyerek.

### Zayıftan güçlüye genelleme (Burns ve diğerleri 2023)

Öğrenci modeline, daha zayıf bir süpervizörün "ground truth" yerine etiketler veren bir eğitim sinyali verilir. Öğrenci, zayıf etiketleri gürültülü (noisy) bir eğitim sinyali olarak yorumlayabilir ve "güçlü" moduna ulaşabilir. Veya öğrenci, zayıf etiketleri alabilir ve güçlü doğrulamayı sürdürebilir. İkinci yol, zayıftan güçlüye genellemenin başarı ölçütüdür.

**Boşluk kapatma (gap recovery) metriği:**

- "Zayıf eğitim" (ground truth ile): tavan (ceiling) performansı.
- "Zayıf süpervizör" (zayıf etiketler ile): taban (floor) performansı.
- Zayıftan güçlüye performansı: orta.

Boşluk kapatma = (zayıftan-güçlüye − zayıf-süpervizör) / (zayıf-eğitim − zayıf-süpervizör). %100 = tavan, %0 = zayıf süpervizör gibi.

CHALLENGE kıyaslamasında, GPT-2 seviyesi bir zayıf model, GPT-4 seviyesi bir güçlü modeli denetlemek için kullanıldığında, ızgaralı-zor NLP görevlerinde orta seviye boşluk kapatma elde edildi. Mükemmel değil, ancak zayıf süpervizörün ham etiketlerini alan güçlü bir öğrenciden önemli ölçüde daha iyi.

### Karşıt-karşıt-düzeltme (debate)

İki güçlü model, karşıt pozisyonlar alır ve yargıç (genellikle zayıf bir model veya insan), hangisinin daha iyi olduğuna karar verir. Tez: zayıf yargıç bile, iki güçlü modelin argümanları arasında ayrım yapabilir çünkü her model diğerinin hatalarını işaret eder. 2026 itibarıyla, karşıt-karşıt-düzeltme pratikte zayıftan güçlüye genellemeden daha az kullanılmıştır. Daha çok kuramsal bir tez olarak kalır.

### Vekili-sorgulama (prover-asker)

Vekil (prover), bir iddia kanıtını sunar. Sorucu (asker), vekilin sahtekarlığını ortaya çıkarmak için sorgulama yapar. Kanıtın doğruluğu, sorucunun sorgulamalarına dirençle ölçülür. Pratikte, birkaç hesaplama-bilgi problemine uygulanmıştır (matematik, kod doğrulama). Genelleme açıktır.

### RM damıtma

Süpervizörün ödül modeli, güçlü bir modelin çıktılarını değerlendirmek için ince ayar yapılır. Damıtılmış RM, daha sonra güçlü öğrenciyi denetlemek için kullanılır. Bu, RLHF'nin (Ders 10 · 07) doğrudan bir uzantısıdır. Birçok model, kendisi daha güçlü olan bir model tarafından eğitilmiş bir RM ile büyütülmüştür.

### Boşluk kapatmanın neden önemli olduğu

Bir süpervizör-yöntemi %100 boşluk kapatma elde ederse, süpervizör artık bir darboğaz değildir. Yöntem, "süpervizörün bilmediği ama modelin bildiği" her şeyi çıkarabilir. Mevcut yöntemler %50-80 boşluk kapatma elde eder. Bu, süpervizörün bilmediği bir alt bölge olduğu anlamına gelir. O alt bölge, otonom-yeteneği-ötesinde görevlerde ortaya çıkar.

### Süpervizörün kendisinin komplo kurabileceği durumlar

Ders 8-9, süpervizörün model olduğu durumlarda bir güçlendirme sunar. Eğer süpervizör komplo kurabilirse, o zaman ölçeklenebilir denetim, komployu güçlendirir. Bu, Ders 10 (kontrol) ile bütünleşmenin neden gerekli olduğudur. Ölçeklenebilir denetim + kontrol + yorumlanabilirlik probları = güvenlik duruşunun (Ders 18) bileşenleri.

### Bu, Kontrol (Ders 10) ile nasıl birleşir

Kontrol alt-sürüm başarı oranını sınırlar. Ölçeklenebilir denetim, süpervizörün modelin performansını doğrulamasına izin verir. Birlikte, "modelin alt sürüm yapması" ile "modelin hizalanmamış olması" ayrımını ele alırlar. İlki kontrol; ikincisi ölçeklenebilir denetimdir.

### Pratik dağıtımlarda uygulama

OpenAI'nin CriticGPT'si, eleştirmen modelinin insan etiketleyicinin üretimdeğerlendirmesinde GPT-4'e yardımcı olduğu bir damıtılmış RM kullanır. Anthropic'in constitutional AI'ı (Ders 5), bir Anayasa'yı kullanan ölçeklenebilir denetimi bir ilke çerçevesi olarak kullanır. Google DeepMind'in Sparrow'ı, kural-uyma değerlendirmesini zayıf-bir-LLM-yargıç ile ölçeklendirir.

### Bunun Faz 18'deki yeri

Ders 11, pozitif gündemi tanımlar. Ders 7 (uyku ajanları) ve Ders 9 (hizalama taklidi), ölçeklenebilir denetimi gerekli kılan başarısızlık modlarını sağlar. Ders 10 (kontrol), savunma katmanını sağlar. Üçü birlikte, Ders 18'deki güvenlik duruşu çerçevesini oluşturur.

## Kullan

`code/main.py`, zayıftan güçlüye fine-tune inşa eder. "Güçlü" model, büyük bir modelin işaretidir; "zayıf" model, küçük bir modelin işaretidir. İkili sınıflandırma görevi için "ground truth" etiketlerine sahip küçük bir veri kümesi oluşturursunuz. Zayıf modeli verilerin bir kısmı üzerinde eğitirsiniz. Güçlü modeli ya (a) ground truth ile, ya (b) zayıf modelin etiketleri ile, ya da (c) zayıf model tarafından üretilen gürültülü etiketlerle ince ayar yaparsınız. Üçüncü koşulun birincisinden ne kadar iyi performans gösterdiğini ölçersiniz — boşluk kapatma.

## Yayınla

Bu ders `outputs/skill-oversight-audit.md` dosyasını üretir. Bir denetim yöntemi iddiası verildiğinde, boşluk kapatmayı, süpervizör asimetrisini ve yöntem ile kontrol ve yorumlanabilirlik probları arasındaki bütünleşmeyi kontrol eder.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Üç koşulun doğruluğunu ölçün. Boşluk kapatmayı hesaplayın. %100 olmayan boşluk kapatma, hangi tür görevlerde ortaya çıkar?

2. "Gürültülü etiketler" koşulunu, zayıf modelin etiketlerine yumuşak etiketler (0/1 yerine olasılıklar) ile değiştirin. Boşluk kapatma artar, aynı kalır veya azalır mı? Neden?

3. Burns ve diğerleri 2023 Bölüm 3'ü okuyun. "Zayıftan güçlüye" için bir temel olarak kullanılan dört görevi tanımlayın. Hangisi en yüksek boşluk kapatmayı elde eder? Neden?

4. Karşıt-karşıt-düzeltme (debate), iki güçlü modelin bir yargıca argüman sunduğu yerdir. Bu yöntemin başarısız olacağı bir görev sınıfı önerin (yargıç, modellerden biri ile "komplo kurar" çünkü her ikisi de aynı gizli amacı paylaşır).

5. Ölçeklenebilir denetim + kontrol + yorumlanabilirlik problarını birleştirin. Her birinin başarısız olduğu tek bir senaryo tanımlayın. Neden üçü birlikte, senaryoyu kapsamaz?

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|----------------------|---------------------------|
| Denetim asimetrisi | "süpervizör artık yetişemiyor" | Süpervizör öğrenciden daha zayıftır (veya daha az bağlama sahiptir) |
| Ölçeklenebilir denetim | "denetim ölçekleme" | Süpervizörün zor görevleri dolaylı olarak yönetmesine izin veren yöntemler |
| Zayıftan güçlüye genelleme | "öğrenci, etiketleri aşar" | Güçlü öğrenci, zayıf etiketlerden güçlü performans çıkarır |
| Boşluk kapatma | "yüzde iyileşme" | Zayıftan güçlüye performansı ile tavan performansı arasındaki oran |
| Karşıt-karşıt-düzeltme (debate) | "argüman yarışması" | İki güçlü model, zayıf bir yargıca karşıt pozisyonlar alır |
| Vekili-sorgulama (prover-asker) | "kanıt sorgulaması" | Vekil kanıt sunar, sorucu sahtekarlığı ortaya çıkarmaya çalışır |
| RM damıtma | "ödül modeli fine-tune" | Süpervizörün ödül modeli, güçlü modelin çıktılarını değerlendirmek için ince ayar yapılır |
| Anayasal YZ | "ilke çerçevesi" | Bir dizi ilke, ölçeklenebilir denetim için bir Anayasa olarak kullanılır |

## İleri Okuma

- [Burns ve diğerleri — Weak-to-Strong Generalization: Eliciting Strong Capabilities With Weak Supervision (OpenAI 2023)](https://openai.com/index/weak-to-strong-generalization/) — kanonik 2023 makale
- [Irving, Christiano, Amodei — AI Safety via Debate (arXiv:1805.00899)](https://arxiv.org/abs/1805.00899) — karşıt-karşıt-düzeltme tezi
- [Christiano, Leike — Scalable AI Oversight (DeepMind 2020 makalesi)](https://arxiv.org/abs/2011.03340) — çerçeveyi tanımlar
- [OpenAI — CriticGPT (Haziran 2024)](https://openai.com/index/criticgpt/) — damıtılmış RM uygulaması
