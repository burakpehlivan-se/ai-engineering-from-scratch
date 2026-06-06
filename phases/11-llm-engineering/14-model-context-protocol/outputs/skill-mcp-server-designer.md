---
name: mcp-server-designer
description: Araçlar, kaynaklar ve güvenlik varsayılanlarıyla bir MCP sunucusu tasarlayın ve iskeletini oluşturun.
version: 1.0.0
phase: 11
lesson: 14
tags: [llm-engineering, mcp, tool-use]
---

Size bir alan (dahili API, veritabanı, dosya kaynağı) ve sunucuyu barındıracak konaklar verildiğinde, çıktı:

1. Primitif haritası. Hangi yetenekler `tools` (eylem), hangileri `resources` (salt okunur veri), hangileri `prompts` (kullanıcı çağrılı şablonlar) olur. Her primitif için bir satır.
2. Kimlik doğrulama planı. Stdio (güvenilir yerel), API anahtarlı akışlanabilir HTTP (streamable HTTP), veya PKCE ile OAuth 2.1. Seçin ve gerekçelendirin.
3. Şema taslağı. Her araç parametresi için JSON Şeması, model araç seçimi için ayarlanmış `description` alanlarıyla (API dokümanları için değil).
4. Yıkıcı eylem listesi. Durumu değiştiren her araç; `destructiveHint: true` ve insan onayı gerektirir.
5. Test planı. Araç başına: bir yalnızca şema sözleşme testi, bir MCP istemcisi üzerinden gidiş-dönüş testi, bir kırmızı takım prompt enjeksiyonu vakası.

Onay yolu olmadan diske yazan veya harici API'leri çağıran bir sunucuyu göndermeyi reddedin. Tek bir sunucuda 20'den fazla araç sunmayı reddedin; bunun yerine alan kapsamlı sunuculara bölün.
