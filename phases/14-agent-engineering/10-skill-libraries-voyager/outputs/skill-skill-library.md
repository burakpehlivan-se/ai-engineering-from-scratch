---
name: skill-library
description: Kayıt, benzerlikle retrieval, kompozisyonel execution ve başarısızlık-güdümlü refinement ile Voyager şekilli bir skill kütüphanesi üret.
version: 1.0.0
phase: 14
lesson: 10
tags: [voyager, skills, library, composition, refinement]
---

Bir hedef runtime ve bir domain verildiğinde, Voyager'ın üç bileşenini destekleyen bir skill kütüphanesi üret: curriculum hook, geri çağrılabilir skill store, iteratif refinement.

Şunları üret:

1. `name`, `description`, `code`, `version`, `tags`, `depends_on`, `history` ile `Skill` tipi. Her write önceki kodu kaydeder.
2. `register(skill, dedup=True)` (yeni veya version bump), `search(query, top_k, tag_filter)`, `get(name)`, `topo_order(name)` (dep resolution), `execute(name, context)` (topological run) ile `SkillLibrary`.
3. Retrieval, tüm kütüphane üzerinde LLM puanlaması değil, embedding similarity veya BM25 KULLANMALIDIR. LLM yeniden sıralama, top-k shortlist'te izin verilir.
4. Execution, skill başına exception'ları MUTLAKA yakalayıp refinement loop'unun tüketebileceği geri bildirim olarak trace'e yüzeylemelidir.
5. Bir refinement hook'u: başarısız bir `execute`'tan sonra, runtime (task, skill_name, error, env_state) toplar, bunu modele iletir ve yeniden yazılan skill'de `register` çağırır. Version bumplar; history eski kodu korur.

Sert reject sebepleri:

- Skill'lerin kod değil nesir string'leri olduğu bir kütüphane. Skill'ler executable'dır. Nesir `description`'a aittir.
- Topological sort olmadan kompozisyon. Cycle detection'sız depth-first, skill DAG'larında bozulur.
- Sessiz version üzerine yazma. Her refinement MUTLAKA `version`'ı bumplamalı ve eski kodu denetim için `history`'ye push etmelidir.

Refusal kuralları:

- Hedef runtime'da skill execution için sandbox yoksa, skill'lerin production sistemlere dokunduğu domain'ler için reddet. Gönderim öncesi bir sandbox gerektir (Ders 09 ilkeleri).
- Kullanıcı "refinement olmadan her başarısızlıkta auto-retry" isterse, reddet. Refinement'sız retry'lar bug'ı amplifiye eder; düzeltmez.
- Kütüphane düz retrieval ile ~200 skill'i aşarsa, "production-ready" olarak adlandırmayı reddet. Önce tag filtreleri ve hiyerarşik namespace'ler ekle.

Çıktı: `skill.py`, `library.py`, `execute.py`, `refine.py` ve dedup kuralını, retrieval backend'ini, refinement prompt'unu ve version policy'sini açıklayan bir `README.md`. Claude Agent SDK entegrasyonu için Ders 17'ye, OpenAI Agents SDK tool çevirisi için Ders 16'ya veya skill-library kalitesini değerlendirmek için Ders 30'a işaret eden bir "sırada ne okumalı" ile bitir.
