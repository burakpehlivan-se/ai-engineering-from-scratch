# Eylem Bütçeleri, İterasyon Sınırları ve Maliyet Denetçileri (Cost Governors)

> Orta ölçekli bir e-ticaret agent'ının aylık LLM maliyeti, ekibin "sipariş takibi" (order-tracking) becerisini etkinleştirmesinin ardından 1.200$'dan 4.800$'a fırladı. Bu bir fiyat hatası değil. Bu, yeni bir döngü bulan ve içinde harcamaya devam eden bir agent. Microsoft Agent Governance Toolkit (2 Nisan 2026), bu sınıfa karşı savunmayı kodifiye eder: istek başına `max_tokens`, görev başına token ve dolar bütçeleri, gün/ay başına üst sınırlar, iterasyon sınırları, kademeli model yönlendirmesi (tiered model routing), istem önbellekleme (prompt caching), bağlam pencereleme (context windowing), pahalı eylemlerde insan-döngüde (HITL) kontrol noktaları, bütçe ihlalinde durdurma anahtarları (kill switches). Anthropic'ın Claude Code Agent SDK'sı aynı temel yapı taşlarını farklı isimlerle sunar. Finansal hız sınırları — örneğin 10 dakikada 50$'ı aşınca erişimi kesme — aylık sınırlardan daha hızlı yakalar.

**Tür:** Öğrenme
**Diller:** Python (stdlib, katmanlı maliyet denetçisi simülatörü)
**Önkoşullar:** Faz 15 · 10 (İzin modları), Faz 15 · 12 (Dayanıklı çalıştırma)
**Süre:** ~60 dakika

## Sorun

Otonom agent'lar her turda gerçek para harcar. Bir sohbet botunun kötü çıktısı kötü bir yanıtken, bir agent'ın kötü döngüsü bir faturadır. Sektördeki belgelenmiş başarısızlık modu terimi "Cüzdan Reddi"dir (Denial of Wallet) — agent mantık yürütmeye, araç çağırmaya, faturalandırmaya devam eder ve hiçbir şey durdurmaz çünkü hiçbir şey tasarlanmamıştır.

Çözüm tek bir sayı değildir. Farklı zaman ölçeklerinde ve granülaritelerde bir sınıflar yığınıdır: istek başına, görev başına, saat başına, gün başına, ay başına. İyi tasarlanmış bir yığın, kontrolden çıkmış bir döngüyü dakikalar içinde, yavaş bir sızıntıyı saatler içinde ve kötü bir dağıtımı bir gün içinde yakalar. Aynı yığın, agent uzun vadeli ve otonom olduğunda bir bütçeyi sürdürür.

Bu bir mühendislik dersidir: matematik önemsizdir, disiplin ekiplerin başarısız olduğu yerdir. Aşağıdaki sınırlar listesi ya Microsoft Agent Governance Toolkit'te ya da Anthropic Claude Code Agent SDK belgelerinde adlandırılmıştır.

## Kavram

### Maliyet denetçisi yığını

