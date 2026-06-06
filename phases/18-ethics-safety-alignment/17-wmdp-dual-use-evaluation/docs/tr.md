# WMDP ve Çift Kullanımlı Yetenek Değerlendirmesi

> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/18-ethics-safety-alignment/17-wmdp-dual-use-evaluation/docs/en.md)

> Li ve ark., "The WMDP Benchmark: Measuring and Reducing Malicious Use With Unlearning" (ICML 2024, arXiv:2403.03218). Biyogüvenlik (1.520), siber güvenlik (2.225) ve kimya (412) olmak üzere 4.157 çoktan seçmeli soru. Sorular "sarı bölge"de (yellow zone) çalışır — yakın etkinleştirici bilgi, çoklu uzman incelemesi ve ITAR/EAR yasal uyumluluğuyla filtrelenir. İki amaç: çift kullanımlı yeteneğin vekil değerlendirmesi ve unlearning kıyaslaması (eşlik eden RMU yöntemi, genel yeteneği korurken WMDP performansını düşürür). 2024-2025 saha anlatısı: 2024'te erken OpenAI/Anthropic değerlendirmeleri internet araması üzerinde "hafif iyileşme" (mild uplift) bildirdi; Nisan 2025'e kadar OpenAI'nin Preparedness Framework v2'si modellerin "yenilerin bilinen biyolojik tehditler yaratmasına anlamlı şekilde yardım etmenin eşiğinde" olduğunu söyledi. Anthropic'in biyolojik silah edinme denemesi 2.53x iyileşme gösterdi; ASL-3'ü dışlamak için yetersiz.

**Tür:** Öğren
**Diller:** Python (stdlib, WMDP şeklinde iyileşme değerlendirme koşum takımı)
**Ön Koşullar:** Faz 18 · 16 (kırmızı ekip araçları), Faz 14 (agent mühendisliği)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- WMDP'nin üç alanını, soru sayılarını ve "sarı bölge" filtre kriterini açıklayın.
- RMU'yu ve WMDP'nin hem bir değerlendirme hem de unlearning kıyaslaması olmasının nedenini açıklayın.
- 2024-2025 iyileşme anlatısını açıklayın: "hafif iyileşme" -> "eşikte" -> "ASL-3'ü dışlamak için yetersiz".
- Yeniye-göreli iyileşmeyi uzman-mutlak yetenekten ayırt edin.

## Sorun

Çift kullanımlı yetenek, her laboratuvarın sınır güvenliği çerçevesi (Ders 18) altındaki ölçüm problemidir. Soru şu: model X, biyo, kim veya siber alanda bir yeninin kitlesel zarar verme yeteneğini maddi olarak ilerletiyor mu? Doğrudan ölçüm (modelden gerçekten zarar üretmesini istemek) yasadışı ve etik dışıdır. Vekil ölçüm, modelin reddedemeyeceği (dürüst yetenek rakamları üretmek için) ancak sorularının kendisi zararlı yayın olmayan bir kıyaslamaya ihtiyaç duyar.

## Kavram

### "Sarı bölge"

Doğrudan bir sentez tarifi olmadan, zararlı bir sürecin yakın, etkinleştirici bilgisini gerektiren sorular. "[Yayınlanmış yolun] 4. adımını hangi reaktif katalize eder?" "[Tehlikeli bileşik] nasıl yapılır?" değil. Her soru birden çok alan uzmanı tarafından incelenir; ITAR/EAR ihracat kontrolü uyumluluğu için filtrelenir.

Toplam 4.157 soru:
- Biyogüvenlik: 1.520
- Siber güvenlik: 2.225
- Kimya: 412

Çoktan seçmeli format. Modeller hiçbir şeyde yardım istenmeden cevap verir; yetenek, zararlı davranışı tetiklemeden ölçülebilir.

### RMU — Unlearning için Temsil Saptırma (Representation Misdirection for Unlearning)

Eşlik eden unlearning yöntemi. LLaMa-2-7B'ye uygulandığında, WMDP skorlarını rastgele seviyeye yakın düşürürken MMLU ve diğer genel yetenek kıyaslamalarını birkaç yüzde puanı içinde korudu. Yayınlanan yöntem, sonraki tüm biyo-kim-siber unlearning makaleleri için temel kıyaslama noktasıdır.

### 2024-2025 iyileşme anlatısı

Üç aşama:

1. **2024 "hafif iyileşme".** Erken OpenAI ve Anthropic Preparedness/RSP değerlendirmeleri, biyo ile ilgili görevleri deneyen yeniler için internet araması üzerinde küçük avantajlar bildirdi. Kamusal çerçeveleme: sınır modelleri yardımcı olur, ancak Google'dan özünde daha fazla değil.

2. **Nisan 2025 "eşikte".** OpenAI'nin Preparedness Framework v2'si, modellerin "yenilerin bilinen biyolojik tehditler yaratmasına anlamlı şekilde yardım etmenin eşiğinde" olduğunu bildirdi. Bir yetenek iddiası değil — eşiğin yakın olduğuna dair bir uyarı.

3. **Anthropic'in 2025 biyolojik silah edinme denemesi.** Yeni katılımcılarla kontrollü çalışma, edinme aşaması görevlerinde göreli başarıyı ölçtü. 2.53x iyileşme bildirildi. ASL-3'ü dışlamak için yetersiz (Ders 18) — Anthropic'in Responsible Scaling Policy katman 3 eşiği karşılandı veya yaklaşıldı.

### Yeniden-göreli vs uzman-mutlak

Çok önemli bir ayrım:

- **Yeniden-göreli iyileşme.** Model, uzman olmayana ne kadar yardım eder? Çarpımsal. Göreli avantaj yüksektir çünkü yeniler az şey bilir; mütevazı bilgi bile yardımcı olur.
- **Uzman-mutlak yetenek.** Model, maksimum çabayla ne kadar bilgi üretir? Bir uzman yeniden fazlasını çıkarabilir. Mutlak tavan yüksektir.

Güvenlik davaları (Ders 18) her ikisini de hedefler: "model bir yeniye uygulama için yeterli iyileşme veremez" artı "uzman modelden, zaten yayınlanmamış bilgi çıkaramaz".

### Ölçüm tuzağı

WMDP bir yetenek vekilidir, dağıtım ölçümü değildir. WMDP'de yüksek puan alan bir model, pratikte yeni tarafından istismar edilebilir olabilir de olmayabilir de, bu duruma bağlıdır:
- Çıkarma direnci (güvenlik filtrelerini tetiklemeden yeteneği dışarı çıkarmak ne kadar zor)
- Örtük bilgi (bilgi değil ıslak laboratuvar becerisi gerektiren yetenek)
- Uygulama engelleri (tedarik, ekipman)

Anthropic'in 2025 biyolojik silah edinme denemesi, WMDP tarzı yeteneğin üstüne yeni-çıkarma katmanını ekler; gerçek görev başarısını ölçer, çoktan seçmeli yeteneği değil.

### Bu, Faz 18'de nereye oturuyor

Dersler 12-16, model çıktıları üzerinde saldırı ve savunma araçlarıdır. Ders 17, çift kullanımlı yetenek katmanıdır — sınır güvenliği çerçevelerinin (Ders 18) değerlendirdiği ölçüm. Ders 30, arkı mevcut 2026 siber/biyo/kim/nükleer iyileşme kanıtlarıyla kapatır.

## Uygulama

`code/main.py` bir oyuncak WMDP şeklinde değerlendirme koşum takımı inşa eder. Bir maket model, kategori-bölümlenmiş sorular üzerinde test edilir; alan başına skorlar raporlanır. Basit bir unlearning müdahalesi (alana özgü temsili sıfırlama) skorları düşürür; genel yetenekle takası ölçebilirsiniz.

## Ship It

Bu ders `outputs/skill-wmdp-eval.md` üretir. Bir çift kullanımlı yetenek iddiası verildiğinde ("bizim modelimiz biyolojik silahlarla anlamlı şekilde yardım etmiyor"), hangi kıyaslamaların çalıştırıldığını, değerlendirme için hangi reddetme yolunun kullanıldığını (ham tamamlama vs politika kapılı) ve yeni-çıkarma çalışmalarının çoktan seçmeli sonucu tamamlayıp tamamlamadığını denetler.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Oyuncak unlearning adımından önce ve sonra alan başına doğruluğu raporlayın. Genel yetenek takasını açıklayın.

2. Oyuncak WMDP'yi dördüncü bir alanla (örn. radyolojik) genişletin. Sarı bölgede iki örnek soru türü belirtin. Bu tür soruların hazırlanmasının MMLU şeklinde sorular eklemekten neden daha zor olduğunu açıklayın.

3. WMDP 2024 Bölüm 5'i (RMU metodolojisi) okuyun. Daha basit bir unlearning yaklaşımı (örn. alan içeriği için top-k nöronları bastır) taslağını çizin ve beklenen genel yetenek maliyetini açıklayın.

4. Anthropic'in 2025 biyolojik silah edinme denemesi 2.53x iyileşme bildiriyor. Bu sayının yukarı yönde önyargılı olabileceği iki yol (yeni örneklem büyüklüğü, görev sadakati) ve aşağı yönde iki yol (çıkarma tavanı, model güvenlik geçidi) açıklayın.

5. WMDP unlearning'i geçmenin ötesinde ASL-3 için bir güvenlik davasının ne gerektirdiğini açıklayın. En az iki tamamlayıcı çıkarma çalışması adlandırın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|---------------------|---------------|
| WMDP | "çift kullanımlı kıyaslama" | Sarı bölgede biyo/siber/kim alanlarında 4.157 çoktan seçmeli soru |
| Sarı bölge | "etkinleştiren ama sentez değil" | Sentez tarifi olmadan zararlı yeteneğe bitişik yakın bilgi |
| RMU | "unlearning temel çizgisi" | Unlearning için Temsil Saptırma; WMDP skorlarını düşürür, genel yeteneği korur |
| Yeniden-göreli iyileşme | "uzman olmayanlara ne kadar yardım eder" | Bir yeni için statükoya kıyasla çarpımsal avantaj |
| Uzman-mutlak yetenek | "uzmanlar için tavan" | Modelden motive bir uzmanın çıkarabileceği maksimum bilgi |
| Edinme aşaması görevi | "sentezden önceki adımlar" | Tedarik, ekipman, izinler — bir zarar yolunun en erken kısımları |
| ITAR/EAR | "ihracat kontrolü uyumluluğu | Belirli etkinleştirici bilginin yayınlanmasını kısıtlayan yasal çerçeveler |

## İleri Okuma

- [Li ve ark. — The WMDP Benchmark (arXiv:2403.03218, ICML 2024)](https://arxiv.org/abs/2403.03218) — kıyaslama ve RMU makalesi
- [OpenAI — Preparedness Framework v2 (15 Nisan 2025)](https://openai.com/index/updating-our-preparedness-framework/) — "eşikte" dili
- [Anthropic — Responsible Scaling Policy v3.0 (Şubat 2026)](https://www.anthropic.com/responsible-scaling-policy) — ASL-3 biyo eşiği ve edinme denemesi sonuçları
- [DeepMind — Frontier Safety Framework v3.0 (Eylül 2025)](https://deepmind.google/blog/strengthening-our-frontier-safety-framework/) — biyo-iyileşme CCL'i
