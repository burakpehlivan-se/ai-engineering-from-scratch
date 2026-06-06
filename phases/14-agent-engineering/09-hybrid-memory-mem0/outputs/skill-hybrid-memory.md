---
name: hybrid-memory
description: Fusion scorer, scope taksonomisi ve temporal invalidation ile Mem0 şekilli üç-depolu bir memory sistemi (vector + KV + graph) üret.
version: 1.0.0
phase: 14
lesson: 09
tags: [memory, mem0, vector, graph, kv, fusion, scope]
---

Bir hedef runtime, bir vector backend (Qdrant, pgvector, Chroma, sqlite-vec), bir KV backend (Postgres, Redis, dict) ve bir graph backend (Neo4j, in-memory edge'ler) verildiğinde, fused bir memory sistemi üret.

Şunları üret:

1. Bir `add(text, user_id, session_id, scope, importance, tags)` facade'ı arkasındaki üç store class'ı. Write'ta extractor, `text`'i kayıtlara, KV triple'larına ve graph triple'larına ayrıştırır. Hiçbir store opsiyonel değildir.
2. Bir fusion scorer `score = w_rel * relevance + w_imp * importance + w_rec * recency`. Üç ağırlığı da config olarak açığa çıkar. Çağrı başına değil, ürün başına tune et.
3. Scope taksonomisi: `user`, `session`, `agent`. Retrieval scope'a MUTLAKA saygı göstermelidir. Bir kullanıcı sorgusu başka bir kullanıcının kayıtlarını asla sızdırmamalıdır.
4. Temporal invalidation. Çelişkiler eski edge'leri/kayıtları geçersiz olarak işaretler; asla silmez. Geçmiş sorgular için `search(query, as_of=timestamp)`'ı açığa çıkar.
5. Bir extractor interface'i. Varsayılan LLM-güdümlü olabilir; testler için deterministik bir regex fallback'e izin ver. Patlama önlemek için `add()` başına graph edge'lerini cap'le.

Sert reject sebepleri:

- "Mem0 şekilli" olarak tanımlanan tek-depolu memory. Yalnızca vector, yalnızca KV, yalnızca graph ürünler iyidir ama hibrit memory değildir. Onları yanlış adlandırma.
- Scope başına ağırlıklar veya açık bir `scope=` filtresi olmadan cross-scope retrieval. Scope sızıntısı bir compliance ve privacy olayıdır.
- Çelişkide silme. Invalidate et ve time-stamp ver. Silme bug'ları gizler ve audit'leri bozar.

Refusal kuralları:

- Kullanıcı "importance ağırlıklandırması yok" isterse, reddet. Bir milyon kayıt üzerinde düz relevance ranking, olmak üzere olan bir retrieval başarısızlığıdır.
- Graph backend'in conflict detector'ı yoksa, ortaya çıkan sistemi "Mem0 şekilli" olarak adlandırmayı reddet. İsmi düşür.
- Ürün PII içeriyorsa (medical, legal, HR), ürün sahibi tarafından denetlenmemiş bir extractor ile göndermeyi reddet.

Çıktı: store başına bir dosya artı `memory.py` (facade), `config.py` (ağırlıklar), fusion ağırlıklarını, scope policy'sini, extractor kontratını ve invalidation semantiğini açıklayan `README.md`. Agent yeni skill'ler öğrenmeye ihtiyaç duyuyorsa Ders 10'a, memory op'larında OTel span'ları gerekiyorsa Ders 23'e veya retrieval'da güvenilmez-input işleme için Ders 27'ye işaret eden bir "sırada ne okumalı" ile bitir.
