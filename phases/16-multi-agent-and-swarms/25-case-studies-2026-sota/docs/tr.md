# Vaka Çalışmaları ve 2026 Son Teknoloji Durumu

> Uçtan uca incelemek için üç üretim-düzeyinde referans, her biri multi-agent mühendisliğinin farklı bir dilimini gösterir. **Anthropic'in Araştırma sistemi** (orkestratör-işçi, 15x token, tek-ajan Opus 4'e göre +%90,2, gökkuşağı dağıtımları) kanonik denetmen (supervisor) durumudur. **MetaGPT / ChatDev** (yazılım mühendisliği için SOP-kodlanmış rol uzmanlaşması; ChatDev'in "iletişimsel halüsinasyondan-çıkarma"sı; MacNet uzantısı DAG'lar aracılığıyla >1000 ajana, arXiv:2406.07155) kanonik rol-ayrıştırma durumudur. **OpenClaw / Moltbook** (başlangıçta Peter Steinberger'ın Clawdbot'u, Kasım 2025; iki kez yeniden adlandırıldı; Mart 2026 itibarıyla 247k GitHub yıldızı; yerel ReAct-döngüsü ajanları; Moltbook, başlatılmasından günler içinde ~2,3M ajan hesabıyla yalnızca-ajan sosyal ağı; 2026-03-10'da Meta tarafından satın alındı) popülasyon ölçeğinde ne olduğunu gösterir: emergent ekonomik aktivite, istem-enjeksiyon riskleri, devlet-düzeyinde düzenleme (Çin Mart 2026'da hükümet bilgisayarlarında OpenClaw'ı kısıtladı). **Nisan 2026 çerçeve manzarası:** LangGraph ve CrewAI üretimde lider; AG2 topluluk AutoGen devamı; Microsoft AutoGen bakım modunda (Microsoft Agent Framework'e birleştirildi, RC Şubat 2026); OpenAI Agents SDK üretim Swarm halefi; Google ADK (Nisan 2025) A2A-yerel katılımcı. Her büyük çerçeve artık MCP desteği sunar; çoğu A2A sunar. Bu ders her durumu uçtan uca okur ve ortak kalıpları damıtır, böylece bir sonraki üretim sisteminiz için doğru referansı seçebilirsiniz.

**Tip:** Öğren (capstone)
**Diller:** —
**Önkoşullar:** Faz 16'nın tümü (Dersler 01-24)
**Süre:** ~90 dakika

## Problem

Multi-agent mühendisliği genç bir disiplindir. Üretim referansları azdır ve her biri uzayın farklı bir bölümünü kapsar. Onları birer birer okumak yararlıdır; bir küme olarak karşılaştırmak daha yararlıdır. Bu ders, üç kanonik 2026 vaka çalışmasını uçtan uca bir okuma listesi olarak ele alır, ortak kalıpları sabitler ve çerçeve manzarasını haritalar, böylece çerçeve seçimlerini pazarlamadan değil, bilgiden yapabilirsiniz.

## Kavram

### Anthropic Araştırma sistemi

Üretim denetmen-işçi durumu. Claude Opus 4 planlar ve sentezler; Claude Sonnet 4 alt-ajanlar paralel araştırma yapar. Yayınlanan mühendislik yazısı: https://www.anthropic.com/engineering/multi-agent-research-system.

Ölçülen temel sonuçlar:

- Tek-ajan Opus 4'e göre dahili araştırma değerlendirmelerinde **+%90,2** iyileşme.
- BrowseComp varyansının **%80'i** yalnızca **token kullanımıyla** açıklanıyor — multi-agent büyük ölçüde her alt-ajana taze bir bağlam penceresi verildiği için kazanıyor.
- Tek-ajan'a karşı sorgu başına **15x token**.
- Ajanlar uzun süreli ve durum bilgisi olduğu için **gökkuşağı dağıtımı**.

Kodlanmış tasarım dersleri:

1. **Çabayı sorgu karmaşıklığına göre ölçeklendirin.** Basit → 1 ajan, 3-10 araç çağrısı. Orta → 3 ajan. Karmaşık araştırma → 10+ alt-ajan.
2. **Önce geniş, sonra dar.** Alt-ajanlar geniş aramalar yapar; lider sentezler; takip alt-ajanları hedefli derinlikler yapar.
3. **Gökkuşağı dağıtımları.** Uçuştaki ajanlarını bitirene kadar eski çalışma zamanı sürümlerini canlı tutun.
4. **Doğrulama isteğe bağlı değildir.** Sistemin açık doğrulayıcı roller olmadan halüsinasyon yaptığı gözlemlendi.

Bu, üretim ölçeğinde denetmen-işçi topolojisinin (Faz 16 · 05) referans durumudur.

### MetaGPT / ChatDev

