---
name: mcp-apps-spec
description: İnteraktif bir UI resource'una ihtiyaç duyan bir tool için tam MCP Apps kontratını üret.
version: 1.0.0
phase: 13
lesson: 14
tags: [mcp, apps, ui-resources, csp, iframe-sandbox]
---

İnteraktif bir UI'dan fayda görecek bir tool verildiğinde (timeline, form, dashboard, harita, chart), MCP Apps kontratını üret.

Şunları üret:

1. `ui://` URI. UI resource için tek bir kanonik isim (örn. `ui://notes/timeline`).
2. Tool result shape. `text` preamble ve `ui_resource` block içeren `content[]`; `_meta.ui` doldurulmuş.
3. CSP. `default-src`, `script-src`, `connect-src`, `img-src`, `style-src` için minimum allowlist. Gerekmedikçe `'unsafe-inline'`'dan kaçın.
4. Permissions listesi. Gerekirse kamera / mikrofon / geolocation / network; gerekmiyorsa boş.
5. postMessage giriş noktaları. UI'ın yapacağı `host.*` çağrıları ve neyi döndürdükleri.
6. Güvenlik kontrol listesi. Host'tan ayırt edilebilirlik, no clickjacking, sıkı connect-src, herhangi bir kullanıcı içeriği render ediliyorsa HTML sanitizasyonu.

Sert reject sebepleri:
- `default-src *` içeren CSP. Geniş açık güvenlik riski.
- UI'ın gerçekten kullandığının ötesindeki herhangi bir `permissions` talebi. Minimum privilege.
- Dış script yükleyen herhangi bir ui:// resource'u. Bundle et veya reddet.
- Sanitizasyon olmadan kullanıcı kontrolünde HTML render eden herhangi bir UI. XSS vektörü.

Refusal kuralları:
- UI sadece statik bir sonuç ise, App iskeleti kurmayı reddet; text içerik döndür.
- Tool, native host widget'larından (progress bar, confirmation dialog) fayda görecekse, bunları öner.
- Host henüz MCP Apps'i desteklemiyorsa (2026-04 itibarıyla VS Code stable, Zed, Windsurf), text'e fallback yolunu işaretle.

Çıktı: `ui://` URI'ı, tool result JSON'u, CSP, permissions, postMessage giriş noktaları ve bir güvenlik kontrol listesi içeren tek sayfalık bir kontrat. Bu UI'ı render edecek minimum host'u belirten tek bir cümleyle bitir.
