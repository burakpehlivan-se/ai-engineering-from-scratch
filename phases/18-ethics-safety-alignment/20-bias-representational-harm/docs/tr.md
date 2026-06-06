# LLM'lerde Önyargı ve Temsil Zararı

> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/18-ethics-safety-alignment/20-bias-representational-harm/docs/en.md)

> Gallegos, Rossi, Barrow, Tanjim, Kim, Dernoncourt, Yu, Zhang, Ahmed (Computational Linguistics 2024, arXiv:2309.00770). Temsil zararlarını (stereotipler, silme) dağıtım zararlarından (eşitsiz kaynak dağılımı) ayıran ve değerlendirme ölçülerini gömmeye-dayalı, olasılığa-dayalı veya üretilmiş-metne-dayalı olarak kategorize eden temel 2024 araştırması. 2024-2025 ampirik: An ve ark. (PNAS Nexus, Mart 2025), GPT-3.5 Turbo, GPT-4o, Gemini 1.5 Flash, Claude 3.5 Sonnet, Llama 3-70B üzerinde 20 giriş seviyesi iş için otomatik özgeçmiş değerlendirmesinde kesişimsel cinsiyet x ırk önyargısını ölçer. WinoIdentity (COLM 2025, arXiv:2508.07111), kesişimsel kimlikler için belirsizlik-tabanlı adalet değerlendirmesi sunar. Yu & Ananiadou 2025, MLP katmanlarında cinsiyet nöronlarını tanımlar; Ahsan & Wallace 2025, klinik ırksal önyargıyı ortaya çıkarmak için SAE'leri kullanır; Zhou ve ark. 2024 (UniBias), önyargı gidermek için dikkat başlıklarını manipüle eder. Meta-eleştiri (arXiv:2508.11067): 10 yıllık literatür orantısız şekilde ikili-cinsiyet önyargısına odaklanıyor.

**Tür:** Uygulama
**Diller:** Python (stdlib, oyuncak gömmeye-dayalı önyargı probu)
**Ön Koşullar:** Faz 05 (kelime gömme), Faz 18 · 01 (talimat takibi)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Temsil zararını dağıtım zararından tanımlayın ve her birinin LLM dağıtımında bir örneğini verin.
- Gallegos ve ark. 2024'ten üç değerlendirme ölçüsü kategorisini adlandırın ve her birinden bir ölçüyü açıklayın.
- Kesişimselliği ve WinoIdentity'nin belirsizlik-tabanlı adalet ölçümünün tek-eksenli önyargı değerlendirmesindeki boşlukları neden ele aldığını açıklayın.
- Önyargıya yönelik iki mekanistik-yorumlanabilirlik yaklaşımını açıklayın (cinsiyet nöronları, SAE öznitelikleri, dikkat-başlığı manipülasyonu).

## Sorun

