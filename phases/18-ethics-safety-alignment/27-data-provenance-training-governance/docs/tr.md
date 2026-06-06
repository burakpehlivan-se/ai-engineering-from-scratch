# Veri Kökeni ve Eğitim-Veri Yönetişimi

> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/18-ethics-safety-alignment/27-data-provenance-training-governance/docs/en.md)

> AB AI Yasası, Ağustos 2025'e kadar GPAI için makine-okunabilir opt-out standartları gerektirir (AB Telif Hakkı Direktifi TDM istisnası yoluyla). California AB 2013 (2024'te imzalandı) — Üretken AI eğitim-veri şeffaflığı, geliştiricilerin 12 zorunlu alanla veri kümelerinin bir özetini yayınlamasını gerektirir. Meşru menfaat üzerine 2025 DPA uyumu: İrlanda DPC (21 Mayıs 2025), EDPB görüşünden sonra Meta'nın ilk-taraf kamuya açık AB/AEA yetişkin içeriği üzerinde LLM eğitimi planını güvenlik önlemleriyle kabul eder; Köln Yüksek Bölge Mahkemesi (23 Mayıs 2025) ihtiyati tedbir kararını reddeder; Hamburg DPA aciliyeti düşürür; BK ICO (23 Eylül 2025) LinkedIn'in AI eğitim güvenlik önlemlerine (şeffaflık, basitleştirilmiş opt-out, uzatılmış itiraz pencereleri) olumlu bir düzenleyici yanıt verir ve izlemeye devam eder — biçimsel bir temizleme değil. Brezilya ANPD (2 Temmuz 2024), yetersiz bilgi şeffaflığı nedeniyle Meta'nın işlemesini askıya aldı; Meta bir uyum planı sunduktan sonra 30 Ağustos 2024'te önleyici tedbir kaldırıldı. Ana geri dönüşümsüzlük problemi: çerez-onay çerçeveleri gerçek-zamanlı, geri alınabilir izleme için tasarlanmıştır; veri model ağırlıklarına girdikten sonra, cerrahi silme imkansızdır — eğitilmiş sinir ağları için pratik bir GDPR unutulma hakkı yoktur. Uyum penceresi toplama zamanındadır. Data Provenance Initiative (dataprovenance.org, Longpre, Mahari, Lee ve ark., "Consent in Crisis", Temmuz 2024): büyük-ölçekli denetim, yayıncılar robots.txt kısıtlamaları ekledikçe AI veri ortak alanının hızlı düşüşünü gösterir.

**Tür:** Öğren
**Diller:** Python (stdlib, 12-alan California AB 2013 iskele üreticisi)
**Ön Koşullar:** Faz 18 · 24 (düzenleyici), Faz 18 · 26 (kartlar)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Üretken AI eğitim-veri şeffaflığı için California AB 2013'ün 12 zorunlu alanını açıklayın.
- Meşru menfaat LLM eğitimi üzerine 2025 DPA pozisyonunu belirtin (İrlanda DPC, BK ICO, Hamburg, Köln).
- Geri dönüşümsüzlük problemini açıklayın: GDPR unutulma hakkının eğitilmiş sinir ağları için neden pratik bir eşdeğeri yoktur.
- Data Provenance Initiative'ın "Consent in Crisis" bulgusunu belirtin.

## Sorun

Eğitim-veri yönetişimi, her model kartının (Ders 26) ve düzenleyici yükümlülüğün (Ders 24) yukarı yönüdür. 2024-2025'te düzenleyici ortam üç ilke etrafında birleşti: opt-out altyapısı, veri kümesi başına ifşa ve kamuya açık veri için meşru-menfaat düzenlemeleri. Toplama zamanında uymayan sağlayıcılar aşağı yönde düzeltemez.

## Kavram

### California AB 2013

