# İnsan-Döngüde: Öner-Sonra-Uygula (Propose-Then-Commit)

> 2026'daki HITL (insan-döngüde) konsensüsü özeldir. "Agent sorar, kullanıcı Uygun'a basar" değildir. Öner-sonra-uygula'dır: önerilen eylem, bir özdeşlik anahtarı (idempotency key) ile dayanıklı bir depoya kaydedilir; niyet, veri soyu (data lineage), dokunulan izinler, etki yarıçapı (blast radius) ve geri alma planıyla birlikte bir inceleyiciye sunulur; sadece olumlu onaydan sonra uygulanır; uygulamadan sonra doğrulanarak yan etkinin gerçekten gerçekleştiği doğrulanır. LangGraph'in `interrupt()` artı PostgreSQL checkpoint'leme, Microsoft Agent Framework'ün `RequestInfoEvent`'i ve Cloudflare'ın `waitForApproval()`'ı aynı biçimi uygular. Klasik başarısızlık modu kauçuk mührü (rubber-stamp) onayıdır: "Onaylıyor musunuz?" incelenmeden tıklanır. Belgelenmiş azaltma, açık bir kontrol listesiyle meydan okuma ve yanıt (challenge-and-response) kalıbıdır.

**Tür:** Öğrenme
**Diller:** Python (stdlib, özdeşlik anahtarıyla öner-sonra-uygula durum makinesi)
**Önkoşullar:** Faz 15 · 12 (Dayanıklı çalıştırma), Faz 15 · 14 (Tuzak telleri)
**Süre:** ~60 dakika

## Sorun

Bir agent bir eylem gerçekleştirir. Kullanıcının karar vermesi gerekir: uygun mu değil mi. Karar anlıksa muhtemelen bir inceleme değildir. Karar yapılandırılmışsa yavaştır ama güvenilirdir. Mühendislik sorusu, yapılandırılmış bir incelemeyi en az dirençli yol haline nasıl getireceğinizdir.

2023 dönemi HITL kalıbı senkron bir istemdi: "Agent X'e Y gövdesiyle e-posta göndermek istiyor — onaylıyor musunuz?" Kullanıcı Uygun'a basar. Herkes sistemin güvenli olduğunu hisseder. Pratikte bu yüzey yoğun şekilde kauçuk mühürlenir: kullanıcılar hızlı onaylar, onaylar az şey tahmin eder ve agent yanlış gittiğinde, kullanıcı hatırlayamadığı uzun bir onay geçmişi denetim izinde (audit trail) görünür.

2026 kalıbı — öner-sonra-uygula — HITL'i dayanıklı bir zemine taşır, yapılandırılmış meta veri ekler ve olumlu uygulama ister. Her yönetilen agent SDK'sı bir sürüm sunar: LangGraph `interrupt()`, Microsoft Agent Framework `RequestInfoEvent`, Cloudflare `waitForApproval()`. API isimleri farklıdır; biçim aynıdır.

## Kavram

### Öner-sonra-uygula durum makinesi

1. **Öner.** Agent önerilen bir eylem üretir. Dayanıklı bir depoya (PostgreSQL, Redis, Durable Object) kaydedilir. Şunları içerir:
 - niyet (neden agent bunu yapıyor)
 - veri soyu (hangi kaynak bu önermeye yol açtı)
 - dokunulan izinler (hangi kapsam/dosya/son nokta)
 - etki yarıçapı (en kötü durum nedir)
 - geri alma planı (uygulanırsa nasıl geri alınır)
 - özdeşlik anahtarı (önerme başına benzersiz; yeniden gönderme aynı kaydı döndürür)
2. **Sunma.** İnceleyici öneriyi tüm meta verilerle görür. İnceleyici bir kişidir (kendini inceleyen agent değil).
3. **Uygulama.** Olumlu onay. Eylem çalıştırılır.
4. **Doğrulama.** Uygulamadan sonra yan etki geri okunur ve doğrulanır. Doğrulama adımı başarısız olursa sistem bilinen kötü bir durumdadır ve uyarı devreye girer.

### Özdeşlik anahtarı

