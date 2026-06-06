# Otomatik Uyumsuzluk Araştırması (Anthropic AAR)

> Anthropic, bağımsız sandbox'larda paralel Claude Opus 4.6 Otonom Uyumsuzluk Araştırmacısı (Autonomous Alignment Researcher — AAR) ekipleri çalıştırarak, her sandbox'ın dışında saklanan günlüklerle (log) ortak bir forum aracılığıyla koordine etti (böylece agentlar kendi kayıtlarını silemez). Zayıf-güçlü eğitim (weak-to-strong training) sorununda AAR'lar insan araştırmacıları geride bıraktı. Anthropic'in kendi özeti, belirlenmiş iş akışlarının (prescribed workflows) AAR esnekliğini sıklıkla kısıtladığını ve performansı düşürdüğünü belirtiyor. Uyumsuzluk araştırmasını otomatikleştirmek, RSP'nin tespit etmesi gereken tam uyumsuzluk risklerine (misalignment risk) giden zaman çizelgesini sıkıştıran (compress) adımdır.

**Tür:** Öğrenme
**Diller:** Python (stdlib, paralel araştırma-forumu simülatörü)
**Önkoşullar:** Faz 15 · 05 (AI Scientist v2), Faz 15 · 04 (DGM)
**Süre:** ~60 dakika

## Sorun

Uyumsuzluk araştırması, insan araştırmacı zamanı açısından pahalıdır. Ölçeklenebilir gözetim (scalable oversight), ödül belirtimi (reward specification) veya zayıf-güçlü eğitim gibi sorunlar, iterasyon başına haftalarca süren deneyler gerektirir. Sınır yetenekler (frontier capabilities) ilerledikçe, uyumsuzluk iş yükü nitelikli araştırmacı arzından daha hızlı büyür.

Otomatik Uyumsuzluk Araştırması (AAR), yetenekleri uyumsuzluğu aşan aynı sınır modellerinin (frontier models) boşluğu kapatmaya katkıda bulunup bulunamayacağını sorar. Anthropic'in 2026 AAR-ran bir zayıf-güçlü eğitim çalışmasının (alignment.anthropic.com/2026/automated-w2s-researcher/) raporu, bu sınıfın ilk kamu sonuçlarından biridir.

Sonuç gerçekten olumludur: AAR'lar bir araştırma sorununu insan temel performansından (baseline) daha iyi çözdü. Sonuç ayrıca bu aşamanın geliştirdiği her endişeyi tek bir sistemde yoğunlaştırır. Uyumsuzluk araştırması otomatikleştirilebilirse, güvenlik önlemlerini (safeguards) tehlikeye atan kısımlar da otomatikleştirilebilir. RSP'nin AI R&D yetenik eşiği tam olarak bu döngüyü göz önünde bulundurarak yazılmıştır.

## Kavram

### Mimari (kamu açıklamasına göre)

- **Paralel agentlar.** Birden fazla Claude Opus 4.6 örneği (instance) AAR olarak çalışır, her biri bağımsız bir sandbox'ta. Sandbox'lar dosya sistemi, ağ ve süreç yüzeyini sınırlar.
- **Ortak forum.** Bulgular, depolama arka ucu her sandbox'ın dışında olan ortak bir foruma yayınlanır. Agentlar forumu okuyabilir; ancak kendi sandbox'larından forum kayıtlarını silemez veya düzenleyemez.
- **Görev dağıtımı.** İnsan tarafından tasarlanmış bir görev kuyruğu (task queue), araştırma sorunlarını AAR'lara atar. AAR'lar ayrıştırma önerileri sunar, deneyleri çalıştırır, bulguları yazar.
- **Zayıf-güçlü eğitim odağı.** Yayınlanan çalışma, zayıf-güçlü eğitimi ele almıştır — daha zayıf bir gözetmen (supervisor) modeliyle daha güçlü bir öğrenci (student) modeli eğitmek. AAR'lar bu görevde insan araştırmacıları geçti.

### Sandbox-dışında günlüğün (log) neden önemli olduğu

Günlük bütünlüğü özelliği (log integrity), kontrollü bir deneme ile potansiyel olarak tehlikeye girmiş bir deneme arasındaki farktır. AAR'lar kendi günlüklerini düzenleyebilseydi, başarısız veya şüpheli deneyleri örtbas edebilirlerdi. Anthropic bunu doğrudan belirtir: bu özellik, araştırma çıktısına güvenmenin gerekli bir koşuludur ve doğrulaması önemsiz değildir.

