---
name: ecosystem-blueprint
description: Bir ürün ihtiyacı verildiğinde tam bir Faz 13 ekosistem mimarisi üret; primitive'leri, güvenlik duruşunu, telemetri'yi ve paketlemeyi adlandır.
version: 1.0.0
phase: 13
lesson: 22
tags: [mcp, capstone, ecosystem, architecture, a2a, otel]
---

Bir ürün ihtiyacı verildiğinde (araştırma, özetleme, otomasyon, herhangi bir agent-güdümlü workflow), tam mimariyi üret.

Şunları üret:

1. MCP primitive'leri. Hangi tools, resources, prompts ve task'lara ihtiyaç var. `ui://` app'leri var mı? Async task'lar var mı?
2. Güvenlik duruşu. OAuth 2.1 scope kümesi, gateway RBAC matrisi, pinli hash manifest'i, Rule of Two denetimi.
3. A2A collaboration. Herhangi bir sub-agent çağrısını tanımla. Onların Agent Card'larını tanımla.
4. Telemetri. OTel GenAI span hiyerarşisi. Exporter ve backend seçimi.
5. Paketleme. AGENTS.md, SKILL.md ve deployment yüzeyi (Docker Compose, K8s).
6. Faz 13 derslerine eşleme. Her tasarım seçiminin hangi derse geri izlendiği.

Sert reject sebepleri:
- Tek bir turda güvenilmez input, hassas veri ve consequential action'ı birleştiren herhangi bir mimari (Rule of Two).
- MCP ve A2A hop'larında trace propagation'ı olmayan herhangi bir mimari.
- LLM katmanında en az bir fallback provider'a sahip olmayan herhangi bir mimari.

Refusal kuralları:
- Ürün ihtiyacı doğrudan bir LLM çağrısıyla daha iyi karşılanıyorsa, tam ekosistemin iskeletini kurmayı reddet.
- Ekibin gateway için SRE'si yoksa, managed bir gateway öner (Cloudflare MCP Portals, Portkey).
- Mimari ödemeleri içeriyorsa, AP2'yi drift riskli bir A2A extension'ı olarak işaretle ve ayrı bir onay öner.

Çıktı: primitive'ler, güvenlik duruşu, A2A hop'ları, telemetri planı, paketleme ve ders haritası içeren tek sayfalık bir blueprint. Deployment için tek en zor operasyonel riski tanımlayan bir cümleyle bitir.
