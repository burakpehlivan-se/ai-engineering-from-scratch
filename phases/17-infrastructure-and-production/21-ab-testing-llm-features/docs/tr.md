# LLM Özellikleri için A/B Testi — GrowthBook, Statsig ve "Hissetme" Problemi

> Geleneksel A/B testi deterministik-olmayan LLM'ler için inşa edilmedi. Kritik ayrım: değerlendirmeler (evals) "model işi yapabilir mi?" sorusuna yanıt verir. A/B testleri "kullanıcılar umursar mı?" sorusuna yanıt verir. İkisi de gereklidir; his üzerine göndermek (vibe checks) artık bitti. 2026'da ne test edilir: prompt mühendisliği (ifade), model seçimi (GPT-4 vs GPT-3.5 vs OSS; doğruluk vs maliyet vs gecikme), üretim parametreleri (sıcaklık, top-p). Gerçek vakalar: bir chatbot ödül-modeli varyantı +%70 konuşma uzunluğu ve +%30 tutma (retention) sağladı; Nextdoor AI konu-satırı deneyleri ödül fonksiyonu iyileştirmesinden sonra +%1 CTR sağladı; Khan Academy Khanmigo gecikme-vs-matematik-doğruluğu ekseninde yinelendi. Platform bölünmesi: **Statsig** (Eylül 2025'te OpenAI tarafından 1,1 milyar dolara satın alındı) — sıralı test, CUPED, hepsi-bir-arada. **GrowthBook** — açık kaynak, veri ambarı-native (warehouse-native), Bayesçi + Sıklıkçı + Sıralı motorlar, CUPED, SRM kontrolleri, Benjamini-Hochberg + Bonferroni düzeltmeleri. Depo-SQL tercihine ve "OpenAI tarafından satın alındı"nın kurumunuz için önemli olup olmadığına göre seçersiniz.

**Tür:** Öğren
**Diller:** Python (stdlib, basit sıralı test simülatörü)
**Önkoşullar:** Phase 17 · 13 (Gözlemlenebilirlik), Phase 17 · 20 (Kademeli Dağıtım)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Değerlendirmeleri ("model işi yapabilir") A/B testlerinden ("kullanıcılar umursar") ayırt edin.
- Üç test edilebilir ekseni (prompt, model, parametreler) sıralayın ve her biri için metrik seçin.
- CUPED, sıralı test ve Benjamini-Hochberg çoklu-karşılaştırma düzeltmelerini açıklayın.
- Depo-SQL duruşuna ve kurumsal satın alma tutumuna göre Statsig veya GrowthBook seçin.

## Problem

Bir sistem prompt'unu el ile ayarladınız. Daha iyi hissettiriyor. Gönderiyorsunuz. Dönüşüm (conversion) gürültüyle değişiyor. Metriği suçluyorsunuz. Ya da yeni bir model gönderdiniz ve dönüşüm hareket etmedi — model kötüleşti mi yoksa değişiklik algılanamayacak kadar küçük mü? Bilmiyorsunuz, çünkü A/B olmadan gönderdiniz.

Değerlendirmeler, modelin bir görevi etiketlenmiş bir set üzerinde yapıp yapamayacağını yanıtlar. Kullanıcıların çıktıyı tercih edip etmediğini yanıtlamaz. Bunu yalnızca kontrollü bir çevrimiçi deney yanıtlar, ve ancak deney yeterli güce (power) sahipse, determinizm-olmamayı kontrol ediyorsa ve çoklu karşılaştırmaları düzeltiyorsa.

## Kavram

### Değerlendirmeler vs A/B testleri

**Değerlendirmeler** — çevrimdışı, etiketlenmiş set, hakem (rubrik veya LLM-as-judge veya insan). Yanıt: "Çıktı bu sabit dağılımda doğru / yardımcı / güvenli mi?"

**A/B testi** — çevrimiçi, canlı kullanıcılar, rastgeleleştirilmiş. Yanıt: "Yeni varyant, önemli olan kullanıcı-düzey metriği hareket ettiriyor mu?"

İkisi de gereklidir. Değerlendirmeler maruz kalmadan önce gerilemeleri yakalar; A/B, maruziyetten sonra ürün etkisini onaylar.

### Ne test edilir

1. **Prompt mühendisliği** — ifade, sistem-prompt yapısı, örnekler. Metrik: görev başarısı, kullanıcı tutma, istek başına maliyet.
2. **Model seçimi** — GPT-4 vs GPT-3.5-Turbo vs Llama-OSS. Metrik: doğruluk (görev) + istek başına maliyet + gecikme P99. Çok-amaçlı.
3. **Üretim parametreleri** — sıcaklık, top-p, max_tokens. Metrik: göreve özgü (çıktı çeşitliliği vs determinizm).

### CUPED — varyans azaltma

Deney-Öncesi Veri Kullanan Kontrollü Deneyler (Controlled-experiments Using Pre-Experiment Data). Ön-dönem oynaklığını karşılaştırmadan önce gerileyin. Tipik varyans azaltma: %30-70. Etkin örneklem büyüklüğü bedavaya artar.

Uygulama: hem Statsig hem GrowthBook uygular.

### Sıralı test

Klasik A/B sabit örneklem büyüklüğü varsayar. Sıralı testler ("göz atıp karar verme") tekrarlanan bakışlar altında yanlış-pozitif oranını kontrol eder. Her-zaman-geçerli sıralı prosedürler (mSPRT, Howard'ın güven dizileri) net kazananlarda erken durmanızı sağlar.

### Çoklu-karşılaştırma düzeltmeleri

%95 güvenle 20 A/B testi çalıştırmak, şans eseri bir yanlış pozitif üretir. Bonferroni düzeltmesi test başına α'yı sıkılaştırır; Benjamini-Hochberg yanlış-keşif oranını kontrol eder. GrowthBook ikisini de uygular.

### SRM — örneklem oranı uyumsuzluğu

Atama karması kullanıcıları varyantlara rastgeleleştirir. 50/50 bölme 47/53 veriyorsa, bir şey kırılmıştır — SRM kontrolü işaretler. Her iki platform da uygular.

### Statsig vs GrowthBook

**Statsig**:
- OpenAI tarafından 1,1 milyar dolara satın alındı (Eylül 2025). Barındırılan, SaaS.
- Sıralı test, CUPED, ayrılmış popülasyonlar.
- Hepsi-bir-arada: özellik flag'leri + deneysellik + gözlemlenebilirlik.
- En uygun: ekip zaten paketlenmiş bir ürün istiyor, OpenAI sahipliğini umursamıyor.

**GrowthBook**:
- Açık kaynak (MIT); veri ambarı-native (Snowflake/BigQuery/Redshift'ten doğrudan okur).
- Birden çok motor: Bayesçi, Sıklıkçı, Sıralı.
- CUPED, SRM, Bonferroni, BH düzeltmeleri.
- Kendi-kurulum veya yönetilen bulut.
- En uygun: veri ambarı-SQL ekibi, veri ekibi metrik katmanını kontrol ediyor, OSS istiyor.

### Determinizm-olmama gücü karmaşıklaştırır

Aynı prompt değişen çıktılar üretir. Geleneksel güç hesaplamaları IID (Bağımsız ve Özdeş Dağılımlı) gözlemler varsayar. LLM determinizm-olmama ile, etkin örneklem büyüklüğü nominalden düşüktür. Gerekli örneklem büyüklüğünü güvenlik marjı olarak ~1,3-1,5 katla çarpın.

### Gerçek vaka sonuçları

- Chatbot ödül modeli varyantı: +%70 konuşma uzunluğu, +%30 tutma.
- Nextdoor konu satırları: ödül fonksiyonu iyileştirmesinden sonra +%1 CTR.
- Khan Academy Khanmigo: yinelemeli gecikme-vs-matematik-doğruluğu takası.

### Anti-kalıp: his üzerine göndermek

Her kıdemli mühendis, "daha iyi hissettiriyor" diye gönderilen ve ekibin aylarca fark etmediği ürün metriklerini gerileten bir özelliği adlandırabilir. A/B, zorlayıcı işlevdir.

### Hatırlamanız gereken sayılar

- Statsig OpenAI tarafından satın alındı: 1,1 milyar $, Eylül 2025.
- GrowthBook: açık kaynak MIT; Bayesçi + Sıklıkçı + Sıralı.
- CUPED varyans azaltma: %30-70.
- LLM determinizm-olmama → +%30-50 örneklem-büyüklüğü arabelleği.

## Kullanım

`code/main.py`, sabit ve sıralı sınırlarla sıralı bir A/B testini simüle eder. Sıralının erken nasıl durmanıza izin verdiğini gösterir.

## Yaygınlaştırma

Bu ders `outputs/skill-ab-plan.md` üretir. Özellik değişikliği, iş yükü, taban çizgisi verildiğinde, platform, geçitler, örneklem büyüklüğü seçer.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. %3 dönüşüm taban çizgisiyle beklenen %5'lik artış için, %80 güce örneklem büyüklüğü nedir?
2. Sağlık-düzenlenmiş şirket-içi müşteri için Statsig veya GrowthBook seçin.
3. GPT-4 vs GPT-3.5'i maliyet-başına-çözülen-bilet üzerinde test eden bir A/B tasarlayın. Birincil metrik, koruma metriği (guardrail), ikincil nedir?
4. Kanaryanız geçiyor ama A/B -%1,2 dönüşüm gösteriyor. Gönderir misiniz? Yükseltme ölçütlerini yazın.
5. Ön-dönemde varyansın %60'ı sonrası olan bir kupede CUPED uygulayın. Etkin-örneklem-büyüklüğü artışını hesaplayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|----------------------|---------------|
| Değerlendirme | "çevrimdışı test" | Model yeteneğinin etiketlenmiş-set değerlendirmesi |
| A/B testi | "deney" | Kullanıcılar üzerinde canlı rastgeleleştirilmiş karşılaştırma |
| CUPED | "varyans azaltma" | Varyansı azaltmak için ön-dönem gerilemesi |
| Sıralı test | "göz at-ok testi" | Erken durmaya izin veren her-zaman-geçerli prosedür |
| Çoklu karşılaştırma | "aile hatası" | Birçok test çalıştırmak yanlış pozitifleri şişirir |
| Bonferroni | "sıkı düzeltme" | α'yı test sayısına böl |
| Benjamini-Hochberg | "BH FDR" | Yanlış-keşif-oranı kontrolü, daha az muhafazakâr |
| SRM | "kötü bölme" | Örneklem oranı uyumsuzluğu; atama hatası |
| Statsig | "OpenAI sahipli" | Ticari hepsi-bir-arada, 2025'te satın alındı |
| GrowthBook | "OSS olanı" | MIT veri ambarı-native platform |
| mSPRT | "sıralı olasılık oran testi" | Klasik sıralı prosedür |

## Ek Okuma

- [GrowthBook — AI'ı A/B Test Etme](https://blog.growthbook.io/how-to-a-b-test-ai-a-practical-guide/)
- [Statsig — Prompt'ların Ötesinde: Veri Odaklı LLM Optimizasyonu](https://www.statsig.com/blog/llm-optimization-online-experimentation)
- [Statsig vs GrowthBook karşılaştırması](https://www.statsig.com/perspectives/ab-testing-feature-flags-comparison-tools)
- [Deng ve diğerleri — CUPED](https://www.exp-platform.com/Documents/2013-02-CUPED-ImprovingSensitivityOfControlledExperiments.pdf)
- [Howard — Güven Dizileri](https://arxiv.org/abs/1810.08240)
