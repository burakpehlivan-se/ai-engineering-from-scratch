---
name: handoff-designer
description: Bir Swarm/Agents-SDK-stili sistem için devir topolojisi tasarlayın: hangi agent'lar var, hangi devirleri çağırabilirler, hangi bağlam aktarılır.
version: 1.0.0
phase: 16
lesson: 11
tags: [multi-agent, swarm, handoff, openai-agents-sdk]
---

Kullanıcıya dönük bir görev (genellikle triyaj veya beceri-tabanlı yönlendirme) verildiğinde, OpenAI Swarm veya OpenAI Agents SDK'ya eşlenmeye hazır bir devir topolojisi üretin.

Üretin:

1. **Agent listesi.** Her agent: ad, tek cümlelik amaç, araçlar ve hangi diğer agent'lara devir yapabilir.
2. **Devir fonksiyonları.** Agent başına araç imzaları. Her devir fonksiyonu bir hedef Agent döndürür.
3. **Bağlam aktarım politikası.** Her devir kenarında: tam tarihçe, son N mesaj veya özetlenmiş anlık görüntü. Gerekçelendirin.
4. **Koruma rayları.** Agent başına girdi doğrulaması (hangi promptlar hassas uzmanlara devre izinlidir), gerektiğinde devirde kimlik doğrulama.
5. **Döngü tespiti.** Ping-pong tespit etme kuralı (örn. "A, B'ye devretti; B, A'ya geri devretti" bir kereden fazla arka arkaya gerçekleşti).
6. **Geri-dönüş davranışı.** Bir devir hedefi eksikse (kaldırılmış agent, auth hatası), oturumu hangi agent yönetir.
7. **Oturum / bellek planı.** Agents SDK oturumlarını, arayan-tarafından-yönetilen belleği mi yoksa hiç bellek olmamasını mı kullanacağı.

Keskin redler:

- Döngü tespiti olmayan herhangi bir devir tasarımı.
- Farklı araç izinlerine sahip uzmanlara tam tarihçeyi aktaran devir fonksiyonları (güvenlik riski).
- Swarm'ın durumsuz davranışını varsayan ancak sonra çok-turlu bellek gerektiren tasarımlar — bunun yerine Agents SDK oturumlarını kullanın.

Ret kuralları:

- Görev paralel yürütme gerektiriyorsa, Swarm'ı reddedin ve bunun yerine denetçi (Ders 05) önerin.
- Görev deterministik denetim/replay gerektiriyorsa, reddedin ve LangGraph statik grafik önerin.
- Görev aşamaların basit bir DAG'i ise (araştırma → kod → inceleme), bunun yerine CrewAI Sequential önerin.

Çıktı: Tek sayfalık devir özeti. Prompt injection'ın istenmeyen devirleri nasıl tetikleyebileceği ve hangi koruma raylarının onu engellediği konusunda bir güvenlik notuyla kapatın.
