# Değerlendirme ve Koordinasyon Kıyaslamaları

> Beş 2025-2026 kıyaslaması multi-agent değerlendirme uzayını kapsar. **MultiAgentBench / MARBLE** (ACL 2025, arXiv:2503.01935) yıldız/zincir/ağaç/grafik topolojilerini kilometre-taşı KPI'ları ile değerlendirir; **araştırma için grafik en iyi**, bilişsel planlama ~%3 kilometre-taşı başarısı ekler. **COMMA** çok-modlu asimetrik-bilgi koordinasyonunu değerlendirir; GPT-4o dahil son teknoloji modeller rastgele bir temel çizgiyi yenmekte zorlanır. **MedAgentBoard** (arXiv:2505.12371) dört tıbbi görev kategorisini kapsar ve sıklıkla multi-agent'ın tek-LLM'ye baskın olmadığını bulur. **AgentArch** (arXiv:2509.10769) araç-kullanımı + bellek + orkestrasyonu birleştiren kurumsal ajan mimarilerini kıyaslar. **SWE-bench Pro** ([arXiv:2509.16941](https://arxiv.org/abs/2509.16941)) 41 repo boyunca 1865 probleme sahiptir; iş uygulamaları, B2B hizmetleri ve geliştirici araçlarını kapsar; ön-sınır modeller Verified'da %70+ vs Pro'da ~%23 alır — kirlilik üzerinde bir gerçeklik kontrolü. Claude Opus 4.7 (Nisan 2026) açık ajan-takımları koordinasyonuyla Pro'da **%64,3** bildirilmiştir (henüz Anthropic birincil kaynağı yayınlanmadı — ön-öncül olarak ele alın); Verdent (ajan iskelesi) Verified'da **%76,1 pass@1** alır ([Verdent teknik raporu](https://www.verdent.ai/blog/swe-bench-verified-technical-report)). **AAAI 2026 Köprü Programı WMAC** (https://multiagents.org/2026/) 2026 topluluk odak noktasıdır. Bu ders MARBLE'ın metrikleri üzerine inşa eder, bir topoloji-vs-metrik tarama çalıştırır ve "SWE-bench Verified'ı geçmek genelleştirme kanıtı değildir" kuralını sabitler.

**Tip:** Öğren
**Diller:** Python (stdlib)
**Önkoşullar:** Faz 16 · 15 (Oylama ve Tartışma Topolojisi), Faz 16 · 23 (Başarısızlık Kipleri)
**Süre:** ~75 dakika

## Problem

Bir makale "multi-agent sistemimiz daha iyi" iddia ettiğinde, soru şudur: neyden iyi, nerede, nasıl ölçülmüş? 2023-2024 döneminin multi-agent değerlendirmesi kaostu — herkes kendi metriklerini, kendi temel çizgilerini ve kendi görev setlerini seçti. 2025-2026 kıyaslamaları yapı dayattı.

Paylaşılan kıyaslamalar olmadan, iki multi-agent sistemini anlamlı biçimde karşılaştıramazsınız. Daha kötüsü, tutma-dışı kıyaslamalar olmadan, ön-sınır modeller kirlenebilir. SWE-bench Verified, 2025 ortası itibarıyla eğitim derlemlerinde kısmen kirlenmiş hale geldi; ön-sınır puanlar şişti; Pro kirlenmemiş bir gerçeklik kontrolü olarak tasarlandı.

Bu ders beş kanonik 2026 kıyaslamasını numaralandırır, her birinin neyi ölçtüğünü adlandırır ve kıyaslama iddialarını şüpheyle okumayı öğretir.

## Kavram

### MultiAgentBench (MARBLE) — ACL 2025

arXiv:2503.01935. Dört koordinasyon topolojisini (yıldız, zincir, ağaç, grafik) araştırma, kodlama ve planlama görevleri üzerinde değerlendirir. Kilometre-taşı-tabanlı KPI'lar yalnızca nihai başarı yerine kısmi ilerlemeyi izler.

Ölçülen sonuçlar:

