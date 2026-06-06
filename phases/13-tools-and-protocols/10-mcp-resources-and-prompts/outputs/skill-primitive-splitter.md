---
name: primitive-splitter
description: Bir MCP server taslağındaki her capability'yi gerekçeli olarak tool, resource veya prompt olarak kategorize et.
version: 1.0.0
phase: 13
lesson: 10
tags: [mcp, primitives, resources, prompts]
---

Önerilen bir MCP server'ın capability'leri verildiğinde (düz İngilizce ya da taslak bir tool listesi olarak), her birini tek cümlelik bir gerekçeyle tool, resource veya prompt olarak kategorize et.

Şunları üret:

1. Capability başına kategorizasyon. Her öğe için `{name, primitive: tool | resource | prompt, rationale}` döndür.
2. Resource URI scheme. Herhangi bir capability resource olursa, bir URI scheme (`notes://`, `gh://`, `db://`) ve bir template deseni öner.
3. Prompt argüman iskeletleri. Herhangi bir capability prompt olursa, argüman listesini ve required/optional bayraklarını öner.
4. Subscription adayları. Sık değişen ve `resources/subscribe`'dan fayda görecek resource'ları işaretle.
5. Anti-pattern bayrakları. Eski tasarımın bir resource'un daha iyi hizmet edeceği yerlerde bir read'i tool olarak sardığı (örn. `notes_read(id)`) durumları belirt.

Sert reject sebepleri:
- Bölme olmadan "hem tool hem resource" olarak kategorize edilen herhangi bir capability. Birini seç ya da bir çift iskelet kur.
- Required argüman'ları tanımlanmamış herhangi bir prompt. Slash-command UI'larında yüzeylemek argüman schema'sı gerektirir.
- Adreslenebilir olmayan herhangi bir resource URI scheme'i (URI değil, serbest formatlı string'ler).

Refusal kuralları:
- Tüm capability'ler tool olarak konuyorsa, reddet ve server'ın resource olabilecek read-only verisinin olup olmadığını sor.
- Hiçbir capability prompt'a uymuyorsa, sorun yok; prompt'lar opsiyoneldir. Onları icat etme.
- Server'ın domain'i A2A (agent-to-agent collaboration, opak state) tarafından daha iyi karşılanıyorsa, reddet ve Faz 13 · 19'a yönlendir.

Çıktı: kategorizasyon tablosu, URI scheme önerisi, prompt iskeletleri ve subscription bayraklarını içeren tek sayfalık bir karar raporu. Bu server için en etkili tek tool -> resource dönüşümüyle bitir.
