# Paylaşılan Bellek ve Karatahta Kalıpları

> 2026 multi-agent sistemlerinde iki yaklaşım yan yana bulunur: **mesaj havuzu** (herkes herkesin mesajlarını görür, AutoGen GroupChat veya MetaGPT'te olduğu gibi) ve **abonelikli karatahta** (agent'lar ilgili olaylara abone olur, Context-Aware MCP veya Matrix çatısında olduğu gibi). İkisi de multi-agent sisteminin tek durum bilgisi olan kısmıdır — bu da ilginç hataların yaşadığı yer olduğu anlamına gelir. Referans başarısızlık modu **bellek zehirlenmesidir**: bir agent bir "gerçek" halüsinasyon yapar, diğer agent'lar onu doğrulanmış olarak ele alır ve doğruluk, anında çöküşten çok daha zor hata ayıklanan bir şekilde kademeli olarak bozulur. Bu ders her iki yapıyı da stdlib'den inşa eder, bir zehirlenme saldırısı enjekte eder ve üretimde gerçekten işe yarayan üç hafifletmeyi gösterir.

**Tür:** Öğren + İnşa Et
**Diller:** Python (stdlib, `threading`)
**Ön Koşullar:** Faz 16 · 04 (İlkel Model), Faz 16 · 09 (Paralel Swarm Ağları)
**Süre:** ~75 dakika

## Problem

Multi-agent sistemlerin agent'ların gerçekleri paylaşabileceği bir yere ihtiyacı vardır. Edebî bir seçenek "her şeyi mesajlarda geç"tir — ama bu paylaşılan durumu ekstra kopyalamayla yeniden icat eder. Başka biri "herkese küresel bir günlük ver"dir — ama küresel günlükler sınırsız büyür ve kolayca zehirlenir. Üçüncüsü "agent başına bir görünüm yansıt"tır — ölçeklenebilir ama şema-ağır.

Agent'lardan biri halüsinasyon yapıp halüsinasyonu paylaşılan duruma yazdığında, o durumu okuyan her aşağı yöndeki agent, halüsinasyonu gerçek olarak benimser. İnsan fark ettiğinde, akıl yürütme zinciri beş adım derinlikte ve kök neden, yazılmış üçüncü mesajdır. Multi-agent doğruluk bozulmasını hata ayıklamak, bir çöküşü hata ayıklamaktan daha zordur.

Bu bellek zehirlenmesidir. MAST taksonomisinde (Cemri ve diğerleri, arXiv:2503.13657) belgelenen en yaygın ikinci başarısızlık ailesidir ve yapısaldır: kaynak ve yazılamaz bir doğrulayıcı olmadan herhangi bir paylaşılan-bellek tasarımı sonunda onu sergileyecektir.

## Kavram

### İki ana topoloji

**Tam mesaj havuzu.** Her agent her mesajı okur. AutoGen GroupChat ve MetaGPT bunu kullanır. Basit, şeffaf, incelenebilir, ancak ~10 agent'tan ötesine ölçeklenmez çünkü her agent'ın bağlamı diğer agent'ların işiyle dolar.

```
agent-A ──write──▶ ┌────────────────┐ ◀──read── agent-D
                   │ mesaj havuzu   │
agent-B ──write──▶ │                │ ◀──read── agent-E
                   │ (küresel günlük)│
agent-C ──write──▶ └────────────────┘ ◀──read── agent-F
```

**Abonelikli karatahta.** Agent'lar konulara ilgi bildirir; alt katman yalnızca ilgili mesajları yönlendirir. CA-MCP (arXiv:2601.11595) ve Matrix merkezsiz çatısı (arXiv:2511.21686) bunu kullanır. Daha fazla ölçeklenir, ancak abonelikleri anlamlı kılmak için önceden şema tasarımı gerektirir.

```
                   ┌─ konu: fiyatlar ──┐
agent-A ──pub────▶ │                  │ ──▶ agent-D (abone)
                   ├─ konu: siparişler─┤
agent-B ──pub────▶ │                  │ ──▶ agent-E (abone)
                   ├─ konu: uyarılar  ┤
agent-C ──pub────▶ │                  │ ──▶ agent-F (abone)
                   └──────────────────┘
```

