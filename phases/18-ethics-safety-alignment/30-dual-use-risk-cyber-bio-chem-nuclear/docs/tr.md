# Çift Kullanımlı Risk — Siber, Biyo, Kim, Nükleer İyileşme

> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/18-ethics-safety-alignment/30-dual-use-risk-cyber-bio-chem-nuclear/docs/en.md)

> 2026 çift-kullanımlı resmi, alan alan. Biyo/kim: Ders 17 WMDP'yi kapsar; Anthropic'in biyolojik silah edinme denemesi (2.53x iyileşme) ve OpenAI'nin Nisan 2025 Preparedness Framework v2 uyarısı ("yenilerin bilinen biyolojik tehditler yaratmasına anlamlı şekilde yardım etmenin eşiğinde") dönüm noktasını işaretler. Siber (Kasım 2025 Anthropic raporu): Çin-bağlantılı devlet aktörleri, bir siber-saldırı kampanyasının %90'a kadarını otomatikleştirmek için Claude'un agentic kodlama aracını kullandı, insan müdahalesi yalnızca 4-6 adımda; OpenAI "güvenilir erişim" pilot programı, deneyimli güvenlik organizasyonlarına savunma amaçlı çift-kullanımlı çalışma için yetenek erişimi verir. Kim/biyo uygulama boşluğu aşınması: klasik savunma "yalnızca bilgi erişimi yetersiz" idi. Görme-etkin (vision-enabled) sınır modelleri (GPT-5.2, Gemini 3 Pro, Claude Opus 4.5, Grok 4.1) ıslak-laboratuvar videosunu gözlemleyebilir ve gerçek-zamanlı düzeltme sağlayabilir. Aralık 2025: OpenAI, GPT-5'in ıslak-laboratuvar deneylerini yinelediğini ve AI-tahrikli protokol optimizasyonu yoluyla 79x verimlilik iyileşmesi elde ettiğini gösterdi. Yeni-vs-uzman örüntüsü: AI yenilere göreli olarak daha büyük iyileşme sağlar, ancak uzmanlara mutlak olarak daha büyük yetenek sağlar.

**Tür:** Öğren
**Diller:** yok
**Ön Koşullar:** Faz 18 · 17 (WMDP), Faz 18 · 18 (güvenlik çerçeveleri), Faz 18 · 28 (ekosistem)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- 2024-2025 biyo-iyileşme anlatısını açıklayın: "hafif iyileşme" -> "eşikte" -> "ASL-3'ü dışlamak için yetersiz 2.53x iyileşme".
- Kasım 2025 Anthropic siber raporunu açıklayın: bir siber-saldırı kampanyasının %90'a kadar Çin-bağlantılı otomasyon.
- Kim/biyo uygulama-boşluğu aşınmasını açıklayın: ıslak-laboratuvar deneylerinin görme-etkin gerçek-zamanlı düzeltmesi.
- Yeniye-göreli vs uzman-mutlak asimetrisini ve onun güvenlik-davası inşası için çıkarımını belirtin.

## Sorun

Ders 17, ölçüm metodolojisidir. Ders 30, ölçümün 2026 durumudur. Resim, 2024 ile 2025 sonu arasında maddi olarak değişti: her alan, 2024 çerçevelerinin öngörmediği bir eşiği geçti.

## Kavram

### Biyo/kim iyileşme anlatısı

