# Tarayıcı Agentları ve Uzun Vadeli Web Görevleri

> ChatGPT agentı (Temmuz 2025), Operator ve derin araştırmayı (deep research) tek bir tarayıcı/terminal agentında birleştirdi ve BrowseComp'ta %68,9 ile güncel en iyi sonucu (SOTA) belirledi. OpenAI, 31 Ağustos 2025'te Operator'ı kapattı — ürün katmanında birleşme. Anthropic'in Vercept satın alması, Claude Sonnet'i OSWorld'de %15'in altından %72,5'e taşıdı. WebArena-Verified (ServiceNow, ICLR 2026), orijinal WebArena'da %11,3'lük yanlış-negatif oranını (false-negative rate) düzeltti ve 258 görevlik Hard alt kümesini (subset) yayınladı. Sayılar gerçektir. Saldırı yüzeyi de öyle: OpenAI'ın hazırlık başkanı, tarayıcı agentlarına dolaylı prompt enjeksiyonunun (indirect prompt injection) "tam olarak yamalanamayan bir hata" olduğunu kamuoyu önünde söyledi. Belgelenmiş 2025-2026 saldırılar: Tainted Memories (Atlas CSRF), HashJack (Cato Networks) ve Perplexity Comet'te tek tıklamayla ele geçirme (hijack).

**Tür:** Öğrenme
**Diller:** Python (stdlib, dolaylı prompt enjeksiyonu saldırı yüzeyi modeli)
**Önkoşullar:** Faz 15 · 10 (İzin modları), Faz 15 · 01 (Uzun vadeli agentlar)
**Süre:** ~45 dakika

## Sorun

Bir tarayıcı agentı, güvenilmeyen (untrusted) içerik okuyan ve sonuçları olan eylemler gerçekleştiren uzun vadeli bir agenttır. Agent'ın ziyaret ettiği her sayfa, kullanıcının yazmadığı bir girdidir. Her sayfadaki her form potansiyel bir komut kanalıdır. 2025-2026 saldırı külliyatı bunun hipotetik olmadığını gösteriyor: Tainted Memories, bir saldırganın agent'ın hafızasına (memory) bir sayfa aracılığıyla kötü niyetli talimatlar bağlamasına izin verir; HashJack, agent'ın ziyaret ettiği URL parçacıklarında (fragments) komutları gizler; Perplexity Comet ele geçirmesi tek tıklamayla olur.

Savunma manzarası rahatsız edicidir. OpenAI'ın hazırlık başkanı sessiz parçayı yüksek sesle söyledi: dolaylı prompt enjeksiyonu "tam olarak yamalanamayan bir hatadır." Bunun nedeni, saldırının agent'ın okuma-vs-hareket (reading-vs-acting) sınırında yaşamasıdır; bu mimari olarak belirsizdir — modelin okuduğu her token, ilke olarak bir talimat olarak okunabilir.

Bu ders saldırı yüzeyini adlandırır, benchmark manzarasını adlandırır (BrowseComp, OSWorld, WebArena-Verified) ve gerçek savunmalar hakkında Ders 14 ve 18'de akıl yürütmeniz için minimal bir dolaylı prompt enjeksiyonu senaryosunu modeller.

## Kavram

### 2026 manzarası, her sistem için bir paragrafta

**ChatGPT agentı (OpenAI).** Temmuz 2025'te başlatıldı. Operator (tarayıcı) ve Deep Research (çok saatlik araştırma) birleştirildi. Bağımsız Operator 31 Ağustos 2025'te kapatıldı. BrowseComp'ta SOTA %68,9; OSWorld ve WebArena-Verified'da güçlü sayılar.

**Claude Sonnet + Vercept (Anthropic).** Anthropic'in Vercept satın alması bilgisayar-kullanımı yeteneklerine odaklandı. Claude Sonnet'i OSWorld'de %15'in altından %72,5'e taşıdı. Claude Computer Use bir araç API'si olarak yayınlanıyor.

**Gemini 3 Pro ve Browser Use (DeepMind).** Browser Use entegrasyonu bilgisayar-kullanımı kontrolleri sunar; FSF v3 (Nisan 2026, Ders 20) özellikle ML R&D alanında otonomluğu takip eder.

**WebArena-Verified (ServiceNow, ICLR 2026).** İyi belgelenmiş bir sorunu düzeltir: orijinal WebArena'nın ~%11,3 yanlış-negatif oranı (başarısız olarak işaretlenmiş ancak aslında çözülmüş görevler) vardı. Verified sürümü, insan tarafından düzenlenmiş başarı kriterleriyle yeniden puanlar ve 258 görevlik Hard alt kümesini ekler (ICLR 2026 makalesi, openreview.net/forum?id=94tlGxmqkN).

### BrowseComp, OSWorld ve WebArena karşılaştırması

