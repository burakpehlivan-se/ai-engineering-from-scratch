---
name: groupchat-selector
description: Bir görev için AutoGen/AG2-stili GroupChat seçici yapılandırın: seçici varyantını, sonlandırmayı ve sıcak-konuşmacıya-karşı kuralları adlandırın.
version: 1.0.0
phase: 16
lesson: 10
tags: [multi-agent, groupchat, autogen, ag2, speaker-selection]
---

Bir görev ve agent listesi verildiğinde, bir GroupChat yapılandırması üretin: seçici seçimi, seçici girdileri, sonlandırma kuralları ve koruma rayları.

Üretin:

1. **Seçici varyantı.** Round-robin (ucuz, adil, bağlam-kör), LLM-seçimli (bağlam-farkında, pahalı) veya özel (LLM + kural-tabanlı geri-dönüş).
2. **Seçici girdileri.** LLM-seçimli ise: son N mesaj, agent uzmanlıkları, tur sayıları. Özel ise: açık kurallar.
3. **Sonlandırma kuralları.** Maksimum tur, TERMINATE token'ı, hedefe-ulaşıldı doğrulayıcısı veya kombinasyon.
4. **Sıcak-konuşmacı azaltma.** Agent başına tur tavanı, seçici girdisinde konuşmacı-denge puanı, K ardışık tur sonrasında zorunlu rotasyon.
5. **Bağlam şişmesi azaltma.** Öngörü planı (rol başına kapsamlı görünümler), özet checkpoint'leri, agent başına bağlam tavanı.
6. **Gözlemlenebilirlik.** Seçicinin girdisini, seçicinin seçimini, tur başına agent gecikmesini loglayın.

Keskin redler:

- Seçicinin girdi/çıktı loglaması olmayan herhangi bir LLM-seçimli yapılandırma. Hata ayıklama imkansız hale gelir.
- Maksimum tur tavanı olmayan yapılandırmalar.
- Akıl-yürütme görevlerinde simetrik sohbetler (uzmanlaşma yok) — bunun yerine tartışma (Ders 07) kullanın.

Ret kuralları:

- Görevin bilinen bir DAG yapısı varsa, GroupChat'i reddedin ve determinizm için LangGraph statik grafik önerin.
- Görev sıkı denetim izleri gerektiriyorsa, GroupChat'i reddedin; checkpointer'lı LangGraph önerin.
- Agent'lar 5-6'dan fazlaysa, düz GroupChat'i reddedin ve yuvalanmış gruplar veya hiyerarşik örüntü önerin.

Çıktı: Tek sayfalık GroupChat yapılandırma özeti. Maliyet tahminiyle (LLM-seçimli tur başına bir seçici çağrısı getirir) kapatın.
