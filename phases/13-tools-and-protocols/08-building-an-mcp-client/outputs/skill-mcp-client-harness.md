---
name: mcp-client-harness
description: MCP server'ların (isim, komut, args) deklaratif bir listesi verildiğinde, handshake, namespace birleştirme ve routing içeren bir multi-server client iskeleti kur.
version: 1.0.0
phase: 13
lesson: 08
tags: [mcp, client, multi-server, routing, namespace]
---

Çalıştırılacak MCP server'ların konfigürasyonu verildiğinde, her birini spawn eden, her biriyle handshake yapan, tool listelerini tek bir namespace'te birleştiren ve her çağrıyı sahip server'a yönlendiren bir client harness üret.

Şunları üret:

1. Server konfigürasyon parser'ı. `name -> {command, args, env}` eşle. Komutların path üzerinde var olduğunu doğrula.
2. Spawn planı. `bufsize=1`, text mode olacak şekilde stdin/stdout/stderr pipe'ları ile subprocess. Popen kullan. Server başına bir arka plan reader thread'i.
3. Handshake pipeline'ı. Her oturum için: `initialize` gönder, response'u bekle, capability'leri kalıcılaştır, `notifications/initialized` gönder.
4. Namespace birleştirme. Bir çakışma policy'si seç: `prefix-on-collision` (varsayılan), `reject-on-collision` veya `silent-overwrite` (yasak). Startup'ta birleştirilmiş bir tool listesi yazdır.
5. Routing fonksiyonu. `client.call(canonical_name, arguments)` sahip oturumu arar ve bir `tools/call` mesajı yazar. Pending-request tablosunda bir future üzerinden eşleşen-id response'unu await eder.

Sert reject sebepleri:
- Her server'ı kendi process'inde spawn etmeyen herhangi bir harness. Process içi multiplexing, izolasyon modelini bozar.
- Varsayılan çakışma policy'si `silent-overwrite` olan herhangi bir harness. Güvenlik riski.
- Stdout read'lerinde ana thread'i bloklayan herhangi bir harness. Notification'lar takılır.

Refusal kuralları:
- Bir server'ın komutu güvenilmez ise (pinli bir allowlist'te değilse), spawn etmeyi reddet ve güvenlik kontrolü için Faz 13 · 15'e yönlendir.
- Kullanıcı bir gerekçe olmadan 10'dan fazla server konfigüre ediyorsa, uyar ve bir gateway öner (Faz 13 · 17).
- Burada OAuth'u yönetmen istenirse reddet ve Faz 13 · 16'ya yönlendir.

Çıktı: Session, merge logic, routing ve konfigüre edilmiş her server'ı çalıştıran bir main loop içeren tam bir client-harness Python dosyası (~150 satır). Çakışma policy'sini ve birleştirilmiş tool sayısını adlandıran tek satırlık bir özetle bitir.
