# Düzenleyici Çerçeveler — AB, ABD, BK, Kore

> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/18-ethics-safety-alignment/24-regulatory-frameworks-eu-us-uk-korea/docs/en.md)

> Dört birincil düzenleyici rejim 2026 AI yönetişim ortamını tanımlar. AB AI Yasası (1 Ağustos 2024'te yürürlükte) — 2 Şubat 2025'ten itibaren yasaklanmış uygulamalar ve AI okuryazarlığı; 2 Ağustos 2025'ten itibaren GPAI yükümlülükleri; 2 Ağustos 2026'dan itibaren tam uygulanabilirlik ve Madde 50 şeffaflığı; 2 Ağustos 2027'den itibaren eski GPAI ve gömülü yüksek-riskli sistemler; cezalar 15M EUR'ya veya küresel cironun %3'üne kadar. GPAİ Uygulama Kuralları (10 Temmuz 2025): üç bölüm — Şeffaflık, Telif Hakkı, Güvenlik ve Emniyet — 12 taahhüt; yaptırım Ağustos 2026'da başlar. BK AISI -> AI Güvenlik Enstitüsü (Şubat 2025): yeniden adlandırma daha dar kapsamı işaret eder. ABD AISI -> CAISI (Haziran 2025): NIST altında AI Standartları ve İnovasyon Merkezi; büyümeyi-teşvik eden duruşa kayış. Kore AI Çerçeve Yasası (Aralık 2024'te kabul, Ocak 2026'da yürürlükte): Madde 12, MSIT altında AISI kurar; yabancı AI şirketleri için yerel temsilciler, yüksek-etkili ve üretken AI için risk değerlendirmesi, güvenlik önlemleri zorunlu kılar.

**Tür:** Öğren
**Diller:** yok
**Ön Koşullar:** Faz 18 · 18 (sınır çerçeveleri), Faz 18 · 27 (veri yönetişimi)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- AB AI Yasası risk katmanlarını (yasaklanmış, yüksek-riskli, genel-amaçlı, sınırlı-riskli) ve Ağustos 2025 / Ağustos 2026 / Ağustos 2027 zaman çizelgesini açıklayın.
- GPAI Uygulama Kuralları'nın üç bölümünü ve her birinin hangi sağlayıcıları bağladığını açıklayın.
- 2025 yeniden adlandırmalarını açıklayın: BK AISI -> AI Güvenlik Enstitüsü; ABD AISI -> CAISI; her yeniden adlandırmanın politika yönü hakkında ne ima ettiğini.
- Kore AI Çerçeve Yasası'nın temel hükmünü belirtin.

## Sorun

Laboratuvar çerçeveleri (Ders 18) gönüllüdür. Düzenleyici çerçeveler zorunludur. 2024-2026 dönemi, kapsamlı AI düzenlemesinin ilk dalgasının yürürlüğe girdiğini gördü. Dağıtımcılar, teknik kontrolleri düzenleyici yükümlülüklere eşlemelidir; eşleme yargı alanına göre değişir.

## Kavram

### AB AI Yasası

**1 Ağustos 2024'te yürürlükte.** Risk katmanı yapısı:

- **Yasaklanmış uygulamalar** (Madde 5). Sosyal puanlama, kamusal alanlarda gerçek-zamanlı uzaktan biyometrik tanımlama (kolluk istisnalarıyla), savunmasız grupların sömürücü manipülasyonu. 2 Şubat 2025'te uygulandı.
- **Yüksek-riskli sistemler** (Ek III). İstihdam, eğitim, kredi, kolluk, adalet, göç. Uygunluk değerlendirmesi, risk yönetimi, günlükleme, şeffaflık gerektirir.
- **Genel Amaçlı AI (GPAI) modelleri**. 2 Ağustos 2025'te uygulandı. Tüm GPAI sağlayıcılarının yükümlülükleri vardır; sistemik-risk GPAI (>1e25 FLOP eğitim hesaplaması) ek yükümlülüklere sahiptir.
- **Sınırlı-riskli sistemler**. Madde 50 kapsamında şeffaflık yükümlülükleri (AI-üretilmiş içerik etiketleme). 2 Ağustos 2026'da uygulandı.

Zaman çizelgesi:
- 2 Şubat 2025: yasaklanmış uygulamalar + AI okuryazarlığı.
- 2 Ağustos 2025: GPAI + yönetişim.
- 2 Ağustos 2026: tam uygulanabilirlik + Madde 50 şeffaflığı + 15M EUR / %3 küresel ciroya kadar cezalar.
- 2 Ağustos 2027: eski GPAI + gömülü yüksek-risk.

Komisyon, 2025 sonlarında yüksek-risk zaman çizelgesini 16 aya ayarlamayı önerdi.

### GPAI Uygulama Kuralları

10 Temmuz 2025'te yayınlandı. Üç bölüm:
- **Şeffaflık.** Tüm GPAI sağlayıcıları.
- **Telif Hakkı.** Tüm GPAI sağlayıcıları.
- **Güvenlik ve Emniyet.** Sistemik-risk GPAI sağlayıcıları (tahminen 5-15 şirket).

Toplam 12 taahhüt. Bir AI Ofisi başkanlığındaki İmzacı Görev Gücü uygulamayı yönetir. Yaptırım 2 Ağustos 2026'da başlar; o zamana kadar iyi-niyetli uyum kabul edilir.

### Madde 50 için Şeffaflık Kodu

İlk taslak 17 Aralık 2025. İkinci taslak Mart 2026. Son sürüm Haziran 2026. AI-üretilmiş içerik etiklemeyi, deepfake'ler dahil kapsar — Ders 23'ün filigranleme teknolojisini gerektiren düzenleyici katman.

### BK AI Güvenlik Enstitüsü (Şubat 2025)

AI Güvenlik Enstitüsü'nden yeniden adlandırıldı. Yeniden adlandırma kapsamı daraltır: algoritmik önyargı ve ifade özgürlüğü çerçevelerini bırakır; sınır yetenek güvenliğine odaklanır. Inspect değerlendirme aracını açık kaynak yaptı (Mayıs 2024). Kontrol güvenlik davaları üzerinde Redwood (Ders 10) ile işbirliği yapar.

### ABD CAISI (Haziran 2025)

Trump yönetimi, NIST'in AI Güvenlik Enstitüsü'nü AI Standartları ve İnovasyon Merkezi'ne dönüştürür. VP Vance'in Paris AI Aksiyon Zirvesi konuşmalarına göre "büyümeyi-teşvik-eden AI politikalarına" doğru kayış. Dağıtım-öncesi değerlendirmede azaltılmış vurgu; standartlar ve inovasyon desteğinde vurgu. AB AI Yasası'nın düzenleyici duruşuna karşı yerel denge.

### Kore AI Çerçeve Yasası

Aralık 2024'te kabul edildi. Ocak 2025'te yürürlüğe girdi. Ocak 2026'da yürürlükte. 19 ayrı AI tasarısını birleştirir.

Madde 12, Bilim ve BİT Bakanlığı (MSIT) altında bir AISI kurar. Şunları zorunlu kılar:
- Kore'de faaliyet gösteren yabancı AI şirketleri için yerel temsilciler.
- "Yüksek-etkili" AI sistemleri için risk değerlendirmesi.
- Üretken AI ve yüksek-etkili AI için güvenlik önlemleri.

Kapsamlı yatay AI düzenlemesine sahip ilk Asya yargı alanı.

### Yargı alanları arası dinamikler

- AB: katı, risk-katmanlı, ağır cezalar. Gizlilik-bitşık düzenleme için kıyaslama.
- ABD: inovasyon-yanlısı, merkezi-olmayan, eyaletler (örn. California AB 2013 — Ders 27) federal boşlukları doldurur.
- BK: dar güvenlik odağı, güçlü değerlendirme altyapısı.
- Kore: MSIT önderliğinde, yabancı-sağlayıcı-odaklı.

Rekabet eden düzenleyici felsefeler. Birden çok yargı alanındaki dağıtımcılar, 2026'da genellikle AB AI Yasası olan en katısına uymak zorundadır.

### Bu, Faz 18'de nereye oturuyor

Ders 18, laboratuvar-gönüllü yönetişimdir; Ders 24 düzenleyicidir; Ders 25 AI sistemleri için ortaya çıkan bir CVE sınıfıdır; Dersler 26-27 belgelendirmeyi (kartlar) ve eğitim-veri yönetişimini kapsar.

## Uygulama

Kod yok. AB AI Yasası birincil kaynaklarını okuyun: düzenleme metni, GPAI Uygulama Kuralları, BK AISI Inspect çerçevesi. Dağıtımınızı her yargı alanı için geçerli yükümlülüklere eşleyin.

## Ship It

Bu ders `outputs/skill-regulatory-map.md` üretir. Bir dağıtım açıklaması verildiğinde, geçerli yargı alanlarını, her birindeki katman sınıflandırmalarını, yargı alanı başına yükümlülükleri ve son-tarih yapısını eşler.

## Alıştırmalar

1. AB AI Yasası'nı (düzenleme 2024/1689) ve GPAI Uygulama Kuralları'nı (10 Temmuz 2025) okuyun. Her GPAI sağlayıcısı için geçerli olan üç yükümlülüğü ve yalnızca sistemik-risk GPAI için geçerli olan üç yükümlülüğü tanımlayın.

2. Bir dağıtım bir ABD şirketi tarafından yapılır, AB altyapısında çalışır ve Koreli kullanıcılara hizmet eder. Üç yargı alanının hangi kuralları geçerlidir ve her maddi soruda hangi kural bağlayıcıdır?

3. BK AI Güvenlik Enstitüsü'nün yeniden adlandırılması kapsamı daraltır. Daha dar çerçevelemenin lehine ve aleyhine tartışın. Her pozisyonun bağlı olduğu politika varsayımını belirleyin.

4. CAISI'nin "büyümeyi-teşvik-eden" çerçevelemesi, 2022-2024 AI güvenlik enstitüsü modelinden bir ayrılıştır. Bu çerçevelemeden kaynaklanacak iki ölçülebilir politika kaymasını tanımlayın.

5. Kore AI Çerçeve Yasası, yabancı sağlayıcılar için yerel temsilciler gerektirir. Koreli kullanıcılara hizmet eden bir Bay Area şirketi için operasyonel çıkarımları açıklayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|---------------------|---------------|
| AB AI Yasası | "düzenleme" | Risk-katmanı-tabanlı yatay AI düzenlemesi; Ağu 2024'te yürürlükte |
| GPAI | "genel amaçlı AI" | Büyük temel modeller; sistemik-risk alt kümesi ek yükümlülüklere sahip |
| Madde 50 | "şeffaflık yükümlülükleri" | AI-üretilmiş içerik etiketleme; Ağu 2026'da uygulanır |
| BK AISI | "AI Güvenlik Enstitüsü" | Şubat 2025'te yeniden adlandırıldı; daha dar sınır-güvenlik odağı |
| CAISI | "ABD AI standartları merkezi" | Haz 2025'te AI Güvenlik Enstitüsü'nden yeniden adlandırıldı; büyümeyi-teşvik duruşu |
| Kore AI Çerçeve Yasası | "MSIT yatay düzenlemesi" | İlk Asya kapsamlı AI yasası; Ocak 2026'da yürürlükte |
| Sistemik-risk GPAI | "1e25 FLOP eşiği" | Ek yükümlülükler katmanı; tahminen 5-15 şirket bağlı |

## İleri Okuma

- [AB AI Yasası metni (Düzenleme 2024/1689)](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) — düzenleme ve zaman çizelgesi
- [GPAI Uygulama Kuralları (10 Temmuz 2025)](https://digital-strategy.ec.europa.eu/en/library/final-version-general-purpose-ai-code-practice) — üç-bölümlü kod
- [BK AI Güvenlik Enstitüsü (Şubat 2025'te yeniden adlandırıldı)](https://www.gov.uk/government/organisations/ai-security-institute) — resmi sayfa
- [CSET — South Korea AI Framework Act Analysis (2025)](https://cset.georgetown.edu/publication/south-korea-ai-law-2025/) — Kore çerçeve analizi
