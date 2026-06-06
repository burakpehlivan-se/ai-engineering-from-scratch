---
name: benchmark-reader
description: Çok-agent'lı bir benchmark iddiasını şüpheci okuyun. İddiayı benchmark seçimi, kontaminasyon, temeller, istatistiksel anlamlılık, görev çeşitliliği ve maliyet açıklaması üzerinden notlandırır.
version: 1.0.0
phase: 16
lesson: 24
tags: [multi-agent, benchmarks, evaluation, SWE-bench, MARBLE]
---

Yayınlanmış veya dahili çok-agent'lı benchmark performansı iddiası verildiğinde, iddiayı notlandırın ve uyarıları yüzeye çıkarın.

Üretin:

1. **Benchmark + split tanımlama.** Hangi benchmark (MARBLE, COMMA, MedAgentBoard, AgentArch, SWE-bench Pro, SWE-bench Verified, özel)? Hangi split (tam, tutulmuş, kontaminasyon-temizlenmiş)? Bilinmeyen split'ler diskalifiye edicidir.
2. **Kontaminasyon durumu.** Benchmark, test edilen modelin eğitim-kesim-tarihinden sonra mı? Benchmark eğitim kesim tarihinden önceyse, kontaminasyon riski için işaretleyin ve iddiayı indirimleyin.
3. **Temel kalitesi.** Tek-LLM'ye karşı, rastgele karşı, önceki çok-agent'lı çalışmalara karşı. Ayarlanmamış-aynı-sistem karşı sayılmaz; bu bir ablasyondur, temel değil.
4. **İstatistiksel anlamlılık.** N deneme, güven aralığı veya standart hata, p-değeri veya eşdeğeri. N < 50 denemede istatistik olmadan iddialar yetersiz desteklenmiştir.
5. **Görev çeşitliliği.** Bir görev, bir domain veya birçok? Tek-görev iddiaları genelleme anlamına gelmez.
6. **Maliyet açıklaması.** Görev başına token, görev başına duvar-saati, görev başına dolar maliyeti. 20x maliyette %90'lık bir çözüm iş kararıdır; maliyet olmadan, iddia eksiktir.
7. **Harf notu + tek cümlelik karar.**

   - **A:** Altı kontrolün tümü geçer; iddia muhtemelen sağlamdır.
   - **B:** Bir zayıflık; iddia notlu uyarılarla olasıdır.
   - **C:** İki zayıflık; iddia telkindir ancak çoğaltma gerektirir.
   - **D:** Üç veya daha fazla zayıflık; iddia kanıt değildir.
   - **F:** Diskalifiye edici sorun (açıklanmamış split üzerinde kontaminasyon, istatistik yok, temel yok).

Keskin redler:

- Verified vs Pro belirtmeden "SWE-bench" gösteren iddialar. 40+ puanlık boşluk bunu belirsiz raporlamayı kabul edilemez yapar.
- Temel karşılaştırma olmadan iddialar. "Sistemimiz %X yapıyor" bir sayıdır, sonuç değildir.
- Çok-agent'lı sistemler için 20'den az denemeye dayanan iddialar. Varyans çok yüksektir.
- Maliyet-raporlanmamış çok-agent'lı sistem iddiaları. Koordinasyon vergisi önemlidir.

Ret kuralları:

- Benchmark herkese açık değilse ve kullanıcının dahili denetim izi yoksa, not atanamaz. Değerlendirme artefaktlarının yayınlanmasını önerin.
- İddia şu anda hakemli inceleme altındaki bir makaleden ise (arXiv preprint, gönderilmemiş), ihtiyat olarak bir harf notu düşürün.
- Kullanıcı iddia sahibinin kendisi denetim istiyorsa, denetimi doğrudan çalıştırın; iddia henüz yayına hazır olmadığında işaretleyin.

Çıktı: Tek sayfalık not kartı. Tek cümlelik bir özetle başlayın ("Not: C — iyi benchmark seçimi, yeterli temeller, ancak kontaminasyon kontrolü ve maliyet açıklaması yok."), sonra yukarıdaki yedi bölüm. "Notu yükseltmek için ne düzeltmeli" önceliklendirilmiş bir listeyle bitirin.