- **Grafik** topolojisi araştırma senaryoları için en iyi; herhangi-birinden-herhangi-birine eleştiriyi destekler.
- **Zincir** adım-adım-iyileştirme kodlaması için en iyi.
- **Yıldız** hızlı-olgusal yoğunlaştırma için en iyi.
- **Koordinasyon vergisi** grafik üzerinde ~4 ajan sonrasında ortaya çıkar.
- **Bilişsel planlama** topolojiler arasında ~%3 kilometre-taşı başarısı ekler.

Şu durumda kullanın: koordinasyon topolojilerini elmalar-elmalara karşılaştırmak istediğinizde. MARBLE deposu (https://github.com/ulab-uiuc/MARBLE) değerlendiriciyi sağlar.

### COMMA — çok-modlu asimetrik bilgi

Ajanların farklı gözlem kiplerine sahip olduğu ve tam bilgi paylaşımı olmadan koordine olması gereken görevleri kapsar. Bildirilen sonuç rahatsız edicidir: GPT-4o dahil ön-sınır modeller COMMA'da ajan-ajan işbirliğinde **rastgele bir temel çizgiyi** yenmekte zorlanır. Sinyal, çok-modlu ajan kiplerinin yetersiz eğitildiği ve yetersiz değerlendirildiğidir — LLM'ler tek-modlu işbirliğini makul biçimde ele alır; çok-modlu koordinasyon çöker.

Şu durumda kullanın: sisteminiz çok-modlu veya asimetrik-bilgi koordinasyonuna sahip. COMMA'dan gelen sıfır sonucu, iddia etmeden önce ölçme konusunda bir uyarıdır.

### MedAgentBoard — alan stres testi

arXiv:2505.12371. Dört tıbbi görev kategorisi: teşhis, tedavi planlaması, rapor üretimi, hasta iletişimi. Multi-agent'ı tek-LLM'ye ve geleneksel kural-tabanlı sistemlere karşı karşılaştırır.

Bulgu: çoğu kategoride multi-agent tek-LLM'ye baskın DEĞİLDİR. Multi-agent avantajı dardır — görev ayrıştırma, alt görevler açıkça ayrılabilir olduğunda yardımcı olur (teşhis + tedavi); koordinasyon ek yükü uzmanlık kazancını aştığında zarar verir (rapor üretimi).

Şu durumda kullanın: alanınızın net kesilmiş tek-LLM temel çizgileri var. MedAgentBoard'ın dersi genelleşirse, önerilen birçok multi-agent sistemi aşırı mühendislik edilmiştir.

### AgentArch — kurumsal mimariler

arXiv:2509.10769. Araç kullanımı, bellek ve orkestrasyonun birlikte katmanlandığı kurumsal ayarlar. Kıyaslama, her katmanın katkısını izole eder: araç eklemek ne kadar yardımcı olur? Bellek eklemek? Çok-ajanlı orkestrasyon eklemek?

Şu durumda kullanın: kurumsal bir ajan yığını tasarlıyor ve her katmanı gerekçelendirmeniz gerekiyor. AgentArch, değerini ölçemeyeceğiniz özellikler satın almaktan kaçınmaya yardımcı olur.

### SWE-bench Pro — gerçeklik kontrolü

arXiv:2509.16941. İş uygulamaları, B2B hizmetleri ve geliştirici araçlarını kapsayan 41 repo boyunca 1865 problem. Sonraki eğitim kesim tarihleriyle **kirlenmemiş** olacak şekilde tasarlandı. Ön-sınır modeller Verified'da %70+ vs Pro'da ~%23 alır. Fark, kirlilik sinyalidir.

Nisan 2026 puanları:
- Claude Opus 4.7 Pro'da: **%64,3** (açık ajan-takımları koordinasyonuyla bildirilmiştir; henüz Anthropic birincil kaynağı yayınlanmadı — ön-öncül olarak ele alın).
- Verdent (ajan iskelesi) Verified'da: **%76,1 pass@1** ([teknik rapor](https://www.verdent.ai/blog/swe-bench-verified-technical-report)).
- Ajan iskelesi olmadan Pro'da ön-sınır ham puanlar: ~%23-35 ([SWE-bench Pro makalesi](https://arxiv.org/abs/2509.16941)).

Çıkarım: "SWE-bench Verified'ı yendik" artık yetenek kanıtı değil. Pro mevcut geçit testidir. Ajan-takımı iskelesi, Pro'da ölçülebilir kazanımlar üretir (~30-40 puan fark), bu da 2026'da çok-ajanlı koordinasyonun en güçlü deneysel argümanlarından biridir.

### AAAI 2026 WMAC

AAAI 2026 Köprü Programı — Çok-Ajanlı Koordinasyon Çalıştayı (https://multiagents.org/2026/). Çok-ajanlı AI araştırması için 2026 topluluk odak noktası. Kabul edilen makaleler ve çalıştay bildirileri, yeni yöntemleri değerlendirmek için kanonik yerdir; üretim kararları için WMAC-kabul edilmiş iddiaları arXiv ön baskılarına tercih edin.

### Kıyaslama iddialarını şüpheyle okuyun — 2026 kontrol listesi

Biri bir multi-agent sonucu iddia ettiğinde:

1. **Hangi kıyaslama, hangi dilim?** SWE-bench Verified vs Pro çok fark eder. Yanlış dilimde bildirilen bir sayı işe yaramaz.
2. **Kirlilik kontrolü.** Kıyaslama, modelin eğitim kesim tarihinden sonra mı yayınlandı? Değilse, dikkatle ele alın.
3. **Temel çizgi karşılaştırması.** Tek-LLM temel çizgisine, rastgeleye, önceki multi-agent çalışmalarına karşı. "Aynı sistemin ayarlanmamış sürümüne karşı" değil.
4. **İstatistiksel anlamlılık.** N deneme, p-değeri, güven aralığı. Ön-sınır modeller yüksek-varyanslıdır; tek koşum yanıltır.
5. **Görev çeşitliliği.** Bir görev mi, çok mu? Üretim için genelleştirme önemlidir.
6. **Maliyet açıklaması.** Görev başına token, duvar saati. %90 çözüm 20x maliyette bir iş kararıdır, bir yetenek iddiası değil.

### Hiçbir kıyaslamanın iyi ölçmediği şeyler

- **Uzun-ufuklu koordinasyon.** Duvar-saati etkileşim günleri. Tüm mevcut kıyaslamalar kısa çalışır.
- **Düşmanca dayanıklılık.** Bir ajan kötü niyetli veya ele geçirildiğinde ne olur?
- **Dağıtım altında kayma.** Kıyaslamalar statiktir; üretim dağılımları kayar.
- **Maliyet-normalleştirilmiş performans.** Çoğu kıyaslama ham doğruluk raporlar, dolar başına doğruluk değil.

Gerçekten önemsediğiniz eksen için kendi dahili kıyaslamanızı inşa etmek çoğu zaman doğru harekettir.

## İnşa Et

`code/main.py` etkileşimsiz bir yürüyüştür:

- Oyuncak bir görev üzerinde 3 multi-agent sistemi simüle eder.
- Her biri için MARBLE tarzı kilometre-taşı metrikleri hesaplar.
- Bir "eğitim" setinden görevleri tutarak bir kirlilik kontrolü çalıştırır.
- Rastgele bir temel çizgiye açıkça karşılaştırır.
- Bir kıyaslama-iddiaları puan kartı yazdırır.

Çalıştır:

```bash
python3 code/main.py
```

#### Açıklama
Beklenen çıktı: ham doğruluk, kilometre-taşı başarısı, görev başına maliyet, rastgele temel çizgi farkı ve bir kirlilik-kontrol notu içeren sistem puan kartı.

## Kullan

`outputs/skill-benchmark-reader.md` herhangi bir multi-agent kıyaslama iddiasını okur ve inceleme kontrol listesini uygular. Çıktı: bir not ve uyarılar.

## Yayınla

Üretim değerlendirme disiplini:

- **Gerçek üretim dağılımınızı yansıtan dahili bir kıyaslama inşa edin.** Genel kıyaslamalar bilgilendirir ama ikame etmez.
- **Her karşılaştırmaya rastgele bir temel çizgi dahil edin.** Bir koordinasyon görevinde rastgeleyi büyük bir farkla yenemiyorsanız, görev kötü konulmuş olabilir.
- **Doğrulukla birlikte maliyeti raporlayın.** Token maliyeti ve duvar saati. Ops ekiplerinin ikisine de ihtiyacı var.
- **Kıyaslamayı çeyrekte bir yeniden inşa edin.** Üretim dağılımı kayar; bayat kıyaslamalar yanıltır.
- **Yayınlanmış-kıyaslama aşırı-uyumundan kaçının.** Takımınız özellikle SWE-bench Pro sayıları için optimize ediyorsa, üretimde gerilersiniz.

## Alıştırmalar

1. `code/main.py` dosyasını çalıştırın. Simüle edilmiş üç sistemden hangisinin en iyi kilometre-taşı başına maliyete sahip olduğunu belirleyin. En yüksek ham-doğruluk sistemiyle eşleşiyor mu?
2. MultiAgentBench'i (arXiv:2503.01935) okuyun. Kendi görev alanınız için, MARBLE'ın dört topolojisinden hangisini önereceğine karar verin. Makalenin sonuçlarından gerekçelendirin.
3. SWE-bench Pro makalesini okuyun. Spesifik olarak onu kirliliğe-dayanıklı yapan nedir? Aynı teknik, sizin önemsediğiniz diğer kıyaslamalara uygulanabilir mi?
4. COMMA'nın çok-modlu koordinasyon bulgusunu okuyun. Dahili kıyaslamanıza ekleyebileceğiniz basit bir çok-modlu koordinasyon görevi tasarlayın. Ne yararlı bir sinyal sayılır?
5. Kıyaslama-iddiaları kontrol listesini son zamanlardaki bir multi-agent makalesinin manşet sonucuna uygulayın. İddiaya hangi notu verirsiniz?

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|------|----------------|------------------------|
| MARBLE | "MultiAgentBench" | ACL 2025; yıldız/zincir/ağaç/grafik topolojileri ve kilometre-taşı KPI'ları. |
| COMMA | "Çok-modlu kıyaslama" | Çok-modlu asimetrik-bilgi koordinasyonu; ön-sınır modeller rastgeleye karşı zorlanır. |
| MedAgentBoard | "Alan stres testi" | Dört tıbbi kategori; sıklıkla multi-agent tek-LLM'ye baskın olmaz. |
| AgentArch | "Kurumsal kıyaslama" | Araçlar + bellek + orkestrasyon katmanlı. |
| SWE-bench Pro | "Kirliliğe-dayanıklı" | 1865 problem, 41 repo; Verified'da %70+'a karşı ~%23 (kirlilik sinyali). |
| Kilometre-taşı başarısı | "Kısmi kredi" | Yalnızca nihai başarıyı değil, ilerlemeyi ödüllendiren kıyaslamalar. |
| Kirlilik | "Kıyaslama eğitime sızdı" | Yayınlandıktan sonra, kıyaslamalar eğitim derlemlerine kayar; puanlar şişer. |
| WMAC | "AAAI 2026 Köprü Programı" | Çok-Ajanlı Koordinasyon Çalıştayı; topluluk odak noktası. |

## İleri Okuma

- [MultiAgentBench / MARBLE](https://arxiv.org/abs/2503.01935) — kilometre-taşı KPI'larıyla topoloji kıyaslaması
- [MARBLE deposu](https://github.com/ulab-uiuc/MARBLE) — referans uygulama
- [MedAgentBoard](https://arxiv.org/abs/2505.12371) — alan stres testi; multi-agent sıklıkla baskın olmaz
- [AgentArch](https://arxiv.org/abs/2509.10769) — kurumsal ajan mimarileri
- [SWE-bench liderlik tabloları](https://www.swebench.com/) — ön-sınır modeller için Verified ve Pro puanları
- [AAAI 2026 WMAC](https://multiagents.org/2026/) — 2026 topluluk odak noktası