Altyapı terimleriyle karşılığı, harici depolamaya yazılan (write-through) yalnızca eklenen (append-only) günlüklerdir (ör. S3 nesne kilidi, değişmez Datadog günlükleri). Agent'ın geçmiş kayıtları değiştirmek için kimlik bilgisi (credential) yoktur. Bu, 2026 kurumsal güvenlik ekiplerinin fidye yazılımına (ransomware) dayanıklı denetim izleri (audit trails) oluşturmak için kullandığı aynı kalıptır.

### Belirlenmiş iş akışı takası (tradeoff)

Anthropic'in raporu, belirlenmiş iş akışlarının AAR esnekliğini sıklıkla kısıtladığını ve performansı düşürdüğünü not eder. Başka bir deyişle: insan tasarımcı araştırma planını adım adım yazarsa, AAR'lar yüksek düzey hedefler ve ayrıştırma özgürlüğü verildiğinden daha kötü performans gösterir. Bu, ajan araştırmasındaki (LangGraph, Microsoft'un Agent Framework) sonuçlarla tutarlı; aşırı tanımlanmış iskeletler, yetenekli agentlara zarar verir.

Güvenlik ima edilmesi incelidir. AAR performansını artıran esneklik, aynı zamanda yetkisiz ayrıştırma, yeni araç kullanımı ve hedef-sapmasına (goal-drift) izin veren esnekliktir. Takas bir tasarım alanı kararıdır: ne kadar esneklik, insanları geçecek kadar yetenek sağlar, ancak agent'a hedefleri dağıtım-dışına genelleştirmek için yer vermez?

### Sıkıştırma riski (compression risk)

RSP v3.0 (Ders 19), bir AI R&D yetenik eşiği sunar: insan + AI araçlarıyla rekabetçi maliyetle tam AI R&D hattını (pipeline) otomatikleştirme yeteneği. DeepMind'ın FSF v3'ü, paralel bir ML R&D otonomluk seviyesi içerir. Her iki çerçeve de bu eşiği yükseltilmiş kontroller için tetikleyici olarak ele alır.

AAR, bu eşiğin bir adım gerisidir: hattın bir kısmını (belirli, iyi tanımlanmış görevlerdeki uyumsuzluk araştırması) otomatikleştirir, ancak uçtan uca yetenek geliştirme döngüsünü değil. Zaman çizelgesi sorusu, boşluğun ne kadar hızlı kapandığıdır.

Sıkıştırılmış zaman çizelgeleri, birikimli hata (compounding failure) endişesidir. Uyumsuzluk araştırması ve yetenek araştırması benzer oranlarda birikirse, uyumsuzluk risk yüzeyi en az yetenek kadar hızlı büyür. Yetenek daha hızlı birikirse (tarihsel eğilim), boşluk genişler. Bu, AAR'ın nitelikli bir iyilik (qualified good) olarak savunulmasının argümanıdır: araştırma süreci güvenilir olduğu sürece, her ek uyumsuzluk sonucu boşluğu azaltır.

### AAR'ın yerini almadığı şeyler

İnsan araştırmacılar görev kuyruğunu belirler, sonuçları inceler ve anayasal yetkiyi (constitutional authority) elinde tutar. AAR'lar hattın orta kısmını hızlandırır, uçları değil. Anthropic'in yayımladığı çıktılar hem AAR katkılarını hem de neyin yayımlanacağı, neyin geri çekileceği ve neyin iyileştirileceği konusundaki insan araştırmacı yargılamasını içerir.

Bu, Ders 15'teki öneri-sonra-karar (propose-then-commit) kalıbının kendisine uygulanmasıdır: AAR'lar önerir; insanlar karar verir.

## Kullan

`code/main.py`, çoklu-AAR araştırma forumunu simüle eder. Üç bağımsız "research agent" paralel çalışır, bulguları opsiyonel tahrif (tamper) denemeleriyle yalnızca eklenen bir foruma gönderir.

Şunları izleyin:

- Sandbox-dışında günlüklemenin günlük tahrif denemelerini nasıl yakaladığını.
- Serbest ayrıştırma ile görev dağıtımının zor sorunlarda sabit iş akışlarını nasıl geçtiğini.
- Günlüğün tahrif-evident olmadığı durumda tek bir tehlikeye girmiş AAR'ın forumun sinyalini nasıl kirletebileceğini.

## Üret

`outputs/skill-aar-deployment-review.md`, otomatik uyumsuzluk araştırması hattı için bir önceden-dağıtım incelemesidir.

## Alıştırmalar

1. `code/main.py` dosyasını çalıştırın. "Sabit iş akışı" ve "serbest ayrıştırma" ayarlarını karşılaştırın. Serbest ayrıştırma her zaman kazanır mı, yoksa sabit iş akışının rekabetçi olduğu sorun sınıfları var mı?

2. Simülatörü bir agent'ın günlük tahrifine deneyecek şekilde değiştirin. Yalnızca eklenen günlüğün bunu tespit ettiğini doğrulayın. Günlükte tespit imzasının tam olarak nasıl göründüğünü açıklayan bir paragraf yazın.

3. Anthropic'in zayıf-güçlü AAR raporunu okuyun. AAR'ların insan araştırmacıları geçtiği belirli alt görevi belirleyin. Bunu otomatikleştirmeye uygun kılan şey neydi?

4. AAR esnekliği (daha iyi sonuçlar) ile belirlenmiş iş akışı kısıtlamaları (daha kolay denetim) arasında denge kuran bir görev kuyruğu dağıtım politikası tasarlayın. İkisi arasında nasıl A/B testi yapacağınızı açıklayın.

5. RSP v3.0'ın AI R&D-4 eşiğini okuyun. AAR'ın şu anda yapmadığı, bu eşiği aşacağını düşündüğünüz bir paragraf açıklayın.

## Anahtar Terimler

| Terim | Ne Söyleniyor | Aslında Ne Anlama Geliyor |
|---|---|---|
| AAR | "Otomatik Uyumsuzluk Araştırmacısı" | Uyumsuzluk sorunları üzerinde otonom olarak çalıştırılan Claude Opus 4.6 örneği |
| Zayıf-güçlü eğitim (Weak-to-strong training) | "Daha güçlü bir modeli daha zayıf bir gözetmenle eğitme" | AAR'ların insanları geçtiği klasik ölçeklenebilir gözetim benchmark'ı |
| Ortak forum (Shared forum) | "Agentların bulguları yayınladığı yer" | Yalnızca eklenen, sandbox-dışında depolama |
| Sandbox-dışında günlük (Out-of-sandbox log) | "Agent kendi kaydını düzenleyemez" | Harici depolamaya tahrif-evident write-through |
| Belirlenmiş iş akışı (Prescribed workflow) | "İnsan tasarımcıdan adım adım plan" | AAR'ı kısıtlar; serbest ayrıştırmaya kıyasla sıklıkla performansı düşürür |
| Serbest ayrıştırma (Free decomposition) | "Agent görevi nasıl ayırdığına karar verir" | Daha yetenekli, denetlenmesi daha zor |
| AI R&D eşiği (AI R&D threshold) | "RSP/FSF yetenek seviyesi" | Rekabetçi maliyetle R&D hattının tam otomasyonu |
| Sıkıştırılmış zaman çizelgesi (Compressed timeline) | "Uyumsuzluk vs yetenek yarışı" | Yetenek uyumsuzluktan daha hızlı birikirse, uyumsuzluk riski artar |

## İleri Okuma

- [Anthropic — Otomatik Zayıf-Güçlü Araştırmacı](https://alignment.anthropic.com/2026/automated-w2s-researcher/) — birincil kaynak.
- [Anthropic Sorumlu Ölçekleme Politikası v3.0](https://anthropic.com/responsible-scaling-policy/rsp-v3-0) — AI R&D eşiği çerçevesi.
- [Anthropic — AI Agent Otonomunu Ölçme](https://www.anthropic.com/research/measuring-agent-autonomy) — daha geniş agent-otonomluğu çerçevesi.
- [DeepMind Sınır Güvenlik Çerçevesi v3](https://deepmind.google/blog/strengthening-our-frontier-safety-framework/) — RSP'ye paralel ML R&D otonomluk seviyeleri.
- [Burns ve ark. (2023). Weak-to-Strong Generalization (OpenAI)](https://openai.com/index/weak-to-strong-generalization/) — AAR'ların saldırdığı temel sorun.
