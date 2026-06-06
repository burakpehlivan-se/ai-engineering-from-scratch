---
name: elicitation-form-designer
description: Çağrı ortasında kullanıcı onayı veya belirsizlik giderme gerektiren bir tool için elicitation form schema'sını ve mesaj template'ini tasarla.
version: 1.0.0
phase: 13
lesson: 12
tags: [mcp, elicitation, user-input, forms]
---

Davranışı çağrı ortasında kullanıcı input'u gerektirebilen bir tool verildiğinde, elicitation schema'sını ve mesajını tasarla.

Şunları üret:

1. Trigger condition. Tool'un `elicitation/create` çağırmasına neden olması gereken tam input ya da belirsizliği belirt.
2. Mesaj template'i. Host'un kullanıcıya gösterdiği tek bir cümle. Sade, spesifik, jargon'dan arınmış.
3. Schema. Türlendirilmiş property'ler ve `enum` listesi (belirsizlik giderme için) veya `boolean` (onay için) içeren düz JSON Schema. Nest etme.
4. Branch handling. `accept` / `decline` / `cancel` durumlarını tool davranışlarına eşle.
5. Rate-limit kuralı. Tool invocation başına elicitation'ları sınırla; asla bir loop içinde elicit etme.

Sert reject sebepleri:
- Object'leri nest eden herhangi bir schema. Elicitation v1 düzdür.
- LLM'in nesir olarak sorabileceği eksik bir argümanı doldurmak için kullanılan herhangi bir elicitation.
- Yüksek frekanslı herhangi bir elicitation (tool çağrısı başına birden fazla).

Refusal kuralları:
- Tool read-only ve düşük riskli ise, elicit etmeyi reddet ve sadece sonucu döndür.
- Tool yıkıcı ve host `destructiveHint` annotation'larını destekliyorsa, annotation kullanmayı ve onayı client'ın native olarak halletmesini öner.
- İhtiyaç bir OAuth sign-in ise, URL-mode elicitation öner ve SEP-1036 drift riskini işaretle.

Çıktı: trigger condition, mesaj template'i, schema, branch handling, rate-limit kuralı ve form mode'un mu URL mode'un mu daha uygun olduğuna dair bir notla birlikte tek sayfalık bir tasarım.
