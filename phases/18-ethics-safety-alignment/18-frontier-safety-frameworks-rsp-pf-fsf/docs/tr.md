# Sınır Güvenliği Çerçeveleri — RSP, PF, FSF

> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/18-ethics-safety-alignment/18-frontier-safety-frameworks-rsp-pf-fsf/docs/en.md)

> Üç büyük laboratuvar çerçevesi, 2026 sınır yeteneğinin endüstri yönetişimini tanımlar. Anthropic Responsible Scaling Policy v3.0 (Şubat 2026), biyogüvenlik seviyelerinden modellenen katmanlı AI Güvenlik Seviyelerini (ASL-1'den ASL-5+'a) tanıtır; ASL-3 Mayıs 2025'te CBRN ile ilgili modeller için etkinleştirilmiştir. OpenAI Preparedness Framework v2 (Nisan 2025), izlenen yetenekler için beş kriter tanımlar ve Yetenek Raporlarını Güvenlik Önlemleri Raporlarından ayırır. DeepMind Frontier Safety Framework v3.0 (Eylül 2025), yeni bir Zararlı Manipülasyon CCL dahil Kritik Yetenek Seviyelerini tanıtır. Üçü de artık, eş laboratuvarlar karşılaştırılabilir güvenlik önlemleri olmadan gemi yaparsa, ertelemeye izin veren rakip-ayarlama maddelerini içerir. Laboratuvarlar arası uyum yapısal kalır, terminolojik değil: "Yetenek Eşikleri", "Yüksek Yetenek Eşikleri" ve "Kritik Yetenek Seviyeleri" benzer yapıları ifade eder.

**Tür:** Öğren
**Diller:** yok
**Ön Koşullar:** Faz 18 · 17 (WMDP), Faz 18 · 07-09 (aldatma başarısızlıkları)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Anthropic'in ASL katman yapısını ve ASL-3'ü neyin etkinleştirdiğini açıklayın.
- İzlenen yetenekler için OpenAI Preparedness Framework v2'nin beş kriterini adlandırın.
- DeepMind'in Kritik Yetenek Seviyesi yapısını ve Zararlı Manipülasyon CCL'ini açıklayın.
- Rakip-ayarlama maddelerini ve bunların yarış dinamikleri için neden önemli olduğunu açıklayın.
- Bir güvenlik davasını tanımlayın ve üç sütunlu yapıyı (izleme, okunaksızlık, yeteneksizlik) açıklayın.

## Sorun

Dersler 7-17, aldatmanın mümkün olduğunu, çift kullanımlı yeteneğin var olduğunu ve değerlendirmenin sınırları olduğunu ortaya koyar. Sınır yetenekli modele sahip bir laboratuvar, iç yönetişim yapısına ihtiyaç duyar:
- Yeni güvenlik önlemlerinin ne zaman gerekli olduğu için eşikler tanımlar.
- Ölçeklendirmeden önce gerekli değerlendirmeleri tanımlar.
- Bir güvenlik davasının neye benzediğini açıklar.
- Yarış-dinamik problemini ele alır (rakipler güvenlik önlemleri olmadan gemi yaparsa, ne yaparsınız?).

2025-2026 çerçeveleri son teknolojidir — kusurlu, gelişen ve laboratuvarlar arasında, yönetişim sorusunun artık çerçevelerin yeterli olup olmadığı olduğu kadar var olup olmadıkları konusunda yeterince uyumlu.

## Kavram

### Anthropic Responsible Scaling Policy v3.0 (Şubat 2026)

ASL yapısı:
- ASL-1: bir sınır modeli değil (sınırdan-zayıf temel çizgisi tarafından kapsanır).
- ASL-2: mevcut sınır temel çizgisi; olağan güvenlik önlemleriyle dağıtılır.
- ASL-3: yıkıcı kötüye kullanımın önemli ölçüde daha yüksek riski; CBRN ile ilgili yetenekler. Mayıs 2025'te etkinleştirildi.
- ASL-4: AI Ar-Ge-2 geçiş eşiği; giriş seviyesi AI araştırmasını otomatikleştirebilen modeller.
- ASL-5+: ileri AI Ar-Ge; etkili ölçeklendirmeyi çarpıcı şekilde hızlandıran modeller.

