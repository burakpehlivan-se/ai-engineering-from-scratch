---
name: scheming-triage
description: Bir ajan dağıtım olayı raporunu Apollo üç-sütunlu komplo (scheming) çerçevesine göre triyaj et
version: 1.0.0
phase: 18
lesson: 8
tags: [scheming, agent-safety, apollo, three-pillars, safety-cases]
---

Bir ajan dağıtım olayı raporu (beklenmeyen araç kullanımı, veri erişimi, kendini-koruma-yanlısı davranış) verildiğinde, başarısızlık kipini sınıflandır ve komplo aday olduğunda Apollo üç-sütunlu testini uygula.

Çıktı:

1. Başarısızlık sınıfı triyajı. Olayı şu şekilde etiketle: yetenek başarısızlığı (model görevi yapamadı), kontrol başarısızlığı (izleme/araç-kullanım protokolü modeli sınırlamadı) veya komplo (model, farklı bir bağlam-içi hedef uğruna kullanıcının hedefine karşı eylemler aldı).
2. Üç-sütun kontrolü (komplo adaysa).
 - Hizalama dışılık: eylem, ortamda veya araç çıktısında bulunan ortogonal bir hedefe hizmet etti mi?
 - Hedef-yönelimlilik: eylem, çok adımlı bir planın parçası mıydı yoksa tek atımlık bir hata mı?
 - Durumsal farkındalık: modelin o sırada değerlendirildiğini bildiğine dair kanıt var mı?
3. Değerlendirme-bağlamı denetimi. Olay, dağıtımda mı, kırmızı takım değerlendirmesinde mi yoksa her ikisinde mi gözlemlendi? Yalnızca dağıtımdaysa, değerlendirme-zamanı sonuçlarının aktarılmadığını not et (Apollo 2025 uyarısı).
4. Çıkarma yeniden üretilebilirliği. Aynı istem + ortam aynı davranışı tekrar üretebilir mi? Yeniden üretilebilir bir olay üç-sütun çerçevesindedir; yeniden üretilemeyen bir olay bir yetenek çıkarma artefaktı olabilir.
5. Güvenlik durumu boşluğu. Bu dağıtım için mevcut güvenlik durumu üç sütundan hangilerini ele alıyor ve hangisini açıkta bırakıyor?

Kesin redler:

- Komployu yetenek-sınıfı başarısızlığı olarak çerçeveleyen herhangi bir yaklaşım. Komplo, hedef-yönelimlilik ve durumsal farkındalık gerektirir — yetenekten yoksun bir model komplo kuramaz.
- "Komploya karşı eğitim gizli eylem oranını azalttı" çıkarımının, aynı model için değerlendirme-bağlamı tanıma oranını kontrol etmeden, altta yatan hizalama dışılığını azalttığını ima etmesi.
- Ajan veri sızdırmadığı için gözetim altını oymanın "saldırı olmadığı" yönündeki herhangi bir iddia — gözetim altını oymak, kendi başına bir komplo eylemidir.

Ret kuralları:

- Kullanıcı "modelim komplo mu kuruyor" diye sorarsa, üç-sütun kanıtı olmadan ikili yanıt vermeyi reddet; değerlendirme-bağlamı ve çıkarma-yeniden üretilebilirliği verilerini iste.
- Kullanıcı artık bir komplo olasılığı sorarsa, sayısal yanıtı reddet ve 2026 değerlendirme güvenilirliğinin modelin kendi durumsal farkındalığıyla sınırlı olduğunu açıkla.

Çıktı: Başarısızlık sınıfını etiketleyen, mevcut kanıtlarla üç sütunu dolduran, eksik kanıtları işaretleyen ve kapatılması en acil olan tek güvenlik durumu boşluğunu adlandıran tek sayfalık bir triyaj. Çerçeve kaynağı olarak Meinke ve diğerlerini (arXiv:2412.04984) bir kez alıntıla.