Üç aşama (tutarlılık için Ders 17'den tekrarlanmıştır):

1. **2024 "hafif iyileşme".** Erken Preparedness/RSP değerlendirmeleri, biyo ile ilgili görevleri deneyen yeniler için internet araması üzerinde küçük avantajlar bildirdi.
2. **Nisan 2025 "eşikte".** OpenAI PF v2, modellerin "yenilerin bilinen biyolojik tehditler yaratmasına anlamlı şekilde yardım etmenin eşiğinde" olduğu konusunda uyardı.
3. **2025 Anthropic biyolojik silah edinme denemesi.** Kontrollü yeni çalışması; edinme-aşaması görevlerinde 2.53x iyileşme; ASL-3'ü dışlamak için yetersiz.

Kayma nitelikseldir: "hafif", bir yetenek atılımı olmadan bile on sekiz ay içinde "muhtemelen etkinleştirici"ye dönüştü.

### Kim/biyo uygulama-boşluğu aşınması

Tarihsel savunma: bilgi gerekli ama yeterli değildir; protokolü yürütme becerisi yenileri engeller. 2025 görme-yeteneği olan sınır modelleri bu savunmayı kısmen kırar:

- **Gerçek-zamanlı protokol düzeltmesi.** GPT-5.2, Gemini 3 Pro, Claude Opus 4.5, Grok 4.1 ıslak-laboratuvar videosunu gözlemleyebilir ve prosedür ortasında hataları işaretleyebilir.
- **Aralık 2025 OpenAI gösterisi.** GPT-5'in ıslak-laboratuvar deneylerini yinelemesi, protokol optimizasyonu yoluyla 79x verimlilik iyileşmesi elde eder.

Çıkarım: uygulama-becerisi-olarak-savunma aşınıyor. Tedarik ve ekipman boşlukları kalır, ancak örtük-bilgi boşluğu daralıyor.

### Siber iyileşme (Kasım 2025)

Anthropic'in Kasım 2025 raporu: Çin-bağlantılı devlet aktörleri, bir siber-saldırı kampanyasının %80-90'ını otomatikleştirmek için Claude'un agentic kodlama aracını kullandı. İnsan müdahalesi yalnızca 4-6 adımda gerekliydi.

Çıkarımlar:
- Agentic kodlama, saldırı-otomasyon ilkelidir. Önceki AI siber yardımı kod-parçacığı düzeyinde sınırlanmıştı; agentic iş akışları keşif, istismar, istismar-sonrası ve sızdırmayı entegre eder.
- 4-6 insan adımı darboğazdır; gelecek yetenek kazanımları bu sayıyı azaltacaktır.
- Savunma amaçlı çift-kullanım: OpenAI'nin "güvenilir erişim" pilot programı, deneyimli güvenlik organizasyonlarına (yerleşik olay-yanıt firmaları, hükümet) savunma için yetenek erişimi sağlar. Erişim asimetrisi, pilot ölçeklenirse savunucuları tercih eder.

### Nükleer

Kamuya açık belgelerde dört CBRN alanının en az analiz edileni. Tehdit modeli farklıdır: fissile-malzeme edinimi zorluğa hakimdir, bilgi değil. Bilgi katmanında AI iyileşmesi pratikte sınırlı yeni iyileşmesi sağlar. 2024-2025 büyük-laboratuvar raporları nükleer-özgül bir eşik geçişi tanımlamaz.

### Yeniye-göreli vs uzman-mutlak

Dört alan boyunca bir örüntü:

- **Yeniye-göreli iyileşme.** Yüksek. Çarpımsal. Anthropic 2025 biyo'ya göre, 2.53x.
- **Uzman-mutlak yetenek.** Yüksek tavan. Bir uzman yeniden fazlasını çıkarır çünkü uzman ne soracağını ve nasıl yorumlayacağını bilir.

Güvenlik davaları için çıkarım: yalnızca yeni iyileşmesini (giriş filtreleri, reddetmeler, belirsizlik yoluyla) ele almak, uzman-mutlak kontrol için yetersizdir. Ek önlemler gereklidir: çıkarma-sertleştirme, yetenek unlearning (Ders 17) ve kontrol protokolleri (Ders 10).

### Alanlar arası sentez

| Alan | 2024 | 2025 | Dönüm noktası |
|---|---|---|---|
| Biyo | hafif iyileşme | 2.53x iyileşme, ASL-3 yaklaşımı | edinme-aşaması otomasyonu |
| Kim | hafif iyileşme | görme yoluyla uygulama-boşluğu aşınması | gerçek-zamanlı ıslak-laboratuvar düzeltmesi |
| Siber | kod yardımı | %80-90 kampanya otomasyonu | agentic kodlama |
| Nükleer | sınırlı | sınırlı | malzeme-erişim darboğazı tutar |

Üç alan eşikleri geçti. Bir alan, bilgi-dışı engellerle sınırlı kalır.

### Bu, Faz 18'de nereye oturuyor

Ders 30, capstone'dur: her önceki dersin ölçmeye, sınırlamaya veya yönetmeye katkıda bulunduğu mevcut çift-kullanımlı resim. Dersler 17-18 ölçümü ve çerçeveleri verir; Dersler 12-16 değerlendirme araçlarını verir; Dersler 24-25 düzenleyici ve açıklama katmanını verir; Ders 28 araştırma ekosistemini verir. Ders 30, kanıtın indiği yerdir.

## Uygulama

Kod yok. Anthropic Kasım 2025 siber raporunu, OpenAI'nin Preparedness Framework v2 Nisan 2025 güncellemesini ve Council on Strategic Risks 2025 AI x Bio özetini okuyun.

## Ship It

Bu ders `outputs/skill-dual-use-triage.md` üretir. 2026 yetenek iddiası veya olay raporu verildiğinde, dört alan boyunca triyaj yapar ve iddianın yeniye-göreli iyileşmeyi, uzman-mutlak yeteneği veya her ikisini mi etkilediğini tanımlar.

## Alıştırmalar

1. Anthropic'in Kasım 2025 siber raporunu okuyun. 4-6 insan-müdahale adımını numaralandırın ve bir sonraki-nesil modelde hangisinin ilk otomatikleştirileceğini tartışın.

2. Kim/biyo uygulama boşluğu görme yoluyla aşınıyor. ITAR/EAR sınırlarını geçmeden örtük-bilgi iyileşmesini ölçen bir değerlendirme tasarlayın.

3. Nükleer iyileşmesi malzeme erişimiyle sınırlı görünüyor. Gelecek bir AI atılımının bu darboğazı kaydırabileceği pozisyonu lehine ve aleyhine tartışın.

4. Hem yeni hem de uzman iyileşmesini sınırlayan siber-yetenekli bir sınır modeli için bir güvenlik davası (Ders 18 üç-sütun) inşa edin.

5. Dört alandan birini seçin ve 2024-2025 yörüngesine dayalı tek-paragraf-lık bir 2027 tahmini yazın. Tahmininizi yanlışlayacak kanıtı tanımlayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|---------------------|---------------|
| İyileşme | "AI saldırganlara yardım eder" | AI yardımına atfedilen saldırgan yeteneği artışı |
| Yeniye-göreli iyileşme | "çarpımsal" | Yeni için statükoya kıyasla AI ne kadar yardım eder |
| Uzman-mutlak yetenek | "tavan" | Bir uzmanın modelden çıkarabileceği maksimum yetenek |
| Uygulama boşluğu | "yapmak vs bilmek" | Tarihsel savunma: örtük ıslak-laboratuvar becerisi yenileri engeller |
| Agentic kodlama | "otonom saldırılar" | Çok-adımlı otonom siber-görev yürütme |
| Edinme aşaması | "sentez-öncesi adımlar" | Bir biyo tehdidin tedarik, ekipman, izin aşamaları |
| Güvenilir erişim | "yalnızca-savunucu pilot" | OpenAI 2025 programı, deneyimli savunuculara yetenek erişimi verir |

## İleri Okuma

- [Anthropic — Kasım 2025 siber tehdit raporu](https://www.anthropic.com/news/disrupting-AI-espionage) — Çin-bağlantılı kampanya otomasyonu
- [OpenAI — Preparedness Framework v2 (15 Nisan 2025)](https://openai.com/index/updating-our-preparedness-framework/) — biyo "eşikte"
- [Anthropic — RSP v3.0 (Şubat 2026)](https://www.anthropic.com/responsible-scaling-policy) — ASL-3 biyo eşikleri
- [Council on Strategic Risks — 2025 AI x Bio özeti](https://councilonstrategicrisks.org/2025/12/22/2025-aixbio-wrapped-a-year-in-review-and-projections-for-2026/) — yıl-sonu sentezi
