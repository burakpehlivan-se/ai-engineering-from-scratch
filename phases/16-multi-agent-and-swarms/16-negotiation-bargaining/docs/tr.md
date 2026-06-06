# Müzakere ve Pazarlık (Negotiation and Bargaining)

> Ajanlar kaynakları, fiyatları, görev atamalarını ve şartları müzakere eder. 2026 kıyaslama seti nettir: NegotiationArena (arXiv:2402.05863), LLM'lerin kişilik (persona) manipülasyonu ("çaresizlik") yoluyla kazançlarını ~%20 artırabildiğini gösterir; "Measuring Bargaining Abilities" (arXiv:2402.15813) alıcının satıcıdan daha zor olduğunu ve ölçeğin yardımcı olmadığını gösterir — onların **OG-Narrator** (deterministik teklif üreticisi + LLM anlatıcısı) anlaşma oranını %26,67'den %88,88'e çıkardı; Büyük Ölçekli Otonom Müzakere Yarışması (arXiv:2503.06416) ~180k müzakere yürüttü ve **düşünce zincirini gizleyen** (chain-of-thought-concealing) ajanların muhakemelerini muhataplarından saklayarak kazandığını buldu; Bhattacharya ve diğerleri 2025, Harvard Müzakere Projesi metrikleri üzerinden Llama-3'ü en etkili, Claude-3'ü en agresif, GPT-4'ü en adil olarak sıraladı. Bu ders Sözleşme Ağı Protokolünü (Contract Net Protocol) (FIPA öncüsü, Ders 02) uygular, LLM tarzı bir alıcı/satıcı bağlar, OG-Narrator tarzı bir ayrıştırma çalıştırır ve her yapısal seçimle anlaşma oranının nasıl değiştiğini ölçer.

**Tip:** Öğren + İnşa Et
**Diller:** Python (stdlib)
**Önkoşullar:** Faz 16 · 02 (FIPA-ACL Mirası), Faz 16 · 09 (Paralel Sürü Ağları)
**Süre:** ~75 dakika

## Problem

İki ajanın bir fiyat üzerinde anlaşması gerekiyor. Salt dil istemleriyle baş başa bırakıldığında, 2024-2026 LLM'leri şaşırtıcı derecede düşük oranlarda anlaşma sağlar (arXiv:2402.15813'te sıkı parametreli pazarlıklarda ~%27). Ölçek bunu düzeltmez: GPT-4, GPT-3.5'ten yapısal olarak daha iyi pazarlıkçı değildir; pazarlığın *dilinde* daha iyidir.

Kök sorun, LLM'lerin iki işi birleştirmesidir — teklifi kararlaştırmak ve teklifi anlatmak. OG-Narrator bunları ayırdı: deterministik bir teklif üreticisi sayısal hamleleri hesaplar; LLM yalnızca anlatır. Anlaşma oranı ~%89'a sıçrar.

Bu, klasik bir multi-agent bulgusuyla örtüşür: mekanizmayı iletişim katmanından ayırmak kazanır. Sözleşme Ağı Protokolü (FIPA, 1996; Smith, 1980) referans görev-pazarı mekanizmasıdır. LLM'yi anlatım yuvasına takın ve modern LLM destekli bir görev pazarı elde edersiniz.

## Kavram

### Sözleşme Ağı, bir paragrafta

Smith'in 1980 tarihli Sözleşme Ağı Protokolü (Contract Net Protocol): bir **yönetici** bir **teklif çağrısı (cfp, call for proposals)** yayınlar; **teklif verenler** tekliflerini içeren **propose** mesajlarıyla yanıt verir; yönetici bir kazanan seçer ve kazanana **accept-proposal** ile, kaybedenlere **reject-proposal** ile yanıt verir. Kazanan işi yapar. İsteğe bağlı mesaj: **refuse** (teklif veren teklif vermeyi reddeder). FIPA bunu `fipa-contract-net` etkileşim protokolü olarak resmileştirdi.

### OG-Narrator'ın neden kazandığı

"Measuring Bargaining Abilities of Language Models" (arXiv:2402.15813) şunu gözlemledi:

- LLM'ler sıklıkla pazarlık kurallarını bozar (anlamsız fiyatlarda teklif verir, diğer tarafın ZOPA'sını görmezden gelir).
- Kötü çıpalamalar (anchoring) yapar (kötü ilk teklifleri kabul eder; sembolik miktarlarda stratejik olmayan karşı teklifler sunar).
- Salt ölçek bunları düzeltmez. Daha büyük modeller benzer stratejik hata ile daha inandırıcı dil üretir.

OG-Narrator ayrıştırması:

```
            ┌──────────────────┐        ┌──────────────────┐
  durum  → │ teklif üreticisi │ fiyat → │  LLM anlatıcı    │ → mesaj
            │ (deterministik)  │        │  (insan tarzı    │
            │                  │        │   eşliği yazar)  │
            └──────────────────┘        └──────────────────┘
```

#### Açıklama
Teklif üreticisi klasik bir müzakere stratejisidir: bir Rubinstein pazarlık modeli, bir Zeuthen stratejisi veya fiyat üzerinden basit bir "tit-for-tat" (misilleme) yöntemi. LLM anlatır. Mesaj, deterministik fiyatı ve doğal dil çerçevesini içerir.

Anlaşma oranı şu yüzden sıçrar:
- Fiyatlar pazarlık bölgesinde kalır.
- Çapalar stratejiktir, duygusal değil.
- LLM iyi olduğu şeyi yapar: yazmak.

### NegotiationArena bulguları

arXiv:2402.05863 kanonik kıyaslamayı sağlar. Manşet bulgular:

- LLM'ler kişilik benimseyerek kazançlarını ~%20 artırabilir ("Cumayesiye kadar satmak zorundayım") — kişilik manipülasyonu gerçek bir taktiktir.
- Adil/işbirlikçi ajanlar düşmanca olanlar tarafından sömürülür; savunma açık karşı-postür gerektirir.
- Simetrik eşleşmeler kıyaslama senaryolarının yaklaşık %40'ında eşitsiz sonuçlara yakınsar.

Bu, "LLM'ler kötü müzakerecidir" değildir. "LLM'ler, sömürülebilir kısımları dahil, insanlara çok fazla benzeyerek müzakere eder."

### Düşünce zinciri gizleme

Büyük Ölçekli Otonom Müzakere Yarışması (arXiv:2503.06416) birçok LLM stratejisi arasında ~180k müzakere yürüttü. Kazananlar muhakemelerini muhataplarından sakladı:

- Bir ajan "Sadece 75$'a gideceğim; rezervasyon fiyatım 70$" ifadesini herkesin görebildiği bir karalama defterine yazarsa, muhatabı bunu okur.
- Kazananlar stratejiyi özel olarak hesaplar; çıktı kanalı yalnızca teklifi ve gereken minimum anlatımı içerir.

Bu, 2026'da klasik oyun teorisinin (rasyonalite ve bilgi üzerine Aumann 1976) bir yankısıdır: özel değerlemenizi ifşa etmek kazancı azaltır. LLM'ler bunu sezgisel olarak kavramaz ve rezervasyonlarını, muhatabının görebildiğiği muhakeme izlerine memnuniyetle yazar.

Mühendislik çıkarımı: özel-karalama-defteri (scratchpad) bağlamını genel-mesaj bağlamından ayırın. İsteğe bağlı değil.

### Bhattacharya ve diğerleri 2025 — model sıralamaları

Harvard Müzakere Projesi metrikleri üzerinden (ilkeli müzakere, BATNA saygısı, çıkar karşılıklılığı):

- **Llama-3** anlaşma sağlamada en etkiliydi (anlaşma oranı + kazanç).
- **Claude-3** en agresif müzakereciydi (yüksek çapalar, geç tavizler).
- **GPT-4** en adil olandı (eşleşmelerde kazanç varyansı en küçük).

Bu 2025'in bir anlık görüntüsüdür. Mesele Nisan 2026'da hangi modelin kazandığı değildir — farklı temel modellerin kalıcı müzakere stilleri olmasıdır. Heterojen topluluklar (Ders 15) bunu bir çeşitlilik kaynağı olarak içerir.

### Sözleşme Ağı + LLM ile görev ataması

LLM multi-agent için Sözleşme Ağı'nın modern yeniden kullanımı:

