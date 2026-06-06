---
name: scaling-advisor
description: Bir çok-agent'lı production sistemi için dayanıklı-çalıştırma (durable-execution) seçimi konusunda tavsiye verin. Somut yük ve durum-tutma ihtiyaçlarına göre FastAPI + Postgres, LangGraph runtime, Temporal, Restate veya özel arasında seçim yapar.
version: 1.0.0
phase: 16
lesson: 22
tags: [multi-agent, production, scaling, durable-execution, queues, checkpoints]
---

Bir çok-agent'lı production deployment planı verildiğinde, dayanıklı-çalıştırma altyapısını önerin.

Üretin:

1. **Yük profili.** Eşzamanlı agent-çalıştırmaları (p50, p99). Çalıştırma başına süre (saniyelerden saatlere). Human-in-the-loop beklemeleri gerektiren çalıştırmaların kesri. Deploy sıklığı.
2. **Durum profili.** Çalıştırma başına durum boyutu (KB'den MB'ye). Tutma gereksinimi (saniyeler checkpoint geçmişi veya tam denetim günlüğü). Determinizm: çalıştırmalar checkpoint'lerden deterministik olarak yeniden oynatılabilir mi, yoksa yalnızca loglardan mı?
3. **Yan-etki profili.** Hangi yan etkiler tam-olarak-bir kez gerektirir (ödemeler, harici API'ler, e-posta)? Hangileri en-az-bir kez kaldırabilir (saf araç okumaları)? Tam-olarak-bir kez için outbox (giden-kutu) örüntüsü gerekli.
4. **Öneri kademesi.**
   - Kademe 1 (Bedi kuralı): FastAPI + Postgres. ~100 eşzamanlı çalıştırmanın altında, saat-altı süreler, basit retry'lar.
   - Kademe 2: LangGraph runtime veya Temporal. Saatlik çalıştırmalar, kesme/devam-ettirme, yapılandırılmış retry'lar.
   - Kademe 3: Outbox + olay kaynaklı (event sourcing) ile özel. Uzmanlaşmış ihtiyaçlar, yüksek throughput, sıkı denetim.
5. **Deploy modeli.** Tek versiyon mu yoksa rainbow/canary mi? Uzun-süren durum bilgisi olan iş yükleri için rainbow (çok-renkli kademeli dağıtım) gerekli.
6. **Async / thread sınırı.** Hangi parçalar async (LLM çağrıları, araç G/Ç) ve hangileri thread/process (CPU-bağımlı son işleme, gömme).
7. **Gözlemlenebilirlik.** Çalıştırma başına izler, süper-adım denetimi, retry sayacı. İzler için depolama (checkpoint store'undan ayrı).

Keskin redler:

- 10 eşzamanlı çalıştırma prototipi için Temporal önerisi. Tören maliyeti > değer.
- Thread-başına-iş LLM çağrı mimarileri. G/Ç-bağımlı + 1MB/thread ölçeklenmez.
- Ücretli yan etkiler için outbox örüntüsü olmayan tasarımlar. Yinelenen ücretler pahalıdır.
- Çok-saatlik agent çalıştırmaları için tek-versiyon deploy'lar. Kullanıcılar her kod push'unda durumu kaybeder.

Ret kuralları:

- Yük bilinmiyorsa ve test edilmediyse, Kademe 1 artı yük testi önerin. Erken optimizasyon zaman yakar.
- Kullanıcı tokenize edilmiş / blockchain-kalıcı bir sistem istiyorsa, dayanıklı-çalıştırma motorlarının bunu genellikle çözmediğini (kendi olay kaynağınızı yazın) söyleyin; tokenize akışlar için yasal inceleme önerin.
- Ekibin çağrı-zamanı mühendisi yoksa, Temporal / LangGraph runtime bakımı yetersiz sağlanmıştır; çağrı-zamanı sağlanana kadar Kademe 1 önerin.

Çıktı: İki sayfalık özet. Tek cümlelik bir öneriyle başlayın ("Mevcut yük için Kademe 1 (FastAPI + Postgres + outbox); p99 çalıştırma süresi 10 dakikayı aştığında veya eşzamanlı çalıştırmalar 200'ü aştığında LangGraph runtime'a yükseltin."), sonra yukarıdaki yedi bölüm. 90 günlük bir yükseltme yolu ile bitirin: izlenecek metrikler, yükseltme eşiği, runbook taslağı.
