---
name: fipa-mapper
description: Herhangi bir 2026 agent-protokolü spesifikasyonunu (MCP, A2A, ACP, ANP, CA-MCP, NLIP veya yeni bir tane) FIPA-ACL performative'lerine ve etkileşim protokollerine eşleyerek neyin gerçek yenilik neyin yeniden icat olduğuna karar verin.
version: 1.0.0
phase: 16
lesson: 02
tags: [multi-agent, protocols, FIPA, speech-acts, interoperability]
---

Yeni bir agent-protokolü spesifikasyonu verildiğinde, okuyucunun hangi parçaların yeniden icat hangilerinin gerçek yeni yapı olduğunu anlayabilmesi için FIPA-ACL eşlemesini üretin.

Üretin:

1. **Zarf eşlemesi.** Spesifikasyonun tanımladığı her mesaj türü için, en yakın FIPA performative'ini adlandırın (`inform`, `request`, `query-if`, `query-ref`, `propose`, `accept-proposal`, `reject-proposal`, `cfp`, `subscribe`, `cancel`, `failure`, `not-understood` veya diğer ~20'den biri). Hiçbir performative uymuyorsa, boşluğu kesin olarak tanımlayın.
2. **Korelasyon modeli.** Spesifikasyon, istekleri yanıtlara, iptali orijinal isteğe ve akış olaylarını subscribe'a nasıl ilişkilendiriyor? FIPA'nın `:conversation-id` ve `:reply-with` alanlarıyla karşılaştırın.
3. **İçerik-dili duruşu.** Spesifikasyon bir içerik şeması (tipli artefaktlar, JSON-Schema) zorunlu kılıyor mu, doğal dili mi kabul ediyor, yoksa açık mı bırakıyor? FIPA'nın SL0/SL1 ve ontoloji alanlarıyla karşılaştırın.
4. **Etkileşim-protokolü kütüphanesi.** Spesifikasyonun üzerine hangi FIPA etkileşim protokolleri uygulanabilir: contract-net, subscribe-notify, request-when, propose-accept? Her birini uygulayacak mesajları adlandırın.
5. **Keşif modeli.** Bir agent muhatap ve yetenekleri nasıl bulur (MCP `listTools`, A2A Agent Card, ANP DID + meta-protokol)? FIPA'nın directory facilitator ve yellow-pages servisiyle karşılaştırın.
6. **Yeniden icat vs yenilik.** Üç sütunlu kısa bir tablo üretin: [FIPA kavramı, modern spesifikasyon eşdeğeri, ne değişti]. Her satırı [reinvention] veya [novel-structure] olarak işaretleyin. Bir satır, ancak spesifikasyon FIPA'nın sahip olmadığı bir ilkel sunuyorsa "novel-structure"dur — merkezi olmayan kimlik, tipli multimodal artefaktlar ve LLM-yorumlanabilir içerik yaygın adaylardır.

Keskin redler:

- Spesifikasyonun FIPA'nın sahip olmadığı bir ilkel göstermeden "devrimci" olduğunu iddia eden herhangi bir eşleme. Speech-act teorisi + ontoloji yükü başarısızlık moduydu, ilkeller değil.
- Keşif katmanını göz ardı eden framework karşılaştırmaları. Keşfi olmayan bir spesifikasyon eksik, yeni değildir.
- "Protokol X, FIPA'nın yerini alıyor" gibi, iki agent içerik anlamı konusunda anlaşamazsa ne olacağını ele almayan ifadeler (anlamsal sürüklenme).

Ret kuralları:

- Spesifikasyon ön-standardizasyon aşamasındaysa (taslak < 6 aylık, genel uygulama yok), eşlemenin geçici olduğunu belirtin ve en olası üç değişikliği işaretleyin.
- Spesifikasyon kapalı-kaynak veya yalnızca-kurumsal ise (bazı ACP çeşitleri), belgelenen şeyi eşleyin ve boşlukları adlandırın.
- Kullanıcı yalnızca bir blog gönderisi sağlıyorsa (spesifikasyon belgesi yok), eşlemeden önce spesifikasyonu isteyin.

Çıktı: Tek sayfalık bir özet. Tek cümlelik bir özetle başlayın ("Protokol X, JSON sözdizimi ve DID tabanlı keşif katmanıyla FIPA `request`/`subscribe`'tır."), sonra yukarıdaki altı bölüm, sonra şu soruyu yanıtlayan kapanış paragrafı: "Bu spesifikasyon hangi eski FIPA başarısızlık modunu yeniden keşfedecek?"