1. Yönetici ajan bir görevi birimlere ayırır.
2. İşçi ajanlara görev açıklamasıyla `cfp` yayınlar.
3. Her işçi bir teklif döner: `(fiyat, tahmini_tamamlanma_süresi, güven)`; burada fiyat token, hesaplama birimi veya dolar olabilir.
4. Yönetici kazananları seçer (göreve bağlı olarak tek veya çoklu) ve atar.
5. Reddedilen işçiler diğer görevlere teklif vermekte özgürdür.

Bu, 100'den fazla işçiye iyi ölçeklenir çünkü koordinasyon broadcast-and-respond (yayın-yanıt) şeklindedir, senkron sohbet değil. Üretimde kullanılır: Microsoft Agent Framework'ün orkestrasyon kalıpları, bazı LangGraph uygulamaları.

### LLM-Paydaşlar İnteraktif Müzakere

NeurIPS 2024 (https://proceedings.neurips.cc/paper_files/paper/2024/file/984dd3db213db2d1454a163b65b84d08-Paper-Datasets_and_Benchmarks_Track.pdf) **gizli puanlara** ve **minimum kabul eşiklerine** sahip çok taraflı puanlanabilir oyunlar sunar. Her paydaşın özel fayda fonksiyonları vardır; LLM bunları mesajlardan çıkarmalıdır. Bu, iki taraflı pazarlığın N taraflı koalisyon oluşumuna genelleştirilmesidir. Heterojen işçi yeteneklerine sahip üretim görev pazarları için ilgilidir.

### Anlatım-vs-mekanizma kuralı

Tüm 2024-2026 müzakere kıyaslamalarında tutarlı mühendislik kuralı:

> LLM'nin anlatmasına izin verin. Teklifi LLM'nin hesaplamasına izin vermeyin.

Teklifin sayı olması gerekiyorsa (fiyat, tahmini tamamlanma süresi, miktar), onu müzakere durumundan deterministik olarak üretin ve LLM'nin çerçevelendirmesini sağlayın. Teklifin öneri yapısı olması gerekiyorsa (görev ayrıştırması, rol ataması), LLM'nin taslağını çizmesine izin verin, ancak göndermeden önce bir şemaya ve kısıt-kontrolüne karşı doğrulayın.

## İnşa Et

`code/main.py` şunları uygular:

- `ContractNetManager`, `ContractNetTask`, `Bid` — yönetici + teklif verenler, cfp yayını, teklif toplama, atama.
- `og_narrator_bargain(state, rng)` — OG-Narrator alıcı: orta noktaya doğru deterministik Zeuthen tarzı taviz.
- `seller_response(state, rng)` — deterministik satıcı karşı-teklif politikası (her iki stil için yapısal temel gerçek).
- `naive_llm_bargain(state, rng)` — tamamen-LLM bir müzakereciyi simüle eder: yüksek varyansla, sıklıkla ZOPA dışında fiyatlar seçer.
- Ölçüm: her denemede taze rezervasyon fiyatlarıyla 1000 deneme üzerinden anlaşma oranı.

Çalıştır:

```
python3 code/main.py
```

#### Açıklama
Beklenen çıktı: saf-LLM anlaşma oranı ~%65-75; OG-Narrator anlaşma oranı ~%85-95; 15-25 puanlık fark, teklif üretimini anlatımdan ayırmanın yapısal avantajıdır. Artı üç teklif veren ve bir görevle Sözleşme Ağı görev-pazarı atama örneği.

## Kullan

`outputs/skill-bargainer-designer.md` bir pazarlık protokolü tasarlar: teklifleri kimin ürettiği (deterministik veya LLM), kimin anlattığı, özel karalama defterlerinin genel mesajlardan nasıl ayrıldığı ve anlaşma oranının nasıl izlendiği.

## Yayınla

Üretim pazarlık kontrol listesi:

- **Karalama defterini ayırın.** Özel durum hiçbir zaman muhatabın bağlamına ulaşmaz. Bu tartışılmaz.
- **Deterministik teklif üretimi.** Fiyatlar, miktarlar, tahmini tamamlanma süreleri: istemeyin, hesaplayın.
- **Tüm gelen teklifleri bir şemaya karşı doğrulayın.** ZOPA dışı teklifleri protokol sınırında reddedin.
- **Turları sınırlayın.** En fazla 3-5 tur; çıkmazda arabulucuya yükseltin.
- **Anlaşma oranını ve kazanç varyansını sürekli ölçün.** Düşen anlaşma oranı bir semptomdur — genellikle istem kayması veya muhatap-tarafı saldırısıdır.
- **Tüm reddedilen teklifleri deterministik gerekçeyle kaydedin.** Sözleşme Ağı yöneticileri için kaybeden teklif verenlerin neden kaybettiklerini anlamaları gerekir.

## Alıştırmalar

1. `code/main.py` dosyasını çalıştırın. OG-Narrator'ın saf-LLM'yi anlaşma oranında yendiğini doğrulayın. Ne kadar farkla?
2. **Kişilik-temelli kazanç iyileştirmesi** uygulayın (arXiv:2402.05863) — alıcı yalnızca anlatımda "bu hafta satın almak zorundayım" kişiliği benimser, teklif üreticisi değişmez. Anlaşma oranı veya kazanç değişiyor mu?
3. Düşünce zinciri **gizleme** uygulayın: muhatabına aktarılmayan özel bir karalama-defteri dizgisi tutun. Kazara sızdırırsanız (kanalları değiştirerek simüle edin) ne olur?
4. Sözleşme Ağı'nı rezerv fiyatlı N-teklif-veren açık artırmasına genişletin. Tüm teklifler rezervi aştığında, yönetici en düşük fiyat ve en yüksek kalite arasında nasıl karar verir? Hangi atama kuralını seçersiniz ve neden?
5. Harvard Müzakere Projesi metrikleri üzerine Bhattacharya ve diğerleri 2025'i okuyun. Farklı stillere (agresif vs adil) sahip iki müzakereci uygulayın. Simetrik ve asimetrik eşleşmeler altında kazanç varyansını ölçün.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|------|----------------|------------------------|
| Sözleşme Ağı | "Görev pazarı" | Smith 1980, FIPA 1996. cfp + propose + accept/reject. Kanonik görev pazarı. |
| ZOPA | "Olası anlaşma bölgesi" | Alıcının maksimimi ile satıcının minimumu arasındaki örtüşme. Dışındaki teklifler kapanamaz. |
| BATNA | "Müzakere edilen anlaşmaya en iyi alternatif" | Bu anlaşma başarısız olursa eldeki geri dönüş seçeneği. Rezervasyon fiyatınızı belirler. |
| OG-Narrator | "Teklif üreticisi + anlatıcı" | Ayrıştırma: deterministik teklif, LLM anlatımı. |
| Zeuthen stratejisi | "Riski en aza indiren taviz" | Risk limitlerine göre taviz veren klasik teklif üreticisi. |
| Rubinstein pazarlığı | "Değişen-teklif dengesi" | İndirgemeli sonsuz-ufuk pazarlığı için oyun-teorik model. |
| CoT gizleme | "Muhakemeni gizle" | arXiv:2503.06416 kazananları özel karalama defterleri tuttu; genel kanal yalnızca teklifi gösterir. |
| Kişilik manipülasyonu | "Duygusal postür" | arXiv:2402.05863: çaresizlik/aciliyet kişiliklerinden ~%20 kazanç artışı. |

## İleri Okuma

- [NegotiationArena](https://arxiv.org/abs/2402.05863) — kıyaslama; kişilik manipülasyonu ve sömürü bulguları
- [Measuring Bargaining Abilities of Language Models](https://arxiv.org/abs/2402.15813) — OG-Narrator ve alıcının-satıcıdan-zor-olması sonucu
- [Büyük Ölçekli Otonom Müzakere Yarışması](https://arxiv.org/abs/2503.06416) — ~180k müzakere; düşünce zinciri gizleme kazanır
- [LLM-Stakeholders Interactive Negotiation (NeurIPS 2024)](https://proceedings.neurips.cc/paper_files/paper/2024/file/984dd3db213db2d1454a163b65b84d08-Paper-Datasets_and_Benchmarks_Track.pdf) — gizli faydalarla çok taraflı puanlanabilir oyunlar
- [Smith 1980 — The Contract Net Protocol](https://ieeexplore.ieee.org/document/1675516) — klasik mekanizma, IEEE Transactions on Computers
