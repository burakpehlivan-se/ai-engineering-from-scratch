---
name: prompt-caching-planner
description: Önbellek dostu bir prompt düzeni tasarlayın ve doğru sağlayıcı önbellekleme modunu seçin.
version: 1.0.0
phase: 11
lesson: 15
tags: [llm-engineering, caching, cost]
---

Size bir prompt (sistem + araçlar + few-shot + geri getirme + geçmiş + kullanıcı) ve bir kullanım profili (saat başına istekler, gerekli TTL, sağlayıcı) verildiğinde, çıktı:

1. Düzen. Tek bir önbellek kesme noktası işaretlenmiş olarak bölümleri yeniden sıralayın; hangi bölümlerin kararlı, hangilerinin geçici olduğunu açıklayın.
2. Sağlayıcı modu. Anthropic cache_control, OpenAI otomatik, veya Gemini CachedContent. TTL ve yeniden kullanım kalıbından gerekçelendirin.
3. Başa baş noktası. TTL içinde yazma başına beklenen okumalar; matematikle önbelleksiz duruma karşı net maliyet.
4. Doğrulama planı. İkinci özdeş istekte `cache_read_input_tokens > 0` olacağına dair CI iddiası; önbelleğe alınmış ve önbelleğe alınmamış token'lara göre bölünmüş pano.
5. Başarısızlık modları. Bu kurulumda önbelleğin kaçırılmasının en olası üç nedenini (dinamik zaman damgası, araç yeniden sıralaması, yakın kopya metin) ve her birini nasıl önleyeceğinizi listeleyin.

Dinamik bir alanı kesme noktasının üzerine yerleştiren bir önbellek planını göndermeyi reddedin. 2x yazma primini geri ödeyecek bir yeniden kullanım sayısı olmadan 1 saat TTL'sini etkinleştirmeyi reddedin.