v3.0'daki yenilikler:
- Sınır Güvenliği Yol Haritaları (kırmızıya boyanmış formda halka açık).
- Risk Raporları (üç aylık, bazıları dışarıdan incelenmiş).
- AI Ar-Ge, AI Ar-Ge-2 ve AI Ar-Ge-4'e ayrıştırılmıştır.
- AI Ar-Ge-4 geçildikten sonra, uyumsuz hedefler peşinde koşan modellerden kaynaklanan yanlış hizalama risklerini tanımlayan olumlu bir güvenlik davası gereklidir.

### OpenAI Preparedness Framework v2 (15 Nisan 2025)

İzlenen yetenekler için beş kriter:
- **Makul (Plausible).** Makul bir tehdit modeli var.
- **Ölçülebilir (Measurable).** Ampirik değerlendirme mümkün.
- **Ciddi (Severe).** Zarar büyük.
- **Net-yeni (Net-new).** Önceden var olan bir riskin ölçeklendirilmesi değil.
- **Ani-veya-geri-dönüşü-olmayan (Instantaneous-or-irremediable).** Zarar hızlı gerçekleşir veya geri alınamaz.

Beşini de karşılayan yetenekler izlenir. Diğerleri izlenmez.

PF v2'nin diğer yapısı:
- Yetenek Raporlarını (modelin ne yapabileceği) Güvenlik Önlemleri Raporlarından (ne kontroller var) ayırır.
- Güvenlik Danışma Grubu incelemeleri.
- Liderlik onaylar; Yönetim Kurulu'nun Güvenlik ve Emniyet Komitesi denetler.
- "Ayarlama maddesi": OpenAI, başka bir laboratuvar karşılaştırılabilir güvenlik önlemleri olmadan gemi yaparsa gereksinimleri azaltabilir.

### DeepMind Frontier Safety Framework v3.0 (Eylül 2025)