| Benchmark | Neyi ölçer | Ufuk |
|---|---|---|
| BrowseComp | Zaman baskısı altında açık web'de belirli bulguları bulma | dakikalar |
| OSWorld | Agent'ın tam bir masaüstünü çalıştırması (fare, klavye, kabuk) | onlarca dakika |
| WebArena-Verified | Simüle edilmiş sitelerde işlemlisel (transactional) web görevleri | dakikalar |
| Hard alt kümesi | Çok sayfa durum geçişleri içeren WebArena-Verified görevleri | onlarca dakika |

Farklı eksenler. Yüksek bir BrowseComp puanı, agent'ın bulguları bulduğunu söyler; bir uçak bileti ayırtabileceğini söylemez. OSWorld puanı "masaüstümde çalışır mı"ya daha yakındır. WebArena-Verified "bir akışı tamamlayabilir mi"ye daha yakındır. Herhangi bir üretim kararı, görev dağıtımına uyan benchmark'ı gerektirir.

### Saldırı yüzeyi, adlandırılmış

1. **Dolaylı prompt enjeksiyonu (indirect prompt injection).** Güvenilmeyen sayfa içeriği talimatlar içerir. Agent bunları okur. Agent bunları çalıştırır. Herkese açık örnekler: 2024 Kai Greshake ve ark., 2025 Tainted Memories makalesi, 2026 HashJack (Cato Networks).
2. **URL parçacığı / sorgu enjeksiyonu (URL fragment / query injection).** Bir taranmış (crawled) URL'nin `#fragment`'i veya sorgu dizesi (query string) komutlar içerir. Hiçbir zaman görsel olarak görüntülenmez; agent'ın bağlamının (context) içindedir.
3. **Hafıza bağlama saldırıları (memory-binding attacks).** Sayfa, agent'a kalıcı bir hafıza yazması için talimat verir (Ders 12 dayanıklı durumu kapsar). Bir sonraki oturumda hafıza, görünür bir tetikleyici olmadan yükü (payload) ateşler.
4. **Kimlik doğrulanmış oturumlara CSRF-şekilli saldırılar.** Tainted Memories sınıfı: agent bir yerde oturum açmış; saldırganın sayfası, agent'ın kullanıcının çerezleriyle (cookies) gerçekleştirdiği durum-değiştirici istekler gönderir.
5. **Tek tıklamayla ele geçirme (one-click hijack).** Görsel olarak masum bir düğme, agent'ın takip ettiği bir yükü bindirir. Comet sınıfı.
6. **Agent'ın host yüzeyindeki Content-Safety-Policy delikleri.** Görüntüleme ve araç katmanları kendileri birer vektör olabilir; tarayıcı-içinde-tarayıcı-agentı yığını genişir.

### Neden "tam olarak yamalanamıyor"

Saldırı, agent'ın yeteneği ile izomorfiktir. Agent, işini yapmak için güvenilmeyen içerik okumak zorundadır. Agent'ın okuduğu her içerik talimatlar içerebilir. Agent'ın takip ettiği her talimat, kullanıcın gerçek isteğiyle uyumsuz olabilir. Savunmalar (güven sınırları, sınıflandırıcılar, araç izin listeleri, sonuçları olan eylemlerde HITL) saldırının maliyetini artırır ve patlama yarıçapını (blast radius) azaltır. Sınıfı kapatmaz.

Bu, Lob teoremiyle aynı akıl yürütme kalıbıdır (Ders 8): agent bir sonraki token'ın güvenli olduğunu kanıtlayamaz; yalnızca güvensiz token'ların daha tespit edilebilir olduğu bir sistem kurabilir.

### Üretime gelen savunma duruşu

- **Okuma/yazma sınırı.** Okuma asla sonuç değildir (consequential). Yazma (bir form göndermek, içerik yayınlamak, yan etkili bir araç çağırmak), başlatan içerik güven sınırının dışındaysa taze insan onayı gerektirir.
- **Görev başına araç izin listesi.** Agent gezebilir; ancak o araç bu görev için açıkça etkinleştirilmediyse bir havale (wire transfer) başlatamaz. Ders 13 bütçeleri kapsar.
- **Oturum izolasyonu.** Tarayıcı agentı oturumları yalnızca kapsamlandırılmış (scoped) kimlik bilgileriyle çalıştırılır. Üretim kimlik doğrulaması yok, kişisel e-posta yok. Her HTTP isteğinin kayıtları denetim için saklanır.
- **İçerik arındırıcı (content sanitizer).** Getirilen HTML, model bağlamına (context) birleştirilmeden önce bilinen-kötü kalıplardan arındırılır. Kolay saldırıları azaltır; sofistike yükleri (payload) durdurmaz.
- **Sonuçları olan eylemlerde HITL.** Öneri-sonra-karar (propose-then-commit) kalıbı (Ders 15).
- **Hafıza için kanarya token'ları (canary tokens).** Bir hafıza girişi ateşlenirse, kullanıcı bunu görür (Ders 14).

