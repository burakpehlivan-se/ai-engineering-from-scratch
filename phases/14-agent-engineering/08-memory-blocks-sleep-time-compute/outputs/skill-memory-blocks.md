---
name: memory-blocks
description: Kritik path dışında bir sleep-time consolidation agent ile Letta şekilli üç katmanlı bir memory sistemi (core block'lar, recall, archival) üret.
version: 1.0.0
phase: 14
lesson: 08
tags: [memory, letta, blocks, sleep-time, consolidation]
---

Bir hedef runtime, bir primary model ve (muhtemelen daha güçlü) bir sleep-time model verildiğinde, açık block türleri ve async consolidation içeren üç katmanlı bir memory sistemi üret.

Şunları üret:

1. `label`, `value`, `limit`, `description`, `version`, `history` içeren `Block` tipi. Her write version'ı bumplar ve eski değeri kaydeder. `near_limit(threshold=0.8)`'i açığa çıkar.
2. En az üç varsayılan block içeren bir `BlockStore`: `human` (kullanıcı hakkında gerçekler), `persona` (agent self-concept'i) ve `task` (mevcut scope). Kullanıcı tanımlı block'lara izin ver.
3. Bir `Recall` store — session ile paginate edilen turn log'u. Her turn'da auto-write. Tail cap'te evict olur ama geri çağrılabilir kalır.
4. Bir `Archival` store — en az iki backend (vector, KV). Insert kayıt id'sini döndürür. Çelişkide sil yerine invalidate et.
5. Turn'leri halleden ve sadece raw write'lar yapan bir `PrimaryAgent`. Kritik path'te özetleme yok.
6. Turn'ler arasında çalışan bir `SleepTimeAgent`: eşiğin üzerindeki block'ları özetle, çelişen archival kayıtlarını invalidate et, paylaşılan block'lara `learned_context` yaz.

Sert reject sebepleri:

- Doğrudan bir lookup hariç, kullanıcı-yüzlü bir turn sırasında senkron çalışan herhangi bir memory op. Özetleme, consolidation, invalidation sleep-time geçişine aittir.
- Çelişkide archival kayıtlarını silmek. Geçmiş denetlenebilir kalsın diye invalidate et.
- Persona veya Safety block'una bir review adımı olmadan yazmak. Bu block'lar davranışı global olarak şekillendirir; sessiz write'lar bug'ları maskeler.

Refusal kuralları:

- Runtime block'ları session'lar arasında kalıcılaştıramıyorsa, "memory" olarak tanımlanan bir ürün göndermeyi reddet. İddiayı düşür.
- Sleep-time agent'ın trace çıktısı yoksa, reddet. Sessiz consolidation bir debugging ölü bölgesidir.
- Kullanıcı "invalidation yok, her zaman en son write'a güven" isterse, geçmiş iddiaların önemli olduğu herhangi bir domain için reddet (compliance, medical, legal).

Çıktı: component başına bir dosya artı varsayılan block'ları, sleep-time cadence'ini ve çelişki çözüm policy'sini adlandıran bir `README.md`. Agent memory üzerinde graph reasoning'e ihtiyaç duyuyorsa Ders 09'a veya ürün memory op'larında OTel span'larına ihtiyaç duyuyorsa Ders 23'e işaret eden bir "sırada ne okumalı" ile bitir.
