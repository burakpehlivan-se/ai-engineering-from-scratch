---
name: role-designer
description: Belirli bir görev için planlayıcı/yürütücü/eleştirmen/doğrulayıcı rollerini ve açık G/Ç şemalarını adlandıran bir rol listesi üretin.
version: 1.0.0
phase: 16
lesson: 08
tags: [multi-agent, role-specialization, metagpt, chatdev, verification]
---

Bir görev verildiğinde, G/Ç şemaları ve deterministik bir doğrulayıcı ile uzmanlaşmış bir rol listesi üretin. CrewAI, LangGraph, AutoGen veya özel döngülere eşlenmeye hazır.

Üretin:

1. **Rol listesi.** 3-5 rol. Her birini adlandırın. Minimum: planlayıcı, yürütücü, doğrulayıcı. Eleştirmen isteğe bağlı.
2. **Rol başına G/Ç şeması.** Her rol için: ne tüketir (yukarı yöndeki rolden) ve ne üretir (şema, düz yazı değil). Dataclass-stili gösterim kullanın.
3. **Doğrulayıcı spesifikasyonu.** Deterministik kontrolü adlandırın: test paketi, tür denetleyici, şema doğrulayıcı, linter. Geçer/kalır kriterlerini tanımlayın.
4. **Eleştirmen spesifikasyonu (isteğe bağlı).** Dahil edilirse, hangi öznel kaliteyi yargıldığını adlandırın. Somut kontrol listesi, "iyi kod" değil.
5. **İletişimsel halüsinasyondan-arındırma kuralları.** Bir ayrıntı eksik olduğunda her bir aşağı yöndeki rolün yukarı yöne göndermesine izin verilen soruları adlandırın, böylece uydurmazlar.
6. **Revizyon döngüsü bütçesi. İnsana çıkmadan önce maksimum tur. Varsayılan 2. **

7. **Framework eşlemesi.** Her biri için tek satır: bu rol listesini CrewAI, LangGraph, AutoGen'da nasıl ifade edersiniz.

Keskin redler:

- Deterministik doğrulayıcısı olmayan herhangi bir rol listesi. Tüm-LLM listeleri MAST kontrolünü geçemez.
- Bulanık G/Ç ("yürütücü çıktı döndürür"). Her zaman şemayı belirtin.
- Eleştirmen ve doğrulayıcının birleştirilmesi. Farklı hataları yakalarlar; ikisi de haklıysa, ikisi de var olmalıdır.

Ret kuralları:

- Görevin deterministik bir doğruluk kontrolü yoksa (tamamen üretken iş, yaratıcı yazım), reddedin ve bunun yerine insan incelemci döngüsü veya çok-agent'lı tartışma (Ders 07) önerin.
- Görev 3+ rol için çok küçükse (10 dakikanın altında insan işi), reddedin ve tek-agent önerin.

Çıktı: Tek sayfalık rol-tasarım özeti. MAST başarısızlık-boşluğu kontrolüyle kapatın: en az bir deterministik doğrulayıcının var olduğunu doğrulayın.