Özdeşlik anahtarı olmadan, geçici bir hatadan sonra yeniden deneme, onaylanmış bir eylemi iki kez çalıştırabilir. Somut örnek: kullanıcı "A'dan B'ye 100$ aktar" işlemini onaylar. Ağ kesilir. İş akışı yeniden dener. Kullanıcı bir kez onaylamıştır ancak aktarma iki kez çalışır. Özdeşlik anahtarı onayı tek, benzersiz bir yan etkiye bağlar; ikinci uygulama boşuna çalışır.

Bu, Stripe ve AWS API'lerinin kullandığı özdeşlik kalıbıdır. Microsoft Agent Framework belgelerinde agent onayları için yeniden kullanmak açıkça belirtilmiştir.

### Dayanıklılık: neden onaylar süreçlerden uzun yaşar

Onay bekleme odası, agent'ın sahip olmadığı bir durum parçasıdır. İş akışı durdurulmuştur (Ders 12). Onay geldiğinde iş akışı tam olarak o noktadan devam eder. Bu yüzden LangGraph `interrupt()`'ı sadece bellek içi durumla değil, PostgreSQL checkpoint'lemesiyle eşleştirir — iki gün sonra gelen bir onay hala iş akışını sağlam bulur.

### Kauçuk mühürlü onaylar ve meydan okuma-yanıt azaltması

HITL için varsayılan arayüz ("Onayla" / "Reddet" düğmeleri) gerçek bir inceleme olmadan hızlı onaylar üretir. Belgelenmiş azaltma: Onayla düğmesinin etkinleşmesinden önce belirli sorulara olumlu yanıtlar gerektiren bir meydan okuma-yanıt kontrol listesi. Somut biçim:

- "Bu eylemin hangi kaynağı dokunduğunu anlıyor musunuz? [ ]"
- "Etki yarıçapının kabul edilebilir olduğunu doğruladınız mı? [ ]"
- "Bunu başarısız olursa geri alma planınız var mı? [ ]"

Kendi başına bürokrasi değil — bir zorlayıcı işlev. Kutuları işaretleyemeyen inceleyici ya açıklama ister (yükseltme) ya da reddeder (güvenli varsayılan). Anthropic agent-güvenlik araştırması, kauçuk mühürlü onay kalıpları için azaltma olarak açıkça kontrol listesi驱动lı HITL'i belirtir.

### Sonuç eylem sayılan şeyler

Her eylemin öner-sonra-uygula gerektirmez. 2026 rehberliği:

- **Sonuç eylemleri** (her zaman HITL): geri dönüşü olmayan yazılar, finansal işlemler, giden iletişim, üretim veritabanı değişiklikleri, yıkıcı dosya sistemi işlemleri.
- **Geri dönüşü olan eylemler** (bazen HITL): yerel dosyalarda düzenlemeler, hazırlık ortamı (staging) değişiklikleri, net geri almayla geri dönüşü olan yazılar.
- **Okumalar ve denetimler** (asla HITL): dosya okuma, kaynak listeleme, salt okunur API çağrısı.

### Eylem sonrası doğrulama

"Uygulama çalıştı" ile "yan etki gerçekleşti" aynı şey değildir. Ağ bölünmesi (partition) ve yarış durumları (race conditions), arka tarafın kalıcı hale getirmediği halde başarılı olduğunu düşünen bir iş akışı üretebilir. Doğrulama adımı, uygulamadan sonra hedef kaynağı tekrar okuyarak doğrular. Bu, `RETURNING` yan cümleciğiyle veritabanı işlemleri veya `PutObject` sonrası AWS `GetObject` ile aynı kalıptır.

### EU AI Act Madde 14

Madde 14, AB'deki yüksek riskli AI sistemleri için etkili insan gözetimini zorunlu kılar. "Etkili" süsleme değildir. Düzenleyici dil açıkça kauçuk mühürlü kalıpları hariç tutar. Meydan okuma-yanıt ile öner-sonra-uygula, Microsoft Agent Governance Toolkit uyumluluk belgelerinde Madde 14 incelemesinden geçen biçmdir.

## Kullan

