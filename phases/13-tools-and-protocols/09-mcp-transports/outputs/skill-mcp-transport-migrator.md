---
name: mcp-transport-migrator
description: Eski HTTP+SSE'den, session id sürekliliği ve Origin doğrulamasıyla Streamable HTTP'ye geçiş için bir migration planı üret.
version: 1.0.0
phase: 13
lesson: 09
tags: [mcp, streamable-http, sse-migration, session-id, origin]
---

Mevcut bir HTTP+SSE (legacy) MCP server'ı verildiğinde, tek-endpoint Streamable HTTP'ye geçiş için bir migration planı üret.

Şunları üret:

1. Endpoint yeniden yazımı. `/messages` ve `/sse`'yi tek bir `/mcp` altında birleştir. POST'u request handling'e, GET'i SSE stream'e, DELETE'i session sonlandırmaya eşle.
2. Session sürekliliği. İlk POST'ta yeni `Mcp-Session-Id` üret. Client tarafından sağlanan id'leri reddet. Client önce bir legacy session cookie'si gönderirse, bridging logic'ini koru.
3. Origin doğrulaması. Açık production origin'lerini allowlist'e al (`https://app.company.com`, `https://claude.ai`, localhost varyantları). Diğer hepsini 403 ile reddet.
4. Last-event-id replay. Oturum başına son event'lerin bir ring buffer'ını tut, böylece yeniden bağlanmalar devam edebilsin.
5. Deprecation penceresi. Geçiş tarihini ve eski endpoint'lerin uyarı header'ı ile yeni olanına 301 yaptığı 60 günlük bir grace period belgele.

Sert reject sebepleri:
- Her iki endpoint'i süresiz olarak hayatta tutan herhangi bir plan. Legacy SSE 2026'da kaldırılıyor.
- Session id'lerin client tarafından üretildiği herhangi bir plan. Cryptographic-randomness gerekliliğini bozar.
- Origin doğrulaması olmayan herhangi bir plan. DNS-rebinding güvenlik açığı.

Refusal kuralları:
- Server yalnızca yerel ise (stdio), HTTP'ye migrate etmeyi reddet; stdio yerel için doğrudur.
- Server henüz OAuth göndermiyorsa, public olarak açmadan önce Faz 13 · 16'yı tamamla.
- Hosting hedefi uzun ömürlü HTTP'yi desteklemiyorsa (örn. Vercel free tier), reddet ve Cloudflare Workers öner.

Çıktı: endpoint değişikliklerini, Origin allowlist'ini, session-id planını, deprecation takvimini ve initialize, tools/list, streaming notification'ları, last-event-id ile yeniden bağlanma ve açık DELETE'i kapsayan bir test kontrol listesini içeren bir migration runbook.
