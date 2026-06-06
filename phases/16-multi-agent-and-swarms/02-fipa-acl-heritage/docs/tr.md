# FIPA-ACL Mirası ve Söz Edimleri (Speech Acts)

> MCP'den önce, A2A'dan önce, FIPA-ACL vardı. 2000'de IEEE Foundation for Intelligent Physical Agents (FIPA — Akıllı Fiziksel Ajanlar Vakfı), yirmi performative (icra edici söz), iki içerik dili ve bir dizi etkileşim protokolü — contract net (sözleşme ağı), subscribe/notify (abone ol/bildir), request-when (istendiğinde talep et) — ile bir agent iletişim dilini onayladı. Web için ontoloji yükü çok ağır olduğundan endüstride gözden düştü, ancak multi-agent sistemlerinin LLM rönesansı aynı fikirleri biçimsel semantik olmadan sessizce yeniden uyguluyor: JSON sözleşmeleri performative'lerin, doğal dil ontolojilerin yerini alıyor. Bu ders FIPA-ACL'yi ciddiye alarak, 2026 protokol kararlarının hangilerinin yeniden icat, hangilerinin yenilik olduğunu ve mevcut dalganın 2000'lerin çoktan çözdüğü sorunları nereden yeniden keşfedeceğini göstermeyi amaçlıyor.

**Tür:** Öğren
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 16 · 01 (Neden Multi-Agent)
**Süre:** ~60 dakika

## Problem

2026 agent protokolü manzarası kalabalık: araçlar için MCP, agent'lar için A2A, kurumsal denetim için ACP, merkezsiz güven için ANP, doğal dil içerik için NLIP, artı CA-MCP ve düzinelerce araştırma önerisi. Her spesifikasyon kendini temel olarak sunuyor.

Dürüst okuma şudur: çoğu çok spesifik yirmi yıllık bir karar ağacını yeniden keşfediyor. Austin (1962) ve Searle (1969)'dan gelen söz edimi teorisi (speech act theory) bize "ifadeler eylemdir" dedirtti. KQML (1993) bunu bir kablo protokolüne dönüştürdü. FIPA-ACL (2000'de onaylandı) referans standardizasyonu üretti: yirmi performative, SL0/SL1 içerik dilleri, contract-net ve subscribe-notify için etkileşim protokolleri. JADE ve JACK Java referans platformlarıydı. Çaba ontoloji yükü çok ağır olduğu ve web kazandığı için 2010 civarında söndü.

MCP'nin `tools/call`'ına, A2A'nın görev yaşam döngüsüne veya CA-MCP'nin paylaşılan bağlam deposuna baktığınızda, FIPA kararlarının daha yumuşak, JSON-yerli bir yeniden harmanlanmasına bakıyorsunuz. Mirası bilmek size iki şey söyler: yeni "inovasyon"lardan hangileri aslında yeniden icat, ve yeni spesifikasyonların hangi eski başarısızlık modlarını yeniden keşfedeceği.

## Kavram

### Söz Edimleri, bir paragrafta

Austin bazı cümlelerin dünyayı tanımlamadığını — onu değiştirdiğini fark etti. "Söz veriyorum." "Talep ediyorum." "Beyan ediyorum." Bunlara performative ifadeler (icra edici söylemler) adını verdi. Searle bunu beş kategoriye formelleştirdi: assertive (bildiren), directive (yönlendiren), commissive (taahhüt eden), expressive (ifade eden), declarative (beyan eden). KQML (Finin ve diğerleri, 1993) bunu yazılım agent'ları için operasyonel hale getirdi: bir mesaj bir performative (eylem) artı içerik (eylemin ne hakkında olduğu) içerir. FIPA-ACL, KQML'nin boşluklarını doldurdu ve yirmi performative etrafında standardizasyon sağladı.

### Yirmi FIPA performative'i (kısmi liste)

| Performative | Niyet |
|---|---|
| `inform` | "Sana P'nin doğru olduğunu söylüyorum" |
| `request` | "Senden X'i yapmanı istiyorum" |
| `query-if` | "P doğru mu?" |
| `query-ref` | "X'in değeri nedir?" |
| `propose` | "X'i yapmayı öneriyorum" |
| `accept-proposal` | "Öneriyi kabul ediyorum" |
| `reject-proposal` | "Öneriyi reddediyorum" |
| `agree` | "X'i yapmayı kabul ediyorum" |
| `refuse` | "X'i yapmayı reddediyorum" |
| `confirm` | "P'nin doğru olduğunu teyit ediyorum" |
| `disconfirm` | "P'yi inkâr ediyorum" |
| `not-understood` | "Mesajın ayrıştırılamadı" |
| `cfp` | "X için teklif çağrısı" |
| `subscribe` | "X değiştiğinde beni bilgilendir" |
| `cancel` | "Devam eden X'i iptal et" |
| `failure` | "X'i denedim ve başarısız oldum" |

