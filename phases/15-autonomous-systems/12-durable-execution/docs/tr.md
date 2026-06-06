# Uzun Süreli Arka Plan Agentları: Dayanıklı Çalıştırma (Durable Execution)

> Üretimdeki uzun vadeli agent'lar `while True` içinde çalışmaz. Her LLM çağrısı checkpoint, retry ve replay ile bir etkinliğe (activity) dönüşür. Temporal'ın OpenAI Agents SDK entegrasyonu Mart 2026'da GA'ya çıktı. Claude Code Routines (Anthropic), kalıcı bir yerel sürecin olmadığı programlanmış Claude Code çağrılarını çalıştırır. Oturumlar insan girişinde durur, deploy'lardan sağ çıkar ve `thread_id` ile indekslenen en son checkpoint'ten devam eder. Yeni kullanım kolaylığının arkasında eski bir kalıp vardır — iş akışı orkestrasyonu (workflow orchestration) — ancak yeni bir girdiyle: LLM çağrıları artık belirsiz (nondeterministic) etkinliklerdir ve kurtarma sırasında deterministik olarak yeniden oynatılmalıdır.

**Tür:** Öğrenme
**Diller:** Python (stdlib, minimal dayanıklı çalıştırma durum makinesi)
**Önkoşullar:** Faz 15 · 10 (İzin modları), Faz 15 · 01 (Uzun vadeli agent'lar)
**Süre:** ~60 dakika

## Sorun

Dört saat çalışan bir agent'ı düşünün. Üç araç çağırır, kullanıcıyı iki kez uyarır ve kırk LLM çağrısı yapar. Çalışmanın ortasında, üzerinde çalıştığı sunucu yeniden başlar. Ne olur?

- Basit bir `while True` döngüsünde: her şey kaybolur. Çalışma sıfırdan başlar. Üç araç çağrısı (gerçek yan etkilerle) tekrar çalışır. Kullanıcı zaten onayladığı şeyler için tekrar uyarılır. Kırk LLM çağrısı tekrar faturalandırılır.
- Dayanıklı çalıştırma ile: çalışma en son checkpoint'ten devam eder. Tamamlanmış etkinlikler tekrar çalışmaz; sonuçları dayanıklı log'dan yeniden oynatılır (replay). Kullanıcı zaten onayladığı şeyleri tekrar onaylamaz. Yapılmış olan LLM çağrıları tekrar faturalandırılmaz.

Bu, iş akışı motorlarının (Temporal, Cadence, Uber'ın Cherami) on yıldır sunduğu aynı kalıptır. Yeni olan, LLM çağrılarının artık bir tür etkinlik olmasıdır — belirsiz, pahalı ve yan etkili — ve bu kalıba sorunsuzca oturmasıdır.

Dersin tekrar eden teması: uzun vadeli güvenilirlik (reliability) düşer (METR "35 dakika bozulma" (35-minute degradation) gözlemler — başarı oranı yaklaşık karesel olarak ufukla düşer). Dayanıklı çalıştırma, güvenilirlik profilinin izin verdiği süreden daha uzun çalışmalar sağlar; bu, tasarım doğruysa güvenli bir hata verme yolu, yanlışsa güvensiz bir hata verme yoludur.

## Kavram

### Etkinlikler, iş akışları ve yeniden oynatma

- **İş akışı (Workflow):** deterministik orkestrasyon kodu. Etkinliklerin sırasını, dallanmaları ve bekleme sürelerini tanımlar. Olay logundan (event log) yeniden oynatılabilmek için deterministik olmalıdır.
- **Etkinlik (Activity):** belirsiz, başarısız olabilim iş birimi. LLM çağrısı, araç çağrısı, dosya yazma, HTTP isteği. Her etkinlik girdileriyle (ve tamamlandığında çıktıyla) birlikte loglanır.
- **Olay logu (Event log):** dayanıklı arka depo. Her etkinlik başlatma, tamamlama, hata, yeniden deneme ve her iş akışı kararı kaydedilir.
- **Yeniden oynatma (Replay):** kurtarma sırasında iş akışı kodu baştan çalıştırılır; zaten tamamlanmış her etkinlik tekrar çalıştırılmadan loglanmış sonucunu döndürür. Sadece tamamlanmamış etkinlikler çalıştırılır.

Bu, React'ın sanal DOM'a karşı yeniden işleme (re-render) veya Git'in commit'lerden çalışma ağacını (working tree) yeniden oluşturmasıyla aynı şekildir. Orkestratördeki determinizm, dayanıklılığı ucuza mal eder.

### Neden LLM çağrıları bu kalıba uyuyor

LLM çağrıları:
- Belirsizdir (sıcaklık (temperature) > 0; sıcaklık 0 olsa bile model sürümleri arasında sapar).
- Pahalıdır (para ve gecikme (latency)).
- Başarısız olabilir (hız sınırları (rate limits), zaman aşımları).
- Yan etkilidir (araç çağrısı yapıyorlarsa).

Bu tam olarak etkinlik profilidir. Her LLM çağrısını bir etkinlik olarak sarmak, üstel geriye doğru bekleme (exponential backoff) ile yeniden deneme, yeniden başlatmalar arası checkpoint ve hata ayıklama için yeniden oynatılabilir bir iz (trace) sağlar.

### `thread_id` ile indekslenen checkpoint'ler

LangGraph, Microsoft Agent Framework, Cloudflare Durable Objects ve Claude Code Routines aynı API biçiminde birleşti: bir `thread_id` (veya eşdeğeri) oturumu tanımlar; her durum geçişi bir arka plana (PostgreSQL varsayılan, geliştirme için SQLite, önbellek için Redis) kalıcı hale gelir; devam etme en son checkpoint'i okur.

Arka plan seçimi önemlidir:

- **PostgreSQL:** dayanıklı, sorgulanabilir, deploy'lardan sağ çıkar. LangGraph için varsayılan.
- **SQLite:** sadece yerel geliştirme; sunucular arası veri kaybı.
- **Redis:** hızlı ancak AOF/anlık görüntü (snapshot) yapılandırılmazsa geçici.
- **Cloudflare Durable Objects:** şeffaf şekilde dağıtılmış; benzersiz bir anahtarla kapsamlı; saatlerden haftalara kadar sağ kalır.

### İnsan girdisi birinci sınıf durum olarak

Öner-sonra-uygula (propose-then-commit) (Ders 15) dayanıklı bir "insan bekliyor" durumu gerektirir. İş akışı durur, harici kuyruk bekleyen isteği tutar ve onay tam olarak o noktadan devam eder. Dayanıklılık olmadan bu en iyi çabayken (best-effort), dayanıklılıkla gece gelen bir onay sabah iş akışını devam ettirir.

### 35 dakika bozulması

METR, ölçülen her agent sınıfının ~35 dakikalık sürekli çalışma sonrasında güvenilirlik düşüşü gösterdiğini gözlemledi. Görev süresini iki katına çıkarmak başarısızlık oranını yaklaşık olarak dört katına çıkarır. Dayanıklı çalıştırma bunu düzeltmez; güvenilirlik profilinin izin verdiği süreden daha uzun çalıştırmanızı sağlar. Güvenli kalıp, dayanıklılığı yeniden girişte taze insan-döngüde (HITL) kontrolü gerektiren checkpoint'lerle ve duvar saatinden (wall-clock time) bağımsız olarak toplam hesaplama bütçesini sınırlayan bütçe durdurma anahtarlarıyla (kill switches) (Ders 13) birleştirmektir.

### Dayanıklı çalıştırmanın yanlış cevap olduğu durumlar

- İnsan girdisi olmadan birkaç dakikadan kısa çalışmalar. Yük > fayda.
- Katı salt okunur bilgi erişimi.
- Doğruluğun tek bir bağlam penceresi (context window) içinde uçtan uca çalışmasını gerektiren görevler (bazı akıl yürütme görevleri; bazı tek-atımlı üretimler).

## Kullan

`code/main.py`, stdlib Python'da minimal bir dayanıklı çalıştırma motoru uygular. Şunları destekler:

- Girdileri ve çıktıları JSON olay loguna kaydeden `@activity` dekoratörü.
- Etkinlikleri sıralayan bir iş akışı fonksiyonu.
- Tamamlanmış etkinlikleri tekrar çalıştırmadan yeniden oynatmak için `run_or_replay(workflow, event_log)` fonksiyonu.

Sürücü, üç etkinlikli bir iş akışını simüle eder, ortasında çöker ve (a) basit yeniden denemenin her şeyi tekrar çalıştırmasına karşılık (b) yeniden oynatmanın sadece eksik etkinliği çalıştırmasını gösterir.

## Üret

`outputs/skill-durable-execution-review.md`, önerilen bir uzun çalışma agent dağıtımını doğru dayanıklı çalıştırma biçimi için inceler: etkinlikler, determinizm, checkpoint arka planı, insan girdisi durumu ve devam etmede HITL ilkesi.

## Alıştırmalar

1. `code/main.py` çalıştırın. Basit yeniden deneme ile yeniden oynatma arasındaki etkinlik çalışma sayısındaki farkı gözlemleyin. Çökme noktasını değiştirin ve yeniden oynatma sayısının buna göre değiştiğini gösterin.

2. Oyuncak motoru açıkça `thread_id` kullanacak şekilde dönüştürün. Motoru paylaşan eşzamanlı iki oturumu simüle edin ve olay loglarının çakışmadığını doğrulayın.

3. Oyuncak motorda bir etkinlik alın. Bir belirsizlik (bir iş akışı kararındaki duvar saati zaman damgası) ekleyin. Yeniden oynatmada sapmayı gösterin. Gerçek motorların bunu nasıl ele aldığını açıklayın (yan etki kaydı, `Workflow.now()` API'leri).

4. LangChain "Runtime behind production deep agents" yazısını okuyun. Çalışma ortamının (runtime) kalıcı hale getirdiği her durumu listeleyin ve her birinin hangi başarısızlık modunu ele aldığını adlandırın.

5. 6 saatlik otonom kodlama görevi için bir checkpoint ilkesi tasarlayın. Nerede checkpoint alırsınız? Çökmede devam etme nasıl görünür? Hangi durumlarda taze HITL gerekir?

## Anahtar Terimler

| Terim | Ne Söyleniyor | Aslında Ne Anlama Geliyor |
|---|---|---|
| Workflow (İş akışı) | "Agent'ın betiği" | Deterministik orkestrasyon kodu; olay logundan yeniden oynatılabilir |
| Activity (Etkinlik) | "Bir adım" | Belirsiz birim (LLM çağrısı, araç çağrısı); öncesi ve sonrası loglanır |
| Event log (Olay logu) | "Arka depo" | Her durum geçişinin dayanıklı kaydı |
| Replay (Yeniden oynatma) | "Devam" | İş akışını yeniden çalıştır; tamamlanmış etkinlikler tekrar çalıştırılmadan loglanmış sonucu döndürür |
| Checkpoint (Kontrol noktası) | "Kayıt noktası" | thread_id ile indekslenen kalıcı durum; devam etmede en son kazanır |
| thread_id | "Oturum anahtarı" | Dayanıklı durumu kapsamlı kılan tanımlayıcı |
| 35 dakika bozulması | "Güvenilirlik düşüşü" | METR: başarı oranı yaklaşık karesel olarak ufukla düşer |
| Belirsizlik (Non-determinism) | "Yeniden oynatmada sapma" | Duvar saati, rastgelelik, LLM çıktısı; yan etki olarak kaydedilmelidir |

## İleri Okuma

- [Anthropic — Claude Code Agent SDK: agent loop](https://code.claude.com/docs/en/agent-sdk/agent-loop) — bütçe, turlar ve devam etme anlamları.
- [Microsoft — Agent Framework: insan-döngüde ve checkpoint'ler](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) — RequestInfoEvent biçimi.
- [LangChain — Üretimdeki Derin Agentların Çalışma Ortamı](https://www.langchain.com/conceptual-guides/runtime-behind-production-deep-agents) — somut çalışma ortamı gereksinimleri.
- [OpenAI Agents SDK + Temporal entegrasyonu (Trigger.dev duyurusu)](https://trigger.dev) — LLM çağrıları için etkinlik biçimi.
- [Anthropic — Pratikte agent otonomunu ölçme](https://www.anthropic.com/research/measuring-agent-autonomy) — 35 dakika bozulma referansı.