`code/main.py`, stdlib Python'da bir öner-sonra-uygula durum makinesi uygular. Dayanıklı depo bir JSON dosyasıdır. Özdeşlik anahtarı (thread_id, eylem imzası) hash'idir. Sürücü üç durumu simüle eder: temiz bir onay akışı, geçici hatadan sonra yeniden deneme (iki kez çalışmamalı) ve kauçuk mühürlü varsayılan ile meydan okuma-yanıt akışı karşılaştırması.

## Üret

`outputs/skill-hitl-design.md`, önerilen bir HITL iş akışını öner-sonra-uygula biçimi için inceler ve eksik meta veri, özdeşlik, doğrulama veya meydan okuma-yanıt katmanlarını işaretler.

## Alıştırmalar

1. `code/main.py` çalıştırın. Onaylanmış bir önermenin yeniden denemesinin dayanıklı kaydı kullandığını ve tekrar çalıştırılmadığını doğrulayın. Şimdi özdeşlik anahtarına bir zaman damgası ekleyin ve yeniden denemenin iki kez çalıştığını gösterin.

2. Önerme kaydını bir `rollback` alanı ile genişletin. Doğrulama adımı başarısız olan bir uygulamayı simüle edin. Geri almanın otomatik olarak devreye girdiğini gösterin.

3. Microsoft Agent Framework'ün `RequestInfoEvent` belgelerini okuyun. API'nin içerdiği ancak oyuncak motorun eksik olduğu bir meta veri alanı belirleyin. Ekleyin ve neye karşı koruduğunu açıklayın.

4. Belirli bir eylem için (ör. "herkese açık bir Twitter hesabında paylaşım") bir meydan okuma-yanıt kontrol listesi tasarlayın. İnceleyicinin yanıtlaması gereken üç soru nedir? Neden bu üçü?

5. Senkron bir "Onaylıyor musunuz?" isteminin yeterli olacağı (dayanıklı depo gerekmediği) bir durum seçin. Nedenini açıklayın ve kabul ettiğiniz risk sınıfını adlandırın.

## Anahtar Terimler

| Terim | Ne Söyleniyor | Aslında Ne Anlama Geliyor |
|---|---|---|
| Propose-then-commit (Öner-sonra-uygula) | "İki aşamalı onay" | Kalıcı önerme + olumlu uygulama + doğrulama |
| Idempotency key (Özdeşlik anahtarı) | "Yeniden deneme güvenli jetonu" | Önerme başına benzersiz; ikinci uygulama boşuna çalışır |
| Data lineage (Veri soyu) | "Nereden geldiği" | Bu önermeye yol açan belirli kaynak içeriği |
| Blast radius (Etki yarıçapı) | "En kötü durum" | Eylem yanlış giderse etki kapsamı |
| Rubber-stamp (Kauçuk mührü) | "Hızlı onay" | Gerçek inceleme olmadan "Onayla" tıklanması |
| Challenge-and-response (Meydan okuma-yanıt) | "Zorlayıcı kontrol listesi" | İnceleyici belirli sorulara olumlu onay vermeli |
| RequestInfoEvent | "MS Agent Framework ilkel elementi" | Yapılandırılmış meta veriyle dayanıklı HITL isteği |
| `interrupt()` / `waitForApproval()` | "Çerçeve ilkel elementleri" | LangGraph / Cloudflare ile aynı biçimin eşdeğerleri |

## İleri Okuma

- [Microsoft Agent Framework — İnsan döngüde](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) — `RequestInfoEvent`, dayanıklı onaylar.
- [Cloudflare Agents — İnsan döngüde](https://developers.cloudflare.com/agents/concepts/human-in-the-loop/) — `waitForApproval()` ve Durable Objects.
- [Anthropic — Pratikte agent otonomunu ölçme](https://www.anthropic.com/research/measuring-agent-autonomy) — uzun vadeli risk için azaltma olarak HITL.
- [EU AI Act — Madde 14: İnsan gözetimi](https://artificialintelligenceact.eu/article/14/) — yüksek riskli sistemler için düzenleyici temel.
- [Anthropic — Claude'un Anayasası (Ocak 2026)](https://www.anthropic.com/news/claudes-constitution) — gözetim etrafında anayasal çerçeve.
