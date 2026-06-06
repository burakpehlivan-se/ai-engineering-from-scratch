---
name: supervisor-designer
description: Belirli bir araştırma-tarzı sorgu için bir denetçi/orchestrator-işçi sistemi tasarlayın: ana prompt, işçi rolleri, ayrıştırma kuralları ve sentez şablonu belirleyin.
version: 1.0.0
phase: 16
lesson: 05
tags: [multi-agent, supervisor, orchestrator, anthropic-research, langgraph]
---

Paralel alt-agent araştırmasından fayda gören bir kullanıcı sorgusu verildiğinde, herhangi bir framework'e (LangGraph, OpenAI Agents SDK, CrewAI Hierarchical) bağlanmaya hazır bir denetçi-örüntüsü tasarımı üretin.

Üretin:

1. **Karmaşıklık tahmini.** Bu sorgu basit mi (1 agent, 3-10 araç çağrısı), orta (2-4 işçi), yoksa karmaşık mı (5+ işçi)? Anthropic'in çaba-ölçeklendirme sezgiseli'ni (scale-effort heuristic) kullanarak tek cümleyle gerekçelendirin.
2. **Ana sistem promptu.** Şunları içermelidir: (a) ayrıştırma talimatları, (b) sentez talimatları, (c) ana'nın ham kaynak içeriği asla okumadığı, yalnızca işçi özetlerini okuduğu açık kuralı.
3. **İşçi sistem promptları. Her rol için bir tane, her biri dar kapsamını ve ana'nın beklediği çıktı formatını adlandıran. **

4. **Alt-soru ayrıştırma kuralları.** Ana sorguyu nasıl böler? Önce-geniş-sonra-dar, yoksa doğrudan ayrıştırma? Bir alt-soruyu ne diskalifiye eder (diğeriyle örtüşme, çok geniş)?
5. **Sentez şablonu. Açık çakışma-yönetimi kuralı: iki işçi çelişkili gerçekler döndürürse, sentez sessizce birini seçmek yerine anlaşmazlığı yüzeye çıkarmalıdır. **

6. **Model eşleştirmesi.** Ana için hangi model (akıl-yürütme kademesi), işçiler için hangisi (daha hızlı/ucuz kademe). Ödünleşimi açıklayın.
7. **Gözlemlenebilirlik gereksinimleri.** Minimum iz noktaları: plan, her işçi başlangıcı/bitişi, sentez girdisi, sentez çıktısı.

Keskin redler:

- Ana'nın kendisinin araç kullandığı herhangi bir tasarım. Ana yalnızca planlar ve sentezler.
- Kapsam kaymasına izin veren işçi promptları (örn. "X ile ilgili her şeyi araştır" bir sınır olmadan).
- Çakışmaları gizleyen sentez şablonları.

Ret kuralları:

- Sorgu basitse (toplamda 10'un altında araç çağrısı tahmini), tasarımı reddedin ve tek-agent önerin. Anthropic'in 15× token maliyeti bulgusunu gösterin.
- Sorgu sıralıysa (adım 2 adım 1'in çıktısına ihtiyaç duyuyor), reddedin ve bunun yerine pipeline/zincir örüntüsü önerin.
- Kullanıcı determinizm ve denetim için optimize ediyorsa, denetçiyi reddedin ve LangGraph statik grafik önerin.

Çıktı: Tek sayfalık tasarım özeti. Karmaşıklık tahmini ve örüntü-uyum kararıyla ("denetçi uyar") başlayın. Sistem sürekli çalışacaksa, rainbow-deployment (çok-renkli kademeli dağıtım) hatırlatmasıyla kapatın.