## Kullan

`code/main.py`, üç sentetik sayfaya karşı küçük bir tarayıcı agentı çalışmasını modeller. Bir sayfa masumdur, birinde görünür metinde doğrudan prompt enjeksiyonu blobu vardır, birinde URL parçacığı enjeksiyonu (görünmez ancak agent'ın bağlamının içindedir) vardır. Betik şunları gösterir: (a) saf bir agentın ne yapacağını, (b) okuma/yazma sınırının neyi yakaladığını, (c) arındırıcının neyi yakaladığını, (d) ikisinin de neyi kaçıracağını.

## Üret

`outputs/skill-browser-agent-trust-boundary.md`, önerilen bir tarayıcı agentı dağıtımını (deployment) kapsamlandırır: hangi güven bölgelerine (trust zones) dokunur, neyi yazma yetkisi vardır ve ilk çalıştırmadan önce hangi savunmalar yerinde olmalıdır.

## Alıştırmalar

1. `code/main.py` dosyasını çalıştırın. Arındırıcının yakaladığı ancak okuma/yazma sınırının yakalamadığı saldırıyı ve yalnızca okuma/yazma sınırının yakaladığı saldırıyı belirleyin.

2. Arındırıcıyı HashJack tarzı URL parçacığı enjeksiyonunun bir sınıfını tespit edecek şekilde genişletin. Meşru parçacıklara sahip iyi niyetli URL'ler üzerinde yanlış-pozitif oranını ölçün.

3. Bildiğiniz gerçek bir tarayıcı agentı iş akışını seçin (ör. "bir uçak bileti ayırt"). Her okumayı ve her yazmayı listeleyin. Hangilerinin HITL gerektirdiğini ve nedenini işaretleyin.

4. WebArena-Verified ICLR 2026 makalesini okuyun. Orijinal WebArena'nın puanlamasının güvenilir olmadığı bir görev kategorisini belirleyin ve Verified alt kümesinin bunu nasıl çözdüğünü açıklayın.

5. Bir tarayıcı agentı ortamı için bir hafıza kanaryası (memory canary) tasarlayın. Ne saklarsınız, nerede ve alarmı ne tetikler?

## Anahtar Terimler

| Terim | Ne Söyleniyor | Aslında Ne Anlama Geliyor |
|---|---|---|
| Dolaylı prompt enjeksiyonu (Indirect prompt injection) | "Kötü sayfa metni" | Agent'ın okuduğu bir sayfadaki güvenilmeyen içerik, agent'ın çalıştırdığı talimatlar içerir |
| Tainted Memories | "Hafıza saldırısı" | Agent, saldırgan tarafından sağlanan bir talimatı dayanıklı hafızaya yazar; bir sonraki oturumda tetiklenir |
| HashJack | "URL parçacığı saldırısı" | URL parçacığı / sorgu dizesine gizlenmiş yük, agent'ın bağlamındadır ancak görsel olarak görüntülenmez |
| Tek tıklamayla ele geçirme (One-click hijack) | "Kötü düğme" | Görünür fırsat (affordance), agent'ın çalıştır takip yükünü bindirir |
| BrowseComp | "Web arama benchmark'ı" | Açık web'de belirli bulguları bulma; dakika ölçekli ufuk |
| OSWorld | "Masaüstü benchmark'ı" | Tam OS kontrolü; çok adımlı GUI görevleri |
| WebArena-Verified | "Düzeltilmiş web-görevi benchmark'ı" | Hard alt kümesiyle ServiceNow'un yeniden puanlanmış WebArena'sı |
| Okuma/yazma sınırı (Read/write boundary) | "Yan etki kapısı" | Okuma asla sonuç değildir; güven-dışındaysa yazma taze onay gerektirir |

## İleri Okuma

- [OpenAI — ChatGPT agent Tanıtımı](https://openai.com/index/introducing-chatgpt-agent/) — Operator ve deep research birleşmesi; BrowseComp SOTA.
- [OpenAI — Bilgisayar-Kullanan Agent](https://openai.com/index/computer-using-agent/) — Operator soy ağacı ve ChatGPT agent olan mimari.
- [Zhou ve ark. — WebArena](https://webarena.dev/) — orijinal benchmark.
- [WebArena-Verified (OpenReview)](https://openreview.net/forum?id=94tlGxmqkN) — ICLR 2026 düzeltilmiş-alt küme makalesi.
- [Anthropic — Pratikte Agent Otonomunu Ölçme](https://www.anthropic.com/research/measuring-agent-autonomy) — bilgisayar-kullanan agentlar için saldırı yüzeyi tartışmasını içerir.