1. **İstek başına `max_tokens`.** Basit. Tek bir çağrının sınırsız bir tamamlama (completion) üretmesini önler.
2. **Görev başına token bütçesi.** Tüm çalışma boyunca N token'ı aşma. Sınırdan sert durdurma.
3. **Görev başına dolar bütçesi.** Token ile aynı ancak para birimi cinsinden. Claude Code'da `max_budget_usd`.
4. **Araç başına üst sınır.** En fazla N `WebFetch` çağrısı, N `shell_exec` çağrısı vb.
5. **İterasyon sınırı (`max_turns`).** Toplam agent döngüsü iterasyonları; sonsuz akıl yürütme döngülerini önler.
6. **Dakika/saat/gün/ay başına üst sınır.** Kayan pencereler (rolling windows). Farklı zaman ölçeklerinde sızıntıları yakalar.
7. **Finansal hız sınırı.** Örneğin "10 dakikada 50$'ı aşarsa erişimi kes." Aylık sınırlar devreye girmeden önce döngü tabanlı yakımı yakalar.
8. **Kademeli model yönlendirmesi.** Varsayılan olarak daha küçük bir modele geç; sadece bir sınıflandırıcı (classifier) görevin buna değer olduğuna karar verdiğinde daha büyük bir modele yükselt.
9. **İstem önbellekleme.** Sistem istemi (system prompt) ve kararlı bağlam sağlayıcı önbelleğinde saklanır; yeniden gönderme token maliyeti neredeyse sıfırdır.
10. **Bağlam pencereleme.** Aktif bağlamı bir eşik altında tutmak için sıkıştırma/özetleme; doğrudan token maliyeti azaltma.
11. **Pahalı eylemlerde HITL kontrol noktaları.** Pahalı olduğu bilinen bir eylemden önce (uzun araç çağrısı, büyük indirme, maliyetli model yükseltme) insan onayı iste.
12. **Bütçe ihlalinde durdurma anahtarı.** Herhangi bir sınır devreye girdiğinde oturum iptal edilir. Sınır kaydedilir; ayrı bir yeniden etkinleştirme yolu gerektirir.

### Neden yığın, tek bir sınır değil

Tek bir aylık sınır, kontrolden çıkmış bir agent'ı sadece cüzdan tükendikten sonra yakalar. Tek bir istek başına sınır, oturum düzeyinde hiçbir şeyi yakalamaz. Farklı başarısızlık modları farklı zaman ölçekleri gerektirir:

- **Kontrolden çıkmış döngü** (agent 5 saniyelik bir yeniden deneme döngüsünde takılmış): hız sınırı tarafından yakalanır.
- **Yavaş sızıntı** (agent görev başına beklenenin ~2 katı iş yapıyor): günlük sınır tarafından yakalanır.
- **Kötü dağıtım** (yeni sürüm 5x token kullanıyor): haftalık/aylık sınır tarafından yakalanır.
- **Meşru artış** (gerçek talep, hata değil): saat/gün sınırı ile net logla yakalanır.

### Claude Code'un bütçe yüzeyi

Claude Code Agent SDK şunları sunar (açık belgeler):

- `max_turns` — iterasyon sınırı.
- `max_budget_usd` — dolar sınırı; ihlalde oturum iptal edilir.
- `allowed_tools` / `disallowed_tools` — araç izin listesi ve yasaklama listesi.
- Araç kullanımından önce özel maliyet muhasebesi için kanca noktaları (hook points).

İzin modu merdiveni (Ders 10) ile birleştirin. `max_budget_usd` olmadan bir `autoMode` oturumu denetimsiz otonomluktur. Anthropic, Auto Modu açıkça bütçe kontrolleri gerektiren olarak çerçevelendirir; sınıflandırıcı maliyetle orthogonal'dır.

### EU AI Act, OWASP Agentic Top 10

Microsoft Agent Governance Toolkit, OWASP Agentic Top 10 ve EU AI Act Madde 14 (insan gözetimi) gereksinimlerini kapsar. AB'de üretim için loglama ve sınır uygulamaları opsiyonel değildir.

### Gözlemlenen 1.200$ → 4.800$ vakası

Microsoft belgelerindeki gerçek vaka: aylık maliyeti yeni bir araç eklenmesinin ardından üçe katlanan bir e-ticaret agent'ı. Araç, agent'ın her oturumda sipariş durumunu sorgulamasına izin veriyordu. Döngü tespiti yok. Araç başına sınır yok. Haftalık büyümeye uyarı yok. Çözüm, araç başına sınır artı günlük büyüme uyarısı oldu. Bu bir şablondur: her yeni araç yüzeyi yeni bir potansiyel döngüdür; her yeni aracın kendi sınırı ve kendi uyarısı olmalıdır.

## Kullan

`code/main.py`, katmanlı bir maliyet denetçisi yığını ile ve olmadan bir agent çalışmasını simüle eder. Simüle edilen agent bazı turlardan sonra sorgulama döngüsüne (polling loop) sapar; katmanlı yığın hız penceresi içinde yakalarken, tek bir aylık sınır günler sonra devreye girer.

