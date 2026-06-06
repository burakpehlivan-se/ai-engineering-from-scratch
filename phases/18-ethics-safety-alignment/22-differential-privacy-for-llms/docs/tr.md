# LLM'ler için Diferansiyel Gizlilik

> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/18-ethics-safety-alignment/22-differential-privacy-for-llms/docs/en.md)

> DP-SGD standart olmaya devam ediyor — gürültü-enjekte edilmiş gradyan güncellemeleri biçimsel (epsilon, delta) garantileri sağlar. Hesaplama, bellek ve fayda (utility) üzerindeki ek yük önemlidir; parametre-verimli DP ince ayarı (LoRA + DP-SGD) yaygın 2025 yapılandırmasıdır (ACM 2025). Gerilim içinde iki kanıt kümesi: kanarya-tabanlı üyelik çıkarımı (Duan ve ark., 2024) dil modellerine karşı sınırlı başarı bildirir; eğitim-veri çıkarımı (Carlini ve ark., 2021; Nasr ve ark., 2025) önemli düzeyde kelimesi kelimesine ezberleme kurtarır. Çözüm (arXiv:2503.06808, Mart 2025): boşluk, neyin ölçüldüğündedir — eklenen kanaryalar vs "en çıkarılabilir" veri. Yeni kanarya tasarımları, gölge modeller olmadan kayıp-tabanlı MIA'yı mümkün kılar ve gerçekçi DP garantileriyle gerçek veri üzerinde eğitilmiş bir LLM'nin ilk önemsiz DP denetimini sağlar. Alternatifler: PMixED (arXiv:2403.15638) — sonraki-token dağılımları üzerinde uzman karışımı yoluyla çıkarım zamanında özel tahmin; DP sentetik veri üretimi (Google Research 2024). Ortaya çıkan saldırı: LLM Geri Bildirimi yoluyla Diferansiyel Gizlilik Tersine Çevirme — güven skoru sızıntısı.

**Tür:** Uygulama
**Diller:** Python (stdlib, DP-SGD gürültü-enjeksiyonu ve ε-δ muhasebeci gösterimi)
**Ön Koşullar:** Faz 01 · 09 (bilgi teorisi), Faz 10 · 01 (büyük-model eğitimi)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- (epsilon, delta)-diferansiyel gizliliği tanımlayın ve DP-SGD tarifini belirtin.
- 2024-2025 gerilimini açıklayın: kanarya MIA ile eğitim-veri çıkarımı farklı resimler verir.
- PMixED'yi ve çıkarım-zamanlı özel tahminin DP eğitimine neden bir alternatif olduğunu açıklayın.
- LLM Geri Bildirimi yoluyla Diferansiyel Gizlilik Tersine Çevirme saldırısını açıklayın.

## Sorun

LLM'ler ezberler. Carlini ve ark. 2021, üretim dil modellerinin talep üzerine eğitim metnini kelimesi kelimesine yeniden ürettiğini gösterdi. DP biçimsel savunmadır: herhangi bir tekil eğitim örneğine karşı çıktının kanıtlanabilir şekilde duyarsız olacak şekilde eğitin. 2024-2025 kanıtları, DP-SGD'nin gerekli olduğunu ancak dağıtılan ε değerlerinin tehdit modeliyle eşleşmeyebileceğini gösteriyor.

## Kavram

### (ε, δ)-diferansiyel gizlilik

