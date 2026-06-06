---
name: durable-execution-review
description: Doğru dayanıklı-çalıştırma (durable-execution) şekli (aktiviteler, determinizm, checkpoint backend, insan girdi durumu, devam-ettirmede-HITL) için önerilen uzun-çalışan agent deployment'ını inceleyin.
version: 1.0.0
phase: 15
lesson: 12
tags: [durable-execution, workflows, checkpointing, temporal, langgraph, agents-sdk]
---

Önerilen uzun-çalışan bir agent deployment'ı (Temporal + OpenAI Agents SDK, PostgreSQL checkpointer'lı LangGraph, Microsoft Agent Framework, Claude Code Routines, Cloudflare Durable Objects veya kurum içi eşdeğeri) verildiğinde, tasarımı dayanıklı-çalıştırma (durable-execution) örüntüsüne karşı denetleyin.

Üretin:

1. **Aktivite envanteri.** Her aktiviteyi (LLM çağrısı, araç çağrısı, HTTP isteği, dosya yazımı) listeleyin. Her biri için, retry (yeniden deneme) politikası, zaman aşımı ve idempotency key (tekrar-koruma anahtarı) ile bir aktivite olarak sarıldığını doğrulayın. Aktivite zarfının dışındaki ham LLM çağrıları güvenilirlik deliğidir.
2. **İş akışı determinizmi.** İş akışı kodunun içindeki her deterministik-olmayan okumayı (duvar saati, rastgele, harici durum) tanımlayın. Her biri, replay (yeniden oynatma) aynı değeri döndürsün diye bir yan-etki aktivitesi olarak kayıt edilmelidir. Gizli deterministik-olmama, replay sürüklenmesinin en yaygın nedenidir.
3. **Checkpoint backend.** Backend'i adlandırın (PostgreSQL, SQLite, Redis, Durable Objects). Deploy'ları (production dağıtımları) hayatta tuttuğunu doğrulayın. SQLite yalnızca geliştirme içindir. Redis AOF veya snapshot yapılandırması gerektirir. Cloudflare Durable Objects şeffaftır ancak benzersiz anahtar disiplini gerektirir.
4. **İnsan girdi durumu.** HITL için duraklamaların birinci-sınıf iş akışı durumu olduğunu, yoklama döngüsü (polling loop) olmadığını doğrulayın. İş akışı, onay geldiğinde tam olarak devam eden harici bir sinyalde (onay kuyruğu, webhook, `interrupt()` ilkeli) bloke olmalıdır.
5. **Devam-ettirmede-HITL politikası.** Çökmeden sonra herhangi bir devam-ettirme için, bir sonraki aktiviteyi yürütmeden önce taze HITL'nin gerekli olup olmadığını belirtin. Bu olmadan, dayanıklı çalıştırma artı çökmeden önce verilen bir onay, bağlam değiştiğinde onaylanmış bir eylemi yeniden tetikleyebilir. Uzun horizon'lar için kritiktir.

Keskin redler:

- LLM çağrılarının aktivite olarak sarılmadığı Agent SDK kullanımı.
- Deploy'ları hayatta tutmayan checkpoint backend'leri.
- Duvar saatini veya rastgeleyi aktivite sarmalaması olmadan gömen iş akışları.
- Sinyal yerine yoklama döngüsü olarak modellenen insan girdisi.
- Devam-ettirmede-HITL politikası olmayan uzun horizon'lu (bir saatin üzerinde) çalıştırmalar.
- Dayanıklılığın üzerine katmanlanmış bütçe kill switch'i (Ders 13) olmayan çalıştırmalar.

Ret kuralları:

- Kullanıcı, yan-etki aktivitelerinde açık idempotency olmayan dayanıklı bir iş akışı öneriyorsa, reddedin ve önce idempotency key'leri isteyin. Yoksa retry'lar çift-çalıştıracak.
- Kullanıcı bir replay testi gösteremiyorsa (iş akışını çalıştır, ortasında çök, replay et, çift yan etki olmadığını doğrula), reddedin ve production'dan önce o testi isteyin.
- Kullanıcı HITL kontrol noktası olmayan 24 saatlik gözetimsiz bir çalıştırma öneriyorsa, reddedin. 35 dakikalık bozulma (Ders 12 notları) bunu dayanıklılık doğru olsa bile bir güvenilirlik sorunu yapar.

Çıktı formatı:

Şunları içeren bir tasarım-inceleme memo'su döndürün:

- **Aktivite tablosu** (aktivite, retry politikası, zaman aşımı, idempotency key)
- **Determinizm denetimi** (deterministik-olmayan okumalar ve her birinin nasıl ele alındığı)
- **Checkpoint backend** (ad, deploy-hayatta-mı e/h, replay-test durumu)
- **HITL durum şekli** (birinci-sınıf durum / yoklama / eksik)
- **Devam-ettirmede-HITL politikası** (açık, gerekçeyle)
- **Hazırlık** (production / staging / yalnızca-araştırma)