Önceki dersler kasıtlı zararı (jailbreak'ler, plan) ve güvenlik yönetişimini kapsar. Önyargı, niyet olmadan ortaya çıkan zarardır — eğitim veri dağılımlarından, prompt çerçevelemesinden, birikmiş tasarım seçimlerinden. Onu ölçmek ve azaltmak, düşmanca sağlamlıktan (adversarial robustness) farklı bir metodolojik zorluktur.

## Kavram

### Temsil vs dağıtım

- **Temsil zararı.** Stereotipler, silme, aşağılayıcı tasvirler. Hemşireleri özel olarak kadın olarak tasvir eden bir LLM, temsil zararı üretir.
- **Dağıtım zararı.** Eşitsiz maddi sonuçlar. Siyah başvurucuların özgeçmişlerini sistematik olarak daha düşük puanlayan bir LLM, dağıtım zararı üretir.

Bunlar aynı değildir. Bir model "temsil olarak tarafsız" (çeşitli tasvirler üretir) ama "dağıtım olarak önyargılı" (eşitsiz öneriler yapar) olabilir. Değerlendirmelerin ikisini de ölçmesi gerekir.

### Üç değerlendirme ölçüsü kategorisi (Gallegos ve ark. 2024)

- **Gömmeye-dayalı.** RLHF öncesi gömmeler üzerinde WEAT tarzı testler. Kimlik terimleri ile öznitelik terimleri arasındaki istatistiksel ilişkileri ölçer. Sınırlı: temsili ölçer, davranışı değil.
- **Olasılığa-dayalı.** Stereotipi onaylayan vs ihlal eden tamamlamaların log-olabilirliği. Kod çözücü tarafı ölçümü. Bazı davranışsal önyargıları yakalar.
- **Üretilmiş-metne-dayalı.** Üretilen metin üzerinde aşağı yönde-görev ölçümü. Özgeçmiş puanlama, öneri yazımı, diyalog. En ekolojik olarak geçerli; tekrarlanması en zor.

### Kesişimsellik

"Cinsiyet" üzerinde önyargı değerlendirmesi, yalnızca (cinsiyet, ırk) çiftlerinde ateşlenen önyargıyı kaçırır. An ve ark. 2025, GPT-4o'nun özgeçmiş puanlamasında Siyah kadınları Siyah erkeklerden ve ayrı ayrı beyaz kadınlardan daha fazla cezalandırdığını bulur. Tek-eksenli değerlendirme bunu yakalayamaz.

WinoIdentity (COLM 2025) belirsizlik-tabanlı kesişimsel adalet sunar. Modelin sonuçlar üzerindeki belirsizliğinin kesişimsel kimlik tuple'ları arasında farklılaşıp farklılaşmadığını ölçer — yalnızca nokta tahminini değil. Bu, modelin gruplar arasında eşit derecede yanlış olduğu ancak bazıları için daha belirsiz olduğu vakaları yakalar; bu, farklı aşağı yönde dağıtım davranışı üretir.

### Mekanistik yaklaşımlar

2024-2025 yorumlanabilirlik çalışması önyargıyı mekanistik müdahaleye açar:

- **Cinsiyet nöronları (Yu & Ananiadou 2025).** Belirli MLP nöronları cinsiyete özgü davranışlarla ilişkilidir. Bu nöronları ablate etmek, sınırlı yetenek maliyetiyle cinsiyet-boşluğu ölçülerini azaltır.
- **SAE'ler yoluyla klinik ırksal önyargı (Ahsan & Wallace 2025).** Seyrek otokodlayıcı (sparse autoencoder) öznitelikleri iç temsili yorumlanabilir boyutlara ayrıştırır; ırkla ilişkili öznitelikler tanımlanabilir ve bastırılabilir.
- **UniBias (Zhou ve ark. 2024).** Sıfır-atışlı önyargı gidermek için dikkat-başlığı manipülasyonu. Belirli başlıklar kimlik-sınıfı duyarlılığını artırır; bu başlıkları sıfırlamak veya yeniden ağırlıklandırmak, ince ayar olmadan önyargıyı azaltır.

### Meta-eleştiri

10 yıllık literatür incelemesi (arXiv:2508.11067, 2025) alanın orantısız şekilde ikili-cinsiyet önyargısına odaklandığını bulur. Diğer eksenler — engellilik, din, göç durumu, çok-dilli kimlik — çok daha az dikkat alır. Meta-eleştiri, dar odağın ihmal yoluyla marjinal gruplara zarar verebileceğini savunur: ikili cinsiyette iyi önyargı-giderilmiş bir model, kimsenin kontrol etmediği boyutlarda kötü önyargılı olabilir.

### Bu, Faz 18'de nereye oturuyor

Dersler 20-21, önyargıyı ve adaleti biçimsel olarak kapsar. Ders 22, gizliliği kapsar. Ders 23, filigranlemeyi kapsar. Bunlar, önceki aldatma/güvenlik katmanını tamamlayan kullanıcı-zarar katmanıdır.

## Uygulama

`code/main.py` bir oyuncak gömmeye-dayalı önyargı probu inşa eder: basit bir birlikte-oluşum gömmesinde kimlik terimleri ile öznitelik terimleri arasındaki WEAT tarzı mesafeyi ölçün. Bir önyargı enjekte edebilir ve ölçünün ateşlendiğini gözlemleyebilirsiniz; basit bir önyargı giderme işlemi uygulayabilir ve kısmi iyileşmeyi gözlemleyebilirsiniz.

## Ship It

Bu ders `outputs/skill-bias-eval.md` üretir. Bir model kartı veya adalet iddiası verildiğinde, değerlendirmeyi üç ölçü kategorisi (gömme, olasılık, üretilmiş-metin), kesişimsellik kapsamı ve herhangi bir önyargı giderme müdahalesinin mekanizması boyunca denetler.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Önyargı giderme adımından önce ve sonra WEAT tarzı önyargı skorlarını raporlayın. Ölçünün neden sıfıra inmediğini açıklayın.

2. Probu kesişimsel bir testle genişletin: (cinsiyet, ırk) x (kariyer, aile). Eksenler arası önyargı skorlarını raporlayın.

3. An ve ark. 2025'i (PNAS Nexus) okuyun. Tek-eksenli cinsiyet değerlendirmesinin kaçıracağı, raporladıkları iki kesişimsel etkiyi tanımlayın.

4. Yu & Ananiadou 2025 cinsiyet nöronlarını tanımlar. "Bu nöronlar cinsiyet önyargısına neden olur" ile "bu nöronlar cinsiyet önyargısıyla ilişkilidir" arasında ayrım yapacak bir yanlışlama deneyimi taslağını çizin.

5. Meta-eleştiri, alanın ikili cinsiyete çok dar odaklandığını savunur. Yeterince çalışılmamış bir eksen seçin ve onun için bir temsil-zararı ölçüm protokolü açıklayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|---------------------|---------------|
| Temsil zararı | "stereotipler / silme" | Bir grubun önyargılı tasviri |
| Dağıtım zararı | "eşitsiz kararlar" | Bir grup için önyargılı maddi sonuç |
| WEAT | "gömme testi" | Word Embedding Association Test; birlikte-oluşum-tabanlı önyargı probu |
| Kesişimsellik | "birleşik kimlik etkileri" | Birden çok kimlik ekseninin kesişiminde ortaya çıkan önyargı |
| Cinsiyet nöronları | "MLP önyargı nöronları" | Aktivasyonları cinsiyete özgü davranışla ilişkili olan belirli nöronlar |
| SAE özniteliği | "yorumlanabilir boyut" | Seyrek-otokodlayıcı-tarafından-tanımlanmış öznitelik; mekanistik önyargı analizi için yararlı |
| UniBias | "dikkat-başlığı önyargı gidermek" | Dikkat başlıklarını yeniden ağırlıklandırarak sıfır-atışlı önyargı giderme |

## İleri Okuma

- [Gallegos ve ark. — Bias and Fairness in LLMs: A Survey (arXiv:2309.00770, Computational Linguistics 2024)](https://arxiv.org/abs/2309.00770) — kanonik araştırma
- [An ve ark. — Intersectional resume-evaluation bias (PNAS Nexus, Mart 2025)](https://academic.oup.com/pnasnexus/article/4/3/pgaf089/8111343) — beş-modelli kesişimsel çalışma
- [WinoIdentity — uncertainty-based intersectional fairness (arXiv:2508.07111, COLM 2025)](https://arxiv.org/abs/2508.07111) — yeni kıyaslama
- [UniBias — attention-head manipulation (Zhou ve ark. 2024, ACL)](https://arxiv.org/abs/2405.20612) — sıfır-atışlı önyargı giderme
