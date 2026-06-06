---
name: tool-registry
description: JSON Schema doğrulaması, parallel dispatch ve observability ile bir production tool kataloğu ve registry oluştur.
version: 1.0.0
phase: 14
lesson: 06
tags: [function-calling, tools, schema, validation, bfcl, parallel-tools]
---

Bir task domain'i verildiğinde, bir agent'ın BFCL V4 eksenleri (agentic, multi-turn, live, non-live, hallucination) genelinde güvenilir şekilde kullanabileceği bir tool kataloğu üret.

Şunları üret:

1. Tool tanımları. Her tool için: `name` (snake_case), `description` (modele ne zaman kullanması ve ne zaman KULLANMAMASI gerektiğini söyler), tipli property'ler ve required field'lar içeren JSON Schema input, uygun olduğunda enum'lar, sayısallar için minimum/maximum, tool başına timeout, tool başına sandbox policy (fs surface, network, memory cap).
2. Açıklama kalite kontrolü. Her açıklamayı "bu, modele bu tool'u diğerleri yerine ne zaman seçmesi gerektiğini söylüyor mu?" sorusundan geçir. İki tool'un örtüşen açıklamaları varsa, reddet ve yeniden yaz.
3. Parallel-dispatch planı. Her gerçekçi task için, hangi tool çağrılarının bağımsız (paralelleştirilebilir) ve hangilerinin sıralı olması gerektiğini tanımla. Beklenen bir dispatch graph'ı yay.
4. Doğrulama policy'si. Enum check'ler, type coercion kuralları (örn. "int-as-string kabul et, float-as-string reddet"), required-field zorunluluğu. Her başarısızlık yapılandırılmış bir observation string döndürür, asla loop'a fırlatmaz.
5. Observability. Her tool, `gen_ai.tool.name`, `gen_ai.tool.call.id`, `gen_ai.tool.call.arguments`, `gen_ai.tool.call.result` (content policy gerektirdiğinde inline değil referans) attribute'larıyla bir OpenTelemetry GenAI `tool_call` span'ı yayar.

Sert reject sebepleri:

- Generic shell/command-exec tool. Reddet ve spesifik fiillere böl (`git_status`, `fs_read`, `npm_test`).
- Parametrenin kapalı bir değer kümesi olduğunda enum eksik olması. Enum doğrulaması, drift'i yakalamanın en ucuz yoludur.
- İki farklı tool için aynı açıklama. Model bunlar arasında güvenilir şekilde seçim yapamaz.
- Sadece tool'u adlandıran (`description` ("İki sayı ekler"). Alternatiflere göre NE ZAMAN seçilmesi gerektiğini ekle.
- Timeout yok. Her tool çağrısının bir tavanı olmalıdır.

Refusal kuralları:

- Tool listesi tek bir agent için 30 tool'u aşarsa, reddet ve subagent delegasyonu öner (Ders 17).
- Herhangi bir tool, onay kapısı olmadan yıkıcı bir eylem gerçekleştiriyorsa, reddet ve Ders 09'a (izinler, sandboxing) yönlendir.
- Task computer use ise (click, type, screenshot), reddet ve Ders 21'e yönlendir — bu, vision-tabanlı eylemlerle ayrı bir tool shape'idir.

Çıktı: Anthropic / OpenAI / Gemini SDK çağrılarına yapıştırılmaya hazır bir JSON tool kataloğu, bir dispatch-graph diyagramı, bir doğrulama policy dokümanı ve registry'nin geçmesi gereken BFCL tarzı bir mini-eval.

Bir "sırada ne okumalı" işaretçisiyle bitir: Ders 09 (sandboxing), Ders 23 (OTel GenAI span'ları) veya Ders 30 (eval-driven).
