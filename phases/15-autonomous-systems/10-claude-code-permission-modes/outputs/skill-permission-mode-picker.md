---
name: permission-mode-picker
description: Bir Claude Code görevini başlatmadan önce doğru permission mode (izin modu), bütçe tavanlarını ve gerekli izolasyonu eşleştirin.
version: 1.0.0
phase: 15
lesson: 10
tags: [claude-code, permission-modes, auto-mode, budgets, isolation]
---

Önerilen bir Claude Code görevi verildiğinde, izin modunu seçin, bütçeleri ayarlayın ve agent'ın başlamasına izin verilmeden önce gereken minimum izolasyonu belirtin.

Üretin:

1. **Görev profili.** Görevin ne yaptığına dair tek cümle, yanlış giderse patlama yarıçapına dair tek cümle.
2. **Mod önerisi.** Şunlardan biri: `plan`, `default`, `acceptEdits`, `acceptExec`, `autoMode`, `yolo`, `bypassPermissions`. Patlama yarıçapına atıfta bulunan tek cümleyle gerekçelendirin.
3. **Bütçe sayıları.** `max_turns`, `max_budget_usd` ve araç başına tavanlar için somut değerler. Bir saatin üzerindeki gözetimsiz çalıştırmalar için, geri alamayacağınız bir insan hatası için ödeyeceğiniz kadar veya daha az bir dolar tavanı belirtin.
4. **İzolasyon gereksinimleri.** Dosya sistemi kapsamı (yalnızca proje dizini, scratch dizini, kısa-ömürlü container). Ağ politikası (egress yok, yalnızca allowlist, tam). Kimlik bilgisi yüzeyi (yok, kapsamlı token, geniş token). `bypassPermissions` veya `yolo` için, çalıştırma production kimlik bilgileri bağlanmamış kısa-ömürlü bir container içinde olmalıdır.
5. **Trajectory denetim planı.** Çalıştırmadan sonra bir insan trajectory'yi nasıl inceleyecek? `autoMode`, `yolo` ve 30 dakikalık horizon'un üzerindeki her şey için zorunludur.

Keskin redler:

- Commit edilmemiş değişiklikleri olan bir depoya karşı `bypassPermissions`.
- Bütçe tavanı olmayan `autoMode`.
- Ortamda geniş kimlik bilgileri (AWS, GCP, repo kapsamlı GitHub PAT) olan `acceptEdits`'in üzerindeki herhangi bir mod.
- Trajectory denetimi zamanlanmamış bir saatten uzun gözetimsiz çalıştırmalar.
- Auto Mode sınıflandırıcısının yeni bir görev dağılımı için tek başına yeterli olduğu iddiaları.

Ret kuralları:

- Kullanıcı bir başarısızlığın patlama yarıçapını adlandıramıyorsa, reddedin ve başlamadan önce açık bir en-kötü-durum cümlesi isteyin.
- Kullanıcı production veritabanı kimlik bilgilerinin erişilebilir olduğu bir çalışma alanında `autoMode` istiyorsa, reddedin ve önce kapsamlı kimlik bilgileri veya kısa-ömürlü bir container isteyin.
- Önerilen bütçe tavanı, kullanıcının kötü bir çalıştırmada kaybetmeye razı olduğundan fazlaysa, reddedin ve daha düşük bir tavan isteyin.

Çıktı formatı:

Şunları içeren tek sayfalık bir çalıştırma kartı döndürün:

- **Görev özeti** (tek cümle)
- **Patlama yarıçapı** (tek cümle, en kötü durum)
- **Mod** (açık)
- **Bütçeler** (`max_turns`, `max_budget_usd`, araç başına tavanlar)
- **İzolasyon** (fs kapsamı, ağ politikası, kimlik bilgisi yüzeyi)
- **Denetim planı** (trajectory'yi kim inceler, ne zaman, hangi rubrike karşı)
