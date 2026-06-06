# Anthropic Sorumlu Ölçekleme Politikası v3.0

> RSP v3.0, 24 Şubat 2026'da yürürlüğe girdi ve 2023 politikasının yerini aldı. İki katmanlı azaltma: Anthropic'ın tek taraflı yapacakları ile endüstri çapında bir öneri olarak çerçevelendirilenler (RAND SL-4 güvenlik standartları dahil). Sınır Güvenlik Yol Haritaları (Frontier Safety Roadmaps) ve Risk Raporları (Risk Reports) bir kerelik teslimatlar yerine sürekli belgeler olarak eklenir. 2023 durma taahhüdü düşürülür. AI R&D-4 eşiği tanıtıldı: bir kez aşılırsa, Anthropic, uyumsuzluk (misalignment) risklerini ve azaltmaları tanımlayan olumlu bir vaka yayınlamak zorundadır. Claude Opus 4.6 bunu aşmaz. Anthropic, v3.0 duyurusunda "bunu güvenle dışarıda bırakmak zorlaşıyor" der. SaferAI, 2023 RSP'yi 2.2 olarak değerlendirdi; v3.0'ı 1.9'a düşürdü ve Anthropic'ı OpenAI ve DeepMind ile birlikte "zayıf" RSP kategorisine koydu. Nitel eşikler 2023 nicel taahhütlerinin yerini aldı; durma maddesinin kaldırılması en keskin gerilemedir.

**Tür:** Öğrenme
**Diller:** Python (stdlib, RSP eşiği karar motoru)
**Önkoşullar:** Faz 15 · 06 (Otomatik uyumluluk araştırması), Faz 15 · 07 (Öz iyileştirme)
**Süre:** ~45 dakika

## Sorun

Sınır laboratuvarları (frontier labs), kısmen teknik belgeler, kısmen yönetim belgeleri ve kısmen düzenleyicilere sinyaller olan ölçekleme politikaları yayınlar. RSP v3.0 mevcut Anthropic belgesidir. Bunu dikkatlice okumak önemli değildir çünkü uyması bağlayıcıdır (değildir); çerçeve, bir laboratuarın felaket riskini (catastrophic risk) nasıl kavradığını ve tavizleri halka nasıl ilettiğini şekillendirir.

v3.0 ile v2.0 farkı yararlı birimdir. Eklenen: Sınır Güvenlik Yol Haritaları, Risk Raporları, AI R&D-4 eşiği. Kaldırılan: 2023 durma taahhüdü. Yeniden çerçevelendirilen: Anthropic tek taraflı ve endüstri önerisi olarak ikiye bölünmüş iki katmanlı azaltma takvimi. Dış inceleme — SaferAI — notu 2.2'den (v2) 1.9'a (v3.0) düşürdü. Bir ölçekleme politikası daha parlak görünürken nasıl daha az titiz olabileceğinin yoludur bu.

## Kavram

### İki katmanlı azaltma takvimi

- **Anthropic tek taraflı eylemler:** diğer laboratuvarlar ne yaparsa yapsın Anthropic'ın yapacakları. Eşik üzerinde eğitim durdurma, belirli güvenlik önlemleri, belirli dağıtım kapıları.
- **Endüstri çapında öneriler:** Anthropic'ın endüstrinin toplu olarak yapması gerektiğini düşündükleri. RAND SL-4 güvenlik standartlarını içerir. Bunlar Anthropic tarafında taahhütler değildir; politika savunuculuğudur.

İki katmanlı yapı v2'de yoktu. Bu, okuyucunun her taahhüdün hangi sütunda olduğunu kontrol etmesi gerektiği anlamına gelir. "Endüstri çapında öneriler" sütunundaki bir güvenlik önlemi Anthropic'ın sözü değildir; Anthropic'ın umududur.

### AI R&D-4 eşiği

Bu, RSP v3.0'ın önemli bir sonraki eşik olarak adlandırdığı yetenek düzeyidir. Özellikle: rekabetçi maliyetle önemli bir AI araştırma fraksiyonunu otomatikleştirebilecek bir model. Anthropic bir modelin bunu aştığına inandığında, sürekli ölçeklemeden önce uyumsuzluk risklerini ve azaltmaları tanımlayan olumlu bir vaka yayınlamalıdır.

