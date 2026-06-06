# Uyumluluk — SOC 2, HIPAA, GDPR, PCI-DSS, AB AI Yasası, ISO 42001

> Çok-çerçeve kapsamı, 2026 kurumsal anlaşmaları için masa başına alınan bir bedeldir. **AB AI Yasası**: 1 Ağustos 2024'ten beri yürürlükte. Yüksek-risk gereksinimlerinin çoğu 2 Ağustos 2026'da yürürlüğe girer. Yüksek-risk-sistem yükümlülükleri için cezalar €15M veya küresel yıllık cironun %3'üne kadar (Madde 99(4)); yasaklanmış AI uygulamaları için €35M veya %7'ye kadar (Madde 99(3)). AB kullanıcılarına hizmet veriliyorsa küresel olarak geçerlidir. **Colorado AI Yasası**: 30 Haziran 2026'da yürürlüğe girer (SB25B-004 ile Şubat 2026'dan ertelendi) — yüksek-risk sistemler için etki değerlendirmeleri, AI kararlarına itiraz hakkı. Virginia, kredi/istihdam/konut/eğitim için benzer. **SOC 2 Type II**: fiili B2B AI gereksinimi (fintech için Type I değil, Type II). **GDPR**: belgelenen en büyük AI-özgü ceza, Clearview AI'ye karşı €30,5M (Hollanda DPA, Eylül 2024); İtalya'nın Garante'si OpenAI'ya karşı €15M verdi (Aralık 2024, Mart 2026'da temyizde bozuldu). Çıkarım anında gerçek-zamanlı PII sansürleme savunulabilir standarttır; işlem-sonrası temizlik yeterli değildir. **HIPAA**: sağlık bağlı — PHI'yi BAA olmadan harici AI hizmetlerine gönderemez. **PCI-DSS**: AI-etkileşim-katmanı kapsamı otomatik değil, yapılandırma + sözleşmesel anlaşmalar gerektirir. **ISO 42001**: yükselen AI yönetişim standardı, ISO 27001 ile birlikte büyüyen tedarik gereksinimi. Referans profili: OpenAI, SOC 2 Type 2, ISO/IEC 27001:2022, ISO/IEC 27701:2019, GDPR/CCPA/HIPAA (BAA)/FERPA, ChatGPT ödeme bileşenleri için PCI-DSS sürdürür. Çapraz-çerçeve eşleme denetim yorgunluğunu azaltır: erişim kontrolleri ISO 27001 A.5.15-5.18, GDPR Madde 32, HIPAA §164.312(a) arasında eşlenir.

**Tür:** Öğren
**Diller:** (Python isteğe bağlı — uyumluluk politika + süreçtir, kod değil)
**Önkoşullar:** Phase 17 · 25 (Güvenlik), Phase 17 · 13 (Gözlemlenebilirlik)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- LLM ürünleri için ilgili yedi 2026 çerçevesini sıralayın ve her birini bir müşteri segmentiyle eşleştirin.
- AB AI Yasası yürürlük zaman çizgisini (Ağustos 2024'te yürürlükte; Ağustos 2026'da yüksek-risk yürürlüğü) ve iki katmanlı ceza tavanını (yüksek-risk yükümlülükleri için €15M / %3, yasaklanmış uygulamalar için €35M / %7) alıntılayın.
- İşlem-sonrası PII temizliğinin GDPR için neden yeterli olmadığını ve gerçek-zamanlı çıkarım-katmanı sansürlemeyi savunulabilir standart olarak açıklayın.
- Çapraz-çerçeve kontrol eşlemeyi açıklayın (ör. erişim kontrolü, ISO 27001 A.5.15-5.18 + GDPR Madde 32 + HIPAA §164.312(a) ile eşlenir).

## Problem

Kurumsal bir müşterinin tedarik bölümü SOC 2 Type II, GDPR, HIPAA BAA, ISO 27001 ve "AB AI Yasası uyumluluk beyanı" istiyor. Ekibinizde SOC 2 Type I var. Type II'den altı ay uzaksınız ve GDPR Madde 30 kayıtlarına başlamadınız.

Çok-çerçeve kapsamı bir LLM sorunu değildir — kurumsal-SaaS sorunudur, LLM'ye özgü katmanlarla. 2026'da tedarik ekipleri, çerçeve başına bir satır ve kontrol başına bir sütun içeren bir matris ister, PDF değil.

## Kavram

### Yedi çerçeve

| Çerçeve | Kapsam | LLM'ye özgü gereksinim |
|---------|--------|------------------------|
| SOC 2 Type II | B2B SaaS taban çizgisi | 6-12 ay boyunca denetlenen süreç kontrolleri |
| HIPAA | ABD sağlık | BAA gerekli; PHI imzalanmış anlaşma olmadan altyapıdan ayrılamaz |
| GDPR | AB kullanıcıları | Gerçek-zamanlı PII sansürleme; veri özne hakları; Madde 30 kayıtları |
| PCI-DSS | Ödeme verisi | Ödemeye dokunan AI için yapılandırma + sözleşmeler |
| AB AI Yasası | AB kullanıcılarına hizmet | Risk katmanı sınıflandırması; yüksek-risk sistemler: uygunluk değerlendirmesi, dokümantasyon, günlükleme |
| Colorado AI Yasası | CO sakinlerine hizmet | Etki değerlendirmeleri; itiraz hakkı |
| ISO 42001 | AI yönetişimi | Yükselen; ISO 27001 ile eşleşir |

### AB AI Yasası zaman çizgisi

- 1 Ağustos 2024: yürürlükte.
- 2 Şubat 2025: yasaklanmış-AI uygulamaları yürürlükte.
- 2 Ağustos 2026: yüksek-risk sistemleri yürürlükte (uygunluk değerlendirmesi, dokümantasyon, günlükleme).
- Ağustos 2027: uyumlaştırılmış mevzuat kapsamındaki ürünlerdeki yüksek-risk sistemleri.

Risk katmanları: Kabul edilemez (yasak), Yüksek-risk (uygunluk + günlükleme), Sınırlı-risk (şeffaflık), Minimal-risk (kısıtlama yok). Çoğu B2B LLM SaaS sınırlı-risk'tir; yüksek-risk, istihdam, kredi, eğitim, kolluk kuvvetleri, göç ve temel hizmetler için devreye girer.

Cezalar (Madde 99): yüksek-risk-sistem yükümlülüklerinin ihlali için €15M veya küresel yıllık cironun %3'üne kadar (Madde 99(4)); yasaklanmış AI uygulamaları için €35M veya %7'ye kadar (Madde 99(3)); hangisi yüksekse.

### GDPR — gerçek-zamanlı sansürleme standarttır

İşlem-sonrası temizlik (LLM gördükten sonra PII'yi sansürle) savunulabilir bir duruş değildir — model veriyi zaten gördü. Gerçek-zamanlı çıkarım-katmanı sansürleme 2026 standardıdır:

- LLM çağrısından önce varlık tanıma.
- Tutarlı tokenizasyon (Mesh yaklaşımı) semantiği korur.
- Yalnızca sansürlenmiş prompt'ları ve onaylanmış opt-in ham olanları saklayın.

Son yaptırımlar: Clearview AI'ye karşı €30,5M (Hollanda DPA, Eylül 2024) bugüne kadarki en büyük belgelenen AI-özgü GDPR cezasıdır; OpenAI'ya karşı €15M (İtalya'nın Garante'si, Aralık 2024) en büyük LLM-özgü cezadır, ancak Mart 2026'da temyizde bozulmuştur ve karar daha fazla inceleme altındadır. İşlem-sonrası iddialar denetimde başarısız oldu.

### HIPAA — BAA isteğe bağlı değildir

PHI'yi imzalanmış İş Ortağı Anlaşması olmadan harici AI hizmetlerine gönderemezsiniz. Üç hyperscaler LLM platformu (Bedrock, Azure OpenAI, Vertex) BAA sunar. Doğrudan OpenAI API BAA sunar. Doğrudan Anthropic API BAA sunar. PHI göndermeden önce onaylayın.

### SOC 2 Type II

Type I: kontroller tasarlanmış ve belgelenmiş.
Type II: kontroller 6-12 ay boyunca etkili çalışır.

2026'da B2B tedarik varsayılan olarak Type II'dir. Type I başlangıçtır; Type II geçittir.

Yaygın denetim sürücüleri: erişim günlükleri (kim ne gördü), değişiklik yönetimi (nasıl dağıtıldı), risk değerlendirmeleri (çeyreklik), olay müdahalesi (test edildi mi?). Phase 17 · 25'ten denetim günlüğü doğrudan yeniden kullanılabilir.

### Çapraz-çerçeve eşleme

Bir erişim kontrolü politikası, birden çok çerçeve kontrolünü karşılar:

| Kontrol | Çerçeveler |
|---------|-----------|
| Erişim günlükleme | ISO 27001 A.5.15-5.18, GDPR Madde 32, HIPAA §164.312(a) |
| Değişiklik yönetimi | ISO 27001 A.8.32, PCI DSS Req. 6, HIPAA ihlal bildirimi kapsamı |
| Aktarımdaki şifreleme | ISO 27001 A.8.24, GDPR Madde 32, HIPAA §164.312(e) |
| Sır yönetimi | ISO 27001 A.8.19, PCI DSS Req. 8, SOC 2 CC6.1 |

Uyumluluk araçları (Drata, Vanta, Secureframe) bu eşlemeyi otomatikleştirir. Ölçekte maliyete değer.

### ISO 42001 — yükselen

2023 sonunda yayınlandı. ISO 27001 ile birlikte büyüyen tedarik gereksinimi. Risk yönetimi, veri kalitesi, şeffaflık, insan gözetimi dahil AI yönetişimi için çerçeve.

### OpenAI'nin referans profili

OpenAI, SOC 2 Type 2, ISO/IEC 27001:2022, ISO/IEC 27701:2019, GDPR/CCPA/HIPAA (BAA)/FERPA, ChatGPT ödeme bileşenleri için PCI-DSS sürdürür. Bu kabaca 2026'daki kurumsal masa başına alınan bedellerdir.

### Hatırlamanız gereken sayılar

- AB AI Yasası cezaları: yüksek-risk yükümlülükleri için €15M / %3'e kadar (Madde 99(4)); yasaklanmış uygulamalar için €35M / %7'ye kadar (Madde 99(3)).
- AB AI Yasası yüksek-risk yürürlüğü: 2 Ağustos 2026.
- En büyük belgelenen AI-özgü GDPR cezası: €30,5M, Clearview AI (Hollanda DPA, Eylül 2024).
- En büyük LLM-özgü GDPR cezası: €15M, OpenAI (İtalya'nın Garante'si, Aralık 2024; Mart 2026'da temyizde bozuldu).
- SOC 2 Type II penceresi: 6-12 ay çalıştırılan kontroller.
- Colorado AI Yasası yürürlük tarihi: 30 Haziran 2026 (SB25B-004 ile Şubat 2026'dan ertelendi).

## Kullanım

`code/main.py` Python'da uyumluluk-eşleme elektronik tablosudur — bir kontrol verildiğinde, karşıladığı çerçeveleri listeler.

## Yaygınlaştırma

Bu ders `outputs/skill-compliance-matrix.md` üretir. Müşteri segmenti ve coğrafya verildiğinde, gerekli çerçeveleri ve kontrolleri belirtir.

## Alıştırmalar

1. İlk kurumsal müşteriniz SOC 2 Type II, HIPAA BAA, AB AI Yasası beyanı gerektiriyor. Anlaşmayı kazanmak için minimum uygulanabilir uyumluluk duruşu nedir?
2. Üç varsayımsal LLM ürününü AB AI Yasası risk katmanları altında sınıflandırın. Yüksek-risk'te ne değişir?
3. BAA olmadan bir sağlayıcıya yanlışlıkla PHI gönderdiniz. Olay müdahalesi boyunca yürüyün.
4. ISO 42001'in orta-pazar bir AI satıcısı için 2026'da "gerekli" olup olmadığını tartışın.
5. LLM denetim günlüğü alanlarınızı (Phase 17 · 25) en az üç çerçeve kontrolüyle eşleyin.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|----------------------|---------------|
| SOC 2 Type II | "denetlenen kontroller" | 6-12 ay boyunca çalışan, bağımsız doğrulanmış kontroller |
| HIPAA BAA | "sağlık sözleşmesi" | İş Ortağı Anlaşması; PHI için gerekli |
| GDPR | "AB gizliliği" | Gerçek-zamanlı PII sansürleme, 2026 savunulabilir standarttır |
| AB AI Yasası | "AB AI kuralları" | Yüksek-risk yürürlüğü Ağustos 2026; €15M / %3 (yüksek-risk yükümlülükleri) — €35M / %7 (yasaklanmış uygulamalar) |
| Colorado AI Yasası | "ABD AI eyalet yasası" | 30 Haziran 2026 yürürlükte (SB25B-004 ile ertelendi); etki değerlendirmeleri |
| ISO 42001 | "AI yönetişimi" | AI riski + şeffaflık için yükselen çerçeve |
| ISO 27001 | "güvenlik ISMS" | Bilgi Güvenliği Yönetim Sistemi taban çizgisi |
| Uygunluk değerlendirmesi | "AB AI doküman paketi" | Yüksek-risk gereksinimi: dokümanlar, test, günlükleme |
| Çapraz-çerçeve eşleme | "tek kontrol, birçok çerçeve" | Tek politika birden çok çerçeve kontrolünü karşılar |

## Ek Okuma

- [OpenAI Güvenlik ve Gizlilik](https://openai.com/security-and-privacy/) — referans uyumluluk profili.
- [GuardionAI — LLM Uyumluluk 2026: ISO 42001, AB AI Yasası, SOC 2, GDPR](https://guardion.ai/blog/llm-compliance-guide-iso-42001-eu-ai-act-soc2-gdpr-2026)
- [Dsalta — SOC 2 Type 2 Denetim Kılavuzu 2026: 10 AI Kontrolü](https://www.dsalta.com/resources/ai-compliance/soc-2-type-2-audit-guide-2026-10-ai-powered-controls-every-saas-team-needs)
- [AB AI Yasası resmi metin](https://eur-lex.europa.eu/eli/reg/2024/1689/oj) — birincil kaynak.
- [Colorado AI Yasası](https://leg.colorado.gov/bills/sb24-205) — birincil kaynak.
- [ISO/IEC 42001:2023](https://www.iso.org/standard/81230.html) — AI yönetim sistemi standardı.