### Hangisi ne zaman kazanır

- **Tam havuz** agent'lar az (< 10), heterojen ve konuşma kısa vadeli olduğunda kazanır. Kimin ne söylediğini akıl yürütmek, herkes her şeyi gördüğünde önemsizdir.
- **Karatahta** agent'lar çok, rolde homojen ama örnekte çok sayıda (swarms) ve konuşma uzun ömürlü olduğunda kazanır. Yönlendirme, token maliyetini ve bağlam kirliliğini tasarruf eder.

Üretim sistemleri sıklıkla karıştırır: üstte küçük bir tam havuz (planlama katmanı), altta karatahtalar (işçi katmanı).

### Bellek zehirlenmesi, bir senaryoda

Üç agent bir araştırma görevinde çalışır. Agent A bir getirme (retrieval) agent'ıdır. Agent B bir özetleyicidir. Agent C bir analisttir.

1. A bir sayfayı getirir ve paylaşılan duruma bir mesaj yazar: "Çalışma %42 doğruluk iyileştirmesi bildiriyor."
2. Getirilen sayfa aslında "%4.2 iyileştirme" diyordu. A bir ondalık halüsinasyon yaptı.
3. B, paylaşılan durumu okuyarak şunu yazar: "Büyük %42 doğruluk kazancı bildirildi (kaynak: A)."
4. C, paylaşılan durumu okuyarak şunu yazar: "Benimsenmesi önerilir — %42'lik sıçrama dönüştürücü."
5. Son rapor, hiç var olmayan bir %42 sayısını alıntılar.

Hiçbir agent çökmedi. Hiçbir test başarısız olmadı. Sistem "çalıştı." Halüsinasyon, bir agent'ın bağlamından paylaşılan durum yoluyla her aşağı yöndeki agent'ın akıl yürütmesine geçti.

### Neden bu yapısaldır

Paylaşılan durum olmadan, A agent'ının halüsinasyonu A'nın bağlamında kalır. Aşağı yöndeki agent'lar yeniden getirir veya yeniden türetirdi ve hatayı yakalayabilirdi. Saf paylaşılan durumla, A'nın bağlamı herkesin bağlamı olur ve halüsinasyon gerçek olarak aklanır.

Sorunun kendisi paylaşılan durum değil — **kaynak ve bağımsız bir doğrulayıcı olmadan** paylaşılan durumdur. Bunu ele alan üç hafifletme:

1. **Her yazımda kaynağı (provenance) nitelendirin.** Paylaşılan durumdaki her giriş, onu kimin yazdığını, ne zaman, hangi prompt altında ve (varsa) agent'ın alıntıladığı kaynağı kaydeder. Aşağı yöndeki agent'lar, kaynağa anahtarlanmış bir şüphecilikle okur.
2. **Yazımları sürümleyin; onları yalnızca eklemeli (append-only) olarak ele alın.** Bir düzeltme, yeniden yerinde güncelleme değil, eskisinin yerini alan yeni bir giriştir. Denetim izi korunur.
3. **Paylaşılan duruma yazamayan en az bir agent tutun.** Bir salt okunur doğrulayıcı agent girişleri örnekler, kaynakları yeniden getirir ve tutarsızlıkları işaretler. Havuza yazamadığı için havuz tarafından zehirlenemez.

### Karatahta öncüsü (Hayes-Roth, 1985)

Karatahta kalıbı, LLM agent'larından dört on yıl önceye dayanır. Hayes-Roth (1985, "A Blackboard Architecture for Control"), küresel bir karatahtayı gözlemleyen, kısmi çözümler katkıda bulunan ve diğer kaynakları tetikleyen uzman Bilgi Kaynaklarını tanımladı. 2026 karatahtası (CA-MCP, Matrix), aynı kalıptır — Bilgi Kaynakları olarak LLM agent'ları ve kısmi çözümler olarak JSON blob'ları. Eski literatür, yazma çakışması, fırsatçı kontrol ve tutarlılık için modern sistemlerin yeniden keşfettiği belgelenmiş çözümlere sahiptir.

### Projeksiyon ve tam görünüm