Tam liste `fipa00037.pdf` (FIPA ACL Message Structure) içindedir. Mesele bunları ezberlemek değil — mesele her birinin sonunda bir LLM protokolünün yeniden ekleyeceği bir primitive karşılık gelmesidir.

### Kanonik FIPA-ACL mesajı

```
(inform
  :sender       agent1@platform
  :receiver     agent2@platform
  :content      "((price IBM 83))"
  :language     SL0
  :ontology     finance
  :protocol     fipa-request
  :conversation-id   conv-42
  :reply-with   msg-17
)
```

Yedi alan protokol zarfını (envelope) taşır; bir alan (`content`) yükü (payload) taşır. Kalan alanlar, her seferinde retry, threading ve ontolojiyi bir JSON protokolüne bağlarken yeniden icat ettiğiniz şeylerdir.

### İki eski platform

**JADE** (Java Agent DEvelopment framework, 1999–2020'ler) en çok kullanılan FIPA-uyumlu runtime'dı. Agent'lar bir temel sınıfı extend eder, ACL mesajları değiş tokuş eder, konteynerlerin içinde çalışır ve "behaviors" kullanarak koordine olurdu. Etkileşim protokolü kütüphanesi contract-net, subscribe-notify, request-when ve propose-accept ile birlikte geliyordu.

**JACK** (Agent Oriented Software, ticari) FIPA mesajlarının üzerinde BDI (Belief-Desire-Intention — İnanç-Arzu-Niyet) akıl yürütmesini vurguladı. Daha biçimsel, daha az benimsenmiş.

Web stack'i multi-agent kullanım durumlarını yutunca ikisi de düşüşe geçti. MCP ve A2A, 2026'nın runtime "konteyner"leridir.

### FIPA Neden Söndü

- **Ontoloji yükü.** FIPA, `content`'i ayrıştırmak için paylaşılan bir ontoloji gerektiriyordu. Ontolojilerde anlaşmak yıllar süren bir standartlar sürecidir. Web sadece HTTP + JSON kullandı.
- **Kimsenin kullanmadığı biçimsel semantik.** SL (Semantic Language — Anlamsal Dil) titiz doğruluk koşulları veriyordu, ancak çoğu üretim sistemi serbest biçimli içerik kullanıp biçimciliği görmezden geldi.
- **Araç kilitlenmesi.** JADE yalnızca Java'ydı; JACK ticariydi. Çok dilli takımlar ikisinin de etrafından dolaştı.
- **İnternet stack'i kazandı.** REST, sonra JSON-RPC, sonra gRPC, ACL'nin taşıma katmanının (transport) yerini aldı.

### LLM Rönesansı FIPA-Lite

Bir FIPA `request`'ini bir MCP `tools/call`'ı ile karşılaştırın:

```
(request                                {
  :sender  agent1                         "jsonrpc": "2.0",
  :receiver tool-server                   "method":  "tools/call",
  :content "(lookup stock IBM)"           "params":  {"name":"lookup_stock",
  :ontology finance                                   "arguments":{"symbol":"IBM"}},
  :conversation-id c42                    "id": 42
)                                        }
```

Aynı zarf, farklı sözdizimi. İkisi de taşır: kim, kime, niyet, yük, korelasyon kimliği. Biri diğerinin üzerinde devrim değil — aynı tasarım üzerinde farklı ödünleşimlerdir.

Liu ve diğerlerinin 2025 taraması ("A Survey of Agent Interoperability Protocols: MCP, ACP, A2A, ANP", arXiv:2505.02279) bu soy çizgisini açık hale getirir: MCP araç-kullanım söz edimlerine, A2A agent-eş söz edimlerine, ACP denetim izi söz edimlerine, ANP merkezsiz kimlik uzantılarına karşılık gelir. Yeni spesifikasyonlar JSON sözdizimi ve gevşek semantiği olan ACL torunlarıdır.

### Ödünleşim, açıkça ifade edildi

**FIPA'nın size verdiği ve modern spesifikasyonların düşürdüğü:**

- Biçimsel semantik — `inform`'un göndericinin içeriğe inandığını ima ettiğini kanıtlayabilirsiniz
- Performative'lerin kanonik bir kataloğu — "bir `cancel`imiz olmalı mı?"yı yeniden tartışmanıza gerek yok
- Onlarca yıllık etkileşim protokolü kalıpları — contract-net, subscribe-notify, propose-accept — bilinen doğruluk özellikleriyle

**Modern spesifikasyonların size verdiği ve FIPA'nın vermediği:**

- Her modern araçla uyumlu JSON-yerli yükler
- LLM'lerin elle kodlanmış bir ontoloji olmadan yorumlayabildiği doğal dil içeriği
- Web stack taşıma katmanı (HTTP, SSE, WebSocket)
- Kendini tanımlayan belgelerle yetenek keşfi (MCP `listTools`, A2A Agent Card)

Daha kolay uygulama için daha gevşek niyet semantiği. Ödün tam olarak budur.

### Taşınmaya değer etkileşim protokolleri

FIPA yaklaşık 15 etkileşim protokolüyle geldi. LLM multi-agent sistemlerine taşımaya değer üçü var:

1. **Contract Net Protokolü (CNP).** Yönetici `cfp` (teklif çağrısı) yayınlar; teklif verenler `propose` ile yanıt verir; yönetici kabul/red eder. Bu kanonik görev-pazarı kalıbıdır (Faz 16 · 16 Müzakere).
2. **Subscribe/Notify.** Abone `subscribe` gönderir; yayıncı konu her değiştiğinde `inform` gönderir. Bu 2026'daki her event-bus'tur.
3. **Request-When.** "Y koşulu tuttuğunda X'i yap." Ön koşullarla gecikmeli eylem. 2026'daki karşılığı dayanıklı iş akışı motorlarındaki ertelenmiş görevlerdir (Faz 16 · 22 Üretim Ölçeklendirme).

Her biri modern mesaj kuyruklarına, HTTP + polling'e veya SSE streaming'e temiz şekilde eşlenir.

### Ontolojiyi düşürdüğünüzde ne kırılır

Paylaşılan ontoloji olmadan, agent'lar anlamı doğal dil içerikten çıkarır. Belgelenmiş 2026 başarısızlık modu **anlamsal sürüklenmedir (semantic drift)**: iki agent aynı kelimeyi (`"customer"`) örtüşmeyen derecede farklı kavramlar için kullanır, alıcı agent yanlış yoruma göre hareket eder, hiçbir şema doğrulayıcısı bunu yakalamaz. FIPA'nın ontoloji gerekliliği mesajı ayrıştırma zamanında reddederdi.

Tam ontolojiye gitmeden hafifletmeler:

- `content` üzerinde JSON Schema — yapısal hataları tel üzerinde reddeder
- Tipli yapıtlar (A2A) — yanlış modaliteyi reddeder
- Zarfta açık performative — içerik doğal dil olduğunda bile niyeti belirsizlikten kurtarır

### 2026 spesifikasyonları, söz edimi mirasına eşlenmiş

| Modern spesifikasyon | FIPA karşılığı | Koruduğu | Düşürdüğü |
|---|---|---|---|
| MCP `tools/call` | `request` | açık niyet, korelasyon kimliği | biçimsel semantik, ontoloji |
| MCP `resources/read` | `query-ref` | açık niyet, korelasyon kimliği | biçimsel semantik |
| A2A görev yaşam döngüsü | contract-net + request-when | eşzamansız yaşam döngüsü, durum geçişleri | biçimsel tamlık garantileri |
| A2A streaming olayları | subscribe/notify | eşzamansız itme | tipli yüklem aboneliği |
| CA-MCP paylaşılan bağlam | blackboard (Hayes-Roth 1985) | çok yazarlı paylaşılan bellek | mantıksal tutarlılık modeli |
| NLIP | doğal dil içerik | LLM-yerli | şema |

Tabloyu yukarıdan aşağıya okuduğunuzda, kalıp şudur: yapısal primitive'i koru, biçimciliği düşür, belirsizliği LLM'lerin örtmesine izin ver.

## İnşa Et

`code/main.py`, salt stdlib bir FIPA-ACL çevirmeni uygular. Kanonik ACL zarfını kodlar ve kodunu çözer ve her MCP / A2A mesaj şeklinin aynı yedi alana nasıl indirgendiğini gösterir. Demo:

- Beş MCP tarzı ve A2A tarzı mesajı FIPA-ACL olarak kodlar.
- FIPA-ACL'yi modern karşılığına geri kodunu çözer.
- Bir yönetici ile üç teklif veren arasında `cfp`, `propose`, `accept-proposal`, `reject-proposal` kullanarak oyuncak bir Contract Net müzayedesi çalıştırır.

Çalıştırın:

```
python3 code/main.py
```

Çıktı, her modern mesajı hem 2026 JSON biçiminde hem de FIPA-ACL biçiminde yan yana gösteren bir iz, ardından bir contract-net teklifinin gidiş-dönüşüdür. Aynı protokol primitive'leri gidiş-dönüşü atlatır; yalnızca sözdizimi farklıdır.

## Kullan

`outputs/skill-fipa-mapper.md`, herhangi bir agent protokolü spesifikasyonunu okuyan ve FIPA-ACL eşlemesini üreten bir yetenektir. Yeni bir protokolü benimsemeden önce şunu yanıtlamak için kullanın: "Bu gerçekten yeni mi, yoksa JSON sözdizimli bir `inform` mı?"

## Dağıt

FIPA-ACL'yi geri getirmeyin. Onun kontrol listesini geri getirin:

- Her mesajın niyet primitive'i (performative) nedir?
- İstek-yanıt ve iptal için bir korelasyon kimliği var mı?
- Açık bir içerik dili var mı (JSON-RPC, düz metin, yapılandırılmış tipli yapıt)?
- Etkileşim protokolleri birinci sınıf mı, yoksa contract-net'i sıfırdan mı yeniden uyguluyorsunuz?
- İki agent içerik anlamı konusunda anlaşamazsa ne olur (anlamsal sürüklenme)?

Yeni bir protokolü üretime göndermeden önce bu beş soruyu belgelendirin.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Gidiş-dönüş kodlamasını gözlemleyin. `tools/call`, `resources/read` ve A2A görev oluşturma'ya hangi FIPA performative'inin karşılık geldiğini belirleyin.
2. Contract-net demosunu, yöneticinin teklif ortasında görevi geri çekmesine izin veren bir `cancel` performative'i ile genişletin. `cancel`'in tek başına retry'lerin çözmediği hangi başarısızlık durumunu çözdüğünü açıklayın.
3. FIPA ACL Message Structure (http://www.fipa.org/specs/fipa00037/) bölüm 4.1–4.3'ü okuyun. Bu derste ele alınmayan bir performative seçin ve modern JSON-RPC karşılığını açıklayın.
4. Liu ve diğerleri, arXiv:2505.02279'u okuyun. MCP, A2A, ACP, ANP'nin her biri için, korudukları ve düşürdükleri FIPA performative ailelerini listeleyin.
5. Kendi sisteminizde bir `request` performative'inin `content` alanı için minimal bir JSON-Schema tasarlayın. Bu şema size saf doğal dilin vermediği neyi veriyor, bedeli ne?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Speech act (Söz edimi) | "Bir şey yapan ifade" | Austin/Searle: eylem olarak ifadeler. ACL'nin kuramsal ebeveyni. |
| FIPA | "O eski XML şeyi" | IEEE Foundation for Intelligent Physical Agents. 2000'de ACL'yi standartlaştırdı. |
| ACL | "Agent İletişim Dili" | FIPA'nın zarf biçimi: performative + içerik + üst veri. |
| Performative | "Yüklem" | Mesajın niyet sınıfı: `inform`, `request`, `propose`, `cfp` vb. |
| KQML | "FIPA'nın öncüsü" | Knowledge Query and Manipulation Language (1993). Daha basit, daha dar. |
| Ontology (Ontoloji) | "Paylaşılan kelime hazinesi" | İçerik dilinin konuştuğu kavramların biçimsel tanımı. |
| SL0 / SL1 | "FIPA içerik dilleri" | Semantic Language seviye 0 ve 1 — biçimsel içerik dili ailesi. |
| Contract Net | "Görev pazarı" | Yönetici cfp yayınlar; teklif verenler önerir; yönetici kabul eder. Kanonik etkileşim protokolü. |
| Interaction protocol (Etkileşim protokolü) | "Mesaj kalıbı" | Bilinen doğruluğa sahip bir performative dizisi: request-when, subscribe-notify vb. |

## İleri Okuma

- [Liu ve diğerleri — A Survey of Agent Interoperability Protocols: MCP, ACP, A2A, ANP](https://arxiv.org/html/2505.02279v1) — modern spesifikasyonları FIPA mirasına bağlayan kanonik 2025 taraması
- [FIPA ACL Message Structure Specification (fipa00037)](http://www.fipa.org/specs/fipa00037/) — 2000'de onaylanan zarf biçimi
- [FIPA Communicative Act Library Specification (fipa00037)](http://www.fipa.org/specs/fipa00037/) — tam performative kataloğu
- [MCP specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) — `request`/`query-ref`'in modern araç-kullanım karşılığı
- [A2A specification](https://a2a-protocol.org/latest/specification/) — contract-net ve subscribe-notify'nin modern agent-eş karşılığı
