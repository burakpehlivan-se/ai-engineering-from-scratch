---
name: cross-policy-diff
description: OpenAI Preparedness Framework v2, Anthropic RSP v3.0 ve DeepMind FSF v3 referans olarak kullanılarak belirli bir yetenek için çapraz-politika karşılaştırması üretin.
version: 1.0.0
phase: 15
lesson: 20
tags: [preparedness-framework, fsf, rsp, cross-policy, scaling-policy]
---

Belirli bir frontier yeteneği (örn. "uzun-menzilli otonomi", "otonom çoğalma ve adaptasyon", "Ar-Ge otomasyonu") verildiğinde, üç çerçevenin her birinin yeteneği nasıl sınıflandırdığını ve hangi azaltmaları tetiklediğini gösteren bir çapraz-politika farkı üretin.

Üretin:

1. **OpenAI PF v2 sınıflandırması.** Tracked veya Research. Tracked ise, Capabilities + Safeguards Report tetikleyicilerini adlandırın. Research ise, politika metninin "potansiyel" azaltmalar olduğunu not edin.
2. **Anthropic RSP v3.0 sınıflandırması.** Hangi eşik (ASL-3, AI R&D-4, sabit-kodlu yasak)? Hangi azaltma (olumlu durum, güvenlik + deployment)? Taahhüdün Anthropic-tek-taraflı kademesinde mi yoksa sektör-öneri kademesinde mi yaşadığını doğrulayın.
3. **DeepMind FSF v3 sınıflandırması.** Hangi domain (Cyber, Bio, ML R&D, CBRN)? Hangi CCL veya Tracked Capability Level? Yanıltıcı hizalama (deceptive alignment) izlemesi tetikleniyor mu?
4. **Yakınsama özeti.** Üç politika yeteneğin ciddiyeti konusunda anlaşıyor mu, yoksa anlamlı bir anlaşmazlık mı var? Hangi sınıflandırma en titiz, hangisi en az?
5. **Ölçüm bağımlılığı.** Her sınıflandırma yetenek ölçümüne bağlıdır. Yeteneğin nasıl ölçüldüğünü ve hangi eval sağlayıcısının (METR, Apollo, dahili, üçüncü-taraf) o ölçümü sahiplendiğini adlandırın.

Keskin redler:

- Belge düzeyinde kanıt olmadan duyuru-metni benzerliğine dayalı çapraz-politika hizalaması iddiaları.
- Kaynak belgede spesifik bir maddeye işaret edemeyen herhangi bir sınıflandırma.
- "Research Category"yi (OpenAI) "Tracked Category"yle eşdeğer olarak ele almak — farklı operasyonel sonuçları vardır.

Ret kuralları:

- Kullanıcı her sınıflandırma için kaynak belge pasajlarını üretemiyorsa, reddedin ve önce alıntıları isteyin.
- Kullanıcı politika-varlığını pratikte-azaltma kanıtı olarak ele alıyorsa, reddedin ve spesifik azaltmaların tetiklendiğine dair kanıt isteyin.
- Yetenek bir çerçeve tarafından "kapsanıyor" iddia ediliyorsa ancak kelime belgede geçmiyorsa, reddedin ve somut bir madde referansı isteyin.

Çıktı formatı:

Şunları içeren bir fark belgesi döndürün:

- **Yetenek tanımı** (tek cümle)
- **OpenAI PF v2 satırı** (sınıflandırma, tetik, kaynak madde)
- **Anthropic RSP v3.0 satırı** (sınıflandırma, tetik, tek-taraflı-vs-öneri)
- **DeepMind FSF v3 satırı** (domain, CCL / TCL, yanıltıcı-hizalama dahiliyeti)
- **Yakınsama özeti** (anlaşma + anlamlı anlaşmazlık)
- **Ölçüm sahipliği** (eval sağlayıcısı, eval kadansı)
- **Okuyucu önerisi** (en titiz, en az titiz, gerekçeli)