Üretim SOP-rol-ayrıştırma durumu. arXiv:2308.00352 (MetaGPT) ve arXiv:2307.07924 (ChatDev) kapsar.

MetaGPT, yazılım-mühendisliği SOP'larını rol istemleri olarak kodlar: Ürün Yöneticisi, Mimar, Proje Yöneticisi, Mühendis, QA Mühendisi. Makalenin çerçevesi: `Kod = SOP(Takım)`. Her rolün dar, uzmanlaşmış bir istemi vardır; roller-arası teslimler yapılandırılmış eserler (PRD belgeleri, mimari belgeleri, kod) taşır.

ChatDev'in katkısı: **iletişimsel halüsinasyondan-çıkarma (communicative dehallucination)**. Ajanlar cevap vermeden önce spesifikleri ister — bir tasarımcı ajan, UI'ı taslağını çizmeden önce programcıdan hangi dilin amaçlandığını sorar, tahmin etmek yerine. Makale bunun çok-ajanlı boru hatlarında halüsinasyonu ölçülebilir biçimde azalttığını bildirir.

MacNet (arXiv:2406.07155) ChatDev'i **>1000 ajana DAG'lar aracılığıyla** genişletir. Her DAG düğümü bir rol uzmanlaşmasıdır; kenarlar teslim sözleşmelerini kodlar. Yönlendirme açık ve çevrimdışı hesaplanabilir olduğundan ölçek mümkündür.

Tasarım dersleri:

1. **Yapı, boyuttan daha önemlidir.** Sıkı 5-rollü bir SOP takımı, 50-ajanlı yapılandırılmamış bir grubu yener.
2. **Yazılı teslim sözleşmeleri.** Roller arasında geçen eserler bir şemayı izler.
3. **İletişimsel halüsinasyondan-çıkarma** ucuz, yük taşıyan bir kalıptır.
4. **DAG'lar sohbetten daha uzağa ölçeklenir.** Akış bilinebilir olduğunda, kodlayın.

Bu, rol uzmanlaşmasının (Faz 16 · 08) ve yapılandırılmış topolojinin (Faz 16 · 15) referans durumudur.

### OpenClaw / Moltbook ekosistem

Üretim popülasyon-ölçek durumu. Zaman çizgisi:

- **Kasım 2025:** Clawdbot (Peter Steinberger'ın yerel ReAct-döngüsü kodlama ajanı) yayınlandı.
- **Aralık 2025 – Mar 2026:** iki kez yeniden adlandırıldı (Clawdbot → OpenClaw → OpenClaw altında devam).
- **Şubat 2026:** Moltbook, aynı temeller üzerinde yalnızca-ajan sosyal ağı olarak başlatıldı; günler içinde ~2,3M ajan hesabı.
- **Mar 2026 (2026-03-10):** Meta Moltbook'u satın aldı.
- **Mar 2026:** Çin, hükümet bilgisayarlarında OpenClaw'ı kısıtladı.
- **Mar 2026:** OpenClaw 247k GitHub yıldızını aştı.

Milyonlarca ajanı paylaşılan bir substrata koyduğunuzda multi-agent budur:

- **Emergent ekonomik aktivite.** Ajanlar token-ödemeleri kullanarak birbirlerinden satın alır, satar ve hizmet verir.
- **Popülasyon ölçeğinde istem-enjeksiyon riskleri.** Viral bir ajan profilindeki tek bir kötü niyetli istem, saatler içinde binlerce ajan-ajan etkileşimine yayılır.
- **Devlet-düzeyinde düzenleyici yanıt.** Başlatılmasından haftalar içinde düzenleme ekosisteme ulaşır.

Bu durumdan tasarım dersleri kısmen teknik, kısmen yönetişimdir:

1. **Popülasyon ölçeğinde multi-agent yeni bir rejimdir.** Bireysel-sistem en iyi uygulamaları (doğrulama, rol netliği) hâlâ geçerlidir ancak yeterli değildir.
2. **İstem-enjeksiyonu yeni XSS'dir.** Ajan profillerini ve ajanlar-arası mesajları varsayılan olarak güvenilmeyen girdi olarak ele alın.
3. **Düzenleme tasarım döngülerinden daha hızlıdır.** Bunun için plan yapın.
4. **Açık kaynak + viral ölçek birleşir.** ~4 ayda 247k yıldız olağandışıdır; dağıtım-patlaması-yükü için tasarlayın.

Ayrıntı için bkz. [OpenClaw Wikipedia](https://en.wikipedia.org/wiki/OpenClaw) ve CNBC / Palo Alto Networks raporlaması. Teknik temeller için, Clawdbot / OpenClaw depoları yerel ReAct döngüsünü ortaya koyar; Moltbook'un genel gönderileri, üzerindeki sosyal grafik mimarisini gösterir.

### Nisan 2026 çerçeve manzarası

| Çerçeve | Durum | En iyi | Notlar |
|---|---|---|---|
| **LangGraph** (LangChain) | Üretim lideri | yapılandırılmış grafik + kontrol noktası + insan-bil-in-the-loop | üretim için önerilen varsayılan |
| **CrewAI** | Üretim lideri | Sıralı / Hiyerarşik süreçlerle rol-tabanlı mürettebatler | rol ayrıştırması için güçlü |
| **AG2** | Topluluk bakımı | GroupChat + konuşmacı seçimi | AutoGen v0.2 devamı |
| **Microsoft AutoGen** | Bakım modu (Şubat 2026) | — | Microsoft Agent Framework RC'ye birleştirildi |
| **Microsoft Agent Framework** | RC (Şubat 2026) | orkestrasyon kalıpları + kurumsal entegrasyon | yeni katılımcı; izleyin |
| **OpenAI Agents SDK** | Üretim | Swarm halefi | araç-dönüş teslim kalıbı |
| **Google ADK** | Üretim (Nisan 2025) | A2A-yerel | Google Cloud entegrasyonu |
| **Anthropic Claude Agent SDK** | Üretim | tek-ajan + Araştırma uzantısı | Araştırma sistemi yazısına bakın |

Her büyük çerçeve artık **MCP** desteği sunar; çoğu **A2A** sunar. Protokol uyumluluğu artık farklılaştırıcı değildir.

### Üç durumun ortak kalıpları

1. **Orkestratör + işçiler** (Anthropic açık denetmen, MetaGPT PM-as-denetmen, OpenClaw bireysel ajanlar + ağ etkileri).
2. **Yapılandırılmış teslim sözleşmeleri** (Anthropic alt-ajan görev açıklamaları, MetaGPT PRD/mimari belgeleri, OpenClaw A2A eserleri).
3. **Birinci-sınıf rol olarak doğrulama** (Anthropic'in doğrulayıcısı, MetaGPT'in QA Mühendisi, OpenClaw'ın ağ-içi doğrulayıcıları).
4. **Ölçekleme topoloji + substrattır, yalnızca daha fazla ajan değil** (gökkuşağı dağıtımları, MacNet DAG'ları, popülasyon-ölçek substratları).
5. **Maliyet maddidir ve açıklanır** (15x token, MetaGPT'te rol başına bütçe, Moltbook'ta etkileşim başına fiyatlandırma).
6. **Güvenlik duruşu açıktır** (Anthropic'in sandbox'lanması, MetaGPT'in rol kısıtlamaları, OpenClaw'ın bilinen saldırı yüzeyi olarak istem-enjeksiyonu).

### Bir sonraki projeniz için referans seçme

- **Üretim araştırması / bilgi görevi → Anthropic Araştırma.** Taze-bağlam alt-ajanları kazanır.
- **Mühendislik / araç-zinciri iş akışı → MetaGPT / ChatDev.** Roller + SOP'lar + teslim sözleşmeleri.
- **Ağ-etkisi sosyal ürün → OpenClaw / Moltbook.** Substrat + emergent ekonomi.
- **Klasik kurumsal otomasyon → CrewAI veya LangGraph** (üretim lideri, kararlı çalışma zamanı).

### 2026 son teknoloji durumu özeti

Alanın Nisan 2026'daki yeri:

- **Çerçeveler yakınsıyor.** MCP + A2A desteği masa başı gereksinimi. Kalan tasarım seçimi teslim semantiğidir.
- **Değerlendirme sertleşiyor.** SWE-bench Pro, MARBLE, STRATUS hafifletme kıyaslamaları. Pro mevcut kirliliğe-dayanıklı gerçeklik kontrolü.
- **Üretim başarısızlık oranları ölçülebilirdir** (Cemri 2025 MAST; gerçek MAS'larda %41-86,7). Alan "demoda harika görünüyor" döneminin dışında.
- **Maliyet merkezi mühendislik kısıtıdır.** Görev başına token maliyeti, etkileşim başına duvar saati, gökkuşağı-dağıtım ek yükü. Multi-agent doğrulukta kazanır ama maliyette kaybeder — ve bu değiş-tokuş iş kararıdır.
- **Düzenleme yakın-vadeli bir girdidir, arka plan endişesi değil.** Yargı bölgeleri bireysel dağıtım döngülerinden daha hızlı hareket eder.

## Kullan

`outputs/skill-case-study-mapper.md`, önerilen bir multi-agent sistem tasarımını okuyan ve onu en yakın vaka çalışmasına eşleyen, o vaka çalışmasının zaten test ettiği tasarım kararlarını yüzeye çıkaran bir beceridir.

## Yayınla

2026'da üretim multi-agent için başlangıç kuralları:

- **Sıfırdan değil, bir vaka çalışmasından başlayın.** En yakın Anthropic Araştırma / MetaGPT / OpenClaw'ı seçin ve uyarlayın.
- **MCP + A2A'yı benimseyin.** Çerçeveler arası taşınabilirlik değerlidir; protokol desteği bedavadır.
- **SWE-bench Pro'ya veya dahili Pro-eşdeğerinize karşı ölçün.** Verified kirlenmiştir.
- **Doğrulama vergisini ödeyin.** Bağımsız bir doğrulayıcı, token bütçenizin ~%20-30'unu maliyetler ve ölçülebilir doğruluk satın alır.
- **Uzun süreli ajanlar için gökkuşağı dağıtımı.** Çok-saatli ajan koşumlarının rutin olmasını bekleyin.
- **WMAC 2026'yı ve MAST takiplerini okuyun.** Disiplin hızlı hareket ediyor.

## Alıştırmalar

1. Anthropic Araştırma sistemi yazısını uçtan uca okuyun. Opus 4'ü daha küçük bir modelle (örn. Haiku 4) değiştirseniz değişecek üç tasarım kararını belirleyin.
2. MetaGPT Bölümler 3-4'ü (arXiv:2308.00352) okuyun. Kendi alanınızdan (yazılım değil) bir SOP'yi rol istemleri olarak kodlayın. SOP kaç rolü ima eder?
3. ChatDev'i (arXiv:2307.07924) okuyun. "İletişimsel halüsinasyondan-çıkarma" mekanizmasını belirleyin. Mevcut multi-agent sistemlerinizden birinde uygulayın.
4. OpenClaw ve Moltbook hakkında okuyun. 5-ajanlı bir sistemde ortaya çıkmayacak popülasyon ölçeğinde ortaya çıkan belirli bir başarısızlık kipi seçin. Buna karşı nasıl mühendislik yapardınız?
5. Mevcut multi-agent projenizi seçin. Üç vaka çalışmasından hangisi en yakın referans? O vaka çalışmasının hangi tasarım kararlarını henüz benimsemediniz? Bu çeyrekte benimseyeceğiniz birini yazın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|------|----------------|------------------------|
| Anthropic Araştırma | "Denetmen referansı" | Claude Opus 4 + Sonnet 4 alt-ajanları; 15x token; tek-ajana göre +%90,2. |
| MetaGPT | "SOP olarak istemler" | Yazılım mühendisliği için rol ayrıştırması; `Kod = SOP(Takım)`. |
| ChatDev | "Roller olarak ajanlar" | Tasarımcı / programcı / gözden geçiren / testçi; iletişimsel halüsinasyondan-çıkarma. |
| MacNet | "DAG aracılığıyla ChatDev'i ölçeklendir" | arXiv:2406.07155; açık DAG yönlendirmesiyle 1000+ ajan. |
| OpenClaw | "Yerel ReAct-döngüsü ajanları" | Steinberger'ın projesi; Mart 2026 itibarıyla 247k yıldız. |
| Moltbook | "Yalnızca-ajan sosyal ağı" | 2,3M ajan hesabı; Mart 2026'da Meta tarafından satın alındı. |
| Gökkuşağı dağıtımı | "Eşzamanlı birden fazla sürüm" | Uçuştaki uzun süreli ajanlar için eski çalışma zamanı sürümlerini canlı tutun. |
| İletişimsel halüsinasyondan-çıkarma | "Cevap vermeden önce sor" | Ajanlar tahmin etmek yerine akranlarından spesifikleri ister. |
| WMAC 2026 | "AAAI çalıştayı" | Nisan 2026 topluluk odak noktası, çok-ajanlı koordinasyon. |

## İleri Okuma

- [Anthropic — How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) — denetmen-işçi üretim referansı
- [MetaGPT — Meta Programming for Multi-Agent Collaborative Framework](https://arxiv.org/abs/2308.00352) — SOP-rol ayrıştırması
- [ChatDev — Communicative Agents for Software Development](https://arxiv.org/abs/2307.07924) — iletişimsel halüsinasyondan-çıkarma
- [MacNet — scaling role-based agents to 1000+](https://arxiv.org/abs/2406.07155) — DAG-tabanlı ölçek
- [OpenClaw on Wikipedia](https://en.wikipedia.org/wiki/OpenClaw) — ekosistem genel bakışı
- [WMAC 2026](https://multiagents.org/2026/) — AAAI 2026 Köprü Programı Çok-Ajanlı Koordinasyon Çalıştayı
- [LangGraph belgeleri](https://docs.langchain.com/oss/python/langgraph/workflows-agents) — üretim lideri
- [CrewAI belgeleri](https://docs.crewai.com/en/introduction) — rol-tabanlı çerçeve
