---
name: mcp-server-platform
description: StreamableHTTP, OAuth 2.1 kapsamları, OPA politikası, yıkıcı araçlar için insan-onay geçidi ve keşif için bir kayıt defteri (registry) ile üretim bir MCP sunucusu dağıt
version: 1.0.0
phase: 19
lesson: 13
tags: [capstone, mcp, fastmcp, streamablehttp, oauth, opa, registry, governance]
---

Bir kurumsal ortam verildiğinde, 10 dahili araçlı bir MCP sunucusu, keşif için bir kayıt defteri hizmeti ve yıkıcı araçları Slack onayıyla geçitlendiren bir yönetişim katmanı gönder.

İnşa planı:

1. FastMCP sunucusu, 10 salt-okunur aracı (Postgres, S3, Jira, Linear, Datadog, PagerDuty, GitHub, Notion, Slack, Salesforce) yazı tipli şema ve gerekli kapsamla aç.
2. StreamableHTTP taşıma, yük dengeleyici arkasında durumsuz.
3. OAuth 2.1 belirteç içe-bakış (introspection) ara yazılımı; SPIFFE / SPIRE ile iş yükü kimliği.
4. Her araç çağrısında OPA / Rego politika kararları: kapsam zorlama, PII sansürleme, yük boyutu kapakları.
5. Yıkıcı araçlar (Jira create, Linear create, Postgres write) ayrı bir MCP sunucusunda, 15 dakika içinde Slack kartıyla yükseltilen `approved:by:human` kapsamı gerektirir.
6. Her sunucudan `.well-known/mcp-capabilities` yoklayan, JSON Schema ile doğrulayan ve bir list/search/validate/enable UI'ı sunan kayıt defteri hizmeti.
7. Yazma öncesi Presidio PII sansürlemesiyle kiracı başına JSONL denetim günlüğü.
8. 100-istemcili yük testi yatay ölçeği gösterir; MCP uygunluk paketini geçer.

Değerlendirme rubriği:

| Ağırlık | Kriter | Ölçüm |
|:-:|---|---|
| 25 | Şartname uygunluğu | StreamableHTTP + yetenek manifesti MCP uygunluk testlerini geçer |
| 20 | Güvenlik | Kapsam zorlama, her araçta OPA kapsamı, sır hijyeni |
| 20 | Gözlemlenebilirlik | Yazma üzerinde PII sansürlemesiyle araç başına denetim günlüğü |
| 20 | Ölçek | Yatay ölçek gösterisiyle 100-istemcili yük testi |
| 15 | Kayıt defteri UX | Keşfet / doğrula / etkinleştir-devre dışı bırak iş akışı çalıştırılmış |

Kesin redler:

- Durumsuz oturumlar gerektiren sunucular (2026 StreamableHTTP durumsuz sözleşmesini ihlal eder).
- Yıkıcı araçların salt-okunur olanlarla aynı kimlik yüzeyini paylaştığı tek-sunucu topolojisi.
- Ham PII'yi kalıcı yapan denetim günlükleri.
- Yetenek manifestini yok sayma; kayıt defteri entegrasyonu sert gereksinimdir.

Ret kuralları:

- OAuth olmadan dağıtmayı reddet; anonim erişim diskalifiye edicidir.
- Slack onay akışı olmadan yıkıcı araçları göndermeyi reddet.
- Kapsamı veya açıklaması yetenek manifestinde olmayan bir aracı açmayı reddet.

Çıktı: İki MCP sunucusunu (salt-okunur + yıkıcı), kayıt defteri hizmetini, Slack onay entegrasyonunu, OPA politikalarını, 100-istemcili yük testi iskeletini, uygunluk testi sonuçlarını ve açmayı düşündüğünüz ancak açmadığınız araçları (ve neden) ve kuru-çalışma sırasında yakın-kaçırmaları yakalayan en iyi üç OPA kuralını açıklayan bir yazıyı içeren bir depo.
