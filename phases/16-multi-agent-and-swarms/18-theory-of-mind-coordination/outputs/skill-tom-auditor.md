---
name: tom-auditor
description: "Emergent coordination" (acıkan koordinasyon) iddia eden bir çok-agent'lı sistemi denetleyin. Gerçek ToM-etkin koordinasyonu, kontrol koşulları, istatistiksel testler ve tamamlayıcılık ölçümü ile prompt-süslü illüzyondan ayırır.
version: 1.0.0
phase: 16
lesson: 18
tags: [multi-agent, theory-of-mind, coordination, evaluation, emergence]
---

Acıkan koordinasyon iddia eden bir çok-agent'lı sistem verildiğinde, koordinasyonun gerçek mi yoksa prompt mühendisliğinin bir artefaktı mı olduğunu denetleyin.

Üretin:

1. **İddia çıkarma.** Hangi koordinasyon davranışı iddia ediliyor? (iş bölümü, beklenti, tamamlayıcı eylemler, fikir birliğine ulaşma). Tam olarak belirtin.
2. **Prompt inceleme.** Herhangi bir agent'ın sistem promptu açıkça koordinasyon, rol seçimi veya takım farkındalığı talimatı veriyor mu? Evet ise, iddiayı kısmen prompt-süslü olarak işaretleyin ve bir kontrol tasarlayın.
3. **Kontrol koşulu.** Koordinasyon-tetikleyici dili çıkarılmış sistemin bir versiyonu. Tam olarak hangi metnin değiştiğini belirtin.
4. **Metrik.** En az biri: kimlik-bağlantılı farklılaşma, hedef-yönelimli tamamlayıcılık, daha-yüksek-dereceli sinerji (Riedl 2025). "Agent'lar birlikte çalışıyor gibi görünüyor" kanıt olarak kabul etmeyin.
5. **İstatistiksel test.** Sistem ve kontrol üzerindeki metriğin anlamlılığı. `p < 0.05` için gereken örneklem büyüklüğü. `n < 50` deneme ise, gücü açıkça rapor edin.
6. **Model-kapasite kontrolü.** Karşılaştırmayı daha küçük bir temel modelde tekrarlayın. Etki devam ediyor mu yoksa kayboluyor mu? Li/Riedl her ikisi de kapasite-bağımlılığı gösterir.
7. **Başarısızlık-vakası incelemesi.** Sistem başarısız olduğunda, ToM durumu (varsa) neye benziyor? Kimlik karışıklığı (inanç-agent bağlama kırılmış) veya içerik halüsinasyonu (yanlış inanç içeriği)?

Keskin redler:

- Kontrol koşulu olmadan acıkanlık iddiaları. Demo kayıtları kanıt değildir.
- İstatistiksel incelemede kaybolan iddialar (`n >= 50` denemede `p < 0.05` altında etki). Bunlar koordinasyon illüzyonlarıdır.
- Yalnızca bir modelde geçerli olan iddialar. Daha küçük güçlü bir temel de ToM promptlaması olmadan etkiyi başarıyorsa, koordinasyon ToM-tahrikli değildir.
- Mekanizma açıklaması olarak "agent'larımız sadece çözdü". Mekanizma iddialarının ToM durumunun loglanmış ve incelenebilir olması gerekir.

Ret kuralları:

- Sistemin agent başına akıl-yürütme loglaması yoksa, denetim gerçek koordinasyonu rastgelelikten ayırt edemez. Yeniden denetlemeden önce yapılandırılmış ToM-durumu logları eklenmesini önerin.
- Görevin oracle-hesaplanmış optimal koordinasyonu varsa, kontrol yerine optimalle karşılaştırın.
- İddia dar ise ("tek-turlu görevde koordinasyon"), denetim daha kısa bir kontrol olabilir: tek turda tamamlayıcılığı ölçün, uzun-horizon analizi gerekmez.

Çıktı: İki sayfalık denetim. Tek cümlelik bir kararla başlayın ("Koordinasyon iddiası prompt-süslü: 'birlikte çalış' dilini kaldırmak metriği 0.82'den 0.31'e düşürür, kontrol-anlamlı."), sonra yukarıdaki yedi bölüm. Prompt-süslü koordinasyonu gerçek koordinasyona dönüştürmek için bir düzeltme listesiyle bitirin: açık ToM durumu, loglama ile daha uzun horizonlar, karışık-modelli topluluklar.
