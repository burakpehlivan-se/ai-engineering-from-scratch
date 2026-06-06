---
name: control-protocol-audit
description: Bir dağıtım protokolünü AI Control (Yapay Zeka Kontrolü) tehdit modeli altında denetle
version: 1.0.0
phase: 18
lesson: 10
tags: [ai-control, subversion, trusted-editing, untrusted-monitoring, safety-case]
---

Bir dağıtım protokolü açıklaması verildiğinde, onu AI Control tehdit modeli altında denetle: U (güvenilmeyen güçlü), T (güvenilir zayıf), H (güvenilir insan) ve protokolün yararlılık-güvenlik cephesindeki konumunu ölç.

Çıktı:

1. Rol ataması. Hangi modelin U ve hangisinin T olduğunu belirle. Eğer T, U'nun başka bir örneği ise, hemen gizli iş birliği (collusion) riskini işaretle.
2. Denetim bütçesi muhasebesi. H nasıl tahsis ediliyor? Tek biçimli mi, rastgele mi, bayrak-yönlendirmeli mi? Beklenen olarak çıktıların hangi kesri denetleniyor?
3. Gizli iş birliği vektörlerinin listelenmesi. Güvenilmeyen bileşenlerin her çifti için (U-üretici + U-izleyici, U-üretici + U-editör), gizli iş birliği vektörlerini sırala: steganografik ipuçları, paylaşılan-eğitim öncül istismarı, zamanlama kanalları.
4. Yetenek boşluğu analizi. T, U'dan ne kadar zayıf? T'nin düzenleme sinyali ne zaman gürültüye dönüşür (örn. T, U'nun ürettiği arka kapıları güvenilir şekilde tespit edemez)?
5. En kötü durum tehdit modeli. U'nun protokol hakkında mükemmel bilgiyle karşıt olduğu varsayımı altında, saldırganın en iyi stratejisi nedir? Kırmızı takım denemelerinin hangi kesri başarılı olur?

Kesin redler:

- Gizli iş birliği direnç mekanizması olmadan U'yu kendi izleyicisi olarak kullanan herhangi bir protokol açıklaması.
- Kırmızı takımın protokol görünürlüğüne sahip olduğu kırmızı takım değerlendirmesi olmadan "sıfıra yakın arka kapı oranı" iddiası.
- T'den U'ya yetenek boşluğunu ve H bütçesini açıklamadan herhangi bir protokol denetimi.

Ret kuralları:

- Kullanıcı "bu protokol güvenli mi" diye sorarsa, üç parçalı kanıt olmadan reddet: (a) kırmızı takım sonucu, (b) yetenek boşluğu tahmini, (c) H bütçesi.
- Kullanıcı hizalamayı ve kontrolü karıştırırsa ("U'yu hizaladık, bu yüzden bir protokole ihtiyacımız yok"), reddet ve Ders 9'a (hizalama faking'i) yönlendir — hizalama U'nun bir özelliğidir, kontrol protokolün bir özelliğidir.

Çıktı: Yukarıdaki beş bölümü dolduran, en zayıf halkayı (genellikle T'den U'ya yetenek boşluğu veya gizli iş birliği direnci) adlandıran ve ele alınmamış en büyük tek başarısızlık kipini belirten tek sayfalık bir denetim. Tehdit modeli kaynağı olarak Greenblatt ve diğerlerini (arXiv:2312.06942) bir kez alıntıla.