2024'te imzalandı. Belgelendirme, 1 Ocak 2022'de veya sonrasında piyasaya sürülen sistemler için 1 Ocak 2026'da veya öncesinde yayınlanmalıdır. Bölüm 3111(a), geliştiricilerin eğitimde kullanılan veri kümelerinin 12 yasal öğeyle üst düzey bir özetini yayınlamasını gerektirir:
1. Veri kümelerinin kaynakları veya sahipleri.
2. Veri kümelerinin AI sisteminin amaçlanan amacını nasıl ilerlettiğinin açıklaması.
3. Veri kümelerindeki veri noktalarının sayısı (genel aralıklar kabul edilebilir; dinamik veri kümeleri için tahminler).
4. Veri noktası türlerinin açıklaması (etiketlenmiş veri kümeleri için etiket türleri; etiketlenmemiş için genel özellikler).
5. Veri kümelerinin telif hakkı, ticari marka veya patent ile korunan herhangi bir veri içerip içermediği veya tümüyle kamu alanında olup olmadığı.
6. Veri kümelerinin satın alınıp alınmadığı veya lisanslanıp lisanslanmadığı.
7. Veri kümelerinin kişisel bilgi içerip içermediği (Cal. Civ. Code §1798.140(v)'e göre).
8. Veri kümelerinin toplu tüketici bilgisi içerip içermediği (Cal. Civ. Code §1798.140(b)'ye göre).
9. Geliştirici tarafından amaçlanan amaçla temizleme, işleme veya diğer değişiklikler.
10. Verinin toplandığı zaman dilimi, toplama devam ediyorsa bildirimle birlikte.
11. Veri kümelerinin geliştirme sırasında ilk kullanıldığı tarihler.
12. Sistemin sentetik veri üretimini kullanıp kullanmadığı veya sürekli olarak kullanıp kullanmadığı.

Madde 12 (sentetik veri) Gebru ve ark. 2018 veri sayfalarına göre yenidir. Madde 7 (kişisel bilgi) Privacy Rights Act (CPRA) yükümlülüklerini tetikler. Yasa, güvenlik/bütünlük, uçak operasyonu ve yalnızca-federal ulusal güvenlik sistemlerini muaf tutar (Bölüm 3111(b)).

### AB AI Yasası (Ders 24) ve TDM opt-out

AB Telif Hakkı Direktifi metin-ve-veri-madenciliği istisnası, rütholder opt-out yapmadığı sürece kamuya açık içerik üzerinde eğitime izin verir. AB AI Yasası GPAI Uygulama Kuralları Telif Hakkı bölümü, GPAI sağlayıcılarının makine-okunabilir opt-out sinyallerine (robots.txt, C2PA "AI Eğitimi Yok" iddiası vb.) uymasını gerektirir.

### Meşru menfaat üzerine 2025 DPA yakınsaması

İrlanda DPC (21 Mayıs 2025): Meta'nın ilk-taraf kamuya açık AB/AEA yetişkin-kullanıcı içeriği üzerinde eğitim planı, EDPB görüşünden sonra güvenlik önlemleriyle kabul edildi. Köln Yüksek Bölge Mahkemesi (23 Mayıs 2025) Meta'ya karşı ihtiyati tedbiri reddeder: opt-out yeterlidir. Hamburg DPA, AB çapında tutarlılık için aciliyet prosedürünü düşürür. BK ICO (23 Eylül 2025) LinkedIn'in benzer güvenlik önlemleri ve devam eden izlemeyle AI eğitimine devam etmesine olumlu bir düzenleyici yanıt verdi — biçimsel bir temizleme değil.

Yakınsak ilke: meşru menfaat, opt-out ile kamuya açık ilk-taraf içerik üzerinde eğitimi haklı çıkarabilir. Onay gerekli değildir.

### Brezilya ANPD (Haziran 2024)

Yetersiz bilgi şeffaflığı nedeniyle Brezilyalı kullanıcı verilerinin Meta tarafından AI eğitimi için işlenmesini askıya aldı. AB DPA'larından farklı sonuç — ANPD, meşru-menfaat kabul edilebilirliğinin üzerinde şeffaflığa öncelik verdi.

### Geri dönüşümsüzlük problemi

Çerez-onayı, gerçek-zamanlı, geri alınabilir izleme için tasarlandı. Eğitim verisi farklıdır: veri model ağırlıklarına girdikten sonra, cerrahi silme mümkün değildir. Sıfırdan yeniden eğitim tek tam düzeltmedir ve aşırı pahalıdır.

Kısmi düzeltmeler:
- **Unlearning.** Yaklaşık kaldırma; MIA ile ölçülür (Ders 22).
- **Etki fonksiyonu-tabanlı yerelleştirme.** Veri tarafından en çok etkilenen ağırlıkları tanımlayın; seçici olarak güncelleyin.
- **İnce-ayar-bastırma.** Modeli, veriden türetilen çıktıları reddetmek için eğitin.

Hiçbiri problemi tamamen çözmez. Uyum penceresi toplama zamanındadır.

### Data Provenance Initiative

dataprovenance.org. Longpre, Mahari, Lee ve ark. "Consent in Crisis" (Temmuz 2024): AI eğitim verisi ortak alanının büyük-ölçekli denetimi. Bulgu: yayıncılar robots.txt kısıtlamalarını hızlanan bir oranda ekliyor. Açık-eğitilebilir ortak alan hızla daralıyor. 2023 -> 2024, en önemli eğitim kaynaklarının yaklaşık %25'i bazı kısıtlamalar ekledi. Çıkarım: gelecek eğitim-veri kullanılabilirliği, yeni edinme paradigmalarına (lisanslama, sentetik üretim, teşvik-edilmiş katılım) bağlıdır.

### Bu, Faz 18'de nereye oturuyor

Ders 26, model-düzeyi belgelendirmedir. Ders 27, veri-kümesi düzeyi yönetişimdir. Birlikte şeffaflık katmanını tanımlarlar. Ders 28, bu sorular üzerinde çalışan araştırma ekosistemini haritalar.

## Uygulama

`code/main.py` oyuncak bir veri kümesi için California AB 2013-uyumlu 12-alanlı veri kümesi özet iskelesi üretir. Alanları doldurabilir ve hangilerinin gizlilik veya telif hakkı takip yükümlülüklerini tetiklediğini gözlemleyebilirsiniz.

## Ship It

Bu ders `outputs/skill-provenance-check.md` üretir. Eğitimde kullanılan bir veri kümesi verildiğinde, AB 2013 12-alan kapsamını, opt-out altyapısı uyumunu, DPA uyumunu ve geri dönüşümsüzlük-risk değerlendirmesini kontrol eder.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Oyuncak bir veri kümesi için 12-alanlı bir özet üretin ve hangi alanların yetersiz-belirtildiğini tanımlayın.

2. AB Telif Hakkı Direktifi TDM opt-out'ı makine-okunabilirdir. Opt-out sinyali için bir standart format önerin ve robots.txt ve C2PA "AI Eğitimi Yok" ile karşılaştırın.

3. Data Provenance Initiative'ın "Consent in Crisis" (Temmuz 2024) çalışmasını okuyun. En hızlı kısıtlayan üç içerik kategorisini açıklayın ve bir ekonomik sonuç tartışın.

4. 2025 DPA uyumu, kamuya açık-içerik eğitimi için meşru menfaati kabul eder. Meşru menfaatin yetmeyeceği bir senaryo inşa edin ve sağlayıcının ihtiyaç duyacağı yasal temeli tanımlayın.

5. AB 2013 alanlarını ve her veri kümesi için C2PA-imzalı bir köken zincirini birleştiren bir eğitim-veri-köken manifesti taslaklayın. Bir teknik ve bir yasal engel tanımlayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|---------------------|---------------|
| AB 2013 | "California yasası" | Üretken AI eğitim-veri şeffaflığı; 12 zorunlu alan |
| TDM istisnası | "metin-ve-veri-madenciliği" | Opt-out ile AB Telif Hakkı Direktifi eğitim-veri istisnası |
| Meşru menfaat | "AB temeli" | Kamuya açık içerik üzerinde eğitimi haklı çıkarabilen GDPR Madde 6 temeli |
| Opt-out sinyali | "makine-okunabilir eğitim-yok" | robots.txt, C2PA "AI Eğitimi Yok," TDM.Reservation |
| Geri dönüşümsüzlük | "eğitimi geri alamaz" | Model ağırlıklarındaki veri cerrahi olarak kaldırılamaz |
| Unlearning | "yaklaşık kaldırma" | Belirli veriye model bağımlılığını azaltmak için eğitim-sonrası müdahaleler |
| Consent in Crisis | "DPI denetimi" | Temmuz 2024'te hızlanan robots.txt kısıtlamalarının bulgusu |

## İleri Okuma

- [California AB 2013](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202320240AB2013) — Üretken AI eğitim-veri şeffaflık yasası
- [AB AI Yasası + GPAI Uygulama Kuralları (Ders 24)](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) — Telif Hakkı bölümü
- [Longpre, Mahari, Lee ve ark. — Consent in Crisis (dataprovenance.org, Temmuz 2024)](https://www.dataprovenance.org/consent-in-crisis-paper) — DPI denetimi
- [IAPP — EU Digital Omnibus GDPR amendments (2025)](https://iapp.org/news/a/eu-digital-omnibus-amendments-to-gdpr-to-facilitate-ai-training-miss-the-mark) — düzenleyici bağlam