Bir rastgele algoritma M, bir örnekte farklılık gösteren herhangi iki veri kümesi D ve D' ve herhangi bir olay S için (ε, δ)-DP'dir:
P(M(D) in S) <= e^ε * P(M(D') in S) + δ.

Yorumu: çıktı dağılımı (ε ile parametrelenmiş) herhangi bir tekil bireyin katkısının güvenilir şekilde çıkarılamayacağı kadar yakındır, δ olasılığı hariç.

### DP-SGD

Abadi ve ark. 2016. Standart tarif:
1. Bir mini-yığın örnekleyin.
2. Örnek başına gradyanları hesaplayın.
3. Her örnek başına gradyanı bir C eşiğine kırpın.
4. Kırpılmış gradyanları toplayın ve std σ * C ile Gauss gürültüsü ekleyin.
5. Gürültülü toplamı parametreleri güncellemek için kullanın.

Gizlilik maliyeti bir muhasebeci (Moments Accountant, Rényi DP muhasebecisi) tarafından izlenir. LLM literatüründe rapor edilen ε değerleri tehdit modeline, veri hassasiyetine ve fayda hedefine göre geniş ölçüde değişir; evrensel olarak "güvenli" varsayılan ε yoktur. Yayınlanan örnekler bazı LLM eğitim ayarlarında kabaca ε ≈ 1–10 arasında değişir, ancak bunlar açıklayıcıdır — önerilen varsayılanlar değildir. Daha düşük ε genellikle daha fazla gürültü gerektirir ve fayda kaybını artırabilir.

### LoRA + DP-SGD

Bir sınır modelinin tam DP-SGD'si çok pahalıdır. LoRA (Hu ve ark. 2022) gradyan güncellemelerini küçük bir adaptörle sınırlar, örnek başına gradyan depolamasını azaltır. LoRA + DP-SGD yaygın 2025 yapılandırmasıdır. DP garantileri adaptör için geçerlidir; temel model sabit tutulur.

### 2024-2025 gerilimi

İki kanıt hattı:

- **Kanarya MIA (Duan ve ark. 2024).** Benzersiz kanaryaları eğitim verisine ekleyin, bir üyelik-çıkarım saldırganının bunları tanımlayıp tanımlayamayacağını ölçün. Dil modellerinde sınırlı başarı bildirir. MIA'nın zor olduğunu önerir.
- **Eğitim-veri çıkarımı (Carlini 2021, Nasr ve ark. 2025).** Modele bir önekle verin; eğitimden kelimesi kelimesine metin kurtarıp kurtarmadığını ölçün. Önemli ezberleme bildirir. İlgili anlamda MIA'nın kolay olduğunu önerir.

Mart 2025 çözümü (arXiv:2503.06808): ikisi farklı şeyler ölçer. MIA, eklenen kanaryalar üzerinde "örnek e, D'de mi?" diye sorar. Çıkarım, "D'den ne kurtarabilirim?" diye sorar. Gizlilik için önemli olan "en çıkarılabilir" örnektir; kanaryalar, çıkarılabilir olacak şekilde optimize edilmedikleri için bunu yetersiz bildirir.

Yeni kanarya tasarımları. Gölge modeller olmadan kayıp-tabanlı MIA. Gerçekçi DP garantileriyle gerçek veri üzerinde eğitilmiş bir LLM'nin ilk önemsiz DP denetimi.

### DP eğitimine alternatifler

- **PMixED (arXiv:2403.15638).** Çıkarım zamanında özel tahmin. Sonraki-token dağılımları üzerinde uzman karışımı; her uzman eğitim verisinin bir kısmını görür; toplama DP için gürültü ekler. DP eğitimini tamamen önler.
- **DP sentetik veri üretimi (Google Research 2024).** LoRA ince ayarı DP-SGD ile yapın, sentetik veri örnekleyin, aşağı yönde bir sınıflandırıcıyı sentetik veri üzerinde eğitin.

İkisi de, farklı bir tehdit modeli pahasına, tam DP eğitiminin fayda maliyetini dolanır.

### LLM Geri Bildirimi yoluyla Diferansiyel Gizlilik Tersine Çevirme

Ortaya çıkan 2025 saldırısı. Bir DP-eğitimli modelin güven skorlarını bireyleri yeniden tanımlamak için bir oracle olarak kullanın. Çıktılar sızmasa bile, güven dağılımları sızabilir.

Savunma: güvenleri açığa çıkarmayın veya açığa çıkarmadan önce kırpın/nicemlendirin. Bu, (ε, δ)-DP eğitiminin ötesinde ek bir gereksinimdir.

### Bu, Faz 18'de nereye oturuyor

Dersler 20-21, önyargı/adalettir. Ders 22, gizliliktir. Ders 23, filigranleme yoluyla köken (provenance)dir. Ders 27, düzenleyici veri-köken katmanını kapsar.

## Uygulama

`code/main.py`, oyuncak bir ikili-sınıflandırma veri kümesinde DP-SGD'yi simüle eder. Gürültü çarpanı σ ve kırpma normu C'yi tarayabilir ve (ε, δ) bütçesini ve doğruluk maliyetini izleyebilirsiniz. Bir "kanarya saldırısı" benzersiz bir eğitim örneği ekler ve DP'den önce ve sonra bir log-kayıp testinin onu tespit edip edemeyeceğini ölçer.

## Ship It

Bu ders `outputs/skill-dp-audit.md` üretir. Bir dil modeli dağıtımında DP iddiası verildiğinde, (ε, δ) değerlerini, kullanılan muhasebeciyi, MIA değerlendirme protokolünü ve güven-açığa-çıkarma vektörlerinin değerlendirilip değerlendirilmediğini denetler.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. σ'yi {0.5, 1.0, 2.0} içinde tarayın ve (ε, δ)-doğruluk takasını raporlayın. Faydanın çöktüğü noktayı tanımlayın.

2. Bir kanarya ekleme ve log-kayıp testi uygulayın. σ = 1.0'da DP-SGD'den önce ve sonra tespit oranını ölçün.

3. Nasr ve ark. 2025'i eğitim-veri çıkarımı üzerine okuyun. Çıkarım başarısı orta ε altında neden çökmez? Bu, MIA-olarak-değerlendirme hakkında ne ima eder?

4. Tamamen çıkarım zamanında çalışan PMixED (arXiv:2403.15638) kullanan bir dağıtım tasarlayın. PMixED'in DP-SGD'nin ele almadığı hangi tehdit modelini ele alır?

5. LLM Geri Bildirimi yoluyla DP Tersine Çevirme saldırısını taslaklayın. Güven-skoru sızıntısını sınırlayan bir karşı-önlem tasarlayın ve dağıtım maliyetini tahmin edin.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|---------------------|---------------|
| DP | "(ε, δ)-diferansiyel gizlilik" | Biçimsel gizlilik: komşu-veri-kümesi değişikliği altında çıktı dağılımı yakın |
| DP-SGD | "gürültü-enjekte SGD" | Gradyan kırpma + Gauss gürültüsü ekleme; standart DP eğitimi |
| LoRA + DP-SGD | "verimli özel ince ayar" | Düşük-sıralı adaptörler üzerinde DP-SGD; standart 2025 yapılandırması |
| MIA | "üyelik çıkarımı" | Bir örneğin eğitim verisinde olup olmadığını belirleyen saldırı |
| Kanarya | "eklenmiş filigran örneği" | DP sızıntısını ölçmek için kullanılan benzersiz eğitim örneği |
| PMixED | "özel çıkarım karışımı" | Sonraki-token dağılımları üzerinde uzman-karışımı yoluyla çıkarım-zamanlı DP |
| DP Tersine Çevirme | "güven sızıntısı saldırısı" | Yeniden tanımlama için model güvenini oracle olarak kullanan saldırı |

## İleri Okuma

- [Abadi ve ark. — DP-SGD (arXiv:1607.00133)](https://arxiv.org/abs/1607.00133) — standart DP eğitim algoritması
- [Carlini ve ark. — Extracting Training Data (arXiv:2012.07805)](https://arxiv.org/abs/2012.07805) — kanonik çıkarım makalesi
- [Duan ve ark. — Canary MIA on LLMs (arXiv:2402.07841, 2024)](https://arxiv.org/abs/2402.07841) — sınırlı-başarı MIA
- [Kowalczyk ve ark. — Auditing DP for LLMs (arXiv:2503.06808, Mart 2025)](https://arxiv.org/abs/2503.06808) — gerilimin çözümü
- [PMixED (arXiv:2403.15638)](https://arxiv.org/abs/2403.15638) — çıkarım-zamanlı özel tahmin