Saf bir karatahta, her aboneye aynı projeksiyonu (konu kapsamlı) verir. Daha agresif bir tasarım **agent başına projeksiyondur**: her agent, rolüne özelleştirilmiş bir görünüm alır. LangGraph durum reducer'ları kanonik 2026 uygulamasıdır — reducer fonksiyonu, küresel durumu role özgü bir dilime katlar.

Agent başına projeksiyon daha fazla ölçeklenir, ancak bir şema gerektirir. Olmadan, her agent'ın promptunda ad-hoc projeksiyonu yeniden inşa edersiniz.

### Yazma çakışması kalıpları

Birden fazla agent'ın aynı anda yazması, sadece bir LLM problemi değil, bir eşzamanlılık problemidir. İşe yarayan üç kalıp:

- **Sıralı yazıcı (tek üretici).** Tüm yazımlar, yazanları serileştiren bir koordinatör agent'tan geçer. Basit, ama darboğaz.
- **Sürümlemeyle iyimser eşzamanlılık.** Her girişin bir sürümü vardır; yazarlar sürüm uyuşmazlığında başarısız olur ve yeniden dener. Klasik veritabanı tekniği.
- **Konu bölümleme.** Farklı agent'lar farklı konulara sahiptir. Konular arası çakışma yok. Tasarlanmış bölüm sınırları gerektirir.

Çoğu 2026 çatısı, LLM çağrıları çakışmanın nadir olduğu ve darboğazın acıtmadığı kadar yavaş olduğu için varsayılan olarak sıralı yazıcıya gelir.

### Yazılamaz doğrulayıcı

En yük taşıyıcı hafifletme, salt okunur doğrulayıcıdır. Uygulama kuralları:

- Doğrulayıcı, durumu takımla paylaşır (karathtayı veya havuzu okur).
- Doğrulayıcının paylaşılan duruma yazma tutamacı yoktur — yalnızca ayrı bir doğrulama kanalına yazabilir.
- Doğrulayıcı, yazımlarda alıntılanan kaynakları bağımsız olarak getirir. Anlaşmazlıkları işaretler.
- Doğrulayıcının kendi çıktıları bir insana veya ayrı bir karar agent'ına yönlendirilir, havuza asla geri beslenmez.

Bu ayrım olmadan, doğrulayıcının çıktıları havuzda yeni girişler haline gelir; bu, zehirli bir havuzun doğrulayıcıyı zehirlemesi ve doğrulamalarını zehirlemesi anlamına gelir.

## İnşa Et

`code/main.py` her iki topolojiyi stdlib Python'da artı oyuncak bir zehirlenme saldırısını ve üç hafifletmeyi uygular.

- `MessagePool` — tam okumalı iş parçacığı güvenli yalnızca-eklemeli günlük.
- `Blackboard` — agent başına aboneliklerle konu-anahtarlı pub/sub.
- `ProvenanceEntry` — her yazma (writer, timestamp, prompt_hash, source_uri) kaydeder.
- `PoisoningScenario` — A agent'ının bir ondalık halüsinasyon yaptığı üç-agent'lı bir araştırma görevi çalıştırır. Son raporu yazdırır.
- `Verifier` — kaynakları yeniden getiren ve tutarsızlıkları işaretleyen salt okunur bir agent. Doğrulayıcı mevcutken aynı senaryoyu çalıştırır.

Çalıştırın:

```
python3 code/main.py
```

Beklenen çıktı:
- 1. çalıştırma (doğrulayıcı yok): halüsinasyonlu %42 son rapora yayılır.
- 2. çalıştırma (doğrulayıcıyla): doğrulayıcı tutarsızlığı işaretler, havuz "işaretlendi" olarak etiketlenir, son rapor bir geri çekme içerir.

## Kullan

`outputs/skill-memory-auditor.md`, herhangi bir multi-agent sisteminin paylaşılan-bellek tasarımını kaynak, sürümleme ve doğrulayıcı ayrımı için denetleyen bir yetenektir. Üretimden önce yeni multi-agent mimarilerinde çalıştırın.

## Dağıt

Herhangi bir paylaşılan-bellek tasarımı için:

- Her yazımda kaynağı kaydedin: `(writer, timestamp, prompt_hash, tool_calls_cited, source_uri)`.
- Günlüğü yalnızca-eklemeli yapın. Düzeltmeler, yerine geçeni referans veren yeni girişlerdir.
- Bağımsız kaynak erişimli en az bir salt okunur doğrulayıcı agent dağıtın.
- Doğrulayıcı çıktısını ayrı bir kanala yönlendirin, paylaşılan havuza geri değil.
- Yerine geçenlerin oranını günlüğe kaydedin — yükselen oran, halüsinasyon kalıplarının erken kanıtıdır.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. 1. çalıştırmanın halüsinasyonu yaydığını ve 2. çalıştırmanın onu yakaladığını doğrulayın.
2. İkinci bir halüsinasyon ekleyin: B agent'ı bir veri kümesi boyutu uydurur. Doğrulayıcı, ikisi için elle ayarlanmadan ikisini de yakalamalıdır.
3. Tam havuzu konu bölümleriyle (`prices`, `summaries`, `analyses`) bir karathtaya değiştirin. Konu bölümleme hangi zehirlenme senaryolarını uygulamayı daha zor hale getirir ve hangilerine yardımcı olmaz?
4. Hayes-Roth'u (1985, "A Blackboard Architecture for Control") okuyun. 2026 sistemlerinin faydalanacağı, bu derste tartışılmayan iki kontrol kalıbını belirleyin.
5. CA-MCP'yi (arXiv:2601.11595) okuyun. Paylaşılan Bağlam Deposunu `code/main.py`'deki MessagePool veya Blackboard sınıfına eşleyin. CA-MCP üzerine hangi ilkelleri ekler?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Message pool (Mesaj havuzu) | "Paylaşılan sohbet geçmişi" | Her agent'ın okuduğu yalnızca-eklemeli günlük. Tam şeffaflık, zayıf ölçeklenme. |
| Blackboard (Karatahta) | "Paylaşılan çalışma alanı" | Konu-anahtarlı pub/sub. Agent'lar ilgili konulara abone olur. Daha fazla ölçeklenir. |
| Provenance (Kaynak) | "Kim neyi yazdı" | Her yazmadaki üst veri: yazar, zaman damgası, prompt, kaynaklar. |
| Memory poisoning (Bellek zehirlenmesi) | "Halüsinasyonlar yayılıyor" | Bir agent'ın hatası paylaşılan duruma girer, aşağı yöndeki agent'lar onu gerçek olarak benimser. |
| Append-only (Yalnızca-eklemeli) | "Yerinde güncelleme yok" | Düzeltmeler, eskisinin yerini alan yeni girişlerdir. Denetim izini korur. |
| Unwritable verifier (Yazılamaz doğrulayıcı) | "Bağımsız denetçi" | Kaynakları yeniden getiren ve tutarsızlıkları işaretleyen salt okunur agent. |
| Projection (Projeksiyon) | "Kapsamlı görünüm" | Küresel durumdan hesaplanan agent başına görünüm. LangGraph reducer'ları kanonik durumdur. |
| Knowledge Source (Bilgi Kaynağı) | "Uzman agent" | Hayes-Roth'un 1985'teki karatahta katılımcısı terimi. |

## İleri Okuma

- [Cemri ve diğerleri — Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657) — MAST taksonomisi; bellek zehirlenmesi bir koordinasyon-başarısızlık alt ailesidir
- [CA-MCP — Context-Aware Multi-Server MCP](https://arxiv.org/abs/2601.11595) — koordineli MCP sunucuları için Paylaşılan Bağlam Deposu
- [Matrix — merkezsiz multi-agent çatısı](https://arxiv.org/abs/2511.21686) — merkezi orkestratör olmadan mesaj kuyruğu tabanlı karatahta
- [LangGraph durumu ve reducer'ları](https://docs.langchain.com/oss/python/langgraph/workflows-agents) — üretimde agent başına projeksiyon kalıbı
- [Anthropic — Multi-agent araştırma sistemimizi nasıl inşa ettik](https://www.anthropic.com/engineering/multi-agent-research-system) — üretim dağıtımından kaynak ve doğrulama notları
