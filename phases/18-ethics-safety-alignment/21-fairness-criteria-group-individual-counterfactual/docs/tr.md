# Adalet Kriterleri — Grup, Bireysel, Karşı-olgusal

> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/18-ethics-safety-alignment/21-fairness-criteria-group-individual-counterfactual/docs/en.md)

> Üç aile adalet literatürünü yapılandırır. Grup adaleti: demografik parite, eşitlenmiş odds (equalized odds), koşullu kullanım doğruluğu eşitliği — korunan gruplar arasında ortalama olarak eşit oranlar. Bireysel adalet (Dwork ve ark. 2012): benzer bireyler benzer kararlar alır; karar haritası üzerinde Lipschitz koşulu. Karşı-olgusal adalet (Kusner ve ark. 2017): bir karar, hassas öznitelikler karşı-olgusal olarak değiştirildiğinde değişmezse, birey için adildir. 2024 teorik sonuç (NeurIPS 2024): doğuştan bir CF-vs-doğruluk takası vardır; modelden-bağımsız bir yöntem, optimal-ama-adaletsiz bir tahmin ediciyi sınırlı doğruluk kaybıyla CF bir tahmin ediciye dönüştürür. Geri-izleme karşı-olgusalları (arXiv:2401.13935, Ocak 2024): yasal olarak korunan öznitelikler üzerinde müdahale gerektirmeyen yeni paradigma. Felsefi uzlaşma (ICLR Blogposts 2024): nedensel grafiklerle, belirli grup adaleti ölçülerini karşılamak karşı-olgusal adaleti gerektirir.

**Tür:** Öğren
**Diller:** Python (stdlib, üç-kriter karşılaştırması)
**Ön Koşullar:** Faz 18 · 20 (önyargı), Faz 02 (klasik ML)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Üç grup adaleti kriterini (demografik parite, eşitlenmiş odds, koşullu kullanım doğruluğu eşitliği) ve bir imkansızlık sonucunu belirtin.
- Bireysel adaleti Dwork ve ark. 2012 Lipschitz formülasyonu yoluyla açıklayın.
- Karşı-olgusal adaleti ve onun nedensel-grafik bağımlılığını açıklayın.
- Geri-izleme karşı-olgusallarını ve bunların korunan-özellik üzerinde müdahale problemini neden dolandığını açıklayın.

## Sorun

Ders 20, önyargıyı ölçmekle ilgiliydi. Ders 21, ölçümün hizmet etmesi gereken adalet standardını tanımlamakla ilgili. Üç aile yapısal olarak farklı standartlar verir — bir model grup-adil ve bireysel-adaletsiz, karşı-olgusal olarak adil ve grup-adaletsiz olabilir. Bir standart seçmek bir politika kararıdır; evrensel olarak optimal standart yoktur.

## Kavram

### Grup adaleti