Claude Opus 4.6 v3.0 duyurusuna göre bunu aşmaz. Belge şunu ekler: "bunu güvenle dışarıda bırakmak zorlaşıyor." Bu ifade önemlidir; eşiklein canlı bir endişe olacak kadar yakın olduğunu kabul eder, spekülatif bir sınır olmadığını.

Ders 6 (Otomatik Uyumluluk Araştırması) ve Ders 7 (Öz İyileştirme) doğrudan bu eşik besler. Otomatik uyumluluk araştırmacılarının araştırma kalitesi bariyerlerini aşması, AI R&D-4 eşiğinin yaklaştığının kanıtıdır.

### Sınır Güvenlik Yol Haritaları ve Risk Raporları

v3.0 iki tür eseri sürekli belgelere yükseltir:

- **Sınır Güvenlik Yol Haritası:** planlanan güvenlik çalışması, yetenek beklentileri ve azaltma araştırması hakkında ileriye dönük belge.
- **Risk Raporu:** dağıtım sonrası belirli modeller hakkında geriye dönük belge, gözlemlenen yetenek ve artan riski tanımlar.

Her ikisi de herkese açıktır. Her ikisi de ilan edilmiş bir ritimle güncellenir. Yararlı olan: okuyucunun bir Yol Haritası'nda söylenenleri bir Risk Raporu'nda raporlananlarla karşılaştırabilmesidir.

### Durma maddesinin kaldırılması

2023 RSP, belirli yetenek eşiklerini aşarsa eğitimin azaltmalar yerinde olana kadar duracağına dair açık bir durma taahhüdü içeriyordu. v3.0, açık durmayı daha yumuşak bir formülasyonla değiştirir (olumlu bir vaka yayınla, azaltmalar yeterliyse devam et). SaferAI ve diğer analistler bunu doğrudan yeni belgedeki en güçlü gerileme olarak nitelendirdi.

Değişikliğin politika gerekçesi: 2023'teki nicel eşikler, karşılaştırma ölçütlerinin (benchmark) kendilerinin yeniden ölçeklenmesi nedeniyle 2026 dönemi yetenek karşılaştırmalarıyla ulaşılamaz çıktı. Karşıt argüman: bir ölçekleme politikasındaki durma maddesi bir taahhüt cihazıdır; kaldırmak politikanın güvenilirliğini kaldırır.

### SaferAI'ın düşürülmesi

Bağımsız bir kuruluş olan SaferAI, RSP tarzı belgeleri değerlendirir. Herkese açık notları: 2023 Anthropic RSP 2.2 puan aldı (4.0'ın en iyi mevcut RSP ve 1.0'ın nominal olduğu bir ölçekte). v3.0 1.9 puan aldı. Bu, Anthropic'ı "orta"dan "zayıfa" taşıdı ve OpenAI ve DeepMind ile birlikte zayıf kategoride yer almasını sağladı.

SaferAI'a göre düşürme faktörleri:
- Nitel eşikler nicellerin yerini aldı.
- Durma taahhüdü kaldırıldı.
- AI R&D-4 eşiği azaltmaları "olumlu vaka" olarak tanımlandı, belirli önlemler olarak değil.
- İnceleme mekanizmaları Anthropic'ın Güvenlik Danışma Grubuna (Safety Advisory Group) bağlı, sınırlı bağımsız gözetimle.

### Bu dersin olmadığı şey

Bu bir uyumluluk dersi değildir. RSP v3.0 bir düzenleme değildir; Anthropic'ı buna uymaya zorlayan hiçbir şey yoktur. Ders, belgeyi gerektiği titizlik ve şüphecilikle okumaktadır. Ölçekleme politikaları, sınır laboratuvarlarının felaket riski duruşu hakkında gönderdiği birincil herkese açık sinyallerdir. Bunları iyi okumak, sınır yeteneklerine bağlı çalışan herkes için pratik bir beceridir.

## Kullan

`code/main.py`, RSP eşik-değerlendirme biçimini yansıtan küçük bir karar motoru uygular: bir aday model ve bir dizi yetenek ölçümü verildiğinde, AI R&D-4 eşiğinin aşılıp aşılmadığını, gerekli olumlu vaka bölümlerini ve dağıtımın devam edip edemeyeceğini döndürür. Kasıtlı olarak basittir; nokta, belgenin mantığını açıkça ortaya koymaktır.