## Üret

`outputs/skill-agent-budget-audit.md`, önerilen bir agent dağıtımının maliyet denetçisi yığınını denetler ve eksik katmanları işaretler.

## Alıştırmalar

1. `code/main.py` çalıştırın. Sorgulama döngüsü yörüngesinde hız sınırının iterasyon sınırından önce devreye girdiğini doğrulayın. Şimdi hız sınırını devre dışı bırakın ve iterasyon sınırı yakalayana kadar agent'ın ne kadar "harcadığını" ölçün.

2. Bir tarayıcı agent'ı (Ders 11) için araç başına sınır kümesi tasarlayın. Hangi aracın en sıkı sınıra ihtiyacı var? Hangi araç risksiz sınırsız çalışabilir?

3. Microsoft Agent Governance Toolkit belgelerini okuyun. Araç setinin adlandırdığı her sınır türünü listeleyin. Her birini bir başarısızlık moduyla (kontrolden çıkmış döngü, yavaş sızıntı, kötü dağıtım, artış) eşleştirin.

4. Gerçekçi bir görev için gece gözetimsiz çalışmayı fiyatlandırın (örneğin "bir depoda 50 sorunu sınıflandır"). `max_budget_usd` tahmininizin 2 katına ayarlayın. 2x tercihini gerekçelendirin.

5. Claude Code'un `max_budget_usd`'si oturum toplam maliyeti üzerinde devreye girer. Dışarıdan uygulayacağınız tamamlayıcı bir hız sınırı tasarlayın. Kesmeyi tetikleyen ne ve yeniden etkinleştirme nasıl görünür?

## Anahtar Terimler

| Terim | Ne Söyleniyor | Aslında Ne Anlama Geliyor |
|---|---|---|
| Denial of Wallet (Cüzdan Reddi) | "Kontrolden çıkmış fatura" | Sınırlama olmayan döngüde harcama üreten agent döngüsü |
| max_tokens | "İstek başına sınır" | Tek bir tamamlamanın boyutu için tavan |
| max_turns | "İterasyon sınırı" | Bir oturumdaki agent döngüsü iterasyonları için tavan |
| max_budget_usd | "Dolar durdurma anahtarı" | Oturum maliyet sınırı; ihlalde iptal edilir |
| Velocity limit (Hız sınırı) | "Oran sınırı" | Kısa pencerede harcama sınırı (ör. 50$ / 10 dk) |
| Tiered routing (Kademeli yönlendirme) | "Önce küçük model" | Ucuz model varsayılan; sadece sınıflandırıcı gerektiğinde yükselt |
| Prompt caching (İstem önbellekleme) | "Önbelleğe alınmış sistem istemi" | Sağlayıcı tarafı önbellek yeniden gönderme token maliyetini neredeyse sıfıra düşürür |
| HITL checkpoint | "İnsan onay kapısı" | Pahalı eylemden önce gerekli insan dokunuşu |

## İleri Okuma

- [Anthropic Claude Code Agent SDK — agent döngüsü ve bütçeler](https://code.claude.com/docs/en/agent-sdk/agent-loop) — `max_turns`, `max_budget_usd`, araç izin listeleri.
- [Microsoft Agent Framework — insan-döngüde ve yönetim](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) — maliyet denetçisi kontrol noktaları.
- [Anthropic — Claude Yönetilen Agentlar genel bakışı](https://platform.claude.com/docs/en/managed-agents/overview) — sağlayıcı tarafı maliyet kontrolleri.
- [Anthropic — İstem önbellekleme (Claude API belgeleri)](https://platform.claude.com/docs/en/prompt-caching) — önbellekleme mekaniği.
- [Anthropic — Pratikte agent otonomunu ölçme](https://www.anthropic.com/research/measuring-agent-autonomy) — uzun vadeli agent'lar için maliyet profili.