- **Demografik parite.** P(Y=1 | A=a) = P(Y=1 | A=a') tüm gruplar için. Eşit kabul oranları.
- **Eşitlenmiş odds.** P(Y=1 | Y*=y, A=a) = P(Y=1 | Y*=y, A=a'). TPR ve FPR gruplar arasında eşit.
- **Koşullu kullanım doğruluğu eşitliği.** P(Y*=y | Y=y, A=a) = P(Y*=y | Y=y, A=a'). Tahmin değerleri gruplar arasında eşit.

İmkansızlık (Chouldechova, Kleinberg-Mullainathan-Raghavan 2017): bu üçü, eşit olmayan temel oranlar altında aynı anda karşılanamaz.

### Bireysel adalet

Dwork ve ark. 2012. f karar haritası, göreve özgü bir benzerlik metriği d'ye göre, |f(x) - f(x')| <= L * d(x, x') bazı Lipschitz sabiti L için bireysel olarak adildir. Benzer bireyler benzer kararlar alır.

d tanımlamayı gerektirir. İstatistiksel değil, politika sorusu.

### Karşı-olgusal adalet

Kusner ve ark. 2017. Karar, popülasyonun nedensel modeli altında, birey i'nin hassas öznitelikleri karşı-olgusal olarak değiştirildiğinde değişmezse, birey i için karşı-olgusal olarak adildir.

Nedensel DAG gerektirir. DAG bir modelleme seçimidir. Karşı-olgusal adalet yalnızca DAG kadar haklıdır.

### CF-vs-doğruluk takası

NeurIPS 2024 teorik: karşı-olgusal adalet ile tahmin doğruluğu arasında doğuştan bir takas vardır. Modelden-bağımsız bir yöntem, optimal-ama-adaletsiz bir tahmin ediciyi sınırlı doğruluk maliyetiyle CF bir tahmin ediciye dönüştürebilir. Doğruluk maliyeti, optimal adaletsiz tahmin edicideki hassas-özellik katsayısının büyüklüğüne bağlıdır.

### Geri-izleme karşı-olgusalları

arXiv:2401.13935 (Ocak 2024). Geleneksel karşı-olgusallar, hassas öznitelik üzerinde müdahale gerektirir — "bu kişi farklı bir cinsiyette olsaydı karar değişir miydi?" Yasal olarak, bu sorunludur: korunan öznitelikler sınıflandırma yasasında müdahale edilemez.

Geri-izleme karşı-olgusalları yönü tersine çevirir: öznitelik üzerinde müdahale etmek yerine, bireyin gerçek özniteliklerinin hangi kombinasyonunun karşı-olgusal sonucu üreteceğini sorar. Bu yasal itirazı dolanır.

### Felsefi uzlaşma

ICLR Blogposts 2024. Elinizde bir nedensel grafik olduğunda, belirli grup adaleti ölçülerini karşılamak karşı-olgusal adaleti gerektirir. Üç aile dik değildir; aynı temel nedensel yapının farklı yüzleridir.

Bu, imkansızlık teoremlerini çözmez (eşit olmayan temel oranlar yine de eşzamanlı grup adaletini engeller). Ancak "grup" ile "bireysel / karşı-olgusal" arasındaki görünür muhalefetin kısmen nedensel modeli açıkça belirtmemenin bir eseri olduğunu gösterir.

### Bu, Faz 18'de nereye oturuyor

Ders 20, önyargı ölçümüdür. Ders 21, adalet tanımıdır. Ders 22, gizliliktir (farklı gizlilik). Ders 23, filigranlamedir. Bunlar, Dersler 7-11'in aldatma-bitşık derslerini tamamlayan dağıtım-bitşık derslerdir.

## Uygulama

`code/main.py` hassas bir öznitelik ve eşit olmayan temel oranlara sahip bir oyuncak ikili-sınıflandırma veri kümesi inşa eder. Basit bir sınıflandırıcı üzerinde demografik parite, eşitlenmiş odds ve koşullu kullanım doğruluğu eşitliğini hesaplayın. Üç ölçünün anlaşmazlığını gözlemleyin. Demografik parite için bir yeniden-ağırlıklandırma uygulayın ve diğer ikisi üzerindeki maliyetini gözlemleyin.

## Ship It

Bu ders `outputs/skill-fairness-criterion.md` üretir. Bir adalet iddiası veya politikası verildiğinde, hangi kriterin iddia edildiğini, modelin iddia edilen eşit olmayan temel oranlar altında kalan kriterleri karşılayıp karşılayamayacağını ve iddianın bağlı olduğu nedensel DAG'ı tanımlar.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Varsayılan veride üç grup ölçüsünü raporlayın. Demografik-parite-hedefli yeniden-ağırlıklandırmayı uygulayın ve yeniden raporlayın.

2. Dwork ve ark. 2012 bireysel-adalet ölçüsünü, hassas-olmayan öznitelikler üzerinde L2 kullanarak uygulayın. L=1 sabitiyle kaç çiftin Lipschitz'i ihlal ettiğini raporlayın.

3. Kusner ve ark. 2017'i okuyun. Özgeçmiş puanlama için basit iki-özellikli bir nedensel DAG inşa edin ve onun ima ettiği karşı-olgusal-adalet koşulunu tanımlayın.

4. 2024 geri-izleme-karşı-olgusalları makalesi, korunan öznitelikler üzerinde müdahaleyi önler. Bunun yasal uyumluluk için önemli olduğu bir senaryo açıklayın.

5. ICLR 2024 uzlaşması, grup ve karşı-olgusal adaletin aynı yapının yüzleri olduğunu savunur. `code/main.py`'deki üç kriterden ikisini seçin ve onları eşdeğer kılacak nedensel varsayımı belirtin.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|---------------------|---------------|
| Demografik parite | "eşit oranlar" | P(Y=1 | A=a) gruplar arasında eşit |
| Eşitlenmiş odds | "eşit TPR/FPR" | Gerçek-pozitif ve yanlış-pozitif oranları gruplar arasında eşit |
| Koşullu kullanım doğruluğu | "eşit PPV/NPV" | Tahmin değerleri gruplar arasında eşit |
| Bireysel adalet | "Lipschitz koşulu" | Benzer bireyler benzer kararlar alır |
| Karşı-olgusal adalet | "nedensel değişiklik değişmezliği" | Karşı-olgusal öznitelik değişikliği altında karar değişmez |
| Geri-izleme karşı-olgusalı | "gerçekler yoluyla açıkla" | Sonuçtan ileriye değil, öznitelikten geriye doğru muhakeme edilen karşı-olgusal |
| İmkansızlık teoremi | "üçü çatışır" | Chouldechova / KMR 2017: eşit olmayan temel oranlar altında grup kriterleri karşılıklı dışlayıcı |

## İleri Okuma

- [Dwork ve ark. — Fairness through Awareness (arXiv:1104.3913)](https://arxiv.org/abs/1104.3913) — bireysel adalet
- [Kusner, Loftus, Russell, Silva — Counterfactual Fairness (arXiv:1703.06856)](https://arxiv.org/abs/1703.06856) — karşı-olgusal adalet
- [Chouldechova — Fair prediction with disparate impact (arXiv:1703.00056)](https://arxiv.org/abs/1703.00056) — imkansızlık
- [Backtracking Counterfactuals (arXiv:2401.13935)](https://arxiv.org/abs/2401.13935) — korunan-özellik müdahaleleri için yeni paradigma
