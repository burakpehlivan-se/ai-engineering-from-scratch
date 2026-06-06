---
name: mcp-server-scaffolder
description: Doğru tools/resources/prompts ayrımı ve SDK terfi yoluyla domain'e özgü bir MCP server iskeleti kur.
version: 1.0.0
phase: 13
lesson: 07
tags: [mcp, server, fastmcp, scaffold]
---

Bir domain verildiğinde (notlar, ticket'lar, dosyalar, database, ne olursa), bir MCP server planı üret: hangi capability'lerin tool, hangilerinin resource, hangilerinin prompt olarak açılacağı, ayrıca Python veya TypeScript SDK'ya bir terfi (graduation) yolu.

Şunları üret:

1. Tool listesi. Kullanıcının açıkça yapılmasını istediği atomik operasyonlar. İsim, açıklama (Use-when deseni), input schema ve annotation ipuçlarını içer.
2. Resource listesi. Kullanıcının okumak istediği veri. URI scheme, mime type ve `resources/subscribe`'ın etkinleştirilip etkinleştirilmeyeceği.
3. Prompt listesi. Host'un slash-command olarak açması gereken tekrar kullanılabilir template'ler. Argüman listesi.
4. Capability deklarasyonu. Server'ın `initialize` içinde döndürdüğü tam `capabilities` objesi.
5. Graduation notları. Her parça için FastMCP (Python) veya TypeScript SDK eşdeğerleri. İskeletteki elle yazılmış bir stdlib desenini değiştiren bir SDK özelliğini (örneğin `lifespan`, `context`) adlandır.

Sert reject sebepleri:
- Yalnızca tool olarak sunulan ve resource olarak sunulmayan herhangi bir "database query". Doğru bölme şudur: `/list` ve `/read` için resource, parametrelerle `/query` için tool.
- Kullanıcı input'u alan tool'larla ayrıcalıklı olanları aynı namespace'te annotation olmadan karıştıran herhangi bir server.
- Dayanıklı bir notification mekanizması olmadan `resources/subscribe` capability'si iddia eden herhangi bir server iskeleti.

Refusal kuralları:
- Domain'in read-only yüzeyi yoksa, resource iskeletini reddet; sadece tool içeren bir server öner.
- Domain'in doğal slash-command template'leri yoksa, prompt iskeletini reddet.
- Kullanıcı bir auth scheme isterse reddet ve Faz 13 · 16'ya (OAuth 2.1) yönlendir.

Çıktı: üç primitive listesini, capability objesini ve 10 satırlık örnek bir `@app.tool()` decorator tarzı graduation snippet'ini içeren tek sayfalık bir server planı. Server'ın ayarlaması gereken en önemli annotation bayrağıyla bitir.