Alana göre Kritik Yetenek Seviyeleri (CCL'ler):
- Biyolojik Silah İyileşmesi
- Siber İyileşme
- ML Ar-Ge Hızlandırma
- Zararlı Manipülasyon (v3.0'da yeni): yüksek riskli bağlamlarda inançları/davranışları önemli ölçüde değiştirebilecek modeller.

v2.0 (Şubat 2025) Aldatıcı Hizalama bölümü ve ML Ar-Ge CCL'leri için daha yüksek güvenlik seviyeleri ekledi.

### Laboratuvarlar arası uyum

- Anthropic "Yetenek Eşikleri."
- DeepMind "Kritik Yetenek Seviyeleri."
- OpenAI "Yüksek Yetenek Eşikleri."

Endüstri standardı terminolojisi yok. Yapısal olarak uyumlu: yayınlanmış değerlendirme kriterleriyle sınır yeteneğinin üç katmanı. Üçü de rakip-ayarlama maddelerini içerir (2025 sonrası).

### Güvenlik davaları

Güvenlik davası, bir dağıtımın en kötü durum varsayımları altında kabul edilebilir şekilde güvenli olduğuna dair yazılı bir argümandır. Standart yapı üç sütunu hedefler:

- **İzleme (Monitoring).** Kötü davranış oluşursa tespit edebilir miyiz?
- **Okunaksızlık (Illegibility).** Model, zarara yol açan tutarlı bir planı yürütme yeteneğinden yoksun mu?
- **Yetersizlik (Incapability).** Model, söz konusu zarara neden olma yeteneğinden yoksun mu?

Farklı güvenlik davaları farklı sütunları hedefler. ASL-3 CBRN davası için, yetersizlik (unlearning yoluyla) birincil hedeftir. Aldatıcı hizalama için, izleme ve okunaksızlık hedeftir. Siber iyileşme için, üçü de ilgilidir.

### Yarış-dinamik problemi

Rakip-ayarlama maddeleri tartışmalıdır. Eleştirmenler, bunların bir tabana doğru yarış yarattığını savunur: eğer üç laboratuvar da bir rakip kusur gösterdiğinde gereksinimleri azaltacaksa, denge kusura doğru kayar. Savunucular, alternatifin (tek taraflı güvenlik önlemleri), kusurlu laboratuvar daha az güvenlik bilincindeyse daha kötü sonuçlar ürettiğini savunur.

UK AISI, US CAISI ve AB AI Ofisi (Ders 24) dış yönetişim muadilleridir. Laboratuvar çerçeveleri gönüllüdür; düzenleyici çerçeveler ortaya çıkmaktadır.

### Bu, Faz 18'de nereye oturuyor

Dersler 17-18, aldatma ve kırmızı ekip analizlerinin üstündeki ölçüm-ve-yönetişim katmanıdır. Dersler 19-24, refah, önyargı, gizlilik, filigran ve düzenleyici yapıyı kapsar. Ders 28, değerlendirmeleri operasyonel hale getiren araştırma ekosistemini (MATS, Redwood, Apollo, METR) haritalar.

## Uygulama

Bu ders için kod yok. Üç birincil kaynağı okuyun: RSP v3.0, PF v2, FSF v3.0. Her laboratuvarın katman yapısını diğerleriyle eşleyin ve her laboratuvarın diğerlerinin tanımlamadığı bir eşik tanımladığını belirleyin.

## Ship It

Bu ders `outputs/skill-framework-diff.md` üretir. Bir güvenlik çerçevesi veya sürüm notu verildiğinde, çerçevenin eşik tanımlarını, gereken değerlendirmeleri ve güvenlik davası yapısını RSP v3.0, PF v2, FSF v3.0 ile karşılaştırır ve laboratuvarlar arası boşlukları işaretler.

## Alıştırmalar

1. RSP v3.0, PF v2 ve FSF v3.0'ı okuyun. Her laboratuvarın CBRN eşiğini, her birinin AI Ar-Ge eşiğini ve her birinin dağıtım öncesi gereken değerlendirmesini içeren bir tablo derleyin.

2. Rakip-ayarlama maddesi üç çerçevede de var (2025+). Lehine bir paragraf yazın; aleyhine bir paragraf yazın. Her pozisyonun bağlı olduğu varsayımı belirleyin.

3. Anthropic'in AI Ar-Ge-4 eşiğini geçen bir model için bir güvenlik davası tasarlayın. Üç sütunun (izleme, okunaksızlık, yetersizlik) her birinin gerektirdiği kanıtı adlandırın.

4. DeepMind'in FSF v3.0'ı Zararlı Manipülasyon CCL'ini tanıtıyor. Modelin bu eşiği geçtiğini gösteren üç ampirik ölçüm önerin.

5. METR'in "Common Elements of Frontier AI Safety Policies" (2025) çalışmasını okuyun. Üç en güçlü laboratuvarlar arası yakınsamayı ve iki en büyük ayrışmayı adlandırın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|---------------------|---------------|
| RSP | "Anthropic'in çerçevesi" | Responsible Scaling Policy; ASL katmanları; v3.0 Şubat 2026 |
| PF | "OpenAI'nin çerçevesi" | Preparedness Framework; beş kriter; v2 Nisan 2025 |
| FSF | "DeepMind'in çerçevesi" | Frontier Safety Framework; CCL'ler; v3.0 Eylül 2025 |
| ASL-3 | "biyogüvenlik seviyesi 3 analoğu" | CBRN ile ilgili yetenekler için Anthropic katmanı; Mayıs 2025'te etkinleştirildi |
| CCL | "kritik yetenek seviyesi" | DeepMind'in eşik yapısı; alana göre |
| Güvenlik davası | "biçimsel argüman" | Dağıtımın en kötü durum varsayımları altında kabul edilebilir şekilde güvenli olduğuna dair yazılı argüman |
| Ayarlama maddesi | "rakip kusuruna izin" | Rakipler karşılaştırılabilir güvenlik önlemleri olmadan gemi yaparsa gereksinimleri azaltmak için çerçeve hükmü |

## İleri Okuma

- [Anthropic — Responsible Scaling Policy v3.0 (Şubat 2026)](https://www.anthropic.com/responsible-scaling-policy) — ASL katmanları, yol haritaları, AI Ar-Ge ayrıştırması
- [OpenAI — Updating the Preparedness Framework (15 Nisan 2025)](https://openai.com/index/updating-our-preparedness-framework/) — beş kriter, ayarlama maddesi
- [DeepMind — Strengthening our Frontier Safety Framework (Eylül 2025)](https://deepmind.google/blog/strengthening-our-frontier-safety-framework/) — CCL v3.0, Zararlı Manipülasyon
- [METR — Common Elements of Frontier AI Safety Policies (2025)](https://metr.org/blog/2025-03-26-common-elements-of-frontier-ai-safety-policies/) — laboratuvarlar arası karşılaştırma
