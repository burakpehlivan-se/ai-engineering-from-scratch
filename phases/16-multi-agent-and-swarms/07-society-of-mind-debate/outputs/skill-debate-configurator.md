---
name: debate-configurator
description: Belirli bir görev için çok-agent'lı bir tartışma (debate) yapılandırın, çalıştırmadan önce kalite kazanımını ve token maliyetini tahmin edin.
version: 1.0.0
phase: 16
lesson: 07
tags: [multi-agent, debate, society-of-mind, consensus]
---

Bir soru veya görev verildiğinde, herhangi bir agent framework'ünde (LangGraph, AutoGen, özel döngü) çalıştırılmaya hazır bir tartışma yapılandırması üretin.

Üretin:

1. **Görev-uyum kontrolü.** Bu görev consensus (fikir birliği) ile iyileştirilebilir mi? Tartışma akıl-yürütme, gerçeklik ve ayrıştırmaya yardımcı olur; zaten deterministik olan (aritmetik, kod derleme) veya tamamen üretken (yaratıcı yazım) görevlere yardımcı olmaz.
2. **Agent sayısı.** 3, 4 veya 5. Varsayılan 3; 4+ yalnızca maliyet-duyarsız ve görev daha çeşitli görüşler gerektiriyorsa.
3. **Tur sayısı.** 2 veya 3. Varsayılan 3; nadiren daha fazla. Du ve ark.'nın platosunu gösterin.
4. **Heterojenlik.** Aynı temel model (daha basit, daha ucuz, daha ilişkili hatalar) veya karışık aile (Llama + Claude + GPT; ilişkisizleştirir; daha pahalı, yönlendirme katmanı gerektirir).
5. **Rol ataması.** Simetrik (tüm agent'lar aynı role sahip) veya tek-karşıt (bir agent'a anlaşmamak talimatı verilmiş). Karşıt yuva, dalkavukluk kaskadlarına karşı ucuz bir sigortadır.
6. **Birleştirme yöntemi.** Çoğunluk oyu (ayrık yanıtlar), ağırlıklı ortalama (sayısal) veya LLM-hakem sentezi (açık-uçlu).
7. **Maliyet tahmini.** N agent × R tur × tur başına medyan token. Mevcut sağlayıcı fiyatlandırmasıyla dolar tahminini belirtin.

Keskin redler:

- Somut bir maliyet gerekçesi olmadan 5'ten fazla agent veya 3'ten fazla tur içeren herhangi bir yapılandırma.
- Bilinen dalkavukluk riski olan görevlerde yalnızca simetrik tartışmalar.
- Deterministik bir doğrulayıcısı olan görevler için tartışma (derleme, test, kesin matematik) — bunun yerine doğrulayıcıyı çalıştırın.

Ret kuralları:

- Görev basit gerçek aramasıysa, reddedin ve retrieval-augmented (erişimle zenginleştirilmiş) tek-agent önerin.
- Görev üretkense (şiir yaz), reddedin — tartışma çıktıları ortalamaya doğru çeker.
- Kullanıcı token/dolar bütçesi belirlememişse, reddedin ve bir tane isteyin. Tartışma, tek-agent maliyetinin 5-15 katıdır.

Çıktı: Tek sayfalık yapılandırma özeti. Görev-uyum kontrolüyle başlayın, toplam maliyet tahminiyle kapatın.
