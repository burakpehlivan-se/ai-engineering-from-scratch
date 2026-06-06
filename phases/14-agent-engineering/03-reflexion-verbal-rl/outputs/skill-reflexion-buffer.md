---
name: reflexion-buffer
description: TTL, dedup ve scoped scope ile verbal RL için bir reflection episodic-memory buffer'ı yönet.
version: 1.0.0
phase: 14
lesson: 03
tags: [reflexion, episodic-memory, self-healing, verbal-rl, sleep-time]
---

Bir task sınıfı verildiğinde (tekrarlayan agent çalıştırma türü — örn. "bir fonksiyonu refactor et," "bir destek ticket'ını kapat"), reflection'ların bir episodic-memory buffer'ını yönet. Her reflection bir başarısızlık modunu ve düzeltici insight'ı doğal dilde kaydeder. Buffer, aynı task sınıfının bir sonraki denemesine prepend edilir.

Şunları üret:

1. Reflection yakalama. Bir deneme bir evaluator skoru eşiğin altında biterek sona erdiğinde, "X yapmayı başaramadım çünkü Y; bir sonraki sefere, Z" şeklinde tek satırlık bir reflection yay. Tekrarlanabilir olmadıkça dış başarısızlıklarda (network, upstream 500'ler) reflection'ları at.
2. TTL ve dedup. Reflection'lar varsayılan olarak N denemeden sonra expire olur (10 önerilir). Tam tekrarlar collapse olur. Yakın tekrarlar (küçük bir embedding modelinde >0.9 cosine veya >= %80 paylaşılan substring) sadece en son olanı tutar.
3. Scope policy. Üç scope: task-class (task ismi başına), user (aynı kullanıcı için task'lar arasında), agent (tüm kullanıcılar arasında). Varsayılan task-class'tır. Sadece reflection kullanıcıya özgü tercihlere atıfta bulunuyorsa user scope'a escalate et; asla agent scope'a otomatik olarak escalate etme.
4. Compaction. Buffer budget'ı aştığında, sleep-time compaction çalıştır: yakın tekrarları cluster'la, özetle, birleştir. Compaction hot path dışında çalışır — birincil agent'ın yanıtını geciktirme.
5. Prompt entegrasyonu. "Önceki denemelerden öğrendiklerim" başlıklı, bullet'lı bir liste içeren tek bir block yay. Prompt'ta 6 öğeyle sınırla; taşma ayrı bir özet öğesine gider ("... ve timeout'lar hakkında 4 eski reflection daha").

Sert reject sebepleri:

- Reflection'ları "bir sonraki sefere daha dikkatli ol" olarak yazmak. Bu aksiyon alınabilir değildir. Reflector'ı somut bir bir sonraki sefer talimatı zorlayan bir prompt'la yeniden çalıştır.
- Reflection'ları trial sayısı yerine wall-clock zamanına dayalı olarak expire etmek. Offline-replayable çalıştırmalar için TTL trial-scoped olmalıdır, zaman-scoped değil.
- Secret'lara referans veren reflection'ları depolamak (API key'ler, token'lar, PII). Buffer'a commit etmeden önce spesifik bir "contains secret" sınıfı hatasıyla reject et.

Refusal kuralları:

- Hiçbir evaluator attach edilmemişse, reddet ve Ders 05'i (Self-Refine/CRITIC) öner — reflection bir sinyal gerektirir, sezgi değil.
- Task sınıfı one-shot ise (asla tekrarlamaz), reddet; episodic memory asla tekrarlamayan bir task için hiçbir şey yapmaz.

Çıktı: yapılandırılmış bir buffer dosyası (reflection objeleri ile JSON: trial id, task class, scope, text, created_at, ttl_remaining), bir sonraki deneme için bir prompt block'u ve yakında expire olacak girdileri listeleyen bir "stale reflections" raporu.

Buffer sürekli cap'ine ulaşıyorsa Ders 06'ya (context compression) veya compaction'ı hot path dışına taşımak için Ders 08'e (Letta sleep-time compute) işaret eden bir "sırada ne okumalı" notuyla bitir.
