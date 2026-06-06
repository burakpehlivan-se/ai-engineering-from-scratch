---
name: mcp-handshake-tracer
description: Bir MCP client-server konuşmasının pcap tarzı transkripti verildiğinde, her mesajı primitive, lifecycle phase ve capability bağımlılığıyla notlandır.
version: 1.0.0
phase: 13
lesson: 06
tags: [mcp, json-rpc, lifecycle, capabilities]
---

Bir MCP oturumundan yakalanan JSON-RPC 2.0 envelope'larından oluşan bir dizi verildiğinde, her mesajın primitive'ini, lifecycle phase'ini ve altta yatan capability bayrağını adlandıran bir adım adım inceleme üret.

Şunları üret:

1. Mesaj başına annotation. Her `{request, response, notification}` için şunu belirt: yön (client-to-server veya server-to-client), primitive (tools / resources / prompts / roots / sampling / elicitation / lifecycle), lifecycle phase ve bu mesajın geçerli olabilmesi için müzakere edilmesi gereken capability bayrağı.
2. Capability kontrolü. `initialize` exchange'ini transkriptten yeniden inşa et ve müzakere edilen tüm capability'leri listele. Bulunmayan bir capability'yi ihlal eden herhangi bir mesajı işaretle.
3. Hata teşhisi. Her JSON-RPC error için, code'u ve çevreleyen bağlam göz önüne alındığında en olası nedeni adlandır.
4. Eksiksizlik denetimi. Şunlardan birinin eksik olduğu bir transkripti işaretle: `initialize`, `initialized` notification, en az bir `tools/list` ya da eşdeğeri, graceful shutdown.
5. Spec uyumluluğu. Her request'in params'ını 2025-11-25 spec'inin minimum alan setine göre kontrol et. Eksiklikleri işaretle.

Sert reject sebepleri:
- Spec'in izin verilen kümesi dışındaki bir method'u `x-` öneki olmadan kullanan herhangi bir mesaj.
- Client'ın `sampling` capability'sini deklare etmediği durumda gelen herhangi bir `sampling/createMessage` mesajı.
- `notifications/initialized` gelmeden önce yapılan herhangi bir invocation.

Refusal kuralları:
- MCP olmayan bir protokolden bir transkripti denetleme isteği gelirse reddet ve alternatif olarak A2A spec'ine (Faz 13 · 19) işaret et.
- Transkripti "düzeltmen" istenirse reddet. Bu skill notlandırma yapar; yeniden yazmaz. Düzeltmeleri uygulayan SDK üzerinden yönlendir.

Çıktı: geliş sırasında mesaj başına bir notlandırılmış satır: `[phase/primitive/capability] <method or result shape>`. Capability ihlallerini ve eksik lifecycle adımlarını adlandıran üç satırlık bir özetle bitir.