## Üret

`outputs/skill-scaling-policy-review.md`, bir ölçekleme politikasını (Anthropic, OpenAI, DeepMind veya dahili) v3.0 referansına göre inceler: iki katmanlı yapı, eşikler, durma taahhütleri, bağımsız inceleme.

## Alıştırmalar

1. `code/main.py` çalıştırın. Farklı yetenek düzeylerinde üç sentetik model besleyin. Eşik değerlendiricinin beklendiği gibi davrandığını ve doğru olumlu vaka şablonunu ürettiğini doğrulayın.

2. RSP v3.0'ı tam olarak okuyun (32 sayfa). "Endüstri çapında öneriler" katmanında yaşayan her taahhüdü belirleyin. Bunlardan hangileri v2'de "Anthropic tek taraflı" olurdu?

3. SaferAI'ın RSP değerlendirme metodolojisini okuyun. Belgeye karşı ölçütlerini uygulayarak v3.0 için 1.9 notunu yeniden üretin. Hangi ölçüt satırı düşürmeyi en çok tetikledi?

4. 2023 durma taahhüdü kaldırıldı. Politikanın güvenilirliğini korurken 2023 karşılaştırma ölçütü ölçekleme sorununu kabul eden bir alternatif taahhüt önerin.

5. RSP v3.0'ı OpenAI Hazırlık Çerçevesi v2 (Ders 20) ile karşılaştırın. v3.0'ın daha güçlü olduğu bir alan seçin. Hazırlık Çerçevesi'nin daha güçlü olduğu bir alan seçin.

## Anahtar Terimler

| Terim | Ne Söyleniyor | Aslında Ne Anlama Geliyor |
|---|---|---|
| RSP | "Anthropic'ın ölçekleme politikası" | Sorumlu Ölçekleme Politikası; v3.0 24 Şubat 2026'da yürürlükte |
| AI R&D-4 | "Araştırma otomasyon eşiği" | Rekabetçi maliyetle önemli bir araştırma fraksiyonunu otomatikleştirme yeteneği |
| Affirmative case (Olumlu vaka) | "Güvenlik gerekçesi" | Risklerin tanımlandığı ve azaltmaların yeterli olduğu yayınlanan argüman |
| Frontier Safety Roadmap (Sınır Güvenlik Yol Haritası) | "İleriye dönük plan" | Planlanan güvenlik çalışması ve beklenen yetenekler hakkında sürekli belge |
| Risk Report (Risk Raporu) | "Modelin geriye dönük incelemesi" | Dağıtım sonrası gözlemlenen yetenek ve artan risk hakkında sürekli belge |
| Two-tier mitigation (İki katmanlı azaltma) | "Tek taraflı vs endüstri" | Anthropic taahhütleri ile endüstri önerileri, ayrılmış |
| Pause commitment (Durma taahhüdü) | "2023 maddesi" | Eğitmenin duracağına dair açık promise; v3.0'da kaldırıldı |
| SaferAI rating (SaferAI notu) | "Bağımsız RSP notu" | Üçüncü taraf ölçütü; v3.0 1.9 puan aldı (v2 2.2 idi) |

## İleri Okuma

- [Anthropic — Sorumlu Ölçekleme Politikası v3.0](https://anthropic.com/responsible-scaling-policy/rsp-v3-0) — tam 32 sayfalık politika.
- [Anthropic — RSP v3.0 duyurusu](https://www.anthropic.com/news/responsible-scaling-policy-v3) — v2'den değişikliklerin özeti.
- [Anthropic — Sınır Güvenlik Yol Haritası](https://www.anthropic.com/research/frontier-safety) — RSP v3.0'dan bağlantılı sürekli belge.
- [Anthropic — Risk Raporu: Claude Opus 4.6](https://www.anthropic.com/research/risk-report-claude-opus-4-6) — mevcut sınır modeli hakkında geriye dönük inceleme.
- [Anthropic — Pratikte agent otonomunu ölçme](https://www.anthropic.com/research/measuring-agent-autonomy) — AI R&D-4'ü ölçülen otonomiye bağlar.
